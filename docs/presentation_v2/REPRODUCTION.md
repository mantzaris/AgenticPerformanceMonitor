# Reproduction and local preview

Run from the repository root in the existing environment. Nothing below requires
RunPod, model weights, a model call, a hosted backend or remote fonts.

```sh
# Optional local preview; Ctrl-C stops this server.
python3 -m http.server 8765 --bind 127.0.0.1 --directory .
# Open http://127.0.0.1:8765/artifacts/presentation_v2/gallery/index.html
```

Alternatively, open `artifacts/presentation_v2/gallery/index.html` directly as a
local file. The saved-reference query links, evidence inspector and expanders
work in Chromium in either mode.

```sh
# Rebuild views, actual browser captures, figures and official-template proof.
python3 scripts/presentation_v2/regenerate.py --inspect

# Focused checks, including the unchanged inherited mapping boundaries.
.venv/bin/python -m pytest -q tests/presentation_v2 tests/presentation_v1
.venv/bin/python scripts/presentation_v2/verify.py --replay
```

To repeat the independent-output export check (use a fresh replica directory):

```sh
python3 scripts/presentation_v2/regenerate.py --output artifacts/presentation_v2/reproduction_build --inspect
python3 scripts/presentation_v2/check_reproduction.py --replica artifacts/presentation_v2/reproduction_build
```

The delivered check compared every individual PNG, native SVG, composite PDF/PNG
and proof page. Output-dependent HTML/provenance links are intentionally not
compared byte for byte. The temporary replica used during delivery was removed
after the successful comparison; its result and per-file hashes are retained.

The regeneration command uses the repository Python for HTML/Playwright, system
Python for ReportLab/Pillow figure composition, and pdfLaTeX/Poppler for the proof.
It runs each dependency in sequence. `--output NEW_DIRECTORY` supports clean
regeneration; historical presentation/pre-draft/Stage 6/manuscript destinations are
rejected. Do not overwrite any earlier package. Source/capture manifests are
regenerated for the selected output root; the initial historical inventory remains
append-independent and is not rewritten by regeneration.

Individual commands:

```sh
.venv/bin/python scripts/presentation_v2/build.py
.venv/bin/python scripts/presentation_v2/capture.py --chromium /snap/bin/chromium
python3 scripts/presentation_v2/compose.py
python3 scripts/presentation_v2/proof.py
.venv/bin/python scripts/presentation_v2/browser_review.py --chromium /snap/bin/chromium
```

The optional `--replay` verification uses the original source-bound validator and
replays six saved results into temporary directories. The analytical dispatcher
is patched to fail if called. The validator recomputes verification quantities
from the already saved, allowlisted development bundle, without creating new
analytical answers, changing scores or accessing reserved observations. The normal
renderer only reads accepted selected artifacts.

## Recorded capture environment

- Chromium 153.0.8010.36 / Playwright 1.55.0, headless, `--no-sandbox --disable-gpu`.
- Publication viewport: 548×1100 CSS pixels, 500-pixel captured surface, device
  scale 3. Desktop: 1280×1100; mobile: 390×844; device scale 3.
- Local DejaVu Sans. No network font loading, animation, transitions or external requests.
- Font readiness and SVG text bounds checked before capture. Selectors, crop bounds,
  source HTML hashes, source evidence hashes, state and interaction events are in
  `capture_manifest.json`. Two Figure 2 states are actual `select_option` actions.
- PDF/PNG composition uses ReportLab 3.5.34 and Pillow 9.4.0 in system Python
  3.8.10; application Python is 3.10.18. pdfTeX 1.40.20 / TeX Live 2019, Poppler
  and the archived official template supply the four-page layout proof.

The official template was archived and verified in the preceding packages:
`artifacts/predraft_v1/template/manifest.json`. Its source archive SHA256 is
`ec6cfaa11962e08d5c6a402124f21c3bca3591397521406ab6d1889398a3807a`.
This stage reuses that verified copy: text width 158.0134 mm, column gap 8 mm,
panel width 75.0067 mm. No new template or geometry is substituted.

UI PDFs contain raster browser captures with vector panel lettering and external
annotations. They are **not vector dashboards**. SVG files under each gallery
view's `charts/` directory are genuine vectors carrying saved-value metadata.
Composite PNGs use 300 dpi; proof renders use 96 and 150 dpi. Critical figure text
is at least 8.27 pt for preferred candidates. The 2×2 reduction trial is 5.17 pt
and explicitly not recommended for publication. Screen proofs are not a calibrated
physical print or a usability study.

The original presentation, pre-draft and manuscript replay/build commands remain
available unchanged. This regeneration produces new candidate assets only; it
does not replace manuscript draft v1's figures or begin a new research stage.
