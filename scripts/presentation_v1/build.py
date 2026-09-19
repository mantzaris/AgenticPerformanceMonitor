"""Generate the offline gallery from selected saved Stage 6 artifacts only."""
import argparse
from pathlib import Path
import html
import os
from trajectory_dashboards.presentation_v1.model import EXAMPLES, load
from trajectory_dashboards.presentation_v1.render import render
from trajectory_dashboards.common import read_json, write_json, file_hash


def build(output):
    output=Path(output).resolve()
    if 'presentation' not in output.name:
        raise ValueError('Use a clearly named presentation output directory')
    gallery=output/'gallery';gallery.mkdir(parents=True,exist_ok=True)
    entries=[]
    for slug,label,method,case in EXAMPLES:
        source=Path(f'artifacts/stage6/comparison/{method}/{case}/accepted')
        model=load(source,label)
        entry=render(model,gallery/slug)
        entries.append({**entry,'slug':slug,'anonymous_label':label,'source_person_id':model['question']['person_id'],
                        'method':method,'case':case,'question':model['question'],
                        'selection_status':model['selection_status'], 'source_spec':str(source/'spec.json')})
    css=Path('src/trajectory_dashboards/presentation_v1/style.css').read_text()
    descriptions={
        'personal':('Personal progress','Earlier and recent activity, followed by the separately selected peer comparisons.'),
        'references':('Reference comparison','Switch among three saved comparisons. The person and focal window stay fixed.'),
        'observations':('Limited observations','Explicit unavailable measurements beside eligibility, zero-click and assessment states.'),
        'assessments':('Assessment activity','Submission measures and dated record states; grades and learning are not inferred.'),
        'incomplete':('Incomplete agent answer','Correct numbers with an omitted recent peer answer. The original failure is preserved.'),
        'baseline':('Same question · baseline','The saved enumeration result answers personal and peer support separately.'),
    }
    cards=''.join(f'<a class="gallery-card" href="{e["slug"]}/index.html"><h2>{html.escape(e["anonymous_label"])} · {descriptions[e["slug"]][0]}</h2><img src="../captures/{e["slug"]}-expanded.png" alt="Preview of {descriptions[e["slug"]][0]}" loading="lazy"><p>{descriptions[e["slug"]][1]}</p><p>{html.escape(e["selection_status"])}</p></a>' for e in entries)
    figures=[('figure1','Figure 1 · readable two-panel adaptation candidate'),('figureS2','Figure S2 · observation and assessment views'),('figure2','Figure 2 · controlled saved-reference change'),('figureS1','Figure S1 · correct numbers, incomplete answer'),('figure1_grid','Four-panel overview · reduction proof, not recommended at 180 mm')]
    figure_links=''.join(f'<li>{title}: <a href="../figures/{name}.html">view and paper-size proof</a> · <a href="../figures/{name}.png">PNG</a> · <a href="../figures/{name}.pdf">PDF</a></li>' for name,title in figures)
    captions_link=os.path.relpath(Path('docs/presentation_v1/CAPTIONS.md').resolve(),gallery)
    review_link=os.path.relpath(Path('PRESENTATION_V1_REVIEW.md').resolve(),gallery)
    content=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Saved evidence · presentation gallery</title><style>{css}.gallery-card img{{object-fit:contain;object-position:center;height:320px;background:#f6f8f8}}</style></head><body><main class="gallery"><header><div class="eyebrow">AGENTIC PERFORMANCE MONITOR · PRESENTATION V1</div><h1>One evidence system.<br>Different analytical questions.</h1><p>Explore new renderings of saved Stage 6 development cases. The agent selected answers; deterministic tools calculated their values; the original compiler supplied tagged context. This presentation changes layout and emphasis.</p><p>No new inference, success-rate calculation or usability evaluation. Reference controls select saved analysis. Anonymous labels are stable within this package.</p></header><div class="gallery-grid">{cards}</div><section class="figures-list"><h2>Figure candidates and reduction proofs</h2><ul>{figure_links}</ul><p>PDF composites contain raster browser captures and vector panel labels; they are not vector dashboards. Each case also includes genuine SVG chart assets.</p><p><a href="../source_manifest.json">Source manifest and original identifiers</a> · <a href="../capture_manifest.json">Capture manifest</a> · <a href="{html.escape(captions_link)}">Captions</a> · <a href="{html.escape(review_link)}">Review entry point</a></p></section></main></body></html>'''
    (gallery/'index.html').write_text(content)
    inv=read_json('artifacts/presentation_v1/historical_inventory.json')
    write_json(output/'source_manifest.json',{'starting_commit':inv['starting_commit'],'dataset':'Saved OULAD development results',
        'scope':'Read-only saved selected evidence; no agent, evaluator, backend or reserved-data execution',
        'selection_rule':'User-prespecified compact_a 01/05/09/17; incomplete 15 and its baseline. All candidates suitable; no replacements.',
        'entries':entries,'software_hashes':{str(p):file_hash(p) for p in sorted(Path('src/trajectory_dashboards/presentation_v1').glob('*')) if p.is_file()},
        'deduplication':'Only personal claims with identical original wording, units, person/cutoff, windows, all personal numerical fields and selection origin. Original indices and IDs retained. Every original panel remains accessible, including differing bootstrap intervals.',
        'numerical_check':'Saved evidence digests are checked on build; separate verify.py runs the historical source-bound validator. Neither check establishes completeness.',
        'new_inference_generations':0})
    print(f'Built {len(entries)} saved dashboards: {gallery}/index.html')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='artifacts/presentation_v1')
    build(parser.parse_args().output)
