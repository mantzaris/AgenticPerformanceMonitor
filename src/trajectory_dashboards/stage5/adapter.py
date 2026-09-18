"""Reuse the exact Stage 4 episode code; bind only logging and display destinations.

FunctionType preserves the original code object and its scientific/prompt globals.
The isolated globals dictionary avoids mutating any historical module or writing
its ledger. Checkpoint identity never enters the public question or policy.
"""
from pathlib import Path
from types import FunctionType
from ..common import read_json
from ..stage4.agents import episode as historical_episode
from ..stage4.display import render as historical_render
from ..stage4.evaluation import evaluate  # Exactly the same scoring function.
from .core import event


def render(*args, **kwargs):
    binding = historical_render(*args, **kwargs)
    out = Path(kwargs.get('output', args[4] if len(args) > 4 else ''))
    path = out / 'dashboard.html'
    path.write_text(path.read_text().replace('STAGE 4', 'STAGE 5').replace('Stage 4', 'Stage 5'))
    return binding


def episode(engine, question, interface, generate, case, model_key):
    def stage_event(value):
        event({**value, 'model_key': model_key, 'condition': model_key + '_' + interface})
    isolated = {**historical_episode.__globals__, 'event': stage_event, 'render': render}
    run = FunctionType(historical_episode.__code__, isolated, historical_episode.__name__,
                       historical_episode.__defaults__, historical_episode.__closure__)
    return run(engine, question, interface, generate, case)


def replay(engine, source, output):
    source = Path(source)
    return render(engine, read_json(source / 'question.json'), read_json(source / 'spec.json'),
                  read_json(source / 'evidence.json'), output,
                  origin=read_json(source / 'bound.json')['selection_origin'],
                  provenance=read_json(source / 'selection_provenance.json'))
