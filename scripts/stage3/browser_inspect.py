"""Predeclared case choices; actual follow-up form plus representative inspection."""
import argparse
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json,write_json,file_hash,now
from trajectory_dashboards.stage3.core import ROOT


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8766);parser.add_argument('--chromium',default='/snap/bin/chromium');args=parser.parse_args()
    out=ROOT/'inspection';out.mkdir(parents=True,exist_ok=True)
    if (out/'browser.json').exists():raise ValueError('Inspection exists; preserve original')
    records=[];errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':980})
        page.on('pageerror',lambda e:errors.append(str(e)))
        for qid in ['s3_01a','s3_03a','s3_09a','s3_07a']:
            for method in ['baseline','coverage_aware']:
                case=ROOT/'pilot'/method/qid
                if not (case/'accepted').exists():
                    records.append({'question_id':qid,'method':method,'status':'no accepted dashboard','failure':read_json(case/'result.json')});continue
                path=case/'accepted'
                page.goto(f'http://127.0.0.1:{args.port}/'+str(path/'dashboard.html'))
                b=read_json(path/'bound.json')
                body=page.locator('body').inner_text()
                assert b['conclusion'] in body
                assert all(c['text'] in body for c in b['claims'])
                assert page.locator('svg').count()>0
                page.screenshot(path=str(out/f'{method}_{qid}.browser.png'),full_page=True)
                records.append({'question_id':qid,'method':method,'status':'rendered','conclusion':b['conclusion'],'claim_texts':[c['text'] for c in b['claims']],'spec':str(path/'spec.json'),'screenshot':str(out/f'{method}_{qid}.browser.png')})
        parent=ROOT/'pilot/baseline/s3_07a/accepted'
        before={n:file_hash(parent/n) for n in ['question.json','spec.json','evidence.json','bound.json','dashboard.html']}
        page.goto(f'http://127.0.0.1:{args.port}/'+str(parent/'dashboard.html'))
        page.screenshot(path=str(out/'followup_before.browser.png'),full_page=True)
        page.locator('select[name="reference"]').select_option('early_stage')
        page.locator('select[name="profile"]').select_option('standard')
        with page.expect_navigation():page.get_by_role('button',name='Analyze and save follow-up').click()
        child=Path(urlparse(page.url).path.lstrip('/')).parent
        assert child!=parent
        e=next(iter(read_json(child/'evidence.json').values()))
        assert e['window']==[8,11] and e['reference_window']==[0,3] and e['cutoff_day']==83
        assert before=={n:file_hash(parent/n) for n in before}
        assert 'cutoff day 83' in page.locator('body').inner_text()
        page.screenshot(path=str(out/'followup_after.browser.png'),full_page=True)
        page.locator('details').first.locator('summary').click()
        assert page.locator('details').first.get_attribute('open') is not None
        page.locator('details').first.screenshot(path=str(out/'followup_inspector.browser.png'))
        write_json(out/'browser.json',{'created_utc':now(),'browser':browser.version,'status':'PASS','selection_rule':'First case in each predeclared family, phrasing a, baseline and proposed when accepted; failures retained.','records':records,'followup':{'parent':str(parent),'child':str(child),'parent_hashes':before,'parent_unchanged':True,'request':{'reference':'early_stage','profile':'standard'},'evidence_id':e['evidence_id'],'status':e['status'],'summary':e['summary'],'checks':['Actual form POST and redirect','New deterministic dispatch/evidence/specification/render','Updated cutoff/reference/window definitions','Evidence inspector opens','Original result unchanged']},'browser_errors':errors,'limitations':['One desktop Chromium browser; automated inspection and Codex visual review, not independent human scientific/usability review']})
        browser.close()
    print('Inspected representative pages and saved recomputing follow-up:',child)

if __name__=='__main__':main()
