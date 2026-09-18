"""Returned-evidence identities, derived metadata, and explicit selection only.

No evaluator, task-kind routing, question-text parser, or analytical dispatcher.
The public question supplies person/course/cutoff context, never required answers.
"""
from typing import Literal
from pydantic import Field, model_validator
from ..contracts import Contract
from ..common import digest
from ..stage2.core import Question, Request, Evidence
from ..stage2.integrity import validate_evidence
from ..stage4.semantic import compile_answer as historical_compile

Kind = Literal['peer_comparison', 'personal_change', 'assessment_status', 'observation_status', 'measurement_limit']
KINDS = ('peer_comparison', 'personal_change', 'assessment_status', 'observation_status', 'measurement_limit')


class DerivedSelection(Contract):
    kind: Kind
    evidence_id: str


class BindingSelection(Contract):
    identity: str = Field(min_length=1, max_length=700)


class DerivedAnswer(Contract):
    answers: list[DerivedSelection] = Field(min_length=1, max_length=10)


class BindingAnswer(Contract):
    answers: list[BindingSelection] = Field(min_length=1, max_length=10)


class DerivedAction(Contract):
    action: Literal['analyze', 'final']
    requests: list[Request] = Field(default_factory=list, max_length=6)
    answers: list[DerivedSelection] = Field(default_factory=list, max_length=10)

    @model_validator(mode='after')
    def shape(self):
        if self.action == 'analyze' and (not self.requests or self.answers):
            raise ValueError('analyze requires requests and no answers')
        if self.action == 'final' and (self.requests or not self.answers):
            raise ValueError('final requires answers and no requests')
        return self

    @property
    def answer(self):
        return DerivedAnswer(answers=self.answers)


class BindingAction(DerivedAction):
    answers: list[BindingSelection] = Field(default_factory=list, max_length=10)

    @property
    def answer(self):
        return BindingAnswer(answers=self.answers)


def identity(question, evidence, kind):
    """Canonical human-readable handle; no task ID or requested-answer checklist."""
    q, e = Question.model_validate(question), Evidence.model_validate(evidence)
    if kind not in KINDS:
        raise ValueError('Unknown answer kind')
    base = f'{kind}|person={e.focal_id}|course={q.course}|cutoff={e.cutoff_day}|feature={e.feature}'
    if kind == 'personal_change':
        a, b = e.summary['baseline_window'], e.summary['recent_window']
        return base + f'|earlier={a[0]}:{a[1]}|recent={b[0]}:{b[1]}'
    # Context selections identify their source record as well; only personal
    # meaning explicitly removes the irrelevant reference population.
    a, b = e.window, e.reference_window
    return base + f'|focal={a[0]}:{a[1]}|reference={e.reference}|reference_window={b[0]}:{b[1]}'


def derived(e, kind):
    e = Evidence.model_validate(e)
    if kind == 'peer_comparison':
        status, scope = e.status, 'peer'
    elif kind == 'personal_change':
        status, scope = e.summary['personal_status'], 'personal'
    else:
        # Unknown grade availability is a measurement limitation regardless of
        # the sample size/support of the record used to select its context.
        return {'support': 'describe', 'scope': 'measurement' if kind == 'measurement_limit' else 'context',
                'answer_state': 'unavailable_measurement' if kind == 'measurement_limit' else 'recorded_context'}
    return {'support': 'describe' if status == 'supported' else 'insufficient_evidence',
            'scope': scope, 'answer_state': 'answered' if status == 'supported' else 'supported_insufficiency'}


def catalogue(question, evidence):
    """Same catalogue for B and C, generated solely from returned records."""
    return [{'identity': identity(question, evidence, k), 'kind': k,
             'evidence_id': Evidence.model_validate(evidence).evidence_id,
             'derived_metadata': derived(evidence, k)} for k in KINDS]


def personal_signature(e):
    e = Evidence.model_validate(e)
    names = ('baseline_window', 'recent_window', 'baseline_mean', 'recent_mean',
             'baseline_observations', 'recent_observations', 'personal_change', 'personal_status')
    return digest({'feature': e.feature, 'unit': e.unit, 'focal_id': e.focal_id,
                   'cutoff_day': e.cutoff_day, 'summary': {k: e.summary[k] for k in names}})


def resolve(question, handle, records):
    matches = [(eid, kind, e) for eid, e in records.items() for kind in KINDS
               if identity(question, e, kind) == handle]
    if not matches:
        raise ValueError('Unresolved binding: unknown or mismatched feature/window/reference/scope identity; copy an exact returned catalogue identity. No substitution is allowed.')
    if len(matches) > 1:
        if any(k != 'personal_change' for _, k, _ in matches) or len({personal_signature(e) for _, _, e in matches}) != 1:
            raise ValueError('Ambiguous binding: matching records disagree or do not satisfy the personal-summary equivalence rule')
    # Equivalent personal summaries may have different peer context. Stable
    # representative selection is mechanical and does not add a peer answer.
    eid, kind, e = min(matches, key=lambda m: m[0])
    return eid, kind, e, sorted(m[0] for m in matches)


def compile_selection(engine, question, answer, evidence, condition):
    q = Question.model_validate(question)
    cls = DerivedAnswer if condition == 'derived_b' else BindingAnswer
    answer = cls.model_validate(answer)
    # Validate supplied records before interpreting their identifiers/metadata.
    records = {eid: validate_evidence(engine, q, value) for eid, value in evidence.items()}
    if any(eid != e.evidence_id for eid, e in records.items()):
        raise ValueError('Evidence mapping key disagrees with its validated identifier')
    intents, bindings, seen = [], [], set()
    for selection in answer.answers:
        if condition == 'derived_b':
            eid, kind = selection.evidence_id, selection.kind
            if eid not in records:
                raise ValueError('Unknown evidence identifier: choose only returned evidence IDs')
            e, aliases = records[eid], [eid]
            handle = identity(q, e, kind)
        else:
            handle = selection.identity
            eid, kind, e, aliases = resolve(q, handle, records)
        if (kind, eid) in seen:
            raise ValueError('Duplicate selected answer; do not repeat an identical kind/evidence pair')
        seen.add((kind, eid))
        meta = derived(e, kind)
        intents.append({'kind': kind, 'evidence_id': eid, 'support': meta['support']})
        bindings.append({'original_selection': selection.model_dump(), 'identity': handle,
                         'resolved_evidence_id': eid, 'equivalent_evidence_ids': aliases,
                         'derived_metadata': meta})
    semantic = {'answers': intents, 'conclusion': {'kind': 'descriptive', 'scope': 'selected', 'evidence_ids': []}}
    spec, provenance = historical_compile(engine, q, semantic, records)
    provenance.update(interface=condition, original_selection=answer.model_dump(), resolved_bindings=bindings,
                      metadata_origin='compiler_derived_from_explicit_selection_and_validated_evidence',
                      equivalence_rule='Exact personal temporal/numerical signature; lexicographically smallest returned ID; no peer meaning in personal identity')
    provenance['conclusion']['origin'] = 'compiler_supplied'
    provenance['conclusion']['reason'] = 'neutral descriptive heading; no substantive cross-reference conclusion inferred'
    return spec, provenance
