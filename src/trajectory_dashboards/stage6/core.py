"""Stage-local configuration and outputs; unchanged descriptive calculations."""
from pathlib import Path
from ..common import read_json, file_hash, digest
from ..stage2.core import Question, Request, Registry, append_event
from ..stage2.backend import Engine as BaseEngine

ROOT = Path('artifacts/stage6')
CONDITIONS = ('baseline', 'compact_a', 'derived_b', 'binding_c')


class Engine(BaseEngine):
    def __init__(self):
        super().__init__(ROOT / 'source', Registry('configs/stage6.json'))


def event(value):
    append_event(value, ROOT / 'execution.jsonl')


def verify_freeze():
    frozen = read_json(ROOT / 'protocol/freeze.json')
    for p, sha in frozen['files'].items():
        if file_hash(p) != sha:
            raise ValueError('Frozen input changed: ' + p)
    return digest(frozen)
