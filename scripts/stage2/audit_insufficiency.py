"""Post-hoc display audit of a frozen scoring defect; never replaces primary scores."""
from pathlib import Path
from trajectory_dashboards.common import read_json,write_json,now
from trajectory_dashboards.stage2.core import ROOT


def main():
    audit=[]
    for r in read_json(ROOT/'reports/pilot_per_task.json'):
        if not r['insufficient_expected']:continue
        case=ROOT/'pilot'/r['method']/r['task_id']/'accepted'
        entry={'task_id':r['task_id'],'method':r['method'],'frozen_appropriate_insufficiency_flag':r['appropriate_insufficiency'],'accepted_output':case.exists(),'displayed_supported_insufficiency_conclusion':False,'displayed_insufficiency_claim':False}
        if case.exists():
            s=read_json(case/'spec.json');b=read_json(case/'bound.json');e=read_json(case/'evidence.json')
            entry.update(conclusion=s['conclusion'],displayed_conclusion=b['conclusion'],claim_templates=[c['template'] for c in s['claims']],displayed_claims=[c['text'] for c in b['claims']],evidence_has_insufficient_support=any(x['status']=='insufficient_evidence' or x['summary']['personal_status']=='insufficient_evidence' for x in e.values()))
            entry['displayed_supported_insufficiency_conclusion']=s['conclusion']=='insufficient_evidence' and entry['evidence_has_insufficient_support']
            entry['displayed_insufficiency_claim']=any('Insufficient' in c['text'] for c in b['claims'])
        audit.append(entry)
    summary=[{'method':m,'denominator':sum(r['method']==m for r in audit),'frozen_flag_count':sum(bool(r['frozen_appropriate_insufficiency_flag']) for r in audit if r['method']==m),'displayed_supported_insufficiency_count':sum(r['displayed_supported_insufficiency_conclusion'] or r['displayed_insufficiency_claim'] for r in audit if r['method']==m)} for m in ['baseline','generic','reference_sensitive']]
    write_json(ROOT/'reports/insufficiency_display_audit.json',{'created_utc':now(),'status':'POST-HOC SCORING AUDIT, not a replacement primary metric','reason':'Frozen score() requires a comparison/personal_change claim template and ignores the admissible insufficient_evidence conclusion. Four reference-sensitive outputs have a supported explicit insufficient-evidence conclusion but only measurement_limits claim templates.','frozen_scores_changed':False,'outputs_changed':False,'pilot_rerun':False,'requires_external_review':True,'summary':summary,'cases':audit})
    print(summary)

if __name__=='__main__':main()
