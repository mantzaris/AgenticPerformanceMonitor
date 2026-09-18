# Fixed-policy interface ablation

The exact Stage 4 episode code object is reused in isolated globals. The policy,
tool dispatcher, request schema, continuation instructions, budgets, renderer,
numerical validator and Stage 3/4 completeness/provenance scorer are unchanged.
Only the semantic Action class, interface paragraph, tool-result catalogue and
selection-to-old-compiler adapter differ. A's complete model messages and behavior
are unchanged apart from the public case/context and Stage 6 logging.

| Component | A: compact | B: derived metadata | C: explicit binding |
| --- | --- | --- | --- |
| Model selection | kind, opaque evidence ID, support; scoped conclusion | kind, evidence ID | exact semantic identity |
| Support/scope | Model authors; validator checks | Derived from selected kind and validated record | Same as B |
| Cross-reference conclusion | Model may select validated conclusion | None added; neutral descriptive heading | Same as B |
| Returned facts | Historical compact result | Same result plus mechanical answer catalogue | Byte-identical catalogue procedure to B |
| Layout/context | Historical semantic compiler | Same compiler | Same compiler |

B/C expose identical analytical information, including all handles and their
kind/evidence mappings; C only changes which representation the model must return.
A remains unchanged and does not see the extra catalogue. Consequently B–A measures
the derived-metadata interface package (including redundant presentation of existing
facts), not a pure causal effect of deleting fields. C–B isolates explicit selection
identity under that shared catalogue; C–A is the entire intervention.

## Canonical identities

Identities are human-readable exact-match strings, scoped to the frozen source and
registry carried in evidence provenance. They use no task ID, task kind, rubric,
question-text checklist or required-analysis sequence. Every returned result
mechanically exposes each existing answer kind, whether relevant to the question
or not. No result outside the episode is eligible.

Peer identity fields: `peer_comparison|person=...|course=...|cutoff=...|feature=...|
focal=start:end|reference=...|reference_window=start:end`. The reference key resolves
to the unchanged frozen population rule; course/person context identifies the
prior-attempt subgroup when applicable. The shared fixed exclusion pool is in the
source manifest, and the tool result includes the full reference label and counts.

Personal fields: `personal_change|person=...|course=...|cutoff=...|feature=...|
earlier=start:end|recent=start:end`. A peer definition is not part of personal
meaning. Context identities use their existing kind and source-record fields;
they select only that context, never a comparison.

For repeated personal summaries, every candidate must be source-validated and
agree exactly in feature, unit, person, cutoff, earlier/recent windows, means,
observation counts, change and personal support. The exact canonical signature is
checked; the lexicographically smallest returned ID is a stable representative.
All equivalent IDs are recorded. Nonpersonal collisions or disagreeing personal
summaries are ambiguous and rejected. No numerical averaging or nearest matching.

The resolver records original selection, full identity, resolved ID, equivalent
IDs and derived support/scope/answer state. Peer and personal insufficiency are
distinct. Grade availability remains unavailable measurement context, independent
of sample support. Unknown handles, altered windows/references/context and unsupported
schema fields are rejected. A valid selection of an irrelevant earlier comparison
is allowed by integrity but remains incomplete under the unchanged question scorer.
Integrity cannot infer the model's intended missing answer.

## Compilation and responsibility

B/C translate selected answers to historical semantic intents and invoke the
unchanged Stage 4 compiler. That compiler still provides required layout/context,
but no missing comparison/change claim or analysis. The heading is compiler-supplied
neutral description, never credited as a model conclusion. Every comparison/change
is linked to an explicit original selection; derived support labels do not count
as new investigation. B/C cannot author a cross-reference conclusion, but existing
scoring credits a complete set of scoped comparisons as an equivalent answer.

Replay requires the saved specification, evidence and provenance; re-resolving C's
equivalence proof also uses the episode's complete saved returned-evidence dictionary.
No model or additional analysis is needed. Catalogue presence is never completeness.
