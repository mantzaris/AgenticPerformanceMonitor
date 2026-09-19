# Reproduce and preview — CPU/browser only

Run from the repository root on `main`. The commands read saved development outputs;
they do not run agents, the experimental scorer, `Engine.analyze`, or final validation.
Historical source-bound replay uses only the existing Stage 6 development source bundle.
Do not invoke the old GPU runners for this package.

## Local preview

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/artifacts/predraft_v1/gallery/index.html`.
The server serves the repository so relative links to original dashboards work.
Stop it with Ctrl-C. All pages also work directly via `file://`; no hosted backend,
remote fonts, CDN or external service is used. No server is left running by the build.

## Regenerate the final package

The official archive and its unmodified extracted files are committed under
`artifacts/predraft_v1/template`. No network is needed to reproduce. To verify them:

```bash
python3 scripts/predraft_v1/template.py
python3 scripts/predraft_v1/regenerate.py --inspect
```

`--inspect` opens the six live views, all six figure proofs, all six LaTeX page
renders, all 96 review pages, and four full original scientific-review examples.
Chromium is closed at completion. Use `--chromium /path/to/chromium` if needed.
The generator only accepts output directories beginning with `predraft_v1`.

The exact component commands are:

```bash
.venv/bin/python scripts/predraft_v1/build.py
.venv/bin/python scripts/predraft_v1/review_packet.py
python3 scripts/predraft_v1/vector_figures.py
.venv/bin/python scripts/predraft_v1/capture.py
python3 scripts/predraft_v1/compose.py
python3 scripts/predraft_v1/proof.py
python3 scripts/predraft_v1/verify.py
.venv/bin/python scripts/predraft_v1/browser_review.py
```

Capture uses real local Chromium, `--disable-gpu`, viewport 548×1100 CSS px and
DSF 3; exported surfaces are 500 CSS px, with smaller documented selector crops.
Fonts and native SVGs are awaited; animations are disabled. The reference control
is actually operated for all three saved comparisons. PNG composites are 300 dpi.
The proof uses pdfLaTeX, official `article.cls`, `SCITEPRESS.sty`, `apalike.sty` and
`apalike.bst`, unchanged. The preamble loads `algorithm2e` because SCITEPRESS renews
its caption macro. Captions use the official `small` size (9 pt). No geometry change.
`SOURCE_DATE_EPOCH`, omitted PDF dates and invariant composition permit exact export
reproduction; these metadata settings do not alter layout or scientific content.

## Fresh-output reproduction check

Snap Chromium cannot open host `/tmp` files. Use a separate repository directory:

```bash
python3 scripts/predraft_v1/regenerate.py --output artifacts/predraft_v1_reproduction
python3 scripts/predraft_v1/check_reproduction.py
```

The fresh directory is temporary and should not be committed. The comparison covers
captures, composites, genuine vectors, proof PDF/pages, derived results and blank
forms. Output-root paths in HTML/manifests legitimately differ. Do not overwrite a
rated human-review form: the generator produces blank forms; preserve ratings elsewhere.

## Focused checks

```bash
.venv/bin/python -m pytest -q tests/predraft_v1 tests/presentation_v1
python3 scripts/predraft_v1/verify.py
.venv/bin/python scripts/presentation_v1/verify.py --replay \
  --output artifacts/predraft_v1/checks/historical_replays.json
```

The last command reuses the original numerical validator and replays the six saved
examples, including the incomplete agent and baseline, into temporary directories.
It does not change a primary score. The older presentation and its replay commands
remain documented in `docs/presentation_v1/REPRODUCTION.md`.

## Environment used

- Existing project `.venv`: Python 3.10.18, Playwright 1.55.0, pytest 8.4.2 and the
  project's installed dependencies. No new Python packages were installed.
- System Python 3.8.10: Pillow 9.4.0, ReportLab 3.5.34, Matplotlib 3.1.2.
- Chromium 153.0.8010.36 at `/snap/bin/chromium`, headless, GPU disabled.
- pdfTeX 1.40.20 (TeX Live 2019/Debian), `pdftoppm`, `pdfinfo`, `pdffonts`.
- Local DejaVu Sans regular/bold; Times-compatible Nimbus Roman for template text.
  Every live PDF font in the final compiled proof is embedded.

On another machine provide these tools or equivalent compatible versions; exact
pixel/byte equality is only asserted for the recorded environment. No external
font download, statistical refitting, model initialization or GPU host connection
is required.

## Official template acquisition (already preserved)

The current [ICAART Templates page](https://icaart.scitevents.org/Templates.aspx)
links the [SCITEPRESS archive](https://www.scitepress.org/documents/SCITEPRESS_Conference_Latex.zip).
Retrieved over HTTPS on 2026-09-19. The browser fetch of the ZIP was denied, but
`curl -fL` downloaded the official archive successfully. Its SHA256 is
`ec6cfaa11962e08d5c6a402124f21c3bca3591397521406ab6d1889398a3807a`.
Do not replace this copy silently if the live template changes; version the new
retrieval and rerun the dimensional proof.
