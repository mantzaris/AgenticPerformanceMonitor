# Semantic answer mapping v1

An analyze Action is unchanged: one to six typed requests with feature, reference
and baseline/recent window. Final full Actions contain the existing Specification.
Final compact Actions contain `action: final`, `answers: [...]` and an optional
`conclusion: {...}` at the same level, with no nested answer wrapper.
Each intent has `kind`, a returned `evidence_id`, and `support`.
No arbitrary executable code, quantitative value or narrative claim is accepted.

| Explicit semantic intent | Substantive selection | Layout |
|---|---|---|
| `peer_comparison` | `comparison` claim, including exact focal/reference window means or scoped insufficiency | Comparison panel, including available means/counts |
| `personal_change` | Only `personal_change` claim for the evidence's earlier/recent windows | Trajectory; never adds a peer window-mean claim/panel |
| `assessment_status` | Dated assessment-state context | Assessment panel |
| `observation_status` | Administrative/recorded-state context | Observation panel |
| `measurement_limit` | Explicit selection of `measurement_limits` claim | No substantive quantitative panel implied |

Comparison/change `support` must be `describe` exactly when that comparison is
supported, and `insufficient_evidence` otherwise. This rejects unsupported estimates
and fabricated insufficiency. Other intents use `describe`: measurement unavailable
is not sample-size insufficiency. The peer intent also exposes the focal mean;
no separate focal-only primitive is introduced in this narrow experiment.

At most ten distinct kind/evidence intents and six selected IDs. Repeated identical
intents, unknown IDs and arbitrary fields are rejected. Only explicit answer IDs
are selected; unselected retrieved records are untouched. Question/cutoff labels
come from the validated question and evidence, never evaluator routing.

Conclusion defaults to `{kind: descriptive, scope: selected, evidence_ids: []}`.
`same_direction`/`direction_differs` require scope `peer` and at least two explicitly
selected, supported recent click comparisons with matching computed directions.
`insufficient_evidence` requires scope `peer` or `personal` and nonempty IDs of
explicitly selected insufficient answers of that type. The original global
conclusion check also runs; incompatible broader selected evidence is rejected.
Scoped comparison/change claims remain visible alongside the general heading.

The compiler adds the common trajectory and observation panel if absent; assessment
context when the existing contract requires it; and a trajectory for any selected
ID lacking a quantitative panel. If a context-only ID lacks a required claim, it
adds only the existing measurement-limits boilerplate. **It never adds a comparison
or personal-change claim**, never runs analysis, and never consults the task kind,
task ID, requested-answer rubric or all-retrieved list to choose content.

Every claim/panel records `origin`, selected answer indices and the mechanical
reason if compiler supplied. A deduplicated panel requested both explicitly and
mechanically is selected. Standard caveats and compiler-only observation/assessment
context are reported separately; they are not agent investigation. Exact compiler
output can be reconstructed from the saved semantic selection plus returned
evidence, with the original source-bound validator applied.

No scoring repair is made. The unchanged Stage 3 scorer measures visible coverage;
an explicit-selection projection attributes answers to the method versus compiler.
Fixtures require personal-only selection to leave peer requests unanswered, and
peer-only selection to leave personal requests unanswered, even if both estimates
were available in the tool result.

Construction originally tested a nested `answer` envelope. Five of six known-case
episodes misplaced fields at the root; all six failed for envelope or substantive
support errors. Before freezing, the semantic envelope was flattened to the form
above. No substantive support/conclusion check was relaxed. The failed originals
remain associated with their construction commit. One remaining construction
generation is allocated to a fixed final-format check using saved known-case tool
results; it is not a new successful investigation episode or pilot evidence.
