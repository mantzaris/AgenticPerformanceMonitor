"""Reproduce known Stage 5 scores/traces offline; no inference or output changes."""
from trajectory_dashboards.common import read_json, write_json, file_hash, now
from trajectory_dashboards.stage5.core import Engine
from trajectory_dashboards.stage5.reporting import score_case
from trajectory_dashboards.stage6.core import ROOT, event


def main():
    target = ROOT/'diagnosis/stage5_reproduction.json'
    if target.exists():
        raise ValueError('Preserve the original diagnosis')
    engine = Engine()
    old = read_json('artifacts/stage5/reports/per_case.json')
    results = []
    keys = ['valid_after_repair', 'complete_requested_coverage', 'complete_method_selected_coverage',
            'missing_requested_analyses', 'retrieved_but_omitted', 'scoped_insufficiency_items',
            'compiler_supplied_answers', 'oracle_retrieved_upper_bound']
    for t in read_json('artifacts/stage5/tasks/manifest.json')['tasks']:
        q = t['question'];path = 'artifacts/stage5/comparison/qwen14b_semantic/'+q['question_id']
        scored = score_case(engine, q, path, 'qwen14b_semantic')
        original = next(r for r in old if r['condition']=='qwen14b_semantic' and r['question_id']==q['question_id'])
        assert all(scored[k] == original[k] for k in keys)
        results.append({k:scored[k] for k in ['question_id',*keys]})
    write_json(target, {'utc':now(),'status':'PASS','method':'Offline unchanged scorer plus original trace inspection; no model inference',
        'original_report_sha256':file_hash('artifacts/stage5/reports/per_case.json'), 'cases':results,
        'visible_complete':sum(r['complete_requested_coverage'] for r in results),
        'method_selected_complete':sum(r['complete_method_selected_coverage'] for r in results),
        'retrieved_upper_bound':sum(r['oracle_retrieved_upper_bound'] for r in results),
        'diagnosis':{'s5_06':'peer selections with unselected personal conclusion scope; repair keeps mismatch',
                     's5_07':'recent course record retrieved; baseline course and earlier-stage peer answers selected instead',
                     's5_08':'recent course evidence selected as personal change only; peer answers use baseline windows'},
        'use':'Known construction material, not new confirmation evidence'})
    event({'event':'stage5_diagnosis_reproduced','visible_complete':9,'method_selected_complete':8,'retrieved_upper_bound':12})
    print('PASS: Stage 5 14B compact 9 visible, 8 selected, 12 retrieved')


if __name__=='__main__':main()
