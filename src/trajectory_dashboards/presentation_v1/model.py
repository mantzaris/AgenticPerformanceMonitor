"""Map only saved, selected content; never inspect rubrics or unselected tool results."""
from pathlib import Path
from copy import deepcopy
from ..common import read_json, digest, file_hash

EXAMPLES = [
    ("personal", "Case A", "compact_a", "s6_01"),
    ("references", "Case B", "compact_a", "s6_05"),
    ("observations", "Case C", "compact_a", "s6_09"),
    ("assessments", "Case D", "compact_a", "s6_17"),
    ("incomplete", "Case E", "compact_a", "s6_15"),
    ("baseline", "Case E", "baseline", "s6_15"),
]
FEATURES = {
    "clicks_per_eligible_day": "Recorded click rate",
    "nonbanked_submissions": "Non-banked submissions",
    "scheduled_no_submission": "Scheduled assessments without a recorded submission",
    "active_days": "Days with recorded activity",
}
QUESTIONS = {
    "personal_change": "How has my recorded click rate changed, and how does it compare with peers?",
    "reference_sensitivity": "How does my recent click rate compare across peer definitions?",
    "observation_limits": "What can my recent activity and assessment records establish?",
    "assessment_availability": "What do my assessment records show about submissions and learning?",
    "insufficient_support": "Can my recent click rate be compared with my history and with peers?",
}


def reference_name(e):
    if e["reference"] == "course":
        return "Presentation peers"
    if e["reference"] == "early_stage":
        return "Presentation peers · earlier period"
    if e["reference"] == "same_prior_attempt":
        group = "repeat attempt" if "(repeat_attempt)" in e["reference_label"] else "first attempt"
        return f"Same prior-attempt group · {group}"
    raise ValueError("Unknown saved reference")


def layout_for(claims, evidence):
    """Semantic dispatch, independent of case identifiers and evaluation labels."""
    personal = [c for c in claims if c["template"] == "personal_change"]
    comparisons = [evidence[c["evidence_id"]] for c in claims if c["template"] == "comparison"]
    if personal:
        return "personal" if any(evidence[c["evidence_id"]]["summary"]["personal_status"] == "supported" for c in personal) else "support"
    if comparisons and all(e["status"] != "supported" for e in comparisons):
        return "observations"
    if comparisons and all(e["feature"] in {"nonbanked_submissions", "scheduled_no_submission"} for e in comparisons):
        return "assessments"
    if len({(e["reference"], tuple(e["reference_window"])) for e in comparisons}) > 1:
        return "references"
    return "comparison"


def deduplicate_claims(spec, bound, provenance, evidence):
    result, signatures = [], {}
    for index, (c, text, origin) in enumerate(zip(spec["claims"], bound["claims"], provenance["claims"], strict=True)):
        if c["template"] != text["template"] or c["evidence_id"] != text["evidence_id"]:
            raise ValueError("Saved claim binding disagrees with the specification")
        e = evidence[c["evidence_id"]]
        # Exact wording AND analytical meaning AND selection origin must agree.
        # Personal meaning deliberately excludes an irrelevant peer definition.
        if c["template"] == "personal_change":
            meaning = {k: e["summary"][k] for k in (
                "baseline_window", "recent_window", "baseline_mean", "recent_mean",
                "baseline_observations", "recent_observations", "personal_change", "personal_status")}
            signature = digest([c["template"], text["text"], origin["origin"],
                                e["feature"], e["unit"], e["focal_id"], e["cutoff_day"], meaning])
        else:
            signature = digest([c, text, origin])
        if signature in signatures:
            existing = result[signatures[signature]]
            existing["original_indices"].append(index)
            existing["evidence_ids"].append(c["evidence_id"])
        else:
            signatures[signature] = len(result)
            result.append({**c, "original_text": text["text"], "origin": origin["origin"],
                           "original_indices": [index], "evidence_ids": [c["evidence_id"]]})
    return result


def load(source, label):
    source = Path(source)
    names = ["question.json", "spec.json", "bound.json", "evidence.json", "selection_provenance.json"]
    q, spec, bound, all_evidence, prov = [read_json(source / n) for n in names]
    if q["split"] != "development" or bound["validation"] != "PASS":
        raise ValueError("Only saved validated development dashboards are allowed")
    evidence = {eid: all_evidence[eid] for eid in spec["evidence_ids"]}
    for eid, e in evidence.items():
        if digest(e) != bound["evidence_hashes"][eid]:
            raise ValueError("Saved evidence changed since numerical validation")
        if e["focal_id"] != q["person_id"] or e["cutoff_day"] != q["cutoff_day"]:
            raise ValueError("Context mismatch")
    for item in spec["claims"] + spec["panels"]:
        if item["evidence_id"] not in evidence:
            raise ValueError("Unselected evidence")
    claims = deduplicate_claims(spec, bound, prov, evidence)
    panels = [{**p, "origin": origin["origin"], "original_index": i, "reason": origin.get("reason")}
              for i, (p, origin) in enumerate(zip(spec["panels"], prov["panels"], strict=True))]
    comparisons = [c for c in claims if c["template"] == "comparison"]
    # Only claim-selected comparisons become controls/answer cards. A personal
    # selection carrying a recent peer summary must NOT create a peer answer.
    comparison_ids = list(dict.fromkeys(c["evidence_id"] for c in comparisons))
    compatible = len(comparison_ids) > 1 and len({
        (evidence[k]["feature"], tuple(evidence[k]["window"]), evidence[k]["summary"]["focal_mean"])
        for k in comparison_ids}) == 1
    result = {
        "schema": "saved-presentation-v1", "label": label, "source": str(source),
        "question": q, "question_heading": QUESTIONS.get(q["kind"], q["text"]),
        "spec": spec, "bound": bound, "provenance": prov, "claims": claims,
        "panels": panels, "evidence": evidence, "layout": layout_for(claims, evidence),
        "comparison_ids": comparison_ids, "switchable": compatible,
        "method": "Deterministic enumeration" if prov["interface"] == "baseline" else "Qwen2.5-14B · compact A",
        "selection_status": bound["selection_origin"],
        "source_hashes": {str(source / n): file_hash(source / n) for n in names},
        "presentation_changes": ["semantic layout", "anonymous display label", "deterministic concise wording",
                                 "exact personal-claim duplicates collapsed with provenance", "saved-reference selector"],
    }
    return deepcopy(result)
