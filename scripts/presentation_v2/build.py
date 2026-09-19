"""Build presentation v2 from the six prescribed saved development dashboards."""
import argparse
import os
from pathlib import Path
from trajectory_dashboards.common import read_json, write_json, file_hash
from trajectory_dashboards.presentation_v1.model import EXAMPLES, load
from trajectory_dashboards.presentation_v2.render import render

LABELS = {
    'personal': ('Personal progress', 'Earlier and recent windows, with separate personal and peer answers.'),
    'references': ('Reference comparison', 'Select a saved comparison. The person stays fixed; the reference changes.'),
    'observations': ('Limited observations', 'Recorded zero, administrative ineligibility and unavailable quantities.'),
    'assessments': ('Assessment activity', 'Submission measures and dated assessment states, without achievement ratings.'),
    'incomplete': ('Preserved incomplete answer', 'The original earlier-window peer selections and personal insufficiency.'),
    'baseline': ('Enumeration counterpart', 'The same question with a separately explicit recent-peer insufficiency answer.'),
}

def build(root):
    root = Path(root).resolve()
    history = read_json('artifacts/presentation_v2/historical_inventory.json')
    assert not any(root == Path(n).resolve() or root in Path(n).resolve().parents for n in history['files']), 'Output would overlap historical files'
    root.mkdir(parents=True, exist_ok=True)
    entries = []
    for slug, label, method, case in EXAMPLES:
        source = Path('artifacts/stage6/comparison') / method / case / 'accepted'
        model = load(source, label)
        entry = render(model, root / 'gallery' / slug)
        entries.append({**entry, 'slug': slug, 'anonymous_label': label, 'method': method,
                        'case': case, 'source_person_id': model['question']['person_id']})
    software = [*Path('src/trajectory_dashboards/presentation_v2').glob('*'),
                *Path('src/trajectory_dashboards/presentation_v1').glob('*'),
                *Path('src/trajectory_dashboards/predraft_v1').glob('*')]
    write_json(root / 'source_manifest.json', {
        'starting_commit': history['starting_commit'], 'entries': entries,
        'source_policy': 'Accepted selected development evidence only; no unselected results, rubric, or new analysis.',
        'software_hashes': {str(p): file_hash(p) for p in software if p.is_file()},
        'new_experimental_generations': 0, 'scoring_changes': False,
    })
    cards = ''.join(f'''<a class="case-card" href="{e['slug']}/index.html"><img src="../captures/{e['slug']}.png" alt="{LABELS[e['slug']][0]} saved-output preview"><div><span>{e['anonymous_label']} · {'Enumeration' if e['method']=='baseline' else 'Compact A'}</span><h2>{LABELS[e['slug']][0]}</h2><p>{LABELS[e['slug']][1]}</p></div></a>''' for e in entries)
    figures = [('figure1', 'Adaptation: personal progress and limited observations'),
               ('figure2', 'A controlled saved-reference change'), ('figureS1', 'Correct numbers, incomplete answer'),
               ('figureS2', 'Additional adaptation: references and assessments'),
               ('figure1_grid', 'Four-panel reduction trial (not recommended at paper size)')]
    links = ''.join(f'<li><b>{title}</b><br><a href="../figures/{n}.html">Final-size proof</a> · <a href="../figures/{n}.pdf">PDF</a> · <a href="../figures/{n}.png">PNG</a></li>' for n, title in figures)
    docs = os.path.relpath(Path('docs/presentation_v2').resolve(), root / 'gallery')
    old = os.path.relpath(Path('artifacts/predraft_v1/gallery/index.html').resolve(), root / 'gallery')
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Saved analytical dashboards · presentation v2</title><style>
body{{font:17px/1.5 "DejaVu Sans",sans-serif;background:#f4f6f7;color:#192e38;margin:0}}main{{max-width:1150px;margin:auto;padding:32px 24px 60px}}h1{{font-size:36px;line-height:1.15;margin:8px 0 16px;max-width:850px}}header p{{max-width:840px}}.eyebrow{{color:#176b72;font-weight:700;font-size:14px}}a{{color:#176b72}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:24px;margin:30px 0}}.case-card{{display:grid;grid-template-columns:160px 1fr;gap:20px;text-decoration:none;color:inherit;background:white;border:1px solid #d9e2e5;border-radius:8px;padding:16px}}.case-card img{{width:160px;height:220px;object-fit:cover;object-position:top;border:1px solid #d9e2e5}}.case-card h2{{font-size:23px;line-height:1.2;margin:10px 0}}.case-card span{{font-size:13px;color:#176b72}}.case-card p{{font-size:15px}}section{{background:white;border:1px solid #d9e2e5;border-radius:8px;padding:24px;margin:24px 0}}li{{margin:16px 0}}a:focus-visible{{outline:3px solid #ad7235;outline-offset:4px}}@media(max-width:800px){{.grid{{grid-template-columns:1fr}}h1{{font-size:28px}}.case-card{{grid-template-columns:110px 1fr;gap:14px}}.case-card img{{width:110px;height:160px}}}}</style></head><body><main><header><div class="eyebrow">PRESENTATION V2 · SAVED DEVELOPMENT EXAMPLES</div><h1>Different questions.<br>Evidence kept in context.</h1><p>Explore the selected answers, their original calculation and compiler context. These are new renderings of saved results, with no new inference, accuracy evaluation or usability study.</p></header><div class="grid">{cards}</div><section><h2>Paper figure candidates</h2><p>Designed for the verified SCITEPRESS text width of 158.0134 mm. Main candidates use readable paired panels; the four-view trial is retained for inspection.</p><ul>{links}</ul><p><a href="../proof/index.html">Official-template figure proof</a> · <a href="{docs}/CAPTIONS.md">Captions</a></p></section><section><h2>Evidence and reproduction</h2><p>Agent or enumeration: answer selection. Analytical tools: all numerical values. Original compiler: tagged required context. Presentation v2: layout, chart styling and saved-reference emphasis. Numerical binding and question completeness are separate properties.</p><p><a href="../source_manifest.json">Sources and hashes</a> · <a href="../capture_manifest.json">Capture states</a> · <a href="../figure_manifest.json">Dimensions and figure provenance</a> · <a href="{docs}/REPRODUCTION.md">Reproduction</a> · <a href="{old}">Preserved pre-draft gallery</a></p></section></main></body></html>'''
    (root / 'gallery' / 'index.html').write_text(page)
    print('Built six saved-content views:', root)

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', default='artifacts/presentation_v2')
    build(p.parse_args().output)
