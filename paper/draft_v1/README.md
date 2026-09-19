# Manuscript Draft V1

[Read the complete anonymous PDF](main.pdf) · [top-level review](../../MANUSCRIPT_DRAFT_V1_REVIEW.md)
· [decisions before submission](DECISIONS_BEFORE_SUBMISSION.md)
· [all proof pages](checks/pages.html)

This is a complete ICAART 2027 author-review manuscript, not a submission or a
claim that adjudication/held-out validation has finished. It reports the frozen
development study. Five figures and three generated tables are in the manuscript;
the assessment figure remains an additional review candidate.

From the repository root, using the existing environment:

```sh
python3 paper/draft_v1/scripts/build.py
.venv/bin/python paper/draft_v1/scripts/browser_proof.py --chromium /snap/bin/chromium
python3 paper/draft_v1/scripts/verify.py
```

The first command regenerates tables from saved reports, publication figures from
the preserved plotting path/captures, and runs pdfLaTeX/BibTeX/pdfLaTeX twice. The
second renders every page, opens it in CPU-only Chromium, checks the saved reference
states, and counts raster-panel text. The third performs manuscript-specific
consistency/preservation checks. None calls an evaluator, analytical dispatcher,
model, GPU, external service, or reserved data source. Chromium may need the local
sandbox permission used by other repository browser commands.

To compile only the included LaTeX, figures and tables:

```sh
cd paper/draft_v1
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The verified setup uses TeX Live 2019 / pdfTeX 1.40.20 / BibTeX 0.99d, the unmodified
official `article.cls`, `SCITEPRESS.sty`, `apalike.sty`, `apalike.bst`, and standard
packages (including `algorithm2e`, `footmisc`, `pslatex`, `url`). The CPU figure
builder uses system Python 3.8.10, Matplotlib 3.1.2, Pillow 9.4.0, and PyPDF2 1.26.0.
Browser inspection uses repository Python 3.10.18, Playwright 1.55.0, Chromium
153.0.8010.36, `--disable-gpu`, and local fonts. Poppler supplies `pdftotext`,
`pdftoppm`, `pdfinfo`, and `pdffonts`. No new dependency installation was needed.
`build.py` fixes `SOURCE_DATE_EPOCH` and `FORCE_SOURCE_DATE` for repeatable PDF
metadata. Exact-byte reproducibility is checked in this recorded environment;
different TeX/font/library versions may change bytes or pagination.

The original official archive and its source manifest remain in
[`artifacts/predraft_v1/template`](../../artifacts/predraft_v1/template).
Current-source verification is in [venue notes](review/VENUE_AND_TEMPLATE.md).

Sources and accountability:

- [Organized prose](sections/), [main.tex](main.tex), [bibliography](references.bib).
- [Claim/figure/table provenance](review/CLAIM_TO_EVIDENCE.md),
  [reference checks](review/REFERENCES_VERIFIED.md), [generated manifests](generated/).
- [Verification](checks/verification.json), [count method](checks/character_count.json),
  [browser record](checks/browser.json), [inspection notes](review/INSPECTION.md).
- [Original full review packet](../../artifacts/predraft_v1/human_review/index.html)
  remains pending and unchanged. Internal links in these notes are intentionally
  absent from the anonymous PDF.

For a local review, open `main.pdf` or `checks/pages.html` directly; no server is
required. The unchanged [pre-draft gallery](../../artifacts/predraft_v1/gallery/index.html)
links the complete UI examples, saved-reference interaction and original provenance.
