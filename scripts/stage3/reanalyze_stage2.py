"""Post-hoc semantic reanalysis; read historical outputs, never rerun agents."""
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,now,file_hash
from trajectory_dashboards.stage2.backend import Engine
from trajectory_dashboards.stage2.integrity import validate
from trajectory_dashboards.dashboard import claim_text
from trajectory_dashboards.stage3.core import ROOT,event
from trajectory_dashboards.stage3.evaluation import score_case


def main():
    out=ROOT/'stage2_reanalysis';out.mkdir(parents=True,exist_ok=True)
    if (out/'per_question.json').exists():raise ValueError('Reanalysis already exists; preserve version')
    engine=Engine(); originals=read_json('artifacts/stage2/reports/pilot_per_task.json')
    old={(r['method'],r['task_id']):r for r in originals}
    rows=[]
    for t in read_json('artifacts/stage2/tasks/manifest.json')['tasks']:
        if t['subset']!='pilot':continue
        q=t['question']
        for method in ['baseline','generic','reference_sensitive']:
            case=Path('artifacts/stage2/pilot')/method/q['question_id']
            accepted=case/'accepted'
            if accepted.exists():
                s,e=validate(engine,q,read_json(accepted/'spec.json'),read_json(accepted/'evidence.json'))
                b=read_json(accepted/'bound.json')
                assert [c['text'] for c in b['claims']]==[claim_text(c,e[c.evidence_id]) for c in s.claims]
            new=score_case(q,case,historical=True); original=old[method,q['question_id']]
            changes=[]
            if q['kind']=='reference_sensitivity':changes.append('Rubric defect: personal history was not requested; replace required retrieval/templates with the requested three-reference direction answer.')
            if q['kind']!='assessment_availability':changes.append('Underspecified historical activity feature: permit coherent supported activity features, rather than a hidden click-rate-only requirement.')
            if q['kind']=='observation_limits':changes.append('Rubric overrequirement: broad assessment-record wording does not uniquely mandate both numerical assessment features; visible dated assessment states can answer it.')
            if new['global_supported_insufficiency']:changes.append('Scorer defect repaired: the supported insufficient_evidence conclusion is credited as a global finding. Multiple unsupported scopes still require attribution for individual requested answers.')
            if new['retrieved_but_omitted']:changes.append('Genuine display omission under revised semantics: '+', '.join(new['retrieved_but_omitted']))
            if new['missing_requested_analyses']:changes.append('Genuine missing requested analysis under revised semantics: '+', '.join(new['missing_requested_analyses']))
            if new['compiler_supplied_answers']:changes.append('Visible standard caveat answers measurement unavailability; credit is compiler-supplied, not method-selected.')
            if not new['valid_after_permitted_repair']:changes.append('Historical failure preserved; no accepted dashboard, zero complete requested coverage.')
            rows.append({**new,'method':method,'question_text':q['text'],'original_score':original,'change_explanations':changes,
                         'endpoint_changed':original['all_task_context_covered']!=new['complete_requested_coverage'],
                         'score_fraction_changed':original['coverage_fraction']!=new['answer_fraction']})
    summary=[]
    for m in ['baseline','generic','reference_sensitive']:
        rr=[r for r in rows if r['method']==m]
        summary.append({'method':m,'denominator':12,'original_full_context':sum(r['original_score']['all_task_context_covered'] for r in rr),
                        'revised_complete_requested':sum(r['complete_requested_coverage'] for r in rr),
                        'revised_complete_method_selected':sum(r['complete_method_selected_coverage'] for r in rr),
                        'supported_global_insufficiency':sum(r['global_supported_insufficiency'] for r in rr),
                        'original_appropriate_insufficiency':sum(bool(r['original_score']['appropriate_insufficiency']) for r in rr)})
    write_json(out/'per_question.json',rows)
    write_json(out/'summary.json',{'label':'POST-HOC Stage 2 reanalysis; not replacement primary scores','created_utc':now(),'historical_scores_sha256':file_hash('artifacts/stage2/reports/pilot_per_task.json'),'agent_reruns':0,'summary':summary,'external_review':'Outstanding; automated audit is not human review'})
    lines=['# Stage 2 post-hoc reanalysis under Stage 3 semantics','',
           'Original outputs and primary scores are unchanged. No inference was rerun. New answer denominators differ from the old context checklist; these are not interchangeable metrics. Every revised item and change explanation is in per_question.json. External scientific review is outstanding.','',
           '| Method | Original full context | Revised complete requested | Revised method-selected complete |','|---|---:|---:|---:|']
    lines.extend(f"| {r['method']} | {r['original_full_context']}/12 | {r['revised_complete_requested']}/12 | {r['revised_complete_method_selected']}/12 |" for r in summary)
    for r in rows:
        lines.extend(['',f"## {r['method']} / {r['question_id']}",f"Old coverage {r['original_score']['coverage_fraction']:.3f}; revised requested answers {r['answer_fraction']:.3f}. Old full-context={r['original_score']['all_task_context_covered']}; new complete-answer={r['complete_requested_coverage']}.",*['- '+s for s in r['change_explanations']]])
    (out/'REANALYSIS.md').write_text('\n'.join(lines)+'\n')
    event({'event':'stage2_posthoc_reanalysis_completed','cases':36,'model_calls':0})
    print(summary)

if __name__=='__main__':main()
