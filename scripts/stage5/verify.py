"""Focused frozen inputs, provenance, resource ledger and exact replay checks."""
import argparse,json,tempfile
from collections import Counter
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,file_hash,now,digest
from trajectory_dashboards.stage5.core import ROOT,Engine
from trajectory_dashboards.stage5.adapter import replay
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
    assert len(prior)==45 and len(new)==12 and not prior&new and len(m['tasks'])==12
    earlier=read_json('artifacts/stage4/tasks/manifest.json')
    assert prior==set(earlier['reference_pool_excluded_people'])
    engine=Engine();splits=read_json('artifacts/data/splits.json')['assignments']
    assert not set(engine.weekly.person_id)&set(splits['reserved']) and engine.excluded==prior|new
    assert all(file_hash(ROOT/'source'/n)==file_hash(Path('artifacts/stage4/source')/n) for n in engine.meta['files'])
    order=read_json(ROOT/'protocol/execution_order.json')['agent_order']
    assert len(order)==48 and len({(e['question_id'],e['condition']) for e in order})==48
    for model in ['qwen7b','qwen14b']:
        for method in ['full_spec','semantic']:
            assert sum(e['model_key']==model and e['interface']==method and e['within_case_position']==1 for e in order)==6
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
            with tempfile.TemporaryDirectory(prefix='stage5-replay-') as tmp:
                replay(engine,parent,Path(tmp)/'replay')
                for name in ['bound.json','chart.vl.json','dashboard.svg','selection_provenance.json']:
                    assert file_hash(parent/name)==file_hash(Path(tmp)/'replay'/name),str(parent)+' '+name
            replayed.append(str(parent))
    events=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()] if (ROOT/'model_ledger.jsonl').exists() else []
    gens=[e for e in events if e['event']=='generation_started'];counts=Counter(e['budget_partition'] for e in gens)
    assert len(gens)<=208 and counts['comparison']<=192 and counts['setup']<=16
    ends=[e for e in events if e['event']=='process_finished'];seconds=sum(e['elapsed_seconds'] for e in ends)
    assert seconds<=7200
    results=[read_json(p) for p in (ROOT/'comparison').rglob('result.json')]
    assert all(r.get('generations',0)<=4 and r.get('tool_calls_attempted',0)<=6 and r.get('repairs',0)<=1 for r in results)
    if args.replay:
        assert len(results)==60
        assert {e['process_id'] for e in events if e['event']=='process_started'}=={e['process_id'] for e in ends}
        for path in (ROOT/'gpu').glob('*/runtime.json'):
            r=read_json(path)
            if r['generations_this_process']:
                assert r['parameter_devices']==['cuda:0'] and r['parameter_dtypes']==['torch.bfloat16'] and r['cuda_execution_proof']['device_events']>0
                assert r['revision']==read_json('configs/stage5.json')['models'][r['model_key']]['revision']
        for path in (ROOT/'gpu/generations').glob('*.metadata.json'):
            r=read_json(path)
            if r['status']=='completed':assert r['input_device']=='cuda:0' and r['output_device']=='cuda:0' and r['nvidia_smi_own_process']
    # Compare complete initial public messages between checkpoints, before their
    # identical pinned templates/tokenizers. Neither may see evaluator-only files.
    first_messages={}
    for path in (ROOT/'gpu/generations').glob('*.metadata.json'):
        meta=read_json(path)
        if meta['budget_partition']=='comparison' and meta['phase']=='action_1':
            value=read_json(str(path).replace('.metadata.json','.input.json'))
            payload=json.loads(value[1]['content'])
            assert set(payload)=={'question','windows','available_features','available_references','tool_window_choices','action_schema','public_interpretation_rules'}
            first_messages[(meta['model_key'],meta['question_id'],meta['method'])]=value
    if args.replay:
        assert len(first_messages)==48
        for task in m['tasks']:
            for method in ['full_spec','semantic']:
                assert first_messages[('qwen7b',task['question']['question_id'],method)]==first_messages[('qwen14b',task['question']['question_id'],method)]
        assert len(gens)==len({e['generation'] for e in gens})
        for model in ['qwen7b','qwen14b']:
            proof=read_json(ROOT/f'checks/capacity_{model}.json')
            assert proof['status']=='PASS' and proof['metadata']['prompt_tokens']==16000 and proof['metadata']['completion_tokens']==1500
    write_json(output,{'created_utc':now(),'status':'PASS','historical_files_unchanged':len(history),'frozen_files_unchanged':len(frozen),'new_people':12,'prior_people_excluded':45,'reserved_people_excluded':len(splits['reserved']),'comparison_results':len(results),'generation_partitions':dict(counts),'total_generations':len(gens),'model_process_seconds':seconds,'replay_count':len(replayed),'replayed':replayed,'semantic_recompile_count':len(semantic_recompiled),'semantic_recompiled':semantic_recompiled,'checks':['immutable history and frozen inputs','unchanged source observations','person-disjoint structural selection and reference pool','balanced paired order','48 equivalent public initial messages across checkpoints','generic policy unchanged','compiler output reconstructed without extra analyses','no compiler comparison/change claims','exact bound/chart/SVG/provenance replay','CUDA proof and append-only ledger ceilings']})
    print('PASS',output,'replayed',len(replayed))


if __name__=='__main__':main()
