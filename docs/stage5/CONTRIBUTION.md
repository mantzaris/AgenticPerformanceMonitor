# Provisional contribution assessment before comparison

The experiment addresses a checkpoint-capability explanation of incomplete answers
under a fixed evidence/visualization contract. It does not establish a general
limitation of agents, a causal effect of parameter count, or unrestricted natural
language understanding. The prior failures are evidence about particular bounded
implementations; the enumeration baseline uses a small predefined registry.

Generated visualizations and staged generation are established. [LIDA (Dibia,
ACL 2023)](https://aclanthology.org/2023.acl-demo.11/) explicitly decomposes data
summarization, goal exploration, visualization generation/refinement and graphical
presentation. [InsightPilot (Ma et al., 2023)](https://arxiv.org/abs/2304.00477)
combines an LLM with analysis actions for iterative data exploration. These primary
sources rule out novelty claims based simply on an LLM choosing analyses or a
multi-stage chart pipeline. This is a focused overlap check, not an exhaustive
novelty review.

The [Qwen2.5 technical report](https://arxiv.org/abs/2412.15115) describes a family
of pretrained/post-trained checkpoints. Its reported capabilities are motivation,
not measurements of this dashboard task. The official [14B model card](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct/tree/cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8)
and Apache 2.0 license are preserved with the acquisition manifest. Use the fixed
checkpoints' actual paired results, not the model card's general capability claims,
to make the Stage 5 decision.

A defensible possible direction is an empirical reliability study of which
responsibilities belong to a model and which to deterministic analytical/rendering
components. Its useful measurements distinguish retrieved evidence, explicitly
selected answers, mechanically supplied context, numerical integrity and visible
question completeness. These engineering distinctions may be useful even if the
model adds no benefit over enumeration. They are not yet a demonstrated novel
method or publication-ready result; independent scientific/usability review and a
broader related-work assessment remain necessary.

If both fixed checkpoints fail the gate without substantial improvement, further
prompt-policy refinement on the same small registry is not justified by this
stage. Retain enumeration and consider whether a materially different question
requiring demonstrated benefit from flexible investigation is needed. Do not
automatically construct or execute that new study. If the larger checkpoint passes,
external review should first decide whether broader validation of that fixed
condition addresses a useful research question beyond reproducing the registry.
The final operational and research recommendation belongs in STAGE5_REVIEW.md.
