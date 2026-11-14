# ICAART 2027 short-paper revision

- [Revised paper (8 pages)](main.pdf)
- [Readable red/blue diff against the submitted paper](changes.pdf)
- [Reviewer-request mapping and outstanding evidence](REVISION_NOTES.txt)
- [LaTeX source](main.tex) · [exact source diff](changes.diff) · [checks](checks.json)

The title, abstract, introduction, frozen outcome table, bibliography, and official
style files are preserved. Reductions elsewhere meet the eight-page short-paper
allowance. The new analyses are post hoc. Independent human ratings, new test-case
runs, and user-study results have not been produced; the notes distinguish these
outstanding requests from completed changes. Author details remain as in the
anonymous submission.

Build the paper and diff from the repository root (pdfLaTeX, BibTeX, latexdiff,
and Poppler are required):

```sh
python3 paper-revised/build.py
```

Reproduce the paired comparisons with Python 3.8+ and no third-party packages:

```sh
python3 paper-revised/analysis/paired_statistics.py --output /tmp/paired-statistics.json
```

For the duplicate sensitivity, use Python 3.10+ with `pyarrow==20.0.0` (also in
the repository's pinned dependencies):

```sh
python3 paper-revised/analysis/duplicate_sensitivity.py --output /tmp/duplicate-sensitivity.json
```

These commands use saved development data. They do not rerun models, load reserved
observations, or overwrite the original paper or frozen experiment reports.
The build checks title/abstract/introduction preservation, frozen outcome values,
style files, all 86 frozen experiment hashes, page count, and LaTeX diagnostics.
