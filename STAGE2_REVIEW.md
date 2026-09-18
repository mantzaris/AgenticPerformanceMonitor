# Stage 2 independent-review handoff

**Stage 2 execution is complete. Ready for independent review with specified
limitations; not ready for full research evaluation.** The deterministic baseline
covered all twelve pilot tasks. Both agents omitted requested context, and the
frozen insufficiency-scoring item has a documented defect. All original results
remain available; no failed pilot episode was rerun.

Current branch: `main`. After Stage 2 completed, the repository owner requested
consolidation onto `main` and deletion of the working branch. `main` was
fast-forwarded, preserving every Stage 2 commit, and the local
`stage2/scientific-pilot` branch was deleted. No corresponding remote branch
existed. The frozen scope and execution ledgers retain the historical branch
name. Future work follows the owner's workflow recorded in [AGENTS.md](AGENTS.md).

Stage 2 starting commit:
`dd87aaf012b2ecb8f9a45f00f782fabeebb4450c`.
Construction GPU execution used `4e80e4e` (the source snapshot is recorded in its runtime).
Scientific implementation and pre-pilot hardening are committed in `39c68e9`.
Frozen pilot execution commit: `5163ac032465a294b02684e80e94bf2e11a22164`.
Stage 2 completion commit: `2cce1156a3b41159a328b9c3a77b4d97b4e41abb`.
Subsequent commits on `main` document the branch consolidation and workflow;
the current tip is available with `git rev-parse HEAD`.

**Transport history:** at the Stage 2 handoff, the work was committed locally.
Automatic review initially
rejected the push over destination/payload concerns. Read-only verification showed
that the existing origin's main ref exactly matched the starting commit; the
public OULAD source/license and proposed artifact contents were checked. The
same direct push was then permitted, but GitHub HTTPS authentication failed:
`could not read Username`, with terminal prompts disabled. No branch was pushed.
The publication command after consolidation is `git push origin main`.
See [transport evidence](artifacts/stage2/checks/git_transport.json) and
[destination/payload checks](artifacts/stage2/checks/push_preflight.json).

## Read first

- [Frozen scope](docs/stage2/SCOPE.md), [analysis protocol](docs/stage2/ANALYSIS_PROTOCOL.md), [evaluation protocol](docs/stage2/EVALUATION_PROTOCOL.md).
- [Freeze manifest](artifacts/stage2/protocol/freeze.json): task manifest, evaluator-only facts/rubrics, prompts, configuration, source bundle and executable scientific/scoring code, all hashed before pilot inference.
- [Exact reproduction commands](docs/stage2/REPRODUCTION.md).
- [Task manifest](artifacts/stage2/tasks/manifest.json) and [rubrics awaiting external scientific review](artifacts/stage2/evaluator_only/rubrics.json).
- [Original research plan](Agentic_Longitudinal_Dashboards_Research_Plan.md) and unchanged [Stage 1 handoff](STAGE1_REVIEW.md).

## Implemented behavior

The versioned Stage 2 package shares a small registry of reference definitions,
question families and time profiles across tools, validation and rendering. An
analysis request selects a feature, reference and named window; the profile
jointly validates its baseline, recent window and complete-week cutoff. The
question's intent is separate from an empirically supported conclusion. A
reference-sensitivity question can produce a descriptive or same-direction
answer rather than an automatic claim of changed interpretation.

The integrity validator independently recomputes summaries, personal changes,
peer identities/counts, every displayed trajectory value and bootstrap endpoint
from the trusted source bundle. Resealing a corrupted record does not make it
valid. Units and reference/window labels must match. It returns all missing
panel/claim obligations together for the one permitted repair. Numerical wording
and boilerplate context are deterministically compiled and explicitly labeled.
Task coverage is scored separately; universal validation does not enforce a
preferred investigation sequence or require all three references for a question.

The strong deterministic baseline enumerates the admissible reference registry
and selects evidence with declared question-kind rules. A generic agent and a
reference-sensitive agent share the same model, decoding, tools, integrity rules,
source data and renderer. The latter can request another analysis after observing
the first result. Raw outputs, tool requests/results, errors, stopping decisions
and final specifications are preserved. Failed episodes remain failed; their
separately available deterministic baseline is not counted as agent success.

The local HTML form executes a new analytical request when a user changes the
reference or time profile. It saves a new evidence/specification/render package
and parent hash link. It preserves the original dashboard. No model call is
needed for replay or this follow-up.

## Data, scientific checks and assumptions

The original creator-deposited UCI OULAD source and Stage 1 audit remain unchanged:
28,785 distinct people, 32,593 registrations and 173,912 assessment records. The
fixed split still reserves 8,583 people across registrations; only development
features are loaded into Stage 2. The two development presentations remain
AAA_2013J and BBB_2013B, with 254 and 1,269 registrations and 18,276 weekly rows.
The small committed Stage 2 bundle contains only the allowlisted derived fields;
raw CSVs and model weights remain outside Git.

Six construction and twelve pilot tasks use 18 distinct focal people. None is
one of the original three demonstrations. Selection uses eligibility support,
prior-attempt category, course/profile and a fixed hash, never activity magnitudes
or final outcomes. All are real-data tasks. Synthetic edge cases occur only in
implementation tests. The fixed reference pool excludes all 18 focal people and
the three original demonstration people across their registrations. These are
retrospective development cases, not an eventual held-out benchmark.

Window means weight eligible weeks equally within person, then peers equally.
Partially eligible weeks therefore retain the same within-person weight as full
weeks after computing the daily click rate. Peer composition can change with
registration/withdrawal, and observed history lengths differ. Neither missingness
nor withdrawal is assumed ignorable. A reference contrast requires at least 20
peers and two focal weeks; personal change needs two weeks in each window. These
are provisional support rules, not power or clinical/educational validity claims.

Logging completeness is unknown; no clicks is not evidence of logging failure,
zero effort or zero learning. Administrative ineligibility and unknown eligibility
remain null rather than zero. Scores and banked credits remain withheld because
release/approval timestamps are absent. Scheduled assessments are opportunities,
not verified obligations; exemption and schedule-change histories are unavailable.
Weekly assessment states mean status at that week's end, not a later updated view.
Earlier-stage peers answer a different descriptive question, not an automatically
fairer or causally adjusted one.

The 500-replicate person bootstrap gives pointwise intervals for peer means. It
does not estimate individual prediction uncertainty, focal contrast uncertainty,
personal-change uncertainty, or the uncertainty of a difference between references.
Sign changes and equal signs are descriptive, not significance/invariance tests.

[Raw-source checks](artifacts/stage2/statistics/raw_source_checks.json) independently
check construction person-weeks using SQL sums/distinct counts. The independent
row-loop reducer checks analytical results without calling the production analysis
function. Neither is independent human review.

The primary treatment still preserves all source rows. The bounded exact-row
sensitivity used 193,708 eligible source rows, with 15,937 repeated excess rows.
Both [primary](artifacts/stage2/statistics/preserve_source_rows.json) and
[alternative](artifacts/stage2/statistics/drop_exact_source_rows.json) results,
plus the [alternative source bundle](artifacts/stage2/statistics/exact_row_sensitivity_source/manifest.json),
are saved for six construction cases and three references each. Magnitudes change;
no supported contrast changed sign. Exact repetition is not proven duplication
error, so neither interpretation establishes unique click events.

The [bounded mixed-model diagnostic](artifacts/stage2/statistics/mixed_model_diagnostic.json)
found full fixed-design rank (12 columns, condition number 12.78). One Powell retry
converged with random-intercept variance 0.54651 and residual variance 0.55555 on
the original AAA fit sample. The original L-BFGS singular-covariance failure remains
preserved. This is consistent with an optimizer/boundary-path problem; its exact
numerical cause was not reconstructed. The retry does not validate model assumptions
or a detector and supplies no dashboard claim.

## Working follow-up and rendered evidence

Start the local app:

```bash
.venv/bin/python -m trajectory_dashboards.stage2.followup --port 8765
```

Open `http://127.0.0.1:8765/artifacts/stage2/construction/baseline/c04/accepted/dashboard.html`.
The saved [browser verification](artifacts/stage2/followup_demo/verification.json)
links the [original](artifacts/stage2/construction/baseline/c04/accepted/dashboard.html)
to the [newly computed child](artifacts/stage2/followups/c04_followup_7dc4249cfd/dashboard.html).
Changing from recent weeks 8–11 to 2–3, earlier weeks 0–1 and the earlier-stage
reference changed an unsupported recent comparison into a supported descriptive
comparison based on two eligible focal weeks. The observed recent rate is zero;
the tool did not invent activity or explain its cause.

[Before](artifacts/stage2/followup_demo/before.browser.png) and
[after](artifacts/stage2/followup_demo/after.browser.png) browser screenshots show
the changed definitions, eligibility states, counts and accurate interval labels.
Chromium submitted the real form, followed the saved-child redirect and expanded
the inspector; no page errors were recorded. Parent hashes are unchanged.
Inspection was by Codex, not independent human scientific review. Only desktop
Chromium was exercised; accessibility, mobile and concurrent users remain outside
this minimal prototype. Long reference labels produce dense pages; per-week
denominators remain available in the inspector.

## Pilot, verification and resource totals

All three methods ran once on each of the twelve frozen tasks. Construction
used six additional model episodes, alternating policies: one accepted after
repair, five failed, with 23 generations. Those cases are excluded from pilot
evidence. The [construction changes](artifacts/stage2/protocol/construction_changes.json)
clarified compact output layouts and aggregated repair errors before the freeze;
they did not relax numerical validation or support rules. The freeze timestamp
was **2026-09-18T18:09:00.019667+00:00**.

| Method | First final valid | Valid after repair | Full requested context | Mean frozen coverage | Tool calls | Generations |
|---|---:|---:|---:|---:|---:|---:|
| Deterministic baseline | 12/12 | 12/12 | 12/12 | 1.000 | 42 | 0 |
| Generic agent | 7/12 | 10/12 | 4/12 | 0.650 | 64 | 39 |
| Reference-sensitive agent | 9/12 | 12/12 | 2/12 | 0.711 | 46 | 39 |

All 12 tasks remain in each denominator. The generic agent had three repaired
successes and two failures: p08 still omitted a trajectory after repair, and p09
still exceeded the ten-panel contract. The reference-sensitive agent had three
repaired successes and no rejected final outputs. Accepted outputs passed the
same independent numerical/evidence checks; no unsupported quantitative claim
was accepted within the controlled vocabulary. There were **zero deterministic
fallbacks**. Boilerplate supplied by the compiler is explicitly separate from
agent-selected content.

The reference-sensitive agent requested subsequent analyses after seeing results
in 12/12 episodes; the generic agent did so in 10/12. These counts describe the
observable sequence, not a counterfactual test of adaptive reasoning. Common
omissions included personal-history claims, same-prior-attempt comparisons and
assessment evidence. Some agent dashboards repeated charts or identical limitation
claims. Original layouts were preserved rather than silently improved.

**Scoring limitation:** the frozen “appropriate insufficiency” item requires a
comparison/personal-change claim and ignores the valid, visible
`insufficient_evidence` conclusion. Its original counts are baseline 4/4,
generic 3/4 and reference-sensitive 0/4. A separately labeled
[post-hoc display audit](artifacts/stage2/reports/INSUFFICIENCY_SCORING_AUDIT.md)
finds evidence-supported visible insufficiency statements in 4/4, 3/4 and 4/4
respectively. The original score is not a complete measure of appropriate handling.
This defect needs external review before another experiment. No frozen score,
output, prompt, configuration or code file was changed; the audit is a disclosed
post-hoc addition, not a replacement primary metric.

The baseline performed best on the frozen coverage rules with no inference cost.
This pilot shows no advantage over that baseline on measured task coverage or
integrity. The reference-sensitive policy had better observed validity and fewer
tools than the generic policy, but fewer fully covered tasks. This single small
development run supports neither general superiority nor repeatability.

Detailed [per-task JSON](artifacts/stage2/reports/pilot_per_task.json),
[CSV](artifacts/stage2/reports/pilot_per_task.csv), and
[raw comparison](artifacts/stage2/reports/pilot_comparison.json) include failures,
omissions, repair counts, tokens and latency. Agent artifacts are under
`artifacts/stage2/pilot/{generic,reference_sensitive}/p01` through `p12`;
baseline artifacts are under `pilot/baseline/`. Each accepted package contains
`question.json`, `spec.json`, `evidence.json`, `bound.json`, `chart.vl.json`, and
HTML/SVG/PNG exports. Invalid outputs and errors remain outside `accepted/`.

| Cost, pilot only | Baseline | Generic | Reference-sensitive |
|---|---:|---:|---:|
| Prompt tokens | 0 | 159,067 | 134,668 |
| Completion tokens | 0 | 14,128 | 10,425 |
| Sum of episode latency, seconds | 21.11 | 433.57 | 263.91 |
| Generation wall time, seconds | 0 | 398.78 | 249.34 |
| Recorded CUDA-event time, seconds | 0 | 335.11 | 247.25 |

Latency is not a hardware-controlled speed comparison: baseline analysis ran on
the local CPU, agents on the GPU host, and the first generic generation incurred
CUDA profiler overhead. Shared loading/cleanup overhead is reported per model
process rather than allocated arbitrarily to a policy.

The actual device was **NVIDIA RTX 6000 Ada Generation, 49,140 MiB**, driver
580.159.04. Both model processes verified existing file hashes for
**Qwen/Qwen2.5-7B-Instruct**, revision
`a09a35458c702b33eeacc393d103063234e8bc28`, using **Transformers 4.55.2,
PyTorch 2.8.0+cu128, BF16, no quantization or CPU offload**. Greedy decoding used
at most 1,500 new tokens and a 16,000-input-token cap. All parameters, inputs and
generated tensors were on `cuda:0`; profiler device events and own-process VRAM
confirm actual GPU execution. The pinned model's unused sampling defaults caused
Transformers warnings under greedy decoding; the warnings are preserved.

**Resource use:** 101 attempted generations total (23 construction + 78 pilot);
no new model download. Model-process runtime was **1,044.144634 seconds
(17 min 24.14 s)**: 313.510545 construction and 730.634089 pilot, including startup,
hash verification, loading, tool dispatch, validation/rendering and cleanup.
Both processes exited. The final GPU query showed no compute processes and
2 MiB used memory; the pod was left running. The local follow-up server was stopped
after verification. Stage wall time to completed handoff artifacts was **3729.78 seconds
(62.16 minutes)**, from 17:33:59 UTC to 2026-09-18T18:36:08.777044+00:00. The
[run manifest](artifacts/stage2/run_manifest.json) records this separately; final
Git transport is outside that measurement. Including transport checks and final
metadata, elapsed stage time was **66.67 minutes** through 2026-09-18T18:40:39.259057+00:00. Neither metric is RunPod billing time.

[Execution ledger](artifacts/stage2/execution.jsonl) and
[model budget ledger](artifacts/stage2/model_ledger.jsonl) are append-only across
the two starts. Every episode stayed within six tool calls, four generations and
one final repair. Original prompts/outputs and token/device metadata are under
`artifacts/stage2/gpu/generations/`; runtime files are under
`gpu/construction_01/` and `gpu/pilot_02/`. No private connection details or
credentials were added to tracked artifacts.

The original 12 checks passed before editing. Final pre-pilot checks passed
**28 tests**: the original 12 and 16 focused Stage 2 cases, including resealed
numerical corruption, alternate windows/cutoffs, insufficient history, independent
hand-calculated weighting, focal exclusion, actionable errors and recomputing
follow-up. The final [verification](artifacts/stage2/checks/verification.json)
replayed **42 accepted packages** without inference, with exact bound claims,
chart specifications and SVGs. All 111 inventoried Stage 1 artifacts and all 45
frozen pilot input files remained unchanged. Browser inspection covered the real
follow-up and three representative pilot exports; records/screenshots are under
`artifacts/stage2/checks/pilot_browser/` and `followup_demo/`.

| Acceptance criterion | Status | Evidence |
|---|---|---|
| Preserve Stage 1; reproduce relevant checks and inspect failed case | PASS | `checks/stage1_inventory.json`, pre-pilot test record, unchanged Stage 1 failure |
| Shared reference/window registry and cutoff validation | PASS | `configs/stage2.json`, `src/trajectory_dashboards/stage2/core.py`, boundary tests |
| Intent separated from empirical conclusion; source-bound numerical validation | PASS | `src/trajectory_dashboards/stage2/integrity.py`, resealed-corruption tests, p03 baseline |
| Explicit statistical protocol, source-row sensitivity, independent calculations and bounded fit diagnostic | PASS | `docs/stage2/ANALYSIS_PROTOCOL.md`, `statistics/` |
| 6 construction + 12 frozen, person-disjoint real development tasks | PASS | `tasks/manifest.json`, `protocol/freeze.json` |
| Three comparable methods, once per frozen task; actual adaptive GPU tool loop | PASS | `pilot/`, `gpu/`, ledgers |
| Reliable full question coverage by agents | PARTIAL | Generic 4/12 and reference-sensitive 2/12 full frozen coverage |
| Frozen insufficiency item measures all admissible answer channels | FAIL | `reports/INSUFFICIENCY_SCORING_AUDIT.md`; primary values preserved |
| One actual recomputing follow-up with immutable parent and replay | PASS | `followup_demo/verification.json`, child `link.json` |
| Complete failures, resource counts, device proof and focused replay verification | PASS | `run_manifest.json`, `checks/verification.json`, `checks/gpu_cleanup.json` |
| Reserved evaluation, training, model sweeps, extra datasets, multi-agent systems, paper | NOT ATTEMPTED | Outside Stage 2 scope |

The only post-freeze analytical addition was the disclosed insufficiency display
audit (deviation D1 in the run manifest). No pilot input or primary score was
tuned, no case was dropped, and no failed model episode was repeated.

## Scientific review decisions and next bounded stage

External review should assess the estimands and partial-week weighting, fixed
reference exclusions, support thresholds, source-row interpretation and informative
withdrawal. It should also review task realism and the automatic rubrics: activity
coverage operationalizes a predeclared click-rate estimand, and another sensible
activity feature can remain numerically valid while missing that rubric item.
Coverage is therefore not a validated measure of usefulness. Compiler-added
caveats and a controlled claim vocabulary cannot establish that an unconstrained
agent reasons safely. No participant or independent human evaluation occurred.

Recommend a next bounded stage of external scientific review of these frozen
questions, rubrics and saved outputs, followed by targeted construction-only
interface revisions and a preregistered evaluation design. Keep the reserved
population closed until that review resolves the estimands and scoring rules.
Do not infer superiority, repeatability, generalization or readiness for a full
research benchmark from this pilot. No training, second dataset, model sweep,
multi-agent system or manuscript work was attempted.
