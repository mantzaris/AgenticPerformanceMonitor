"""Observable bounded action loop; generation is injected by one GPU backend."""
import json,time
from pathlib import Path
from ..common import read_json,write_json,now
from ..prepare import FEATURES
from .core import ROOT,Question,Action,Specification,event
from ..stage2.backend import compact
from ..stage2.integrity import validate
from .display import render


def episode(engine,question,method,generate,case):
    q=Question.model_validate(question);case=Path(case)
    if (case/'result.json').exists() or (case/'started.json').exists():
        raise ValueError('Episode already attempted; do not rerun a failed pilot case')
    case.mkdir(parents=True,exist_ok=True)
    write_json(case/'started.json',{'utc':now(),'method':method,'question_id':q.question_id})
    prompts=read_json('configs/stage3_prompts.json')
    result={'method':method,'question_id':q.question_id,'started_utc':now(),'status':'failed','first_attempt_valid':False,'repairs':0,'generations':0,'tool_calls_attempted':0,'tool_calls_executed':0,'prompt_tokens':0,'completion_tokens':0,'fallback':False,'subsequent_analysis_after_results':False,'redundant_requests':0}
    # The complete registry is universal affordance information, never a task-specific answer/tool checklist.
    payload={'question':q.model_dump(),'windows':engine.registry.profile(q),'available_features':FEATURES,'available_references':engine.cfg['references'],'tool_window_choices':['recent','baseline'],'action_schema':Action.model_json_schema(),'public_interpretation_rules':Path('docs/stage3/PUBLIC_INTERPRETATION.md').read_text().split('For the historical')[0]}
    messages=[{'role':'system','content':prompts['common']+'\n'+prompts[method]},{'role':'user','content':json.dumps(payload)}]
    if method=='coverage_aware':
        messages.append({'role':'user','content':'First phase: extract the distinct user requests into a concise request_map. Request exactly ONE analysis now. An analyze action has requests and no specification. Your map describes requested answers, not a list of every possible tool call. Personal earlier/recent means are returned together.'})
    evidence={};sequence=[];seen_requests=set();final_attempted=False;repair_pending=False
    start=time.monotonic()
    try:
        for turn in range(engine.cfg['episode']['generations']):
            if turn:
                messages.append({'role':'user','content':json.dumps({'generations_remaining_including_this':engine.cfg['episode']['generations']-turn,'analytical_requests_remaining':engine.cfg['episode']['tool_calls']-result['tool_calls_attempted'],'instruction':'Return final now.' if turn>=2 or repair_pending else 'Choose the next useful analysis or return final, based on the observed results.'})})
                if method=='coverage_aware' and turn==1 and not repair_pending:
                    messages.append({'role':'user','content':'Update your request_map from the returned evidence. If requested answers still need analysis, batch useful unresolved requests now, with specification omitted/null. Otherwise return final. Do not combine analyze requests and a final specification in one Action. No hidden checklist exists; use only the public question and returned results.'})
            result['generations']+=1
            raw,metrics=generate(messages,q.question_id,method,'repair' if repair_pending else f'action_{turn+1}',case)
            for k in ('prompt_tokens','completion_tokens'):result[k]+=metrics.get(k,0)
            step={'turn':turn+1,'raw_output':raw,'generation_metadata':metrics}
            sequence.append(step)
            messages.append({'role':'assistant','content':raw})
            parsed=None
            try:
                parsed=json.loads(raw)
                action=Action.model_validate(parsed)
                step['action']=action.action
                step['request_map']=[s.model_dump() for s in action.request_map]
                step['stopping_status']=action.stopping_status
                for state in action.request_map:
                    if any(eid not in evidence for eid in state.evidence_ids):
                        raise ValueError('request_map.evidence_ids must refer to previously returned evidence; use an empty list before analysis')
                write_json(case/'request_state.json',{'request_map':step['request_map'],'stopping_status':action.stopping_status,'origin':'model-authored public task state; no hidden evaluator checklist','turn':turn+1})
                if action.action=='analyze':
                    if repair_pending:raise ValueError('Specification repair must return action=final; no additional analyses')
                    if turn==engine.cfg['episode']['generations']-1:raise ValueError('No generation remains for a final specification')
                    if result['tool_calls_attempted']+len(action.requests)>engine.cfg['episode']['tool_calls']:
                        raise ValueError('Analytical request budget exceeded; select existing evidence and return final')
                    if evidence:result['subsequent_analysis_after_results']=True
                    tool_results=[]
                    for req in action.requests:
                        result['tool_calls_attempted']+=1
                        signature=(req.feature,req.reference,req.window)
                        if signature in seen_requests: result['redundant_requests']+=1
                        seen_requests.add(signature)
                        try:
                            e=engine.analyze(q,req)
                            evidence[e.evidence_id]=e
                            result['tool_calls_executed']+=1
                            tool_results.append({'request':req.model_dump(),'result':compact(e)})
                        except Exception as exc:
                            tool_results.append({'request':req.model_dump(),'error':f'{type(exc).__name__}: {exc}'})
                    step['tool_results']=tool_results
                    messages.append({'role':'tool','name':'analyze','content':json.dumps(tool_results)})
                    write_json(case/'tool_results.json',{k:e.model_dump() for k,e in evidence.items()})
                else:
                    was_first=not final_attempted
                    final_attempted=True
                    step['specification']=action.specification.model_dump()
                    validate(engine,q,action.specification,evidence)
                    render(engine,q,action.specification,evidence,case/'accepted',origin='agent repaired' if result['repairs'] else 'agent original')
                    result.update(status='agent_generated_and_repaired' if result['repairs'] else 'agent_generated_and_accepted',first_attempt_valid=was_first and result['repairs']==0)
                    step['stopping_decision']='valid final specification'
                    break
            except Exception as exc:
                error=f'{type(exc).__name__}: {exc}'
                step['validation_error']=error
                write_json(case/f'validation_error_{turn+1}.json',{'raw_output':raw,'error':error})
                is_final=repair_pending or not isinstance(parsed,dict) or parsed.get('action')=='final'
                if is_final:
                    final_attempted=True
                    if result['repairs']>=engine.cfg['episode']['repairs'] or turn>=engine.cfg['episode']['generations']-1:
                        result['error']=error;step['stopping_decision']='failed final; repair unavailable';break
                    result['repairs']+=1;repair_pending=True
                    messages.append({'role':'user','content':'Final specification invalid. One repair is permitted. Return the entire corrected final Action using existing evidence. Actionable error: '+error})
                else:
                    messages.append({'role':'tool','name':'analyze','content':json.dumps({'error':error,'instruction':'Correct the request within the remaining budget, or finalize existing evidence.'})})
            finally:
                write_json(case/'sequence.json',sequence)
        if result['status']=='failed' and 'error' not in result:result['error']='Episode generation ceiling reached without an accepted final specification'
    except Exception as exc:
        result['error']=f'{type(exc).__name__}: {exc}'
        raise
    finally:
        result.update(completed_utc=now(),elapsed_seconds=time.monotonic()-start)
        write_json(case/'sequence.json',sequence)
        write_json(case/'tool_results.json',{k:e.model_dump() for k,e in evidence.items()})
        write_json(case/'result.json',result)
        event({'event':'agent_episode_finished',**result})
    # No silent fallback. A separately saved baseline remains available for every task.
    return result
