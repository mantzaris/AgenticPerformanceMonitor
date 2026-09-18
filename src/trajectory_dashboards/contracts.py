from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class DatasetManifest(Contract):
    dataset: str
    source_url: str
    retrieved_utc: str
    license: str
    attribution: str
    archive_sha256: str
    files: dict[str, dict[str, Any]]
    counts: dict[str, Any]
    relationships: dict[str, Any]
    time_semantics: dict[str, str]
    observation_states: dict[str, str]


class Question(Contract):
    question_id: str
    role: Literal["learner", "instructor", "researcher"]
    kind: Literal["personal_change", "reference_sensitivity", "measurement_limits"]
    text: str
    person_id: int
    course: str
    cutoff_day: int = Field(ge=0)
    split: Literal["development"] = "development"


class AnalysisRequest(Contract):
    tool: Literal["analyze"] = "analyze"
    question_id: str
    feature: Literal["clicks_per_eligible_day", "active_days", "distinct_resources", "nonbanked_submissions", "scheduled_no_submission"]
    reference: Literal["course", "same_prior_attempt", "early_stage"]
    start_week: int = Field(ge=0)
    end_week: int = Field(ge=0)
    @model_validator(mode="after")
    def window(self):
        if self.start_week > self.end_week:
            raise ValueError("reversed window")
        return self


class EvidenceRecord(Contract):
    evidence_id: str
    question_id: str
    request: AnalysisRequest
    feature: str
    unit: str
    reference: str
    reference_label: str
    window: list[int]
    reference_window: list[int]
    cutoff_day: int
    status: Literal["supported", "insufficient_evidence"]
    people: int = Field(ge=0)
    observations: int = Field(ge=0)
    peer_ids: list[int]
    focal_id: int
    summary: dict[str, Any]
    peer_summary_rows: list[dict[str, Any]]
    trajectory: list[dict[str, Any]]
    observation_status: list[dict[str, Any]]
    assessment_status: list[dict[str, Any]]
    uncertainty: dict[str, Any]
    limitations: list[str]
    provenance: dict[str, Any]


class ClaimRecord(Contract):
    template: Literal["comparison", "personal_change", "measurement_limits"]
    evidence_id: str


class Panel(Contract):
    kind: Literal["trajectory", "comparison", "observation_status", "assessment_status"]
    evidence_id: str


class DashboardSpecification(Contract):
    question_id: str
    cutoff_day: int
    evidence_ids: list[str] = Field(min_length=1, max_length=6)
    claims: list[ClaimRecord] = Field(min_length=1, max_length=6)
    panels: list[Panel] = Field(min_length=2, max_length=6)
    annotation: Literal["descriptive_only", "reference_dependent", "measurement_limited"]
    followups: list[Literal["inspect_reference", "inspect_personal_history", "check_assessment_availability"]] = Field(max_length=3)


class RunManifest(Contract):
    stage: Literal["stage1"] = "stage1"
    started_utc: str
    completed_utc: str | None = None
    code_commit: str
    code_sha256: str
    config_sha256: str
    dataset_sha256: str
    environment: dict[str, Any]
    resource_use: dict[str, Any]
    results: list[dict[str, Any]]
