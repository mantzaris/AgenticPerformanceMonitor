"""Offline, oracle-assisted diagnosis. Never imported by the deployed methods."""
import json
from collections import Counter
from pathlib import Path
from trajectory_dashboards.common import read_json, write_json, file_hash, now
from trajectory_dashboards.stage3.evaluation import evaluate, requirements, _retrieved
from trajectory_dashboards.stage3.core import Engine
from trajectory_dashboards.stage2.integrity import validate_evidence, reference_conclusion


def error_tags(error):
    tags = []
    if any(s in error for s in ['specification.panels', 'Selected evidence coverage', 'specification.claims']):
        tags.append('structural_specification')
    if any(s in error for s in ['specification.conclusion', 'Unsupported semantic', 'Unknown evidence', 'unknown s2_', 'content hash', 'trusted source']):
        tags.append('substantive_or_unsupported')
    if 'JSONDecodeError' in error:
        tags.append('invalid_json')
    if any(s in error for s in ['extra_forbidden', 'extra inputs', 'Extra inputs', 'request_map', 'stopping_status']):
        tags.append('field_or_schema_error')
    if any(s in error for s in ['requires 1', 'final requires', 'analyze requires']):
        tags.append('conflicting_action_fields')
    if 'at most' in error or 'too_long' in error:
        tags.append('excessive_items')
    return tags


def main():
    out = Path('artifacts/stage4/diagnostics')
    if (out/'stage3_cases.json').exists():
        raise ValueError('Preserve original diagnosis')
    tasks = {t['question']['question_id']: t['question'] for t in read_json('artifacts/stage3/tasks/manifest.json')['tasks']}
    scores = read_json('artifacts/stage3/reports/per_question.json')
    engine = Engine()
    cases = []
    for score in scores:
        method, qid = score['method'], score['question_id']
        path = Path('artifacts/stage3/pilot')/method/qid
        q = tasks[qid]
        retrieved = read_json(path/'tool_results.json')
        for e in retrieved.values():
            validate_evidence(engine, __import__('trajectory_dashboards.stage2.core', fromlist=['Question']).Question.model_validate(q), e)
        available = [{**item, 'evidence_available': _retrieved(item, retrieved)} for item in requirements(q)]
        steps = read_json(path/'sequence.json') if (path/'sequence.json').exists() else []
        traces = []; intended = []
        for step in steps:
            error = step.get('validation_error', '')
            raw = step['raw_output']; metrics = step['generation_metadata']
            try:
                parsed = json.loads(raw); parse_error = None
            except json.JSONDecodeError as exc:
                parsed = None; parse_error = {'message': exc.msg, 'position': exc.pos, 'characters_after_error': len(raw)-exc.pos}
            spec = parsed.get('specification') if isinstance(parsed, dict) else None
            substantive = []
            if isinstance(spec, dict):
                selected = {k: v for k, v in retrieved.items() if k in spec.get('evidence_ids', [])}
                unknown = set(spec.get('evidence_ids', []))-set(retrieved)
                if unknown: substantive.append('unknown evidence identifiers')
                projection = {**spec, 'evidence_ids': list(selected),
                    'claims': [c for c in spec.get('claims', []) if isinstance(c,dict) and c.get('evidence_id') in selected and c.get('template') in {'comparison','personal_change','measurement_limits'}],
                    'panels': [p for p in spec.get('panels', []) if isinstance(p,dict) and p.get('evidence_id') in selected and p.get('kind') in {'trajectory','comparison','observation_status','assessment_status'}]}
                conclusion = spec.get('conclusion')
                if conclusion in {'same_direction','direction_differs'}:
                    expected = reference_conclusion([__import__('trajectory_dashboards.stage2.core',fromlist=['Evidence']).Evidence.model_validate(e) for e in selected.values()])
                    if conclusion != expected:
                        substantive.append('unsupported reference conclusion');projection['conclusion']='descriptive'
                elif conclusion=='insufficient_evidence' and not any(e['status']!='supported' or e['summary']['personal_status']!='supported' for e in selected.values()):
                    substantive.append('unsupported insufficiency');projection['conclusion']='descriptive'
                elif conclusion not in {'descriptive','insufficient_evidence'}:
                    substantive.append('unsupported conclusion vocabulary');projection['conclusion']='descriptive'
                judged = evaluate(q, projection, selected, retrieved, valid=bool(selected))
                intended.append({'turn':step['turn'],'complete_ignoring_layout':judged['complete_requested_coverage'] and not substantive,
                                 'covered_items_ignoring_layout':[a['id'] for a in judged['requested_answers'] if a['covered']],
                                 'not_selected_items':[a['id'] for a in judged['requested_answers'] if not a['covered'] and a['relevant_evidence_retrieved']],
                                 'substantive_problems':substantive})
            traces.append({'turn':step['turn'],'validation_error':error,'tags':error_tags(error),
                           'parseable_json':parsed is not None,'parse_error':parse_error,
                           'completion_tokens':metrics.get('completion_tokens'),
                           'output_token_ceiling':1500,'hit_output_ceiling':metrics.get('completion_tokens')==1500,
                           'finish_reason':'not recorded in Stage 3; no EOS-based inference',
                           'substantive_problems':substantive})
        terminal_valid=score['valid_after_permitted_repair']
        labels=[]
        if not all(a['evidence_available'] for a in available):labels.append('necessary_evidence_not_requested')
        if any(i['not_selected_items'] for i in intended):labels.append('retrieved_but_not_selected_in_attempted_answer')
        if not terminal_valid and any('structural_specification' in t['tags'] for t in traces) and intended:labels.append('intended_answer_rejected_by_structure')
        if any(t['substantive_problems'] or 'substantive_or_unsupported' in t['tags'] for t in traces):labels.append('substantive_or_unsupported_error')
        if score['claimed_complete_but_incomplete']:labels.append('incorrect_claim_of_completion')
        if score.get('redundant_requests',0):labels.append('redundant_analytical_requests')
        cases.append({'method':method,'question_id':qid,'case_id':score['case_id'],'family':score['family'],
            'original_valid':terminal_valid,'original_complete':score['complete_requested_coverage'],
            'original_score_path':'artifacts/stage3/reports/per_question.json','trace_path':str(path/'sequence.json') if steps else None,
            'labels_nonexclusive':labels,'oracle_evidence_available_items':available,
            'oracle_evidence_availability_upper_bound':bool(retrieved) and all(a['evidence_available'] for a in available),
            'oracle_note':'Offline evaluator-assisted evidence sufficiency for admissible answers, including scoped insufficiency/unavailability. Ignores selection/layout errors. NOT agent success or a deployable selector.',
            'intended_answer_projections':intended,'traces':traces,
            'terminal_rejected_complete_intention':not terminal_valid and any(i['complete_ignoring_layout'] for i in intended),
            'redundant_exact_requests':score.get('redundant_requests',0),'redundant_equivalent_analyses':score['redundant_equivalent_analyses']})
    summaries=[]
    for method in ['baseline','generic','reference_sensitive','coverage_aware']:
        rows=[r for r in cases if r['method']==method]
        summaries.append({'method':method,'questions':len(rows),'accepted_complete':sum(r['original_complete'] for r in rows),
            'oracle_upper_bound':sum(r['oracle_evidence_availability_upper_bound'] for r in rows),
            'failed':sum(not r['original_valid'] for r in rows),'labels':dict(Counter(label for r in rows for label in r['labels_nonexclusive'])),
            'rejected_complete_intentions':sum(r['terminal_rejected_complete_intention'] for r in rows),
            'output_ceiling_hits':sum(t['hit_output_ceiling'] for r in rows for t in r['traces'])})
    assert [s['accepted_complete'] for s in summaries]==[24,11,11,6]
    write_json(out/'stage3_cases.json',{'created_utc':now(),'source_scores_sha256':file_hash('artifacts/stage3/reports/per_question.json'),'cases':cases})
    write_json(out/'stage3_summary.json',{'created_utc':now(),'summaries':summaries,'source_bound_retrieved_evidence_verified':True,
        'interpretation':'Multiple mechanisms coexist. Structural rejection is observed, but interface causation is a hypothesis. Oracle-assisted upper bounds cannot be counted as agent successes.',
        'truncation':'No output hit 1500 tokens. Stage 3 did not record EOS/finish reasons; malformed JSON is not labeled truncation merely from its length.',
        'instructions':'No logically contradictory panel obligations identified: six comparison panels plus shared trajectory, observation and assessment need at most nine of ten panels. Instruction complexity remains a hypothesis, not an observed cause.'})
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':main()
