"""Shared descriptive backend. No model output is executed as analysis code."""
from __future__ import annotations

import pandas as pd
from ..analysis import finite_mean, interval, LIMITATIONS
from ..common import read_json, file_hash, digest, now
from ..prepare import FEATURES
from .core import ROOT, Registry, Question, Request, seal


class Engine:
    def __init__(self, source=ROOT / "source", registry=None):
        self.registry = registry or Registry()
        self.cfg = self.registry.cfg
        self.source = source
        self.meta = read_json(source / "manifest.json")
        for name, expected in self.meta["files"].items():
            if file_hash(source / name) != expected:
                raise ValueError("Trusted source bundle hash mismatch: " + name)
        self.weekly = pd.read_parquet(source / "weekly.parquet").sort_values(["course", "person_id", "week"])
        self.assessments = pd.read_parquet(source / "assessment_status.parquet")
        self.excluded = set(self.meta["excluded_reference_people"])
        assignments = read_json("artifacts/data/splits.json")["assignments"]
        if set(self.weekly.person_id) - set(assignments["development"]):
            raise ValueError("Non-development person in source bundle")
        if self.weekly.duplicated(["person_id", "course", "week"]).any():
            raise ValueError("Source person-course-week keys are not unique")
        self.integrity_cache = {}

    def analyze(self, question, request):
        q, req = Question.model_validate(question), Request.model_validate(request)
        p = self.registry.profile(q)
        data = self.weekly[self.weekly.course.eq(q.course) & self.weekly.end_day.le(q.cutoff_day)]
        focal = data[data.person_id.eq(q.person_id)]
        if focal.empty:
            raise ValueError("question.person_id: unavailable in this development presentation")
        group = focal.prior_attempt_group.iloc[0]
        window, ref_window, label = self.registry.context(q, req, group)
        peers = data[~data.person_id.isin(self.excluded | {q.person_id})]
        if self.cfg["references"][req.reference]["group"] == "same_prior_attempt":
            peers = peers[peers.prior_attempt_group.eq(group)]
        selected = peers[peers.week.between(*ref_window) & peers[req.feature].notna()]
        per = selected.groupby("person_id").agg(value=(req.feature, "mean"), observations=(req.feature, "size"), eligible_days=("eligible_days", "sum")).reset_index()
        values = {name: focal[focal.week.between(*win)] for name, win in [("focal", window), ("baseline", p["baseline"]), ("recent", p["recent"]) ]}
        s = {}
        for name, rows in values.items():
            s[name + "_mean"] = finite_mean(rows[req.feature])
            s[name + "_observations"] = int(rows[req.feature].notna().sum())
        seed = self.registry.seed(q, req)
        lo, hi = interval(per.value, seed, self.cfg["bootstrap_replicates"])
        supported = len(per) >= self.cfg["minimum_peer_people"] and s["focal_observations"] >= self.cfg["minimum_focal_weeks"]
        personal = all(s[n+"_observations"] >= self.cfg["minimum_focal_weeks"] for n in ("baseline", "recent"))
        s.update(peer_mean=finite_mean(per.value), peer_ci_low=lo, peer_ci_high=hi,
                 focal_eligible_days=float(values["focal"].eligible_days.sum()),
                 baseline_window=p["baseline"], recent_window=p["recent"],
                 personal_change=s["recent_mean"]-s["baseline_mean"] if personal else None,
                 personal_status="supported" if personal else "insufficient_evidence")
        s["contrast"] = s["focal_mean"]-s["peer_mean"] if supported else None
        trajectory = []
        for week in range((q.cutoff_day+1)//7):
            pw = peers[peers.week.eq(week) & peers[req.feature].notna()]
            fw = focal[focal.week.eq(week)]
            lo, hi = interval(pw[req.feature], seed+week+1, self.cfg["bootstrap_replicates"])
            trajectory.append(dict(week=week, end_day=week*7+6, focal_value=finite_mean(fw[req.feature]), peer_mean=finite_mean(pw[req.feature]), peer_ci_low=lo, peer_ci_high=hi, peer_people=int(pw.person_id.nunique()), peer_observations=len(pw), unit=FEATURES[req.feature], reference=req.reference))
        cols = ["week", "start_day", "end_day", "eligible_days", "observation_status", "logging_completeness", "score_status", req.feature]
        obs = focal[cols].rename(columns={req.feature: "value"}).astype(object)
        obs = obs.where(pd.notna(obs), None).to_dict("records")
        ast = self.assessments[self.assessments.person_id.eq(q.person_id) & self.assessments.course.eq(q.course) & self.assessments.as_of_day.le(q.cutoff_day)].to_dict("records")
        return seal(dict(question_id=q.question_id, request=req.model_dump(), feature=req.feature, unit=FEATURES[req.feature], reference=req.reference, reference_label=label, window=window, reference_window=ref_window, cutoff_day=q.cutoff_day, status="supported" if supported else "insufficient_evidence", people=len(per), observations=int(per.observations.sum()), peer_ids=list(map(int, per.person_id)), focal_id=q.person_id, summary=s, peer_summary_rows=per.to_dict("records"), trajectory=trajectory, observation_status=obs, assessment_status=ast,
            uncertainty={"method": "person_cluster_percentile_bootstrap", "replicates": self.cfg["bootstrap_replicates"], "level": 0.95, "label": "95% bootstrap interval for peer mean; not individual prediction uncertainty", "resampling_unit": "person with within-window history kept together", "scope": "Pointwise descriptive intervals; no interval for a focal contrast, personal change or reference difference"},
            limitations=LIMITATIONS + ["All task focal people are excluded from the fixed development reference pool.", "Earlier-stage peers answer a different descriptive question; they are not a causal or automatically fairer adjustment."],
            provenance={"executed_utc": now(), "source_bundle_sha256": digest(self.meta), "config_sha256": digest(self.cfg), "request_sha256": digest(req.model_dump()), "seed": seed, "minimum_peer_people": self.cfg["minimum_peer_people"], "aggregation": "Equal weight per eligible person, equal weight per observed week within person; trajectories use same-week peers, including for the early-stage reference."}))


def compact(e):
    """Only allowlisted results enter model context; no raw rows, rubrics or scoring targets."""
    return {"evidence_id": e.evidence_id, "feature": e.feature, "unit": e.unit, "reference": e.reference, "reference_label": e.reference_label, "window": e.window, "reference_window": e.reference_window, "status": e.status, "people": e.people, "observations": e.observations, "summary": e.summary, "observation_states": sorted({r["observation_status"] for r in e.observation_status}), "assessment_states": sorted({r["state"] for r in e.assessment_status}), "limitations": e.limitations, "uncertainty": e.uncertainty}
