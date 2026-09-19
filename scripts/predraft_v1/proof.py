"""Compile layout/caption proof using the byte-unmodified official template."""
import argparse,hashlib,json,os,re,shutil,subprocess
from pathlib import Path
EPOCH='1789792909'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def escape(t):
 for a,b in [('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#')]:t=t.replace(a,b)
 return t

def proof(root):
 root=Path(root).resolve();out=root/'proof';out.mkdir(exist_ok=True)
 official=Path('artifacts/predraft_v1/template/official').resolve()
 for name in ['article.cls','SCITEPRESS.sty','apalike.sty','apalike.bst']:
  shutil.copyfile(official/name,out/name);assert sha(out/name)==sha(official/name)
 captions=json.loads(Path('docs/predraft_v1/captions.json').read_text())
 preamble=r'''\documentclass[a4paper,twoside]{article}
\usepackage{graphicx}
\usepackage{calc}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{multicol}
\usepackage{pslatex}
\usepackage{apalike}
\usepackage{algorithm2e}
\usepackage[bottom]{footmisc}
\usepackage{SCITEPRESS}
\pdfinfoomitdate=1
\pdftrailerid{}
\begin{document}
\typeout{PROOF-TEXTWIDTH=\the\textwidth}
\typeout{PROOF-COLUMNSEP=\the\columnsep}
\typeout{PROOF-TEXTHEIGHT=\the\textheight}
\twocolumn
'''
 body=[]
 for name in ['figure1','figure2','figure3','figure4','figureS1','figureS2']:
  if name=='figureS1':body.append(r'\renewcommand{\thefigure}{S\arabic{figure}}\setcounter{figure}{0}')
  width=r'\textwidth' if name!='figureS2' else '75.0067mm'
  body.append(r'\begin{figure*}[tp]\centering'+'\n'+r'\includegraphics[width='+width+']{../figures/'+name+'.pdf}\n'+r'\caption{'+escape(captions[name])+'}\n'+r'\label{fig:'+name+'}\n'+r'\end{figure*}\clearpage'+'\n')
 source=preamble+'\n'.join(body)+r'\end{document}'+'\n';(out/'layout.tex').write_text(source)
 env={**os.environ,'SOURCE_DATE_EPOCH':EPOCH,'FORCE_SOURCE_DATE':'1'}
 for i in range(2):
  r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','layout.tex'],cwd=out,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  (out/f'compile_{i+1}.txt').write_text(r.stdout)
  if r.returncode:raise RuntimeError(r.stdout[-4000:])
 log=(out/'layout.log').read_text();assert not re.search(r'Overfull|Float too large|LaTeX Error',log)
 dimensions=dict(re.findall(r'PROOF-(\w+)=(\d+\.\d+)pt',log));assert abs(float(dimensions['TEXTWIDTH'])/72.27-6.221)<.0001
 info=subprocess.check_output(['pdfinfo',str(out/'layout.pdf')],text=True);(out/'pdfinfo.txt').write_text(info)
 for dpi in [96,150]:subprocess.run(['pdftoppm','-r',str(dpi),'-png',str(out/'layout.pdf'),str(out/f'page_{dpi}dpi')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 pages=sorted(out.glob('page_96dpi-*.png'));assert len(pages)==6,len(pages)
 html=''.join(f'<section><h2>Page {i}</h2><img style="width:210mm" src="{p.name}" alt="Official-template proof page {i}"></section>' for i,p in enumerate(pages,1))
 (out/'index.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Official-template figure layout proof</title><style>body{{font:17px/1.5 "DejaVu Sans",sans-serif;background:#eef2f4;margin:24px;color:#192e38}}img{{display:block;background:white}}a{{color:#176b72}}</style><h1>Layout and caption proof</h1><p><a href="../gallery/index.html">Gallery</a> · <a href="layout.pdf">A4 proof PDF</a> · <a href="layout.tex">LaTeX source</a></p><p>Unmodified official SCITEPRESS template. Normal two-column figure floats and 9 pt captions; no geometry or caption shrinking. Not a manuscript draft. Print at 100%, without fit-to-page. CSS dimensions are not calibrated physical screen dimensions.</p>{html}</html>')
 (out/'manifest.json').write_text(json.dumps({'template_files':{p.name:sha(p) for p in out.glob('*.sty')},'article_cls_sha256':sha(out/'article.cls'),'source_sha256':sha(out/'layout.tex'),'pdf_sha256':sha(out/'layout.pdf'),'pages':len(pages),'dimensions_tex_pt':dimensions,'pdf_dimensions':'A4, 210 x 297 mm','normal_figures':'figure* [tp], clearpage between isolated layout proofs','caption_font':'Unmodified SCITEPRESS caption package font=small (9 pt)','geometry_changes':False,'source_date_epoch':EPOCH,'pdflatex':subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0],'figures':[{'path':str(p.relative_to(root)),'sha256':sha(p)} for p in sorted((root/'figures').glob('*.pdf'))]},indent=2)+'\n')
 for p in out.glob('*.aux'):p.unlink()
 for p in out.glob('*.log'):p.unlink()
 print('Compiled official-template proof:',len(pages),'pages',dimensions)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');proof(p.parse_args().output)
