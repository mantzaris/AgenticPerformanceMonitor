# Stage 6 review entry point

**Stage 6 completed. Explicit binding did not improve the frozen endpoint.**
Enumeration scored 24/24 complete visible answers; A scored 21/24, B 15/24 and
C 15/24. Model-selected completeness was **18/24, 14/24 and 11/24** for A/B/C.
No agent met the combined engineering gate. Retain enumeration and stop further
tuning of this interface approach on the same registry. Between B and C, B is the
simpler and better-supported implementation; neither replaces A or enumeration.

**A scoring caveat affects four B assessment cases:** their requested recent means
are visibly present inside personal-change claims but are not credited by the
unchanged focal-item predicate. Primary scores are preserved; see the
[display/scoring audit](docs/stage6/SCORING_CAVEAT.md). No agent gate is rescued by
that four-case issue alone. Human scientific/rubric review remains pending, and
agent final validation and publication readiness are blocked. Reserved observations
remain unopened. Work and commits are on `main`, with no force-push.

Starting commit: `2828c07c86c518106d3add6320279585ec6c22ac`.
Construction execution: `09882f579b4fa406fcd3f129cd9b7857d610d63f`.
Completed pre-freeze implementation: `2999aed53280117b7b19ee4c21b0ebf9a5b18599`.
Frozen comparison execution: `949019eceb9b0278d1836e1544689c9829bb7b10`.
Complete results/review commit: `857d065f27c9080d36938fac30aa153bb87bf9d7`.
The final handoff commit adds [publication metadata](artifacts/stage6/publication.json);
resolve its full SHA with `git log -1 --format=%H -- artifacts/stage6/publication.json`.
Its SHA and actual push status are also reported in the session completion.

## Read first

- [Scope](docs/stage6/SCOPE.md), [frozen protocol and decision rules](docs/stage6/PROTOCOL.md), [interface and binding definitions](docs/stage6/INTERFACES.md).
- [Exact reproduction commands](docs/stage6/REPRODUCTION.md); saved dashboards need no inference.
- [Freeze manifest](artifacts/stage6/protocol/freeze.json), canonical JSON SHA256 `bfcf5de8d63f06f7b7065fb104366bb20888ddc1a7f44f69043007936ec35989`.
- [People/questions/selection](artifacts/stage6/tasks/manifest.json), [hidden requirements and independent facts](artifacts/stage6/evaluator_only/rubrics.json), [counterbalanced order](artifacts/stage6/protocol/execution_order.json).
- [Preserved Stage 5](STAGE5_REVIEW.md), [original plan](Agentic_Longitudinal_Dashboards_Research_Plan.md), [unchanged statistical protocol](docs/stage2/ANALYSIS_PROTOCOL.md).

## Diagnosis and intervention

Offline reproduction confirms the old 14B compact result: 9/12 complete visible
answers, 8/12 complete through model selections and enough retrieved evidence for
all twelve under the oracle diagnostic. This is saved in the
[diagnosis](artifacts/stage6/diagnosis/stage5_reproduction.json), without rerunning
those agents. Stage 5 case 06 selected peer answers but declared a personal-scope
insufficiency conclusion. Cases 07–08 retrieved recent course evidence and omitted
the requested peer answer. These known cases were construction material only.

The hypothesis is that making the intended analytical answer explicit improves
complete valid answers on fresh development people. A is unchanged 14B compact;
B removes model-authored support/scope/conclusion and derives those metadata from
selected kind/evidence IDs; C replaces that selection pair with an exact semantic
identity. All retain the generic investigation policy. Both B and C receive the
same mechanical catalogue of returned answers, irrespective of the question's
requirements. B–A therefore measures the documented metadata/interface package,
including catalogue presentation; C–B isolates identity selection under that
shared information. A gain over A alone cannot establish a binding effect.

Peer identities include person/course/cutoff, feature, focal window, reference
population key and reference window. Personal identities contain the earlier and
recent personal windows and deliberately omit peer definitions. Resolution is
restricted to returned, source-validated evidence. Equivalent personal summaries
must agree exactly in numerical and temporal fields; a stable returned ID is
chosen and all aliases recorded. Unknown, altered or ambiguous handles fail.
There is no nearest-match substitution, hidden checklist, added analysis or
inferred missing answer. A valid irrelevant selection can still be incomplete.

The unchanged Stage 4 compiler constructs layout and required context from
explicit selections. It adds no missing comparison or personal-change claim.
B/C receive a neutral compiler-authored heading, not an inferred cross-reference
conclusion. Every accepted comparison/change is checked against original model
selections. Compiler context and method-selected completeness are separately
accounted for, including grades unavailable because release timing is unknown.
See the [mapping and provenance rules](docs/stage6/INTERFACES.md) and the
[construction record](docs/stage6/CONSTRUCTION.md).

## Frozen design

Twenty-four new development people, four per existing family, were selected by
administrative eligibility and a fixed hash seed. All 57 earlier focal people and
all 24 new people are excluded from the shared reference pool across registrations.
Insufficiency cases use fewer than two recent eligible weeks and at least one
earlier week, with separate personal and peer questions. No activity magnitudes
or expected method outcomes were used in selection. Repeating preparation
reproduced people, questions, independently calculated facts and execution order.

All four conditions run on all 24 questions: 96 method/case slots, including 72
agent episodes. Six A/B/C permutations repeat four times, balancing positions and
pair order. Enumeration runs on the same GPU host CPU. Agent episodes have at most
six analytical calls, four generations and one final repair. The checkpoint,
backend, BF16 precision, 16,000 input tokens, 1,500 output tokens, greedy decoding,
support thresholds, statistical tools and Stage 3/4 scoring remain fixed.

Primary endpoint: complete valid visible answers. Model-selected completeness is
reported separately. The fixed engineering gate requires at least 22/24 complete
visible answers, zero accepted unsupported quantitative answers, and correctly
scoped separate personal/peer answers on all four insufficient-support cases.
These are development gates, not statistical generalization or publication gates.

## Complete results under the frozen evaluator

All 96 slots were attempted once. No infrastructure-blocked condition, episode
rerun or deterministic fallback occurred. Five agent episodes ended without an
accepted dashboard: A12/A22 and C18/C19/C20. The compiler/evaluator/analytical code
were not changed after freeze.

| Condition | First final valid | Valid after repair | Complete visible | Complete through method selections | Both insufficiency answers | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Enumeration | 24/24 | 24/24 | 24/24 | 24/24 | 4/4 | PASS |
| A: unchanged compact | 21/24 | 22/24 | 21/24 | 18/24 | 3/4 | FAIL |
| B: derived metadata | 22/24 | 24/24 | 15/24* | 14/24 | 2/4 | FAIL |
| C: explicit binding | 21/24 | 21/24 | 15/24 | 11/24 | 1/4 | FAIL |

“First final” concerns the first final specification, not the absence of earlier
analysis-action errors. Successful repairs: A one of three, B two of two, C zero
of three. Zero accepted unsupported quantitative answers were found among all 91
accepted dashboards. The frozen detector found no unsupported `describe` assertions
or unbound numeric fields; this does not mean there were no semantic errors—unknown
identifiers, invalid scopes and incomplete selections are reported separately.

*B17–20 are the documented equivalent-form caveat. Crediting only those disputed
cases would give 19/24 visible, still below the target with only 2/4 insufficiency
cases complete. This conditional bound is not an adopted new primary score.

[Primary report](artifacts/stage6/reports/comparison.json),
[per-case JSON](artifacts/stage6/reports/per_case.json),
[CSV](artifacts/stage6/reports/per_case.csv), and
[all paired outcomes](artifacts/stage6/reports/paired_cases.json) preserve every
case and condition. S = complete through method selections; C = visibly complete
with compiler-supplied requested context; I = accepted but incomplete under the
frozen rule; F = no accepted output. I* denotes the B mean-form caveat. Numbers
and wording always come from deterministic tools, including method-selected answers.

| Case | Family | Enumeration | A | B | C |
| --- | --- | --- | --- | --- | --- |
| s6_01 | personal_change | S | S | S | S |
| s6_02 | personal_change | S | S | S | S |
| s6_03 | personal_change | S | S | S | S |
| s6_04 | personal_change | S | S | S | S |
| s6_05 | reference_sensitivity | S | S | S | S |
| s6_06 | reference_sensitivity | S | S | S | S |
| s6_07 | reference_sensitivity | S | S | S | S |
| s6_08 | reference_sensitivity | S | S | S | S |
| s6_09 | observation_limits | S | C | I | C |
| s6_10 | observation_limits | S | C | I | C |
| s6_11 | observation_limits | S | C | C | C |
| s6_12 | observation_limits | S | F | I | I |
| s6_13 | insufficient_support | S | S | S | S |
| s6_14 | insufficient_support | S | S | I | I |
| s6_15 | insufficient_support | S | I | I | I |
| s6_16 | insufficient_support | S | S | S | I |
| s6_17 | assessment_availability | S | S | I* | C |
| s6_18 | assessment_availability | S | S | I* | F |
| s6_19 | assessment_availability | S | S | I* | F |
| s6_20 | assessment_availability | S | S | I* | F |
| s6_21 | alternate_windows | S | S | S | I |
| s6_22 | alternate_windows | S | F | S | S |
| s6_23 | alternate_windows | S | S | S | I |
| s6_24 | alternate_windows | S | S | S | S |

| Paired comparison (right minus left) | Both complete | Right only | Left only | Neither | Net visible change |
| --- | ---: | ---: | ---: | ---: | ---: |
| binding_c − compact_a | 14 | 1 | 7 | 2 | -6 |
| binding_c − derived_b | 12 | 3 | 3 | 6 | +0 |
| derived_b − compact_a | 14 | 1 | 7 | 2 | -6 |

Method-selected net changes are −7 for C−A, −3 for C−B and −4 for B−A. C versus B
has three visible improvements and three regressions, with no net gain; B's four
assessment scoring disputes additionally limit interpretation of that equality.
These are paired development descriptions, not significance tests, independent
confirmation from earlier stages or a per-case best-condition deployment strategy.

## Mechanism, failures and compiler accounting

A and B retrieved enough evidence for every question under the oracle diagnostic;
C did so for 21/24. C18–20 had invalid analysis batches, **zero returned evidence**,
and invented unresolved handles at final and repair. No nearest answer was
substituted. They never received a returned catalogue, so catalogue contents alone
cannot explain those failures. These are model/schema failures, not GPU failures.
All 168 comparison generations reached EOS; maximum actual output was 491 tokens,
so the observed failures were not truncation at the 1,500-token ceiling.

| Mechanism/accounting | A | B | C |
| --- | ---: | ---: | ---: |
| Missing requested-analysis items | 0 | 0 | 9 |
| Retrieved-but-omitted items, including rejected dashboards | 12 | 19* | 9 |
| Such omissions in accepted dashboards | 1 | 19* | 6 |
| Automatic scope-error episode tags | 2 | 0 | 0 |
| Unknown evidence-ID episodes | 1 | 0 | 0 |
| Unresolved binding episodes | 0 | 0 | 3 |
| Ambiguous binding episodes | 0 | 0 | 0 |
| Schema-error episodes (nonexclusive) | 1 | 4 | 7 |
| Compiler-supplied requested context items | 7 | 12 | 12 |
| Compiler-added panels | 32 | 37 | 37 |
| Compiler-added comparison/personal-change claims | 0 | 0 | 0 |
| Derived selection-metadata records | 0 | 114 | 80 |
| Neutral compiler headings | 0 | 24 | 21 |

*Eight of B's 19 item omissions are the disputed recent means in B17–20. Do not
interpret the automatic count as nineteen literal absences from the rendered pages.

A15 selected earlier-window/earlier-stage peer answers instead of the requested
recent course-peer answer. C12 selected a valid baseline click-rate answer while
the question requested the recent mean. These are observable wrong-window choices
for the question, even though labels/source bindings are internally correct. A15
also has a wrong-reference alternative. C18/C20 supplied empty invalid reference
keys in analysis batches. A09/A12 paired peer answers with personal conclusion
scope; A09 repaired it, A12 did not. A22's repair retained invalid descriptive scope.
B14/B15 and C14–16 omitted explicit personal insufficiency; C21/C23 omitted the
personal answer under the frozen rule. These distinctions are preserved in
[case records](artifacts/stage6/reports/per_case.json) and
[manual trace observations](artifacts/stage6/inspection/trace_review.json).

The frozen automatic taxonomy is intentionally preserved: it misses C12's focal
wrong-window category, misses A22's descriptive-scope error (three scope-involved
episodes were trace-inspected: A09/A12/A22), and calls B23's 11-versus-10 panel-limit
failure schema rather than layout. The manual audit adds those descriptions without changing
scores. B23 repaired the panel overflow. Valid bindings never implied full question
completion. Derived support/scope removes redundant authored fields; it did not
improve answer selection here. Existing peer trajectories can accompany personal
panels as shared context; they are not credited as requested peer-window answers.

## Execution cost and actual GPU verification

| Condition | Tool calls | Exact / equivalent duplicates | Generations | Input / output tokens | Episode seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Enumeration | 84 | 0 / 0 | 0 | 0 / 0 | 35.40 |
| A: unchanged compact | 76 | 0 / 5 | 52 | 178,794 / 10,274 | 484.64 |
| B: derived metadata | 79 | 0 / 8 | 53 | 238,675 / 10,012 | 504.21 |
| C: explicit binding | 82 | 4 / 12 | 63 | 262,031 / 10,695 | 536.32 |

Equivalent duplicates use the frozen feature/group/window signature; exact calls
use the narrower request signature. Median episode seconds were 1.18, 17.07, 16.87
and 21.19 for enumeration/A/B/C. Enumeration used the same host CPU and was much
cheaper. Latencies include analysis/rendering and are descriptive; shared loading
is not assigned arbitrarily to a condition.

- Checkpoint: `Qwen/Qwen2.5-14B-Instruct`, revision
  `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`; [preserved manifest](artifacts/stage5/models/qwen14b/manifest.json), all local file hashes verified. No downloads or new models.
- Actual GPU: NVIDIA RTX 6000 Ada Generation, 49,140 MiB, driver 580.159.04.
  Transformers 4.55.2, Torch 2.8.0+cu128, CUDA 12.8, BF16/SDPA, all parameters and
  inference input/output on `cuda:0`; no quantization or CPU offload. CUDA profiler
  recorded 2,431 device events per load, with per-generation CUDA timing and own-PID
  GPU residency. [Construction runtime](artifacts/stage6/gpu/qwen14b_construction_01/runtime.json),
  [comparison runtime](artifacts/stage6/gpu/qwen14b_comparison_02/runtime.json),
  [generation metadata](artifacts/stage6/gpu/generations), and the unchanged
  [full-bound capacity proof](artifacts/stage5/checks/capacity_qwen14b.json).
- 185 attempted generations: 17 setup/construction/profile, 168 comparison.
  The six construction episodes used 15 generations; each of two loads used one
  single-token profile generation. All limits hold; maximum actual input was
  10,888 tokens. There were no failed GPU generations or infrastructure-blocked slots.
- Cumulative model-process time **1,719.02 s (28.65 min)**: construction 153.02 s,
  comparison 1,566.00 s, including loading and cleanup. Shared initialization was
  41.16/37.55 s and profiling 1.58/1.65 s. Peak allocated memory was 30.78 GiB;
  peak reserved in comparison was 35.23 GiB. [Resource detail](artifacts/stage6/reports/resource_detail.json).
- Both model PIDs exited, GPU compute-process list was empty, and no Stage 6 local
  server was started. Chromium closed after inspection. The pod remains running.
  [Cleanup proof](artifacts/stage6/checks/process_cleanup.json). Pod billing time is
  unknown and is not inferred from these timings.

Append-only [execution ledger](artifacts/stage6/execution.jsonl) and
[model ledger](artifacts/stage6/model_ledger.jsonl) preserve counters across both
loads. Stage wall time is measured separately from the start at
2026-09-18T23:19:16Z; the review snapshot was **68.63 minutes** after that start.
The measured snapshot and limits are in the
[run manifest](artifacts/stage6/run_manifest.json).

## Verification, review and replay

| Check actually performed | Result / evidence |
| --- | --- |
| Binding, aliases, support/scope, grade limits, omissions and common-interface fixtures | 12 PASS; [test log](artifacts/stage6/checks/construction_tests_03.txt). Initial fixture expectation failure retained in 01; corrected log 02 and construction note preserved. |
| Stage 5 diagnosis without inference | PASS; 9 visible / 8 selected / 12 evidence-sufficient reproduced |
| Structural selection and separate row-loop facts | PASS; [repeat preparation](artifacts/stage6/checks/selection_reproduction.json), 52 independent fact records agree with saved baseline |
| History, freeze, splits, budgets and actual GPU path | PASS; 5,278 historical files and 86 frozen inputs unchanged; 24 fresh people, 57 prior people excluded; 8,583 reserved IDs excluded without reading their observations |
| All accepted replay and agent recompile | PASS; 91 exact bound/chart/SVG/provenance replays, 67 agent recompile checks; [verification](artifacts/stage6/checks/final_verification.json) |
| Browser/export inspection | PASS with documented presentation limits; 28 slots, 26 pages, two rejected slots, zero browser errors; [visual/trace review](artifacts/stage6/inspection/VISUAL_REVIEW.md) |
| External scientific and rubric review | PENDING; [human packet](artifacts/stage6/human_review/README.md), [machine-readable packet](artifacts/stage6/human_review/packet.json) |
| Engineering gate for an agent | FAIL for A, B and C; enumeration PASS |
| Final reserved-data validation | NOT ATTEMPTED; [blocked preparation draft](docs/stage6/FINAL_VALIDATION_DRAFT.md) |

Representative self-contained HTML exports and adjacent saved specifications,
evidence, bound claims and provenance:
[personal C01](artifacts/stage6/comparison/binding_c/s6_01/accepted/dashboard.html),
[references C05](artifacts/stage6/comparison/binding_c/s6_05/accepted/dashboard.html),
[observation C09](artifacts/stage6/comparison/binding_c/s6_09/accepted/dashboard.html),
[insufficiency baseline13](artifacts/stage6/comparison/baseline/s6_13/accepted/dashboard.html),
[assessment B17 caveat](artifacts/stage6/comparison/derived_b/s6_17/accepted/dashboard.html),
[alternate C21](artifacts/stage6/comparison/binding_c/s6_21/accepted/dashboard.html).
[All screenshots](artifacts/stage6/inspection) follow the prespecified rule. No
rejected output was replaced with an enumeration dashboard.

```bash
.venv/bin/python -m pytest -q tests/test_stage6.py
.venv/bin/python scripts/stage6/verify.py --replay --output /tmp/stage6-verification.json
.venv/bin/python - <<'PY_REPLAY'
from trajectory_dashboards.stage6.core import Engine
from trajectory_dashboards.stage6.adapter import replay
replay(Engine(), 'artifacts/stage6/comparison/binding_c/s6_01/accepted', '/tmp/stage6-replay')
PY_REPLAY
```

Open `/tmp/stage6-replay/dashboard.html`. [Reproduction documentation](docs/stage6/REPRODUCTION.md)
includes exact fresh-workspace preparation, deterministic analysis, offline rescoring
and optional separately authorized GPU commands. Never overwrite saved attempts.
No model call, raw-data download or weights are needed for replay.

## Deviations and decision

No execution deviation: checkpoint, scientific definitions, scoring, prompts,
compiler and code remained frozen; no reruns, fallback success, reserved observation
access, new download or ceiling violation. Pre-freeze construction changes and the
one fixture expectation failure are documented. Post-freeze inspection discovered
and separately documented the scoring/diagnostic caveats; primary results were not
changed. Supplementary trace and resource summaries describe saved artifacts only.

Retain enumeration for this small registry. B is preferable to C among the two
proposed interfaces on simplicity, validity, method-selected completeness and cost,
but neither improves on A or meets the gate. Do not continue prompt/policy/binding
tuning on these known families to obtain a positive result. The next bounded step
is external scientific/rubric review of the packet and, if authorized, a separately
versioned post-hoc audit with **zero new inference and no reserved data**.

The candidate publication argument is a transparent negative reliability and
responsibility-allocation study, not a novel JSON/tool/rendering technique or an
agent advantage. See [contribution assessment](docs/stage6/CONTRIBUTION.md) and
[focused primary-source overlap](docs/stage6/PRIOR_ART.md). No agent passes the
engineering gate; rubric equivalence and scientific assumptions remain unreviewed;
no held-out, generalization or usability evidence exists. These are publication
blockers. The [conditional validation draft](docs/stage6/FINAL_VALIDATION_DRAFT.md)
is preparation only, with no promoted agent or opened reserved observations.

## Scientific limits retained

Window reference means give equal weight to eligible people, after averaging each
person's eligible observed weeks. Weekly trajectories use that week's eligible
people. This corrects an imprecise phrase in the old Stage 5 review without changing
its artifacts or the estimator. Different histories and changing peer composition
limit interpretation. Earlier-stage peers are not causal adjustment or inherently
fairer comparisons. Thresholds remain engineering support rules.

The 500-replicate person bootstrap estimates uncertainty of reference means, not
individual prediction intervals or uncertainty for personal changes and contrasts.
Scores/grades remain withheld without release timing. Zero recorded activity,
unknown logging completeness, administrative ineligibility and unavailable
measurements remain distinct. Clicks do not establish effort, learning or ability.
The primary treatment of repeated source rows and earlier sensitivity findings
are unchanged. The separate mixed-model artifact is not a validated detector or
source for dashboard claims. Reserved observations remain unopened; split IDs are
used only to verify exclusion.
