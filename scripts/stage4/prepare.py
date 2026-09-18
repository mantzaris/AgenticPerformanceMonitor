"""Twelve new development people selected by administrative structure only."""
import shutil
from trajectory_dashboards.common import read_json,write_json,file_hash,digest,now
from trajectory_dashboards.stage2.core import Question,Request
from trajectory_dashboards.stage2.integrity import independent_facts
from trajectory_dashboards.stage3.core import Engine as PreviousEngine
from trajectory_dashboards.stage3.evaluation import requirements
from trajectory_dashboards.stage4.core import ROOT,Engine,event


def main():
    if (ROOT/'tasks/manifest.json').exists():raise ValueError('Preserve selected tasks')
    cfg=read_json('configs/stage4.json');previous=read_json('artifacts/stage3/tasks/manifest.json')
    old=PreviousEngine();prior=set(previous['reference_pool_excluded_people']);used=set(prior)
    cases=[];tasks=[];order=[]
    # Reuse the declared family/course/profile/eligibility slots and public
    # wording, never the old focal people or outcome values.
    for i,slot in enumerate(previous['cases'],1):
        cid=f's4_{i:02d}';kind=slot['family'];course=slot['course'];profile=slot['profile'];criterion=slot['criterion'];p=cfg['profiles'][profile]
        rows=old.weekly[old.weekly.course.eq(course)&old.weekly.end_day.le(p['cutoff_day'])];pool=[]
        for person,g in rows.groupby('person_id'):
            if person in used:continue
            n=int(g.eligible_days.gt(0).sum());recent=int(g[g.week.between(*p['recent'])].eligible_days.gt(0).sum());earlier=int(g[g.week.between(*p['baseline'])].eligible_days.gt(0).sum())
            ok=n>=len(g)-1 and min(recent,earlier)>=2
            if criterion=='partial':ok=1<=n<len(g)-1
            if criterion=='insufficient':ok=recent<2 and earlier>=1
            if criterion in {'repeat','first'}:ok=ok and g.prior_attempt_group.iloc[0]==criterion+'_attempt'
            if ok:pool.append(int(person))
        if not pool:raise ValueError('No structural candidates for '+cid)
        person=min(pool,key=lambda x:digest([cfg['selection_seed'],cid,x]));used.add(person)
        old_q=next(t['question'] for t in previous['tasks'] if t['case_id']==slot['case_id'] and t['phrasing']=='a')
        q={**old_q,'question_id':cid,'person_id':person}
        case={'case_id':cid,'person_id':person,'family':kind,'course':course,'profile':profile,'criterion':criterion,'candidate_people':len(pool),'synthetic':False}
        cases.append(case);tasks.append({'case_id':cid,'question':q,'synthetic':False})
        pair=['full_spec','semantic'] if i%2 else ['semantic','full_spec']
        order.extend({'question_id':cid,'method':m,'position':j+1} for j,m in enumerate(pair))
    source=ROOT/'source';source.mkdir(parents=True,exist_ok=True)
    for name in old.meta['files']:shutil.copyfile(old.source/name,source/name)
    write_json(source/'manifest.json',{**old.meta,'created_utc':now(),'excluded_reference_people':sorted(used),'historical_source_manifest_sha256':file_hash(old.source/'manifest.json'),'description':'Unmodified development-only feature bundle; fixed pool excludes all 33 earlier and 12 new Stage 4 focal people across registrations.'})
    write_json(ROOT/'tasks/manifest.json',{'version':'stage4-v1','selected_utc':now(),'cases':cases,'tasks':tasks,'prior_focal_people_excluded':sorted(prior),'new_focal_people':sorted(used-prior),'reference_pool_excluded_people':sorted(used),'selection_rule':'Minimum SHA256(seed, Stage 4 case ID, person ID) among unused people meeting declared administrative eligibility/prior-attempt/course/profile conditions. No activity magnitudes or method results used.','seed':cfg['selection_seed'],'design':'12 development people, one question each, two per existing family; not held-out evaluation or new families.','external_review':'Awaiting human scientific review'})
    write_json(ROOT/'protocol/execution_order.json',{'baseline':'All twelve on the same GPU host CPU before model loading','agent_order':order,'counterbalance':'Full interface first in odd cases, compact first in even cases; six of each, one of each per family.'})
    construction=[]
    for cid in ['s3_01','s3_03','s3_05','s3_07','s3_09','s3_11']:
        q=next(t['question'] for t in previous['tasks'] if t['question']['question_id']==cid+'a')
        construction.append({'question':{**q,'question_id':'s4_build_'+cid},'method':'semantic'})
    write_json(ROOT/'tasks/construction.json',{'episodes':construction,'note':'Six already known Stage 3 people, one per family; at most 24 construction generations, not new pilot evidence.'})
    engine=Engine();rubrics=[]
    for t in tasks:
        q=Question.model_validate(t['question']);items=requirements(q.model_dump());signatures=set();facts={}
        for item in items:
            if item['category'] in {'peer','personal','focal','direction'}:
                signatures.update((f,r) for f in item['features'] for r in item.get('references',[item.get('reference','course')]))
        for f,r in sorted(signatures):
            fact=independent_facts(engine,q,Request(question_id=q.question_id,feature=f,reference=r))
            facts[f+':'+r]={k:fact[k] for k in ['feature','unit','reference','reference_label','window','reference_window','status','people','observations','summary']}
        rubrics.append({'question_id':q.question_id,'required_answers':items,'independent_facts':facts,'external_review':'Awaiting independent human scientific review; row-loop cross-check is not human review'})
    write_json(ROOT/'evaluator_only/rubrics.json',{'version':'unchanged Stage 3 answer semantics with explicit compiler attribution','agent_visibility':'Never provided to policy, tool, compiler or model; only offline scoring','rubrics':rubrics})
    event({'event':'tasks_selected','new_people':12,'questions':12,'manifest_sha256':file_hash(ROOT/'tasks/manifest.json')})
    print([(c['case_id'],c['person_id'],c['candidate_people']) for c in cases])


if __name__=='__main__':main()
