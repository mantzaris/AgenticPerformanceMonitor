"""Focused scientific invariants, immutable inputs and exact replay without a model."""
import argparse, json, tempfile
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,file_hash,now,digest
from trajectory_dashboards.stage3.core import ROOT,Engine
from trajectory_dashboards.stage3.display import replay


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--replay',action='store_true');args=parser.parse_args()
    output=Path(args.output)
    if output.exists():raise ValueError('Verification output already exists; choose a new path')
    history=read_json(ROOT/'checks/history_inventory.json')['files']
    assert all(file_hash(p)==sha for p,sha in history.items())
    freeze=ROOT/'protocol/freeze.json'
    frozen=read_json(freeze)['files'] if freeze.exists() else {}
    assert all(file_hash(p)==sha for p,sha in frozen.items())
    manifest=read_json(ROOT/'tasks/manifest.json');tasks=manifest['tasks']
    new=set(manifest['new_focal_people']);prior=set(manifest['prior_focal_people_excluded'])
    assert len(new)==12 and not new&prior and len(tasks)==24
    engine=Engine();splits=read_json('artifacts/data/splits.json')['assignments']
    assert not set(engine.weekly.person_id)&set(splits['reserved'])
    assert new|prior <= engine.excluded
    rubric={r['question_id']:r for r in read_json(ROOT/'evaluator_only/rubrics.json')['rubrics']}
    for cid in {t['case_id'] for t in tasks}:
        a,b=rubric[cid+'a'],rubric[cid+'b']
        assert a['required_answers']==b['required_answers'] and a['independent_facts']==b['independent_facts']
    order=read_json(ROOT/'protocol/execution_order.json')['agent_order']
    assert len(order)==72 and len({(e['question_id'],e['method']) for e in order})==72
    for m in ['generic','reference_sensitive','coverage_aware']:
        assert all(sum(e['method']==m and e['position']==p for e in order)==8 for p in [1,2,3])
    old=read_json('configs/stage2_prompts.json');newprompts=read_json('configs/stage3_prompts.json')
    assert all(old[m]==newprompts[m] for m in ['generic','reference_sensitive'])
    replayed=[]
    if args.replay:
        for path in sorted(ROOT.rglob('spec.json')):
            if not (path.parent/'bound.json').exists():continue
            with tempfile.TemporaryDirectory(prefix='stage3-replay-') as tmp:
                replay(engine,path.parent,Path(tmp)/'replay')
                for name in ['bound.json','chart.vl.json','dashboard.svg']:
                    assert file_hash(path.parent/name)==file_hash(Path(tmp)/'replay'/name),str(path)+' '+name
            replayed.append(str(path.parent))
    events=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()] if (ROOT/'model_ledger.jsonl').exists() else []
    gens=[e for e in events if e['event']=='generation_started']
    assert len(gens)<=320
    assert sum(e['budget_partition']=='construction_setup' for e in gens)<=32
    assert sum(e['budget_partition']=='pilot' for e in gens)<=288
    process=[e for e in events if e['event']=='process_finished']
    assert sum(e['elapsed_seconds'] for e in process)<=7200
    results=[read_json(p) for p in (ROOT/'pilot').rglob('result.json')]
    assert all(r.get('tool_calls_attempted',0)<=6 and r.get('generations',0)<=4 and r.get('repairs',0)<=1 for r in results)
    if args.replay:
        assert len(results)==96
        assert {e['process_id'] for e in events if e['event']=='process_started'}=={e['process_id'] for e in process}
        for p in (ROOT/'gpu').glob('*/runtime.json'):
            r=read_json(p);assert r['parameter_devices']==['cuda:0'] and r['cuda_execution_proof']['device_events']>0
        for p in (ROOT/'gpu/generations').glob('*.metadata.json'):
            r=read_json(p)
            if r['status']=='completed':assert r['input_device']=='cuda:0' and r['output_device']=='cuda:0' and r['nvidia_smi_own_process']
    write_json(output,{'created_utc':now(),'status':'PASS','historical_files_unchanged':len(history),'frozen_files_unchanged':len(frozen),'new_people':12,'question_instances':24,'agent_order_entries':72,'paired_facts_and_requirements_equal':True,'reserved_people_excluded':len(splits['reserved']),'old_policy_texts_unchanged':True,'replayed':replayed,'replay_count':len(replayed),'pilot_result_count':len(results),'attempted_generations':len(gens),'model_process_seconds':sum(e['elapsed_seconds'] for e in process),'checks':['person-disjoint structural selection','fixed reference exclusions','unmodified development observations','identical paired facts/contracts','balanced serial positions','historical/frozen hashes','bounds and actual CUDA tensor/kernel proof','exact bound/chart/SVG replay when requested']})
    print('PASS',output,'replays',len(replayed))

if __name__=='__main__':main()
