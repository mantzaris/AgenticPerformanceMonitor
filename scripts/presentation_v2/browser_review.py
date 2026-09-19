"""Final-size figure/proof inspection, gallery navigation and expander checks."""
import argparse
from pathlib import Path
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright
from trajectory_dashboards.common import read_json, write_json, file_hash

def review(root, chromium):
    root = Path(root).resolve(); records = []; errors = []; network = []; missing = []
    (root/'checks').mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=chromium, headless=True, args=['--no-sandbox','--disable-gpu'])
        c = b.new_context(viewport={'width':1100, 'height':1180}, device_scale_factor=1); page = c.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('request', lambda r: network.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
        def visit(path):
            page.goto(path.as_uri()); page.evaluate('document.fonts.ready')
            page.wait_for_function('[...document.images].every(i=>i.complete && i.naturalWidth>0)')
            for href in page.locator('a[href]').evaluate_all('es=>es.map(e=>e.href)'):
                u = urlsplit(href)
                if u.scheme == 'file' and not Path(unquote(u.path)).exists(): missing.append(href)
        visit(root/'gallery/index.html')
        assert page.locator('.case-card').count() == 6
        page.screenshot(path=str(root/'checks/gallery_browser.png'), full_page=True, animations='disabled')
        for e in read_json(root/'source_manifest.json')['entries']:
            for route in ['index.html', 'figure.html']:
                visit(root/'gallery'/e['slug']/route)
                for d in page.locator('.below-surface > details').all():
                    d.locator(':scope > summary').click(); assert d.get_attribute('open') is not None
                    d.locator(':scope > summary').click(); assert d.get_attribute('open') is None
                # Test the main answer's evidence link, including ancestor expansion.
                for link in page.locator('.figure-surface .evidence-link').all():
                    target = link.get_attribute('href'); link.click()
                    assert page.locator(target).get_attribute('open') is not None
                    page.locator(target).evaluate('e=>e.open=false')
                records.append({'path': f'gallery/{e["slug"]}/{route}', 'expanders_and_evidence_links': 'PASS'})
        for e in read_json(root/'figure_manifest.json')['figures']:
            path = root/'figures'/f'{e["name"]}.html'; visit(path)
            bounds = page.locator('.paper').bounding_box()
            assert abs(bounds['width'] - e['width_mm']*96/25.4) < .1
            page.locator('.paper').screenshot(path=str(root/'checks'/f'browser_{e["name"]}.png'))
            records.append({'path': str(path.relative_to(root)), 'type': 'final-size figure', 'bounds': bounds,
                            'pdf_sha256': file_hash(root/'figures'/f'{e["name"]}.pdf'), 'recommended': e['recommended']})
        visit(root/'proof/index.html')
        for i, image in enumerate(page.locator('section img').all(), 1):
            bounds = image.bounding_box(); assert abs(bounds['width'] - 210*96/25.4) < .1
            image.screenshot(path=str(root/'checks'/f'browser_proof_{i}.png'))
            records.append({'type':'official-template page', 'page':i, 'bounds':bounds})
        version = b.version; c.close(); b.close()
    assert not errors and not network and not missing, (errors, network, missing)
    write_json(root/'checks/browser_review.json', {'browser':version, 'records':records,
        'browser_errors':errors, 'external_requests':network, 'broken_links':missing, 'browser_closed':True,
        'scope':'CPU browser views and intended-size proofs; not a usability or independent scientific review'})
    print('Inspected gallery, twelve routes, five figure candidates, and four proof pages; controls/links passed')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default='artifacts/presentation_v2')
    ap.add_argument('--chromium', default='/snap/bin/chromium'); args = ap.parse_args()
    review(args.output, args.chromium)
