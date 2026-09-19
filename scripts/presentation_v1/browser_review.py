"""Inspect final views, live values, vector bounds, links and paper-size proofs."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json, write_json
from trajectory_dashboards.presentation_v1.charts import num


def inspect(root,chromium):
    root=Path(root).resolve();out=root/'inspection';out.mkdir(exist_ok=True)
    if str(chromium).startswith('/snap/') and root.is_relative_to('/tmp'):
        raise ValueError('Use a repository output directory with Snap Chromium; host /tmp file URLs are not visible to the snap.')
    report={'pages':[],'figures':[],'errors':[],'external_requests':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox','--disable-gpu'])
        page=browser.new_page(viewport={'width':1100,'height':1100},device_scale_factor=1)
        page.on('pageerror',lambda error:report['errors'].append(str(error)))
        page.on('request',lambda req:report['external_requests'].append(req.url) if req.url.startswith(('http:','https:')) else None)
        sources=read_json(root/'source_manifest.json')
        for entry in sources['entries']:
            for route in ['index.html','figure.html']:
                path=root/'gallery'/entry['slug']/route
                page.set_viewport_size({'width':600 if route=='figure.html' else 1000,'height':1100})
                page.goto(path.as_uri());page.evaluate('document.fonts.ready')
                m=read_json(path.parent/'presentation.json')
                # Independently read actual DOM labels, not the exported model object.
                checked=0
                for card in page.locator('.answer-card.peer').all():
                    e=m['evidence'][card.get_attribute('data-evidence')];s=e['summary'];txt=card.text_content()
                    assert e['unit'] in txt
                    assert f'Person: weeks {e["window"][0]}–{e["window"][1]}' in txt
                    assert f'reference: weeks {e["reference_window"][0]}–{e["reference_window"][1]}' in txt
                    for value in (e['people'],e['observations']):
                        assert f'{value:,}' in txt
                    if e['status']=='supported':
                        for key in ['focal_mean','peer_mean','peer_ci_low','peer_ci_high']:
                            assert num(s[key]) in txt
                        assert num(s['contrast'],True) in txt
                    else:
                        assert 'Peer comparison unavailable' in txt
                    checked+=1
                links=page.locator('a').evaluate_all('(links)=>links.map(a=>a.href)')
                missing=[]
                for link in links:
                    url=urlsplit(link)
                    if url.scheme=='file' and not Path(unquote(url.path)).is_file():
                        missing.append(link)
                assert not missing,missing
                # Expanding all saved panels exposes labels that a top-only screenshot
                # could miss. Check SVG text geometrically against its own viewport.
                page.locator('details').evaluate_all('(nodes)=>nodes.forEach(e=>e.open=true)')
                clipped=page.locator('svg').evaluate_all('''(svgs)=>svgs.flatMap((svg,i)=>{
                  const vb=svg.viewBox.baseVal;
                  return [...svg.querySelectorAll('text')].flatMap(t=>{
                    const b=t.getBBox();
                    return b.x < -1 || b.x+b.width > vb.width+1 || b.y < -1 || b.y+b.height > vb.height+1 ? [{svg:i,text:t.textContent,box:{x:b.x,y:b.y,w:b.width,h:b.height},viewport:{w:vb.width,h:vb.height}}] : [];
                  });
                })''')
                report['pages'].append({'page':str(path.relative_to(root)),'peer_cards_source_checked':checked,'broken_links':missing,'clipped_svg_text':clipped})
        page.set_viewport_size({'width':1000,'height':1200})
        for f in read_json(root/'figure_manifest.json')['figures']:
            path=root/'figures'/f'{f["name"]}.html'
            page.goto(path.as_uri());page.evaluate('document.fonts.ready')
            page.wait_for_function('[...document.images].every(i=>i.complete && i.naturalWidth>0)')
            proof=page.locator('.proof');box=proof.bounding_box()
            assert abs(box['width']-180/25.4*96)<.1
            proof.screenshot(path=str(out/f'{f["name"]}.browser-proof.png'))
            page.locator('.large summary').click()
            assert page.locator('.large').get_attribute('open') is not None
            report['figures'].append({'name':f['name'],'browser_opened':True,'physical_size_css_mm':180,'proof_bounds_css':box,'full_resolution_control':'PASS'})
        page.goto((root/'gallery/index.html').as_uri());page.wait_for_function('[...document.images].every(i=>i.complete && i.naturalWidth>0)')
        gallery_links=page.locator('a').evaluate_all('(nodes)=>nodes.map(a=>a.href)')
        missing=[link for link in gallery_links if urlsplit(link).scheme=='file' and not Path(unquote(urlsplit(link).path)).is_file()]
        assert not missing,missing
        report['gallery']={'links_checked':len(gallery_links),'broken_links':missing,'previews':'whole expanded-page previews, object-fit contain'}
        page.screenshot(path=str(out/'gallery.browser.png'),full_page=True)
        report['browser']=browser.version;browser.close();report['browser_closed']=True
    write_json(out/'browser_verification.json',report)
    clipped=[(r['page'],x) for r in report['pages'] for x in r['clipped_svg_text']]
    if clipped:
        raise AssertionError('Clipped SVG labels: '+str(clipped))
    assert not report['errors'] and not report['external_requests']
    print(f'{len(report["pages"])} pages and {len(report["figures"])} figure proofs inspected; labels, values and links passed.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/presentation_v1');p.add_argument('--chromium',default='/snap/bin/chromium');a=p.parse_args();inspect(a.output,a.chromium)
