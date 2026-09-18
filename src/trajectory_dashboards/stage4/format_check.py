"""One pre-freeze construction generation; saved known evidence, no tool dispatch."""
import json,time
from ..common import read_json,write_json,now
from ..prepare import FEATURES
from ..stage2.backend import compact
from ..stage2.core import Evidence
from .core import ROOT,event
from .semantic import SemanticAction,compile_answer
from .display import render


def execute(engine,generate):
    case=ROOT/'construction_format/semantic/s4_build_s3_01'
    if (case/'started.json').exists():raise ValueError('Format check already attempted')
    case.mkdir(parents=True,exist_ok=True);write_json(case/'started.json',{'utc':now(),'limit':1})
    q=read_json(ROOT/'tasks/construction.json')['episodes'][0]['question']
    evidence=read_json(ROOT/'construction/semantic/s4_build_s3_01/tool_results.json')
    prompts=read_json('configs/stage4_prompts.json')
    payload={'question':q,'windows':engine.registry.profile(q),'available_features':FEATURES,'available_references':engine.cfg['references'],
             'action_schema':SemanticAction.model_json_schema(),'public_interpretation_rules':(ROOT.parents[1]/'docs/stage4/PUBLIC_INTERPRETATION.md').read_text()}
    messages=[{'role':'system','content':prompts['common']+'\n'+prompts['generic_policy']+'\n'+prompts['semantic']},
              {'role':'user','content':json.dumps(payload)},
              {'role':'tool','name':'analyze','content':json.dumps([{'result':compact(Evidence.model_validate(e))} for e in evidence.values()])},
              {'role':'user','content':'Construction format check only. Saved known-case tool results were supplied above. Return one final Action now, with answers and conclusion at the top level. No more analyses or repair generations are available.'}]
    result={'status':'failed','kind':'one-generation construction format check, not an investigation episode','question_id':q['question_id'],'generations':1,'tool_calls':0,'repairs':0,'started_utc':now()};start=time.monotonic()
    try:
        raw,metrics=generate(messages,q['question_id'],'semantic','format_check',case)
        (case/'output.txt').write_text(raw);write_json(case/'generation_metadata.json',metrics)
        action=SemanticAction.model_validate_json(raw)
        if action.action!='final':raise ValueError('Format check requires final')
        spec,provenance=compile_answer(engine,q,action.answer,evidence)
        render(engine,q,spec,evidence,case/'accepted',origin='construction format check',provenance=provenance)
        result['status']='format_accepted'
    except Exception as exc:
        result['error']=f'{type(exc).__name__}: {exc}'
    finally:
        result.update(completed_utc=now(),elapsed_seconds=time.monotonic()-start)
        write_json(case/'result.json',result);event({'event':'construction_format_check',**result})
    return result
