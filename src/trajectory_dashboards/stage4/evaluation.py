"""Unchanged Stage 3 visible-answer semantics with explicit compiler attribution."""
from ..stage3.evaluation import evaluate as historical_evaluate


def evaluate(question, spec, selected, retrieved, provenance, valid=True):
    result = historical_evaluate(question, spec, selected, retrieved, valid=valid)
    if not valid:
        return result
    # Same visible scoring rules; this projection only identifies who selected
    # content. Compiler-only panels/boilerplate are not agent investigation.
    projected = {**spec,
                 'claims': [c for c,p in zip(spec['claims'],provenance['claims']) if p['origin']=='method_selected'],
                 'panels': [c for c,p in zip(spec['panels'],provenance['panels']) if p['origin']=='method_selected']}
    chosen = historical_evaluate(question, projected, selected, retrieved, valid=True, compiler_context=False)
    selected_answers = {a['id']: a for a in chosen['requested_answers']}
    for a in result['requested_answers']:
        if a['covered']:
            a['origin'] = 'method_selected' if selected_answers[a['id']]['covered'] else 'compiler_supplied'
    result['compiler_supplied_answers'] = [a['id'] for a in result['requested_answers'] if a['origin']=='compiler_supplied']
    result['complete_method_selected_coverage'] = all(a['covered'] and a['origin']=='method_selected' for a in result['requested_answers'])
    result['method_selected_fraction'] = sum(a['covered'] and a['origin']=='method_selected' for a in result['requested_answers'])/len(result['requested_answers'])
    result['attribution_note'] = 'Stage 3 answer judgments unchanged; compiler-only context separately attributed through an explicit selection projection.'
    return result
