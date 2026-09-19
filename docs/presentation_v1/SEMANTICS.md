# Presentation contract

This package is a new rendering of saved Stage 6 development outputs. It does not
change an agent, compiler, evaluator, analytical result, score or historical page.
It reads only the accepted question, specification, evidence, bound claims and
selection provenance. It never reads task rubrics or the episode's unselected
tool-result dictionary. The separate S1 editorial annotation cites the existing
audit; it is not an input to the renderer.

## Selection and presentation

`model.py` admits saved, validated development artifacts and checks their saved
evidence digests. The separate verification command invokes the unchanged
source-bound numerical validator and historical replay. These checks establish
numerical binding, not answer completeness. No evaluator was run in this stage.

Every answer card comes from a selected `comparison`, `personal_change`, or
`measurement_limits` claim. In particular, a recent peer summary in a record
selected only for personal history does not become a recent peer answer. Every
original claim and panel remains accessible, with its original text, evidence,
provenance and multiplicity. Unselected evidence is never retrieved.

Layout selection uses the selected claims, features, references and support
states, not case identifiers. Supported personal history emphasizes earlier and
recent windows; unsupported personal history keeps the personal and peer scopes
separate; multiple compatible peer definitions provide a saved-reference selector;
unsupported measurements emphasize availability; assessment features emphasize
weekly measures and dated record states. The public question kind selects a
deterministic abbreviated heading. The complete original question and conclusion
remain accessible immediately below the main view.

The compact reading route is an explicitly labeled **excerpt**, not an alternate
answer. For personal progress it emphasizes a recent peer comparison only if one
was selected. Other selected comparisons remain in the expanded answer section.
If only earlier peer comparisons were selected, those retain their earlier labels.
The compact observation view emphasizes the status timeline; dated assessment
states remain in the expanded view and original panels. Both routes retain the
complete saved claim list, original conclusion, panel vocabulary and evidence.

## Responsibility

| Component | Responsibility in these outputs |
| --- | --- |
| Saved agent, or enumeration baseline | Selected analytical answers, evidence identifiers and conclusion. |
| Original analytical tools | Calculated observations, means, differences, counts and bootstrap intervals. |
| Original semantic compiler | Supplied deterministic wording, required panels and standard caveats, as recorded in `selection_provenance.json`. |
| New presentation layer | Organizes those selections, abbreviates labels, draws SVGs, consolidates exact duplicate personal claims and switches emphasis among saved references. |
| Figure composition | Adds panel lettering and explicitly external editorial annotations; never alters the captured dashboard pixels. |

The main examples all use compact A. Case C was accepted after the historical
single repair; this package did not repair it. Its three insufficiency selections
are agent authored; the observation, trajectory, assessment and grade context is
original compiler content. Case D selected both peer-comparison measures,
assessment/observation states and measurement limitations; its trajectory is
compiler supplied. These distinctions are exposed in the expanded views and
captions. Shared caveats are not agent investigation.

## Values, time and availability

Display values come directly from saved summary fields and result-table rows.
Two decimals are applied only at display time, so a displayed difference need not
equal subtraction of two already rounded displayed means. Raw values remain in
the inspector. All windows and reference windows are retained explicitly.

The peer mean averages person-level within-window means with equal person weight.
Counts distinguish people, person-weeks and observed focal weeks. Trajectory peers
are same-week peers; their composition can change over time. An earlier-period
reference is a different question, not a causally adjusted or automatically fairer
population. The selected population and reference-period definitions stay linked
to their original evidence.

Whiskers and shaded bands are the original 95% peer-mean bootstrap intervals
(500 person-level replicates). They are not individual prediction intervals, nor
intervals for the focal-minus-peer contrast or personal change. No interval is
created by this renderer. All comparable reference marks use a shared zero-based
scale. The saved-reference control changes the highlight, selected values,
reference/window label and evidence link together. The focal value, feature,
window and scale stay fixed. It invokes no analytical pipeline or model.

`observation_status` denotes administrative eligibility and **click-record** state
even in an assessment-feature record. It must not be inferred from the feature's
numeric value. For example, Case C has a scheduled non-submission in week 2 while
its click-record state is zero activity. Recorded zero is `0.00`; null is
`Unavailable`; ineligibility is hatched and marked ×; unknown state has a ? legend.
The examples contain no synthetic unknown-state periods. Logging completeness is
unknown throughout, separately from the administrative/recorded state. Lines
break at null values rather than interpolating through ineligible periods.

Assessment measures retain their meanings: non-banked submissions per observed
week and scheduled assessments without recorded submission per observed week.
The dated assessment rows are saved snapshots at the shown as-of days, not a log
of grades or all recent submission events. In Case D the scheduled rows are due
on days 19 and 54, with states as of days 20 and 55; the requested weekly means
are for weeks 8–11 through day 83. Do not interpret the day-55 state as an updated
day-83 obligation or grade. The later weekly submission measure and earlier
dated state need not coincide. Grade-release and banking-approval timestamps
remain unknown; no achievement, ability, effort or learning rating is produced.

## Deduplication and preserved failure

Only personal claims with identical original wording, selection origin, feature,
unit, focal person/cutoff, earlier/recent windows, means, counts, change and support
are consolidated. The irrelevant peer definition is excluded from personal
meaning. Case A has two copies of the same personal change; agent Case E has two
copies of the same personal insufficiency. Original claim indices and both
evidence identifiers remain in each presentation manifest. No peer comparisons
are merged: Case E's two earlier peer claims have different reference identities
and different bootstrap endpoints despite equal means. All original panels are
retained separately, including repeated panels with differing intervals.

S1 uses compact A / s6_15 and its enumeration result. The accepted agent selected
earlier peer answers and personal insufficiency but omitted the requested recent
peer-support answer. Its recent peer evidence is present because it was selected
for **personal** meaning; this does not authorize a peer answer. The failure is
preserved in both reading routes. Reviewer annotations are outside the captures.
The existing [trace audit](../../artifacts/stage6/inspection/trace_review.json) and
[visual review](../../artifacts/stage6/inspection/VISUAL_REVIEW.md) substantiate this
interpretation. No success rate or task score was recalculated.

This is a bounded vocabulary for this repository's saved development artifacts,
not a general natural-language dashboard system or an independently reviewed
scientific/clinical decision interface. The Stage 6 scoring caveat and pending
external scientific review remain unresolved.
