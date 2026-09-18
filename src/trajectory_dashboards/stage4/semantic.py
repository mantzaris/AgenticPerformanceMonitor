"""Compile explicit answer selections, never a question-derived answer checklist.

No evaluator, task manifest, statistical dispatcher or task-ID routing is used.
The unchanged source validator runs after compilation.
"""
from typing import Literal
from pydantic import Field, model_validator
from ..contracts import Contract
from ..stage2.core import Question, Request, Specification, Evidence
from ..stage2.integrity import validate, reference_conclusion


class Intent(Contract):
    kind: Literal['peer_comparison', 'personal_change', 'assessment_status', 'observation_status', 'measurement_limit']
    evidence_id: str
    support: Literal['describe', 'insufficient_evidence'] = 'describe'


class Conclusion(Contract):
    kind: Literal['descriptive', 'same_direction', 'direction_differs', 'insufficient_evidence'] = 'descriptive'
    scope: Literal['selected', 'peer', 'personal'] = 'selected'
    evidence_ids: list[str] = Field(default_factory=list, max_length=6)


class Answer(Contract):
    answers: list[Intent] = Field(min_length=1, max_length=10)
    conclusion: Conclusion = Field(default_factory=Conclusion)


class SemanticAction(Contract):
    action: Literal['analyze', 'final']
    requests: list[Request] = Field(default_factory=list, max_length=6)
    answer: Answer | None = None

    @model_validator(mode='after')
    def shape(self):
        if self.action == 'analyze' and (not self.requests or self.answer is not None):
            raise ValueError('analyze requires 1–6 requests and no answer')
        if self.action == 'final' and (self.requests or self.answer is None):
            raise ValueError('final requires answer and no requests')
        return self


def compile_answer(engine, question, answer, evidence):
    q = Question.model_validate(question)
    answer = Answer.model_validate(answer)
    ids = list(dict.fromkeys(a.evidence_id for a in answer.answers))
    if len(ids) > 6:
        raise ValueError('Select at most six returned evidence identifiers')
    if any(eid not in evidence for eid in ids):
        raise ValueError('Unknown evidence identifier; choose only returned identifiers: ' + str(sorted(evidence)))
    bound = {eid: Evidence.model_validate(evidence[eid]) for eid in ids}
    claims, panels, claim_origins, panel_origins = [], [], [], []

    def add(where, origins, kind, eid, selected=None, reason=None):
        field = 'template' if where is claims else 'kind'
        value = {field: kind, 'evidence_id': eid}
        if value in where:
            idx = where.index(value)
            if selected is not None:
                origins[idx]['answer_indices'].append(selected)
                origins[idx]['origin'] = 'method_selected'
            return
        where.append(value)
        origins.append({'origin': 'method_selected' if selected is not None else 'compiler_supplied',
                        'answer_indices': [selected] if selected is not None else [], 'reason': reason})

    seen = set()
    for i, intent in enumerate(answer.answers):
        signature = (intent.kind, intent.evidence_id)
        if signature in seen:
            raise ValueError('Duplicate semantic answer selection; select each kind/evidence pair once')
        seen.add(signature)
        e = bound[intent.evidence_id]
        if intent.kind in {'peer_comparison', 'personal_change'}:
            supported = e.status == 'supported' if intent.kind == 'peer_comparison' else e.summary['personal_status'] == 'supported'
            expected = 'describe' if supported else 'insufficient_evidence'
            if intent.support != expected:
                raise ValueError(f'answers[{i}].support: this {intent.kind} requires {expected}; do not assert an unsupported estimate or unsupported insufficiency')
            add(claims, claim_origins, 'comparison' if intent.kind == 'peer_comparison' else 'personal_change', e.evidence_id, i)
            # A personal selection never adds a peer window-mean comparison.
            add(panels, panel_origins, 'comparison' if intent.kind == 'peer_comparison' else 'trajectory', e.evidence_id, i)
        else:
            if intent.support != 'describe':
                raise ValueError('Insufficient support belongs to a particular peer/personal comparison, not a general context intent')
            if intent.kind == 'measurement_limit':
                add(claims, claim_origins, 'measurement_limits', e.evidence_id, i)
            else:
                add(panels, panel_origins, intent.kind, e.evidence_id, i)

    conclusion = answer.conclusion
    scoped = set(conclusion.evidence_ids)
    if len(scoped) != len(conclusion.evidence_ids) or not scoped <= set(ids):
        raise ValueError('Conclusion scope must contain distinct identifiers explicitly selected in answers')
    if conclusion.kind == 'descriptive':
        if scoped or conclusion.scope != 'selected':
            raise ValueError('Descriptive conclusion uses scope=selected and empty evidence_ids')
    elif conclusion.kind in {'same_direction', 'direction_differs'}:
        peer_ids = {a.evidence_id for a in answer.answers if a.kind == 'peer_comparison'}
        if conclusion.scope != 'peer' or len(scoped) < 2 or not scoped <= peer_ids:
            raise ValueError('Reference conclusion requires scope=peer and at least two explicitly selected peer comparisons')
        if reference_conclusion([bound[eid] for eid in scoped]) != conclusion.kind:
            raise ValueError('Unsupported semantic reference conclusion for its explicit evidence scope')
    else:
        kind = {'peer': 'peer_comparison', 'personal': 'personal_change'}.get(conclusion.scope)
        allowed = {a.evidence_id for a in answer.answers if a.kind == kind and a.support == 'insufficient_evidence'}
        if not scoped or not scoped <= allowed:
            raise ValueError('Insufficiency conclusion requires a nonempty peer/personal scope with explicitly selected insufficient answers')

    # Mechanical structure is shared with the full-specification contract. These
    # additions are separately attributed and never include a comparison/change.
    if not any(p['kind'] == 'trajectory' for p in panels):
        add(panels, panel_origins, 'trajectory', ids[0], reason='common trajectory requirement')
    if not any(p['kind'] == 'observation_status' for p in panels):
        add(panels, panel_origins, 'observation_status', ids[0], reason='common observation context')
    assessment_ids = [eid for eid, e in bound.items() if e.feature in {'nonbanked_submissions', 'scheduled_no_submission'}]
    if assessment_ids and not any(p['kind'] == 'assessment_status' and p['evidence_id'] in assessment_ids for p in panels):
        add(panels, panel_origins, 'assessment_status', assessment_ids[0], reason='common assessment context')
    for eid in ids:
        if not any(c['evidence_id'] == eid for c in claims):
            add(claims, claim_origins, 'measurement_limits', eid, reason='per-evidence claim requirement; shared measurement boilerplate only')
        if not any(p['evidence_id'] == eid and p['kind'] in {'trajectory', 'comparison'} for p in panels):
            add(panels, panel_origins, 'trajectory', eid, reason='per-evidence quantitative panel requirement')
    spec = Specification(question_id=q.question_id, cutoff_day=q.cutoff_day, evidence_ids=ids,
                         claims=claims, panels=panels, conclusion=conclusion.kind, followups=[])
    # Rechecks the original global conclusion semantics as well as every source value.
    validate(engine, q, spec, evidence)
    provenance = {'interface': 'semantic', 'semantic_answer': answer.model_dump(),
                  'claims': claim_origins, 'panels': panel_origins,
                  'conclusion': {'origin': 'method_selected', **conclusion.model_dump()},
                  'additional_analyses': 0, 'inserted_comparison_or_personal_claims': 0,
                  'boilerplate': 'Standard renderer caveats; not agent investigation'}
    return spec, provenance


def full_provenance(spec, interface='full_spec'):
    spec = Specification.model_validate(spec)
    return {'interface': interface,
            'claims': [{'origin': 'method_selected', 'answer_indices': []} for _ in spec.claims],
            'panels': [{'origin': 'method_selected', 'answer_indices': []} for _ in spec.panels],
            'conclusion': {'origin': 'method_selected'}, 'additional_analyses': 0,
            'inserted_comparison_or_personal_claims': 0,
            'boilerplate': 'Standard renderer caveats; not agent investigation'}
