from pathlib import Path
from typing import Literal
from pydantic import Field
from ..contracts import Contract
from ..stage2.core import Question, Request, Specification, Action as BaseAction, Registry, append_event
from ..stage2.backend import Engine as BaseEngine

ROOT = Path('artifacts/stage3')
METHODS = ('generic', 'reference_sensitive', 'coverage_aware')


class RequestState(Contract):
    request: str = Field(min_length=1, max_length=180)
    status: Literal['uninvestigated', 'evidence_available', 'answered', 'insufficient_evidence', 'unavailable_measurement']
    evidence_ids: list[str] = Field(default_factory=list, max_length=6)


class Action(BaseAction):
    # Available to all policies. These are model-authored public task states, not reasoning traces.
    request_map: list[RequestState] = Field(default_factory=list, max_length=8)
    stopping_status: Literal['continue', 'complete', 'budget_limited', 'unresolved'] = 'continue'


class Engine(BaseEngine):
    def __init__(self):
        super().__init__(ROOT / 'source', Registry('configs/stage3.json'))


def event(value):
    append_event(value, ROOT / 'execution.jsonl')
