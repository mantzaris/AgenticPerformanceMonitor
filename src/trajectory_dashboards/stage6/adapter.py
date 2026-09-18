"""Exact historical episode loop, with isolated interface-specific bindings."""
from pathlib import Path
from types import FunctionType
from ..common import read_json
from ..stage4.agents import episode as historical_episode
from ..stage4.display import render as historical_render
from ..stage4.evaluation import evaluate
from ..stage2.backend import compact as historical_compact
from .binding import DerivedAction, BindingAction, compile_selection, catalogue
from .core import event


def render(*args, **kwargs):
    result = historical_render(*args, **kwargs)
    out = Path(kwargs.get('output', args[4] if len(args) > 4 else ''))
    p = out / 'dashboard.html'
    p.write_text(p.read_text().replace('STAGE 4', 'STAGE 6').replace('Stage 4', 'Stage 6'))
    return result


def episode(engine, question, condition, generate, case):
    def record(value):
        event({**value, 'condition': condition})
    def generator(messages, qid, method, phase, destination):
        return generate(messages, qid, condition, phase, destination)
    isolated = {**historical_episode.__globals__, 'event': record, 'render': render}
    if condition != 'compact_a':
        def prompts(path):
            value = read_json(path)
            if str(path) == 'configs/stage4_prompts.json':
                value = {**value, 'semantic': read_json('configs/stage6_prompts.json')[condition]}
            return value
        def compact(e):
            return {**historical_compact(e), 'available_answers': catalogue(question, e)}
        isolated.update(read_json=prompts, compact=compact,
                        SemanticAction=DerivedAction if condition == 'derived_b' else BindingAction,
                        compile_answer=lambda eng, q, a, es: compile_selection(eng, q, a, es, condition))
    run = FunctionType(historical_episode.__code__, isolated, historical_episode.__name__,
                       historical_episode.__defaults__, historical_episode.__closure__)
    result = run(engine, question, 'semantic', generator, case)
    return result


def replay(engine, source, output):
    source = Path(source)
    return render(engine, read_json(source/'question.json'), read_json(source/'spec.json'),
                  read_json(source/'evidence.json'), output, origin=read_json(source/'bound.json')['selection_origin'],
                  provenance=read_json(source/'selection_provenance.json'))
