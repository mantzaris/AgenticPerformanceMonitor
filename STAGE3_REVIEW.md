# Stage 3 independent-review handoff

**Stage 3 executed and verified; ready for independent scientific review with
limitations. The coverage-aware policy did not improve completeness.** The strong
deterministic baseline answered all 24 questions and was cheaper. Do not advance
the new policy unchanged to a full evaluation. External human review remains
outstanding; this is a provisional development pilot.

Work is on `main`, following [AGENTS.md](AGENTS.md). Starting commit:
`367fce597a4ba1d1277e9f84db5b5cc5241cbf69`.
Initial construction used `690f1a4`; the two format checks used `637732f`.
Final scientific/execution implementation: `6f07d4e0cf706e6589bc3d1a20bfe96a59256d82`.
Frozen pilot execution commit: `6c0020b103a8485549cfa7659df3246e07cafb0d`.
Completed results/review package: `6b784823ac2b305e531396c4b7a4f731f79dbd29`.
The final handoff is the subsequent `main` tip (`git rev-parse HEAD`), reported in
the completion message. No historical commit was rewritten.

The results package was pushed to `origin main`. Plain HTTPS initially lacked a
configured credential helper; the existing authenticated GitHub CLI account worked
with a command-scoped helper. No credential was printed or stored in this repository,
and no permanent authentication configuration changed. [Push record](artifacts/stage3/checks/push_result.json).

## Read first

- [Scope](docs/stage3/SCOPE.md), [analysis protocol](docs/stage3/ANALYSIS_PROTOCOL.md), [evaluation protocol](docs/stage3/EVALUATION_PROTOCOL.md), and [shared public interpretation rules](docs/stage3/PUBLIC_INTERPRETATION.md).
- [Freeze manifest](artifacts/stage3/protocol/freeze.json): 56 input/code files, frozen before every pilot method ran.
- [Twelve cases and 24 question instances](artifacts/stage3/tasks/manifest.json), [evaluator-only requirements/facts](artifacts/stage3/evaluator_only/rubrics.json), and [counterbalanced execution order](artifacts/stage3/protocol/execution_order.json).
- [Exact reproduction commands](docs/stage3/REPRODUCTION.md).
- [Historical reanalysis](artifacts/stage3/stage2_reanalysis/REANALYSIS.md), [scoring justifications](artifacts/stage3/checks/scoring_justifications.json), and [external-review items](artifacts/stage3/checks/EXTERNAL_REVIEW_ITEMS.md).
- The unchanged [Stage 2 review](STAGE2_REVIEW.md), [frozen insufficiency audit](artifacts/stage2/reports/INSUFFICIENCY_SCORING_AUDIT.md), and [original research plan](Agentic_Longitudinal_Dashboards_Research_Plan.md).

## What changed and why

The evaluator distinguishes source-bound numerical integrity, requested answers,
necessary context, optional additions and selection/compiler provenance. Required
answer items carry a wording or public-interpretation justification. More panels
do not earn a higher answer score. Merely retrieving a result does not display an
answer. Equivalent supported claims and suitable comparison charts are accepted;
personal-window means are not inferred from a trajectory alone.

Supported `insufficient_evidence` conclusions now receive global-finding credit.
A general conclusion resolves a particular comparison only when its unsupported
referent is unique; otherwise feature/window/reference-specific claims are needed.
One unsupported comparison does not excuse omission of another answerable request.
Unavailable grades, insufficient observations and uninvestigated questions remain
different states.

Peer-only reference questions no longer require personal history. Historical
unqualified "activity" permits coherent use of any existing activity feature;
new questions name the requested measure. The historical broad assessment-record
question can be answered with dated assessment states without mandating two
unstated numeric features. These repairs are provisional judgments, not external
human validation.

The new policy is instructed to extract a concise request map from the public
question, see an initial result, select subsequent analyses, update answered/
insufficient/unavailable/uninvestigated states, and check final answer selection. Its map and
stopping status are saved with evidence links; they are model claims about task
state, not trusted coverage scores or private reasoning. The dispatcher does not
fill missing analyses or substantive answers. No evaluator facts, gold checklist
or task-specific required tool sequence enters the model.

The generic and previous reference-sensitive policy texts are unchanged. They run
under the shared Stage 3 Action schema and public rules, so this is the previous
policy **under the Stage 3 interface**, not an exact Stage 2 replication. The new
policy also has phase reminders introduced on known construction cases. The
intervention bundles those reminders and task-state tracking; their separate
effects are not identified here.

All methods use the same unchanged descriptive backend, reference definitions,
source-bound integrity validator and controlled renderer. Shared rendering adds
feature prefixes and explicit personal-insufficiency windows/counts. It inserts
no missing analysis or claim. Standard caveats and numerical wording are compiler
content, reported separately. The strong enumeration baseline retains its existing
selection rules and enumerates the full small reference registry.

## Stage 2: original scores and separate post-hoc reanalysis

No Stage 2 agent was rerun, and no old output, primary score, ledger or frozen file
was changed. All 34 accepted historical dashboards were numerically revalidated;
their actual HTML claim/conclusion bindings were also checked.

| Method | Original full context | Revised complete requested answers | Revised method-selected complete |
|---|---:|---:|---:|
| Deterministic | 12/12 | 12/12 | 12/12 |
| Generic | 4/12 | 2/12 | 2/12 |
| Previous reference-sensitive | 2/12 | 2/12 | 2/12 |

The endpoints have different item definitions and denominators. Gains from fixing
the p03/p04 overrequirement coexist with losses where a peer result was retrieved
but not visibly answered. The four supported global insufficiency conclusions
from the previous reference-sensitive policy are credited as global findings;
that does not establish scoped answers to every requested comparison. See every
[per-question change and original score](artifacts/stage3/stage2_reanalysis/per_question.json)
and the [endpoint-change index](artifacts/stage3/checks/historical_endpoint_changes.json).

## Pilot design and statistical boundaries

Twelve new development people have two equivalent intended phrasings each: **24
dependent question instances, not 24 independent people**. Two cases cover each
of six question families. Selection used course/profile, eligibility counts,
prior-attempt category and a fixed SHA256 ranking, without activity magnitudes or
method outcomes. All prior 21 focal people and all 12 new people are excluded from
the fixed reference pool across registrations. Reserved trajectories remain closed.
Synthetic fixtures appear only in scorer tests, never in the real-data pilot.

Both phrasings have mechanically identical cutoffs, data, reference pools,
requirements and independently calculated facts. Language equivalence and task
realism still need external human review. All six agent-order permutations are
used and paired phrase order alternates; each agent occupies each serial position
eight times. Fixed greedy decoding tests operational phrasing sensitivity, not
stochastic repeatability or general superiority.

The Stage 2 weighting, primary repeated-row treatment, complete-week cutoffs,
support thresholds and bootstrap procedure remain unchanged. Means weight observed
weeks equally within person, then peers equally; eligibility/history imbalance and
changing composition remain limitations. Earlier-stage references answer a
different descriptive question. Pointwise peer-mean intervals are not individual
prediction intervals or uncertainty for personal change/contrasts. Grades and
banking approval remain withheld. The mixed-model artifact supplies no claim.

## Frozen pilot results

All 96 method/question results are retained: 24 deterministic and 72 agent episodes.
No pilot episode was rerun, no fallback was used, and there was no post-freeze
tuning or change to scoring, questions, code or source data.

| Method | First final valid | Valid after repair | Complete requested | Complete method-selected | Both phrasings complete |
|---|---:|---:|---:|---:|---:|
| Deterministic enumeration | 24/24 | 24/24 | 24/24 | 24/24 | 12/12 cases |
| Generic agent | 12/24 | 14/24 | 11/24 | 11/24 | 4/12 cases |
| Previous reference-sensitive | 8/24 | 16/24 | 11/24 | 10/24 | 3/12 cases |
| Coverage-aware | 8/24 | 14/24 | 6/24 | 6/24 | 1/12 cases |

The new policy was less complete and more expensive than both agent controls in
this run. Its task maps were not reliably accurate: 11 episodes claimed completion
while the accepted-answer endpoint was incomplete. It made 26 exact repeated
requests (32 equivalent analyses after canonicalizing reference/window definitions).
Thus its intended duplicate avoidance and final coverage check **were not achieved**.
It did choose a subsequent analysis after results in 18/24 episodes; the previous
policy did so in 18/24 and the generic policy in 11/24. Adaptation alone did not
establish usefulness.

| Method | Missing requested analysis items | Retrieved but omitted items | Scoped insufficiency answers | Measurement-availability answers |
|---|---:|---:|---:|---:|
| Deterministic | 0 | 0 | 8/8 | 8/8 |
| Generic | 0 | 49 (6 in accepted outputs) | 3/8 | 1/8 |
| Previous | 4 | 40 (3 in accepted outputs) | 6/8 | 2/8 |
| Coverage-aware | 5 | 50 (11 in accepted outputs) | 3/8 | 4/8 |

Missing/omitted counts are answer items, not people. A failed dashboard has no
accepted visible answer; its retrieved items remain in the omitted denominator.
The eight insufficiency items are two comparisons for each of four question
instances, representing two people. The eight availability requests come from
observation-limit and assessment questions. Of their credited answers, one for
the previous policy and all four for the new policy came from compiler context;
these are not evidence of agent-selected answers. The previous policy's `s3_05b`
completeness depends on that compiler credit, explaining 11 visible versus 10
method-selected complete outputs. Optional personal-history panels occurred in
4/0/1/4 questions respectively and earned no completeness bonus.

All 68 accepted pilot dashboards passed source-bound numerical integrity checks.
There were no unsupported accepted quantitative claims in the controlled vocabulary.
This is not a claim about unrestricted prose or educational usefulness. Repairs
were attempted in 12/16/16 agent episodes; 2/8/6 respectively became valid. Failures
are preserved with original responses and actionable validation errors. Common
failures were missing trajectory, observation or assessment panels and exceeding
the panel limit; the new policy also had malformed JSON and an oversized task map.
One generic unsupported direction-change conclusion was rejected.

The unchanged common validator requires a trajectory and observation panel even
for assessment-only questions. Some failures therefore concern the shared layout
contract, rather than erroneous numeric calculations. Its scientific necessity
needs review. Validation was not relaxed after observing these failures.

Completeness agrees across paired phrasings in 12/9/7/8 cases respectively; full
answer-pattern agreement is 12/7/6/5. Agreement can mean both answers fail, so it
is not an accuracy score. See [all question records](artifacts/stage3/reports/per_question.json),
[CSV](artifacts/stage3/reports/per_question.csv), [paired case records](artifacts/stage3/reports/paired_cases.json)
and [primary summary](artifacts/stage3/reports/comparison.json). Each failed question
is listed there. [Additional descriptive tabulation](artifacts/stage3/reports/handoff_summary.json)
was produced after execution from unchanged frozen scores; it does not rescore.

## Cost and actual GPU execution

| Method | Tools | Exact / equivalent repeats | Generations | Prompt / completion tokens | Episode seconds |
|---|---:|---:|---:|---:|---:|
| Deterministic | 84 | 0 / 0 | 0 | 0 / 0 | 36.52 |
| Generic | 105 | 2 / 10 | 74 | 343,342 / 27,814 | 727.62 |
| Previous | 91 | 1 / 8 | 84 | 386,817 / 28,670 | 753.60 |
| Coverage-aware | 113 | 26 / 32 | 88 | 478,905 / 43,932 | 1,097.74 |

All timed analyses ran on the same GPU host's CPU. All inference used the existing
**NVIDIA RTX 6000 Ada**, driver 580.159.04, Qwen2.5-7B-Instruct revision
`a09a35458c702b33eeacc393d103063234e8bc28`, Transformers 4.55.2 and Torch
2.8.0+cu128, BF16 on `cuda:0`, with no CPU offload. Existing weights were hash-verified
and reused. Greedy decoding, 1,500 output tokens and all episode limits were shared.
Actual device tensors, CUDA events/kernels and own-process GPU memory establish GPU
execution; a CUDA availability flag alone was not used as proof.

**277 attempted generations: 31 construction/setup and 246 pilot**, below 32/288
partition and 320 total ceilings. The setup count includes three one-token CUDA
profiling generations. Every episode stayed within six tools, four generations
and one final repair. Cumulative model-process time was **3,022.990 seconds
(50 minutes 23 seconds)** including initialization and cleanup: construction
276.319 and 138.078 seconds; pilot 2,608.593 seconds. One model load served all 72
pilot episodes. Its shared initialization was 25.866 seconds and profiling 1.290
seconds, not assigned arbitrarily to a policy. Generation CUDA-event sums and
latencies are separately recorded. Timing includes shared integrity caches and
is not an isolated cold-cache benchmark. Pod billing time is **unknown**.

The append-only [model ledger](artifacts/stage3/model_ledger.jsonl),
[stage ledger](artifacts/stage3/execution.jsonl), [pilot runtime](artifacts/stage3/gpu/pilot_03/runtime.json)
and all original [generation messages/metadata](artifacts/stage3/gpu/generations)
substantiate usage. [Device check after completion](artifacts/stage3/checks/device_after_completion.json)
found no compute processes and 2 MiB used. All three model processes exited; the
local follow-up server also stopped. The pod was not terminated. Exact stage
wall-clock and handoff status are in [run metadata](artifacts/stage3/run_manifest.json):
approximately **93 minutes**, below the six-hour ceiling.

## Checks, dashboards and remaining limitations

| Check / deliverable | Status | Evidence |
|---|---|---|
| Revised scorer fixtures and scientific boundaries | PASS | [44 tests](artifacts/stage3/checks/final_prefreeze_tests.txt), including 16 Stage 3 checks; no frozen code changed afterward |
| Stage 2 post-hoc reanalysis, original scores preserved | PASS, provisional rubric | [Reanalysis](artifacts/stage3/stage2_reanalysis/REANALYSIS.md), [visible bindings](artifacts/stage3/checks/historical_visible_bindings.json) |
| Fresh structural preparation and independent facts | PASS | [Reproduction](artifacts/stage3/checks/preparation_reproduction.json): 12 cases, 24 questions and facts reproduced |
| Frozen pilot, budgets, GPU execution and exclusions | PASS | [Final verification](artifacts/stage3/checks/final_verification.json): 96 results, 8,583 reserved people excluded, 56 frozen and 1,043 historical files unchanged; Stage 2's 45 frozen files unchanged |
| Saved replay without model calls | PASS | 74 accepted construction/pilot/follow-up results replayed with identical bound JSON, Vega-Lite and SVG |
| Representative rendering and real follow-up | PASS with UI limitations | [Browser record](artifacts/stage3/inspection/browser.json), [visual review](artifacts/stage3/inspection/VISUAL_REVIEW.md) |
| Policy tracking and adaptive execution | PARTIAL | Maps and adaptive calls saved; duplicate avoidance and reliable final coverage were not achieved |
| Scientific/rubric/usability review by an independent person | NOT ATTEMPTED | [External-review items](artifacts/stage3/checks/EXTERNAL_REVIEW_ITEMS.md) |

Representative baseline dashboards: [personal change](artifacts/stage3/pilot/baseline/s3_01a/accepted/dashboard.html),
[reference comparison](artifacts/stage3/pilot/baseline/s3_03a/accepted/dashboard.html),
[assessment limits](artifacts/stage3/pilot/baseline/s3_09a/accepted/dashboard.html),
[insufficient support](artifacts/stage3/pilot/baseline/s3_07a/accepted/dashboard.html).
The proposed policy's [personal example](artifacts/stage3/inspection/coverage_aware_s3_01a.browser.png)
and [insufficiency example](artifacts/stage3/inspection/coverage_aware_s3_07a.browser.png)
illustrate valid but incomplete answers, not selected success stories. Every
accepted directory contains question, specification, evidence, bound values and
HTML/SVG/PNG exports. The [follow-up child](artifacts/stage3/followups/s3_07a_followup_0171394851/dashboard.html)
changes reference and cutoff/windows, reruns analysis and preserves its parent.
It correctly remains insufficient; [before/after screenshots](artifacts/stage3/inspection/browser.json)
and the interaction link are saved.

Long reference labels, overlapping panels and boilerplate can obscure answers.
Assessment-state charts need care: states are at the due week's end, not necessarily
the dashboard's later cutoff. The follow-up form's default selection can differ
from its displayed result. These defects were documented, not repaired after the
freeze. One initial local replay invocation ended without a result or captured
error; it was repeated once and the completed verification passed. Empty initial
and completed retry logs are preserved. There were no frozen-pilot protocol deviations.
The reporting-only handoff tabulator was added after freeze and changes no score.

Next bounded stage: obtain independent human review of question equivalence,
scoped insufficiency, admissible visual answers, compiler-credit semantics and the
shared panel contract; then run a small construction-only diagnosis of omissions,
duplicate requests and interface errors. Keep enumeration as the operational
baseline. This pilot demonstrates no measured benefit of the proposed policy;
broader flexible-investigation benefits remain untested. Leave reserved evaluation,
simulations, new models, training and manuscript work closed pending that review.

## Reproduce and inspect

```bash
.venv/bin/python -m pytest -q tests/test_stage3.py
.venv/bin/python scripts/stage3/verify.py --replay --output /tmp/stage3-verification.json
.venv/bin/python scripts/stage3/summarize_handoff.py --output /tmp/stage3-summary.json
.venv/bin/python -m trajectory_dashboards.stage3.followup --port 8766
```

Open `http://127.0.0.1:8766/artifacts/stage3/pilot/baseline/s3_07a/accepted/dashboard.html`.
[Reproduction instructions](docs/stage3/REPRODUCTION.md) cover fresh preparation,
CPU analysis, exact saved replay, rescoring and an optional newly authorized GPU
run in a fresh workspace. Historical episode directories refuse reruns.
