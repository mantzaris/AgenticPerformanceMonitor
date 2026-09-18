"""Bounded development-only raw-source check, exact-row sensitivity and one fit retry."""
import copy,time,warnings,signal
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from trajectory_dashboards.acquire import connection
from trajectory_dashboards.common import read_json,write_json,file_hash,digest,now
from trajectory_dashboards.stage2.core import ROOT,Question,Request,append_event
from trajectory_dashboards.stage2.backend import Engine,compact


def data_checks():
    engine=Engine();w=engine.weekly;db=connection()
    selected=w[['person_id','course']].drop_duplicates().copy()
    selected['code_module']=selected.course.str.split('_').str[0]
    selected['code_presentation']=selected.course.str.split('_').str[1]
    selected=selected.rename(columns={'person_id':'id_student'})
    db.register('selected',selected)
    # This join is many-to-one by audited registration key, checked again below.
    a=db.execute('''SELECT v.*,r.date_registration,r.date_unregistration
        FROM studentVle v JOIN selected s USING(code_module,code_presentation,id_student)
        JOIN studentRegistration r USING(code_module,code_presentation,id_student)
        WHERE v.date BETWEEN 0 AND 83''').df()
    a=a[(a.date>=a.date_registration) & (a.date_unregistration.isna() | (a.date<a.date_unregistration))].copy()
    a['course']=a.code_module+'_'+a.code_presentation;a['week']=a.date//7
    assert len(a)==int(w.source_activity_rows.sum())
    assert not selected.duplicated(['code_module','code_presentation','id_student']).any()
    db.register('eligible_source_rows',a)
    tasklist=[t for t in read_json(ROOT/'tasks/manifest.json')['tasks'] if t['subset']=='construction']
    checks=[]
    for task in tasklist:
        q=Question.model_validate(task['question'])
        rows=w[w.person_id.eq(q.person_id)&w.course.eq(q.course)&w.end_day.le(q.cutoff_day)]
        for r in rows.itertuples():
            # Independent raw SQL sums/distinct counts, without build_weekly or Engine.analyze.
            raw=db.execute('''SELECT coalesce(sum(sum_click),0),count(DISTINCT CASE WHEN sum_click>0 THEN date END),count(DISTINCT id_site),count(*) FROM eligible_source_rows WHERE id_student=? AND course=? AND week=?''',[q.person_id,q.course,r.week]).fetchone()
            if r.eligible_days>0:
                assert np.isclose(float(raw[0])/r.eligible_days,r.clicks_per_eligible_day)
                assert raw[1]==r.active_days and raw[2]==r.distinct_resources and raw[3]==r.source_activity_rows
            else:assert pd.isna(r.clicks_per_eligible_day)
            checks.append({'task_id':q.question_id,'week':r.week,'raw_click_sum':int(raw[0]),'raw_active_days':int(raw[1]),'raw_resources':int(raw[2]),'source_rows':int(raw[3]),'eligible_days':None if pd.isna(r.eligible_days) else float(r.eligible_days),'prepared_rate':None if pd.isna(r.clicks_per_eligible_day) else float(r.clicks_per_eligible_day),'status':'PASS'})
    write_json(ROOT/'statistics/raw_source_checks.json',{'executed_utc':now(),'scope':'Six construction focal people, complete weeks through their cutoff; no pilot outcome inspection','eligible_source_rows':len(a),'join_count_matches_prepared':True,'checks':checks})
    key=['code_module','code_presentation','id_student','id_site','date','sum_click']
    dedup=a.drop_duplicates(key)
    counts=dedup.groupby(['id_student','course','week']).sum_click.sum().rename('dedup_clicks').reset_index().rename(columns={'id_student':'person_id'})
    alt=w.merge(counts,on=['person_id','course','week'],how='left',validate='one_to_one')
    alt['clicks']=alt.dedup_clicks.fillna(0).where(alt.eligible_days.gt(0))
    alt['clicks_per_eligible_day']=alt.clicks/alt.eligible_days.replace(0,np.nan)
    alt=alt.drop(columns='dedup_clicks')
    source=ROOT/'statistics/exact_row_sensitivity_source';source.mkdir(parents=True,exist_ok=True)
    alt.to_parquet(source/'weekly.parquet',index=False)
    engine.assessments.to_parquet(source/'assessment_status.parquet',index=False)
    meta=copy.deepcopy(engine.meta);meta.update(files={p.name:file_hash(p) for p in source.glob('*.parquet')},version='exact-row-deduplication sensitivity; not a correction',primary_source_sha256=digest(engine.meta))
    write_json(source/'manifest.json',meta)
    alternate=Engine(source=source)
    primary_results=[];alternate_results=[]
    for task in tasklist:
        q=Question.model_validate(task['question'])
        for ref in engine.cfg['references']:
            req=Request(question_id=q.question_id,feature='clicks_per_eligible_day',reference=ref)
            for eng,target in [(engine,primary_results),(alternate,alternate_results)]:
                ev=eng.analyze(q,req)
                target.append({'question_id':q.question_id,**compact(ev),'trajectory':ev.trajectory,'source_bundle_sha256':digest(eng.meta)})
    write_json(ROOT/'statistics/preserve_source_rows.json',primary_results)
    write_json(ROOT/'statistics/drop_exact_source_rows.json',alternate_results)
    write_json(ROOT/'statistics/sensitivity.json',{'executed_utc':now(),'scope':'Six construction examples, three references each; source-row sums remain the primary choice','source_rows':len(a),'exact_duplicate_excess':len(a)-len(dedup),'primary':'preserve_source_rows.json','alternative':'drop_exact_source_rows.json','limitation':'Exact equal source rows can represent repeated contributions, not necessarily ingestion errors. Neither interpretation proves unique click events.','contrasts':[{'question_id':p['question_id'],'reference':p['reference'],'primary':p['summary']['contrast'],'alternative':d['summary']['contrast'],'supported':p['status'],'direction_changed':None if p['summary']['contrast'] is None else (np.sign(p['summary']['contrast'])!=np.sign(d['summary']['contrast'])).item()} for p,d in zip(primary_results,alternate_results)]})
    append_event({'event':'raw_and_duplicate_checks_completed','checked_weeks':len(checks),'construction_contrasts':len(primary_results)})


def mixed_diagnostic():
    engine=Engine()
    # Match original failure's cohort, rather than silently change the fitting sample.
    original=[q['person_id'] for q in read_json('artifacts/data/questions.json')]
    w=engine.weekly[engine.weekly.course.eq('AAA_2013J') & ~engine.weekly.person_id.isin(original) & engine.weekly.clicks_per_eligible_day.notna()].copy()
    w['log_rate']=np.log1p(w.clicks_per_eligible_day)
    model=smf.mixedlm('log_rate ~ C(week)',w,groups=w.person_id,re_formula='1')
    result={'started_utc':now(),'historical_result':read_json('artifacts/statistics/mixed_models.json')[0],'diagnostic_only':True,'design_shape':list(model.exog.shape),'design_rank':int(np.linalg.matrix_rank(model.exog)),'design_condition_number':float(np.linalg.cond(model.exog)),'between_person_mean_variance':float(w.groupby('person_id').log_rate.mean().var()),'mean_within_person_variance':float(w.groupby('person_id').log_rate.var().mean()),'retry_method':'powell','maxiter':100,'timeout_seconds':90,'attempts':1,'dashboard_use':False}
    def timeout(*args):raise TimeoutError('Bounded 90-second diagnostic deadline')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(90)
    start=time.monotonic()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            fit=model.fit(reml=True,method='powell',maxiter=100,disp=False)
            result.update(status='converged' if fit.converged else 'not_converged',random_intercept_variance=float(fit.cov_re.iloc[0,0]),residual_variance=float(fit.scale),log_likelihood=float(fit.llf),fixed_effects={k:float(v) for k,v in fit.fe_params.items()})
        except Exception as exc:result.update(status='failed',error=f'{type(exc).__name__}: {exc}')
    signal.alarm(0)
    result.update(elapsed_seconds=time.monotonic()-start,completed_utc=now(),warnings=[str(x.message) for x in caught],interpretation='Full-rank fixed-effects design rules out simple fixed-column collinearity. The original singular random covariance warning is consistent with an optimizer/boundary path failure, but the exact numerical path was not reconstructed. An alternative converged variance would not validate the working model assumptions or an individual detector.')
    write_json(ROOT/'statistics/mixed_model_diagnostic.json',result)
    append_event({'event':'mixed_model_diagnostic_completed','status':result['status'],'elapsed_seconds':result['elapsed_seconds'],'attempts':1})

if __name__=='__main__':
    data_checks();mixed_diagnostic();print('Raw source checks, construction sensitivity and bounded mixed-model diagnostic saved.')
