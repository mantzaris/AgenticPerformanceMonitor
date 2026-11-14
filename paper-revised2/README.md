# ICAART 2027 — second revision

- [Paper](main.pdf) — eight pages, including references.
- [Diff against the submitted version](changes.pdf).
- [Diff against the first revision](changes-from-first.pdf).
- [Short revision notes](REVISION_NOTES.txt).
- [LaTeX source](main.tex) · [exact source diff](changes.diff) · [checks](checks.json).

The title, abstract, introduction, conclusion, original outcome table,
bibliography, and official style files are preserved. Edits focus on the reviewer
requests and the short-paper length limit. The first revision remains untouched.
The author block includes Alexander V. Mantzaris and James H. Korris, with the
affiliations and email addresses supplied by the authors.

The statistical and duplicate-row results are reused unchanged from
[the first revision's analysis directory](../paper-revised/analysis/). Their
source hashes are recorded in `checks.json`. There are no new experiments or
human ratings. The notes identify the reviewer requests that still need new data.

Build the paper and both comparisons from the repository root:

```sh
python3 paper-revised2/build.py
```

This needs pdfLaTeX, BibTeX, latexdiff, and Poppler. It checks preservation of the
original sections, primary scores, style files, and all 86 frozen experiment
files, as well as page count and LaTeX diagnostics. It does not run experiments.
