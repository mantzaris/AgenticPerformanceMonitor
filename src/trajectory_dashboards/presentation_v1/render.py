"""Offline HTML, CSS and native SVG; strictly re-presents saved selected answers."""
from pathlib import Path
import html
import json
import os
from .model import FEATURES, reference_name
from .charts import num, trajectory, references, observation, assessment
from ..common import write_json


def h(x):
    return html.escape(str(x), quote=True)


def window(w):
    return f"weeks {w[0]}–{w[1]}"


def origin_label(origin, model):
    if origin == "compiler_supplied":
        return "Original compiler context"
    return "Baseline selected" if model["method"].startswith("Deterministic") else "Agent selected"


def evidence_link(eid, label="Evidence"):
    return f'<a class="evidence-link" href="#evidence-{eid}">{h(label)} <span aria-hidden="true">↗</span></a>'


def personal_card(claim, model):
    e = model["evidence"][claim["evidence_id"]];s=e["summary"]
    header=f'<div class="card-label">Personal history <span class="origin">{origin_label(claim["origin"],model)}</span></div>'
    if s["personal_status"] == "supported":
        body=f'''<div class="personal-values"><div><span>Earlier · {window(s['baseline_window'])}</span><strong>{num(s['baseline_mean'])}</strong><small>{s['baseline_observations']} observed weeks</small></div><div><span>Recent · {window(s['recent_window'])}</span><strong>{num(s['recent_mean'])}</strong><small>{s['recent_observations']} observed weeks</small></div></div>
<p class="delta"><b>{num(s['personal_change'],True)}</b> {h(e['unit'])}</p><p class="fine">Recent minus earlier; no interval was estimated for this change.</p>'''
    else:
        body=f'''<strong class="unavailable">Personal comparison unavailable</strong><p>Earlier {window(s['baseline_window'])}: <b>{s['baseline_observations']} observed weeks</b>.<br>Recent {window(s['recent_window'])}: <b>{s['recent_observations']} observed weeks</b>.</p><p class="fine">Insufficient observed support for the earlier-to-recent change in {h(FEATURES[e['feature']].lower())}.</p>'''
    duplicate = f'<span class="fine">{len(claim["original_indices"])} identical saved claims consolidated.</span>' if len(claim["original_indices"])>1 else ''
    return f'<section class="answer-card personal" data-answer="personal" data-evidence="{e["evidence_id"]}">{header}{body}<div class="card-foot">{evidence_link(e["evidence_id"])} {duplicate}</div></section>'


def comparison_card(claim, model, compact=False):
    e=model["evidence"][claim["evidence_id"]];s=e["summary"]
    label=FEATURES[e["feature"]]
    body = f'<div class="card-label">{h(label)} <span class="origin">{origin_label(claim["origin"],model)}</span></div>'
    body += f'<h3>{h(reference_name(e))}</h3><p class="window-line">Person: {window(e["window"])} · reference: {window(e["reference_window"])}</p>'
    if e["status"] == "supported":
        body+=f'''<div class="compare-values"><div><span>Person</span><strong>{num(s['focal_mean'])}</strong></div><div><span>Peer mean</span><strong>{num(s['peer_mean'])}</strong></div><div><span>Difference</span><strong>{num(s['contrast'],True)}</strong></div></div><p class="unit">{h(e['unit'])}</p><p class="fine">Peer mean 95% CI [{num(s['peer_ci_low'])}, {num(s['peer_ci_high'])}].</p>'''
    else:
        body+=f'<strong class="unavailable">Peer comparison unavailable</strong><p>{s["focal_observations"]} observed focal weeks; the selected comparison has insufficient support.</p><p class="unit">Measure: {h(e["unit"])}</p>'
    body+=f'<p class="counts">{e["people"]:,} distinct peers · {e["observations"]:,} person-weeks · {s["focal_observations"]} observed focal weeks</p>{evidence_link(e["evidence_id"])}'
    return f'<section class="answer-card peer" data-answer="peer" data-evidence="{e["evidence_id"]}" data-window="{e["window"]}">{body}</section>'


def save_chart(out, name, content):
    path=out/'charts'/f'{name}.svg';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
    return f'<div class="chart" data-chart="{name}">{content}</div>'


def panel_chart(p, model):
    e=model["evidence"][p["evidence_id"]]
    return {"trajectory":trajectory,"observation_status":observation,"assessment_status":assessment}.get(p["kind"],lambda e:references([e],e["evidence_id"]))(e)


def render(model, out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    evidence,claims,panels=model["evidence"],model["claims"],model["panels"]
    q=model["question"];first=next(iter(evidence.values()));s=first["summary"]
    own=[c for c in claims if c["template"]=="personal_change"]
    peers=[c for c in claims if c["template"]=="comparison"]
    measurement=[c for c in claims if c["template"]=="measurement_limits"]
    observation_panels=[p for p in panels if p["kind"]=="observation_status"]
    assessment_panels=[p for p in panels if p["kind"]=="assessment_status"]
    trajectories=[p for p in panels if p["kind"]=="trajectory"]
    state={}
    layer='New presentation · saved development evidence'
    ref_note=f'Peer intervals describe the reference mean ({first["uncertainty"]["replicates"]} person-bootstrap replicates), not this individual or a difference. No causal or significance conclusion.'
    activity_note='Recorded clicks are not effort, ability, learning or study time. Logging completeness is unknown; eligibility is administrative.'
    layout=model["layout"]
    if layout in {"personal","support"}:
        cards=''.join(personal_card(c,model) for c in own)
        if trajectories:
            p=trajectories[0]
            cards+=f'<div class="chart-note">Weekly trajectory · {origin_label(p["origin"],model)}</div>'+save_chart(out,'principal-trajectory',trajectory(evidence[p['evidence_id']]))
        secondary=''.join(comparison_card(c,model) for c in peers)
        main=f'<div class="analysis-grid"><div>{cards}</div><div class="stack"><div class="section-label">Selected peer answers</div>{secondary}</div></div>'
        if observation_panels:
            p=observation_panels[0]
            main+=f'<details class="supplement"><summary>Observation timeline · {origin_label(p["origin"],model)}</summary>{save_chart(out,"principal-observations",observation(evidence[p["evidence_id"]]))}</details>'
        note=activity_note+' '+ref_note
    elif layout=="references" and model["switchable"]:
        records=[evidence[k] for k in model['comparison_ids']]
        # Preserve every selected comparison. Switching changes emphasis, not analysis.
        options=''.join(f'<option value="{e["evidence_id"]}">{h(reference_name(e))} · {window(e["reference_window"])}</option>' for e in records)
        for c in peers:
            eid=c["evidence_id"]
            content=references(records,eid)
            save_chart(out,'reference-'+eid,content)
            state[eid]={"card":comparison_card(c,model),"svg":content,"reference":evidence[eid]["reference"],
                        "window":evidence[eid]["window"],"reference_window":evidence[eid]["reference_window"],
                        "evidence_href":f'#evidence-{eid}',"summary":evidence[eid]['summary']}
        initial=records[0]['evidence_id']
        main=f'''<div class="reference-control"><label for="reference-select">View a saved reference</label><select id="reference-select">{options}</select><span class="fine">Saved analysis only · no new investigation</span></div>
<div class="analysis-grid reference-grid"><div id="reference-chart" class="chart">{state[initial]['svg']}</div><div id="reference-result" aria-live="polite">{state[initial]['card']}<p class="fine change-definition">Population changes for the prior-attempt group. The earlier-period option changes the reference window; the person's recent window stays fixed.</p></div></div>
<div class="all-contrasts">'''+''.join(f'<div><b>{h(reference_name(e))}</b><span>Person − peer: <strong>{num(e["summary"]["contrast"],True)}</strong></span><span>{e["people"]:,} people · {e["observations"]:,} weeks</span></div>' for e in records)+'</div>'
        note=ref_note+' Earlier-period peers are not automatically fairer; observed membership can change across periods.'
    elif layout=="observations":
        p=observation_panels[0]
        status=evidence[p['evidence_id']]
        left=f'<div class="chart-note">{origin_label(p["origin"],model)}</div>'+save_chart(out,'principal-observations',observation(status))
        if assessment_panels:
            a=assessment_panels[0]
            left+=f'<div class="chart-note">{origin_label(a["origin"],model)}</div>'+save_chart(out,'principal-assessments',assessment(evidence[a['evidence_id']]))
        right=f'<section class="answer-card unavailable-card"><div class="card-label">Selected peer comparisons <span class="origin">{origin_label(peers[0]["origin"],model)}</span></div>'
        for c in peers:
            e=evidence[c['evidence_id']]
            right+=f'<div class="unavailable-row" data-answer="peer" data-evidence="{e["evidence_id"]}"><b>{h(FEATURES[e["feature"]])}</b><strong>{num(e["summary"]["focal_mean"])}</strong><span>{h(e["unit"])}</span>{evidence_link(e["evidence_id"])}</div>'
        right+=f'<p><b>{status["summary"]["focal_observations"]} observed focal weeks</b> in {window(status["window"])}. Insufficient support for these selected comparisons.</p><p class="counts">Presentation peers: {status["people"]:,} people / {status["observations"]:,} person-weeks, {window(status["reference_window"])}.</p></section>'
        main=f'<div class="analysis-grid"><div>{left}</div><div>{right}</div></div>'
        note=activity_note+' Grades and banking approval are unavailable because release/approval times are unknown (original compiler context). These are not sample-size failures.'
    elif layout=="assessments":
        main='<div class="assessment-metrics">'+''.join(comparison_card(c,model) for c in peers)+'</div>'
        if assessment_panels:
            p=assessment_panels[0]
            event_chart=f'<div><div class="chart-note">Dated record states · {origin_label(p["origin"],model)}</div>'+save_chart(out,'principal-assessments',assessment(evidence[p['evidence_id']]))+'</div>'
        else:
            event_chart=''
        timeline=''
        if trajectories:
            p=trajectories[0]
            timeline=f'<div><div class="chart-note">Submission trajectory · {origin_label(p["origin"],model)}</div>'+save_chart(out,'principal-trajectory',trajectory(evidence[p['evidence_id']]))+'</div>'
        main=f'{main}<div class="analysis-grid">{event_chart}{timeline}</div>'
        note=' '.join(c['original_text'] for c in measurement)+' Due dates and submission dates differ; dated states describe their saved snapshot, not a later grade. '+ref_note
    else:
        main=''.join(comparison_card(c,model) for c in peers)
        note=activity_note+' '+ref_note

    # Every original panel remains inspectable. Duplicate panels are NOT silently
    # merged: different bootstrap intervals can exist even when means agree.
    supporting=[]
    for i,p in enumerate(panels):
        e=evidence[p['evidence_id']]
        supporting.append(f'<details class="support-panel"><summary>{h(p["kind"].replace("_"," ").capitalize())} · {h(FEATURES[e["feature"]])} · {origin_label(p["origin"],model)}</summary>{save_chart(out,f"original-panel-{i+1}",panel_chart(p,model))}<p>{h(e["reference_label"])}</p>{evidence_link(e["evidence_id"])} · <a href="charts/original-panel-{i+1}.svg">Download vector chart</a><p class="fine">Original panel {i+1}; {h(p.get("reason") or "method-selected content")}.</p></details>')
    originals=''.join(f'<li><span class="origin">{origin_label(c["selection_origin"],model)}</span> {h(c["text"])} {evidence_link(c["evidence_id"])}</li>' for c in model['bound']['claims'])
    claims_html=''.join(personal_card(c,model) if c['template']=='personal_change' else comparison_card(c,model) if c['template']=='comparison' else f'<section class="answer-card"><b>Measurement limits · {origin_label(c["origin"],model)}</b><p>{h(c["original_text"])}</p>{evidence_link(c["evidence_id"])}</section>' for c in claims)
    source_link=os.path.relpath(Path(model['source'])/'dashboard.html',out)
    evidence_details=''
    for eid,e in evidence.items():
        evidence_details+=f'<details class="evidence-record" id="evidence-{eid}"><summary>{h(FEATURES[e["feature"]])} · {h(reference_name(e))} · {window(e["window"])}</summary><p><b>{eid}</b> · {h(e["reference_label"])}</p><p>Saved uncertainty: {h(e["uncertainty"]["scope"])}</p><pre>{h(json.dumps(e,indent=2))}</pre></details>'
    conclusion=model['bound']['conclusion']
    full_context=''.join(f'<li>{h(t)}</li>' for t in model['bound']['compiler_supplied_context'])
    stylesheet=Path(__file__).with_name('style.css').read_text()
    script=Path(__file__).with_name('interaction.js').read_text()
    package=json.dumps({"references":state},ensure_ascii=False).replace('<','\\u003c')
    body=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(model['label'])} · {h(layout.capitalize())}</title><style>{stylesheet}</style></head><body>
<nav class="site-nav"><a href="../index.html">← Development gallery</a><span>Evidence-grounded dashboards</span></nav><main>
<article class="figure-surface" data-layout="{layout}" data-case="{h(model['label'])}">
<header><div class="eyebrow">{h(model['label'])} <span>OULAD · development example</span></div><h1>{h(model['question_heading'])}</h1><div class="context-line"><span>Earlier {window(s['baseline_window'])}</span><span>Recent {window(s['recent_window'])}</span><span>Through day {q['cutoff_day']}</span></div></header>
<div class="analysis-content">{main}</div><aside class="interpretation">{h(note)}</aside>
<footer class="surface-footer"><b>{h(model['method'])}</b><span>Saved selections · deterministic calculations · new presentation</span></footer></article>
<div class="below-surface"><details class="original-question"><summary>Full analytical question and saved conclusion</summary><p>{h(q['text'])}</p><p><b>Original conclusion:</b> {h(conclusion)}</p><p>Source status: {h(model['selection_status'])}. Numerical validation does not establish answer completeness.</p></details>
<details><summary>All selected answers · {len(claims)} distinct / {len(model['spec']['claims'])} original claims</summary><div class="answer-grid">{claims_html}</div></details>
<details><summary>All original panels and observation context</summary>{''.join(supporting)}</details>
<details><summary>Interpretation limits · original compiler boilerplate</summary><ul>{full_context}</ul></details>
<details id="provenance"><summary>Evidence and responsibility</summary><dl><dt>Agent or baseline</dt><dd>Selects the saved answers and conclusion. Selection status: {h(model['selection_status'])}.</dd><dt>Deterministic analytical tools</dt><dd>Calculated all saved measurements, counts and peer-mean intervals.</dd><dt>Original semantic compiler</dt><dd>Generated numerical wording and the explicitly tagged required context. Standard caveats are not agent investigation.</dd><dt>This presentation</dt><dd>Changes layout, typography, SVG charts, anonymous labels and emphasis. It consolidates only exact personal-claim duplicates. No analysis, evidence retrieval, answer repair or completeness evaluation.</dd></dl><p>Numerical binding and answer completeness are separate. All original claims, including multiplicity, follow below.</p><ol>{originals}</ol><p><a href="{h(source_link)}">Open original dashboard</a> · <a href="presentation.json">Presentation/source manifest</a></p><details><summary>Original selection provenance and identifiers</summary><pre>{h(json.dumps({'question':q,'selection_provenance':model['provenance'],'source_hashes':model['source_hashes']},indent=2))}</pre></details></details>
<section class="evidence-section"><h2>Saved evidence inspector</h2>{evidence_details}</section>
<p class="endnote">New renderings of saved development cases. No new inference, accuracy evaluation or usability study. OULAD · Kuzilek, Hlosta &amp; Zdrahal · CC BY 4.0. {h(layer)}.</p></div>
</main><script id="saved-state" type="application/json">{package}</script><script>{script}</script></body></html>'''
    body=body.replace('<span>Evidence-grounded dashboards</span>', '<a href="figure.html">Compact reading view →</a>')
    (out/'index.html').write_text(body)
    from .focus import focused
    focus_surface,focus_states=focused(model,out)
    start=body.index('<article class="figure-surface"');end=body.index('</article>',start)+len('</article>')
    focus_html=body[:start]+focus_surface+body[end:]
    focus_html=focus_html.replace('<body>','<body class="focus-page">').replace('href="figure.html">Compact reading view →','href="index.html">Expanded reading view →')
    focus_html=focus_html.replace(package,json.dumps({'references':focus_states},ensure_ascii=False).replace('<','\\u003c'))
    (out/'figure.html').write_text(focus_html)
    write_json(out/'presentation.json',model)
    return {'layout':layout,'html':str(out/'index.html'),'source':model['source'],'source_hashes':model['source_hashes'],
            'duplicate_claims':[c for c in claims if len(c['original_indices'])>1],
            'chart_files':[str(p) for p in sorted((out/'charts').glob('*.svg'))]}
