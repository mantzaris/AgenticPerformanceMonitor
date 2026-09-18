# Stage 3 evaluation and confirmation protocol v1

This is a provisional development pilot awaiting external human scientific review.
The separate row-loop numerical checker and this automated semantic audit are not
independent human review. Historical Stage 2 primary scores remain immutable.

## Answer semantics

Score five separate dimensions: source-bound numerical integrity; requested
answers; necessary interpretation context; optional additions; and content
provenance. The primary descriptive endpoint is an accepted dashboard with every
requested answer visible. Also report the stricter endpoint requiring every answer
to be method-selected: a standard compiler caveat can answer grade unavailability,
but does not demonstrate agent investigation. Neither endpoint rewards more panels.

Each evaluator-only item includes a question-wording or shared-interpretation
justification. Personal history is optional for peer-only reference questions.
Historical "activity" permits click rate, active days or distinct resources, used
consistently across the comparison; this is a disclosed repair of underspecification,
not a claim that an independent human established the intended meaning. Stage 3
questions explicitly name features. Both phrasings have identical answer contracts.

Accepted answer forms include scoped quantitative comparison claims and supported
focal/reference mean charts. A validated cross-reference conclusion or a complete
set of scoped comparisons can answer a direction question. Mere evidence selection,
an irrelevant template, or an inspector-only result is not a visible requested
answer. A trajectory is not a displayed multi-week mean or personal mean change.
Personal change uses its scoped claim, including supported insufficiency. A single
analysis supplies both personal windows; a baseline-window tool request is not
required merely to retrieve those summaries.

A supported `insufficient_evidence` conclusion receives explicit global-finding
credit. Its existential wording resolves a particular requested comparison only
when the unsupported referent is unique among selected semantic comparisons.
Otherwise scoped comparison/personal claims are needed; the general statement
does not identify which comparison is unsupported. One unavailable comparison
does not excuse another answerable request. Counts and descriptive means remain
available when contrasts are withheld. Grade/learning unavailability is a
measurement limit, not insufficient sample size or an uninvestigated analysis.

Mandatory context is checked separately: exact units/windows/reference counts,
observation states, interval meaning and measurement caveats. Integrity validation
remains the frozen source-bound Stage 2 validator; it does not enforce task
coverage, investigation sequence, or the proposed policy. Controlled numeric
wording and standard caveats are compiler-supplied; the method selects records,
claims, panels and conclusion. Stage 3 adds feature prefixes and scoped window/count
wording to unsupported personal claims for **all** methods; it inserts no missing
analysis or substantive answer. The optional request_map Action field is equally
available to all policies, but only the new policy instructs its systematic use.
No gold requirements or evaluator feedback enter model messages.

## Historical reanalysis

Apply the new evaluator to all 36 saved Stage 2 method/task results without model
calls. Revalidate accepted evidence with the original Engine/config/source and
verify claim text bindings. Preserve original score records and provide per-item
new judgments, old/new endpoints, and a reason for every changed dimension:
rubric overrequirement, feature underspecification, supported-but-unscoped global
insufficiency, retrieved-but-not-displayed information, or missing analysis.
Scores from the two versions have different denominators and are not directly
interchangeable estimates of a single validated metric.

## Pilot design and methods

Twelve new focal people, two per existing family, each with two equivalent
phrasings: 24 question instances, **12 dependent case units**. Exclude all prior
construction/pilot/demo people by person across registrations. Select from the
same development bundle by course, cutoff, eligibility counts and prior-attempt
category using a frozen SHA256 seed/ranking. Do not inspect activity magnitudes,
outcomes or method wins for selection. The fixed reference pool excludes all old
and new focal people. Reserved people remain closed. Real observations are
unmodified; synthetic scorer fixtures never enter pilot results.

Conditions: the existing strong deterministic enumeration baseline; generic agent;
previous reference-sensitive policy; coverage-aware reference-sensitive policy.
The first three use their existing selection/policy logic under the shared Stage 3
interface, not an exact Stage 2 replication. The baseline still enumerates all
three references, retaining relevant results and assessment measures by explicit
rules. It is not weakened to favor agents. Both old agent policy texts are byte-
identical to Stage 2. The new policy derives a concise request map from the public
question, observes a first tool result, chooses subsequent analyses, tracks
unanswered/retrieved/answered/insufficient/unavailable requests, avoids duplicates,
and checks visible answer selection before stopping. Maps are observable task
states, not private reasoning, and are not automatically filled by gold rules.

All timed analytical work runs on the same GPU host CPU. One pinned local model,
backend, BF16 CUDA device, greedy decoding, 1,500 output tokens, 16,000 input tokens,
six tools/four generations/one final repair are shared by the three agents. No
fallback counts as success. Six known Stage 2 construction episodes may inform
pre-freeze changes. Setup/profiling generates a single-token model response and
counts toward the 32 construction/setup budget. Pilot generations have a separate
288 cap. No failed pilot episode is rerun. At least one shared model load is reused
for the full pilot; shared loading and profiler warm-up are reported separately.
Agent order uses all six permutations, balanced across cases and paired phrasings;
phrase order alternates. This measures paraphrase sensitivity, not stochastic
repeatability. No seed-based repetition or significance claim is planned.

Freeze questions, requirements/facts, prompts, public rules, configs, execution
order, source hashes, tests and analytical/inference/evaluation code before pilot
inference. Verify hashes on the host. After freeze, do not tune against results;
disclose any protocol deviation and preserve affected attempts.

## Reporting and checks

Keep all 24 instances in each condition's denominator and aggregate paired results
within each of 12 cases. Report first/post-repair validity, integrity, requested-
answer and method-selected completeness, missing versus retrieved-but-omitted
answers, scoped and global insufficiency, measurement limits, required context,
optional panels, repeated requests/panels, tokens, generations, latency, repairs,
failures and compiler additions. Report a/b agreement and completeness changes by
case; do not count them as independent people. If enumeration is equally complete
and cheaper, say so. No favorable result is required.

Inspect the first selected case in each of personal change, reference sensitivity,
assessment availability and insufficient support. Use phrasing a; inspect the
baseline and proposed method when accepted, otherwise preserve the failure and
inspect its baseline. Choice is fixed before results. Exercise the real follow-up
form once on the first insufficient-support baseline. Save parent/child hashes,
new evidence/spec/export and browser record. Replay accepted results without
inference, verify historical/frozen hashes and split exclusions, and stop model
and local server processes. Pod remains running.
