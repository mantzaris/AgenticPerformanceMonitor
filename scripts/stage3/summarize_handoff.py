"""Post-execution tabulation of frozen scores; does not rescore or change outputs.

This reporting-only script was added after the freeze. All judgments come from
the frozen report.py output. It is not additional pilot inference or evaluation.
"""
import argparse
from collections import Counter
from pathlib import Path

from trajectory_dashboards.common import file_hash, now, read_json, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError("Preserve existing report; choose a new output path")
    source = Path("artifacts/stage3/reports/per_question.json")
    rows = read_json(source)
    methods = []
    for method in ["baseline", "generic", "reference_sensitive", "coverage_aware"]:
        rr = [r for r in rows if r["method"] == method]
        family = {}
        for name in sorted({r["family"] for r in rr}):
            group = [r for r in rr if r["family"] == name]
            family[name] = {
                "question_denominator": len(group),
                "complete": sum(r["complete_requested_coverage"] for r in group),
                "valid": sum(r["valid_after_permitted_repair"] for r in group),
            }
        insuff = [r for r in rr if r["family"] == "insufficient_support"]
        availability = [a for r in rr for a in r["requested_answers"] if a["category"] == "availability"]
        failed = Counter()
        for r in rr:
            if not r["valid_after_permitted_repair"]:
                raw = read_json(Path("artifacts/stage3/pilot") / method / r["question_id"] / "result.json")
                failed[raw.get("error", "unknown failure")] += 1
        methods.append({
            "method": method,
            "families": family,
            "scoped_insufficiency_answers": sum(len(r["scoped_insufficiency_items"]) for r in insuff),
            "scoped_insufficiency_denominator": sum(len(r["requested_answers"]) for r in insuff),
            "availability_answers": sum(a["covered"] for a in availability),
            "availability_denominator": len(availability),
            "availability_method_selected": sum(a["covered"] and a["origin"] == "method_selected" for a in availability),
            "availability_compiler_supplied": sum(a["covered"] and a["origin"] == "compiler_supplied" for a in availability),
            "optional_personal_history_questions": sum(r.get("optional", {}).get("personal_history_selected_but_not_requested", False) for r in rr),
            "exact_repeated_selected_panels": sum(r.get("optional", {}).get("repeated_panel_signatures", 0) for r in rr),
            "adaptive_episodes": sum(r.get("subsequent_analysis_after_results", False) for r in rr),
            "retrieved_but_omitted_in_accepted": sum(len(r["retrieved_but_omitted"]) for r in rr if r["valid_after_permitted_repair"]),
            "retrieved_but_omitted_in_failed": sum(len(r["retrieved_but_omitted"]) for r in rr if not r["valid_after_permitted_repair"]),
            "failure_messages": dict(failed),
        })
    write_json(output, {
        "created_utc": now(), "source": str(source), "source_sha256": file_hash(source),
        "status": "Post-execution descriptive aggregation of unchanged frozen scores",
        "notes": [
            "Eight scoped insufficiency items: two comparisons in each of four phrasings (two people).",
            "Eight availability requests: four observation-limit and four assessment questions.",
            "Failures count as no accepted answer; omitted items in failed episodes are separately identified.",
            "Exact repeated panels do not detect redundant semantic content under different evidence IDs.",
            "All paired phrasings remain dependent; no significance test or new score definition.",
        ], "methods": methods,
    })


if __name__ == "__main__":
    main()
