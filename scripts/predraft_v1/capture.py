"""Capture actual browser states, including saved-reference interactions."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json,write_json,file_hash

def capture(root,chromium):
 root=Path(root).resolve();(root/'captures').mkdir(exist_ok=True)
 manifest={'viewport':{'width':548,'height':1100},'device_scale_factor':3,'browser_flags':['--no-sandbox','--disable-gpu'],'font':'DejaVu Sans, local files','captures':[],'checks':[],'errors':[],'external_requests':[]}
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=chromium,headless=True,args=manifest['browser_flags']);manifest['browser']=browser.version
  context=browser.new_context(viewport=manifest['viewport'],device_scale_factor=3);page=context.new_page()
  page.on('pageerror',lambda e:manifest['errors'].append(str(e)));page.on('request',lambda r:manifest['external_requests'].append(r.url) if r.url.startswith(('http:','https:')) else None)
  def snap(name,entry,selector='.figure-surface',action=None):
   page.evaluate('document.fonts.ready');target=page.locator(selector);bounds=target.bounding_box();path=root/'captures'/f'{name}.png';target.screenshot(path=str(path),animations='disabled')
   manifest['captures'].append({'name':name,'file':str(path.relative_to(root)),'sha256':file_hash(path),'selector':selector,'crop_css_px':bounds,'source_html':f'gallery/{entry["slug"]}/figure.html','html_sha256':file_hash(root/'gallery'/entry['slug']/'figure.html'),'source_hashes':entry['source_hashes'],'control_state':page.evaluate('window.presentationState || null'),'action':action,'minimum_body_font_css_px':20,'minimum_svg_font_css_px':target.locator('svg text').evaluate_all('ts=>ts.length ? Math.min(...ts.map(t=>parseFloat(getComputedStyle(t).fontSize)*t.getScreenCTM().a)) : null')})
  for entry in read_json(root/'source_manifest.json')['entries']:
   slug=entry['slug'];m=read_json(root/'gallery'/slug/'presentation.json');page.goto((root/'gallery'/slug/'figure.html').as_uri());page.wait_for_function('document.documentElement.dataset.presentationReady === "true"');page.evaluate('document.fonts.ready')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert page.locator('.figure-surface').bounding_box()['width']==500
   # Every excerpt answer is explicitly selected, never supplied from a rubric.
   for el in page.locator('.figure-surface [data-answer]').all():
    eid=el.get_attribute('data-evidence');kind=el.get_attribute('data-answer');template={'peer':'comparison','personal':'personal_change'}[kind]
    assert any(c['evidence_id']==eid and c['template']==template for c in m['claims'])
   for c in m['bound']['claims']:assert c['text'] in page.locator('#provenance').text_content()
   # Check all exposed SVG text bounds (axis labels / legends / titles).
   clipping=page.locator('.figure-surface svg').evaluate_all('svgs=>svgs.flatMap(s=>[...s.querySelectorAll("text")].filter(t=>{const b=t.getBBox();return b.x < -1 || b.x+b.width>s.viewBox.baseVal.width+1}).map(t=>t.textContent))')
   assert not clipping,(slug,clipping)
   snap(slug,entry)
   if slug in ['incomplete','baseline']:snap(slug+'-answers',entry,'.excerpt-content')
   if slug=='references':
    states=[]
    for eid in m['comparison_ids']:
     page.select_option('#reference-select',eid);s=page.evaluate('window.presentationState');e=m['evidence'][eid]
     assert s['summary']==e['summary'] and s['reference_window']==e['reference_window']
     assert page.locator('#reference-result [data-evidence]').get_attribute('data-evidence')==eid
     meta=json.loads(page.locator('#reference-chart metadata').text_content());assert meta['selected']==eid and meta['summary']==e['summary']
     link=page.locator('#reference-result .evidence-link');assert link.get_attribute('href')=='#evidence-'+eid;link.click();assert page.locator('#evidence-'+eid).get_attribute('open') is not None;page.locator('#evidence-'+eid).evaluate('e=>e.open=false')
     states.append({'state':s,'chart_domain':meta['x_domain']})
     snap('reference-'+e['reference'],entry,'.switch-excerpt',{'event':'select_option','selector':'#reference-select','value':eid})
    assert len({tuple(s['chart_domain']) for s in states})==1 and len({s['state']['summary']['focal_mean'] for s in states})==1 and len({tuple(s['state']['focal_window']) for s in states})==1
    manifest['checks'].append({'saved_reference_switch':'PASS','new_computation':False,'states':states})
   manifest['checks'].append({'view':slug,'all_original_claims_accessible':len(m['bound']['claims']),'selected_answers_only':True,'svg_text_clipping':False})
  assert not manifest['errors'] and not manifest['external_requests'];context.close();browser.close();manifest['browser_closed']=True
 write_json(root/'capture_manifest.json',manifest);print(len(manifest['captures']),'captures; selection/state/source checks passed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');p.add_argument('--chromium',default='/snap/bin/chromium');a=p.parse_args();capture(a.output,a.chromium)
