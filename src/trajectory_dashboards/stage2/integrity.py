"""Independent row-wise verification against the trusted allowlisted source bundle.

This deliberately does not call Engine.analyze or pandas groupby. Shared registry
definitions are the contract; sums/counts/intervals are recomputed here.
"""
from __future__ import annotations

import math
from collections import defaultdict
import numpy as np
from ..common import digest
from ..prepare import FEATURES
from .core import Question, Request, Evidence, Specification, seal


def mean(values):
    values = [float(v) for v in values if v is not None]
    return math.fsum(values) / len(values) if values else None


def bootstrap(values, seed, reps):
    if len(values) < 2:
        return [None, None]
    rng = np.random.default_rng(seed)
    # Same specified RNG stream as production, independently accumulated draws.
    means = []
    for _ in range(reps):
        ids = rng.integers(0, len(values), size=len(values))
        means.append(float(np.sum(np.take(values, ids))) / len(values))
    return [float(v) for v in np.quantile(means, [0.025, 0.975])]


def independent_facts(engine, question, request):
    q, req = Question.model_validate(question), Request.model_validate(request)
    p = engine.registry.profile(q)
    rows = engine.weekly[engine.weekly.course.eq(q.course) & engine.weekly.end_day.le(q.cutoff_day)].astype(object)
    rows = rows.where(rows.notna(), None).to_dict("records")
    focal = sorted([r for r in rows if r["person_id"] == q.person_id], key=lambda r:r["week"])
    if not focal:
        raise ValueError("No focal source observations")
    window, rw, label = engine.registry.context(q, req, focal[0]["prior_attempt_group"])
    peers = [r for r in rows if r["person_id"] not in engine.excluded | {q.person_id}]
    if engine.cfg['references'][req.reference]['group'] == "same_prior_attempt":
        peers = [r for r in peers if r["prior_attempt_group"] == focal[0]["prior_attempt_group"]]
    groups = defaultdict(list)
    for r in peers:
        if rw[0] <= r["week"] <= rw[1] and r[req.feature] is not None:
            groups[r["person_id"]].append(r)
    per = [dict(person_id=int(pid), value=mean([r[req.feature] for r in rr]), observations=len(rr), eligible_days=math.fsum(r["eligible_days"] for r in rr)) for pid,rr in sorted(groups.items())]
    s = {}
    for name,win in [("focal",window), ("baseline",p["baseline"]), ("recent",p["recent"])]:
        vals = [r[req.feature] for r in focal if win[0] <= r["week"] <= win[1] and r[req.feature] is not None]
        s[name+"_mean"], s[name+"_observations"] = mean(vals), len(vals)
    seed = engine.registry.seed(q, req)
    reps = engine.cfg["bootstrap_replicates"]
    ci = bootstrap([r["value"] for r in per], seed, reps)
    supported = len(per) >= engine.cfg["minimum_peer_people"] and s["focal_observations"] >= engine.cfg["minimum_focal_weeks"]
    personal = min(s["baseline_observations"],s["recent_observations"]) >= engine.cfg["minimum_focal_weeks"]
    s.update(peer_mean=mean([r["value"] for r in per]), peer_ci_low=ci[0], peer_ci_high=ci[1], baseline_window=p["baseline"], recent_window=p["recent"], focal_eligible_days=math.fsum(r["eligible_days"] for r in focal if window[0] <= r["week"] <= window[1] and r["eligible_days"] is not None), personal_change=s["recent_mean"]-s["baseline_mean"] if personal else None, personal_status="supported" if personal else "insufficient_evidence")
    s["contrast"] = s["focal_mean"]-s["peer_mean"] if supported else None
    trajectory = []
    for week in range((q.cutoff_day+1)//7):
        pr = [r for r in peers if r["week"] == week and r[req.feature] is not None]
        fr = [r for r in focal if r["week"] == week]
        lo,hi = bootstrap([r[req.feature] for r in sorted(pr,key=lambda r:r["person_id"])], seed+week+1, reps)
        trajectory.append(dict(week=week,end_day=week*7+6,focal_value=mean([r[req.feature] for r in fr]),peer_mean=mean([r[req.feature] for r in pr]),peer_ci_low=lo,peer_ci_high=hi,peer_people=len({r["person_id"] for r in pr}),peer_observations=len(pr),unit=FEATURES[req.feature],reference=req.reference))
    cols = ["week","start_day","end_day","eligible_days","observation_status","logging_completeness","score_status"]
    obs = [{**{k:r[k] for k in cols},"value":r[req.feature]} for r in focal]
    ast = [r for r in engine.assessments.to_dict("records") if r["person_id"] == q.person_id and r["course"] == q.course and r["as_of_day"] <= q.cutoff_day]
    return dict(question_id=q.question_id,request=req.model_dump(),feature=req.feature,unit=FEATURES[req.feature],reference=req.reference,reference_label=label,window=window,reference_window=rw,cutoff_day=q.cutoff_day,status="supported" if supported else "insufficient_evidence",people=len(per),observations=sum(r["observations"] for r in per),peer_ids=[r["person_id"] for r in per],focal_id=q.person_id,summary=s,peer_summary_rows=per,trajectory=trajectory,observation_status=obs,assessment_status=ast)


def compare(actual, expected, path):
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise ValueError(f"{path}: keys must be {sorted(expected)}")
        for k,v in expected.items():
            compare(actual[k], v, f"{path}.{k}")
    elif isinstance(expected, list):
        if not isinstance(actual,list) or len(actual) != len(expected):
            raise ValueError(f"{path}: expected {len(expected)} bound rows/items")
        for i,v in enumerate(expected):
            compare(actual[i], v, f"{path}[{i}]")
    elif isinstance(expected, (int,float)) and not isinstance(expected,bool):
        if actual is None or isinstance(actual,bool) or not isinstance(actual,(int,float)) or not math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-10):
            raise ValueError(f"{path}: value disagrees with trusted source; expected {expected!r}, got {actual!r}")
    elif actual != expected:
        raise ValueError(f"{path}: expected {expected!r}, got {actual!r}")


def validate_evidence(engine, q, value):
    e = Evidence.model_validate(value)
    if seal(e).evidence_id != e.evidence_id:
        raise ValueError(f"evidence.{e.evidence_id}: content hash mismatch")
    key = digest([q.model_dump(),e.request.model_dump(),digest(engine.meta),digest(engine.cfg)])
    if key not in engine.integrity_cache:
        engine.integrity_cache[key] = independent_facts(engine,q,e.request)
    expected = engine.integrity_cache[key]
    actual = e.model_dump()
    for k,v in expected.items():
        compare(actual[k],v,f"evidence.{e.evidence_id}.{k}")
    compare(e.provenance["config_sha256"],digest(engine.cfg),"provenance.config_sha256")
    compare(e.provenance["source_bundle_sha256"],digest(engine.meta),"provenance.source_bundle_sha256")
    compare(e.provenance["seed"],engine.registry.seed(q,e.request),"provenance.seed")
    compare(e.uncertainty, {"method":"person_cluster_percentile_bootstrap","replicates":engine.cfg["bootstrap_replicates"],"level":0.95,"label":"95% bootstrap interval for peer mean; not individual prediction uncertainty","resampling_unit":"person with within-window history kept together","scope":"Pointwise descriptive intervals; no interval for a focal contrast, personal change or reference difference"},"uncertainty")
    if not e.limitations:
        raise ValueError("evidence.limitations: measurement limitations required")
    return e


def reference_conclusion(records):
    comparable = [e for e in records if e.feature == "clicks_per_eligible_day" and e.request.window == "recent"]
    if not comparable or any(e.status != "supported" for e in comparable):
        return "insufficient_evidence"
    if len({e.reference for e in comparable}) < 2:
        return "descriptive"
    signs = {0 if e.summary["contrast"] == 0 else (1 if e.summary["contrast"] > 0 else -1) for e in comparable}
    return "same_direction" if len(signs) == 1 else "direction_differs"


def validate(engine, question, spec, evidence):
    q = Question.model_validate(question)
    engine.registry.profile(q)
    spec = Specification.model_validate(spec)
    compare(spec.question_id,q.question_id,"specification.question_id")
    compare(spec.cutoff_day,q.cutoff_day,"specification.cutoff_day")
    if len(set(spec.evidence_ids)) != len(spec.evidence_ids):
        raise ValueError("specification.evidence_ids: remove duplicates")
    bound = {}
    for eid in spec.evidence_ids:
        if eid not in evidence:
            raise ValueError(f"specification.evidence_ids: unknown {eid}; select only returned evidence IDs {sorted(evidence)}")
        bound[eid] = validate_evidence(engine,q,evidence[eid])
    for i,item in enumerate([*spec.claims,*spec.panels]):
        if item.evidence_id not in bound:
            raise ValueError(f"claims/panels[{i}].evidence_id: must appear in evidence_ids")
    kinds = {p.kind for p in spec.panels}
    errors=[]
    for needed in ("trajectory","observation_status"):
        if needed not in kinds:
            errors.append(f"specification.panels: missing kind='{needed}'; add it using a selected evidence_id. Keep other panels.")
    assessment_ids={eid for eid,e in bound.items() if e.feature in {"nonbanked_submissions","scheduled_no_submission"}}
    if assessment_ids and not any(p.kind=='assessment_status' and p.evidence_id in assessment_ids for p in spec.panels):
        errors.append(f"specification.panels: assessment evidence requires kind='assessment_status' with one of these evidence_ids: {sorted(assessment_ids)}")
    missing_claims=[eid for eid in bound if not any(c.evidence_id==eid for c in spec.claims)]
    missing_panels=[eid for eid in bound if not any(p.evidence_id==eid and p.kind in {"trajectory","comparison"} for p in spec.panels)]
    if missing_claims or missing_panels:
        errors.append(f"Selected evidence coverage: claims missing for {missing_claims}; trajectory/comparison panels missing for {missing_panels}. Add a comparison panel and claim for every listed ID, or remove redundant IDs and all their references. One shared observation_status panel is enough; at most 10 total panels.")
    if spec.conclusion in {"same_direction","direction_differs"}:
        expected = reference_conclusion(list(bound.values()))
        if spec.conclusion != expected:
            errors.append(f"specification.conclusion: selected results support '{expected}', not '{spec.conclusion}'. 'descriptive' is also admissible.")
    if spec.conclusion == "insufficient_evidence" and not any(e.status != "supported" or e.summary["personal_status"] != "supported" for e in bound.values()):
        errors.append("specification.conclusion: selected results have sufficient descriptive support; use descriptive or an empirically supported reference conclusion")
    if errors:
        raise ValueError("Fix all of these specification errors in the single repair: " + " | ".join(errors))
    # No task-kind/reference investigation policy is encoded in universal integrity.
    return spec,bound
