"""CPU-only reproducible manuscript build; never executes experimental code."""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
def run(args, log):
    p = subprocess.run(args, cwd=HERE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (HERE/'checks'/log).write_text(p.stdout)
    if p.returncode:
        print(p.stdout[-7000:]);raise SystemExit(p.returncode)

if __name__ == '__main__':
    os.environ['SOURCE_DATE_EPOCH'] = '1789797600'
    os.environ['FORCE_SOURCE_DATE'] = '1'
    run([sys.executable,'scripts/generate.py'],'generate.txt')
    tex=['pdflatex','-interaction=nonstopmode','-halt-on-error','main.tex']
    run(tex,'latex_1.txt')
    run(['bibtex','main'],'bibtex.txt')
    run(tex,'latex_2.txt');run(tex,'latex_3.txt')
    run(['pdftotext','-layout','main.pdf','checks/main.txt'],'pdftotext.txt')
    run(['pdfinfo','main.pdf'],'pdfinfo.txt')
    run(['pdffonts','main.pdf'],'pdffonts.txt')
    print((HERE/'checks/pdfinfo.txt').read_text())
