"""Actual screenshot excerpts at verified SCITEPRESS widths; no global reduction."""
import argparse,hashlib,json,subprocess
from io import BytesIO
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader,simpleSplit
MM=72/25.4

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compose(root):
 root=Path(root);out=root/'figures';out.mkdir(exist_ok=True)
 template=json.loads(Path('artifacts/predraft_v1/template/manifest.json').read_text());width=template['textwidth_mm'];cw=template['columnwidth_mm'];gap=template['columnsep_mm']
 captures={r['name']:r for r in json.loads((root/'capture_manifest.json').read_text())['captures']}
 for n in ['DejaVuSans','DejaVuSans-Bold']:pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+n+'.ttf'))
 figures=[('figure1',None,[('personal','(a) Personal progress',None),('observations','(b) Limited observations',None)]),('figure2','Case B · focal weeks 8–11 · day 83 · same person, measurement and scale',[('reference-course','(a) Recent presentation peers',None),('reference-early_stage','(b) Earlier-period peers',None)]),('figureS1','Requested: recent weeks 10–11, compared with own history and presentation peers',[('incomplete-answers','(a) Saved agent selections','Agent-selected peer answers: weeks 0–3. The recent-peer answer is omitted.'),('baseline-answers','(b) Saved enumeration selections','Baseline: explicit recent-peer insufficiency. The personal answer remains separate.')]),('figureS2',None,[('assessments','Assessment activity',None)])]
 entries=[]
 for name,shared,panels in figures:
  paperw=width if len(panels)>1 else cw
  sharedlines=simpleSplit(shared or '', 'DejaVuSans',9,paperw*MM);sharedheight=len(sharedlines)*12+(6 if shared else 0)
  gs=[]
  for cap,title,note in panels:
   record=captures[cap];p=root/record['file'];assert sha(p)==record['sha256']
   with Image.open(p) as im:iw,ih=im.size
   h=cw*MM*ih/iw;notes=simpleSplit(note or '','DejaVuSans',8.5,cw*MM)
   gs.append({'path':p,'capture':cap,'title':title,'height':h,'notes':notes,'total':19+h+(7+11*len(notes) if notes else 0),'source':record})
  height=sharedheight+max(g['total'] for g in gs)
  pdf=out/f'{name}.pdf';c=canvas.Canvas(str(pdf),pagesize=(paperw*MM,height),invariant=1,initialFontName='DejaVuSans');c.setTitle(name+' · saved development excerpts');c.setAuthor('AgenticPerformanceMonitor pre-draft v1');c.setFillColorRGB(.098,.18,.22)
  c.setFont('DejaVuSans',9)
  for i,line in enumerate(sharedlines):c.drawString(0,height-10-i*12,line)
  placements=[]
  for i,g in enumerate(gs):
   x=i*(cw+gap)*MM;top=height-sharedheight;c.setFont('DejaVuSans-Bold',9.5);c.drawString(x,top-11,g['title']);bottom=top-19-g['height'];c.drawImage(ImageReader(BytesIO(g['path'].read_bytes())),x,bottom,width=cw*MM,height=g['height'])
   c.setFont('DejaVuSans',8.5)
   for j,line in enumerate(g['notes']):c.drawString(x,bottom-13-j*11,line)
   fontpt=min(20,g['source']['minimum_svg_font_css_px'] or 20)*cw*MM/g['source']['crop_css_px']['width']
   placements.append({'capture':g['capture'],'capture_sha256':sha(g['path']),'crop_css_px':g['source']['crop_css_px'],'capture_selector':g['source']['selector'],'physical_width_mm':cw,'minimum_body_font_pt':fontpt,'external_annotation':' '.join(g['notes'])})
  c.showPage();c.save();entries.append({'name':name,'width_mm':paperw,'height_mm':height/MM,'pdf_sha256':sha(pdf),'minimum_critical_font_pt':min(p['minimum_body_font_pt'] for p in placements),'panels':placements,'format':'Raster browser captures; vector panel labels/editorial annotations. Not a vector dashboard.','global_scaling':1})
 # Matplotlib-produced PDF/SVG are genuine vector figures, at the same width.
 for name,h in [('figure3',4.6*25.4),('figure4',3.35*25.4)]:entries.append({'name':name,'width_mm':width,'height_mm':h,'minimum_critical_font_pt':8 if name=='figure3' else 8.5,'format':'Genuine vector PDF and SVG (text, paths, rectangles); not a screenshot.','pdf_sha256':sha(out/f'{name}.pdf')})
 for e in entries:
  name=e['name']
  for dpi,suffix in [(300,''),(96,'_proof_96dpi')]:subprocess.run(['pdftoppm','-r',str(dpi),'-png','-singlefile',str(out/f'{name}.pdf'),str(out/(name+suffix))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  e['png_sha256']=sha(out/f'{name}.png')
  (out/f'{name}.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>{name} · final-size proof</title><style>body{{font:17px/1.5 "DejaVu Sans",sans-serif;margin:30px;color:#192e38;background:#f3f6f7}}.paper{{width:{e['width_mm']}mm;background:white}}.paper img{{display:block;width:100%}}a{{color:#176b72}}</style><p><a href="../gallery/index.html">Gallery</a> · <a href="{name}.pdf">PDF</a> · <a href="{name}.png">300 dpi PNG</a></p><h1>{name}</h1><p>Final width {e['width_mm']:.4f} mm; critical text ≥ {e['minimum_critical_font_pt']:.2f} pt. CSS millimetres are not a calibrated screen ruler. Print the official-template proof at 100%, without fit-to-page scaling.</p><p>{e['format']}</p><div class="paper"><img src="{name}_proof_96dpi.png" alt="{name} at final placement size"></div></html>''')
 manifest={'template_manifest':'template/manifest.json','textwidth_mm':width,'columnsep_mm':gap,'panel_width_mm':cw,'device_scale_factor':3,'screenshot_font':'DejaVu Sans','raster_export_dpi':300,'critical_svg_text':'22 SVG units at 500-unit canvas, 470 CSS px or 440 CSS px content widths; ≥8.7 pt in these placements.','figures':entries}
 (root/'figure_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print([(e['name'],round(e['height_mm'],1),round(e['minimum_critical_font_pt'],2)) for e in entries])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');compose(p.parse_args().output)
