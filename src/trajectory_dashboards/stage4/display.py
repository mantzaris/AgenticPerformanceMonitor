"""Reuse the Stage 3 renderer; add inspectable selection/structure provenance."""
import html
import json
from pathlib import Path
from ..common import read_json, write_json
from ..stage3.display import render as historical_render
from .semantic import full_provenance


def render(engine, question, spec, evidence, output, origin='deterministic', provenance=None):
    provenance = provenance or full_provenance(spec, 'baseline')
    binding = historical_render(engine, question, spec, evidence, output, origin=origin)
    out = Path(output)
    write_json(out/'selection_provenance.json', provenance)
    for i, claim in enumerate(binding['claims']):
        claim['selection_origin'] = provenance['claims'][i]['origin']
    binding['interface_provenance'] = provenance
    write_json(out/'bound.json', binding)
    body = (out/'dashboard.html').read_text().replace('STAGE 3', 'STAGE 4').replace('· Stage 3', '· Stage 4')
    start, end = body.index('<h2>Run a follow-up locally</h2>'), body.index('<footer>')
    note = '<h2>Answer selection and compiler provenance</h2><p>Every comparison/change claim follows an explicit selection. Required layout and shared context may be compiler supplied; see the record below.</p><details><summary>Inspect interface provenance</summary><pre>'+html.escape(json.dumps(provenance,indent=2))+'</pre></details><p>Frozen Stage 4 export. Use the documented replay command; this page does not start a follow-up server.</p>'
    (out/'dashboard.html').write_text(body[:start]+note+body[end:])
    return binding


def replay(engine, source, output):
    source = Path(source)
    return render(engine, read_json(source/'question.json'), read_json(source/'spec.json'),
                  read_json(source/'evidence.json'), output,
                  origin=read_json(source/'bound.json')['selection_origin'],
                  provenance=read_json(source/'selection_provenance.json'))
