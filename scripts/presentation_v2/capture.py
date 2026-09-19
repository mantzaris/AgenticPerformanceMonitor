"""CPU browser captures plus semantic, navigation, and saved-state checks."""
import argparse
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json, write_json, file_hash


def displayed(value, signed=False):
    if value is None:
        return 'Unavailable'
    return (f'{value:+,.2f}' if signed and value else f'{value:,.2f}').replace('-', '−')


def capture(root, chromium):
    root = Path(root).resolve(); (root / 'captures').mkdir(exist_ok=True)
    record = {'viewport': {'width': 548, 'height': 1100}, 'device_scale_factor': 3,
              'browser_flags': ['--no-sandbox', '--disable-gpu'], 'font': 'Local DejaVu Sans',
              'captures': [], 'checks': [], 'errors': [], 'external_requests': [], 'broken_links': []}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=chromium, headless=True, args=record['browser_flags'])
        record['browser'] = browser.version
        ctx = browser.new_context(viewport=record['viewport'], device_scale_factor=3)
        page = ctx.new_page()
        page.on('pageerror', lambda e: record['errors'].append(str(e)))
        page.on('request', lambda r: record['external_requests'].append(r.url) if r.url.startswith(('http:', 'https:')) else None)

        def open_page(path, query=''):
            page.goto(path.as_uri() + query)
            page.wait_for_function('document.documentElement.dataset.presentationReady === "true"')
            page.evaluate('document.fonts.ready')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')

        def capture_panel(name, entry, selector='.figure-surface', action=None, route='figure.html'):
            target = page.locator(selector); path = root / 'captures' / (name + '.png')
            target.screenshot(path=str(path), animations='disabled')
            minimum = target.locator('svg text').evaluate_all('ts=>ts.length ? Math.min(...ts.map(t=>parseFloat(getComputedStyle(t).fontSize)*t.getScreenCTM().a)) : null')
            record['captures'].append({
                'name': name, 'file': str(path.relative_to(root)), 'sha256': file_hash(path),
                'selector': selector, 'crop_css_px': target.bounding_box(),
                'source_html': f'gallery/{entry["slug"]}/{route}',
                'html_sha256': file_hash(root / 'gallery' / entry['slug'] / route),
                'source_hashes': entry['source_hashes'], 'action': action,
                'control_state': page.evaluate('window.presentationState || null'),
                'url_query': urlsplit(page.url).query,
                'viewport': page.viewport_size, 'device_scale_factor': 3,
                'minimum_body_font_css_px': 20 if route == 'figure.html' else 12,
                'minimum_svg_font_css_px': minimum,
            })

        def check_answers(model):
            for el in page.locator('.figure-surface [data-answer]').all():
                eid = el.get_attribute('data-evidence'); kind = el.get_attribute('data-answer')
                template = {'peer': 'comparison', 'personal': 'personal_change'}[kind]
                assert any(c['template'] == template and c['evidence_id'] == eid for c in model['claims'])
                e = model['evidence'][eid]; s = e['summary']; content = el.inner_text()
                if kind == 'personal' and s['personal_status'] == 'supported':
                    assert displayed(s['baseline_mean']) in content and displayed(s['recent_mean']) in content
                    assert displayed(s['personal_change'], True) in content and e['unit'] in content
                if kind == 'peer' and e['status'] == 'supported':
                    for key in ['focal_mean', 'peer_mean', 'peer_ci_low', 'peer_ci_high']:
                        assert displayed(s[key]) in content, (eid, key)
                    assert displayed(s['contrast'], True) in content
                    # Assessment excerpts share one explicitly printed denominator
                    # below their two feature cards; it must agree for both records.
                    denominator_content = content
                    if model['layout'] == 'assessments' and page.locator('body.preparation').count():
                        assert len({(model['evidence'][i]['people'], model['evidence'][i]['observations'],
                                     tuple(model['evidence'][i]['reference_window'])) for i in model['comparison_ids']}) == 1
                        denominator_content = page.locator('.figure-surface').inner_text()
                    assert f'{e["people"]:,}' in denominator_content and f'{e["observations"]:,}' in denominator_content
                if kind == 'peer' and s['focal_mean'] is None:
                    assert 'unavailable' in content.lower(), (eid, content)
            for c in model['bound']['claims']:
                assert c['text'] in page.locator('#provenance').text_content()
            clipping = page.locator('.figure-surface svg').evaluate_all('ss=>ss.flatMap(s=>[...s.querySelectorAll("text")].filter(t=>{const b=t.getBBox();return b.x < -1 || b.x+b.width>s.viewBox.baseVal.width+1}).map(t=>t.textContent))')
            assert not clipping, clipping

        for entry in read_json(root / 'source_manifest.json')['entries']:
            slug = entry['slug']; base = root / 'gallery' / slug
            model = read_json(base / 'presentation.json')
            page.set_viewport_size(record['viewport']); open_page(base / 'figure.html')
            assert page.locator('.figure-surface').bounding_box()['width'] == 500
            check_answers(model); capture_panel(slug, entry)
            if model['layout'] == 'support':
                capture_panel(slug + '-answers', entry, '.excerpt-content')
            for route in ['figure.html', 'index.html']:
                page.set_viewport_size(record['viewport'] if route == 'figure.html' else {'width': 1280, 'height': 1100})
                open_page(base / route); check_answers(model)
                page.locator('.responsibility > summary').click()
                assert page.locator('.responsibility').get_attribute('open') is not None
                page.locator('.responsibility > summary').click()
                for href in page.locator('a[href]').evaluate_all('es=>es.map(e=>e.href)'):
                    u = urlsplit(href)
                    if u.scheme == 'file' and not Path(unquote(u.path)).exists(): record['broken_links'].append(href)
                if model['layout'] == 'references' and model['switchable']:
                    states = []
                    for eid in model['comparison_ids']:
                        page.select_option('#reference-select', eid)
                        e = model['evidence'][eid]; state = page.evaluate('window.presentationState')
                        assert state['summary'] == e['summary'] and state['reference_window'] == e['reference_window']
                        meta = json.loads(page.locator('#reference-chart metadata').text_content())
                        assert meta['selected'] == eid
                        assert page.locator('#reference-result [data-evidence]').get_attribute('data-evidence') == eid
                        assert page.locator('#reference-result .evidence-link').get_attribute('href') == '#evidence-' + eid
                        if route == 'figure.html':
                            assert meta['summary'] == e['summary']
                            capture_panel('reference-' + e['reference'], entry, '.switch-excerpt',
                                          {'event': 'select_option', 'selector': '#reference-select', 'value': eid})
                        check_answers(model)
                        states.append({'evidence_id': eid, 'reference': e['reference'], 'reference_window': e['reference_window'],
                                       'focal_window': state['focal_window'], 'focal_mean': state['summary']['focal_mean'],
                                       'domain': meta['x_domain'], 'people': e['people'], 'observations': e['observations']})
                        page.locator('#saved-permalink').click(); page.wait_for_load_state('load')
                        assert page.evaluate('window.presentationState.evidence_id') == eid
                        page.locator('#reference-result .evidence-link').click()
                        assert page.locator('#evidence-' + eid).get_attribute('open') is not None
                        open_page(base / route, '?reference=' + eid)
                    assert len({tuple(s['domain']) for s in states}) == len({s['focal_mean'] for s in states}) == len({tuple(s['focal_window']) for s in states}) == 1
                    open_page(base / route, '?reference=not-a-saved-selection')
                    assert page.evaluate('window.presentationState.error') == 'unknown_saved_reference'
                    assert page.locator('#reference-chart').is_hidden() and page.locator('#reference-result').is_hidden()
                    assert page.locator('#reference-warning').is_visible()
                    page.select_option('#reference-select', model['comparison_ids'][0])
                    assert page.locator('#reference-chart').is_visible() and page.locator('#reference-warning').is_hidden()
                    record['checks'].append({'view': slug, 'route': route, 'states': states,
                                             'bookmark_restore': True, 'unknown_reference_no_substitution': True})
                if route == 'index.html':
                    open_page(base / route)
                    capture_panel(slug + '-desktop', entry, route=route)
                    page.set_viewport_size({'width': 390, 'height': 844}); open_page(base / route)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                    capture_panel(slug + '-mobile', entry, route=route)
                record['checks'].append({'view': slug, 'route': route, 'source_bound_answers': True,
                                         'original_claims_accessible': len(model['bound']['claims']), 'no_svg_text_clipping': True})
        assert not record['errors'] and not record['external_requests'] and not record['broken_links'], record
        ctx.close(); browser.close(); record['browser_closed'] = True
    write_json(root / 'capture_manifest.json', record)
    print(len(record['captures']), 'captures; source values, state changes and URL restoration verified')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default='artifacts/presentation_v2')
    ap.add_argument('--chromium', default='/snap/bin/chromium'); args = ap.parse_args()
    capture(args.output, args.chromium)
