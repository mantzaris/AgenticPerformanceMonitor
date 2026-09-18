"""The existing structural selector, with a fresh seed and all earlier people excluded."""
import shutil
from trajectory_dashboards.common import read_json, write_json, file_hash, digest, now
from trajectory_dashboards.stage2.core import Question, Request
from trajectory_dashboards.stage2.integrity import independent_facts
from trajectory_dashboards.stage3.evaluation import requirements
from trajectory_dashboards.stage4.core import Engine as PreviousEngine
from trajectory_dashboards.stage5.core import ROOT, Engine, event


def main():
    if (ROOT / 'tasks/manifest.json').exists():
        raise ValueError('Preserve selected tasks')
    cfg = read_json('configs/stage5.json')
    previous = read_json('artifacts/stage4/tasks/manifest.json')
    old = PreviousEngine()
    prior = set(previous['reference_pool_excluded_people'])
    used = set(prior)
    cases, tasks, order = [], [], []
    for i, slot in enumerate(previous['cases'], 1):
        cid = f's5_{i:02d}'
        kind, course, profile, criterion = (slot[k] for k in ['family', 'course', 'profile', 'criterion'])
        p = cfg['profiles'][profile]
        rows = old.weekly[old.weekly.course.eq(course) & old.weekly.end_day.le(p['cutoff_day'])]
        pool = []
        for person, g in rows.groupby('person_id'):
            if person in used:
                continue
            n = int(g.eligible_days.gt(0).sum())
            recent = int(g[g.week.between(*p['recent'])].eligible_days.gt(0).sum())
            earlier = int(g[g.week.between(*p['baseline'])].eligible_days.gt(0).sum())
            ok = n >= len(g) - 1 and min(recent, earlier) >= 2
            if criterion == 'partial':
                ok = 1 <= n < len(g) - 1
            if criterion == 'insufficient':
                ok = recent < 2 and earlier >= 1
            if criterion in {'repeat', 'first'}:
                ok = ok and g.prior_attempt_group.iloc[0] == criterion + '_attempt'
            if ok:
                pool.append(int(person))
        if not pool:
            raise ValueError('No structural candidates: ' + cid)
        person = min(pool, key=lambda x: digest([cfg['selection_seed'], cid, x]))
        used.add(person)
        old_q = next(t['question'] for t in previous['tasks'] if t['case_id'] == slot['case_id'])
        q = {**old_q, 'question_id': cid, 'person_id': person}
        cases.append(dict(case_id=cid, person_id=person, family=kind, course=course, profile=profile,
                          criterion=criterion, candidate_people=len(pool), synthetic=False))
        tasks.append({'case_id': cid, 'question': q, 'synthetic': False})
        pair = ['full_spec', 'semantic'] if i % 2 else ['semantic', 'full_spec']
        for model in cfg['model_order']:
            order.extend({'question_id': cid, 'model_key': model, 'interface': interface,
                          'condition': model + '_' + interface, 'within_case_position': j + 1}
                         for j, interface in enumerate(pair))
    source = ROOT / 'source'
    source.mkdir(parents=True, exist_ok=True)
    for name in old.meta['files']:
        shutil.copyfile(old.source / name, source / name)
    write_json(source / 'manifest.json', {**old.meta, 'created_utc': now(), 'excluded_reference_people': sorted(used),
               'historical_source_manifest_sha256': file_hash(old.source / 'manifest.json'),
               'description': 'Unmodified development features; reference pool excludes all 45 earlier and 12 new Stage 5 focal people across registrations.'})
    write_json(ROOT / 'tasks/manifest.json', {'version': 'stage5-v1', 'selected_utc': now(), 'cases': cases, 'tasks': tasks,
               'prior_focal_people_excluded': sorted(prior), 'new_focal_people': sorted(used - prior),
               'reference_pool_excluded_people': sorted(used), 'seed': cfg['selection_seed'],
               'selection_rule': previous['selection_rule'].replace('Stage 4', 'Stage 5'),
               'design': '12 fresh development people; one question each, two per established family; not held-out evaluation.',
               'external_review': 'Awaiting independent human scientific review'})
    ordered = [r for model in cfg['model_order'] for r in order if r['model_key'] == model]
    write_json(ROOT / 'protocol/execution_order.json', {'baseline': 'All twelve on GPU-host CPU before model comparison',
               'model_blocks': cfg['model_order'], 'agent_order': ordered,
               'counterbalance': 'Within each checkpoint, full first for odd cases, compact for even; six first positions each. Checkpoint blocks are 7B then 14B; timing is descriptive.'})
    engine = Engine()
    rubrics = []
    for task in tasks:
        q = Question.model_validate(task['question'])
        items = requirements(q.model_dump())
        signatures, facts = set(), {}
        for item in items:
            if item['category'] in {'peer', 'personal', 'focal', 'direction'}:
                signatures.update((f, r) for f in item['features'] for r in item.get('references', [item.get('reference', 'course')]))
        for f, r in sorted(signatures):
            fact = independent_facts(engine, q, Request(question_id=q.question_id, feature=f, reference=r))
            facts[f + ':' + r] = {k: fact[k] for k in ['feature', 'unit', 'reference', 'reference_label', 'window', 'reference_window', 'status', 'people', 'observations', 'summary']}
        rubrics.append({'question_id': q.question_id, 'required_answers': items, 'independent_facts': facts,
                        'external_review': 'Separate row-loop calculations, not independent human review'})
    write_json(ROOT / 'evaluator_only/rubrics.json', {'version': 'Unchanged Stage 3/4 scoring semantics',
               'agent_visibility': 'Never supplied to policy, tools, compiler or model', 'rubrics': rubrics})
    event({'event': 'tasks_selected', 'new_people': 12, 'questions': 12, 'manifest_sha256': file_hash(ROOT / 'tasks/manifest.json')})
    print([(c['case_id'], c['person_id'], c['candidate_people']) for c in cases])


if __name__ == '__main__':
    main()
