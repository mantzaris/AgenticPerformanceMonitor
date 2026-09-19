"""Genuine vector architecture and counts read directly from frozen reports."""
import argparse,csv,hashlib,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch,FancyBboxPatch
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'apm-predraft-v1','axes.spines.top':False,'axes.spines.right':False})
WIDTH=6.221
COLORS=['#176b72','#a9cdcb','#ebcf94','#d8dfe3']
CATEGORIES=['complete_method_selected','complete_compiler_context','accepted_incomplete','no_accepted_output']
CONDITIONS=['baseline','compact_a','derived_b','binding_c']
def read(p):return json.loads(Path(p).read_text())
def save(fig,root,name):
 out=root/'figures';out.mkdir(parents=True,exist_ok=True)
 fig.savefig(out/f'{name}.pdf',metadata={'CreationDate':None,'ModDate':None,'Creator':'AgenticPerformanceMonitor pre-draft v1'})
 fig.savefig(out/f'{name}.svg',metadata={'Date':None})
 fig.savefig(out/f'{name}.png',dpi=300)
 plt.close(fig)
def counts(root):
 path=Path('artifacts/stage6/reports/per_case.json');rows=read(path);assert len(rows)==96
 grouped={m:[0]*4 for m in CONDITIONS};derived=[]
 for r in rows:
  valid=r['valid_after_repair'];visible=valid and r['complete_requested_coverage'];selected=valid and r.get('complete_method_selected_coverage',False)
  assert not selected or visible
  if visible:assert r['complete_required_context']
  cat=0 if selected else 1 if visible else 2 if valid else 3
  grouped[r['condition']][cat]+=1
  derived.append({'condition':r['condition'],'question_id':r['question_id'],'category':CATEGORIES[cat],'valid_after_repair':valid,'complete_requested_coverage':r['complete_requested_coverage'],'complete_method_selected_coverage':r.get('complete_method_selected_coverage',False)})
 # Independent expected aggregate checks from user/review, never plot inputs.
 expected={'baseline':[24,0,0,0],'compact_a':[18,3,1,2],'derived_b':[14,1,9,0],'binding_c':[11,4,6,3]}
 assert grouped==expected,(grouped,expected)
 assert all(sum(v)==24 for v in grouped.values())
 (root/'results_categories.json').write_text(json.dumps({'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'definition':'Mutually exclusive: selected complete; otherwise visible complete; otherwise accepted; otherwise no accepted output. No rescoring.','categories':CATEGORIES,'counts':grouped,'records':derived,'caveat':'B17–20 are disputed equivalent answer forms; frozen categories preserved.'},indent=2)+'\n')
 with (root/'results_categories.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(derived[0]));w.writeheader();w.writerows(derived)
 fig=plt.figure(figsize=(WIDTH,3.35));ax=fig.add_axes([.23,.40,.745,.46]);labels=['Enumeration','A · compact','B · derived metadata','C · explicit binding']
 for j,m in enumerate(CONDITIONS):
  left=0
  for i,value in enumerate(grouped[m]):
   ax.barh(3-j,value,left=left,height=.63,color=COLORS[i],edgecolor='#506775',linewidth=.6,hatch=['','///','..','xx'][i])
   if value:ax.text(left+value/2,3-j,str(value),ha='center',va='center',color='white' if i==0 else '#192e38',fontsize=10,fontweight='bold')
   left+=value
 ax.set_yticks([3,2,1,0]);ax.set_yticklabels(labels,fontsize=9);ax.set_xlim(0,24);ax.set_xticks([0,4,8,12,16,20,24]);ax.set_xlabel('Cases (24 paired people per condition)',fontsize=9);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
 fig.text(.01,.955,'Stage 6 · frozen development results',fontsize=12,fontweight='bold',color='#192e38')
 legend=['Complete: method selections','Complete: required compiler context','Accepted, incomplete (frozen rule)','No accepted output']
 for i,label in enumerate(legend):
  x=.02+(i%2)*.5;y=.18-(i//2)*.09
  fig.patches.append(Rectangle((x,y),.025,.037,transform=fig.transFigure,facecolor=COLORS[i],edgecolor='#506775',hatch=['','///','..','xx'][i],linewidth=.6))
  fig.text(x+.036,y+.002,label,fontsize=8.5)
 fig.text(.02,.015,'Counts are exclusive; all 96 slots retained. B17–20 answer-form caveat remains pending.',fontsize=8.5,color='#506775')
 save(fig,root,'figure4')

def architecture(root):
 fig=plt.figure(figsize=(WIDTH,4.6));ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,100);ax.set_ylim(0,100);ax.axis('off')
 def box(x,y,w,h,title,lines,fill='#f3f7f7'):
  ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.25,rounding_size=1.3',facecolor=fill,edgecolor='#9ab0b7',linewidth=.8))
  ax.text(x+2,y+h-3.3,title,fontsize=9.6,weight='bold',va='top',color='#192e38')
  ax.text(x+2,y+h-7.8,'\n'.join(lines),fontsize=8.7,va='top',linespacing=1.4,color='#192e38')
 def arrow(a,b,label=None,pos=None,style='-'):
  ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=8,linewidth=.9,color='#506775',linestyle=style))
  if label:ax.text(*(pos or ((a[0]+b[0])/2,(a[1]+b[1])/2)),label,fontsize=8,ha='center',color='#506775',bbox={'facecolor':'white','edgecolor':'none','pad':.5})
 fig.text(.02,.965,'Implemented division of responsibilities',fontsize=12,weight='bold',color='#192e38')
 box(25,80,50,12,'Question + analytical context',['Feature, person, windows and cutoff'])
 box(2,58,43,16,'Agent: requests + selections',['Chooses analyses and answer content','A/B/C interfaces; no frontend code'])
 box(56,58,42,16,'Deterministic analytical tools',['Recorded measures, peers, support,','counts and peer-mean intervals'])
 arrow((40,80),(23,74));arrow((45,69),(56,69),'request',(50.5,72.2));arrow((56,61),(45,61),'result',(50.5,57.0))
 box(2,33,43,18,'Binding + numerical validation',['Returned evidence only; scope/support','checked; B/C derive metadata.','Invalid final → one repair or rejection'])
 box(56,33,42,18,'Original compiler + renderer',['Selected claims → numerical wording','Required context + fixed structure','No missing comparison added'])
 arrow((23,58),(23,51),'selection',(23,54.4));arrow((45,42),(56,42),'valid',(50.5,45.3))
 # Evidence path comes from deterministic tools; validation is rerun after compilation.
 arrow((77,58),(77,51),'evidence',(84,54.4));arrow((66,33),(35,33),None);ax.text(50,29.5,'compiled specification rechecked',fontsize=8,ha='center',color='#506775')
 box(2,9,43,14,'Saved accepted artifacts',['Spec, evidence, bound answers,','selection / compiler provenance'])
 box(56,9,42,14,'New deterministic presentation',['Semantic layout, charts, excerpts','Dashboard + evidence inspector'])
 arrow((23,33),(23,23));arrow((45,16),(56,16),'read',(50.5,19))
 arrow((2,42),(2,73),None,style='--');ax.text(4,53,'repair',fontsize=8,color='#506775')
 ax.text(56,4.2,'Saved-reference selector reads saved records only.',fontsize=8.5,color='#176b72')
 ax.text(2,.4,'Completeness: separate offline evaluator + pending human review; never an integrity guarantee.',fontsize=8.5,color='#506775')
 save(fig,root,'figure3')
 trace={'agent_loop':'src/trajectory_dashboards/stage4/agents.py:episode, reused by stage6/adapter.py','evidence':'src/trajectory_dashboards/stage2/backend.py:Engine.analyze','validation':'src/trajectory_dashboards/stage2/integrity.py:validate','binding':'src/trajectory_dashboards/stage6/binding.py:compile_selection, resolve','compiler':'src/trajectory_dashboards/stage4/semantic.py:compile_answer','original_render':'src/trajectory_dashboards/stage4/display.py:render','presentation':'src/trajectory_dashboards/predraft_v1/render.py; inherited presentation_v1/interaction.js','completeness':'src/trajectory_dashboards/stage3/evaluation.py; stage4/evaluation.py provenance projection','precision_note':'Compiler performs validation internally and episode validates again before saving; diagram groups these into a recheck edge. A retains authored scope/support. B/C derive them. Tools return evidence to the model during the iterative episode; no model runs in this preparation stage.'}
 (root/'architecture_trace.json').write_text(json.dumps(trace,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/predraft_v1');root=Path(p.parse_args().output);counts(root);architecture(root);print('Vector architecture and frozen results exported')
