"""Post-hoc paired comparisons of the saved Stage 6 completeness outcomes.

Run from any directory with Python 3.8+; only the standard library is required.
This does not rerun models, alter the scorer, read reserved observations, or
replace the frozen primary scores. The conditional B17--20 scenario is arithmetic
sensitivity, not independent adjudication. Each comparison uses 24 paired people,
not 96 independent observations. No population-sampling validity is asserted for
the structurally selected development cases.
"""

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "artifacts/stage6/reports/per_case.json"
TASKS = ROOT / "artifacts/stage6/tasks/manifest.json"
CONDITIONS = ("baseline", "compact_a", "derived_b", "binding_c")
COMPARISONS = (
    ("compact_a", "binding_c"),
    ("derived_b", "binding_c"),
    ("compact_a", "derived_b"),
    ("baseline", "compact_a"),
    ("baseline", "derived_b"),
    ("baseline", "binding_c"),
)
DISPUTED_B_CASES = ("s6_17", "s6_18", "s6_19", "s6_20")


def exact_mcnemar(left_only, right_only):
    """Two-sided exact conditional test: 2*Binomial(n, .5) smaller tail.

    Conditional on discordance under marginal homogeneity, the two directions
    are equiprobable. For p=.5 this doubled smaller tail equals the usual exact
    probability-ordering binomial test. There is no continuity correction.
    """
    n = left_only + right_only
    if n == 0:
        return Fraction(1)
    tail = sum(math.comb(n, k) for k in range(min(left_only, right_only) + 1))
    return min(Fraction(1), Fraction(2 * tail, 2 ** n))


def holm_adjust(probabilities):
    """Holm step-down FWER adjustment, keeping exact rational arithmetic."""
    order = sorted(range(len(probabilities)), key=probabilities.__getitem__)
    adjusted = [None] * len(probabilities)
    running = Fraction(0)
    for rank, index in enumerate(order):
        running = max(running, (len(probabilities) - rank) * probabilities[index])
        adjusted[index] = min(Fraction(1), running)
    return adjusted


def scenario(outcomes):
    comparisons = []
    probabilities = []
    for left, right in COMPARISONS:
        ids = sorted(outcomes[left])
        assert set(ids) == set(outcomes[right]) and len(ids) == 24
        groups = {key: [] for key in ("both_complete", "right_only", "left_only", "neither_complete")}
        for qid in ids:
            a, b = outcomes[left][qid], outcomes[right][qid]
            key = ("both_complete" if a and b else "right_only" if b else
                   "left_only" if a else "neither_complete")
            groups[key].append(qid)
        n_left, n_right = len(groups["left_only"]), len(groups["right_only"])
        p = exact_mcnemar(n_left, n_right)
        probabilities.append(p)
        comparisons.append({
            "left": left, "right": right, "paired_people": len(ids),
            "counts": {key: len(value) for key, value in groups.items()},
            "case_ids": groups,
            "net_complete_cases_right_minus_left": n_right - n_left,
            "difference_percentage_points_right_minus_left": 100 * (n_right - n_left) / len(ids),
            "exact_two_sided_mcnemar_p": float(p),
            "exact_p_fraction": str(p),
        })
    for row, adjusted in zip(comparisons, holm_adjust(probabilities)):
        row["holm_adjusted_p_six_comparisons"] = float(adjusted)
        row["holm_adjusted_p_fraction"] = str(adjusted)
    return {
        "complete_visible": {condition: sum(outcomes[condition].values()) for condition in CONDITIONS},
        "comparisons": comparisons,
    }


def build():
    rows = json.loads(SOURCE.read_text())
    tasks = json.loads(TASKS.read_text())
    assert len(rows) == 96
    assert len({case["person_id"] for case in tasks["cases"]}) == 24
    expected_ids = {task["question"]["question_id"] for task in tasks["tasks"]}
    outcomes = {condition: {} for condition in CONDITIONS}
    for row in rows:
        condition, qid = row["condition"], row["question_id"]
        assert qid not in outcomes[condition]
        assert isinstance(row["complete_requested_coverage"], bool)
        assert row["valid_after_repair"] or not row["complete_requested_coverage"]
        outcomes[condition][qid] = row["complete_requested_coverage"]
    assert all(set(values) == expected_ids for values in outcomes.values())
    primary = scenario(outcomes)
    assert primary["complete_visible"] == dict(zip(CONDITIONS, (24, 21, 15, 15)))
    sensitivity = {condition: values.copy() for condition, values in outcomes.items()}
    for qid in DISPUTED_B_CASES:
        assert sensitivity["derived_b"][qid] is False
        sensitivity["derived_b"][qid] = True
    conditional = scenario(sensitivity)
    assert conditional["complete_visible"] == dict(zip(CONDITIONS, (24, 21, 19, 15)))
    # Known exact values guard the test and multiplicity implementation.
    assert exact_mcnemar(7, 1) == Fraction(9, 128)
    assert exact_mcnemar(3, 3) == 1
    assert exact_mcnemar(0, 0) == 1
    assert exact_mcnemar(9, 0) == Fraction(1, 256)
    assert holm_adjust([Fraction(1, 100), Fraction(2, 100), Fraction(3, 100)]) == [Fraction(3, 100), Fraction(4, 100), Fraction(4, 100)]
    return {
        "analysis": "Post-hoc exact paired comparison of frozen visible completeness",
        "sources": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (SOURCE, TASKS)},
        "endpoint": "complete_requested_coverage",
        "unit": "24 paired development people, one question per person; failures remain incomplete",
        "test": "Two-sided exact McNemar test, conditional Binomial(left_only + right_only, 0.5); no continuity correction",
        "multiplicity": "Holm adjustment across all six pairwise visible-completeness comparisons within each scenario",
        "scope": [
            "Added after review; not prespecified confirmatory inference.",
            "Tests assume independent paired cases; shared course/reference pools and structural selection limit generalization.",
            "No absence-of-difference or equivalence conclusion follows from a nonsignificant p-value.",
            "No calibrated population confidence interval is claimed for these selected development cases.",
            "The scenario crediting B17--20 is hypothetical sensitivity only; it is not corrected primary scoring or human review.",
        ],
        "frozen_primary": primary,
        "conditional_credit_B17_to_B20": conditional,
        "conditional_changed_case_ids": list(DISPUTED_B_CASES),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_suffix(".json"))
    args = parser.parse_args()
    report = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    for name in ("frozen_primary", "conditional_credit_B17_to_B20"):
        print(name, report[name]["complete_visible"])
        for row in report[name]["comparisons"]:
            print("{right} - {left}: delta={difference_percentage_points_right_minus_left:+.2f} pp; exact p={exact_two_sided_mcnemar_p:.6f}; Holm p={holm_adjusted_p_six_comparisons:.6f}".format(**row))


if __name__ == "__main__":
    main()
