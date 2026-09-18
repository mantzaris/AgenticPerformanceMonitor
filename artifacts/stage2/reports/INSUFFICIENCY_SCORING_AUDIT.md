# Frozen insufficiency scoring issue

**Do not interpret the raw comparison's 0/4 reference-sensitive “appropriate
insufficiency” count as failure to display insufficient evidence.** The frozen
scorer requires a `comparison` or `personal_change` claim template in addition
to unsupported evidence. It does not credit the specification's explicit
`insufficient_evidence` conclusion, which is an admissible, validated answer
channel and is prominently displayed by the renderer.

Reference-sensitive tasks p05, p06, p07 and p08 all selected that conclusion,
supported by their analytical records. Their selected claims use only
`measurement_limits`, so the frozen item returns false. This is a concrete
rubric/implementation defect, not evidence that those outputs asserted a
supported contrast. The source data, outputs and original scores are unchanged.

| Method | Frozen claim-template item | Displayed, evidence-supported insufficiency statement |
|---|---:|---:|
| Baseline | 4/4 | 4/4 |
| Generic agent | 3/4 | 3/4 |
| Reference-sensitive agent | 0/4 | 4/4 |

The right column is an explicitly **post-hoc display audit**, not a tuned or
replacement primary score. Its [case-level records](insufficiency_display_audit.json)
include the saved conclusion and claim texts. The generic p08 episode failed
validation and has no accepted display. The reference-sensitive p07/p08 outputs
still omit a dedicated personal-history claim, and p05/p06 omit requested
assessment analyses; the other frozen coverage findings remain distinct.

No agent was rerun, no repair was added, and no frozen scoring code, prompt or
configuration changed. External review should revise and validate this scoring
rule before a subsequent experiment. The raw JSON/CSV/Markdown comparison
reports retain the original metric so this issue cannot be silently erased.
