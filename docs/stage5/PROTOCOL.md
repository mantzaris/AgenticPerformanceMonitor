# Frozen checkpoint comparison protocol v1

## Hypothesis and invariant system

The poor completeness of the pinned 7B checkpoint may change with the official
14B instruction-tuned checkpoint from the same family. Primary descriptive
contrast: 14B compact minus 7B compact complete valid answers, paired on twelve
cases. Secondary: 14B versus 7B full; compact versus full within each checkpoint;
all four versus enumeration. Do not select a different winning condition for each
case and present that oracle mixture as an operational method.

Reuse the exact Stage 4 generic episode code, prompts, public interpretation rules,
full/compact schemas, semantic compiler, Stage 2 analytical backend and source-bound
validator, Stage 3 answer predicates and Stage 4 attribution wrapper. No policy,
statistical, support, scoring, tool-routing or deduplication changes. The historical
files are read-only and included in the freeze. New code binds only Stage 5 data,
configuration, logging/output destinations and checkpoint loading. The wrapper
retains the original episode code object in an isolated globals dictionary;
only event logging and the renderer's stage label change. Checkpoint identity is
metadata, not model input. Both receive identical public messages before their
checkpoint-specific tokenizer/chat template. Each checkpoint's pinned files and
tokenizer/template/special-token differences are recorded.

Both use Transformers 4.55.2 / Torch 2.8.0+cu128, SDPA, all parameters BF16 on cuda:0,
no offload/quantization, greedy decoding, 1,500 new tokens and at most 16,000 input
tokens. Standard EOS stopping is unchanged in comparison episodes. Exactly the
same six-tool/four-generation/one-final-repair loop is used. No evaluator-only
requirements/facts or new comparison cases enter setup. A content-valid dashboard
may be incomplete; integrity and requested-answer coverage remain separate.

The descriptive estimands, reference rules, primary repeated-row handling,
500-replicate person bootstrap, time cutoffs and support thresholds are unchanged.
Peer intervals estimate reference means, not personal prediction or contrast
uncertainty. Unknown logging completeness, unverified assessment obligations,
withheld grade availability, changing peer composition and unequal history remain
limitations. See the preserved [Stage 4 protocol](../stage4/PROTOCOL.md).

## Cases, freeze and execution

Select twelve unused development people from the established twelve structural
family/course/profile/eligibility slots, excluding all 45 earlier focal people.
Use seed `stage5-structural-v1-20260918`, choosing minimum SHA256(seed, new case ID,
person ID) among admissible unused people. Do not inspect activity magnitudes or
condition results to select people. Preserve actual observations. Exclude these
twelve from the same fixed development peer pool. Reuse the prior explicit-measure
question wording and answer requirements; one wording per person. Separate row-loop
facts are not independent human gold. Synthetic capacity/scorer checks are not
pilot cases. These are known task families and development data, not held-out data.

Freeze selection, tasks, hidden requirements/facts, exclusion/source hashes,
historical interfaces/prompts/compiler/analysis/scoring files, checkpoint revisions,
runtime config, execution order, report code and decision rules before comparison.
No tuning or rerunning failed cases after freeze. Historical artifacts/ledgers
remain unchanged; Stage 5 ledgers are append-only across restarts. Record exact
starting, setup and comparison commits. No baseline substitution for failed agents.

Enumeration runs first on the GPU host CPU. Then one model block for 7B, then
one for 14B. Within each block, full first in odd cases and compact first in even
cases: six first positions each, one of each within every family. One model load
per comparison block; separate setup loads verify capacity before freeze. Shared
loading/profiling overhead is unallocated to an interface. Block order, cache and
temporal effects make timing descriptive, not a hardware-controlled benchmark.

Setup uses a one-token profile and a capacity-only tensor computation from saved
Stage 4 construction messages. The latter repeats/trims those known tokens to
16,000 positions and executes 1,500 greedy argmax forward steps with the same
Transformers model, SDPA, BF16 and dynamic KV cache. EOS tokens are retained as
generated; computation continues past EOS only for this unscored capacity probe,
without suppressing tokens or adding grammar constraints. This exercises the
full 17,500-position allocation/compute boundary and counts as one setup generation.
It is not an agent answer or a change to comparison stopping/decoding. Save actual
input length, output steps, CUDA execution and peak memory. If the intended bound
fails, do not lower it or substitute another precision/model/backend; retain the
failure and mark the affected comparison as infrastructure blocked.

## Endpoints and mechanism reporting

All twelve cases remain in each denominator. An unattempted infrastructure-blocked
condition is distinct from attempted agent failure, not evidence of poor reasoning.
Report both validity at the first attempted final and after one repair; complete
visible and method-selected requested answers; missing analyses versus retrieved
but undisplayed answers; scoped insufficient support; compiler context separately.
Use the unchanged Stage 4 scorer; the same saved output must receive the same
score regardless of model label. Extra panels receive no completeness bonus.

Save raw requests/responses/results/errors and final bindings. Error categories
are nonexclusive: identifier, JSON/schema, support declaration, conclusion scope,
layout/claim contract, substantive conclusion and infrastructure. Correct the
known Stage 4 reporting string-match omission by specifying these categories
before inference, without changing the integrity or completeness evaluator.
Distinguish unsupported quantitative/semantic attempts rejected by validation from
accepted unsupported quantitative answers; malformed layout alone is not such an
attempt. No raw numeric values or generated code are permitted in either interface.

For each model pair and interface pair report both complete, right condition only,
left condition only and both incomplete. Also report calls, exact/equivalent
repetitions, generations, tokens, latency and peak allocated/observed VRAM, with
setup/loading costs separate. No statistical significance or repeatability claim;
twelve paired development cases are not generalization evidence. The checkpoints
differ in more than parameter count, so this is not a pure causal model-size effect.

## Decision rules and inspection

Retain the gate: at least 11/12 complete valid answers and zero accepted unsupported
quantitative answers for a fixed condition. This is an engineering target only.
If 14B compact reaches it, recommend external review of a broader validation plan
for that fixed condition. If only 14B full reaches it, report that secondary result
explicitly, rather than switching the primary endpoint. Describe remaining cost
and flexibility gaps relative to enumeration in either case.

For a missed gate, prespecify substantial descriptive improvement as at least
three additional complete answers (25 percentage points) for 14B compact over 7B
compact. This is a decision aid, not a significance threshold. If achieved, inspect
the recorded remaining mechanisms and recommend at most a specific separately
reviewed bounded intervention if justified. Do not execute it. If both checkpoints
remain unreliable without that improvement, recommend ending prompt-policy
refinement for this task class and retaining enumeration. A serious accepted
quantitative-integrity failure blocks operational use regardless of completeness.

Inspect the first selected case in each family (01,03,05,07,09,11) for all five
conditions, retaining empty slots for failures. In addition, inspect the
lexicographically first valid-incomplete and first rejected case per agent
condition when not already represented. This outcome-based supplemental rule is
declared in advance and selects failures rather than attractive examples. Verify
requested answers actually reach the display and compiler provenance is truthful.
Replay all accepted outputs without inference. Human scientific/usability review
remains outstanding.

Decision distinguishes operational readiness, established empirical findings,
possible contribution and evidence still needed. Enumeration covers a small,
predefined question/reference registry, not unrestricted natural language. Larger
checkpoint success alone establishes neither novelty nor an advantage over that
baseline. Stop after review, commit/push and process cleanup.
