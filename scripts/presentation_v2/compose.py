"""Reproducible actual-browser panels at verified SCITEPRESS dimensions."""
import argparse
import hashlib
import json
import subprocess
from io import BytesIO
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader, simpleSplit

MM = 72 / 25.4
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def compose(root):
    root = Path(root); out = root / 'figures'; out.mkdir(exist_ok=True)
    template = json.loads(Path('artifacts/predraft_v1/template/manifest.json').read_text())
    width, cw, gap = (template[k] for k in ['textwidth_mm', 'columnwidth_mm', 'columnsep_mm'])
    captures = {r['name']: r for r in json.loads((root / 'capture_manifest.json').read_text())['captures']}
    for font in ['DejaVuSans', 'DejaVuSans-Bold']:
        pdfmetrics.registerFont(TTFont(font, '/usr/share/fonts/truetype/dejavu/' + font + '.ttf'))
    definitions = [
        ('figure1', None, [('personal', '(a) Personal progress', None), ('observations', '(b) Limited observations', None)]),
        ('figure2', 'Case B · person weeks 8–11 · day 83 · same measure and scale', [
            ('reference-course', '(a) Recent presentation peers', None),
            ('reference-early_stage', '(b) Earlier-period peers', None)]),
        ('figureS1', 'Requested recent window: weeks 10–11 · own history and presentation peers', [
            ('incomplete-answers', '(a) Saved agent selections', 'Selected peer answers: weeks 0–3. The recent-peer answer is omitted.'),
            ('baseline-answers', '(b) Saved enumeration', 'Explicit recent-peer insufficiency. Personal insufficiency remains separate.')]),
        ('figureS2', None, [('references', '(a) Reference comparison', None), ('assessments', '(b) Assessment activity', None)]),
        ('figure1_grid', None, [('personal', '(a) Personal progress', None), ('references', '(b) Reference comparison', None),
                              ('observations', '(c) Limited observations', None), ('assessments', '(d) Assessment activity', None)]),
    ]
    records = []
    for name, shared, panels in definitions:
        head = simpleSplit(shared or '', 'DejaVuSans', 9, width * MM)
        head_h = len(head) * 12 + (6 if shared else 0)
        groups = []
        for capture_name, title, note in panels:
            capture = captures[capture_name]; path = root / capture['file']
            assert sha(path) == capture['sha256']
            with Image.open(path) as im: iw, ih = im.size
            image_h = cw * MM * ih / iw
            lines = simpleSplit(note or '', 'DejaVuSans', 8.5, cw * MM)
            groups.append({'capture': capture, 'path': path, 'title': title, 'image_h': image_h,
                           'notes': lines, 'height': 19 + image_h + (7 + 11 * len(lines) if lines else 0)})
        row_heights = [max(g['height'] for g in groups[i:i+2]) for i in range(0, len(groups), 2)]
        natural_height = head_h + sum(row_heights) + (len(row_heights)-1) * gap * MM
        # Retain the required 2x2 trial, explicitly mark reduction if it cannot fit.
        scale = min(1, 235 * MM / natural_height) if len(panels) == 4 else 1
        physical_h = natural_height * scale
        pdf = out / (name + '.pdf')
        c = canvas.Canvas(str(pdf), pagesize=(width * MM, physical_h), invariant=1)
        c.setTitle(name + ' · saved development presentation v2'); c.setAuthor('')
        c.translate((width * MM - width * MM * scale)/2, 0); c.scale(scale, scale)
        c.setFillColorRGB(.098, .18, .22); c.setFont('DejaVuSans', 9)
        for j, line in enumerate(head): c.drawString(0, natural_height - 10 - 12*j, line)
        positions = []
        for i, g in enumerate(groups):
            row, col = divmod(i, 2); x = col * (cw + gap) * MM
            top = natural_height - head_h - sum(row_heights[:row]) - row * gap * MM
            c.setFont('DejaVuSans-Bold', 9.5); c.drawString(x, top - 11, g['title'])
            y = top - 19 - g['image_h']
            c.drawImage(ImageReader(BytesIO(g['path'].read_bytes())), x, y, width=cw*MM, height=g['image_h'])
            c.setFont('DejaVuSans', 8.5)
            for j, line in enumerate(g['notes']): c.drawString(x, y-13-11*j, line)
            cap = g['capture']; mincss = min(20, cap['minimum_svg_font_css_px'] or 20)
            positions.append({'capture': cap['name'], 'sha256': cap['sha256'], 'selector': cap['selector'],
                              'crop_css_px': cap['crop_css_px'], 'control_state': cap['control_state'],
                              'width_mm': cw*scale, 'minimum_critical_font_pt': mincss*cw*MM/cap['crop_css_px']['width']*scale,
                              'external_annotation': ' '.join(g['notes'])})
        c.showPage(); c.save()
        minimum = min(p['minimum_critical_font_pt'] for p in positions)
        e = {'name': name, 'width_mm': width, 'height_mm': physical_h/MM,
             'natural_height_mm': natural_height/MM, 'global_scale': scale,
             'minimum_critical_font_pt': minimum, 'recommended': minimum >= 8,
             'format': 'Raster browser captures with vector panel lettering/editorial annotations; not a vector dashboard.',
             'panels': positions, 'pdf_sha256': sha(pdf)}
        for dpi, suffix in [(300, ''), (96, '_proof_96dpi')]:
            subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-singlefile', str(pdf), str(out/(name+suffix))], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        e['png_sha256'] = sha(out / (name + '.png')); records.append(e)
        verdict = 'Preferred candidate' if e['recommended'] else 'Reduction trial only: use the readable paired alternatives'
        (out / (name + '.html')).write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>{name} · actual-size proof</title><style>body{{font:17px/1.5 "DejaVu Sans",sans-serif;background:#f4f6f7;color:#192e38;margin:24px}}.paper{{width:{width}mm;background:white}}img{{width:100%;display:block}}a{{color:#176b72}}</style><p><a href="../gallery/index.html">Gallery</a> · <a href="{name}.pdf">PDF</a> · <a href="{name}.png">300 dpi PNG</a></p><h1>{name}</h1><p>{verdict}. Width {width:.4f} mm; critical text {minimum:.2f} pt.</p><p>{e['format']}</p><p>CSS physical units are a screen proof, not a calibrated print. Print PDF at 100%.</p><div class="paper"><img src="{name}_proof_96dpi.png" alt="{name} at publication width"></div></html>''')
    (root / 'figure_manifest.json').write_text(json.dumps({
        'template_manifest': 'artifacts/predraft_v1/template/manifest.json',
        'template_manifest_sha256': sha('artifacts/predraft_v1/template/manifest.json'),
        'textwidth_mm': width, 'columnsep_mm': gap, 'panel_width_mm': cw,
        'font': 'Local DejaVu Sans', 'export_dpi': 300, 'figures': records,
    }, indent=2) + '\n')
    print([(e['name'], round(e['height_mm'], 1), round(e['minimum_critical_font_pt'], 2)) for e in records])

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default='artifacts/presentation_v2')
    compose(ap.parse_args().output)
