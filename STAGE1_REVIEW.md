# Stage 1 independent-review handoff

**Ready with specified limitations. Stage 1 is complete; stop here.** The data,
analytical tools, three deterministic demonstrations and a genuine GPU tool loop
work. One of the three agent cases failed after its allowed repair, and one of
the two mixed-model fits failed. Neither is represented as success. This stage
does not establish agent superiority, generalization, estimator calibration or
publication readiness.

Branch: `stage1/research-foundations`.
Validated implementation commit: `c801f1bda91fa9ee4e7e84c3dcb6b3e4227cf6ea`.
GPU execution source commit: `53187de3a55be7be0331d1e0fd200339af1c4c82`.
The final handoff commit is the branch tip (`git rev-parse HEAD`), reported in the
completion message. This documentation/metadata commit leaves the validated
implementation source unchanged. No default-branch merge or force-push is intended.

**Remote status:** the authorized branch push was attempted and failed because
GitHub HTTPS credentials were unavailable (`could not read Username`, terminal
prompts disabled). No branch was published. The complete local branch is ready
for review; after authenticating, use `git push -u origin stage1/research-foundations`.

Stage started **2026-09-18 16:09:04 UTC**. Handoff artifacts froze at
**2026-09-18T16:46:15.026661+00:00**, after **2231.03 seconds** of stage wall time.
Final Git transport is outside that artifact-freeze measurement. Local model
process runtime was **138.151591 seconds** including imports, model loading,
generation, tool dispatch, rendering and cleanup. GPU billing time is unknown.

## Read first

- [Frozen scope and exclusions](docs/STAGE1_SCOPE.md)
- [Time, feature and statistical semantics](docs/TIME_AND_STATISTICS.md)
- [Focused literature overlap](docs/LITERATURE_OVERLAP.md)
- [Dataset audit](artifacts/data/AUDIT.md), [dataset manifest](artifacts/data/manifest.json)
- [Machine-readable run manifest](artifacts/stage1_run.json), [verification](artifacts/verification.json)
- [Original plan, preserved unchanged](Agentic_Longitudinal_Dashboards_Research_Plan.md)

No applicable AGENTS.md or existing implementation was found. The initial working
tree contained only the tracked license and the untracked supplied plan. The plan
was preserved byte-for-byte and included in the Stage 1 branch. The GPU host's
existing PyTorch runtime was reused; dependencies were isolated in a project venv.

## Implemented behavior and acceptance

The CPU pipeline downloads and audits OULAD, reserves people across all their
registrations, derives five cutoff-safe weekly features and selects three cases
without searching for striking results. An analytical dispatcher produces
typed evidence, with personal history, course/subgroup comparisons, observation
states, denominator tables and explicitly labeled bootstrap intervals. A
constrained JSON specification selects evidence and panels; deterministic code
inserts all displayed numerical values. The model cannot supply executable code.
Saved HTML includes expandable evidence inspection; SVG/PNG export the charts.

| Acceptance criterion | Result | Evidence |
| --- | --- | --- |
| Bounded Stage 1 scope and focused prior-art check | PASS | `docs/STAGE1_SCOPE.md`, `docs/LITERATURE_OVERLAP.md` |
| Real source data, license, hashes, schemas and independent counts | PASS | `artifacts/data/manifest.json`, `AUDIT.md` |
| Two structurally supported presentations | PASS | `artifacts/data/preparation.json` |
| Person-grouped reserved split; no reserved analysis/examples | PASS | `artifacts/data/splits.json`, `artifacts/verification.json` |
| Explicit as-of semantics; scores/future labels excluded | PASS | `docs/TIME_AND_STATISTICS.md`, cutoff fixtures in `tests/test_boundaries.py` |
| Zero, unknown, ineligible and scheduled non-submission distinguished | PASS | `src/trajectory_dashboards/prepare.py`, observation/assessment tables in each evidence package |
| Population, subgroup and personal-history analyses | PASS | `artifacts/deterministic/dev_1`, `dev_2`; typed requests and evidence |
| At least one suitable mixed model; failures preserved | PASS | `artifacts/statistics/mixed_models.json`: BBB converged, AAA failed; descriptive fallback labeled |
| Typed contracts and semantic validation | PASS | `artifacts/schemas/`, `dashboard.py`, semantic rejection tests |
| Three materially different real-data deterministic dashboards | PASS | `artifacts/deterministic/dev_1`, `dev_2`, `dev_3` |
| Actual GPU generation → requested tool → returned result → accepted specification | PASS | `artifacts/gpu/generations/`, `dev_1`, `dev_2`, `runtime.json` |
| Attempt all three questions within limits | PASS | Eight generations, eight dispatched analytical requests, `artifacts/gpu/ledger.jsonl` |
| All three agent questions accepted | PARTIAL | One accepted initially, one after repair, one failed; no further repair attempted |
| Agent measurement-limits final specification | FAIL | `artifacts/gpu/dev_3/validation_error_0.json`, `validation_error_1.json`; fallback is separate |
| Focused checks, exports and inference-free replay | PASS | 12 tests; six replayed packages; `artifacts/checks/`, `docs/INSPECTION.md` |
| Full benchmark, additional domains/models, training, manuscript | NOT ATTEMPTED | Explicitly outside authorization |

## Dataset and cohort audit

Creator-deposited [UCI OULAD archive](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset),
retrieved September 18, 2026; **CC BY 4.0**. Attribution: Kuzilek, Hlosta and
Zdrahal, DOI 10.24432/C5KK69. The machine manifest records the exact retrieval
timestamp, download URL and SHA-256 for every source file. Archive SHA-256:
`f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4`.

Observed counts: **28,785 distinct people**, **32,593 student-course registrations**,
**173,912 assessment records**, **10,655,280 interaction rows**, seven modules and
22 presentations. **3,538 people** have multiple registrations. Person counts
must not be replaced by registration counts. The fixed split contains **20,202
development** and **8,583 reserved** people across all registrations.

| Development presentation | Registrations | People with ≥8 fully eligible weeks | Dated non-exam assessments by cutoff |
| --- | ---: | ---: | ---: |
| AAA_2013J | 254 | 239 | 2 |
| BBB_2013B | 1,269 | 1,059 | 3 |

Selection used the first qualifying presentation in each of the first two
qualifying modules in lexical order. No threshold relaxation was needed. There
are **18,276 prepared person-course-weeks**. Focal selection uses a fixed hash;
the third case additionally requires incomplete administrative history. These
are development demonstrations, not eventual held-out benchmark cases.

All audited dimension joins preserve row counts and have no unmatched rows.
The interaction candidate key is not unique: **2,195,960 excess key rows**, including
**787,170 exact repeated-row excess records**. Main preparation sums the source
rows without silently deduplicating them. Equal rows may be genuine contributions;
the archive lacks event identifiers to settle this. A bounded alternative
preprocessing check found 15,937 exact repeated-row excess records among 193,708
selected eligible interaction rows. Dropping them changes magnitudes but not the
direction of the two supported course contrasts in these examples. This is not
a general robustness claim; see `artifacts/data/duplicate_sensitivity.json`.

Missing markers are `?`/empty, not literal dates. There are 45 unknown registration
dates, 22,521 absent withdrawal dates, 173 missing scores, 11 missing assessment
deadlines, and 1,909 banked assessment rows. Withdrawal is recorded for 10,072
registrations; it is not inferred from final-result labels. Course-relative dates,
out-of-course records and resource schedule missingness are detailed in the audit.

## Demonstrations and statistical limits

| Case | Actual result | Saved specification / HTML / chart export |
| --- | --- | --- |
| Personal history | Recent activity is lower than the person's earlier baseline but higher than recent course peers. These are different contrasts. | [spec](artifacts/deterministic/dev_1/spec.json), [HTML](artifacts/deterministic/dev_1/dashboard.html), [PNG](artifacts/deterministic/dev_1/dashboard.png) |
| Reference/stage sensitivity | The focal mean is below all three peer means. The magnitude changes; there is **no sign reversal** in this case. Earlier-stage peers answer a different question. | [spec](artifacts/deterministic/dev_2/spec.json), [HTML](artifacts/deterministic/dev_2/dashboard.html), [PNG](artifacts/deterministic/dev_2/dashboard.png) |
| Measurement limits | No eligible focal observations remain in recent weeks. Earlier zero recorded activity, administrative ineligibility and scheduled submission states are visible. Scores cannot resolve interpretation. | [spec](artifacts/deterministic/dev_3/spec.json), [HTML](artifacts/deterministic/dev_3/dashboard.html), [PNG](artifacts/deterministic/dev_3/dashboard.png) |

Each directory also contains `evidence.json`, `question.json`, `bound.json`,
`chart.vl.json` and `dashboard.svg`. The HTML includes the complete claims and
inspector; PNG/SVG are rendered chart exports, not full-page browser screenshots.
No observations were altered to produce a desired pattern.

The random-intercept Gaussian working model on log1p activity converged for BBB
(1,181 people; 13,151 person-weeks). Random-intercept variance was approximately
0.657 and residual variance 0.511. AAA's fit failed with `Singular matrix` and a
singular-covariance warning; this does not establish that a person effect is absent.
The dashboards use descriptive summaries; the mixed model is a separate feasibility
artifact, not a calibrated detector or an authority for the claims.

Uncertainty comes from 500 person-cluster percentile bootstrap resamples. Intervals
describe a peer mean, not an individual's future observation. There is no personal
prediction interval, formal hypothesis testing or multiplicity claim. Registered
days approximate opportunity, and changing eligibility can change the peer
composition. Prior-attempt availability, fixed assessment schedules, withdrawal-day
conventions, banked exemptions, duplicate rows and informative dropout need domain
review. Scores are withheld entirely because release times are absent. Clicks
cannot establish effort, ability, learning or time spent studying. Annotation
`reference_dependent` identifies a reference-audit question type, not a finding
that the comparison's sign changed.

## GPU test and resources

One model: **Qwen/Qwen2.5-7B-Instruct**, Apache-2.0, revision
`a09a35458c702b33eeacc393d103063234e8bc28`; **Transformers 4.55.2** backend;
PyTorch **2.8.0+cu128**, CUDA runtime **12.8**; BF16, no quantization or CPU offload.
Hardware: NVIDIA RTX 6000 Ada Generation, **49,140 MiB**, driver **580.159.04**.
No model was previously cached. New downloaded files total **15,242,805,751 bytes**
(15.24 decimal GB); weight SHA-256 values were checked against the pinned hub LFS
metadata. See [model manifest](artifacts/gpu/model_manifest.json).

All parameters, generation inputs and output tensors were on `cuda:0`. CUDA events
were timed around generation, the profiler recorded **202,477 CUDA device events**
(including copies) during the first generation, and process-level GPU memory was
observed. Allocated model memory after load was **15,234,903,552 bytes**. These
measurements substantiate actual GPU execution beyond an availability check.

| Question | Generations | Tool calls | Final result |
| --- | ---: | ---: | --- |
| dev_1 | 3 | 3 | Agent-generated and repaired; first output used an unsupported panel type |
| dev_2 | 2 | 3 | Agent-generated and accepted without repair |
| dev_3 | 3 | 2 | Failed: required panel omitted in both final attempts; deterministic fallback separately rendered |

Totals: **8 generations**, including both invalid finals and repairs; **14,685
prompt tokens**, **2,647 completion tokens**; zero warm-up generations. Greedy
decoding, maximum 1,800 new tokens per generation. There was no second model,
training, sweep or paid external inference. The policy is heavily constrained by
typed obligations; this is not a generic-agent comparison or an accuracy estimate.

GPU-process runtime: **138.151591 seconds / 7,200-second ceiling**. Stage wall time
to handoff freeze: **2231.03 seconds / 21,600-second ceiling**.
Generation use: **8 / 20**. These ceilings are enforced by a locked ledger,
pre-generation checks and a process deadline. The original budget is not reset.
The process exited; the GPU then showed 2 MiB and no compute processes.
The existing pod was left running; no allocation change or new pod was made.

Authoritative records: [runtime](artifacts/gpu/runtime.json),
[ledger](artifacts/gpu/ledger.jsonl), [execution log](artifacts/gpu/execution.txt),
[cleanup](artifacts/gpu/cleanup.json), and complete inputs/outputs/metadata under
`artifacts/gpu/generations/`. `runtime_running.json` is a retained intermediate
checkpoint, not the final process state.

Accepted agent outputs: [dev_1](artifacts/gpu/dev_1/accepted/dashboard.html),
[dev_2](artifacts/gpu/dev_2/accepted/dashboard.html). The third output is
[deterministic fallback](artifacts/gpu/dev_3/deterministic_fallback/dashboard.html),
not a successful agent result. Original invalid outputs and errors remain saved.

## Reproduction

Run from the repository root, using Python 3.10 (local tested version) or 3.12
(GPU host). Raw data and weights are ignored. Preparation/analysis regenerate
development artifacts; use a separate checkout when preserving the reference run.

```bash
python3.10 -m venv .venv
.venv/bin/pip install -r requirements.lock
.venv/bin/pip install -e . --no-deps
.venv/bin/trajectory download
.venv/bin/trajectory prepare
.venv/bin/trajectory analyze
.venv/bin/python scripts/duplicate_sensitivity.py
.venv/bin/pytest -q
.venv/bin/python scripts/verify_artifacts.py
```

Replay is independent of raw data and model inference:

```bash
.venv/bin/trajectory replay artifacts/deterministic/dev_1 --output /tmp/apm-replay
.venv/bin/trajectory replay artifacts/gpu/dev_2/accepted --output /tmp/apm-agent-replay
```

Optional new GPU execution, only on an already authorized suitable GPU host with
the checkout/prepared development data present. Reuse a compatible installed
PyTorch build, keep the same model/backend, and use a **new** output directory.
The explicit timestamp below starts a separately authorized reproduction window;
do not point it at the immutable original ledger. No SSH endpoints or credentials
are stored in this repository.

```bash
python3.12 -m venv --system-site-packages .venv
.venv/bin/pip install -e '.[gpu]'
HF_HUB_ENABLE_HF_TRANSFER=0 .venv/bin/python scripts/download_model.py
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 .venv/bin/python scripts/gpu_feasibility.py \
  --model-path models/qwen --output runs/gpu-independent \
  --authorized-start-utc "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

The model-download manifest is regenerated by this command. Exact model text may
vary across hardware/software kernels even with greedy decoding. Replaying saved
results is the preferred review path and makes no generation attempts.

## Verification, failures and next decisions

**12 tests passed** in the final focused run, with no skips. Six saved dashboard
packages replayed without inference; bound claims, chart specifications and HTML
inspector links agreed. Logs: [test output](artifacts/checks/tests.txt),
[JUnit](artifacts/checks/tests.xml), [replay](artifacts/checks/replay.txt),
[preparation](artifacts/checks/preparation.txt), and
[visual inspection](docs/INSPECTION.md). Tests include future-value mutation,
row-order invariance, missingness states, duplicate dimension keys, disjoint person
splits, focal exclusion, forged units/counts/cutoffs, unresolved evidence, omitted
context, bound means, replay and GPU device evidence. These are implementation
checks, not the scientific evaluation.

Known failures are the AAA fit and the third agent case. The initial model download
needed the host's optional fast-transfer flag disabled; download then succeeded
without an inference attempt. Visual defects found during development were fixed
and documented. Browser automation, mobile validation, expert review, interval
coverage calibration and a methods-level CoCo literature comparison remain undone.

Before Stage 2, independently review: the repeated-row interpretation; eligibility
and banking assumptions; prior-attempt reference validity; changing peer composition;
the intended estimand of earlier-stage comparisons; bootstrap calibration; the
strong prompt/evidence obligations; and whether the literature leaves a defensible
contribution. The failed case should inform repair feedback and omission checks,
not be erased by more attempts on the same example.

Proposed Stage 2: resolve these scientific assumptions, freeze an independently
reviewed question/rubric set and reference registry, strengthen the deterministic
enumeration baseline, and run a small predeclared development pilot with matched
analytical access. Keep reserved people untouched until the design is frozen.
No Stage 2 implementation or evaluation has begun.
