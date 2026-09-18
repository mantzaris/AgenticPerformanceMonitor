"""Typed requests and a small shared scientific registry, not an analysis DSL."""
from __future__ import annotations

from pathlib import Path
from typing import Literal
from pydantic import Field, model_validator
from ..common import read_json, digest, now
from ..contracts import Contract, EvidenceRecord, ClaimRecord, Panel
from ..prepare import FEATURES

ROOT = Path("artifacts/stage2")


class Question(Contract):
    question_id: str
    role: Literal["learner", "instructor", "researcher"] = "researcher"
    kind: str
    text: str
    person_id: int
    course: str
    profile: str
    cutoff_day: int
    split: Literal["development"] = "development"


class Request(Contract):
    tool: Literal["analyze"] = "analyze"
    question_id: str
    feature: Literal["clicks_per_eligible_day", "active_days", "distinct_resources", "nonbanked_submissions", "scheduled_no_submission"]
    reference: Literal["course", "same_prior_attempt", "early_stage"]
    window: Literal["recent", "baseline"] = "recent"


class Evidence(EvidenceRecord):
    request: Request


class Specification(Contract):
    question_id: str
    cutoff_day: int
    evidence_ids: list[str] = Field(min_length=1, max_length=6)
    claims: list[ClaimRecord] = Field(min_length=1, max_length=10)
    panels: list[Panel] = Field(min_length=2, max_length=10)
    conclusion: Literal["descriptive", "same_direction", "direction_differs", "insufficient_evidence"]
    followups: list[Literal["change_reference", "change_window", "check_assessment_availability"]] = Field(max_length=3)


class Action(Contract):
    action: Literal["analyze", "final"]
    requests: list[Request] = Field(default_factory=list, max_length=6)
    specification: Specification | None = None

    @model_validator(mode="after")
    def shape(self):
        if self.action == "analyze" and (not self.requests or self.specification is not None):
            raise ValueError("analyze requires 1–6 requests and no specification")
        if self.action == "final" and (self.requests or self.specification is None):
            raise ValueError("final requires specification and no requests")
        return self


class Registry:
    def __init__(self, path="configs/stage2.json"):
        self.cfg = read_json(path)
        for name, p in self.cfg["profiles"].items():
            if p["cutoff_day"] > 83 or p["cutoff_day"] % 7 != 6:
                raise ValueError(f"profiles.{name}.cutoff_day: require a complete week through day 83")
            for label in ("baseline", "recent"):
                a, b = p[label]
                if a < 0 or a > b or b * 7 + 6 > p["cutoff_day"]:
                    raise ValueError(f"profiles.{name}.{label}: invalid or post-cutoff window")
            if p["baseline"][1] >= p["recent"][0]:
                raise ValueError(f"profiles.{name}: baseline must precede recent window")

    def profile(self, q):
        q = Question.model_validate(q)
        if q.kind not in self.cfg["question_kinds"] or q.profile not in self.cfg["profiles"]:
            raise ValueError("question.kind/profile: not in admissible registry")
        p = self.cfg["profiles"][q.profile]
        if q.cutoff_day != p["cutoff_day"]:
            raise ValueError(f"question.cutoff_day: profile {q.profile} requires {p['cutoff_day']}")
        return p

    def context(self, q, req, group):
        p = self.profile(q)
        if req.question_id != q.question_id:
            raise ValueError("request.question_id: cross-question access is forbidden")
        rule = self.cfg["references"][req.reference]
        window = p[req.window]
        ref_window = p["baseline"] if rule["time"] == "baseline" else window
        label = f"{q.course}: {rule['description']}"
        if rule["group"] == "same_prior_attempt":
            label += f" ({group})"
        label += f"; reference weeks {ref_window[0]}–{ref_window[1]}"
        return window, ref_window, label

    def seed(self, q, req):
        # Excludes method/task ID: identical underlying contrasts have identical Monte Carlo intervals.
        return self.cfg["seed"] + int(digest([q.course, q.person_id, q.profile, req.feature, req.reference, req.window])[:7], 16)


def seal(record):
    value = record.model_dump() if hasattr(record, "model_dump") else dict(record)
    value.pop("evidence_id", None)
    stable = {**value, "provenance": {k:v for k,v in value["provenance"].items() if k != "executed_utc"}}
    return Evidence(evidence_id="s2_" + digest(stable)[:20], **value)


def append_event(event, path=ROOT / "execution.jsonl"):
    import json, os
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps({"utc": now(), **event}, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
