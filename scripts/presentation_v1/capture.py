"""Real Chromium interaction, coordinated-state checks and reproducible captures."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json, write_json, file_hash


def capture(root, chromium):
    root=Path(root).resolve();out=root/'captures';out.mkdir(parents=True,exist_ok=True)
    if str(chromium).startswith('/snap/') and root.is_relative_to('/tmp'):
        raise ValueError('Snap Chromium cannot read host /tmp file URLs. Use a new output directory in the repository, or a non-Snap Chromium executable.')
    source=read_json(root/'source_manifest.json')
    manifest={'captured_utc':datetime.now(timezone.utc).isoformat(),'viewport':{'width':600,'height':1000},'expanded_viewport':{'width':1000,'height':1000},
              'device_scale_factor':3,'font':'DejaVu Sans (local system font; no remote requests)',
              'animations':'disabled in stylesheet and screenshot option','selector':'.figure-surface',
              'browser_flags':['--no-sandbox','--disable-gpu'],'captures':[],'interaction_checks':[], 'browser_errors':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium,headless=True,args=manifest['browser_flags'])
        manifest['browser']=browser.version
        context=browser.new_context(viewport=manifest['viewport'],device_scale_factor=3)
        page=context.new_page();errors=[];network=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:network.append(request.url) if request.url.startswith(('https:','http:')) else None)
        def ready():
            page.wait_for_function('document.documentElement.dataset.presentationReady === "true"')
            page.evaluate('document.fonts.ready')
            page.locator('svg').first.wait_for()
            page.evaluate('window.scrollTo(0,0)')
        def snap(name,entry,action=None):
            target=page.locator('.figure-surface')
            before=target.bounding_box()
            assert before and before['width']>500
            image=out/f'{name}.png'
            target.screenshot(path=str(image),animations='disabled')
            state=page.evaluate('window.presentationState || null')
            manifest['captures'].append({'name':name,'file':str(image.relative_to(root)),
                'sha256':file_hash(image),'browser_source':f'gallery/{entry["slug"]}/{Path(urlsplit(page.url).path).name}',
                'route':Path(urlsplit(page.url).path).name,'viewport':page.viewport_size,
                'html_sha256':file_hash(root/'gallery'/entry['slug']/Path(urlsplit(page.url).path).name),
                'source_artifacts':entry['source_hashes'],'crop_css_px':before,'control_state':state,'action':action})
        for entry in source['entries']:
            slug=entry['slug'];page.set_viewport_size(manifest['expanded_viewport']);page.goto((root/'gallery'/slug/'index.html').as_uri());ready()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal overflow'
            # A visible evidence link must open the corresponding saved record.
            link=page.locator('.figure-surface a.evidence-link').first
            href=link.get_attribute('href');link.click()
            assert page.locator(href).get_attribute('open') is not None
            page.locator(href).evaluate('(e)=>e.open=false');page.evaluate('window.scrollTo(0,0)')
            manifest['interaction_checks'].append({'case':slug,'evidence_link':href,'opens_correct_record':True})
            snap(slug+'-expanded',entry)
            page.set_viewport_size(manifest['viewport']);page.goto((root/'gallery'/slug/'figure.html').as_uri());ready()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'compact horizontal overflow'
            snap(slug,entry)
            if slug=='references':
                states=[]
                model=read_json(root/'gallery'/slug/'presentation.json')
                for eid in model['comparison_ids']:
                    page.select_option('#reference-select',eid)
                    state=page.evaluate('window.presentationState');expected=model['evidence'][eid]
                    assert state['summary']==expected['summary']
                    assert state['reference_window']==expected['reference_window']
                    assert page.locator('#reference-result .answer-card').get_attribute('data-evidence')==eid
                    assert page.locator('#reference-result a').get_attribute('href')==f'#evidence-{eid}'
                    chart=json.loads(page.locator('#reference-chart metadata').text_content())
                    assert chart['selected']==eid
                    states.append({'reference':expected['reference'],'state':state,'chart_domain':chart['x_domain']})
                    snap('reference-'+expected['reference'],entry,{'event':'select_option','selector':'#reference-select','value':eid})
                assert len({tuple(s['chart_domain']) for s in states})==1
                assert len({tuple(s['state']['focal_window']) for s in states})==1
                assert len({s['state']['summary']['focal_mean'] for s in states})==1
                manifest['interaction_checks'].append({'case':slug,'coordinated_reference_switch':'PASS','states':states,'new_analysis':False})
            # All saved selected claim texts remain accessible, including duplicates.
            expected=read_json(root/'gallery'/slug/'presentation.json')
            for claim in expected['bound']['claims']:
                assert claim['text'] in page.locator('#provenance').text_content()
            manifest['interaction_checks'].append({'case':slug,'original_claims_preserved':len(expected['bound']['claims'])})
        # Inspect desktop and a narrow responsive page without changing the paper captures.
        page.set_viewport_size({'width':600,'height':1000})
        page.goto((root/'gallery/personal/index.html').as_uri());ready()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(out/'responsive-personal.png'),full_page=False,animations='disabled')
        manifest['responsive_viewport']={'width':600,'height':1000,'horizontal_overflow':False,
            'file':'captures/responsive-personal.png','sha256':file_hash(out/'responsive-personal.png'),
            'browser_source':'gallery/personal/index.html','selector':'viewport'}
        manifest['browser_errors']=errors;manifest['external_requests']=network
        assert not errors and not network
        context.close();browser.close();manifest['browser_closed']=True
    write_json(root/'capture_manifest.json',manifest)
    print(f'{len(manifest["captures"])} captures; reference, evidence links and original-claim checks passed; no browser errors or external requests.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/presentation_v1');p.add_argument('--chromium',default='/snap/bin/chromium');a=p.parse_args();capture(a.output,a.chromium)
