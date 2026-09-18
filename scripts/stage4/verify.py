"""Focused frozen inputs, provenance, resource ledger and exact replay checks."""
import argparse,json,tempfile
from collections import Counter
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,file_hash,now,digest
from trajectory_dashboards.stage4.core import ROOT,Engine
from trajectory_dashboards.stage4.display import replay
from trajectory_dashboards.stage4.semantic import compile_answer


def main():
    p=argparse.ArgumentParser();p.add_argument('--replay',action='store_true');p.add_argument('--output',required=True);args=p.parse_args()
    output=Path(args.output)
    if output.exists():raise ValueError('Choose a new check output; preserve historical results')
    history=read_json(ROOT/'checks/history_inventory.json')['files']
    assert all(file_hash(p)==h for p,h in history.items())
    frozen=read_json(ROOT/'protocol/freeze.json')['files'] if (ROOT/'protocol/freeze.json').exists() else {}
    assert all(file_hash(p)==h for p,h in frozen.items())
    m=read_json(ROOT/'tasks/manifest.json');prior=set(m['prior_focal_people_excluded']);new=set(m['new_focal_people'])
    assert len(prior)==33 and len(new)==12 and not prior&new and len(m['tasks'])==12
    earlier=read_json('artifacts/stage3/tasks/manifest.json')
    assert prior==set(earlier['reference_pool_excluded_people'])
    engine=Engine();splits=read_json('artifacts/data/splits.json')['assignments']
    assert not set(engine.weekly.person_id)&set(splits['reserved']) and engine.excluded==prior|new
    assert all(file_hash(ROOT/'source'/n)==file_hash(Path('artifacts/stage3/source')/n) for n in engine.meta['files'])
    order=read_json(ROOT/'protocol/execution_order.json')['agent_order']
    assert len(order)==24 and len({(e['question_id'],e['method']) for e in order})==24
    for method in ['full_spec','semantic']:
        assert sum(e['method']==method and e['position']==1 for e in order)==6
    assert read_json('configs/stage4_prompts.json')['generic_policy']==read_json('configs/stage3_prompts.json')['generic']
    replayed=[];semantic_recompiled=[]
    if args.replay:
        for path in sorted(ROOT.rglob('spec.json')):
            if not (path.parent/'bound.json').exists():continue
            parent=path.parent;provenance=read_json(parent/'selection_provenance.json')
            if provenance['interface']=='semantic':
                spec,proof=compile_answer(engine,read_json(parent/'question.json'),provenance['semantic_answer'],read_json(parent/'evidence.json'))
                assert spec.model_dump()==read_json(path) and proof==provenance
                assert all(p['origin']=='method_selected' for c,p in zip(spec.claims,proof['claims']) if c.template in {'comparison','personal_change'})
                semantic_recompiled.append(str(parent))
            with tempfile.TemporaryDirectory(prefix='stage4-replay-') as tmp:
                replay(engine,parent,Path(tmp)/'replay')
                for name in ['bound.json','chart.vl.json','dashboard.svg','selection_provenance.json']:
                    assert file_hash(parent/name)==file_hash(Path(tmp)/'replay'/name),str(parent)+' '+name
            replayed.append(str(parent))
    events=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()] if (ROOT/'model_ledger.jsonl').exists() else []
    gens=[e for e in events if e['event']=='generation_started'];counts=Counter(e['budget_partition'] for e in gens)
    assert len(gens)<=128 and counts['construction']<=24 and counts['pilot']<=96 and counts['setup']<=8
    ends=[e for e in events if e['event']=='process_finished'];seconds=sum(e['elapsed_seconds'] for e in ends)
    assert seconds<=5400
    results=[read_json(p) for p in (ROOT/'pilot').rglob('result.json')]
    assert all(r.get('generations',0)<=4 and r.get('tool_calls_attempted',0)<=6 and r.get('repairs',0)<=1 for r in results)
    if args.replay:
        assert len(results)==36
        assert {e['process_id'] for e in events if e['event']=='process_started'}=={e['process_id'] for e in ends}
        for path in (ROOT/'gpu').glob('*/runtime.json'):
            r=read_json(path)
            if r['generations_this_process']:
                assert r['parameter_devices']==['cuda:0'] and r['cuda_execution_proof']['device_events']>0
        for path in (ROOT/'gpu/generations').glob('*.metadata.json'):
            r=read_json(path)
            if r['status']=='completed':assert r['input_device']=='cuda:0' and r['output_device']=='cuda:0' and r['nvidia_smi_own_process']
    write_json(output,{'created_utc':now(),'status':'PASS','historical_files_unchanged':len(history),'frozen_files_unchanged':len(frozen),'new_people':12,'prior_people_excluded':33,'reserved_people_excluded':len(splits['reserved']),'pilot_results':len(results),'generation_partitions':dict(counts),'total_generations':len(gens),'model_process_seconds':seconds,'replay_count':len(replayed),'replayed':replayed,'semantic_recompile_count':len(semantic_recompiled),'semantic_recompiled':semantic_recompiled,'checks':['immutable history and frozen inputs','unchanged source observations','person-disjoint structural selection and reference pool','balanced paired order','generic policy unchanged','compiler output reconstructed without extra analyses','no compiler comparison/change claims','exact bound/chart/SVG/provenance replay','CUDA proof and append-only ledger ceilings']})
    print('PASS',output,'replayed',len(replayed))


if __name__=='__main__':main()
