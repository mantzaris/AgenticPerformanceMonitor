"""Stage-local source and configuration; unchanged descriptive backend."""
from pathlib import Path
from ..stage2.core import Question, Request, Specification, Action as FullAction, Registry, append_event
from ..stage2.backend import Engine as BaseEngine

ROOT = Path('artifacts/stage4')
METHODS = ('full_spec', 'semantic')


class Engine(BaseEngine):
    def __init__(self):
        super().__init__(ROOT / 'source', Registry('configs/stage4.json'))


def event(value):
    append_event(value, ROOT / 'execution.jsonl')
