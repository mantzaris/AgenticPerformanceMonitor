"""Stage-local data/configuration, with the historical analytical implementation."""
from pathlib import Path
from ..common import read_json, file_hash, digest
from ..stage2.core import Question, Request, Specification, Registry, append_event
from ..stage2.backend import Engine as BaseEngine

ROOT = Path('artifacts/stage5')
CONDITIONS = ('baseline', 'qwen7b_full_spec', 'qwen7b_semantic', 'qwen14b_full_spec', 'qwen14b_semantic')


class Engine(BaseEngine):
    def __init__(self):
        super().__init__(ROOT / 'source', Registry('configs/stage5.json'))


def event(value):
    append_event(value, ROOT / 'execution.jsonl')


def verify_freeze():
    frozen = read_json(ROOT / 'protocol/freeze.json')
    for path, sha in frozen['files'].items():
        if file_hash(path) != sha:
            raise ValueError('Frozen input changed: ' + path)
    return digest(frozen)
