"""Controlled numeric binding and offline exports; no executable model content."""
import html
import json
from pathlib import Path
import altair as alt
import vl_convert as vlc
from ..common import write_json, read_json, digest
from ..dashboard import panel_chart, claim_text as legacy_claim_text
from ..analysis import LIMITATIONS
from ..prepare import FEATURES
from .core import Question
from ..stage2.integrity import validate


CONCLUSIONS = {
    "descriptive": "Descriptive results; no claim that the interpretation changes across references.",
    "same_direction": "The selected recent activity contrasts have the same direction across the selected references. Magnitudes can differ. This is not a significance or invariance test.",
    "direction_differs": "The sign of the selected recent activity contrast differs across the selected references. The reference questions differ; this is not a causal explanation or significance test.",
    "insufficient_evidence": "At least one selected comparison or personal-history contrast has insufficient observed support. Available descriptive quantities remain visible with their counts."
}


def claim_text(claim, e):
    text = legacy_claim_text(claim, e)
    if claim.template == "measurement_limits":
        return text
    prefix = f"{e.feature} ({e.unit}): "
    if claim.template == "personal_change" and e.summary["personal_status"] != "supported":
        s = e.summary
        text = (f"Insufficient personal comparison from weeks {s['baseline_window'][0]}–{s['baseline_window'][1]} "
                f"({s['baseline_observations']} observed weeks) to weeks {s['recent_window'][0]}–{s['recent_window'][1]} "
                f"({s['recent_observations']} observed weeks).")
    return prefix + text


def render(engine, question, spec, evidence, output, origin="deterministic", parent=None):
    q = Question.model_validate(question)
    spec,bound = validate(engine,q,spec,evidence)
    out = Path(output)
    if (out/"spec.json").exists():
        raise ValueError("Preserve original export: choose a new output directory")
    out.mkdir(parents=True,exist_ok=True)
    claims = [{"evidence_id":c.evidence_id,"template":c.template,"text":claim_text(c,bound[c.evidence_id]),"selection_origin":origin,"wording_and_values_origin":"deterministic compiler"} for c in spec.claims]
    maxima={f:max([1.0]+[v for e in bound.values() if e.feature==f for k,v in e.summary.items() if k in {"focal_mean","peer_mean","peer_ci_high"} and v is not None])*1.05 for f in FEATURES}
    chart=alt.vconcat(*[panel_chart(p,bound[p.evidence_id],maxima[bound[p.evidence_id].feature]) for p in spec.panels],spacing=28).resolve_scale(color="independent").configure(font="sans-serif",background="#fbfaf7").configure_view(stroke=None).configure_axis(labelFontSize=11,titleFontSize=12).configure_title(anchor="start",color="#142e38",fontSize=17,subtitleFontSize=11)
    chart_spec=chart.to_dict()
    write_json(out/"chart.vl.json",chart_spec)
    svg=vlc.vegalite_to_svg(chart_spec)
    (out/"dashboard.svg").write_text(svg)
    (out/"dashboard.png").write_bytes(vlc.vegalite_to_png(chart_spec,scale=1))
    write_json(out/"spec.json",spec.model_dump())
    write_json(out/"evidence.json",{k:e.model_dump() for k,e in bound.items()})
    write_json(out/"question.json",q.model_dump())
    context = [*LIMITATIONS,"Earlier-stage references answer a different question; they are not automatically fairer or causally adjusted.","All task focal people are excluded from the shared development peer pool."]
    binding={"validation":"PASS","validator":"independent row-wise/source-bound numerical verification","selection_origin":origin,"claims":claims,"conclusion":CONCLUSIONS[spec.conclusion],"compiler_supplied_context":context,"evidence_hashes":{k:digest(e.model_dump()) for k,e in bound.items()},"parent":parent,"profile":engine.registry.profile(q),"numeric_values_origin":"analytical results only; model schema accepts no arbitrary numbers/text"}
    write_json(out/"bound.json",binding)
    cards="".join(f'<li>{html.escape(c["text"])} <a href="#{c["evidence_id"]}">Inspect evidence</a></li>' for c in claims)
    inspectors="".join(f'<details id="{eid}"><summary>{html.escape(e.reference_label)} · {html.escape(e.feature)} · {eid}</summary><pre>{html.escape(json.dumps(e.model_dump(),indent=2))}</pre></details>' for eid,e in bound.items())
    profile=engine.registry.profile(q)
    form='''<h2>Run a follow-up locally</h2><p>Choose another admissible reference or window. This submits a new analysis and preserves this result. Serve this directory using the Stage 3 follow-up server.</p><form method="post" action="/followup"><input type="hidden" name="parent" value="'''+html.escape(str(out),quote=True)+'''"><label>Reference <select name="reference">'''+"".join(f'<option value="{r}">{html.escape(r)}</option>' for r in engine.cfg['references'])+'''</select></label> <label>Window profile <select name="profile">'''+"".join(f'<option value="{name}"'+(' selected' if name==q.profile else '')+f'>{name}: baseline {v["baseline"]}, recent {v["recent"]}, cutoff {v["cutoff_day"]}</option>' for name,v in engine.cfg['profiles'].items())+'''</select></label> <button type="submit">Analyze and save follow-up</button></form>'''
    body=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(q.question_id)} · Stage 3</title><style>body{{font:16px/1.55 system-ui,sans-serif;background:#fbfaf7;color:#142e38;margin:0}}main{{max-width:1100px;margin:auto;padding:32px}}h1{{font-size:28px}}.claims{{background:white;border-left:4px solid #286f83;padding:16px 30px}}.chart{{overflow-x:auto}}li{{margin:12px 0}}details{{border-top:1px solid #bbb;padding:12px 0}}pre{{white-space:pre-wrap;max-height:420px;overflow:auto;background:#eef1f0;padding:16px;font-size:12px}}select,button{{padding:8px;margin:8px}}a{{color:#286f83}}</style><main><p>STAGE 3 · OULAD · DEVELOPMENT PILOT</p><h1>{html.escape(q.text)}</h1><p>{q.course} · source person {q.person_id} · cutoff day {q.cutoff_day} · profile {q.profile}: baseline {profile['baseline']}, recent {profile['recent']}</p><p>Selection: {html.escape(origin)}. Numerical wording and measurement context: deterministic compiler.</p><div class="claims"><strong>{html.escape(CONCLUSIONS[spec.conclusion])}</strong><ul>{cards}</ul></div><div class="chart">{svg}</div><h2>Measurement and interpretation context</h2><ul>{''.join('<li>'+html.escape(x)+'</li>' for x in context)}</ul><h2>Evidence inspector</h2>{inspectors}{form}<footer>OULAD: Kuzilek, Hlosta &amp; Zdrahal, CC BY 4.0, DOI 10.24432/C5KK69. Descriptive development data, not held-out evaluation. No individual prediction intervals.</footer></main></html>'''
    (out/"dashboard.html").write_text(body)
    return binding


def replay(engine, source, output):
    source=Path(source)
    binding=read_json(source/"bound.json")
    return render(engine,read_json(source/"question.json"),read_json(source/"spec.json"),read_json(source/"evidence.json"),output,origin=binding['selection_origin'],parent=binding.get('parent'))
