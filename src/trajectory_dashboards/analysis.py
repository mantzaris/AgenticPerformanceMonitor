from __future__ import annotations

import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from .common import code_hash, digest, file_hash, now, read_json, write_json
from .contracts import AnalysisRequest, EvidenceRecord, Question
from .prepare import FEATURES

LIMITATIONS = [
    "Recorded clicks are not effort, ability, learning or study time; logging completeness is unknown.",
    "Registration approximates opportunity, not actual exposure. The withdrawal day is the first ineligible day.",
    "Assessment scores and banked credit are withheld: grade-release and banking-approval times are unknown.",
    "Scheduled assessments are opportunities, not verified individual obligations; exemptions may be unobserved.",
    "Source interaction rows can repeat; sums preserve all source rows and are not verified unique click events.",
    "Peer means describe eligible observed person-weeks; changing eligibility and informative withdrawal can change composition.",
    "Exploratory development analysis only; no causal, significance, anomaly or prediction claim.",
]


def finite_mean(s):
    s = np.asarray(s, dtype=float)
    s = s[np.isfinite(s)]
    return float(s.mean()) if len(s) else None


def interval(values, seed, reps=500):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return [None, None]
    rng = np.random.default_rng(seed)
    means = values[rng.integers(0, len(values), size=(reps, len(values)))].mean(axis=1)
    return list(map(float, np.quantile(means, [0.025, 0.975])))


class Engine:
    def __init__(self, config="configs/stage1.json", prepared="data/prepared", artifacts="artifacts/data"):
        self.cfg = read_json(config)
        self.prepared = Path(prepared)
        self.meta = read_json(Path(artifacts) / "preparation.json")
        for name, expected in self.meta["files"].items():
            if file_hash(self.prepared / name) != expected:
                raise ValueError("Prepared data hash mismatch")
        if digest(self.cfg) != self.meta["config_sha256"]:
            raise ValueError("Configuration differs from preparation")
        self.weekly = pd.read_parquet(self.prepared / "weekly.parquet")
        self.assessments = pd.read_parquet(self.prepared / "assessment_status.parquet")
        self.questions = {q["question_id"]: Question.model_validate(q) for q in read_json(Path(artifacts) / "questions.json")}
        split = read_json(Path(artifacts) / "splits.json")["assignments"]
        if set(self.weekly.person_id) & set(split["reserved"]):
            raise ValueError("Reserved person entered analytical engine")
        if self.weekly.end_day.max() > self.cfg["cutoff_day"]:
            raise ValueError("Post-cutoff feature")

    def analyze(self, request: AnalysisRequest | dict):
        req = AnalysisRequest.model_validate(request)
        q = self.questions[req.question_id]
        if (req.end_week + 1) * 7 - 1 > q.cutoff_day:
            raise ValueError("Analysis crosses cutoff")
        w = self.weekly[self.weekly.course.eq(q.course)]
        focal = w[w.person_id.eq(q.person_id)].copy()
        peers = w[~w.person_id.eq(q.person_id)].copy()
        label = f"{q.course}: other development students, eligible weeks"
        if req.reference == "same_prior_attempt":
            group = focal.prior_attempt_group.iloc[0]
            peers = peers[peers.prior_attempt_group.eq(group)]
            label += f", {group}"
        ref_window = self.cfg["baseline_weeks"] if req.reference == "early_stage" else [req.start_week, req.end_week]
        if req.reference == "early_stage":
            label += ", earlier study stage"
        label += f" (weeks {ref_window[0]}–{ref_window[1]})"
        p = peers[peers.week.between(*ref_window) & peers[req.feature].notna()]
        pr = p.groupby("person_id").agg(value=(req.feature, "mean"), observations=(req.feature, "size"), eligible_days=("eligible_days", "sum")).reset_index()
        f = focal[focal.week.between(req.start_week, req.end_week)]
        baseline = focal[focal.week.between(*self.cfg["baseline_weeks"])]
        recent = focal[focal.week.between(*self.cfg["recent_weeks"])]
        fm, bm, rm = [finite_mean(x[req.feature]) for x in [f, baseline, recent]]
        pm = finite_mean(pr.value)
        request_hash = digest(req.model_dump())
        seed = self.cfg["seed"] + int(request_hash[:7], 16)
        ci = interval(pr.value, seed, self.cfg["bootstrap_replicates"])
        supported = len(pr) >= self.cfg["minimum_peer_people"] and f[req.feature].notna().sum() >= 2
        trajectory = []
        for week in range(self.cfg["weeks"]):
            pw = peers[peers.week.eq(week) & peers[req.feature].notna()]
            fw = focal[focal.week.eq(week)]
            lo, hi = interval(pw[req.feature], seed + week + 1, self.cfg["bootstrap_replicates"])
            trajectory.append({"week": week, "end_day": week*7+6, "focal_value": finite_mean(fw[req.feature]), "peer_mean": finite_mean(pw[req.feature]), "peer_ci_low": lo, "peer_ci_high": hi, "peer_people": int(pw.person_id.nunique()), "peer_observations": len(pw), "unit": FEATURES[req.feature], "reference": req.reference})
        records = focal[["week", "start_day", "end_day", "eligible_days", "observation_status", "logging_completeness", "score_status", req.feature]].rename(columns={req.feature: "value"})
        records = records.astype(object).where(pd.notna(records), None).to_dict("records")
        ast = self.assessments[self.assessments.person_id.eq(q.person_id) & self.assessments.course.eq(q.course)].to_dict("records")
        summary = {"focal_mean": fm, "focal_observations": int(f[req.feature].notna().sum()), "focal_eligible_days": float(f.eligible_days.sum()), "peer_mean": pm, "peer_ci_low": ci[0], "peer_ci_high": ci[1], "contrast": fm - pm if supported else None, "baseline_mean": bm, "baseline_observations": int(baseline[req.feature].notna().sum()), "baseline_window": self.cfg["baseline_weeks"], "recent_mean": rm, "recent_observations": int(recent[req.feature].notna().sum()), "recent_window": self.cfg["recent_weeks"], "personal_change": rm-bm if rm is not None and bm is not None else None}
        provenance = {"executed_utc": now(), "request_sha256": request_hash, "config_sha256": digest(self.cfg), "source_archive_sha256": self.meta["archive_sha256"], "prepared_files": self.meta["files"], "code_sha256": code_hash(), "seed": seed, "minimum_peer_people": self.cfg["minimum_peer_people"], "peer_rowset_sha256": digest(pr.to_dict("records")), "focal_rowset_sha256": digest(records), "aggregation": "Equal-weight mean of each person's mean over eligible weeks; not a ratio of pooled clicks/days. Trajectories show same-week peers. Earlier-stage comparison uses weeks 0–3 only in the contrast summary."}
        content = dict(question_id=q.question_id, request=req, feature=req.feature, unit=FEATURES[req.feature], reference=req.reference, reference_label=label, window=[req.start_week, req.end_week], reference_window=ref_window, cutoff_day=q.cutoff_day, status="supported" if supported else "insufficient_evidence", people=len(pr), observations=int(pr.observations.sum()), peer_ids=list(map(int, pr.person_id)), focal_id=q.person_id, summary=summary, peer_summary_rows=pr.to_dict("records"), trajectory=trajectory, observation_status=records, assessment_status=ast, uncertainty={"method": "person_cluster_percentile_bootstrap", "replicates": self.cfg["bootstrap_replicates"], "level": 0.95, "label": "95% bootstrap interval for peer mean, not an individual prediction interval", "resampling_unit": "person; the entire within-window history remains together", "scope": "Pointwise/descriptive; no multiplicity correction; personal changes have no interval."}, limitations=LIMITATIONS, provenance=provenance)
        stable = {**content, "request": req.model_dump(), "provenance": {k:v for k,v in provenance.items() if k not in {"executed_utc", "code_sha256"}}}
        return EvidenceRecord(evidence_id="ev_" + digest(stable)[:16], **content)


def fit_models(engine, output="artifacts/statistics"):
    """A descriptive Gaussian working model, deliberately not a detector."""
    excluded = [q.person_id for q in engine.questions.values()]
    results = []
    for course, w in engine.weekly.groupby("course"):
        w = w[~w.person_id.isin(excluded) & w.clicks_per_eligible_day.notna()].copy()
        w["log_rate"] = np.log1p(w.clicks_per_eligible_day)
        formula = "log_rate ~ C(week)" + (" + C(prior_attempt_group)" if w.prior_attempt_group.nunique() > 1 else "")
        result = {"course": course, "formula": formula, "random_effect": "person intercept", "unit": "log(1 + recorded clicks / eligible day)", "cutoff_day": engine.cfg["cutoff_day"], "people": int(w.person_id.nunique()), "observations": len(w), "excluded_focal_people": excluded, "data_sha256": engine.meta["files"]["weekly.parquet"], "started_utc": now(), "limitations": ["Gaussian model of log counts is a working approximation.", "Conditional residual serial independence, normal random effects and ignorable missingness are not validated.", "Fit is descriptive at cutoff, not a prospective forecast or calibrated anomaly score.", "Subgroup and week effects are associational. No model-based individual interval is displayed."]}
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                fit = smf.mixedlm(formula, w, groups=w.person_id, re_formula="1").fit(reml=True, method="lbfgs", maxiter=200, disp=False)
                variance = float(fit.cov_re.iloc[0,0])
                valid = bool(fit.converged and np.isfinite(fit.fe_params).all() and variance > 1e-8)
                result.update(status="converged" if valid else "failed_or_singular", converged=bool(fit.converged), random_intercept_variance=variance, residual_variance=float(fit.scale), fixed_effects={k: float(v) for k,v in fit.fe_params.items()})
                if valid:
                    w["fitted_conditional"] = fit.fittedvalues
                    w["residual"] = fit.resid
                    pairs = w.sort_values(["person_id", "week"])
                    pairs["lag"] = pairs.groupby("person_id").residual.shift()
                    result["residual_lag1_correlation"] = float(pairs[["residual", "lag"]].corr().iloc[0,1])
                    prediction = w[["week", "prior_attempt_group"]].drop_duplicates().sort_values(["week", "prior_attempt_group"])
                    prediction["fixed_mean_log1p_rate"] = fit.predict(prediction)
                    result["fixed_trajectory"] = prediction.to_dict("records")
            except Exception as exc:
                result.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        result["warnings"] = [str(x.message) for x in caught]
        result["fallback"] = "Descriptive peer means and personal baseline are always available; no mixed-model interval is substituted."
        result["completed_utc"] = now()
        results.append(result)
    write_json(Path(output) / "mixed_models.json", results)
    return results
