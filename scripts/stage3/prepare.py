"""Select twelve new people by administrative structure; never by results."""
import itertools, shutil
from pathlib import Path
from trajectory_dashboards.common import read_json, write_json, file_hash, digest, now
from trajectory_dashboards.stage2.core import Question, Request
from trajectory_dashboards.stage2.integrity import independent_facts
from trajectory_dashboards.stage3.core import ROOT, Engine, event
from trajectory_dashboards.stage3.evaluation import requirements


TEXT = {
 'personal_change': [
  'How has my recorded click rate (clicks per eligible day) changed from my earlier history to the recent window, and how does my recent rate compare with presentation peers?',
  'Compare my recent mean clicks per eligible day both with my own earlier mean and with the mean for other development people in this presentation.'],
 'reference_sensitivity': [
  'For recent clicks per eligible day, is the direction of my comparison the same for presentation peers, same-prior-attempt peers, and presentation peers in the earlier study window? Show each of the three comparisons.',
  'Show my recent recorded click-rate comparison against each reference: course presentation, matching prior-attempt group, and the earlier-stage presentation group. Does the direction agree across all three?'],
 'observation_limits': [
  'What is my recent mean clicks per eligible day, and what limits follow from administrative eligibility and unknown logging completeness? Also show recent weekly means of nonbanked submissions and scheduled assessments without recorded submission, with assessment record states. What can these measurements establish?',
  'Describe my recent recorded click rate, eligibility states, and logging limitations. Include mean nonbanked submissions per observed week and mean scheduled assessments lacking a recorded submission per observed week, plus assessment states and what remains unknown.'],
 'insufficient_support': [
  'Is there enough observed support to compare my recent clicks per eligible day with my own earlier mean and with presentation peers? Answer each comparison separately, saying which is unsupported if necessary.',
  'Check two comparisons of my recorded click rate: recent versus my earlier history, and recent versus course peers. For each, give the supported descriptive result or identify insufficient evidence.'],
 'assessment_availability': [
  'What are my recent observed-week means for nonbanked submissions and scheduled assessments without a recorded submission? Include dated assessment record states. Can these records establish my marks or learning progress?',
  'Summarize recent nonbanked submissions per observed week and scheduled non-submissions per observed week, alongside the assessment states. Explain whether marks and learning progress are available from these measurements.'],
 'alternate_windows': [
  'Using these earlier and recent windows, compare my clicks per eligible day with my own earlier mean and with each of the presentation, same-prior-attempt, and earlier-stage peer references. Show whether the peer comparison direction changes.',
  'For the specified windows, show personal earlier-to-recent change in recorded click rate and the recent comparison against all three peer definitions (course, prior-attempt group, earlier stage). Does the direction depend on the reference?']}


def main():
    if (ROOT/'tasks/manifest.json').exists():
        raise ValueError('Task selection already exists; preserve it')
    from trajectory_dashboards.stage2.backend import Engine as OldEngine
    old = OldEngine()
    cfg = read_json('configs/stage3.json')
    old_tasks = read_json('artifacts/stage2/tasks/manifest.json')['tasks']
    prior = {t['question']['person_id'] for t in old_tasks} | {q['person_id'] for q in read_json('artifacts/data/questions.json')}
    used = set(prior)
    layout = [
      ('personal_change','AAA_2013J','standard','adequate'),('personal_change','BBB_2013B','mid','adequate'),
      ('reference_sensitivity','BBB_2013B','standard','repeat'),('reference_sensitivity','BBB_2013B','standard','first'),
      ('observation_limits','BBB_2013B','mid','partial'),('observation_limits','AAA_2013J','standard','partial'),
      ('insufficient_support','BBB_2013B','short','insufficient'),('insufficient_support','BBB_2013B','narrow','insufficient'),
      ('assessment_availability','AAA_2013J','standard','adequate'),('assessment_availability','BBB_2013B','standard','adequate'),
      ('alternate_windows','AAA_2013J','mid','adequate'),('alternate_windows','BBB_2013B','alternate','adequate')]
    cases=[]; tasks=[]; order=[]
    permutations=list(itertools.permutations(['generic','reference_sensitive','coverage_aware']))
    for i,(kind,course,profile,criterion) in enumerate(layout,1):
        cid=f's3_{i:02d}'; p=cfg['profiles'][profile]
        rows=old.weekly[old.weekly.course.eq(course)&old.weekly.end_day.le(p['cutoff_day'])]
        pool=[]
        for person,g in rows.groupby('person_id'):
            if person in used: continue
            n=int(g.eligible_days.gt(0).sum())
            recent=int(g[g.week.between(*p['recent'])].eligible_days.gt(0).sum())
            earlier=int(g[g.week.between(*p['baseline'])].eligible_days.gt(0).sum())
            ok=n>=len(g)-1 and min(recent,earlier)>=2
            if criterion=='partial': ok=1<=n<len(g)-1
            if criterion=='insufficient': ok=recent<2 and earlier>=1
            if criterion in {'repeat','first'}: ok=ok and g.prior_attempt_group.iloc[0]==criterion+'_attempt'
            if ok: pool.append(int(person))
        if not pool: raise ValueError('No structural candidates: '+cid)
        person=min(pool,key=lambda x:digest([cfg['selection_seed'],cid,x])); used.add(person)
        case={'case_id':cid,'person_id':person,'family':kind,'course':course,'profile':profile,'criterion':criterion,'candidate_people':len(pool),'synthetic':False}
        cases.append(case)
        for j,phrase in enumerate(TEXT[kind]):
            q=Question(question_id=cid+('a' if j==0 else 'b'),kind=kind,person_id=person,course=course,profile=profile,cutoff_day=p['cutoff_day'],text=phrase+f" Earlier weeks {p['baseline'][0]}–{p['baseline'][1]}; recent weeks {p['recent'][0]}–{p['recent'][1]}; information through day {p['cutoff_day']}.")
            tasks.append({'case_id':cid,'phrasing':'a' if j==0 else 'b','question':q.model_dump(),'synthetic':False})
        # Each policy occupies each serial position equally across the 24 instances.
        phrases=['a','b'] if i%2 else ['b','a']
        for j,phrase in enumerate(phrases):
            perm=permutations[(i-1)%6]
            if j: perm=tuple(reversed(perm))
            order.extend({'question_id':cid+phrase,'method':m,'case_id':cid,'position':k+1} for k,m in enumerate(perm))
    source=ROOT/'source'; source.mkdir(parents=True,exist_ok=True)
    for name in old.meta['files']: shutil.copyfile(old.source/name,source/name)
    write_json(source/'manifest.json',{**old.meta,'created_utc':now(),'excluded_reference_people':sorted(used),'historical_source_manifest_sha256':file_hash(old.source/'manifest.json'),'description':'Unmodified allowlisted development observations; fixed pool excludes all prior focal people plus 12 Stage 3 focal people across registrations.'})
    write_json(ROOT/'tasks/manifest.json',{'version':'stage3-v1','selected_utc':now(),'cases':cases,'tasks':tasks,'prior_focal_people_excluded':sorted(prior),'new_focal_people':sorted(used-prior),'reference_pool_excluded_people':sorted(used),'selection_rule':'Minimum SHA256(seed, case ID, person ID) among unused people meeting declared eligibility/prior-attempt/course/profile conditions; no activity magnitudes, outcomes or method results.','seed':cfg['selection_seed'],'paired_phrasings':'Two dependent question instances per person/case; same data, cutoff, requested answer set and reference pool. Not 24 independent people.','external_review':'Awaiting human scientific review'})
    write_json(ROOT/'protocol/execution_order.json',{'baseline':'All 24 instances on the GPU host CPU before model loading; time recorded individually.','agent_order':order,'counterbalance':'Six permutations repeated across 12 cases, reversed for the paired phrasing; a/b order alternates by case.'})
    construction=[{'question':{**t['question'],'question_id':'s3_build_'+t['question']['question_id']},'method':'coverage_aware'} for t in old_tasks if t['subset']=='construction']
    write_json(ROOT/'tasks/construction.json',{'episodes':construction,'note':'Known Stage 2 people/questions; diagnosis only, never new pilot evidence.'})
    engine=Engine(); rubrics=[]
    for t in tasks:
        q=Question.model_validate(t['question']); items=requirements(q.model_dump()); facts={}
        signatures=set()
        for item in items:
            if item['category'] in {'peer','personal','focal','direction'}:
                signatures.update((f,r) for f in item['features'] for r in item.get('references',[item.get('reference','course')]))
        for f,r in sorted(signatures):
            fact=independent_facts(engine,q,Request(question_id=q.question_id,feature=f,reference=r))
            facts[f+':'+r]={k:fact[k] for k in ['feature','unit','reference','reference_label','window','reference_window','status','people','observations','summary']}
        rubrics.append({'question_id':q.question_id,'case_id':t['case_id'],'required_answers':items,'independent_facts':facts,'admissible_alternatives':['Scoped numerical claims or supported mean-comparison charts','Validated reference conclusion or complete scoped reference comparisons','Scoped insufficient evidence only for the comparison actually unsupported','Public unavailability caveat, with compiler provenance disclosed'],'prohibited':['Causal/fairness/significance/learning claims','Treating zero clicks as complete logging or no effort','Using scores without release timestamps','A blanket insufficiency claim to excuse an answerable omitted comparison'],'external_review':'Awaiting human scientific review; separate calculation is not human review'})
    write_json(ROOT/'evaluator_only/rubrics.json',{'version':'stage3-v1','agent_visibility':'Never supplied to model, tool or policy; scorer is run only after inference.','rubrics':rubrics})
    event({'event':'tasks_selected','cases':12,'question_instances':24,'new_people':12,'manifest_sha256':file_hash(ROOT/'tasks/manifest.json')})
    print([(c['case_id'],c['person_id'],c['candidate_people']) for c in cases])

if __name__=='__main__': main()
