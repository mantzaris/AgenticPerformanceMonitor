"""All frozen slots, neutral order, blank independent forms. No scoring runs."""
import argparse,csv,hashlib,html,json,os,random
from pathlib import Path
SEED=20260919
FIELDS=['reviewer_name','reviewed_utc','each_requested_answer_present','feature_units_person_match','reference_and_windows_match','insufficiency_scoped','interpretation_justified','uncertainty_justified','equivalent_answer_form_acceptable','overall_completeness_judgment','selection_vs_compiler_attribution','comments']
def read(p):return json.loads(Path(p).read_text())
def dump(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def link(p,base):return os.path.relpath(Path(p).resolve(),base.resolve())
def page(title,body):return f'<!doctype html><html lang="en"><meta charset="utf-8"><title>{html.escape(title)}</title><style>body{{font:17px/1.5 "DejaVu Sans",sans-serif;max-width:1050px;margin:32px auto;padding:20px;color:#192e38;background:#f6f8f8}}section{{background:white;border:1px solid #dbe3e5;padding:18px;margin:18px 0}}a{{color:#176b72}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}}li{{margin:8px 0}}</style><h1>{html.escape(title)}</h1>{body}</html>'
def main(root):
 root=Path(root).resolve();out=root/'human_review';out.mkdir(parents=True,exist_ok=True)
 rows=read('artifacts/stage6/reports/per_case.json');assert len(rows)==96
 qs={t['question']['question_id']:t['question'] for t in read('artifacts/stage6/tasks/manifest.json')['tasks']}
 gold={r['question_id']:r for r in read('artifacts/stage6/evaluator_only/rubrics.json')['rubrics']}
 order=sorted(rows,key=lambda r:(r['question_id'],r['condition']));rng=random.Random(SEED);rng.shuffle(order)
 conditions=sorted({r['condition'] for r in rows});random.Random(SEED+1).shuffle(conditions);aliases={m:f'Condition {i+1}' for i,m in enumerate(conditions)}
 packet=[];mapping=[];sourcehash={};audit=[];adjudication=[]
 for i,r in enumerate(order,1):
  rid=f'R{i:03}';qid=r['question_id'];q=qs[qid];req=gold[qid]['required_answers'];case=Path(r['artifact_path']);accepted=case/'accepted';valid=r['valid_after_repair'];assert accepted.exists()==valid
  slot=out/'slots'/f'{rid}.html';slot.parent.mkdir(exist_ok=True)
  paths={'question':'artifacts/stage6/tasks/manifest.json','requirements':'artifacts/stage6/evaluator_only/rubrics.json','result':str(case/'result.json'),'tool_results':str(case/'tool_results.json')}
  if valid:
   paths.update({name:str(accepted/filename) for name,filename in [('original_dashboard','dashboard.html'),('original_spec','spec.json'),('selected_evidence','evidence.json'),('bound_answers','bound.json'),('selection_provenance','selection_provenance.json')]})
   assert read(accepted/'bound.json')['validation']=='PASS'
  for n in ['sequence.json','requests.json']:
   if (case/n).exists():paths[n.split('.')[0]]=str(case/n)
  for v in paths.values():sourcehash[v]=sha(v)
  flags=[]
  if r['condition']=='derived_b' and qid in [f's6_{j}' for j in range(17,21)]:flags.append('Recent assessment means in personal-change claims: assess equivalent answer form (B17–20 caveat).')
  if qid in ['s6_21','s6_23'] and r['condition']=='binding_c':flags.append('Separately displayed earlier/recent means versus explicit personal-change answer; C21 requires explicit adjudication.')
  if r['family'] in ['observation_limits','insufficient_support','assessment_availability']:flags.append('Unavailable-quantity form and separately scoped insufficiency.')
  flags.append('Support thresholds and reference appropriateness; equal-person weighting and observed history.')
  mapping.append({'review_id':rid,'condition_label':aliases[r['condition']],'condition':r['condition'],'question_id':qid,'source_path':str(case),'adjudication_flags':flags})
  # Initial packet includes justified requirements, never covered/origin/outcome fields.
  record={'review_id':rid,'condition_label':aliases[r['condition']],'question':q,'analytical_requirements':req,'output':'original accepted dashboard' if valid else 'no accepted dashboard','sources':paths,'review':{f:None for f in FIELDS}}
  packet.append(record)
  reqhtml=''.join('<li>'+html.escape(f"{a['category']}: {', '.join(a['features'])}; window={a['window']}"+(f"; reference={a['reference']}" if 'reference' in a else '')+f". {a['justification']}")+'</li>' for a in req)
  if valid:
   outcome=f'<a href="{link(accepted/"dashboard.html",slot.parent)}">Open complete original experimental dashboard</a>. Review the full dashboard and all its claims and panels, not the new paper excerpts.'
  else:
   result=read(case/'result.json');outcome='<b>No accepted dashboard.</b> Original rejection outcome: <pre>'+html.escape(result.get('error','See saved result and sequence.'))+'</pre>'
  sources=''.join(f'<li><a href="{link(v,slot.parent)}">{html.escape(k.replace("_"," "))}</a></li>' for k,v in paths.items() if k not in ['question','requirements','original_dashboard'])
  slot.write_text(page(f'{rid} · {aliases[r["condition"]]}',f'<p><a href="../index.html">Review order and blank forms</a></p><section><h2>Original question</h2><p>{html.escape(q["text"])}</p><p>Person {q["person_id"]} · {q["course"]} · cutoff day {q["cutoff_day"]}. Development data.</p></section><section><h2>Analytical requirements to assess</h2><ul>{reqhtml}</ul><p>These requirements are provisional and may be challenged. Credit justified equivalent answer forms; do not use a required template as the answer.</p></section><section><h2>Original output</h2><p>{outcome}</p><ul>{sources}</ul><p>Selection provenance identifies method selection versus original compiler context. Source-bound numerical validation is a separate property from completeness. All source files are unchanged.</p></section><section><h2>Independent rating</h2><p>Record your ratings for {rid} in your blank reviewer form. Do not consult automated judgments or the coordinator mapping before submitting an independent rating. Method identity may be apparent in original files; neutral labels provide only partial masking.</p><ul>'+''.join('<li>'+f.replace('_',' ').capitalize()+': __________</li>' for f in FIELDS)+'</ul></section>'))
  audit.append({'review_id':rid,'original_automated_judgment':r,'independent_facts':gold[qid]['independent_facts'],'source_checks':{'numerical_integrity':r['numerical_integrity'],'historical_verification':'artifacts/stage6/checks/final_verification.json'},'human_review_status':'PENDING'})
  adjudication.append({'review_id':rid,'reviewer_1_judgment':None,'reviewer_2_judgment':None,'disagreement':None,'adjudicated_judgment':None,'rationale':None,'adjudicator':None,'date':None})
 dump(out/'packet.json',{'status':'PENDING independent human scientific review','order_seed':SEED,'neutral_labels':'Partial masking only; original dashboards/provenance unmodified. Coordinator files are logically separated, not access controlled.','records':packet})
 for reviewer in ['reviewer_1','reviewer_2']:
  dump(out/f'{reviewer}.json',{'reviewer':None,'status':'blank','records':[{'review_id':r['review_id'],'ratings':{f:None for f in FIELDS},'requested_answers':[{'requirement_id':a['id'],'present':None,'scope_correct':None,'equivalent_form':None,'reason':None} for a in r['analytical_requirements']]} for r in packet]})
  with (out/f'{reviewer}.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=['review_id']+FIELDS);w.writeheader();w.writerows({'review_id':r['review_id'],**{x:'' for x in FIELDS}} for r in packet)
  with (out/f'{reviewer}_answers.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=['review_id','requirement_id','present','scope_correct','equivalent_form','reason']);w.writeheader();w.writerows({'review_id':r['review_id'],'requirement_id':a['id']} for r in packet for a in r['analytical_requirements'])
 dump(out/'adjudication.json',{'adjudicator':None,'records':adjudication})
 with (out/'adjudication.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(adjudication[0]));w.writeheader();w.writerows(adjudication)
 dump(out/'coordinator_private/reconciliation.json',{'seed':SEED,'mapping':mapping,'warning':'Do not distribute with initial independent rating materials. Private by review workflow, not technically secured.'})
 dump(out/'audit/automated_judgments.json',{'notice':'Separate audit; original frozen scores, not human truth. Consult only after independent ratings.','records':audit})
 dump(out/'source_manifest.json',{'files':sourcehash,'slots':96,'accepted':sum(r['valid_after_repair'] for r in rows),'rejected':sum(not r['valid_after_repair'] for r in rows),'no_rescoring':True})
 links=''.join(f'<li><a href="slots/{r["review_id"]}.html">{r["review_id"]} · {r["condition_label"]}</a></li>' for r in packet)
 (out/'index.html').write_text(page('Pending scientific review · all 96 Stage 6 slots',f'<p>Use original full experimental dashboards and questions. This package deliberately contains rejected outputs. No human ratings have been collected.</p><section><h2>Independent forms</h2><p><a href="reviewer_1.csv">Reviewer 1: slot ratings</a> · <a href="reviewer_1_answers.csv">answer-by-answer ratings</a> · <a href="reviewer_1.json">combined JSON</a></p><p><a href="reviewer_2.csv">Reviewer 2: slot ratings</a> · <a href="reviewer_2_answers.csv">answer-by-answer ratings</a> · <a href="reviewer_2.json">combined JSON</a></p><p>Save completed copies elsewhere; preserve these blanks. Assess answer presence, feature/units/person/reference/windows, insufficiency scope, interpretation, uncertainty, and supported equivalent forms. Challenge unjustified requirements. Source-bound numerical checks are separate from your scientific judgment.</p></section><section><h2>Reproducibly randomized order</h2><ol>{links}</ol></section><details><summary>Coordinator / separate audit (after independent ratings)</summary><p><a href="coordinator_private/reconciliation.json">Private reconciliation and required adjudication flags</a> · <a href="audit/automated_judgments.json">Preserved automated judgments and independent calculation facts</a> · <a href="adjudication.csv">Blank adjudication CSV</a> · <a href="adjudication.json">Blank adjudication JSON</a></p><p>Explicitly adjudicate B17–20 recent means inside personal claims; separate earlier/recent means versus a personal-change answer (including C21); unavailable-quantity forms; support thresholds and reference appropriateness. No frozen scores change here. A later adjudicated analysis must be separately versioned and labeled post hoc.</p></details>'))
 print('Prepared',len(packet),'slots, two blank independent forms and blank adjudication')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');main(p.parse_args().output)
