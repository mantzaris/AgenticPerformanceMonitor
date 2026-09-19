"""Build separate pre-draft views from selected saved artifacts only."""
import argparse,json,os
from pathlib import Path
from trajectory_dashboards.presentation_v1.model import EXAMPLES,load
from trajectory_dashboards.predraft_v1.render import render
from trajectory_dashboards.common import write_json,file_hash

def build(root):
 root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True);entries=[]
 for slug,label,method,case in EXAMPLES:
  source=Path(f'artifacts/stage6/comparison/{method}/{case}/accepted');m=load(source,label);out=root/'gallery'/slug;entry=render(m,out)
  entries.append({**entry,'slug':slug,'anonymous_label':label,'case':case,'method':method,'source_person_id':m['question']['person_id'],'source_spec':str(source/'spec.json')})
 write_json(root/'source_manifest.json',{'starting_commit':'321439487ef0035538564f3a2829bab9df859b71','entries':entries,'inputs':'Selected saved development evidence only; no evaluator used to render','software_hashes':{str(p):file_hash(p) for p in Path('src/trajectory_dashboards/predraft_v1').glob('*.py')},'historical_presentation':'artifacts/presentation_v1','new_inference_generations':0})
 figures=[('figure1','Personal progress and limited observations'),('figure2','Controlled saved-reference switch'),('figure3','Implemented responsibility boundaries'),('figure4','Frozen Stage 6 development results'),('figureS1','Correct numbers, incomplete answer'),('figureS2','Assessment activity')]
 cards=''.join(f'<li><a href="{e["slug"]}/figure.html">{e["anonymous_label"]}: {e["slug"]}</a> · <a href="{e["slug"]}/index.html">expanded / all original content</a></li>' for e in entries)
 links=''.join(f'<li>{label}: <a href="../figures/{name}.html">size proof</a> · <a href="../figures/{name}.pdf">PDF</a> · <a href="../figures/{name}.png">PNG</a></li>' for name,label in figures)
 (root/'gallery/index.html').write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Pre-draft figure and review gallery</title><style>body{{font:18px/1.55 "DejaVu Sans",sans-serif;color:#192e38;background:#f4f7f8;margin:40px auto;max-width:1000px;padding:24px}}a{{color:#176b72}}section{{background:white;padding:20px;margin:20px 0;border:1px solid #dbe3e5}}li{{margin:10px 0}}</style><h1>Evidence-grounded dashboards</h1><p>Pre-draft preparation v1 · saved Stage 6 development outputs. No new inference or rescoring. New presentation is separate from agent selection, deterministic calculation and original compiler context.</p><section><h2>Readable interface excerpts</h2><ul>{cards}</ul><p>Presentation peers means students in the same course offering. All references use the saved development pool, exclude the focal person and task focal people, and retain their exact windows.</p></section><section><h2>Figures at the official template size</h2><ul>{links}</ul><p><a href="../proof/index.html">Official-template layout proof and rendered pages</a> · <a href="../human_review/index.html">Pending human scientific review: all 96 slots</a></p></section><section><h2>Provenance</h2><p><a href="../source_manifest.json">Selected sources</a> · <a href="../capture_manifest.json">Browser states / crops</a> · <a href="../figure_manifest.json">Final dimensions / font sizes</a> · <a href="../../presentation_v1/gallery/index.html">Preserved presentation v1</a></p></section></html>''')
 print('Built',len(entries),'views in',root)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');build(p.parse_args().output)
