# Manuscript claim and asset provenance

Internal review map. These repository links are deliberately excluded from the
anonymous manuscript. All paths below are relative to the repository root unless
linked otherwise. This drafting stage reads saved evidence; it neither rescores
episodes nor runs analyses on source observations.

| Manuscript location / claim | Primary repository evidence and implementation | Qualification |
| --- | --- | --- |
| Abstract, §6, Table 1, Figure 3: 24/21/15/15 visible; 24/18/14/11 selected | `artifacts/stage6/reports/per_case.json`, `comparison.json`; `scripts/generate.py` in this draft derives tables/macros and checks aggregates. | Frozen automated endpoint; all 96 slots retained; B17–20 disputed. |
| Table 2: paired C−A, C−B, B−A | `artifacts/stage6/reports/comparison.json:paired_comparisons`, `paired_cases.json`. | Same 24 paired people; no significance, pooled stages or best-case mixture. |
| Table 3, §6.4: costs, 168 comparison / 185 overall generations, 1719.02 process seconds | `comparison.json`, `resource_detail.json`, `model_ledger.jsonl`, `execution.jsonl`, `gpu/qwen14b_comparison_02/runtime.json`, `gpu/qwen14b_construction_01/runtime.json`. | Historical measurements; shared loading separate; not billing time. No new inference. |
| §3: source/license and audited counts/joins | `artifacts/data/AUDIT.md`, `manifest.json`, `preparation.json`; `src/trajectory_dashboards/audit.py`, `prepare.py`. | Global structural audit differs from analytical use of reserved observations. Counts refer to people, registrations and source rows separately. |
| §3.1: two offerings / 1,523 development people | `artifacts/data/preparation.json:candidates,selected_courses,distinct_development_people`; preparation selection code. | Lexical structural selection, not representativeness. |
| §3: 8,583 reserved people; no reserved evaluation | `artifacts/stage6/checks/final_verification.json`, Stage 6 review, source manifest's development-only description. | This draft reads saved metadata/checks, not reserved observations. |
| §3.2: eligibility, zero/missing/withdrawal/grade/banked rules | `prepare.py:eligibility,build_weekly`, Stage 2 analysis protocol and Stage 6 registry; original feature/status records in accepted evidence. | Administrative opportunity, unknown logging, unknown grade release; no effort/ability inference. |
| §3.2: duplicate handling | Dataset audit; `artifacts/stage2/statistics/sensitivity.json` and its preserved alternative source manifest. | Primary retains all rows. The earlier bounded sensitivity is not a new Stage 6 robustness claim. |
| §3.3 equations, weighting, thresholds and intervals | `src/trajectory_dashboards/stage2/backend.py:Engine.analyze`, `analysis.py:interval`, `stage2/core.py`, `configs/stage6.json`; `docs/stage2/ANALYSIS_PROTOCOL.md`. | Equal people, equal observed weeks within person; partial-week rates first; 20 peers/2 focal weeks; 500 person resamples. No contrast/change/prediction interval. |
| §4 / Figure 1: requests, evidence, compiler, validator | `stage4/agents.py`, `stage6/adapter.py`, `stage2/backend.py`, `stage2/integrity.py`, `stage4/semantic.py`, `stage4/display.py`. | Generic policy; no generated analysis/frontend code. Source-bound checks are not coverage scoring. |
| §4 identities and aliases / §5 A/B/C | `src/trajectory_dashboards/stage6/binding.py:identity,derived,catalogue,personal_signature,resolve,compile_selection`; `docs/stage6/INTERFACES.md`; frozen schemas/prompts in `artifacts/stage6/protocol/` and configuration. | Personal identity omits peer meaning. B and C share catalogues. B–A is an interface package, not pure metadata ablation. |
| §4.3, Figures 2/4/5, §7 assessment example | `src/trajectory_dashboards/predraft_v1/`, inherited `presentation_v1/`; `artifacts/predraft_v1/source_manifest.json`, `capture_manifest.json`, `figure_manifest.json`; saved A01/A05/A09/A17/A15 + baseline15. | Post-experiment renderings; full originals govern scoring. Observation/grade context in A09 came from original compiler; repaired status retained. |
| §5 case selection, profiles, families | `artifacts/stage6/tasks/manifest.json`, `scripts/stage6/prepare.py`, `configs/stage6.json`, `docs/stage6/PROTOCOL.md`. | Four per family, 24 distinct people, all five profiles including short day-27 windows, 57+24 reference exclusions. |
| §5 freeze, counterbalancing, independent facts | `artifacts/stage6/protocol/freeze.json`, `execution_order.json`, `evaluator_only/rubrics.json`; `checks/selection_reproduction.json`, `checks/final_verification.json`. | Hidden requirements excluded from inference; separate row-loop path is not human review. No evaluator executed while drafting. |
| §5 model and actual GPU path | `artifacts/stage5/models/qwen14b/manifest.json`; saved Stage 6 runtime and per-generation metadata. | Pinned revision, BF16, all parameters GPU; device evidence is historical. |
| §5.4 endpoint definitions | `stage3/evaluation.py:assess_item`, `stage4/evaluation.py` selection projection, `stage6/reporting.py`, per-case attribution fields. | Optional content and universal integrity are separate; selected never means model-calculated. |
| §6.2 retrieved upper bounds / nontruncation | Frozen per-case `oracle_retrieved_upper_bound`, resource detail EOS/token fields and actual sequences. | Oracle-assisted offline diagnostic, not success or deployed policy. |
| §6.2 / Figure 5 A15 omission | `artifacts/stage6/comparison/compact_a/s6_15/{sequence.json,tool_results.json,accepted/bound.json,accepted/spec.json}` and corresponding baseline. | Two correctly bound earlier peer claims; separate personal insufficiency; omitted recent peer answer remains omitted. |
| §6.2 C12/C18–20/A09/A12/A22/B23 | Original sequences, final/repair errors, `inspection/trace_review.json`. | Observable failures; manual annotations supplement imperfect automatic taxonomy without revising scores. |
| §6.3 B17–20 and C21/C23 | Original accepted bound claims, question and specification files; `docs/stage6/SCORING_CAVEAT.md`; Stage 3 focal/person predicates. | B recent means are visible; frozen focal rule does not credit them. Personal mean equivalence is a separate adjudication question. |
| §§6–7 zero detected accepted unsupported quantities | Frozen 91 accepted integrity outcomes, `checks/final_verification.json`; source validator and exact replay records. | Limited to implemented source/support checks; not universal correctness or complete answers. |
| §§6–9 human review pending | `artifacts/predraft_v1/human_review/packet.json` and blank reviewer/adjudication forms; original Stage 6 packet unchanged. | No invented ratings, identities, agreement, or author validation. |
| §§7–8 recommendation | Frozen gate/outcomes and `docs/stage6/FINAL_VALIDATION_DRAFT.md`. | Gate is internal. Enumeration's success applies to predefined registry. No agent candidate or final study is approved here. |

## Publication asset mapping

All main figures use the official **158.0134 mm** text width. Captions, section prose,
and source-generated result macros/tables are in `main.tex`; original captions and
captures remain unchanged.

| Paper asset | Preserved source | Publication operation / minimum critical text |
| --- | --- | --- |
| Figure 1 `figures/architecture.pdf` | `artifacts/predraft_v1/figures/figure3.pdf`; original vector generator | Same genuine vector diagram, anonymous metadata; 8 pt minimum. |
| Figure 2 `figures/adaptation.pdf` | `figure1.pdf`: A01 personal + A09 observation limits | PDF page stream unchanged; metadata anonymized; raster panels + vector lettering; 8.50 pt minimum. |
| Figure 3 `figures/results.pdf` | `figure4.pdf`, same 96 frozen per-case records | Original plotting path reused; heading becomes “Frozen development comparison”; genuine vector; 8.5 pt minimum. |
| Figure 4 `figures/reference_switch.pdf` | `figure2.pdf`, A05 actual course/early-stage selector states | Page stream unchanged; anonymous metadata; raster panels + vector labels; 8.80 pt minimum. |
| Figure 5 `figures/failure.pdf` | `figureS1.pdf`, A15 / enumeration15 | Faithful excerpts, external editorial labels unchanged; anonymous metadata; 8.54 pt minimum. |
| Unused candidate `figures/assessment.pdf` | `figureS2.pdf`, A17 | Retained at 75.0067 mm column width for author review; main text describes it without relying on a supplement; 8.50 pt minimum. |

`generated/provenance.json` records source and output hashes. Original viewport
548×1100 CSS px, device scale 3, Chromium 153.0.8010.36, DejaVu Sans, selectors,
exact excerpt bounds, interaction states and artifact hashes are preserved in the
pre-draft capture manifest. No numerical screenshot pixels were edited. The new
PDF proof is rendered at 96 and 150 dpi; browser loading uses 210 mm CSS image width.
Raster panels inside PDFs are not described as vector graphics. Native chart SVGs
remain available under `artifacts/predraft_v1/gallery/*/charts/`.
