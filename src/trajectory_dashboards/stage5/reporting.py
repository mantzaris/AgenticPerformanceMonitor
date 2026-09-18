"""Condition-neutral scoring and explicit error accounting; no model/policy imports."""
import json
from pathlib import Path
from ..common import read_json, digest
from ..stage2.integrity import validate
from ..stage3.evaluation import requirements, _retrieved
from ..stage4.evaluation import evaluate
from ..stage4.semantic import compile_answer


def error_categories(error):
    low = error.lower()
    tests = {
        'identifier': ['unknown evidence', 'unresolved evidence', 'not returned'],
        'json_or_schema': ['jsondecodeerror', 'validationerror', 'literal_error', 'extra_forbidden'],
        'support': ['.support:', 'insufficient support belongs', 'unsupported insufficiency'],
        'scope': ['conclusion scope', 'requires scope=', 'peer/personal scope'],
        'layout_or_claim_contract': ['specification.panels', 'specification.claims', 'panel contract'],
        'unsupported_conclusion': ['unsupported semantic reference conclusion', 'unsupported conclusion'],
        'source_numerical_integrity': ['disagrees with trusted source', 'content hash mismatch'],
        'infrastructure_or_resource': ['out of memory', 'cuda error', 'time budget', 'deadline', 'context ceiling'],
    }
    return [name for name, terms in tests.items() if any(t in low for t in terms)]


def unsupported_attempts(sequence, retrieved):
    """Check explicit semantic support declarations even if another error came first.

    Full-interface templates automatically withhold unsupported numeric estimates;
    malformed panel structure is not itself an unsupported quantitative assertion.
    """
    findings = []
    for step in sequence:
        try:
            action = json.loads(step['raw_output'])
        except (ValueError, KeyError):
            continue
        if not isinstance(action, dict) or action.get('action') != 'final':
            continue
        for i, intent in enumerate(action.get('answers', [])):
            if not isinstance(intent, dict) or intent.get('evidence_id') not in retrieved:
                continue
            evidence = retrieved[intent['evidence_id']]
            kind = intent.get('kind')
            status = evidence['status'] if kind == 'peer_comparison' else evidence['summary']['personal_status']
            if kind in {'peer_comparison', 'personal_change'} and intent.get('support', 'describe') == 'describe' and status != 'supported':
                findings.append({'turn': step['turn'], 'answer_index': i, 'kind': kind,
                                 'evidence_id': intent['evidence_id'], 'feature': evidence['feature'],
                                 'window': evidence['window'], 'reference': evidence['reference'],
                                 'accepted': step.get('stopping_decision') == 'valid final specification'})
    return findings


def score_case(engine, question, case, condition, metrics=(), blocked_reason=None):
    """Model label affects reporting identity only, never the imported evaluator."""
    case = Path(case)
    model_key, interface = (None, 'baseline') if condition == 'baseline' else condition.split('_', 1)
    attempted = (case / 'started.json').exists()
    result = read_json(case / 'result.json') if (case / 'result.json').exists() else {
        'status': 'not_attempted_infrastructure_blocked' if blocked_reason else 'not_attempted',
        'first_attempt_valid': False, 'error': blocked_reason}
    valid = result['status'] in {'deterministic_accepted', 'agent_generated_and_accepted', 'agent_generated_and_repaired'}
    retrieved = read_json(case / 'tool_results.json') if (case / 'tool_results.json').exists() else {}
    spec, selected, provenance = {}, {}, {}
    if valid:
        accepted = case / 'accepted'
        spec = read_json(accepted / 'spec.json')
        selected = read_json(accepted / 'evidence.json')
        provenance = read_json(accepted / 'selection_provenance.json')
        validate(engine, question, spec, selected)
        if interface == 'semantic':
            rebuilt, proof = compile_answer(engine, question, provenance['semantic_answer'], retrieved)
            assert digest(rebuilt.model_dump()) == digest(spec) and proof == provenance
            assert all(p['origin'] == 'method_selected' for c, p in zip(spec['claims'], proof['claims'])
                       if c['template'] in {'comparison', 'personal_change'})
    scored = evaluate(question, spec, selected, retrieved, provenance, valid)
    sequence = read_json(case / 'sequence.json') if (case / 'sequence.json').exists() else []
    errors = [{'turn': s['turn'], 'error': s['validation_error'], 'categories': error_categories(s['validation_error'])}
              for s in sequence if 'validation_error' in s]
    unsupported = unsupported_attempts(sequence, retrieved)
    assert not any(x['accepted'] for x in unsupported)
    requests = read_json(case / 'requests.json') if (case / 'requests.json').exists() else [t['request'] for s in sequence for t in s.get('tool_results', [])]
    signatures = []
    profile = engine.registry.profile(question)
    for request in requests:
        rule = engine.cfg['references'][request['reference']]
        window = profile[request.get('window', 'recent')]
        rw = profile['baseline'] if rule['time'] == 'baseline' else window
        signatures.append((request['feature'], rule['group'], tuple(window), tuple(rw)))
    mm = [m for m in metrics if m['budget_partition'] == 'comparison' and m['question_id'] == question['question_id']
          and m['model_key'] == model_key and m['method'] == interface]
    return {**result, **scored, 'condition': condition, 'model_key': model_key, 'interface': interface,
            'question_id': question['question_id'], 'family': question['kind'], 'attempted': attempted,
            'blocked_reason': blocked_reason if not attempted else None, 'valid_after_repair': valid,
            'numerical_integrity': 'PASS' if valid else 'NO ACCEPTED OUTPUT',
            'unsupported_accepted_quantitative_answers': 0 if valid else None,
            'unsupported_quantitative_selection_attempts_rejected': unsupported,
            'errors': errors, 'error_categories': sorted({t for e in errors for t in e['categories']}),
            'oracle_retrieved_upper_bound': bool(retrieved) and all(_retrieved(i, retrieved) for i in requirements(question)),
            'redundant_equivalent_analyses': len(signatures) - len(set(signatures)),
            'generations': len(mm), 'prompt_tokens': sum(m.get('prompt_tokens', 0) for m in mm),
            'completion_tokens': sum(m.get('completion_tokens', 0) for m in mm),
            'generation_seconds': sum(m['elapsed_seconds'] for m in mm),
            'cuda_event_seconds': sum(m.get('cuda_event_ms', 0) / 1000 for m in mm),
            'peak_allocated_bytes': max((m.get('peak_allocated_bytes', 0) for m in mm), default=0),
            'peak_reserved_bytes': max((m.get('peak_reserved_bytes', 0) for m in mm), default=0),
            'finish_reasons': [m.get('finish_reason', 'failed') for m in mm],
            'compiler_added_panels': sum(p['origin'] == 'compiler_supplied' for p in provenance.get('panels', [])),
            'compiler_added_claims': sum(p['origin'] == 'compiler_supplied' for p in provenance.get('claims', [])),
            'compiler_inserted_quantitative_claims': provenance.get('inserted_comparison_or_personal_claims', 0),
            'artifact_path': str(case)}


def paired_outcome(left, right):
    if left and right:
        return 'both_complete'
    if right:
        return 'right_only_complete'
    if left:
        return 'left_only_complete'
    return 'both_incomplete'
