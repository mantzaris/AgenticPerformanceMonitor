# Stage 3 offline diagnostic (Stage 4, no new inference)

This audit reads the unchanged original outputs and scores. It validates retrieved evidence against the original source, then uses evaluator requirements **offline only**. Availability and intended-answer projections are not agent successes and are not supplied to Stage 4 inference. Multiple labels may apply.

| Method | Complete accepted | Failed | Oracle evidence-availability bound | Failed episodes with complete intended selection ignoring layout |
|---|---:|---:|---:|---:|
| baseline | 24/24 | 0 | 24/24 | 0 |
| generic | 11/24 | 10 | 24/24 | 6 |
| reference_sensitive | 11/24 | 8 | 22/24 | 6 |
| coverage_aware | 6/24 | 10 | 23/24 | 5 |

The generic method had sufficient retrieved information for all questions, but not all intended answers selected it. All ten generic rejected episodes contained structural errors; six had a complete answer selection in at least one attempt if the rejected layout is ignored. The other controls also combined omissions with structural failures. The main analysis therefore treats layout burden as a testable explanation, not an established cause.

Original counts of complete answers are confirmed: 24, 11, 11 and 6. Exact per-step errors, intended-selection projections, parse positions, oracle item availability and overlapping labels are in [stage3_cases.json](stage3_cases.json). [Summary](stage3_summary.json) records counts and limitations. The original primary scores remain at `artifacts/stage3/reports/`.

None of the recorded Stage 3 outputs reached its 1,500-token ceiling. EOS/finish reasons were not recorded, so there is no direct proof of termination cause. The malformed JSON had an observable syntax error; it is not labeled truncation merely because it was long. Excessive panels, missing trajectory/observation/assessment panels, excessive request-map entries and mixed action fields are distinct schema failures. No logically inconsistent set of mandatory panel instructions was demonstrated. Complexity/confusion is an untested explanatory hypothesis.

Stage 3 requested-answer omissions in valid dashboards remain genuine omissions. Offline structural projections discard unusable fields for diagnosis and never render or relabel those episodes as accepted. Unsupported directions/insufficiency and unknown evidence references are not credited as valid answers. All 119 parseable attempted specification objects had matching question and cutoff labels; that additional check is saved in `checks/diagnostic_label_audit.json`.

There is no independent human scientific review in this audit. Its oracle rules are the provisional Stage 3 interpretation rules.
