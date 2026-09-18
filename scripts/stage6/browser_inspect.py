"""Frozen representative rule: first case in each family, all four conditions; plus first incomplete/rejected per agent condition."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json,write_json,now
from trajectory_dashboards.stage6.core import ROOT,CONDITIONS


def main():
    p=argparse.ArgumentParser();p.add_argument('--chromium',default='/snap/bin/chromium');args=p.parse_args()
    out=ROOT/'inspection';out.mkdir(parents=True,exist_ok=True)
    if (out/'browser.json').exists():raise ValueError('Preserve original browser inspection')
    records=[];errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':980});page.on('pageerror',lambda e:errors.append(str(e)))
        rows=read_json(ROOT/'reports/per_case.json')
        chosen={(qid,method) for qid in ['s6_01','s6_05','s6_09','s6_13','s6_17','s6_21'] for method in CONDITIONS}
        for method in CONDITIONS[1:]:
            for category in ['incomplete','rejected']:
                matching=sorted(r['question_id'] for r in rows if r['condition']==method and
                    ((r['valid_after_repair'] and not r['complete_requested_coverage']) if category=='incomplete' else (r['attempted'] and not r['valid_after_repair'])))
                if matching:chosen.add((matching[0],method))
        for qid,method in sorted(chosen):
            case=ROOT/'comparison'/method/qid
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
    write_json(out/'browser.json',{'created_utc':now(),'status':'PASS','browser':version,'browser_errors':errors,'selection_rule':'First case in each of six frozen families, all four conditions; plus first incomplete/rejected per agent condition; failures retained','records':records,'limitations':['One desktop browser; automated checks plus Codex image inspection, not independent human scientific/usability review','No local server needed; self-contained HTML opened through file URLs']})
    print('Inspected',len(records),'prespecified method/case outputs')


if __name__=='__main__':main()
