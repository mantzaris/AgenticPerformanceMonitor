# Construction record before comparison freeze

Known Stage 5 cases 06–08 were replayed and diagnosed without new inference.
The reproduction confirms 9/12 visible-complete, 8/12 method-selected-complete,
and 12/12 oracle evidence-sufficient outputs for the old 14B compact condition.
Case 06 selected peer answers with a personal conclusion scope; 07–08 retrieved
recent course evidence but omitted the corresponding peer answer. These are
construction material, never fresh confirmation cases.

Six GPU construction episodes ran once: B and C on each known case, using the
Stage 5 reference pool. All produced valid dashboards, but only C on 06 was
visible-complete; its method-selected answer remained incomplete. B on 06 mixed
answers into an analyze action; C on 06 requested an unsupported feature name.
Both recovered within the existing four-generation ceiling. Personal answers
were omitted on 07–08 in both new interfaces; C on 07 also omitted the recent
peer answer. B on 06 omitted the requested observed means. See
`artifacts/stage6/construction/review.json` and
the complete per-episode sequences. This is not evidence that the intervention
works. No prompts or analytical choices were tuned after these outcomes.

The construction process used 16 setup generations including one CUDA profile,
and 153.017 seconds including loading and cleanup. It stopped normally.

The first focused test run had nine passes and one failure because a fixture
expected the wrong error substring: the numerical validator correctly rejected
a forged personal summary with a recomputed hash. Correcting only that expected
substring gave ten passes. Two positive checks were then added for explicitly
selected, separately scoped personal and peer insufficiency; all twelve pass.
Original logs are retained as construction_tests_01/02/03.

After GPU construction, the compiler gained an explicit rejection of unknown
interface names, which does not change B/C behavior. Reporting, replay checks,
selection preparation and freeze machinery were completed. Independent-fact
verification uses the existing numerical comparison tolerance, not exact float
equality. These are pre-freeze changes. No fresh comparison case was sent to a
model during construction. Synthetic fixtures are implementation checks only.
