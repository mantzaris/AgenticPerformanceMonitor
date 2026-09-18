"""Focused invariants, resource accounting, binding recompile and exact replay."""
import argparse,json,tempfile
from collections import Counter
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,file_hash,now
from trajectory_dashboards.stage6.core import ROOT,Engine
from trajectory_dashboards.stage6.adapter import replay
from trajectory_dashboards.stage6.binding import compile_selection
from trajectory_dashboards.stage4.semantic import compile_answer
from trajectory_dashboards.stage2.integrity import compare


def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');p.add_argument('--output',required=True);args=p.parse_args()
    if Path(args.output).exists():raise ValueError('Use a fresh verification output')
    history=read_json(ROOT/'checks/history_inventory.json')['files']
    assert all(file_hash(p)==h for p,h in history.items())
    frozen=read_json(ROOT/'protocol/freeze.json')['files'] if (ROOT/'protocol/freeze.json').exists() else {}
    assert all(file_hash(p)==h for p,h in frozen.items())
    m=read_json(ROOT/'tasks/manifest.json');prior=set(m['prior_focal_people_excluded']);new=set(m['new_focal_people'])
    assert len(prior)==57 and len(new)==24 and len(m['tasks'])==24 and not prior&new
    assert prior==set(read_json('artifacts/stage5/tasks/manifest.json')['reference_pool_excluded_people'])
    eng=Engine();reserved=set(read_json('artifacts/data/splits.json')['assignments']['reserved'])
    assert not set(eng.weekly.person_id)&reserved and eng.excluded==prior|new
    assert all(file_hash(ROOT/'source'/n)==file_hash(Path('artifacts/stage5/source')/n) for n in eng.meta['files'])
    assert Counter(t['question']['kind'] for t in m['tasks'])=={k:4 for k in eng.cfg['question_kinds']}
    for k in ['profiles','references','bootstrap_replicates','minimum_focal_weeks','minimum_peer_people','seed','decoding','episode','input_token_ceiling']:
        assert eng.cfg[k]==read_json('configs/stage5.json')[k]
    order=read_json(ROOT/'protocol/execution_order.json')['agent_order'];assert len(order)==72
    for c in eng.cfg['conditions']:
        assert len({e['question_id'] for e in order if e['condition']==c})==24
        assert Counter(e['within_case_position'] for e in order if e['condition']==c)=={1:8,2:8,3:8}
    # The frozen independent row-loop facts also agree with actual source-bound
    # baseline results when available, not just with a hash of themselves.
    facts_checked=0
    for rubric in read_json(ROOT/'evaluator_only/rubrics.json')['rubrics']:
        path=ROOT/'comparison/baseline'/rubric['question_id']/'tool_results.json'
        if path.exists():
            records=read_json(path)
            for signature,fact in rubric['independent_facts'].items():
                f,ref=signature.split(':');e=next(e for e in records.values() if e['feature']==f and e['reference']==ref and e['request']['window']=='recent')
                for k,v in fact.items():compare(e[k],v,'independent_facts.'+signature+'.'+k)
                facts_checked+=1
    replayed=[];recompiled=[]
    if args.replay:
        for path in sorted((ROOT/'comparison').glob('*/*/accepted/spec.json')):
            a=path.parent;proof=read_json(a/'selection_provenance.json');q=read_json(a/'question.json')
            condition=a.parent.parent.name
            if condition!='baseline':
                retrieved=read_json(a.parent/'tool_results.json')
                spec,p=(compile_answer(eng,q,proof['semantic_answer'],retrieved) if condition=='compact_a' else
                        compile_selection(eng,q,proof['original_selection'],retrieved,condition))
                assert spec.model_dump()==read_json(path) and p==proof
                assert all(pr['origin']=='method_selected' for c,pr in zip(spec.claims,proof['claims']) if c.template in {'comparison','personal_change'})
                recompiled.append(str(a))
            with tempfile.TemporaryDirectory(prefix='stage6-replay-') as tmp:
                replay(eng,a,Path(tmp)/'replay')
                for name in ['bound.json','chart.vl.json','dashboard.svg','selection_provenance.json']:
                    assert file_hash(a/name)==file_hash(Path(tmp)/'replay'/name),str(a)+' '+name
            replayed.append(str(a))
    events=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()]
    gens=[e for e in events if e['event']=='generation_started'];parts=Counter(e['budget_partition'] for e in gens)
    assert len(gens)<=320 and parts['comparison']<=288 and parts['setup']<=32
    assert len({g['generation'] for g in gens})==len(gens)
    ends=[e for e in events if e['event']=='process_finished'];seconds=sum(e['elapsed_seconds'] for e in ends);assert seconds<=7200
    assert {e['process_id'] for e in events if e['event']=='process_started'}=={e['process_id'] for e in ends}
    results=[read_json(p) for p in (ROOT/'comparison').glob('*/*/result.json')]
    assert all(r.get('generations',0)<=4 and r.get('tool_calls_attempted',0)<=6 and r.get('repairs',0)<=1 for r in results)
    if args.replay:
        assert len(results)==96
        for path in (ROOT/'gpu').glob('*/runtime.json'):
            rt=read_json(path);assert rt['parameter_devices']==['cuda:0'] and rt['parameter_dtypes']==['torch.bfloat16']
            assert rt['revision']=='cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8' and rt['cuda_execution_proof']['device_events']>0
        for path in (ROOT/'gpu/generations').glob('*.metadata.json'):
            meta=read_json(path)
            if meta['status']=='completed':assert meta['input_device']==meta['output_device']=='cuda:0' and meta['nvidia_smi_own_process']
            if meta['phase']=='action_1':
                msg=read_json(str(path).replace('.metadata.json','.input.json'));payload=json.loads(msg[1]['content'])
                assert set(payload)=={'question','windows','available_features','available_references','tool_window_choices','action_schema','public_interpretation_rules'}
    write_json(args.output,{'utc':now(),'status':'PASS','historical_files_unchanged':len(history),'frozen_files_unchanged':len(frozen),
        'new_people':24,'prior_focal_people_excluded':57,'reserved_identifiers_excluded':len(reserved),
        'comparison_results':len(results),'independent_facts_checked':facts_checked,'generation_partitions':dict(parts),
        'attempted_generations':len(gens),'model_process_seconds':seconds,'replay_count':len(replayed),'replayed':replayed,
        'agent_recompile_count':len(recompiled),'recompiled':recompiled,
        'checks':['immutable historical/frozen files','unchanged source and scientific settings','person-disjoint selection and fixed exclusions',
                  'balanced order','independent facts agree with saved backend results','exact binding/provenance reconstruction',
                  'no compiler-added comparison/change claims','exact bound/chart/SVG/provenance replay','actual CUDA evidence and cumulative ceilings']})
    print('PASS',args.output,'replayed',len(replayed))


if __name__=='__main__':main()
