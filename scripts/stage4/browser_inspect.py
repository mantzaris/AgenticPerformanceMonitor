"""Frozen representative rule: first case in each family, all three methods."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json,write_json,now
from trajectory_dashboards.stage4.core import ROOT


def main():
    p=argparse.ArgumentParser();p.add_argument('--chromium',default='/snap/bin/chromium');args=p.parse_args()
    out=ROOT/'inspection';out.mkdir(parents=True,exist_ok=True)
    if (out/'browser.json').exists():raise ValueError('Preserve original browser inspection')
    records=[];errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':980});page.on('pageerror',lambda e:errors.append(str(e)))
        for qid in ['s4_01','s4_03','s4_05','s4_07','s4_09','s4_11']:
            for method in ['baseline','full_spec','semantic']:
                case=ROOT/'pilot'/method/qid
                if not (case/'accepted/spec.json').exists():
                    records.append({'method':method,'question_id':qid,'status':'no accepted dashboard','result':read_json(case/'result.json')});continue
                a=case/'accepted';page.goto((a/'dashboard.html').resolve().as_uri())
                b=read_json(a/'bound.json');body=page.locator('body').inner_text()
                assert b['conclusion'] in body and all(c['text'] in body for c in b['claims']) and page.locator('svg').count()>0
                page.locator('details').last.locator('summary').click()
                assert page.locator('details').last.get_attribute('open') is not None
                page.locator('details').last.locator('summary').click()
                image=out/f'{method}_{qid}.browser.png';page.screenshot(path=str(image),full_page=True)
                records.append({'method':method,'question_id':qid,'status':'rendered','screenshot':str(image),'claims':b['claims'],'conclusion':b['conclusion'],'provenance':str(a/'selection_provenance.json')})
        version=browser.version;browser.close()
    write_json(out/'browser.json',{'created_utc':now(),'status':'PASS','browser':version,'browser_errors':errors,'selection_rule':'First case in each of six frozen families, all three methods; failures retained','records':records,'limitations':['One desktop browser; automated checks plus Codex image inspection, not independent human scientific/usability review','No local server needed; self-contained HTML opened through file URLs']})
    print('Inspected',len(records),'prespecified method/case outputs')


if __name__=='__main__':main()
