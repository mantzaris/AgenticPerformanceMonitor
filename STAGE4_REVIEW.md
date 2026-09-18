# Stage 4 review entry point

**Stage 4 complete; engineering readiness target failed. Retain deterministic
enumeration for this task class.** Complete valid answers were 12/12 for enumeration,
3/12 for the full-specification agent and 4/12 for the compact-interface agent.
Compact output was more often valid and cheaper than full output, but did not reach
the prespecified 11/12 target. All accepted quantitative answers passed the shared
source-bound validator. Work is on main; historical artifacts and scores are
unchanged. The reserved population remains closed. No additional stage was begun.

Starting commit: `64c28dff1c2ba82c5abef789c9b21e2fe67f6740`.
Initial construction: `7a1220fa3c97702e31d79ba9099aedf6b531bdb2`.
Flat-envelope format check: `d6283f162108998c18360654693b49cce72a1033`.
Final pre-freeze implementation/protocol: `227653149b87121d05f570852ba186597e08c7ed`.
Frozen pilot execution: `05f3cdcdb67bb6d1760d398b805bd962b60140b5`.
Results/handoff commit: `0beb1bc509831d907662185f65f68ca8ccec8a70`; pushed and verified on
`origin main`. [Publication record](artifacts/stage4/publication.json) records the
successful push and total elapsed time of **61.00 minutes**
through results publication. The final metadata commit is the subsequent main tip (`git rev-parse HEAD`), with its full
SHA reported in the completion message. History is preserved without force-push.

## Read first

- [Scope and ceilings](docs/stage4/SCOPE.md), [frozen analysis/evaluation protocol](docs/stage4/PROTOCOL.md), [semantic mapping](docs/stage4/INTERFACE.md), [shared interpretation rules](docs/stage4/PUBLIC_INTERPRETATION.md).
- [Freeze manifest](artifacts/stage4/protocol/freeze.json): 68 files, digest `7d3cb0f8b352fe1a28c887a3fcb37eb2fef1cf1cfe02afd234238d99a0283650`.
- [Questions and selection](artifacts/stage4/tasks/manifest.json), [evaluator-only independent facts](artifacts/stage4/evaluator_only/rubrics.json), [balanced execution order](artifacts/stage4/protocol/execution_order.json), [exact interface differences](artifacts/stage4/protocol/interface_differences.json).
- [Reproduction commands](docs/stage4/REPRODUCTION.md), original [Stage 3 handoff](STAGE3_REVIEW.md), and [research plan](Agentic_Longitudinal_Dashboards_Research_Plan.md).

## Hypothesis and Stage 3 diagnosis

**Under the same model, analytical tools, evidence validation, and inference budget,
separating semantic answer selection from dashboard layout construction improves
complete, valid answers.** This is a hypothesis motivated by observed failures,
not an established explanation of them.

The unchanged saved scores confirm complete answers of 24/24 for enumeration,
11/24 for generic, 11/24 for the previous reference-sensitive policy and 6/24 for
the coverage-aware policy. Source-validated retrieved evidence could support
admissible answers to 24/24, 24/24, 22/24 and 23/24 questions respectively under an
**offline, evaluator-assisted evidence-availability upper bound**. That bound is
not a deployable selection method or agent success and never enters new inference.

Of 28 rejected agent episodes, 26 ended with panel/claim structural errors, one
with invalid JSON and one with an excessive request map. Six generic rejected
episodes had a complete intended visible selection in at least one attempt when
layout is ignored and the same standard compiler context is included. Other
episodes also omitted needed selections or made unsupported conclusions. These
are overlapping mechanisms, not exclusive causal labels. The complete trace-level
[diagnosis](artifacts/stage4/diagnostics/DIAGNOSIS.md), [case records](artifacts/stage4/diagnostics/stage3_cases.json)
and [terminal errors](artifacts/stage4/diagnostics/terminal_failures.json) preserve
the distinction between available evidence, attempted selection and accepted output.

No Stage 3 output reached its 1,500-token ceiling. Original finish/EOS reasons were
not recorded, so malformed JSON is not classified as truncation solely from length.
No logical contradiction in the panel obligations was demonstrated. Stage 4 now
records ending tokens, EOS and ceiling termination. This audit is automated/code
review, not independent human scientific review.

## Intervention and safeguards

The generic investigation policy is identical in both agent conditions and matches
the old generic policy text. There is no coverage map, phase policy, tool-routing
change or deduplication intervention. Both agents have the same model, data,
question, public rules, tools, ceilings and generation schedule. Only interface
instructions, final schema and the semantic compiler path differ.

The full interface retains the original Specification and manual selection of
evidence, claims, panels and conclusion. Compact finals have explicit semantic
intents, returned evidence IDs, support mode and conclusion scope. Intents cover
peer comparison, personal change, assessment states, observation states and
measurement limitations. A peer comparison also exposes the focal mean; no new
focal-only numerical primitive was introduced. Numeric calculations remain in
the unchanged backend and independent source validator.

The compiler inserts required layout and contextual panels, with provenance, but
never runs additional analysis or selects an unrequested quantitative answer.
Personal-only selection does not insert a peer window comparison, and peer-only
selection does not insert personal change. Context-only evidence receives at most
the existing measurement boilerplate as its mandatory claim. Only explicitly
selected evidence is bound. Unknown IDs, false insufficiency, unsupported estimates
and unsupported conclusions are rejected. Exact mapping and scope constraints are
in [INTERFACE.md](docs/stage4/INTERFACE.md).

The common panel contract and source-bound validation are unchanged. Stage 3's
controlled renderer is reused; a shared wrapper labels Stage 4, exposes provenance
and omits the inapplicable Stage 3 follow-up form from these read-only exports.
Each substantive comparison/change must trace to a semantic selection. Compiler
context can incidentally answer an observation/assessment-context request; this
receives compiler attribution, not method-selected credit.

Visible answer semantics and requirements are unchanged. A provenance projection
using those same predicates distinguishes method-selected from compiler-supplied
answers. [Compatibility audit](artifacts/stage4/checks/scoring_compatibility.json)
reproduces all eight checked scoring endpoints for all 96 original Stage 3 results.
No old score was edited. No rubric or oracle answer selection is model/compiler input.

## Construction and frozen design

Six known Stage 3 cases tested the initial nested semantic envelope. All six
failed: five had root-versus-nested field problems among their errors; another
made an unsupported insufficiency selection. They remain preserved. Before freeze,
the final envelope was flattened, without relaxing any substantive validation.
One remaining construction generation checked that format using saved known-case
tool results and produced a valid compiled export. This was a format check, not
a successful investigation episode or pilot evidence.

A failed initial GPU startup omitted the split manifest from the transfer; the
verified existing manifest was supplied. Its 24.375 seconds count toward process
runtime, with zero generations. A local reproduction attempt found a browser script
shadowing Python's `inspect`; it was renamed before freeze and the failure log kept.
[Construction accounting](artifacts/stage4/checks/construction_summary.json)
records all 24 construction and two pre-pilot profiling generations.

The twelve new focal people were selected by fixed seeded administrative criteria,
without examining activity magnitudes or method performance. There are two cases
per existing family and one explicitly measured/windowed question per person.
All 33 prior focal people and these twelve are excluded from the fixed peer pool
across registrations. Fresh preparation reproduced all questions and independently
calculated rubric facts. Source observations were copied unmodified.

Enumeration runs on the same GPU host CPU. Full and compact conditions each run
once per person, alternating first position within each family. One shared pilot
model load serves all 24 agent episodes. This is twelve paired development cases,
not new task families, stochastic repeatability or held-out generalization.
The frozen target is at least 11/12 compact complete valid visible answers and no
accepted unsupported quantitative answer; selected-answer completeness is separate.

## Complete frozen results

Every frozen case is included. First-final validity means the first attempted
final specification passed, not that the first generation was a final answer.
There were no deterministic fallbacks and no repeated pilot episodes.

| Endpoint (denominator 12 per method) | Enumeration | Full specification | Compact semantic |
| --- | ---: | ---: | ---: |
| First-final validity | 12 | 4 | 7 |
| Valid after at most one repair | 12 | 5 | 7 |
| Complete valid visible answers | 12 | 3 | 4 |
| Complete method-selected answers | 12 | 3 | 4 |
| Accepted unsupported quantitative answers | 0 | 0 | 0 |
| Oracle retrieved-evidence availability bound | 12 | 12 | 11 |
| Episodes attempting a repair | 0 | 8 | 5 |
| Episodes with a panel/claim-contract error | 0 | 8 | 0 |
| Correctly scoped insufficient-answer items (4 requested) | 4 | 1 | 0 |

The primary descriptive difference is **one additional complete answer (4 versus
3 of 12)**. Paired outcomes are two improvements, one regression, two unchanged
complete and seven unchanged incomplete. Visible and method-selected completeness
agree on every case; compiler context does not account for the extra complete case.

| Case / family | Full specification | Compact semantic | Paired completeness |
| --- | --- | --- | --- |
| 01 personal | Valid; recent course comparison omitted | Complete | Improved |
| 02 personal | Complete | Valid; recent course comparison omitted | Regressed |
| 03 references | Complete after repair | Complete | Unchanged complete |
| 04 references | Complete | Complete | Unchanged complete |
| 05 observation | Rejected: observation panel missing | Rejected: unknown evidence ID; no tools executed | Unchanged incomplete |
| 06 observation | Rejected: assessment panel missing | Rejected: insufficiency assigned to general context | Unchanged incomplete |
| 07 support | Valid; peer comparison omitted | Rejected: invalid semantic intent kind | Unchanged incomplete |
| 08 support | Rejected: trajectory panel missing | Rejected: insufficiency conclusion scope | Unchanged incomplete |
| 09 assessment | Rejected: assessment panel missing | Valid; scheduled-no-submission answer omitted | Unchanged incomplete |
| 10 assessment | Rejected: trajectory panel missing | Valid; scheduled-no-submission answer omitted | Unchanged incomplete |
| 11 alternate windows | Rejected: 11 panels exceeds contract | Complete | Improved |
| 12 alternate windows | Rejected: 11 claims/panels exceeds contract | Rejected: reference conclusion scope | Unchanged incomplete |

Enumeration is complete on all twelve rows. The detailed [per-case JSON](artifacts/stage4/reports/per_case.json),
[CSV](artifacts/stage4/reports/per_case.csv), [paired records](artifacts/stage4/reports/paired_cases.json)
and [aggregate report](artifacts/stage4/reports/comparison.json) retain all errors,
missing items, compiler contributions and costs. Each episode directory under
[pilot](artifacts/stage4/pilot) contains its original requests, results, raw output,
stopping decisions and validation errors. Accepted outputs additionally contain
specification, bound evidence, provenance, HTML, SVG and PNG.

Full retrieved sufficient evidence for every question; its accepted dashboards
omit two requested answer items. Compact omitted three items in its accepted
dashboards and failed to retrieve five required items in case 05. Across rejected
and accepted episodes the frozen scorer counts 34 full and 19 compact
retrieved-but-omitted items; rejected dashboards have no accepted visible answers,
so those totals are not a count of deliberate omissions in otherwise valid pages.
The oracle bounds are diagnostic availability only, not agent successes.

Compact compilation eliminates the observed panel/claim-contract errors, but
**does not eliminate schema or semantic errors**. Its five terminal failures concern
an unknown identifier, context support, an invalid intent literal and two conclusion
scopes. The frozen coarse `semantic_or_substantive_error_episodes` counter reports
three compact episodes because its string matching misses the context-support and
intent-literal errors. This reporting limitation is disclosed in a separate
[terminal-error audit](artifacts/stage4/reports/terminal_error_audit.json), without
changing frozen primary scores or rerunning anything. All 81 pilot generations
ended on EOS; none reached the output-token ceiling. Truncation does not explain
these pilot failures.

Case 01's gain occurs with both interfaces valid, so it is an answer-selection
change; case 11's gain accompanies removal of a structural rejection. The interface
can influence investigation and selection even with identical investigation-policy
text. Explicit compact support/scope fields also create failure opportunities that
the full templates partly handle implicitly. This tests the frozen interface
package, not an isolated causal mediation effect of layout alone.

## Compiler accounting and visual inspection

Across seven accepted compact episodes the compiler adds twelve layout/context
panels, zero quantitative comparison/change claims and zero extra boilerplate
claims. Four requested contextual items (assessment states and measurement
availability in cases 09 and 10) are compiler supplied. Those cases remain
incomplete because scheduled non-submission was retrieved but not selected. The
shared caveat text is not credited as agent investigation.

An additional [direct selection audit](artifacts/stage4/checks/selection_audit.json)
compares raw final selections to every accepted compact quantitative claim and
comparison panel using a small [separate check](artifacts/stage4/checks/selection_audit.py).
It calls neither the production compiler nor evaluator: bound evidence IDs equal
explicitly selected IDs, and quantitative claims equal the selected intent mapping.
No extra peer answer is inferred from personal change or from unselected retrievals.
Compiler-added trajectories still show the shared required context; those panels
do not count as an unselected window-mean answer. This supplemental check was added
after inference for verification, not to change selection, scoring or the frozen run.

The frozen inspection rule selected cases 01, 03, 05, 07, 09 and 11 across all
three methods: thirteen accepted pages among eighteen slots, with five failures
retained. Chromium 153.0.8010.36 opened each accepted page, exercised provenance
and checked bound visible text, with no browser errors. Codex visually inspected
seven screenshots spanning all six families, including an accepted incomplete full
dashboard. [Visual notes](artifacts/stage4/inspection/VISUAL_REVIEW.md) document
repeated panels, tall pages and zero-height bars; no renderer was changed after
freeze. This is not independent human review.

| Family | Representative dashboard | Browser screenshot |
| --- | --- | --- |
| Personal | [Compact 01](artifacts/stage4/pilot/semantic/s4_01/accepted/dashboard.html) | [PNG](artifacts/stage4/inspection/semantic_s4_01.browser.png) |
| Reference | [Compact 03](artifacts/stage4/pilot/semantic/s4_03/accepted/dashboard.html) | [PNG](artifacts/stage4/inspection/semantic_s4_03.browser.png) |
| Observation | [Baseline 05](artifacts/stage4/pilot/baseline/s4_05/accepted/dashboard.html) | [PNG](artifacts/stage4/inspection/baseline_s4_05.browser.png) |
| Insufficient support | [Baseline 07](artifacts/stage4/pilot/baseline/s4_07/accepted/dashboard.html), [incomplete full 07](artifacts/stage4/pilot/full_spec/s4_07/accepted/dashboard.html) | [Baseline PNG](artifacts/stage4/inspection/baseline_s4_07.browser.png), [full PNG](artifacts/stage4/inspection/full_spec_s4_07.browser.png) |
| Assessment | [Incomplete compact 09](artifacts/stage4/pilot/semantic/s4_09/accepted/dashboard.html) | [PNG](artifacts/stage4/inspection/semantic_s4_09.browser.png) |
| Alternate windows | [Compact 11](artifacts/stage4/pilot/semantic/s4_11/accepted/dashboard.html) | [PNG](artifacts/stage4/inspection/semantic_s4_11.browser.png) |

## Cost, GPU verification and stopping

| Frozen pilot cost | Enumeration | Full specification | Compact semantic |
| --- | ---: | ---: | ---: |
| Analytical calls | 42 | 54 | 42 |
| Exact / equivalent repeated calls | 0 / 0 | 1 / 5 | 0 / 3 |
| Attempted generations | 0 | 42 | 39 |
| Prompt / output tokens | 0 / 0 | 197,891 / 16,031 | 153,878 / 8,500 |
| Summed episode seconds | 18.14 | 408.96 | 224.42 |
| Generation seconds | 0 | 389.41 | 215.39 |

All analytics ran on the same GPU host's CPU. Compact used about 47% fewer output
tokens and 45% less episode time than full. Enumeration remained both more complete
and much cheaper. Timing is descriptive; it is one counterbalanced run, not
repeatability or a controlled throughput benchmark. Shared pilot initialization
24.05 seconds and profiling/warm-up 1.33 seconds are not allocated to either agent.

The reused model is Qwen/Qwen2.5-7B-Instruct, revision
`a09a35458c702b33eeacc393d103063234e8bc28`, Transformers 4.55.2, Torch 2.8.0+cu128,
BF16, no quantization or CPU offload. Greedy decoding uses a 1,500 output-token
ceiling and the same 16,000 input-token limit. Existing weight hashes matched;
no model download occurred. The actual device is NVIDIA RTX 6000 Ada Generation,
driver 580.159.04, 49,140 MiB. [Runtime proof](artifacts/stage4/gpu/pilot_04/runtime.json)
records CUDA kernel profiling, all parameters on cuda:0, per-generation CUDA
input/output devices and the model's observed GPU process/VRAM. CUDA availability
alone was not used as evidence.

**108 total attempted generations:** 24 construction, 81 pilot and three setup.
All are counted, including construction failures. Four process intervals total
**911.266 seconds (15 minutes 11 seconds)**, including the failed initial startup,
loading, CPU work inside the process and cleanup. The pilot used one shared model
load. [Append-only model ledger](artifacts/stage4/model_ledger.jsonl),
[execution ledger](artifacts/stage4/execution.jsonl) and
[run manifest](artifacts/stage4/run_manifest.json) record the partitions and stage
wall-clock separately. Stage wall-clock through handoff preparation is **58.06 minutes**
(from 20:45:17Z to 21:43:20Z); subsequent Git publication is recorded
separately. Pod billing time is unknown.

The final model process exited successfully at 2026-09-18T21:27:57Z. The subsequent
[device check](artifacts/stage4/checks/device_after_completion.json) found no compute
processes and 2 MiB used. All Stage 4 model processes are stopped. No local server
was started; the inspection browser is closed. The pod remains running.

## Verification, deviations and remaining review

| Requirement | Status and evidence |
| --- | --- |
| Preserve history, frozen design and closed reserved population | PASS: [verification](artifacts/stage4/checks/final_verification.json), 3,176 historical files and 68 frozen files unchanged; 12 new people, 33 prior people and 8,583 reserved IDs excluded appropriately |
| Narrow interface/provenance and shared evaluator checks | PASS: [31 focused tests](artifacts/stage4/checks/final_prefreeze_tests.txt); 15 Stage 4 and 16 Stage 3 tests; [96-output scoring compatibility](artifacts/stage4/checks/scoring_compatibility.json) |
| Fresh selection and independent facts reproduce | PASS: [preparation check](artifacts/stage4/checks/preparation_reproduction.json); separate row-loop facts, not external human gold |
| Same source-bound integrity and no inserted quantitative answers | PASS for all 24 accepted pilot outputs; [direct selection audit](artifacts/stage4/checks/selection_audit.json) for all seven accepted compact outputs |
| Saved outputs replay without inference | PASS: 25 exact bound/chart/SVG/provenance replays and eight semantic recompilations, including the separate construction-format artifact |
| All frozen episodes retained, genuine GPU inference, budgets respected | PASS: 36 method results, 24 agent episodes, [runtime and ledgers](artifacts/stage4/gpu/pilot_04/runtime.json) |
| Representative rendered inspection | PASS within one desktop browser; [notes and limitations](artifacts/stage4/inspection/VISUAL_REVIEW.md) |
| Compact engineering target: 11/12 complete and no accepted unsupported quantity | FAIL: 4/12 complete; quantitative-integrity condition passes |
| Independent human scientific/usability review | NOT ATTEMPTED; still required |

There were no frozen-pilot reruns, prompt/code/rubric changes or score substitutions.
Construction envelope revision, missing-transfer-manifest recovery and script-name
collision were resolved and documented before freeze; failed attempts remain saved.
The post-pilot terminal taxonomy and direct provenance audit are disclosed additions
to reporting/verification, not changes to the frozen evaluator or experiments.

Statistical assumptions remain those of the descriptive backend: observed weekly
means with person weighting, changing eligible peer composition, unequal available
history, unknown logging completeness, withheld grade availability and unverified
assessment obligations. Person-bootstrap intervals concern peer means; neither
personal changes nor individual-versus-reference differences have uncertainty
intervals. No mixed-model detector or causal claim was introduced. Repeated source
rows retain the primary treatment documented and sensitivity-checked earlier.

Twelve new development people, one question per person, known task families and
one greedy run cannot establish generalization, repeatability or model superiority.
The rubric and implementation audits still need external scientific review. The
Stage 3 evidence upper bound uses evaluator-only information and is not a deployable
capability. The compact compiler's source and provenance checks support a narrow
division of responsibility, but the pilot does not establish reliable complete
answers from the model.

**Recommendation: retain deterministic enumeration for this task class.** Do not
proceed to broader agent evaluation on these results. A next separately authorized
bounded step would be external review of the answer contract, insufficiency scope
and repeated-content usability, using these saved examples without new inference.
Any later architecture revision needs its own preregistered development check.
This stage ends with the negative readiness result; no new policy, larger model,
reserved-population evaluation, broad simulation or manuscript was started.

## Reproduce without inference

```bash
.venv/bin/python -m pytest -q tests/test_stage3.py tests/test_stage4.py
.venv/bin/python scripts/stage4/verify.py --replay --output /tmp/stage4-verification.json
.venv/bin/python artifacts/stage4/checks/selection_audit.py
```

[Full commands](docs/stage4/REPRODUCTION.md) cover fresh preparation, independent
fact reproduction, analysis, saved replay, rescoring and optional newly authorized
GPU reproduction in a fresh workspace. No additional inference is needed to inspect
the handoff. Saved attempted episodes and reports refuse replacement.
