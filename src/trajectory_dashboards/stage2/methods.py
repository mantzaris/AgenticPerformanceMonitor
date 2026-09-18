"""Comparable method policies. Integrity is shared; task scoring is separate."""
from .core import Question, Request, Specification
from .integrity import reference_conclusion


def specification(q, records, include_history=True):
    ids=[e.evidence_id for e in records]
    claims=[{"template":"comparison","evidence_id":eid} for eid in ids]
    if include_history: claims.append({"template":"personal_change","evidence_id":ids[0]})
    panels=[{"kind":"trajectory","evidence_id":ids[0]},{"kind":"observation_status","evidence_id":ids[0]}]
    panels.extend({"kind":"comparison","evidence_id":eid} for eid in ids)
    assessment=[e for e in records if e.feature in {"nonbanked_submissions","scheduled_no_submission"}]
    if assessment:
        panels.append({"kind":"assessment_status","evidence_id":assessment[0].evidence_id})
        claims.append({"template":"measurement_limits","evidence_id":assessment[0].evidence_id})
    conclusion=reference_conclusion(records)
    if conclusion=="insufficient_evidence" and all(e.status=="supported" and e.summary['personal_status']=='supported' for e in records):
        conclusion="descriptive"
    return Specification(question_id=q.question_id,cutoff_day=q.cutoff_day,evidence_ids=ids,claims=claims,panels=panels,conclusion=conclusion,followups=["change_reference","change_window","check_assessment_availability"])


def deterministic(engine,question):
    q=Question.model_validate(question)
    rule=engine.cfg['question_kinds'][q.kind]
    requests=[Request(question_id=q.question_id,feature=rule['feature'],reference=r) for r in engine.cfg['references']]
    if 'assessment' in rule['context']:
        for feature in ('nonbanked_submissions','scheduled_no_submission'):
            if feature!=rule['feature']:
                requests.append(Request(question_id=q.question_id,feature=feature,reference='course'))
    records=[engine.analyze(q,r) for r in requests]
    # Enumerate the complete registry, then retain relevant comparisons by declared question kind.
    selected=[e for e in records if 'references' in rule['context'] or e.reference=='course']
    return specification(q,selected,'personal_history' in rule['context']),{e.evidence_id:e for e in records},requests
