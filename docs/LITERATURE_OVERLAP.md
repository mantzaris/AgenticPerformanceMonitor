# Focused overlap assessment — checked 2026-09-18

This revisits the closest work in the supplied plan, not a new survey. Novelty
remains provisional and requires independent review.

| Primary source | Established overlap | Narrow opening being investigated |
| --- | --- | --- |
| [LIDA, Dibia, ACL 2023](https://aclanthology.org/2023.acl-demo.11/) | Staged goal discovery and visualization generation/refinement. | Generated dashboards and staged compilation are not new claims here. |
| [InsightPilot, Ma et al., 2023](https://arxiv.org/abs/2304.00477) | Iterative LLM exploration through structured queries to an analytical engine. | Tool use is established; reference-sensitive individual questions and enforceable evidence obligations are the proposed focus. |
| [CoCo, Malik et al., CHI 2015](https://doi.org/10.1145/2678025.2701407); [author lab description](https://hcil.umd.edu/?p=403) | The lab's indexed primary description confirms statistical and visual comparison of temporal sequences. Publisher/full-page retrieval failed; full methods were not independently verified. | Do not claim cohort comparison itself as novel. A methods-level overlap check remains open. |
| [Steegen et al., 2016](https://journals.sagepub.com/doi/10.1177/1745691616658637) | Multiverse analysis makes sensitivity to defensible data-processing choices explicit. | Reference sensitivity is an application of an established principle, not a new statistical estimator. |

The proposed addition is an independently testable policy for choosing references
and preserving personal-baseline, cohort, observation and uncertainty evidence in
the resulting dashboard. Stage 1 establishes only that this interface can run.
It cannot establish that an agent is preferable to enumerating a small registry.
Later evaluation needs strong deterministic enumeration, independent questions
and omission checks, and matched analytical access and budgets.

Implementation sources: [statsmodels mixed models](https://www.statsmodels.org/stable/mixed_linear.html),
[Vega-Lite grammar](https://vega.github.io/vega-lite/docs/),
[Qwen official model card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
(Apache-2.0; Qwen2 supported in Transformers >=4.37). The installed versions and
model revision are pinned separately; current documentation is not a runtime lock.
