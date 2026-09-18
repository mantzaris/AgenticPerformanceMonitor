"""Frozen checkpoint/interface comparisons, with every case retained."""
import csv
import json
from collections import Counter
from trajectory_dashboards.common import read_json, write_json, now
from trajectory_dashboards.stage5.core import ROOT, Engine, CONDITIONS, verify_freeze
from trajectory_dashboards.stage5.reporting import score_case, paired_outcome


def main():
    verify_freeze()
    out = ROOT / 'reports'
    if (out / 'per_case.json').exists():
        raise ValueError('Preserve original scores; use a fresh reproduction workspace')
    cfg = read_json('configs/stage5.json')
    engine, rows = Engine(), []
    metrics = [read_json(p) for p in (ROOT / 'gpu/generations').glob('*.metadata.json')]
    runtimes = [read_json(p) for p in (ROOT / 'gpu').glob('*/runtime.json')]
    tasks = read_json(ROOT / 'tasks/manifest.json')['tasks']
    for task in tasks:
        q = task['question']
        for condition in CONDITIONS:
            model = None if condition == 'baseline' else condition.split('_', 1)[0]
            failures = [r for r in runtimes if r['model_key'] == model and r['status'] == 'failed']
            reason = failures[-1].get('error') if failures else None
            rows.append(score_case(engine, q, ROOT / 'comparison' / condition / q['question_id'], condition, metrics, reason))
    summaries = []
    for condition in CONDITIONS:
        rr = [r for r in rows if r['condition'] == condition]
        item = {'condition': condition, 'denominator': 12, 'attempted': sum(r['attempted'] for r in rr),
                'first_final_valid': sum(r.get('first_attempt_valid', False) for r in rr),
                'valid_after_repair': sum(r['valid_after_repair'] for r in rr),
                'complete_visible': sum(r['complete_requested_coverage'] for r in rr),
                'complete_method_selected': sum(r['complete_method_selected_coverage'] for r in rr),
                'missing_analysis_items': sum(len(r['missing_requested_analyses']) for r in rr),
                'retrieved_but_omitted_items': sum(len(r['retrieved_but_omitted']) for r in rr),
                'accepted_dashboard_omissions': sum(len(r['retrieved_but_omitted']) for r in rr if r['valid_after_repair']),
                'oracle_retrieved_upper_bound': sum(r['oracle_retrieved_upper_bound'] for r in rr),
                'scoped_insufficient_items': sum(len(r['scoped_insufficiency_items']) for r in rr),
                'unsupported_quantitative_attempts_rejected': sum(len(r['unsupported_quantitative_selection_attempts_rejected']) for r in rr),
                'unsupported_accepted_quantitative_answers': sum(r['unsupported_accepted_quantitative_answers'] or 0 for r in rr),
                'error_episode_counts': dict(Counter(t for r in rr for t in r['error_categories'])),
                'tool_calls': sum(r.get('tool_calls_attempted', 0) for r in rr),
                'duplicate_exact_calls': sum(r.get('redundant_requests', 0) for r in rr),
                'duplicate_equivalent_calls': sum(r['redundant_equivalent_analyses'] for r in rr),
                'generations': sum(r['generations'] for r in rr), 'repairs': sum(r.get('repairs', 0) for r in rr),
                'prompt_tokens': sum(r['prompt_tokens'] for r in rr), 'completion_tokens': sum(r['completion_tokens'] for r in rr),
                'episode_seconds': sum(r.get('elapsed_seconds', 0) for r in rr),
                'generation_seconds': sum(r['generation_seconds'] for r in rr),
                'cuda_event_seconds': sum(r['cuda_event_seconds'] for r in rr),
                'peak_allocated_bytes': max(r['peak_allocated_bytes'] for r in rr),
                'peak_reserved_bytes': max(r['peak_reserved_bytes'] for r in rr),
                'compiler_added_panels': sum(r['compiler_added_panels'] for r in rr),
                'compiler_supplied_answer_items': sum(len(r['compiler_supplied_answers']) for r in rr),
                'fallbacks': sum(r.get('fallback', False) for r in rr),
                'failed_questions': [r['question_id'] for r in rr if r['attempted'] and not r['valid_after_repair']],
                'not_attempted_questions': [r['question_id'] for r in rr if not r['attempted']]}
        item['engineering_gate_met'] = item['complete_visible'] >= 11 and item['unsupported_accepted_quantitative_answers'] == 0
        summaries.append(item)
    comparisons = [('primary_checkpoint_compact', 'qwen7b_semantic', 'qwen14b_semantic'),
                   ('secondary_checkpoint_full', 'qwen7b_full_spec', 'qwen14b_full_spec'),
                   ('interface_7b', 'qwen7b_full_spec', 'qwen7b_semantic'),
                   ('interface_14b', 'qwen14b_full_spec', 'qwen14b_semantic')]
    pairs, paired = [], []
    for label, left, right in comparisons:
        group = []
        for task in tasks:
            qid = task['question']['question_id']
            a = next(r for r in rows if r['question_id'] == qid and r['condition'] == left)
            b = next(r for r in rows if r['question_id'] == qid and r['condition'] == right)
            group.append({'comparison': label, 'left': left, 'right': right, 'question_id': qid,
                          'family': a['family'], 'both_attempted': a['attempted'] and b['attempted'],
                          'outcome': paired_outcome(a['complete_requested_coverage'], b['complete_requested_coverage']),
                          'selected_outcome': paired_outcome(a['complete_method_selected_coverage'], b['complete_method_selected_coverage']),
                          'left_complete': a['complete_requested_coverage'], 'right_complete': b['complete_requested_coverage'],
                          'right_minus_left_seconds': b.get('elapsed_seconds', 0) - a.get('elapsed_seconds', 0)})
        pairs.extend(group)
        paired.append({'comparison': label, 'left': left, 'right': right, 'denominator': 12,
                       'outcomes': dict(Counter(p['outcome'] for p in group)),
                       'selected_outcomes': dict(Counter(p['selected_outcome'] for p in group)),
                       'net_complete_gain': sum(p['right_complete'] - p['left_complete'] for p in group),
                       'infrastructure_note': 'Unattempted cases are identified separately; not a reasoning failure.'})
    events = [json.loads(s) for s in (ROOT / 'model_ledger.jsonl').read_text().splitlines()]
    ends = [e for e in events if e['event'] == 'process_finished']
    partitions = dict(Counter(e['budget_partition'] for e in events if e['event'] == 'generation_started'))
    large = next(s for s in summaries if s['condition'] == 'qwen14b_semantic')
    primary = paired[0]
    decision = ('infrastructure limitation; no checkpoint reasoning conclusion' if large['attempted'] < 12 else
                'review broader validation of fixed 14B compact condition' if large['engineering_gate_met'] else
                'substantial gain but gate missed; review remaining mechanism before a bounded intervention' if primary['net_complete_gain'] >= cfg['substantial_improvement_minimum_net_cases'] else
                'end further prompt-policy refinement for this task class; retain deterministic enumeration')
    report = {'created_utc': now(), 'summaries': summaries, 'paired_comparisons': paired,
              'primary_decision_rule_result': decision,
              'generation_partitions': partitions, 'total_generations': sum(partitions.values()),
              'model_process_seconds': sum(e['elapsed_seconds'] for e in ends), 'model_processes': ends,
              'unclosed_processes': sorted({e['process_id'] for e in events if e['event'] == 'process_started'} - {e['process_id'] for e in ends}),
              'interpretation': 'Twelve paired development cases, two fixed checkpoints, known families; descriptive comparison, not a pure model-size effect or general agent-capability claim.'}
    write_json(out / 'per_case.json', rows)
    write_json(out / 'paired_cases.json', pairs)
    write_json(out / 'comparison.json', report)
    columns = ['condition', 'question_id', 'family', 'status', 'attempted', 'first_attempt_valid', 'valid_after_repair',
               'complete_requested_coverage', 'complete_method_selected_coverage', 'tool_calls_attempted', 'generations',
               'repairs', 'prompt_tokens', 'completion_tokens', 'peak_allocated_bytes', 'elapsed_seconds']
    with (out / 'per_case.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
