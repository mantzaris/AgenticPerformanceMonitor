"""Four figure/caption pages in the archived unmodified official template."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def proof(root):
    root = Path(root).resolve(); out = root/'proof'; out.mkdir(exist_ok=True)
    official = Path('artifacts/predraft_v1/template/official')
    for name in ['article.cls', 'SCITEPRESS.sty', 'apalike.sty', 'apalike.bst']:
        shutil.copyfile(official/name, out/name)
        assert sha(official/name) == sha(out/name)
    captions = json.loads(Path('docs/presentation_v2/captions.json').read_text())
    source = r'''\documentclass[a4paper,twoside]{article}
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
\pdfinfo{/Title (Saved dashboard presentation v2 figure proof) /Author ()}
\begin{document}
\typeout{PROOF-TEXTWIDTH=\the\textwidth}
\typeout{PROOF-COLUMNSEP=\the\columnsep}
\typeout{PROOF-TEXTHEIGHT=\the\textheight}
\twocolumn
'''
    for name in ['figure1', 'figure2', 'figureS1', 'figureS2']:
        if name == 'figureS1': source += r'\renewcommand{\thefigure}{S\arabic{figure}}\setcounter{figure}{0}'+'\n'
        caption = captions[name].replace('%', r'\%').replace('_', r'\_').replace('&', r'\&')
        source += r'\begin{figure*}[tp]\centering'+'\n'+r'\includegraphics[width=\textwidth]{../figures/'+name+'.pdf}\n'+r'\caption{'+caption+'}\n'+r'\end{figure*}\clearpage'+'\n'
    (out/'layout.tex').write_text(source+r'\end{document}'+'\n')
    env = {**os.environ, 'SOURCE_DATE_EPOCH': '1789801800', 'FORCE_SOURCE_DATE': '1'}
    for i in [1, 2]:
        r = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'layout.tex'], cwd=out, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (out/f'compile_{i}.txt').write_text(r.stdout)
        if r.returncode: raise RuntimeError(r.stdout[-2000:])
    log = (out/'layout.log').read_text()
    assert not re.search(r'Overfull|Float too large|LaTeX Error|undefined', log)
    dimensions = dict(re.findall(r'PROOF-(\w+)=(\d+\.\d+)pt', log))
    assert abs(float(dimensions['TEXTWIDTH'])/72.27-6.221) < .0001
    for dpi in [96, 150]:
        subprocess.run(['pdftoppm', '-r', str(dpi), '-png', str(out/'layout.pdf'), str(out/f'page_{dpi}dpi')], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    pages = sorted(out.glob('page_96dpi-*.png')); assert len(pages) == 4
    (out/'fonts.txt').write_text(subprocess.check_output(['pdffonts', str(out/'layout.pdf')], text=True))
    (out/'pdfinfo.txt').write_text(subprocess.check_output(['pdfinfo', str(out/'layout.pdf')], text=True))
    images = ''.join(f'<section><h2>Page {i}</h2><img src="{p.name}" alt="Official-template proof page {i}"></section>' for i, p in enumerate(pages, 1))
    (out/'index.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Presentation v2 · template proof</title><style>body{{font:17px/1.5 "DejaVu Sans",sans-serif;color:#192e38;background:#f4f6f7;margin:24px}}img{{display:block;width:210mm}}a{{color:#176b72}}</style><h1>Official-template figure proof</h1><p><a href="../gallery/index.html">Gallery</a> · <a href="layout.pdf">A4 PDF</a> · <a href="layout.tex">LaTeX source</a></p><p>Unmodified SCITEPRESS margins and captions. Print at 100%; CSS dimensions are not a calibrated print. This is a figure proof, not a manuscript revision.</p>{images}</html>''')
    (out/'manifest.json').write_text(json.dumps({'pages': 4, 'pdf_sha256': sha(out/'layout.pdf'),
        'dimensions_tex_pt': dimensions, 'official_files': {n: sha(out/n) for n in ['article.cls', 'SCITEPRESS.sty', 'apalike.sty', 'apalike.bst']},
        'caption_font': 'Official SCITEPRESS small, 9 pt', 'geometry_changed': False,
        'source_date_epoch': env['SOURCE_DATE_EPOCH'], 'purpose': 'Figure/caption proof only; manuscript unchanged'}, indent=2)+'\n')
    for suffix in ['*.aux', '*.log']:
        for p in out.glob(suffix): p.unlink()
    print('Compiled four official-template proof pages')

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', default='artifacts/presentation_v2')
    proof(p.parse_args().output)
