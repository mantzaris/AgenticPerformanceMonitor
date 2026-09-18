"""As-of preparation. Only allowlisted fields cross into development features."""
from __future__ import annotations

import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from .acquire import connection
from .common import digest, file_hash, now, read_json, write_json
from .contracts import Question

REG_KEY = ["code_module", "code_presentation", "id_student"]
FEATURES = {
    "clicks_per_eligible_day": "recorded clicks / eligible day",
    "active_days": "days with recorded activity / week",
    "distinct_resources": "distinct recorded resources / week",
    "nonbanked_submissions": "non-banked submissions / week",
    "scheduled_no_submission": "scheduled assessments without recorded submission / week",
}


def split_person(person, salt, fraction):
    n = int(hashlib.sha256(f"{salt}:{int(person)}".encode()).hexdigest()[:16], 16)
    return "development" if n / 2**64 < fraction else "reserved"


def eligibility(registration, withdrawal, start, end, cutoff):
    """Withdrawal date is treated as the first ineligible day (declared convention)."""
    if pd.isna(registration):
        return None
    lo = max(start, int(registration))
    hi = min(end, cutoff)
    if pd.notna(withdrawal) and withdrawal <= cutoff:
        hi = min(hi, int(withdrawal) - 1)
    return max(0, hi - lo + 1)


def build_weekly(registrations, activity, submissions, assessments, cutoff):
    """Pure fixture-testable computation; inputs are already limited to development."""
    if registrations.duplicated(REG_KEY).any():
        raise ValueError("Duplicate registration keys")
    regs = registrations.copy()
    regs.loc[regs.date_unregistration > cutoff, "date_unregistration"] = np.nan
    # A future registration is not known as an enrollment at this as-of cutoff.
    regs = regs[regs.date_registration.isna() | (regs.date_registration <= cutoff)]
    weeks = pd.DataFrame({"week": range((cutoff + 1) // 7)})
    grid = regs.merge(weeks, how="cross")
    grid["start_day"] = grid.week * 7
    grid["end_day"] = grid.start_day + 6
    grid["eligible_days"] = [eligibility(r.date_registration, r.date_unregistration, r.start_day, r.end_day, cutoff) for r in grid.itertuples()]
    # Event-to-registration joins are many-to-one, never activity-to-assessment.
    a = activity[(activity.date >= 0) & (activity.date <= cutoff)].merge(regs[REG_KEY + ["date_registration", "date_unregistration"]], on=REG_KEY, validate="many_to_one")
    a = a[(a.date >= a.date_registration) & (a.date_unregistration.isna() | (a.date < a.date_unregistration))]
    a["week"] = a.date // 7
    agg = a.groupby(REG_KEY + ["week"]).agg(clicks=("sum_click", "sum"), active_days=("date", lambda s: s[a.loc[s.index, "sum_click"] > 0].nunique()), distinct_resources=("id_site", "nunique"), source_activity_rows=("date", "size")).reset_index()
    grid = grid.merge(agg, on=REG_KEY + ["week"], how="left", validate="one_to_one")
    for c in ["clicks", "active_days", "distinct_resources", "source_activity_rows"]:
        grid[c] = grid[c].fillna(0)
    sub = submissions[(submissions.date_submitted <= cutoff) & (submissions.is_banked == 0)].merge(assessments[["id_assessment", "code_module", "code_presentation"]], on="id_assessment", validate="many_to_one")
    if sub.duplicated(["id_assessment", "id_student"]).any():
        raise ValueError("Duplicate submissions")
    sub_lookup = {(int(r.id_student), int(r.id_assessment)): int(r.date_submitted) for r in sub.itertuples()}
    due = assessments[(assessments.assessment_type != "Exam") & assessments.date.notna() & (assessments.date <= cutoff)]
    status_rows, submitted_counts, absent_counts, scheduled_counts = [], [], [], []
    grouped_subs = {k: s for k, s in sub.groupby(REG_KEY)}
    grouped_due = {k: d for k, d in due.groupby(["code_module", "code_presentation"])}
    for r in grid.itertuples():
        count = absent = scheduled = 0
        known = pd.notna(r.eligible_days) and r.eligible_days > 0
        ss = grouped_subs.get((r.code_module, r.code_presentation, r.id_student))
        if known and ss is not None:
            mask = (ss.date_submitted >= max(r.start_day, r.date_registration)) & (ss.date_submitted <= r.end_day)
            if pd.notna(r.date_unregistration):
                mask &= ss.date_submitted < r.date_unregistration
            count = int(mask.sum())
        dd = grouped_due.get((r.code_module, r.code_presentation), pd.DataFrame())
        for ar in dd.itertuples():
            if not r.start_day <= ar.date <= r.end_day:
                continue
            state = "unknown_eligibility"
            recorded = sub_lookup.get((int(r.id_student), int(ar.id_assessment)))
            eligible_on_due = eligibility(r.date_registration, r.date_unregistration, int(ar.date), int(ar.date), cutoff)
            if eligible_on_due == 0:
                state = "ineligible_on_due_date"
            elif eligible_on_due == 1:
                scheduled += 1
                if recorded is not None and recorded <= r.end_day:
                    state = "nonbanked_submission_recorded"
                else:
                    state = "no_nonbanked_submission_by_week_end"
                    absent += 1
            status_rows.append({"person_id": int(r.id_student), "course": r.code_module + "_" + r.code_presentation, "week": int(r.week), "assessment_id": int(ar.id_assessment), "due_day": int(ar.date), "as_of_day": int(r.end_day), "state": state, "score_status": "withheld_release_time_unknown"})
        submitted_counts.append(count if known else np.nan)
        absent_counts.append(absent if known else np.nan)
        scheduled_counts.append(scheduled if known else np.nan)
    grid["nonbanked_submissions"] = submitted_counts
    grid["scheduled_no_submission"] = absent_counts
    grid["scheduled_opportunities"] = scheduled_counts
    grid["clicks_per_eligible_day"] = grid.clicks / grid.eligible_days.replace(0, np.nan)
    grid["observation_status"] = np.select([grid.eligible_days.isna(), grid.eligible_days.eq(0), grid.clicks.eq(0)], ["unknown", "ineligible", "zero_recorded_activity"], default="recorded_activity")
    for c in ["clicks", *FEATURES]:
        grid.loc[grid.eligible_days.isna() | grid.eligible_days.eq(0), c] = np.nan
    grid["logging_completeness"] = "unknown"
    grid["score_status"] = "withheld_release_time_unknown"
    grid["course"] = grid.code_module + "_" + grid.code_presentation
    grid["prior_attempt_group"] = np.where(grid.num_of_prev_attempts.eq(0), "first_attempt", "repeat_attempt")
    grid = grid.rename(columns={"id_student": "person_id"})
    # Explicit output allowlist excludes final_result, raw withdrawal dates and scores.
    columns = ["person_id", "course", "week", "start_day", "end_day", "eligible_days", "prior_attempt_group", "observation_status", "logging_completeness", "score_status", "clicks", *FEATURES, "scheduled_opportunities", "source_activity_rows"]
    return grid[columns].sort_values(["course", "person_id", "week"]).reset_index(drop=True), pd.DataFrame(status_rows)


def prepare(config_path="configs/stage1.json"):
    cfg = read_json(config_path)
    db = connection()
    info = db.execute("SELECT code_module,code_presentation,id_student,num_of_prev_attempts FROM studentInfo").df()
    ids = sorted(map(int, info.id_student.unique()))
    assignments = {i: split_person(i, cfg["split_salt"], cfg["development_fraction"]) for i in ids}
    splits = {s: [i for i in ids if assignments[i] == s] for s in ["development", "reserved"]}
    write_json("artifacts/data/splits.json", {"rule": "salted SHA256 first 64 bits / 2**64 < 0.7", "salt": cfg["split_salt"], "group": "id_student across all registrations", "assignments": splits, "counts": {k: len(v) for k,v in splits.items()}})
    # Reserve people before reading any interaction or assessment value for features.
    info = info[info.id_student.map(assignments).eq("development")]
    regs = info.merge(db.execute("SELECT * FROM studentRegistration").df(), on=REG_KEY, validate="one_to_one")
    cutoff = cfg["cutoff_day"]
    assessments = db.execute("SELECT * FROM assessments").df()
    candidates, selected, seen_modules = [], [], set()
    for (module, presentation), r in regs.groupby(["code_module", "code_presentation"], sort=True):
        weeks = [sum(eligibility(x.date_registration, x.date_unregistration, w*7, w*7+6, cutoff) == 7 for w in range(cfg["weeks"])) for x in r.itertuples()]
        n = sum(x >= cfg["minimum_history_weeks"] for x in weeks)
        na = len(assessments[(assessments.code_module == module) & (assessments.code_presentation == presentation) & (assessments.assessment_type != "Exam") & (assessments.date.between(0, cutoff))])
        qualifies = n >= cfg["minimum_people"] and na >= 2
        candidates.append({"course": module + "_" + presentation, "development_registrations": len(r), "people_with_eight_full_eligible_weeks": n, "dated_nonexam_assessments_by_cutoff": na, "qualifies": qualifies})
        if qualifies and module not in seen_modules and len(selected) < 2:
            selected.append((module, presentation))
            seen_modules.add(module)
    if len(selected) < 2:
        raise ValueError("Fewer than two structurally supported presentations")
    regs = regs[regs[["code_module", "code_presentation"]].apply(tuple, axis=1).isin(selected)].copy()
    db.register("selected_regs", regs[REG_KEY])
    activity = db.execute(f"SELECT s.* FROM studentVle s JOIN selected_regs r USING(code_module,code_presentation,id_student) WHERE date BETWEEN 0 AND {int(cutoff)}").df()
    # Score is never loaded into the feature layer.
    submissions = db.execute(f"SELECT s.id_assessment,s.id_student,s.date_submitted,s.is_banked FROM studentAssessment s JOIN assessments a USING(id_assessment) JOIN selected_regs r USING(code_module,code_presentation,id_student) WHERE date_submitted <= {int(cutoff)}").df()
    weekly, ast = build_weekly(regs, activity, submissions, assessments, cutoff)
    out = Path("data/prepared")
    out.mkdir(parents=True, exist_ok=True)
    weekly.to_parquet(out / "weekly.parquet", index=False)
    ast.to_parquet(out / "assessment_status.parquet", index=False)
    course_names = [m + "_" + p for m,p in selected]
    questions = []
    for ix, (kind, course, role, text) in enumerate([
        ("personal_change", course_names[0], "learner", "How does my recent recorded activity compare with my earlier baseline and course peers?"),
        ("reference_sensitivity", course_names[1], "researcher", "Does the comparison change for same-prior-attempt peers or for an earlier study stage?"),
        ("measurement_limits", course_names[1], "instructor", "What can recorded activity and scheduled submission records establish when eligibility and grade availability are limited?"),
    ]):
        w = weekly[weekly.course.eq(course)]
        per = w.groupby("person_id").eligible_days.agg(lambda s: int(s.eq(7).sum()))
        pool = per[per.ge(8)].index.tolist() if ix < 2 else per[per.gt(0) & per.lt(8)].index.tolist()
        if not pool:
            pool = per.index.tolist()
        used = {q.person_id for q in questions}
        pool = [int(x) for x in pool if x not in used]
        person = min(pool, key=lambda i: digest({"selection_seed": cfg["seed"], "person": i, "kind": kind}))
        questions.append(Question(question_id=f"dev_{ix+1}", role=role, kind=kind, text=text, person_id=person, course=course, cutoff_day=cutoff))
    write_json("artifacts/data/questions.json", [q.model_dump() for q in questions])
    manifest = {"created_utc": now(), "config_sha256": digest(cfg), "archive_sha256": read_json("artifacts/data/manifest.json")["archive_sha256"], "cutoff_day": cutoff, "features": FEATURES, "selected_courses": course_names, "candidates": candidates, "rows": len(weekly), "distinct_development_people": int(weekly.person_id.nunique()), "files": {p.name: file_hash(p) for p in out.glob("*.parquet")}, "split_sha256": file_hash("artifacts/data/splits.json"), "selection": "First qualifying presentation from each of first two qualifying modules, lexical order. Focal hash only; case 3 uses 1-7 full eligible weeks as a structural incomplete-history condition.", "course_week_support": weekly.groupby(["course", "week"]).agg(eligible_people=("eligible_days", lambda s: int(s.gt(0).sum())), recorded_people=("observation_status", lambda s: int(s.eq("recorded_activity").sum()))).reset_index().to_dict("records"), "exclusions": {"activity_outside_eligibility": int(len(activity) - weekly.source_activity_rows.sum()), "banked_rows_withheld_by_cutoff": int(submissions.is_banked.eq(1).sum())}}
    write_json("artifacts/data/preparation.json", manifest)
    print({"courses": course_names, "weekly_rows": len(weekly), "questions": [q.model_dump() for q in questions]}, flush=True)
    db.close()
