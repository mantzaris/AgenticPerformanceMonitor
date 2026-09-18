"""Exercise the actual HTML form in an existing local Chromium browser."""
import argparse
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json,write_json,file_hash,now
from trajectory_dashboards.stage2.core import ROOT

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);parser.add_argument('--chromium',default='/snap/bin/chromium');args=parser.parse_args()
    parent=ROOT/'construction/baseline/c04/accepted'
    out=ROOT/'followup_demo';out.mkdir(parents=True,exist_ok=True)
    before_hashes={n:file_hash(parent/n) for n in ['spec.json','evidence.json','question.json','bound.json']}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':980})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{args.port}/'+str(parent/'dashboard.html'))
        page.screenshot(path=str(out/'before.browser.png'),full_page=True)
        page.locator('select[name="reference"]').select_option('early_stage')
        page.locator('select[name="profile"]').select_option('short')
        with page.expect_navigation():
            page.get_by_role('button',name='Analyze and save follow-up').click()
        assert page.url!=f'http://127.0.0.1:{args.port}/'+str(parent/'dashboard.html')
        child=Path(urlparse(page.url).path.lstrip('/')).parent
        page.screenshot(path=str(out/'after.browser.png'),full_page=True)
        page.locator('.chart').screenshot(path=str(out/'after.chart.browser.png'))
        assert 'reference weeks 0–1' in page.locator('body').inner_text()
        assert 'cutoff day 27' in page.locator('body').inner_text()
        page.locator('details').first.locator('summary').click()
        assert page.locator('details').first.get_attribute('open') is not None
        # Inspect expanded traceability separately; saved before/after pages remain preserved.
        page.locator('details').first.screenshot(path=str(out/'after.inspector.browser.png'))
        parent_e=next(iter(read_json(parent/'evidence.json').values()))
        child_e=next(iter(read_json(child/'evidence.json').values()))
        assert child_e['window']==[2,3] and child_e['reference_window']==[0,1]
        assert child_e['evidence_id']!=parent_e['evidence_id']
        assert len(child_e['trajectory'])==4 and len(parent_e['trajectory'])==12
        assert before_hashes=={n:file_hash(parent/n) for n in before_hashes}
        write_json(out/'verification.json',{'executed_utc':now(),'status':'PASS','browser':browser.version,'automation':'playwright 1.55.0 with existing Chromium','parent':str(parent),'child':str(child),'request':{'reference':'early_stage','profile':'short'},'parent_unchanged':True,'parent_hashes':before_hashes,'parent_status':parent_e['status'],'child_status':child_e['status'],'parent_summary':parent_e['summary'],'child_summary':child_e['summary'],'browser_errors':errors,'checks':['Actual browser form POST followed 303 to saved child','New analysis/evidence/specification and render created','Cutoff/window/reference labels updated','Original files unchanged','Evidence inspector expands','Observation and insufficiency states visible'],'limitations':['Single desktop Chromium interaction; no cross-browser, accessibility or concurrent-user evaluation']})
        print({'parent':str(parent),'child':str(child),'before':parent_e['status'],'after':child_e['status'],'browser_errors':errors})
        browser.close()

if __name__=='__main__':main()
