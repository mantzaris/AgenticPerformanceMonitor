"""Domain specifications select evidence; deterministic code owns every number."""
from __future__ import annotations

import html
import json
import math
from pathlib import Path
import altair as alt
import numpy as np
import pandas as pd
import vl_convert as vlc
from .common import digest, read_json, write_json
from .contracts import DashboardSpecification, EvidenceRecord, Question
from .prepare import FEATURES


def close(a, b):
    return a is None and b is None or a is not None and b is not None and math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10)


def average(rows):
    v = [x for x in rows if x is not None]
    return float(np.mean(v)) if v else None


def validate_evidence(e, q):
    e = EvidenceRecord.model_validate(e)
    d = e.model_dump()
    d.pop("evidence_id")
    d["provenance"] = {k:v for k,v in d["provenance"].items() if k not in {"executed_utc", "code_sha256"}}
    if e.evidence_id != "ev_" + digest(d)[:16]:
        raise ValueError("Evidence content hash does not resolve")
    if e.question_id != q.question_id or e.request.question_id != q.question_id or e.focal_id != q.person_id:
        raise ValueError("Evidence belongs to another question/person")
    if e.cutoff_day != q.cutoff_day or e.unit != FEATURES[e.feature] or e.request.feature != e.feature:
        raise ValueError("Unit, feature or cutoff mismatch")
    if e.reference != e.request.reference or e.window != [e.request.start_week, e.request.end_week]:
        raise ValueError("Reference/window mismatch")
    expected_ref_window = [0, 3] if e.reference == "early_stage" else e.window
    if e.reference_window != expected_ref_window or q.course not in e.reference_label:
        raise ValueError("Reference label or reference window mismatch")
    pr = e.peer_summary_rows
    ids = [r["person_id"] for r in pr]
    if len(set(ids)) != len(ids) or sorted(ids) != sorted(e.peer_ids) or e.focal_id in ids:
        raise ValueError("Invalid peer identities or focal leakage")
    if len(ids) != e.people or sum(r["observations"] for r in pr) != e.observations:
        raise ValueError("Incorrect evidence denominators")
    if not close(average([r["value"] for r in pr]), e.summary["peer_mean"]):
        raise ValueError("Peer summary mismatch")
    if any(r["end_day"] > q.cutoff_day for r in e.observation_status + e.trajectory) or any(r["as_of_day"] > q.cutoff_day for r in e.assessment_status):
        raise ValueError("Post-cutoff evidence")
    if (e.window[1] + 1) * 7 - 1 > q.cutoff_day:
        raise ValueError("Post-cutoff request")
    for r in e.observation_status:
        if r["observation_status"] in {"ineligible", "unknown"} and r["value"] is not None:
            raise ValueError("Unavailable value disguised as observation")
        if r["logging_completeness"] != "unknown" or r["score_status"] != "withheld_release_time_unknown":
            raise ValueError("Unsupported observation availability")
    s = e.summary
    for window, mean_name, count_name in [(e.window, "focal_mean", "focal_observations"), (s["baseline_window"], "baseline_mean", "baseline_observations"), (s["recent_window"], "recent_mean", "recent_observations")]:
        values = [r["value"] for r in e.observation_status if window[0] <= r["week"] <= window[1]]
        if not close(average(values), s[mean_name]) or sum(v is not None for v in values) != s[count_name]:
            raise ValueError("Focal result table disagrees with displayed summary")
    status = "supported" if e.people >= e.provenance["minimum_peer_people"] and s["focal_observations"] >= 2 else "insufficient_evidence"
    if e.status != status:
        raise ValueError("Unsupported conclusion state")
    expected = s["focal_mean"] - s["peer_mean"] if status == "supported" else None
    if not close(s["contrast"], expected):
        raise ValueError("Contrast does not match bound result")
    expected_change = s["recent_mean"] - s["baseline_mean"] if s["recent_mean"] is not None and s["baseline_mean"] is not None else None
    if not close(s["personal_change"], expected_change):
        raise ValueError("Personal contrast does not match bound result")
    if e.uncertainty["method"] != "person_cluster_percentile_bootstrap" or e.uncertainty["replicates"] != 500:
        raise ValueError("Unknown uncertainty procedure")
    if not e.observation_status or not e.limitations:
        raise ValueError("Missing observation context")
    for r in e.trajectory:
        if r["unit"] != e.unit or r["reference"] != e.reference or r["peer_people"] != r["peer_observations"]:
            raise ValueError("Trajectory binding mismatch")
    return e


def validate(spec, evidence, q):
    q = Question.model_validate(q)
    spec = DashboardSpecification.model_validate(spec)
    if spec.question_id != q.question_id or spec.cutoff_day != q.cutoff_day:
        raise ValueError("Dashboard question/cutoff mismatch")
    if len(set(spec.evidence_ids)) != len(spec.evidence_ids):
        raise ValueError("Repeated evidence identifiers")
    bound = {}
    for eid in spec.evidence_ids:
        if eid not in evidence:
            raise ValueError("Unsupported evidence reference: " + eid)
        bound[eid] = validate_evidence(evidence[eid], q)
    for p in [*spec.panels, *spec.claims]:
        if p.evidence_id not in bound:
            raise ValueError("Unbound panel or claim")
    kinds = {p.kind for p in spec.panels}
    if not {"trajectory", "observation_status"}.issubset(kinds):
        raise ValueError("Required comparison/observation panels omitted")
    signatures = {(e.feature, e.reference) for e in bound.values()}
    required = {("clicks_per_eligible_day", "course")}
    expected_annotation = "descriptive_only"
    if q.kind == "reference_sensitivity":
        required |= {("clicks_per_eligible_day", "same_prior_attempt"), ("clicks_per_eligible_day", "early_stage")}
        expected_annotation = "reference_dependent"
    elif q.kind == "measurement_limits":
        required.add(("scheduled_no_submission", "course"))
        expected_annotation = "measurement_limited"
        if "assessment_status" not in kinds or "measurement_limits" not in {c.template for c in spec.claims}:
            raise ValueError("Measurement limitations/assessment status omitted")
    if not required.issubset(signatures) or spec.annotation != expected_annotation:
        raise ValueError("Question evidence obligations not satisfied")
    if any(e.window != [8, 11] for e in bound.values()):
        raise ValueError("Stage 1 questions require recent weeks 8–11")
    panel_evidence = {p.evidence_id for p in spec.panels}
    claim_evidence = {c.evidence_id for c in spec.claims}
    if not set(bound).issubset(panel_evidence) or not set(bound).issubset(claim_evidence):
        raise ValueError("Selected evidence must be visible and referenced by a claim")
    if q.kind == "personal_change" and "personal_change" not in {c.template for c in spec.claims}:
        raise ValueError("Personal baseline omitted")
    for signature in required:
        if not any((bound[p.evidence_id].feature, bound[p.evidence_id].reference) == signature and p.kind in {"trajectory", "comparison"} for p in spec.panels):
            raise ValueError("Required comparison is hidden")
    return spec, bound


def requests_for(q):
    base = dict(tool="analyze", question_id=q.question_id, feature="clicks_per_eligible_day", reference="course", start_week=8, end_week=11)
    requests = [base]
    if q.kind == "reference_sensitivity":
        requests.extend([{**base, "reference": r} for r in ["same_prior_attempt", "early_stage"]])
    elif q.kind == "measurement_limits":
        requests.append({**base, "feature": "scheduled_no_submission"})
    return requests


def deterministic_spec(q, records):
    ids = [e.evidence_id for e in records]
    claims = [{"template": "comparison", "evidence_id": i} for i in ids]
    panels = [{"kind": "trajectory", "evidence_id": ids[0]}, {"kind": "observation_status", "evidence_id": ids[0]}]
    annotation = "descriptive_only"
    if q.kind == "personal_change":
        claims.append({"template": "personal_change", "evidence_id": ids[0]})
        panels.append({"kind": "comparison", "evidence_id": ids[0]})
    elif q.kind == "reference_sensitivity":
        panels.extend({"kind": "comparison", "evidence_id": i} for i in ids)
        annotation = "reference_dependent"
    else:
        panels.extend([{"kind": "trajectory", "evidence_id": ids[1]}, {"kind": "assessment_status", "evidence_id": ids[1]}])
        claims.append({"template": "measurement_limits", "evidence_id": ids[1]})
        annotation = "measurement_limited"
    return DashboardSpecification(question_id=q.question_id, cutoff_day=q.cutoff_day, evidence_ids=ids, claims=claims, panels=panels, annotation=annotation, followups=["inspect_reference", "inspect_personal_history", "check_assessment_availability"])


def number(x):
    return "unavailable" if x is None else f"{x:,.2f}"


def claim_text(claim, e):
    s = e.summary
    if claim.template == "measurement_limits":
        return "Grade availability and banking approval are unknown. Scheduled non-submission records cannot establish failure, effort, ability or learning. Logging completeness is unknown."
    if claim.template == "personal_change":
        if s["baseline_observations"] < 2 or s["recent_observations"] < 2:
            return "Insufficient eligible personal history for a baseline-to-recent comparison."
        return f"Personal mean changed from {number(s['baseline_mean'])} in weeks {s['baseline_window'][0]}–{s['baseline_window'][1]} ({s['baseline_observations']} observed weeks) to {number(s['recent_mean'])} in weeks {s['recent_window'][0]}–{s['recent_window'][1]} ({s['recent_observations']} observed weeks): change {number(s['personal_change'])} {e.unit}. This descriptive personal change has no uncertainty interval."
    support = f"{e.people} distinct peers / {e.observations} person-weeks; {s['focal_observations']} observed focal weeks."
    if e.status != "supported":
        return f"Insufficient evidence for a focal comparison in weeks {e.window[0]}–{e.window[1]}. {support} Reference: {e.reference_label}."
    return f"Focal mean {number(s['focal_mean'])}; peer mean {number(s['peer_mean'])}; difference {number(s['contrast'])} {e.unit}, focal weeks {e.window[0]}–{e.window[1]}. {support} Reference: {e.reference_label}. Peer mean 95% bootstrap interval [{number(s['peer_ci_low'])}, {number(s['peer_ci_high'])}]; not an individual prediction interval."


def panel_chart(panel, e, comparison_max=None):
    accent, muted = "#b64c35", "#286f83"
    if panel.kind == "trajectory":
        df = pd.DataFrame(e.trajectory)
        axis_title = ["Scheduled assessments without", "recorded submission / week"] if e.feature == "scheduled_no_submission" else e.unit
        band = alt.Chart(df).mark_area(opacity=0.16, color=muted).encode(x=alt.X("week:Q", title="Week since presentation start", axis=alt.Axis(tickMinStep=1)), y=alt.Y("peer_ci_low:Q", title=axis_title, scale=alt.Scale(zero=True)), y2="peer_ci_high:Q")
        peer = alt.Chart(df).mark_line(color=muted, strokeWidth=2).encode(x="week:Q", y="peer_mean:Q", tooltip=["week", "peer_mean", "peer_people", "peer_observations"])
        focal = alt.Chart(df).mark_line(color=accent, strokeWidth=2.5, point=alt.OverlayMarkDef(color=accent)).encode(x="week:Q", y="focal_value:Q", tooltip=["week", "focal_value"])
        return (band+peer+focal).properties(width=760, height=190, title=alt.TitleParams(text=e.feature.replace("_", " ").capitalize(), subtitle=["Rust: focal student · teal: same-week peers; band: 95% peer-mean bootstrap interval", "Individual prediction uncertainty is not estimated."]))
    if panel.kind == "comparison":
        rows = [{"series": f"Focal: weeks {e.window[0]}–{e.window[1]}", "value": e.summary["focal_mean"], "lo": None, "hi": None}, {"series": "Reference: " + e.reference, "value": e.summary["peer_mean"], "lo": e.summary["peer_ci_low"], "hi": e.summary["peer_ci_high"]}]
        df = pd.DataFrame(rows)
        base = alt.Chart(df).encode(y=alt.Y("series:N", title=None, sort=None), x=alt.X("value:Q", title=e.unit, scale=alt.Scale(domain=[0, comparison_max], zero=True)))
        return (base.mark_bar(size=22, color=muted) + base.mark_rule(color="#142e38").encode(x="lo:Q", x2="hi:Q")).properties(width=760, height=90, title=alt.TitleParams(text=f"{e.reference} · {e.people} peers / {e.observations} person-weeks", subtitle=[e.reference_label, "Whisker: 95% bootstrap interval for reference mean only"]))
    if panel.kind == "observation_status":
        df = pd.DataFrame(e.observation_status)
        df["row"] = "Administrative / recorded state"
        return alt.Chart(df).mark_rect().encode(x=alt.X("week:O", title="Week"), y=alt.Y("row:N", title=None), color=alt.Color("observation_status:N", title="Observation status", scale=alt.Scale(domain=["recorded_activity", "zero_recorded_activity", "ineligible", "unknown"], range=[muted, "#e4bb64", "#aaaeb3", "#ac78a5"]), legend=alt.Legend(orient="bottom", labelLimit=260)), tooltip=["week", "eligible_days", "observation_status", "logging_completeness"]).properties(width=760, height=30, title="Observation status · registration is not study time")
    df = pd.DataFrame(e.assessment_status)
    if df.empty:
        return alt.Chart(pd.DataFrame({"text": ["No scheduled non-exam assessments in this window"]})).mark_text().encode(text="text:N").properties(width=760, height=70)
    return alt.Chart(df).mark_point(filled=True, size=150).encode(x=alt.X("due_day:Q", title="Scheduled due day since presentation start"), y=alt.Y("assessment_id:N", title="Assessment"), color=alt.Color("state:N", title="Record state", legend=alt.Legend(orient="bottom", labelLimit=400)), tooltip=["assessment_id", "due_day", "as_of_day", "state", "score_status"]).properties(width=760, height=120, title=alt.TitleParams(text="Scheduled assessment record state", subtitle="No grade-release timestamps; scores withheld. Exemptions are not verified."))


def render(spec, evidence, q, output):
    spec, evidence = validate(spec, evidence, q)
    q = Question.model_validate(q)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    claims = [{"evidence_id": c.evidence_id, "template": c.template, "text": claim_text(c, evidence[c.evidence_id])} for c in spec.claims]
    maxima = {feature: max([1.0]+[v for e in evidence.values() if e.feature == feature for k,v in e.summary.items() if k in {"focal_mean", "peer_mean", "peer_ci_high"} and v is not None])*1.05 for feature in FEATURES}
    chart = alt.vconcat(*[panel_chart(p, evidence[p.evidence_id], maxima[evidence[p.evidence_id].feature]) for p in spec.panels], spacing=28).resolve_scale(color="independent").configure(font="sans-serif", background="#fbfaf7").configure_view(stroke=None).configure_axis(labelFontSize=11, titleFontSize=12).configure_title(anchor="start", color="#142e38", fontSize=17, subtitleFontSize=11)
    chart_spec = chart.to_dict()
    write_json(out / "chart.vl.json", chart_spec)
    svg = vlc.vegalite_to_svg(chart_spec)
    (out / "dashboard.svg").write_text(svg)
    (out / "dashboard.png").write_bytes(vlc.vegalite_to_png(chart_spec, scale=1.5))
    write_json(out / "spec.json", spec.model_dump())
    write_json(out / "evidence.json", {k:e.model_dump() for k,e in evidence.items()})
    write_json(out / "question.json", q.model_dump())
    bound = {"question_id": q.question_id, "claims": claims, "evidence_hashes": {k:digest(e.model_dump()) for k,e in evidence.items()}, "renderer": "controlled Altair → Vega-Lite → SVG/PNG; HTML inspector requires no network", "validation": "PASS"}
    write_json(out / "bound.json", bound)
    limitations = list(dict.fromkeys(x for e in evidence.values() for x in e.limitations))
    cards = "".join(f'<li>{html.escape(c["text"])} <a href="#{c["evidence_id"]}">Evidence</a></li>' for c in claims)
    inspectors = "".join(f'<details id="{eid}"><summary>{html.escape(e.reference_label)} · {html.escape(e.feature)} · {eid}</summary><pre>{html.escape(json.dumps(e.model_dump(),indent=2))}</pre></details>' for eid,e in evidence.items())
    body = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(q.question_id)} · Reference-sensitive dashboard</title>
<style>body{{font:16px/1.55 system-ui,sans-serif;color:#142e38;background:#fbfaf7;margin:0}}main{{max-width:1100px;margin:auto;padding:40px 28px}}.eyebrow{{letter-spacing:.12em;font-size:12px;color:#286f83}}h1{{font-size:32px;line-height:1.2;max-width:920px}}.meta{{color:#55666b}}li{{margin-bottom:12px}}.claims{{background:white;border-left:4px solid #286f83;padding:18px 28px}}.chart{{overflow-x:auto;margin:30px 0}}details{{border-top:1px solid #ced4d5;padding:15px 0}}summary{{cursor:pointer;font-weight:600}}pre{{white-space:pre-wrap;font-size:12px;background:#f0f2f1;padding:20px;max-height:500px;overflow:auto}}a{{color:#286f83}}footer{{font-size:12px;color:#55666b;margin-top:40px}}</style>
<main><div class="eyebrow">STAGE 1 · OULAD · DEVELOPMENT EXAMPLE</div><h1>{html.escape(q.text)}</h1><p class="meta">{html.escape(q.role)} view · {html.escape(q.course)} · source person {q.person_id} · cutoff day {q.cutoff_day}</p><div class="claims"><ul>{cards}</ul></div><div class="chart">{svg}</div><h2>Limits on interpretation</h2><ul>{''.join('<li>'+html.escape(x)+'</li>' for x in limitations)}</ul><h2>Evidence inspector</h2><p>Every displayed quantitative claim and chart is bound to the saved analytical records below.</p>{inspectors}<h2>Follow-up options</h2><p>{' · '.join(html.escape(x.replace('_',' ')) for x in spec.followups)}</p><p>These are review suggestions; this saved export does not launch analyses.</p><footer>OULAD: Kuzilek, Hlosta &amp; Zdrahal, CC BY 4.0, DOI 10.24432/C5KK69. Source observations unmodified; weekly summaries derived. Descriptive feasibility demonstration, not an evaluation result.</footer></main></html>'''
    (out / "dashboard.html").write_text(body)
    return bound


def replay(source, output):
    source = Path(source)
    return render(read_json(source / "spec.json"), read_json(source / "evidence.json"), read_json(source / "question.json"), output)
