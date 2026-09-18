"""Offline review material; never imported by inference, tools or compilers."""
from trajectory_dashboards.common import read_json,write_json,now
from trajectory_dashboards.stage6.core import ROOT


def main():
    target=ROOT/'human_review/packet.json'
    if target.exists():raise ValueError('Preserve original review packet')
    tasks={t['question']['question_id']:t['question'] for t in read_json(ROOT/'tasks/manifest.json')['tasks']}
    gold={r['question_id']:r for r in read_json(ROOT/'evaluator_only/rubrics.json')['rubrics']}
    rows={(r['question_id'],r['condition']):r for r in read_json(ROOT/'reports/per_case.json')}
    records=[]
    for r in read_json(ROOT/'inspection/browser.json')['records']:
        key=(r['question_id'],r['method']);case=ROOT/'comparison'/r['method']/r['question_id'];a=case/'accepted'
        records.append({'question':tasks[key[0]],'condition':key[1],'required_answers':gold[key[0]]['required_answers'],
            'independent_facts':gold[key[0]]['independent_facts'],'automated_score':rows[key],
            'tool_results_path':str(case/'tool_results.json'),'sequence_path':str(case/'sequence.json'),
            'selected_evidence':read_json(a/'evidence.json') if a.exists() else None,
            'rendered_answers':read_json(a/'bound.json') if a.exists() else None,
            'selection_provenance':read_json(a/'selection_provenance.json') if a.exists() else None,
            'dashboard_path':str(a/'dashboard.html') if a.exists() else None,'screenshot_path':r.get('screenshot'),
            'reviewer':None,'reviewed_utc':None,'human_findings':None})
    write_json(target,{'created_utc':now(),'human_review_status':'PENDING; automated and Codex checks are not independent human review',
        'selection':'First case in every family, all conditions, plus first valid-incomplete and rejected per agent; no attractiveness filtering',
        'interpretation_questions':[
            'Does each requirement follow from the actual wording, and are equivalent supported answer forms credited?',
            'Are the earlier/recent windows and same-time versus earlier-stage references understandable and scientifically defensible?',
            'For each comparison, is support or insufficiency scoped separately to its feature, window and peer/personal meaning?',
            'Do unavailable grades and unknown logging completeness remain distinct from sample-size insufficiency and zero recorded activity?',
            'Does every displayed quantitative answer match the selected evidence and its units, denominators and interval interpretation?',
            'Did any compiler context answer a substantive request that the model did not select? Is that distinction sufficiently visible?',
            'Do duplicate panels or generic caveats obscure the requested answers, and what would a user reasonably conclude?',
            'Are the descriptive development findings strong enough to justify final validation, and what claim remains unsupported?'],
        'records':records})
    print(target)


if __name__=='__main__':main()
