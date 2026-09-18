"""Visible answer semantics, separate from the unchanged source integrity validator.

No agent imports this module or receives the resulting requirements/facts.
"""
from pathlib import Path
from ..common import read_json

ACTIVITY = ['clicks_per_eligible_day', 'active_days', 'distinct_resources']
REFS = ['course', 'same_prior_attempt', 'early_stage']


def requirements(q, historical=False):
    """Every item includes its question-level justification; no panel-count reward."""
    kind = q['kind']
    features = ACTIVITY if historical else ['clicks_per_eligible_day']
    items = []

    def add(name, category, wording, **kw):
        items.append(dict(id=name, category=category, justification=wording,
                          features=features, window='recent', **kw))

    if kind in {'personal_change', 'insufficient_support', 'alternate_windows'}:
        add('personal_change', 'personal', 'Question explicitly requests comparison with own earlier history.')
    if kind in {'personal_change', 'insufficient_support'}:
        add('course_comparison', 'peer', 'Question requests a recent comparison with peers; shared bare-peers definition is presentation peers.', reference='course')
    if kind in {'reference_sensitivity', 'alternate_windows'}:
        if not historical or kind == 'alternate_windows':
            for ref in REFS:
                add('peer_' + ref, 'peer', 'Question requests these peer comparisons (Stage 3 explicitly asks to show each).', reference=ref)
        add('reference_direction', 'direction', 'Question asks whether interpretation/direction differs across the three stated peer definitions.', references=REFS)
    if kind == 'observation_limits':
        add('recent_activity', 'focal', 'Question asks what the recent recorded activity can establish.')
        add('eligibility_states', 'observation', 'Question explicitly mentions administrative eligibility and incomplete observations.')
    if kind in {'observation_limits', 'assessment_availability'}:
        if historical and kind == 'observation_limits':
            add('assessment_records', 'assessment_records', 'Historical wording asks about assessment records, without prescribing two numeric features.')
        else:
            for f in ['nonbanked_submissions', 'scheduled_no_submission']:
                item = dict(id=f, category='focal', features=[f], window='recent',
                            justification='Question explicitly asks about recorded submissions and scheduled non-submissions; Stage 3 asks their observed-week means.')
                items.append(item)
            add('assessment_records', 'assessment_records', 'Assessment state/timestamp context is an explicit shared interpretation requirement for these measurement questions.')
        add('measurement_availability', 'availability', 'Question asks what records establish / whether marks or learning can be inferred; shared interpretation rules require withholding unavailable grades.')
    return items


def _d(e):
    return e.model_dump() if hasattr(e, 'model_dump') else e


def _matching(e, item):
    return (e['feature'] in item['features'] and (item['category']=='personal' or e['request']['window'] == item['window'])
            and (item.get('reference') is None or e['reference'] == item['reference']))


def unsupported_scopes(evidence):
    scopes = set()
    for e in evidence.values():
        e = _d(e)
        if e['status'] != 'supported':
            scopes.add(('peer', e['feature'], e['reference'], tuple(e['window']), tuple(e['reference_window'])))
        if e['summary']['personal_status'] != 'supported':
            scopes.add(('personal', e['feature'], tuple(e['summary']['baseline_window']), tuple(e['summary']['recent_window'])))
    return scopes


def assess_item(item, spec, evidence, compiler_context=True):
    """Equivalent forms require appropriate scope and actual displayed content.

    Inputs have passed independent numerical integrity. Selection alone is not an
    answer. A supported comparison bar chart is a visible comparison; a trajectory
    is not a mean over a requested multi-week window. Inspector-only numbers do
    not count as a displayed answer.
    """
    evidence = {k: _d(v) for k, v in evidence.items() if k in spec.get('evidence_ids', [])}
    matches = [(k, e) for k, e in evidence.items() if _matching(e, item)]
    category = item['category']
    claims = {(c['template'], c['evidence_id']) for c in spec.get('claims', [])}
    panels = {(p['kind'], p['evidence_id']) for p in spec.get('panels', [])}
    result = dict(covered=False, origin=None, form=None, evidence_ids=[], outcome='unanswered')

    def yes(form, ids, outcome='answered', origin='method_selected'):
        return dict(covered=True, origin=origin, form=form, evidence_ids=list(ids), outcome=outcome)

    if category == 'availability':
        ids = [eid for t, eid in claims if t == 'measurement_limits']
        if ids:
            return yes('selected measurement-limits claim', ids, 'unavailable_measurement')
        if compiler_context:
            return yes('standard visible compiler caveat', [], 'unavailable_measurement', 'compiler_supplied')
    if category == 'observation':
        ids = [eid for t, eid in panels if t == 'observation_status']
        if ids:
            return yes('administrative/recorded-state panel', ids)
    if category == 'assessment_records':
        ids = [eid for t, eid in panels if t == 'assessment_status']
        if ids:
            return yes('dated assessment-state panel', ids)
    if category == 'direction':
        for feature in item['features']:
            selected = {e['reference']: (eid, e) for eid, e in matches if e['feature'] == feature}
            if not set(item['references']).issubset(selected):
                continue
            records = [selected[r] for r in item['references']]
            if all(e['status'] == 'supported' for _, e in records) and spec.get('conclusion') in {'same_direction', 'direction_differs'}:
                return yes('validated cross-reference conclusion', [eid for eid, _ in records])
            details = [assess_item({**item, 'category': 'peer', 'features': [feature], 'reference': r}, spec, evidence, compiler_context) for r in item['references']]
            if all(d['covered'] for d in details):
                return yes('complete scoped comparisons allow the descriptive answer without a mandatory conclusion template', [eid for eid, _ in records], 'insufficient_evidence' if any(e['status'] != 'supported' for _, e in records) else 'answered')
        return result
    for eid, e in matches:
        if category == 'personal' and ('personal_change', eid) in claims:
            return yes('scoped personal-history claim', [eid], 'answered' if e['summary']['personal_status'] == 'supported' else 'insufficient_evidence')
        if category == 'peer':
            if ('comparison', eid) in claims:
                return yes('scoped comparison claim', [eid], 'answered' if e['status'] == 'supported' else 'insufficient_evidence')
            if e['status'] == 'supported' and ('comparison', eid) in panels:
                return yes('supported focal/reference mean chart', [eid])
        if category == 'focal':
            # Unsupported comparison claims contain counts, not focal means. A
            # comparison chart still exposes an observed mean or unavailable bar.
            if ('comparison', eid) in panels or (('comparison', eid) in claims and e['status'] == 'supported'):
                return yes('visible focal mean with window/unit (null means unavailable)', [eid], 'unavailable_measurement' if e['summary']['focal_mean'] is None else 'answered')
        if category in {'personal', 'peer'} and spec.get('conclusion') == 'insufficient_evidence':
            scopes = unsupported_scopes(evidence)
            target = (('peer', e['feature'], e['reference'], tuple(e['window']), tuple(e['reference_window'])) if category == 'peer' else
                      ('personal', e['feature'], tuple(e['summary']['baseline_window']), tuple(e['summary']['recent_window'])))
            # A general existential statement resolves a comparison only when its
            # referent is unique. Otherwise credit it as a global finding below.
            if scopes == {target}:
                return yes('unambiguous supported insufficiency conclusion', [eid], 'insufficient_evidence')
    return result


def _retrieved(item, records):
    if item['category'] == 'availability':
        return True  # This is public measurement metadata, not a missing tool.
    if item['category'] in {'observation', 'assessment_records'}:
        return bool(records)
    matches = [e for e in records.values() if _matching(e, item)]
    if item['category'] == 'direction':
        return any(set(item['references']).issubset({e['reference'] for e in matches if e['feature'] == f}) for f in item['features'])
    return bool(matches)


def evaluate(q, spec, selected, retrieved, *, valid=True, historical=False, compiler_context=True):
    selected = {k: _d(e) for k, e in selected.items()}
    retrieved = {k: _d(e) for k, e in retrieved.items()}
    items = requirements(q, historical)
    checks = []
    for item in items:
        answer = assess_item(item, spec, selected, compiler_context) if valid else dict(covered=False, origin=None, form=None, evidence_ids=[], outcome='no_accepted_dashboard')
        available = _retrieved(item, retrieved)
        checks.append({**item, **answer, 'relevant_evidence_retrieved': available,
                       'omission_type': None if answer['covered'] else ('retrieved_but_omitted' if available else 'requested_analysis_missing')})
    templates = [c['template'] for c in spec.get('claims', [])] if valid else []
    contexts = {
        'source_validated_units_windows_counts_intervals': valid,
        'observation_status_visible': valid and any(p['kind'] == 'observation_status' for p in spec.get('panels', [])),
        'logging_and_measurement_caveats_visible': valid and compiler_context,
    }
    signatures = [(p['kind'], selected[p['evidence_id']]['feature'], selected[p['evidence_id']]['reference'], selected[p['evidence_id']]['request']['window']) for p in spec.get('panels', [])] if valid else []
    global_supported = valid and spec.get('conclusion') == 'insufficient_evidence' and bool(unsupported_scopes(selected))
    return dict(question_id=q['question_id'], requested_answers=checks,
                complete_requested_coverage=valid and all(c['covered'] for c in checks),
                complete_method_selected_coverage=valid and all(c['covered'] and c['origin']=='method_selected' for c in checks),
                answer_fraction=sum(c['covered'] for c in checks)/len(checks),
                method_selected_fraction=sum(c['covered'] and c['origin']=='method_selected' for c in checks)/len(checks),
                missing_requested_analyses=[c['id'] for c in checks if c['omission_type']=='requested_analysis_missing'],
                retrieved_but_omitted=[c['id'] for c in checks if c['omission_type']=='retrieved_but_omitted'],
                required_context=contexts, complete_required_context=all(contexts.values()),
                global_supported_insufficiency=bool(global_supported),
                global_insufficiency_scope_count=len(unsupported_scopes(selected)) if global_supported else 0,
                scoped_insufficiency_items=[c['id'] for c in checks if c['outcome']=='insufficient_evidence'],
                compiler_supplied_answers=[c['id'] for c in checks if c['origin']=='compiler_supplied'],
                optional={'personal_history_selected_but_not_requested': 'personal_change' in templates and not any(i['category']=='personal' for i in items),
                          'selected_evidence_count': len(selected), 'repeated_panel_signatures':len(signatures)-len(set(signatures))},
                external_review='Awaiting independent human scientific review; executable checks are not human review')


def score_case(q, case, historical=False):
    case = Path(case)
    result = read_json(case/'result.json') if (case/'result.json').exists() else {'status':'not_attempted', 'first_attempt_valid':False}
    valid = result['status'] in {'agent_generated_and_accepted', 'agent_generated_and_repaired', 'deterministic_accepted'}
    accepted = case/'accepted'
    spec = read_json(accepted/'spec.json') if valid else {}
    evidence = read_json(accepted/'evidence.json') if valid else {}
    retrieved = read_json(case/'tool_results.json') if (case/'tool_results.json').exists() else evidence
    return {**result, **evaluate(q, spec, evidence, retrieved, valid=valid, historical=historical),
            'valid_after_permitted_repair':valid, 'numerical_integrity':'PASS' if valid else 'NO ACCEPTED OUTPUT'}
