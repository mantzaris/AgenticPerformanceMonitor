# Stage 5 review entry point

**Stage 5 completed: 14B compact answered 9/12 cases, versus 2/12 for 7B compact;
enumeration answered 12/12.** The larger checkpoint substantially improved the
primary endpoint but missed the frozen 11/12 engineering gate. Retain enumeration
for this registry. Consider a separately reviewed, bounded answer-binding change;
broader agent validation is premature. No earlier scores or scientific implementation
files changed. The reserved population remains closed.

Starting commit: `a9c3a39fbdff144271ced07607e21098e927c6da`.
Capacity-check execution: `c68457916f2479f0ff7ced572b2d476441e9aeb1`.
Final pre-freeze protocol/reporting: `7062e52f0ead0b2c858f4bc0a0642261703f1844`.
Frozen comparison execution: `7616198845d29f5262ec6ca0d9c3fcda17fe9d65`.
The final main commit is reported at completion; later handoff commits preserve
these execution commits and historical artifacts without force-push.

## Read first

- [Scope and ceilings](docs/stage5/SCOPE.md), [frozen protocol and decision rules](docs/stage5/PROTOCOL.md), [exact reproduction commands](docs/stage5/REPRODUCTION.md).
- [Freeze manifest](artifacts/stage5/protocol/freeze.json), canonical JSON SHA256 `8658768c142060bc154a87005e5b0e77a0b981ac104ed825216ff902dfead348` (the runtime's freeze identifier; the separate file-byte hash is in the run manifest).
- [Tasks/selection](artifacts/stage5/tasks/manifest.json), [evaluator-only requirements and facts](artifacts/stage5/evaluator_only/rubrics.json), [execution order](artifacts/stage5/protocol/execution_order.json).
- Preserved [Stage 4 review](STAGE4_REVIEW.md), [semantic mapping](docs/stage4/INTERFACE.md), [public interpretation rules](docs/stage4/PUBLIC_INTERPRETATION.md), [original research plan](Agentic_Longitudinal_Dashboards_Research_Plan.md).

## Hypothesis and fixed conditions

Test whether poor completeness changes substantially with the larger official
instruction-tuned checkpoint from the same family, holding the analytical system,
generic investigation policy and interfaces fixed. Primary descriptive contrast:
14B compact versus 7B compact complete valid answers on the same twelve cases.
Secondary comparisons are checkpoint effects under full specification, interface
effects within each checkpoint, and all four conditions versus enumeration.

The Stage 4 failures motivate this checkpoint comparison; they do not show that
agents generally cannot perform the task. This study is twelve fresh development
people in known families, one greedy run per condition, not held-out evaluation,
stochastic repeatability or a pure causal effect of parameter count.

The adapter executes the original Stage 4 episode code object with only Stage 5
logging and display-label bindings. It directly imports the unchanged semantic
compiler, numerical validator, statistical tools and completeness/provenance
scorer. Prompts, public information, schemas, greedy decoding, 1,500 output tokens,
16,000 input tokens, six analytical calls, four generations and one final repair
are unchanged. No constrained decoding, new policy or missing-answer insertion
was added. Checkpoint identity appears only in execution metadata and output paths.

All 45 earlier focal people and the twelve new people are excluded from the fixed
peer pool across registrations. The existing structural selector uses declared
seed `stage5-structural-v1-20260918`; it inspects administrative eligibility and
prior-attempt structure, not activity magnitudes or method success. Fresh
preparation reproduced all twelve people/questions and the separate row-loop
facts. No synthetic observation enters the pilot. These facts/rubrics still await
independent human scientific review and are never model inputs.

Enumeration runs on the GPU host CPU before two model blocks, 7B then 14B. Within
each block, full runs first on odd cases and compact on even cases: six first
positions each. All conditions share the same source and reference pool. Timing
is descriptive because model blocks and cache/temporal effects are not eliminated.

## Checkpoints, acquisition and actual device

| Checkpoint | Pinned revision | Files |
| --- | --- | --- |
| Qwen/Qwen2.5-7B-Instruct | `a09a35458c702b33eeacc393d103063234e8bc28` | [Existing manifest](artifacts/gpu/model_manifest.json); weights reused and preserved |
| Qwen/Qwen2.5-14B-Instruct | `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8` | [Acquired manifest](artifacts/stage5/models/qwen14b/manifest.json), [pre-download inspection](artifacts/stage5/models/qwen14b/inspection.json), [official metadata/license](artifacts/stage5/models/qwen14b/official) |

The official 14B checkpoint has Apache 2.0 licensing. Its seventeen selected files
total 29,551,687,352 bytes (29.55 GB), below the 40 GB authorization. Standard caches
and existing model directories were inspected; available disk was 63,875,182,592
bytes before acquisition. File sizes and official LFS SHA256 / Git blob hashes
were checked, followed by actual local SHA256 manifests. Download plus hashing took
179.41 seconds; metadata retrieval is recorded separately. No 7B file was replaced.
Weights stay outside Git. [Acquisition ledger](artifacts/stage5/models/qwen14b/acquisition.jsonl)
retains timing and outcome.

Both use the existing Transformers 4.55.2, Torch 2.8.0+cu128, SDPA, BF16 and cuda:0,
with no quantization or CPU offload. The actual device is NVIDIA RTX 6000 Ada
Generation, driver 580.159.04, 49,140 MiB. All parameter devices/dtypes, CUDA kernel
profiling, generated-tensor devices and own-process GPU memory are recorded. A
CUDA-availability check alone is not the evidence.

[Tokenizer comparison](artifacts/stage5/models/tokenizer_comparison.json) found
identical tokenizer files, chat templates and special-token configurations. Each
checkpoint nevertheless loads its own pinned tokenizer files. Architecture and
checkpoint differences extend beyond parameter count; no size-only causal claim
is made.

Both passed actual capacity checks at 16,000 input positions plus 1,500 greedy
forward steps: [7B proof](artifacts/stage5/checks/capacity_qwen7b.json),
[14B proof](artifacts/stage5/checks/capacity_qwen14b.json). Peak allocated memory was
18,450,055,168 bytes for 7B and 34,687,351,808 for 14B. These capacity-only computations
repeat known construction tokens and continue computation past EOS while retaining
those tokens. They test the complete memory/compute bound and are counted setup
generations, not scored agent answers. Comparison episodes retain ordinary EOS
stopping and the unchanged generation configuration.

## Frozen results and decision

All twelve deterministic runs and 48 agent episodes executed once. There were no
infrastructure-blocked cases, model-generation execution failures or deterministic
fallbacks. Rejected outputs remain failures. Full records are in
[per-case JSON](artifacts/stage5/reports/per_case.json),
[CSV](artifacts/stage5/reports/per_case.csv),
[aggregate report](artifacts/stage5/reports/comparison.json) and
[paired cases](artifacts/stage5/reports/paired_cases.json).

| Condition | First final valid /12 | Valid after repair /12 | Complete visible /12 | Complete method-selected /12 | Repairs attempted | Gate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Enumeration | 12 | 12 | 12 | 12 | 0 | PASS |
| 7B full | 5 | 7 | 6 | 5 | 7 | FAIL |
| 7B compact | 7 | 7 | 2 | 2 | 5 | FAIL |
| 14B full | 7 | 9 | 7 | 7 | 5 | FAIL |
| 14B compact | 11 | 11 | 9 | 8 | 1 | FAIL |

First-final validity concerns the first attempted final specification, not the first
generation: analytical actions can precede it. Integrity is PASS for every accepted
dashboard and **no accepted output** for rejections. There were zero accepted
unsupported quantitative answers. This does not mean there were no unsupported
semantic statements: see the rejected conclusion/support attempts below.

Every case is included below. **C** = complete through method-selected answers;
**C\*** = visibly complete with compiler-supplied required context; **I** = accepted
but incomplete; **R** = rejected, without a dashboard substitute.

| Case | Family | Enumeration | 7B full | 7B compact | 14B full | 14B compact |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | Personal change | C | C | I | C | C |
| 02 | Personal change | C | C | I | C | C |
| 03 | Reference sensitivity | C | C | C | C | C |
| 04 | Reference sensitivity | C | C | C | C | C |
| 05 | Observation limitations | C | R | R | R | C* |
| 06 | Observation limitations | C | R | R | C | R |
| 07 | Insufficient support | C | I | R | I | I |
| 08 | Insufficient support | C | R | R | I | I |
| 09 | Assessment availability | C | R | R | R | C |
| 10 | Assessment availability | C | C* | I | R | C |
| 11 | Alternate windows | C | C | I | C | C |
| 12 | Alternate windows | C | R | I | C | C |

| Paired contrast (left → right) | Both complete | Right only | Left only | Both incomplete | Net change |
| --- | ---: | ---: | ---: | ---: | ---: |
| **7B compact → 14B compact (primary)** | 2 | 7 | 0 | 3 | **+7/12 (+58.3 points)** |
| 7B full → 14B full | 5 | 2 | 1 | 4 | +1/12 |
| 7B full → 7B compact | 2 | 0 | 4 | 6 | -4/12 |
| 14B full → 14B compact | 6 | 3 | 1 | 2 | +2/12 |

For method-selected completeness, the primary comparison is two both complete,
six larger-only, zero smaller-only and four both incomplete (+6/12). The difference
from visible completeness is case 05: the compact compiler supplies the required
dated assessment-state panel. Full 7B case 10 obtains its measurement-availability
answer from standard renderer caveats. Neither counts as completely model-selected.
No per-case best-model mixture is proposed. Stage 4's 3/12 full and 4/12 compact
results concern different people; cross-stage score differences are not checkpoint
effects.

The preregistered engineering gate remains 11/12 complete valid answers with zero
accepted unsupported quantitative answers. Substantial primary descriptive
improvement is prespecified as at least three net additional complete cases;
this is a decision aid, not a significance threshold. See the complete decision
branches in the [protocol](docs/stage5/PROTOCOL.md).

## Failure mechanisms and answer provenance

| Condition | Missing-analysis items | Retrieved but not answered items | Such omissions in accepted dashboards | Offline retrieved-evidence upper bound /12 | Correct scoped insufficiency items |
| --- | ---: | ---: | ---: | ---: | ---: |
| Enumeration | 0 | 0 | 0 | 12 | 4 |
| 7B full | 0 | 24 | 1 | 12 | 1 |
| 7B compact | 10 | 21 | 11 | 10 | 0 |
| 14B full | 0 | 16 | 2 | 12 | 2 |
| 14B compact | 0 | 8 | 2 | 12 | 2 |

Counts in the middle columns are requested answer items, not cases. Rejected
dashboards count every unpresented requested answer; public measurement context
can be available without a tool call. The upper bound uses evaluator requirements
offline and is **oracle-assisted diagnosis, never agent success or model input**.

14B compact retrieved enough evidence for all twelve cases. Its remaining failures:

- **06, rejected:** peer-insufficiency selections use a personal-scope conclusion
  without a personal answer. The single repair keeps that mismatch. Original
  [trace](artifacts/stage5/comparison/qwen14b_semantic/s5_06/sequence.json) is retained.
- **07, valid incomplete:** baseline course and recent earlier-stage comparisons
  do not answer the requested recent course-peer comparison. Personal insufficiency
  is displayed; the needed recent course evidence was retrieved.
- **08, valid incomplete:** recent course evidence is selected only as personal
  change; peer selections use baseline windows. The recent peer insufficiency
  answer is omitted. [Selections and results](artifacts/stage5/comparison/qwen14b_semantic/s5_08/sequence.json).

The preserved [frozen taxonomy](artifacts/stage5/reports/comparison.json) reports
7B compact identifier errors in two episodes, schema errors in eight, and support
and scope errors in one each; categories overlap. Its false insufficiency on case
08 was rejected. Full specifications retain layout errors, especially missing
trajectory/observation/assessment panels and excessive lists. A 14B full case 02
directional conclusion was rejected and repaired. No comparison generation was
truncated: all 137 reached recorded EOS below the 1,500-token ceiling and all raw
comparison outputs parse as JSON. JSON syntax was not the principal failure.

The frozen error string classifier misses one additional 7B full layout episode
(01), the 14B full unsupported directional conclusion (02), and tool-budget denials
on 7B full 11/12 and 7B compact 11. A separately labeled
[post-hoc trace annotation](artifacts/stage5/reports/trace_audit.json) records them;
primary scores and frozen reports are unchanged. Thus layout errors affected seven
7B full episodes and four 14B full episodes, including repaired cases. Tool-budget
denials prevented excess requests and are not infrastructure failures.

Neither interface accepts arbitrary numeric claim values. Source-bound validation
recomputed estimates, labels, support, counts, trajectory values and intervals.
Zero explicit numeric-description selections on unsupported evidence were observed;
invented identifiers, false insufficiency, invalid scope and unsupported direction
are separate semantic failures, not proof that every attempted answer was sound.

Compact compilation supplied 11 panels for 7B and 14 for 14B, but zero comparison
or personal-change claims and zero additional analyses. Required answer items
attributed to shared/compiler context were 0, 1, 2, 0 and 1 respectively in the
condition order above. All 18 accepted semantic outputs reconstruct identically
from saved selections. The compiler did not fill the omitted recent peer answers,
which remain incomplete in scoring and on screen.

## Costs and resource accounting

| Condition | Tool calls | Exact / equivalent duplicate calls | Generations | Input / output tokens | Episode seconds | Peak allocated / reserved GiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Enumeration | 42 | 0 / 0 | 0 | 0 / 0 | 18.48 | N/A |
| 7B full | 53 | 2 / 6 | 41 | 185,088 / 15,141 | 388.87 | 15.89 / 21.46 |
| 7B compact | 37 | 0 / 3 | 40 | 149,994 / 8,245 | 219.84 | 15.55 / 19.71 |
| 14B full | 36 | 0 / 2 | 31 | 115,007 / 9,163 | 456.94 | 29.29 / 32.21 |
| 14B compact | 40 | 0 / 4 | 25 | 86,368 / 4,905 | 249.29 | 29.59 / 32.21 |

Equivalent duplicates account for different registry labels resolving to the same
feature/group/window; exact duplicates use the narrower request definition.
Episode totals include analytical execution and rendering, exclude shared model
loading/profile costs, and are descriptive. The baseline used the same host CPU.
It was complete with no model cost; even 14B compact's episode total was about
13.5 times larger, before shared loading. This is not a controlled throughput claim.

**143/208 attempted generations:** 137/192 comparison plus 6/16 setup/profiling;
81 comparison calls used 7B and 56 used 14B. No repair or failed episode was excluded.
Maximum observed comparison input/output lengths were 9,082/1,410 tokens for 7B
and 6,934/574 for 14B. The separate full-bound probes cover the intended 16,000/1,500
limits. CUDA event time for comparison generations totals 1,240.49 seconds; this
is not the model-process or pod-billing duration.

| Model process | Seconds, including initialization and cleanup |
| --- | ---: |
| 14B capacity setup | 116.99 |
| 7B capacity setup | 58.55 |
| 7B comparison block | 635.95 |
| 14B comparison block | 747.34 |
| **Cumulative model-process time** | **1,558.82 (25m 58.82s), below two hours** |

Comparison shared initialization was 24.62s for 7B and 37.79s for 14B; shared
profile/warm-up was 1.56s and 2.21s. These are recorded once per model block and
not assigned to either interface. [Model ledger](artifacts/stage5/model_ledger.jsonl),
[runtime records](artifacts/stage5/gpu), [stage ledger](artifacts/stage5/execution.jsonl)
and [run manifest](artifacts/stage5/run_manifest.json) separate model, acquisition
and wall-clock time. Stage start was 2026-09-18 21:58:44 UTC; the manifest records
the handoff snapshot and elapsed duration. Pod billing time is unknown.

[Post-run device check](artifacts/stage5/checks/device_after_completion.json) confirms
all four owned model PIDs exited, no GPU compute process remained and GPU memory
was 2 MiB. The browser was closed; no local server was started. Both checkpoints
remain downloaded, and the pod remains running.

## Checks and handoff boundaries

Six focused tests passed. They cover unchanged historical code/artifacts,
equivalent public messages without checkpoint/gold inputs, checkpoint-independent
scoring, pinned files/tokenizers/budgets, person exclusions and the prior reporting
taxonomy gaps. An initial fixture used the wrong existing split-manifest key;
the failed log and corrected final result are preserved. No scientific validator
or scoring rule was relaxed.

The [compatibility audit](artifacts/stage5/checks/scoring_compatibility.json)
reproduces eight scoring endpoints on all 24 saved Stage 4 agent results under
either checkpoint label. [Preparation reproduction](artifacts/stage5/checks/preparation_reproduction.json)
matches selection and independent facts. [Final verification](artifacts/stage5/checks/final_verification.json)
passed: 4,041 historical files and all 88 frozen files unchanged; twelve new people
disjoint from 45 earlier people and 8,583 reserved identifiers; exact replay of 46
accepted bound tables/charts/SVGs/provenance records; recompilation of all 18 accepted
compact outputs; identical initial public messages between checkpoints for all 24
interface/case pairs; actual CUDA execution and all budgets checked. Only reserved
split identifiers were read for exclusion, never reserved observations.

[Browser inspection](artifacts/stage5/inspection/browser.json) checked 23 accepted
pages among 31 prespecified slots; eight rejected slots remain visible in the log.
Ten screenshots were visually inspected across all six families and five conditions.
[Visual notes](artifacts/stage5/inspection/VISUAL_REVIEW.md) record repeated panels,
unavailable/zero-bar presentation limitations and specific incomplete answers.
This is not independent human review. No inference was used for replay or inspection.

[Preflight notes](artifacts/stage5/checks/preflight_notes.json) preserve one corrected
test-fixture key and one corrected metadata transfer command before freeze. The
only post-hoc reporting addition is the explicitly labeled error-taxonomy annotation;
no comparison protocol, prompt, score, source, compiler or statistical definition
changed. No trial was rerun. Setup capacity computation past EOS is disclosed above
and did not alter comparison decoding.

## Representative outputs and reproduction

Every accepted case directory contains `question.json`, `spec.json`, `evidence.json`,
`bound.json`, `selection_provenance.json`, self-contained HTML, Vega-Lite, SVG and PNG.
Original generation inputs/outputs/metadata, observable tool sequence and errors
remain under each condition and [GPU generations](artifacts/stage5/gpu/generations).

| Family | 14B compact HTML | Screenshot | Interpretation |
| --- | --- | --- | --- |
| Personal | [01](artifacts/stage5/comparison/qwen14b_semantic/s5_01/accepted/dashboard.html) | [PNG](artifacts/stage5/inspection/qwen14b_semantic_s5_01.browser.png) | Complete, repeated personal panel |
| References | [03](artifacts/stage5/comparison/qwen14b_semantic/s5_03/accepted/dashboard.html) | [PNG](artifacts/stage5/inspection/qwen14b_semantic_s5_03.browser.png) | All three comparisons visible |
| Observation | [05](artifacts/stage5/comparison/qwen14b_semantic/s5_05/accepted/dashboard.html) | [PNG](artifacts/stage5/inspection/qwen14b_semantic_s5_05.browser.png) | Complete with compiler assessment context |
| Insufficiency | [07](artifacts/stage5/comparison/qwen14b_semantic/s5_07/accepted/dashboard.html) | [PNG](artifacts/stage5/inspection/qwen14b_semantic_s5_07.browser.png) | Valid but recent course answer omitted |
| Assessment | [09](artifacts/stage5/comparison/qwen14b_semantic/s5_09/accepted/dashboard.html) | [PNG](artifacts/stage5/inspection/qwen14b_semantic_s5_09.browser.png) | Both requested means and limitations visible |
| Windows | [11](artifacts/stage5/comparison/qwen14b_semantic/s5_11/accepted/dashboard.html) | [PNG](artifacts/stage5/inspection/qwen14b_semantic_s5_11.browser.png) | Personal and all peer answers visible |

For a complete insufficiency answer see [enumeration 07](artifacts/stage5/comparison/baseline/s5_07/accepted/dashboard.html).
For rejection inspect [14B compact 06](artifacts/stage5/comparison/qwen14b_semantic/s5_06/sequence.json)
and [14B full assessment 09](artifacts/stage5/comparison/qwen14b_full_spec/s5_09/sequence.json).
Selection follows the frozen rule, not attractive results.

```bash
.venv/bin/python -m pytest -q tests/test_stage5.py
.venv/bin/python scripts/stage5/verify.py --replay --output /tmp/stage5-verification.json
.venv/bin/python - <<'PY'
from trajectory_dashboards.stage5.core import Engine
from trajectory_dashboards.stage5.adapter import replay
replay(Engine(), 'artifacts/stage5/comparison/qwen14b_semantic/s5_01/accepted', '/tmp/stage5-replay')
PY
```

See [full reproduction commands](docs/stage5/REPRODUCTION.md) for preparation,
CPU analysis, saved dashboard replay, rescoring and separately authorized GPU
reproduction. Commands use fresh destinations and preserve original results.

## Operational and research-direction decision

**Ready to use within this prototype:** deterministic enumeration over the existing
small task/reference registry, reproducible analytical tools, source validation and
saved dashboard replay. It answered all twelve cases, including separate insufficiency
questions, with much lower cost. This does not establish unrestricted natural-language
understanding, pedagogical validity or suitability for decisions about students.

**Established by this experiment:** the fixed 14B compact checkpoint/interface
produced seven more visibly complete answers than fixed 7B compact on the same
twelve people, with zero observed accepted unsupported numeric answers. Six of
those gains remain under method-selected attribution. The prespecified substantial
gain criterion is met, but the 11/12 gate is not; no agent condition reaches it.
The full-interface checkpoint gain is only one case, and compact is worse than full
for 7B but better for 14B. These descriptive results support a checkpoint/interface
interaction hypothesis, not a general agent limitation or a pure model-size cause.

**Next bounded recommendation, requiring review rather than automatic execution:**
retain enumeration operationally; do not start broader agent evaluation yet.
Review one explicit answer-binding intervention: tie a selected answer to a public
requested comparison identity (feature, focal window, reference window and peer or
personal scope), and reject mismatched bindings before finalization. It must derive
from public question semantics, provide no gold checklist, run no missing analyses
and insert no omitted answers. Cases 06–08 give a concrete mechanism to test; they
do not establish that this intervention will work. Any future test needs a new
frozen comparison against unchanged 14B compact and enumeration. Further generic
prompt-policy tweaking or a larger-model sweep is not justified here. Nothing in
that proposed stage was implemented or executed.

**Possible contribution:** an empirical study of reliability and division of
responsibility in evidence-grounded dashboards, separating evidence retrieval,
selection, numerical correctness, compiler context and visible answer completeness.
LLM-guided analysis and staged visualization generation are already established by
[InsightPilot](https://arxiv.org/abs/2304.00477) and
[LIDA](https://aclanthology.org/2023.acl-demo.11/). The
[focused contribution assessment](docs/stage5/CONTRIBUTION.md) therefore makes no
novelty claim based on tool use or chart compilation alone. A stronger checkpoint
does not create novelty or an advantage over enumeration. If external review finds
that this narrow reliability question has insufficient scientific value, change
the research question materially instead of continuing to optimize this registry.

**Still needed:** independent human review of rubrics, interpretation rules,
estimands and dashboard usability; focused additional prior-art review before any
contribution claim; and separately authorized validation on genuinely unopened
data if a fixed system later meets its engineering gate. Twelve development people,
known question families, one wording and one greedy run per condition cannot
establish generalization or repeatability. Model blocks are not a hardware-controlled
timing experiment. The checkpoints differ in more than parameter count.

Statistical assumptions remain descriptive: equal eligible person-week weighting,
changing peer composition and unequal histories, repeated source rows retained,
person-bootstrap reference-mean intervals, no personal-change/contrast uncertainty,
no individual prediction interval, no causal adjustment, and unknown logging and
grade-availability times. The mixed-model artifact is not used as a detector or
dashboard claim source. No reserved observations, additional dataset, training,
model sweep, full research evaluation or manuscript work was opened. Stage 5 stops
with this handoff.
