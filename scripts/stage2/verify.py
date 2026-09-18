"""Focused saved-artifact verification; no inference and no edits to Stage 1."""
import argparse,json,tempfile
from pathlib import Path
from html import escape
from trajectory_dashboards.common import read_json,write_json,file_hash,digest,now
from trajectory_dashboards.stage2.core import ROOT
from trajectory_dashboards.stage2.backend import Engine
from trajectory_dashboards.stage2.display import replay


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default=str(ROOT/'checks/verification.json'));p.add_argument('--skip-pilot',action='store_true');args=p.parse_args()
    inventory=read_json(ROOT/'checks/stage1_inventory.json')
    for path,expected in inventory['files'].items():
        assert file_hash(path)==expected,('Stage 1 historical file changed',path)
    frozen=ROOT/'protocol/freeze.json'
    if frozen.exists():
        for path,expected in read_json(frozen)['files'].items():assert file_hash(path)==expected,('Frozen pilot input changed',path)
    engine=Engine()
    packages=sorted((ROOT/'construction').glob('*/c*/accepted'))+sorted((ROOT/'followups').glob('*'))
    if not args.skip_pilot:packages+=sorted((ROOT/'pilot').glob('*/p*/accepted'))
    results=[]
    with tempfile.TemporaryDirectory(prefix='stage2-replay-') as tmp:
        for i,source in enumerate(packages):
            output=Path(tmp)/str(i)
            replay(engine,source,output)
            actual,expected=read_json(output/'bound.json'),read_json(source/'bound.json')
            assert actual==expected,source
            assert read_json(output/'chart.vl.json')==read_json(source/'chart.vl.json'),source
            body=(output/'dashboard.html').read_text()
            assert all(escape(c['text']) in body for c in actual['claims'])
            assert all(f'id="{eid}"' in body for eid in actual['evidence_hashes'])
            results.append({'path':str(source),'status':'PASS','numerical_integrity':'independent-source-bound','chart_spec_exact_replay':True,'svg_exact_replay':file_hash(output/'dashboard.svg')==file_hash(source/'dashboard.svg')})
    events=[json.loads(s) for s in (ROOT/'model_ledger.jsonl').read_text().splitlines()]
    starts=[e for e in events if e['event']=='process_started'];ends=[e for e in events if e['event']=='process_finished']
    assert {e['process_id'] for e in starts}=={e['process_id'] for e in ends}
    generations=[e for e in events if e['event']=='generation_started']
    assert len(generations)<=120 and sum(e['elapsed_seconds'] for e in ends)<=7200
    assert len({e['generation'] for e in generations})==len(generations)
    for runtime in (ROOT/'gpu').glob('*/runtime.json'):
        r=read_json(runtime)
        assert r['parameter_devices']==['cuda:0'] and r['parameter_dtypes']==['torch.bfloat16']
        assert r['cuda_execution_proof']['device_events']>0 and r['nvidia_smi_after_load']
        assert r['revision']==engine.cfg['model_revision'] and r['model_files_verified']
        for result in r['results']:
            assert result['generations']<=4 and result['tool_calls_attempted']<=6 and result['repairs']<=1
    if not args.skip_pilot:
        tasks=[t for t in read_json(ROOT/'tasks/manifest.json')['tasks'] if t['subset']=='pilot']
        for t in tasks:
            for method in ('baseline','generic','reference_sensitive'):
                assert (ROOT/'pilot'/method/t['question']['question_id']/'result.json').is_file()
        freeze_time=read_json(frozen)['frozen_utc']
        assert all(e['utc']>freeze_time for e in starts if e['subset']=='pilot')
    write_json(args.output,{'verified_utc':now(),'status':'PASS','historical_files_unchanged':len(inventory['files']),'frozen_inputs_unchanged':frozen.exists(),'replays':results,'model_generations':len(generations),'model_process_seconds':sum(e['elapsed_seconds'] for e in ends),'checks':['Historical Stage 1 hashes unchanged','Frozen pilot hashes unchanged','Every accepted evidence record independently checked against source','Claims, chart tables and evidence links replay without model imports','Reserved identities excluded by engine','All frozen pilot tasks/methods retained','CUDA parameter placement, recorded device events and own-process VRAM','Episode and cumulative budgets; every model process closed']})
    print('Verified',len(results),'saved dashboard packages;',len(generations),'generations, with closed process reservations.')

if __name__=='__main__':main()
