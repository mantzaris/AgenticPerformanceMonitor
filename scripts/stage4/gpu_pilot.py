"""One existing local model, a restart-persistent budget, and bounded episodes."""
import time
PROCESS_START=time.monotonic()
import argparse,contextlib,fcntl,gc,importlib.metadata as metadata,json,os,signal,subprocess,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,file_hash,digest,commit,now
from trajectory_dashboards.stage4.core import ROOT,append_event
from trajectory_dashboards.stage4.core import Engine
from trajectory_dashboards.stage4.agents import episode


def own_gpu_process():
    output=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'],text=True)
    return [line for line in output.splitlines() if line.split(',')[0].strip()==str(os.getpid())]


def verify_freeze():
    frozen=read_json(ROOT/'protocol/freeze.json')
    for path,sha in frozen['files'].items():
        if file_hash(path)!=sha:raise ValueError('Frozen pilot input changed: '+path)
    return digest(frozen)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--subset',choices=['construction','pilot'],required=True)
    parser.add_argument('--model-path',required=True)
    parser.add_argument('--format-check',action='store_true',help='One known-case final-format generation, counted as construction')
    parser.add_argument('--authorization-start-utc',help='Explicit new independent rerun authorization; requires a fresh ledger and outputs, never reuse original results')
    args=parser.parse_args()
    if args.format_check and args.subset!='construction':raise ValueError('Format check is construction only')
    cfg=read_json('configs/stage4.json')
    ledger=ROOT/'model_ledger.jsonl'
    lock=open(ROOT/'model_budget.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    events=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
    starts=[e for e in events if e['event']=='process_started'];ends=[e for e in events if e['event']=='process_finished']
    if {e['process_id'] for e in starts}!={e['process_id'] for e in ends}:
        raise RuntimeError('Unclosed process reservation: reconcile actual runtime before restart')
    used_seconds=sum(e['elapsed_seconds'] for e in ends)
    generations=sum(e['event']=='generation_started' for e in events)
    deadline=datetime.fromisoformat(cfg['deadline_utc'].replace('Z','+00:00'))
    if args.authorization_start_utc:
        if events:raise ValueError('New authorization requires a fresh checkout/output ledger; historical attempts must be preserved')
        deadline=datetime.fromisoformat(args.authorization_start_utc.replace('Z','+00:00'))+timedelta(seconds=cfg['wall_seconds_limit'])
    remaining=min(cfg['gpu_process_seconds_limit']-used_seconds,(deadline-datetime.now(timezone.utc)).total_seconds())
    tasks=read_json(ROOT/'tasks/manifest.json')['tasks']
    if args.subset=='construction':
        episodes=[(t['question'],t['method']) for t in read_json(ROOT/'tasks/construction.json')['episodes']]
    else:
        questions={t['question']['question_id']:t['question'] for t in tasks}
        episodes=[(questions[e['question_id']],e['method']) for e in read_json(ROOT/'protocol/execution_order.json')['agent_order']]
    used={part:sum(e['event']=='generation_started' and e.get('budget_partition')==part for e in events) for part in ['construction','pilot','setup']}
    limits={'construction':cfg['construction_generation_limit'],'pilot':cfg['pilot_generation_limit'],'setup':cfg['setup_generation_limit']}
    episodes=[(q,m) for q,m in episodes if not (ROOT/args.subset/m/q['question_id']/'started.json').exists() and not (ROOT/args.subset/m/q['question_id']/'result.json').exists()]
    if args.format_check:
        if (ROOT/'construction_format/semantic/s4_build_s3_01/started.json').exists():raise ValueError('Format check already attempted')
        episodes=[(read_json(ROOT/'tasks/construction.json')['episodes'][0]['question'],'semantic')]
    if not episodes:
        print('No unattempted episodes remain; historical attempts are preserved.');return
    episode_reservation=1 if args.format_check else 4*len(episodes)
    if used[args.subset]+episode_reservation>limits[args.subset]:
        raise RuntimeError('Insufficient reserved generation partition for unattempted episodes')
    if used['setup']+1>limits['setup'] or generations+episode_reservation+1>cfg['generation_limit']:
        raise RuntimeError('Total generation/setup budget exhausted')
    if remaining<=0:raise RuntimeError('Model/stage time exhausted')
    freeze_hash=verify_freeze() if args.subset=='pilot' else None
    process_id=f"{args.subset}_{len(starts)+1:02d}"
    out=ROOT/'gpu'/process_id;out.mkdir(parents=True,exist_ok=False)
    append_event({'event':'process_started','process_id':process_id,'pid':os.getpid(),'subset':args.subset,'remaining_seconds':remaining,'generations_before':generations,'execution_commit':commit(),'freeze_sha256':freeze_hash},ledger)
    runtime={'process_id':process_id,'subset':args.subset,'started_utc':now(),'execution_commit':commit(),'freeze_sha256':freeze_hash,'model':cfg['model'],'revision':cfg['model_revision'],'backend':cfg['backend'],'precision':'bfloat16','quantization':'none','cpu_offload':False,'decoding':cfg['decoding'],'warmup_generations':1,'warmup_budget_partition':'setup','timing_note':'Shared load/hash/import/profile overhead is not assigned to any method; CPU baseline runs separately on this same host' ,'generations_before':generations,'results':[],'status':'running'}
    def stop(*args):raise TimeoutError('Stage/model process deadline reached')
    signal.signal(signal.SIGALRM,stop);signal.signal(signal.SIGTERM,stop)
    signal.alarm(max(1,int(remaining-(time.monotonic()-PROCESS_START)-10)))
    model=None
    try:
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        runtime['environment']={name:metadata.version(name) for name in ['torch','transformers','accelerate','huggingface-hub','numpy','pandas','pydantic','altair','vl-convert-python']}
        runtime['environment'].update(python=sys.version,cuda_runtime=torch.version.cuda)
        runtime['gpu']=subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader'],text=True).strip()
        if not torch.cuda.is_available() or 'RTX 6000 Ada' not in runtime['gpu']:raise RuntimeError('Intended existing GPU unavailable; no CPU fallback')
        manifest=read_json('artifacts/gpu/model_manifest.json')
        if manifest['revision']!=cfg['model_revision']:raise ValueError('Pinned revision mismatch')
        # Reuse downloaded local weights; validate actual bytes against the historical manifest.
        runtime['model_manifest_sha256']=file_hash('artifacts/gpu/model_manifest.json')
        runtime['model_files_verified']=[]
        for filename,entry in manifest['files'].items():
            expected=entry['sha256']
            if file_hash(Path(args.model_path)/filename)!=expected:raise ValueError('Model file hash mismatch: '+filename)
            runtime['model_files_verified'].append(filename)
        torch.manual_seed(cfg['seed'])
        tokenizer=AutoTokenizer.from_pretrained(args.model_path,local_files_only=True)
        model=AutoModelForCausalLM.from_pretrained(args.model_path,local_files_only=True,torch_dtype=torch.bfloat16,device_map={'':'cuda:0'},attn_implementation='sdpa').eval()
        runtime['parameter_devices']=sorted({str(p.device) for p in model.parameters()})
        runtime['parameter_dtypes']=sorted({str(p.dtype) for p in model.parameters()})
        if runtime['parameter_devices']!=['cuda:0']:raise RuntimeError('Unexpected CPU/offload device')
        runtime['nvidia_smi_after_load']=own_gpu_process();runtime['allocated_bytes_after_load']=int(torch.cuda.memory_allocated())
        engine=Engine()
        write_json(out/'runtime_running.json',runtime)
        first_in_process=True
        load_complete=time.monotonic();runtime['shared_initialization_seconds']=load_complete-PROCESS_START
        def generate(messages,question_id,method,phase,case):
            nonlocal generations,first_in_process
            if generations>=cfg['generation_limit'] or time.monotonic()-PROCESS_START>=remaining or datetime.now(timezone.utc)>=deadline:raise RuntimeError('Stage/model generation or time budget exhausted')
            partition='setup' if phase=='setup_profile' else args.subset
            if used[partition]>=limits[partition]:raise RuntimeError('Generation partition exhausted: '+partition)
            used[partition]+=1
            generations+=1
            stem=ROOT/'gpu/generations'/f'{generations:03d}_{question_id}_{method}_{phase}'
            stem.parent.mkdir(parents=True,exist_ok=True)
            write_json(str(stem)+'.input.json',messages)
            append_event({'event':'generation_started','process_id':process_id,'generation':generations,'question_id':question_id,'method':method,'phase':phase,'budget_partition':partition},ledger)
            record={'generation':generations,'process_id':process_id,'question_id':question_id,'method':method,'phase':phase,'budget_partition':partition,'started_utc':now()}
            start=time.monotonic()
            try:
                prompt=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
                inputs=tokenizer(prompt,return_tensors='pt').to('cuda:0')
                record.update(prompt_tokens=int(inputs.input_ids.shape[1]),input_device=str(inputs.input_ids.device))
                if inputs.input_ids.shape[1]>16000:raise ValueError('Input exceeds frozen 16000-token context ceiling')
                event_start,event_end=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
                profile=torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,torch.profiler.ProfilerActivity.CUDA]) if first_in_process else contextlib.nullcontext()
                with profile as prof,torch.inference_mode():
                    event_start.record()
                    generated=model.generate(**inputs,do_sample=cfg['decoding']['do_sample'],max_new_tokens=1 if phase=='setup_profile' else cfg['decoding']['max_new_tokens'],pad_token_id=tokenizer.eos_token_id)
                    event_end.record();torch.cuda.synchronize()
                if prof:
                    kernels=[e for e in prof.events() if e.device_type==torch.autograd.DeviceType.CUDA]
                    runtime['cuda_execution_proof']={'generation':generations,'device_events':len(kernels),'kernel_names':list(dict.fromkeys(e.name for e in kernels))[:16],'total_device_time_us':float(sum(e.device_time_total for e in kernels))}
                    if not kernels:raise RuntimeError('No CUDA execution recorded')
                    first_in_process=False
                raw=tokenizer.decode(generated[0,inputs.input_ids.shape[1]:],skip_special_tokens=True)
                Path(str(stem)+'.output.txt').write_text(raw)
                eos = model.generation_config.eos_token_id
                eos = eos if isinstance(eos,list) else [eos]
                last_token = int(generated[0,-1])
                reached_eos = last_token in eos
                ceiling = 1 if phase=='setup_profile' else cfg['decoding']['max_new_tokens']
                record.update(last_generated_token_id=last_token, eos_reached=reached_eos,
                              output_token_ceiling=ceiling,
                              finish_reason='eos' if reached_eos else ('output_ceiling' if generated.shape[1]-inputs.input_ids.shape[1]>=ceiling else 'other'))
                record.update(status='completed',completion_tokens=int(generated.shape[1]-inputs.input_ids.shape[1]),output_device=str(generated.device),cuda_event_ms=float(event_start.elapsed_time(event_end)),allocated_bytes=int(torch.cuda.memory_allocated()),peak_allocated_bytes=int(torch.cuda.max_memory_allocated()),nvidia_smi_own_process=own_gpu_process())
                return raw,record
            except Exception as exc:
                record.update(status='failed',error=f'{type(exc).__name__}: {exc}');raise
            finally:
                record.update(elapsed_seconds=time.monotonic()-start,completed_utc=now())
                write_json(str(stem)+'.metadata.json',record)
                append_event({'event':'generation_finished',**record},ledger)
        warm_start=time.monotonic()
        generate([{'role':'user','content':'Return the word ready.'}],process_id,'setup','setup_profile',out)
        runtime['shared_profile_warmup_seconds']=time.monotonic()-warm_start
        runtime['profiling_in_pilot_episode']=False
        if args.format_check:
            from trajectory_dashboards.stage4.format_check import execute
            runtime['results'].append(execute(engine,generate))
            episodes=[]
        for q,method in episodes:
            case=ROOT/args.subset/method/q['question_id']
            try:
                result=episode(engine,q,method,generate,case)
            except Exception as exc:
                result=read_json(case/'result.json')
                if isinstance(exc,TimeoutError) or time.monotonic()-PROCESS_START>=remaining or datetime.now(timezone.utc)>=deadline:
                    raise
                # Preserve a failed generation/episode, do not retry it. A fresh
                # next episode may still run within the existing reservations.
                gc.collect();torch.cuda.empty_cache()
            runtime['results'].append(result)
            write_json(out/'runtime_running.json',runtime)
            print(json.dumps(result),flush=True)
        runtime['status']='completed'
        runtime['partition_totals']=used
    except Exception as exc:
        runtime.update(status='failed',error=f'{type(exc).__name__}: {exc}');raise
    finally:
        if model is not None:
            del model;gc.collect()
            import torch
            torch.cuda.empty_cache();torch.cuda.synchronize()
        elapsed=time.monotonic()-PROCESS_START
        runtime.update(completed_utc=now(),gpu_process_seconds=elapsed,cumulative_gpu_process_seconds=used_seconds+elapsed,generations_this_process=generations-runtime['generations_before'],cumulative_generations=generations,billing_time='Unknown; not inferred from model process or CUDA event time')
        write_json(out/'runtime.json',runtime)
        append_event({'event':'process_finished','process_id':process_id,'elapsed_seconds':elapsed,'generation_count':generations,'status':runtime['status']},ledger)
        signal.alarm(0)

if __name__=='__main__':main()
