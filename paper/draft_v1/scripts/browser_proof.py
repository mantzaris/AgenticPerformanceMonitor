"""Render every manuscript page and count text inside raster UI panels.

CPU/browser only. Reads saved HTML; writes solely in draft_v1. Run with the
repository virtualenv Python (Playwright), after scripts/build.py.
"""
import argparse
import hashlib
import html
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT/'paper/draft_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def count(s):return len(''.join(s.split()))

VISIBLE_TEXT = r'''root => {
 const out=[];
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
 while(walker.nextNode()) {
   const t=walker.currentNode, el=t.parentElement;
   if(!el || el.closest('script,style,metadata,defs,title,select'))continue;
   const cs=getComputedStyle(el);
   if(cs.display==='none'||cs.visibility==='hidden')continue;
   const r=document.createRange();r.selectNodeContents(t);
   if([...r.getClientRects()].some(b=>b.width>0 && b.height>0))out.push(t.textContent);
 }
 root.querySelectorAll('select').forEach(s=>out.push(s.selectedOptions[0].textContent));
 return out.join(' ');
}'''

def main(chromium):
    check=HERE/'checks';proof=check/'pages';proof.mkdir(exist_ok=True)
    for old in proof.glob('*.png'):old.unlink()
    for dpi in [96,150]:
        subprocess.run(['pdftoppm','-r',str(dpi),'-png',str(HERE/'main.pdf'),str(proof/f'page_{dpi}dpi')],check=True)
    images=sorted(proof.glob('page_96dpi-*.png'))
    (check/'pages.html').write_text('<!doctype html><meta charset="utf-8"><title>Anonymous draft page proof</title><style>body{margin:24px;background:#e8ecee;font:16px sans-serif}figure{margin:24px auto;width:794px}img{display:block;width:210mm;box-shadow:0 1px 8px #9aa}figcaption{padding:10px}</style><h1>Draft V1: A4 proof at 96 CSS pixels/inch</h1><p>Every page is shown at 210 mm CSS width. Physical monitor scaling may vary. The 150 dpi originals are also linked.</p>'+''.join(f'<figure id="page-{i}"><figcaption>Page {i} · <a href="pages/{p.name.replace("96dpi","150dpi")}">150 dpi</a></figcaption><img alt="Manuscript page {i}" src="pages/{p.name}"></figure>' for i,p in enumerate(images,1)))
    captures=json.loads((ROOT/'artifacts/predraft_v1/capture_manifest.json').read_text())
    included=['personal','observations','reference-course','reference-early_stage','incomplete-answers','baseline-answers']
    record={'browser_flags':['--no-sandbox','--disable-gpu'],'page_viewport':{'width':850,'height':1200},'page_device_scale_factor':1,'pdf_sha256':sha(HERE/'main.pdf'),'pages':[],'errors':[],'external_requests':[],'raster_panel_text':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium,headless=True,args=record['browser_flags'])
        record['browser']=browser.version
        context=browser.new_context(viewport=record['page_viewport'],device_scale_factor=1)
        page=context.new_page()
        page.on('pageerror',lambda e:record['errors'].append(str(e)))
        page.on('request',lambda r:record['external_requests'].append(r.url) if r.url.startswith(('http:','https:')) else None)
        page.goto((check/'pages.html').as_uri())
        page.wait_for_function('[...document.images].every(x=>x.complete&&x.naturalWidth>0)')
        for i,img in enumerate(images,1):
            page.locator(f'#page-{i}').scroll_into_view_if_needed()
            assert page.locator(f'#page-{i} img').evaluate('e=>e.naturalWidth>0 && Math.abs(e.width-794)<2')
            record['pages'].append({'page':i,'image':str(img.relative_to(HERE)),'sha256':sha(img),'loaded_in_browser':True})
        page.locator('#page-1').screenshot(path=str(check/'browser_page1.png'))
        page.set_viewport_size(captures['viewport'])
        for cap in captures['captures']:
            if cap['name'] not in included:continue
            src=ROOT/'artifacts/predraft_v1'/cap['source_html']
            assert sha(src)==cap['html_sha256']
            page.goto(src.as_uri())
            page.wait_for_function('document.documentElement.dataset.presentationReady === "true"')
            page.evaluate('document.fonts.ready')
            if cap['action']:
                page.select_option(cap['action']['selector'],cap['action']['value'])
                state=page.evaluate('window.presentationState')
                assert state==cap['control_state']
            text=page.locator(cap['selector']).evaluate(VISIBLE_TEXT)
            record['raster_panel_text'].append({'capture_name':cap['name'],'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'selector':cap['selector'],'action':cap['action'],'text':text,'nonwhitespace_characters':count(text)})
        context.close();browser.close()
    record['browser_closed']=True
    assert not record['errors'] and not record['external_requests']
    (check/'browser.json').write_text(json.dumps(record,indent=2)+'\n')
    text=(check/'main.txt').read_text()
    pdf_count=count(text);raster_count=sum(x['nonwhitespace_characters'] for x in record['raster_panel_text'])
    counts={'pages':len(images),'pdf_sha256':sha(HERE/'main.pdf'),'pdf_extracted_nonwhitespace_characters':pdf_count,'additional_raster_figure_characters':raster_count,'combined_nonwhitespace_characters':pdf_count+raster_count,'conservative_glyph_allowance':500,'combined_with_allowance':pdf_count+raster_count+500,'rule_minimum':10000,'rule_maximum':50000,'within_range_even_with_allowance':10000<=pdf_count+raster_count+500<=50000,'method':'pdftotext -layout, remove all Unicode whitespace; add visible DOM text (including SVG text and only selected options) from the six raster panels actually included. Native PDF chart/diagram text, captions, bibliography, tables, footnotes and title are already in extracted PDF text. No score recomputation.','limitations':'A reproducible estimate, not the proprietary submission counter. Hyphenation, ligatures, math extraction and symbolic glyphs can differ; an additional 500-character allowance is reported, not claimed as an exact correction. CSS physical size depends on display scaling.'}
    assert counts['within_range_even_with_allowance']
    (check/'character_count.json').write_text(json.dumps(counts,indent=2)+'\n')
    print(json.dumps(counts,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--chromium',default='/snap/bin/chromium');args=parser.parse_args();main(args.chromium)
