"""Post-hoc exact-row sensitivity for the SAME frozen Stage 6 cases.

Usage: python duplicate_sensitivity.py [--output FILE]
Requires pyarrow==20.0.0 (only to read preserved development Parquet bundles).
No raw data, reserved observations, model, evaluator or frozen artifact is changed.
Independent row-loop summaries reproduce the published equal-person estimator.
The alternative was constructed by scripts/stage2/statistical_checks.py from
the full development grid; its older reference exclusions are NOT used here.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics

import pyarrow
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
PRIMARY = ROOT / "artifacts/stage6/source"
ALTERNATIVE = ROOT / "artifacts/stage2/statistics/exact_row_sensitivity_source"


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def average(values):
    observed = [float(x) for x in values if x is not None]
    return math.fsum(observed) / len(observed) if observed else None


def sign(value):
    return None if value is None else (value > 0) - (value < 0)


def summaries(rows, question, request, config, excluded):
    profile = config["profiles"][question["profile"]]
    feature = request["feature"]
    window = profile[request["window"]]
    reference = config["references"][request["reference"]]
    reference_window = profile["baseline"] if reference["time"] == "baseline" else window
    data = [r for r in rows if r["course"] == question["course"] and r["end_day"] <= question["cutoff_day"]]
    focal = [r for r in data if r["person_id"] == question["person_id"]]
    assert focal
    peers = [r for r in data if r["person_id"] not in excluded | {question["person_id"]}]
    if reference["group"] == "same_prior_attempt":
        peers = [r for r in peers if r["prior_attempt_group"] == focal[0]["prior_attempt_group"]]
    per_person = defaultdict(list)
    for r in peers:
        if reference_window[0] <= r["week"] <= reference_window[1] and r[feature] is not None:
            per_person[r["person_id"]].append(r[feature])
    result = {"people": len(per_person), "observations": sum(map(len, per_person.values())),
              "peer_mean": average([average(values) for values in per_person.values()]),
              "window": window, "reference_window": reference_window}
    for label, bounds in [("focal", window), ("baseline", profile["baseline"]), ("recent", profile["recent"])]:
        values = [r[feature] for r in focal if bounds[0] <= r["week"] <= bounds[1] and r[feature] is not None]
        result[label + "_mean"] = average(values)
        result[label + "_observations"] = len(values)
    supported = result["people"] >= config["minimum_peer_people"] and result["focal_observations"] >= config["minimum_focal_weeks"]
    personal = min(result["baseline_observations"], result["recent_observations"]) >= config["minimum_focal_weeks"]
    result["status"] = "supported" if supported else "insufficient_evidence"
    result["personal_status"] = "supported" if personal else "insufficient_evidence"
    result["contrast"] = result["focal_mean"] - result["peer_mean"] if supported else None
    result["personal_change"] = result["recent_mean"] - result["baseline_mean"] if personal else None
    return result


def matches(a, b):
    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
        return math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10)
    return a == b


def magnitude_summary(values):
    values = [abs(x) for x in values if x is not None]
    return {"n": len(values), "minimum": min(values) if values else None,
            "median": statistics.median(values) if values else None,
            "maximum": max(values) if values else None}


def describe(records):
    click = [r for r in records if r["request"]["feature"] == "clicks_per_eligible_day"]
    supported = [r for r in click if r["primary"]["status"] == "supported"]
    changed = [r for r in supported if r["contrast_direction_changed"]]
    personal = {}
    for r in click:
        personal.setdefault(r["question_id"], r)
    personal_supported = [r for r in personal.values() if r["primary"]["personal_status"] == "supported"]
    assessment = [r for r in records if r["request"]["feature"] in {"nonbanked_submissions", "scheduled_no_submission"}]
    return {"records": len(records), "click_records": len(click),
            "supported_click_peer_contrasts": len(supported),
            "click_peer_contrast_sign_changes": [{"question_id": r["question_id"], "reference": r["request"]["reference"],
                                                    "primary": r["primary"]["contrast"], "alternative": r["alternative"]["contrast"]} for r in changed],
            "absolute_click_peer_contrast_shift": magnitude_summary([r["alternative"]["contrast"] - r["primary"]["contrast"] for r in supported]),
            "absolute_click_peer_mean_shift": magnitude_summary([r["alternative"]["peer_mean"] - r["primary"]["peer_mean"] for r in click]),
            "unique_click_personal_summaries": len(personal),
            "supported_click_personal_changes": len(personal_supported),
            "click_personal_change_sign_changes": [{"question_id": r["question_id"], "primary": r["primary"]["personal_change"],
                                                       "alternative": r["alternative"]["personal_change"]} for r in personal_supported if r["personal_direction_changed"]],
            "absolute_click_personal_change_shift": magnitude_summary([r["alternative"]["personal_change"] - r["primary"]["personal_change"] for r in personal_supported]),
            "assessment_records": len(assessment), "assessment_records_unchanged": sum(r["primary"] == r["alternative"] for r in assessment),
            "support_status_changes": sum(r["primary"]["status"] != r["alternative"]["status"] or r["primary"]["personal_status"] != r["alternative"]["personal_status"] for r in records)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_suffix(".json"))
    args = parser.parse_args()
    config_path = ROOT / "configs/stage6.json"
    tasks_path = ROOT / "artifacts/stage6/tasks/manifest.json"
    rubric_path = ROOT / "artifacts/stage6/evaluator_only/rubrics.json"
    config, tasks, rubric = map(read, [config_path, tasks_path, rubric_path])
    sources = [config_path, tasks_path, rubric_path, Path(__file__),
               ROOT / "scripts/stage2/statistical_checks.py", ROOT / "artifacts/stage2/statistics/sensitivity.json"]
    bundles = []
    for directory in [PRIMARY, ALTERNATIVE]:
        manifest = read(directory / "manifest.json")
        sources.append(directory / "manifest.json")
        for name, expected in manifest["files"].items():
            assert sha(directory / name) == expected, (directory, name)
            sources.append(directory / name)
        rows = [{k: clean(v) for k, v in r.items()} for r in pq.read_table(directory / "weekly.parquet").to_pylist()]
        bundles.append(rows)
    key = lambda r: (r["person_id"], r["course"], r["week"])
    primary, alternate = [{key(r): r for r in rows} for rows in bundles]
    assert len(primary) == len(bundles[0]) and len(alternate) == len(bundles[1])
    assert primary.keys() == alternate.keys()
    other_fields = set(next(iter(primary.values()))) - {"clicks", "clicks_per_eligible_day"}
    assert all(primary[k][f] == alternate[k][f] for k in primary for f in other_fields)
    assert sha(PRIMARY / "assessment_status.parquet") == sha(ALTERNATIVE / "assessment_status.parquet")
    split_path = ROOT / "artifacts/data/splits.json"
    sources.append(split_path)
    development = set(read(split_path)["assignments"]["development"])
    assert {r["person_id"] for r in bundles[0]} <= development
    excluded = set(read(PRIMARY / "manifest.json")["excluded_reference_people"])
    assert excluded == set(tasks["reference_pool_excluded_people"]) and len(excluded) == 81
    assert len(tasks["new_focal_people"]) == 24
    required = {r["question_id"]: set(r["independent_facts"]) for r in rubric["rubrics"]}
    records = []
    checks = 0
    for task in tasks["tasks"]:
        q = task["question"]
        directory = ROOT / "artifacts/stage6/comparison/baseline" / q["question_id"]
        sources.extend([directory / "requests.json", directory / "tool_results.json"])
        saved = read(directory / "tool_results.json")
        for request in read(directory / "requests.json"):
            results = [summaries(rows, q, request, config, excluded) for rows in bundles]
            evidence = next(e for e in saved.values() if e["request"] == request)
            expected = {**evidence["summary"], **{k: evidence[k] for k in ["people", "observations", "status", "window", "reference_window"]}}
            for field, value in results[0].items():
                assert matches(value, expected[field]), (q["question_id"], request, field, value, expected[field])
                checks += 1
            a, b = results
            records.append({"question_id": q["question_id"], "family": q["kind"], "request": request,
                            "required_fact": request["feature"] + ":" + request["reference"] in required[q["question_id"]],
                            "primary": a, "alternative": b,
                            "contrast_direction_changed": sign(a["contrast"]) != sign(b["contrast"]),
                            "personal_direction_changed": sign(a["personal_change"]) != sign(b["personal_change"])})
    required_records = [r for r in records if r["required_fact"]]
    assert len(required_records) == sum(len(v) for v in required.values()) == 52
    directions = []
    for task in tasks["tasks"]:
        q = task["question"]
        if q["kind"] not in {"reference_sensitivity", "alternate_windows"}:
            continue
        rs = [r for r in records if r["question_id"] == q["question_id"] and r["request"]["feature"] == "clicks_per_eligible_day"]
        classifications = {}
        for version in ["primary", "alternative"]:
            signs = {sign(r[version]["contrast"]) for r in rs}
            classifications[version] = "insufficient_evidence" if None in signs else "same_direction" if len(signs) == 1 else "direction_differs"
        directions.append({"question_id": q["question_id"], **classifications,
                           "changed": classifications["primary"] != classifications["alternative"]})
    old = read(ROOT / "artifacts/stage2/statistics/sensitivity.json")
    output = {"analysis": "Post-hoc exact-row sensitivity on the frozen Stage 6 development cases",
              "scope": "Same 24 people, profiles, equal-person/within-person-week estimator, thresholds, and 81 exclusions; no model reruns or rescoring",
              "alternative": "Preserved full development bundle formed by dropping exact equal interaction rows; assessment features unchanged",
              "raw_deduplication_rerun": False,
              "historical_alternative_construction": {k: old[k] for k in ["source_rows", "exact_duplicate_excess", "limitation"]},
              "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(sources))},
              "environment": {"parquet_reader": "pyarrow " + pyarrow.__version__, "arithmetic": "Python standard library math.fsum"},
              "checks": {"weekly_rows_each": len(primary), "distinct_development_people": len({r["person_id"] for r in bundles[0]}),
                         "weekly_key_sets_identical": True, "nonclick_fields_identical": True, "assessment_file_identical": True,
                         "primary_values_checked_against_frozen_evidence": checks, "reserved_observations_read": False,
                         "excluded_reference_people": len(excluded)},
              "all_enumeration_requests": describe(records), "required_fact_records": describe(required_records),
              "reference_direction_questions": directions,
              "featured_case_05": [r for r in records if r["question_id"] == "s6_05"],
              "records": records,
              "limitations": ["Exact equal source rows need not be erroneous; neither treatment identifies unique click events.",
                              "Only means, differences, directions, and support are recalculated; no bootstrap intervals are recomputed.",
                              "Original dashboards, figures, agent behavior and frozen completeness scores remain unchanged.",
                              "This is a development-data sensitivity analysis, not an independent test or a learning-outcome evaluation."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({k: output[k] for k in ["checks", "all_enumeration_requests", "required_fact_records", "reference_direction_questions"]}, indent=2))


if __name__ == "__main__":
    main()
