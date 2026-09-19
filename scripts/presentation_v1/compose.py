"""Compose actual browser captures. PDFs contain raster panels + vector labels.

Run with system python3 (Pillow + ReportLab) in the documented environment.
SVG charts are exported by build.py and remain genuine vector assets.
"""
import argparse
import hashlib
import json
import subprocess
from io import BytesIO
from pathlib import Path
from PIL import Image
import PIL
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit, ImageReader
import reportlab

MM=72/25.4


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compose(root):
    root=Path(root).resolve();out=root/'figures';out.mkdir(parents=True,exist_ok=True)
    captures={c['name']:c for c in json.loads((root/'capture_manifest.json').read_text())['captures']}
    font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');bold=font.with_name('DejaVuSans-Bold.ttf')
    pdfmetrics.registerFont(TTFont('DejaVu',str(font)));pdfmetrics.registerFont(TTFont('DejaVu-Bold',str(bold)))
    specs=[
        ('figure1',[('personal','(a) Personal progress','Own history and a selected peer comparison.'),('references','(b) Reference comparison','Same focal measure; saved peer definitions.')]),
        ('figureS2',[('observations','(c) Limited observations','Ineligibility, recorded zeros and unavailable means.'),('assessments','(d) Assessment activity','Submission measures and dated record states.')]),
        ('figure2',[('reference-course','(a) Recent presentation peers','Person: weeks 8–11. Reference: weeks 8–11.'),('reference-early_stage','(b) Earlier presentation peers','Person: weeks 8–11. Reference: weeks 0–3.')]),
        ('figureS1',[('incomplete','(a) Saved agent answer','Reviewer annotation: the selected peer answers use weeks 0–3. The requested recent peer-support answer is omitted; personal insufficiency does not supply it.'),('baseline','(b) Saved enumeration answer','Reviewer annotation: separate personal and recent-peer insufficiency answers are present. This is the original baseline selection, not a repair to the agent.')]),
        ('figure1_grid',[('personal','(a) Personal progress','Own history and peers.'),('references','(b) Reference comparison','Saved reference definitions.'),('observations','(c) Limited observations','Unavailable is not zero.'),('assessments','(d) Assessment activity','Submission records, not grades.')]),
    ]
    results=[]
    for name,panels in specs:
        column_width=87*MM;gap=6*MM;max_height=240*MM
        geometry=[];row_heights=[]
        for index,(capture,label,note) in enumerate(panels):
            path=root/captures[capture]['file']
            assert sha(path)==captures[capture]['sha256']
            with Image.open(path) as image:
                iw,ih=image.size
            height=column_width*ih/iw
            notes=simpleSplit(note,'DejaVu',8.5,column_width)
            full_height=22+height+9+len(notes)*11
            geometry.append({'path':path,'capture':capture,'label':label,'notes':notes,'height':height,'full_height':full_height,'index':index})
        for i in range(0,len(geometry),2):
            row_heights.append(max(g['full_height'] for g in geometry[i:i+2]))
        raw_height=sum(row_heights)+(len(row_heights)-1)*18
        scale=min(1,max_height/raw_height)
        paper_width=180*MM;paper_height=raw_height*scale
        pdf=out/f'{name}.pdf';c=canvas.Canvas(str(pdf),pagesize=(paper_width,paper_height),invariant=1)
        c.setTitle(name+' · saved development dashboard captures')
        c.setAuthor('AgenticPerformanceMonitor presentation_v1')
        c.translate((paper_width-180*MM*scale)/2,0);c.scale(scale,scale)
        c.setFillColorRGB(0.098,0.18,0.22)
        placements=[]
        for g in geometry:
            row,col=divmod(g['index'],2);x=col*(column_width+gap);top=raw_height-sum(row_heights[:row])-row*18
            c.setFont('DejaVu-Bold',10);c.drawString(x,top-12,g['label'])
            image_top=top-22;image_bottom=image_top-g['height']
            # ImageReader hashes decoded image content; passing the filename
            # instead would make PDF XObject names depend on the output root.
            c.drawImage(ImageReader(BytesIO(g['path'].read_bytes())),x,image_bottom,width=column_width,height=g['height'])
            c.setFont('DejaVu',8.5)
            for i,line in enumerate(g['notes']):
                c.drawString(x,image_bottom-14-i*11,line)
            placements.append({'capture':g['capture'],'source_capture_sha256':sha(g['path']),
                               'panel_label':g['label'],'external_annotation':' '.join(g['notes']),
                               'physical_width_mm':87*scale,'physical_height_mm':g['height']/MM*scale})
        c.showPage();c.save()
        for dpi,suffix in [(300,''),(96,'_proof_96dpi')]:
            subprocess.run(['pdftoppm','-r',str(dpi),'-png','-singlefile',str(pdf),str(out/(name+suffix))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        proof_note='Preferred 180 mm wide candidate.' if name!='figure1_grid' else 'Rejected reduction proof: the four-panel layout exceeds the assumed 240 mm figure height at full width; fitting it reduces the critical text below the intended readable size. Use Figure 1 plus Figure S2.'
        html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{name} · paper-size proof</title><style>body{{font:16px/1.5 "DejaVu Sans",sans-serif;margin:24px;background:#eef2f4;color:#192e38}}a{{color:#176b72}}header{{max-width:900px}}.proof{{width:180mm;background:white;margin:24px 0}}.proof img{{display:block;width:180mm}}.large img{{max-width:100%;height:auto}}@media print{{body{{margin:0;background:white}}header,.large{{display:none}}.proof{{margin:0}}}}</style></head><body><header><p><a href="../gallery/index.html">← Gallery</a> · <a href="{name}.pdf">PDF</a> · <a href="{name}.png">300 dpi PNG</a></p><h1>{name}</h1><p>{proof_note}</p><p>Browser proof at CSS 180 mm (680.3 CSS pixels at 96 dpi). PDF size: 180 × {paper_height/MM:.1f} mm. For physical inspection, print the PDF at 100%, with no fit-to-page scaling. Screen millimetres are CSS units, not a calibrated ruler.</p><p>Raster browser screenshots with vector panel labels. The chart SVGs linked from each source page are genuine vectors. Annotations below the panels are editorial, outside the faithful interface captures.</p></header><section class="proof"><img src="{name}_proof_96dpi.png" alt="{name}: intended-size reduction proof"></section><details class="large"><summary>Inspect full-resolution composite</summary><img src="{name}.png" alt="Full-resolution figure"></details></body></html>'''
        (out/f'{name}.html').write_text(html)
        results.append({'name':name,'pdf':str(pdf.relative_to(root)),'png':f'figures/{name}.png','proof':f'figures/{name}_proof_96dpi.png',
            'physical_width_mm':180,'physical_height_mm':paper_height/MM,'scale_due_to_height_limit':scale,
            'critical_html_font_pt':18*(87*scale/552)*MM,'note':proof_note,'panels':placements,
            'pdf_sha256':sha(pdf),'png_sha256':sha(out/f'{name}.png'), 'pdf_contains':'raster browser captures and vector panel lettering/annotations; not vector dashboards'})
    manifest={'assumed_figure_box_mm':[180,240],'template':'No paper template found in the repository; 180 mm double-column width assumed.',
        'font_files':{str(p):sha(p) for p in (font,bold)},'Pillow':PIL.__version__,'ReportLab':reportlab.Version,
        'PNG_DPI':300,'proof_DPI':96,'figures':results}
    (root/'figure_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print([(r['name'],round(r['physical_height_mm'],1),round(r['critical_html_font_pt'],1)) for r in results])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/presentation_v1');compose(p.parse_args().output)
