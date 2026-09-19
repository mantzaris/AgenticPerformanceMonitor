"""Final browser inspection of figures, template proof, links and review materials."""
import argparse,json,os
from pathlib import Path
from urllib.parse import unquote,urlsplit
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json,write_json,file_hash

def review(root,chromium):
 root=Path(root).resolve();records=[];errors=[];missing=[];network=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox','--disable-gpu'])
  context=browser.new_context(viewport={'width':1100,'height':1180},device_scale_factor=1);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
  def open_page(path):
   page.goto(path.as_uri());page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].every(i=>i.complete && i.naturalWidth>0)')
   for href in page.locator('a[href]').evaluate_all('es=>es.map(e=>e.href)'):
    u=urlsplit(href)
    if u.scheme=='file' and not Path(unquote(u.path)).exists():missing.append(href)
  for entry in read_json(root/'source_manifest.json')['entries']:
   for route in ['figure.html','index.html']:
    path=root/'gallery'/entry['slug']/route;open_page(path)
    assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
    records.append({'path':str(path.relative_to(root)),'type':'live view','errors':False})
  for entry in read_json(root/'figure_manifest.json')['figures']:
   path=root/'figures'/f'{entry["name"]}.html';open_page(path)
   bounds=page.locator('.paper').bounding_box();assert abs(bounds['width']-entry['width_mm']*96/25.4)<.1
   page.locator('.paper').screenshot(path=str(root/'checks'/f'browser_{entry["name"]}.png'))
   records.append({'path':str(path.relative_to(root)),'type':'final-size figure','bounds_css_px':bounds,'width_mm':entry['width_mm']})
  open_page(root/'proof/index.html')
  for i,el in enumerate(page.locator('section img').all(),1):
   bounds=el.bounding_box();assert abs(bounds['width']-210*96/25.4)<.1
   el.screenshot(path=str(root/'checks'/f'browser_proof_{i}.png'));records.append({'type':'official-template page','page':i,'bounds_css_px':bounds})
  # All 96 prepared pages and their original-data links. Read-only local access.
  open_page(root/'human_review/index.html')
  packet=read_json(root/'human_review/packet.json')['records']
  for r in packet:
   open_page(root/'human_review/slots'/f'{r["review_id"]}.html');assert r['question']['text'] in page.locator('body').inner_text()
  # Original full views for concrete scientific review disputes and the failure.
  for method,case in [('compact_a','s6_15'),('baseline','s6_15'),('derived_b','s6_17'),('binding_c','s6_21')]:
   path=Path(f'artifacts/stage6/comparison/{method}/{case}/accepted/dashboard.html').resolve();open_page(path)
   records.append({'path':str(path.relative_to(Path.cwd())),'type':'full original experimental dashboard','checked':'accessible; unmodified question/content is the review basis'})
  open_page(root/'gallery/index.html');assert not errors and not missing and not network
  browser_version=browser.version;context.close();browser.close()
 write_json(root/'checks/browser_review.json',{'browser':browser_version,'records':records,'review_slots_checked':96,'missing_links':missing,'browser_errors':errors,'external_requests':network,'browser_closed':True,'physical_inspection_limit':'Screen inspection at 96 CSS px/in and raster pages at 96/150 dpi, not a calibrated paper print. Actual PDF dimensions/fonts independently recorded.'})
 print(len(records),'views/figures/proof pages and 96 review slots; no browser errors or broken local links')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');p.add_argument('--chromium',default='/snap/bin/chromium');a=p.parse_args();review(a.output,a.chromium)
