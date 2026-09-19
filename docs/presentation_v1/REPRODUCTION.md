# Preview and regenerate

Run from the repository root. No model weights, GPU, network service, API or raw
data download is needed. The generated pages work as local files. To use a local
HTTP preview (useful for browsing original source links), serve the repository:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory .
```

Open <http://127.0.0.1:8765/artifacts/presentation_v1/gallery/index.html>.
Stop the preview with Ctrl-C. It is a static file server; reference controls do not
send requests to an analysis backend. Each case has expanded and compact reading
routes, functional evidence expanders, original-content links and SVG downloads.

## Exact commands used

The existing project `.venv` supplies Python 3.10.18, Playwright 1.55.0 and pytest.
The local system `python3` is Python 3.8.10 with Pillow 9.4.0 and ReportLab 3.5.34.
Composition also uses `pdftoppm` from Poppler and local DejaVu Sans normal/bold
fonts. These were already installed; no dependency, font or model was downloaded.
The original dependency lockfile and project configuration are unchanged.

```bash
.venv/bin/python scripts/presentation_v1/build.py
.venv/bin/python scripts/presentation_v1/capture.py --chromium /snap/bin/chromium
python3 scripts/presentation_v1/compose.py
.venv/bin/python scripts/presentation_v1/browser_review.py --chromium /snap/bin/chromium
.venv/bin/python -m pytest -q tests/presentation_v1 tests/test_stage6.py
.venv/bin/python scripts/presentation_v1/verify.py --replay
```

On another machine, supply an installed Chromium path and the documented Python
packages/fonts. Browser rendering can vary across browser/font versions. The
capture and figure manifests record the tested versions and font hashes. Normal
preview requires none of the capture/composition packages.

The build/capture/compose scripts regenerate **presentation outputs only**. They do
not modify historical experiments. To compare a fresh reproduction without
overwriting this presentation package, use a new output directory whose basename
contains `presentation`:

```bash
.venv/bin/python scripts/presentation_v1/build.py --output artifacts/presentation_v1/reproduction-presentation
.venv/bin/python scripts/presentation_v1/capture.py --output artifacts/presentation_v1/reproduction-presentation --chromium /snap/bin/chromium
python3 scripts/presentation_v1/compose.py --output artifacts/presentation_v1/reproduction-presentation
.venv/bin/python scripts/presentation_v1/browser_review.py --output artifacts/presentation_v1/reproduction-presentation --chromium /snap/bin/chromium
```

Open that directory's `gallery/index.html` as a local file. Original dashboard
and document links resolve back to this checkout. Snap Chromium uses a private
`/tmp` and cannot read the host's `/tmp` through file URLs, so the tested fresh
output is inside the repository. A non-Snap Chromium may use other accessible
output paths. New timestamps and output-root paths
in manifests are expected; the source bindings and image content are reproducible
under the same browser/fonts. The composition PDF uses invariant metadata.

`verify.py --replay` reads only the existing Stage 6 **development** source bundle
to run the old independent source-bound validator. It does not call
`Engine.analyze`, request evidence, run an evaluator or start inference. The six
historical dashboards replay into temporary directories and their specifications,
evidence and selection provenance must remain equal. It also hashes all 7,254
files tracked at the starting commit. Without `--replay`, it only checks that
historical inventory. Original Stage 6 replay commands remain unchanged.

## Capture and publication dimensions

Chromium 153.0.8010.36 runs headless with `--disable-gpu`, on local saved files.
Expanded views use a 1000 × 1000 CSS-pixel viewport; compact views use 600 × 1000.
Both use device scale factor 3. Screenshots capture `.figure-surface`, not a whole
long page. The script waits for fonts, SVGs and the ready marker. Animations and
transitions are disabled. The manifest records each CSS crop, active reference,
page hash and original artifact hashes. Source IDs are preserved only in the
source/inspection records and evidence inspector; visible case names are stable
anonymous labels A–E.

No manuscript template was found. The assumed figure box is 180 mm wide and at
most 240 mm tall. Preferred figures use two 87 mm panels separated by 6 mm.
Critical compact HTML text is 18 CSS pixels, approximately 8.0 pt at that width;
supporting footer text is smaller. Composites are exported at 300 dpi. The 96 dpi
proofs are rendered at CSS 180 mm in the browser, and the PDF records the physical
dimensions. Physical screen size is not calibrated: print the PDF at 100% for a
literal ruler check. No physical print or independent human readability study
was performed. The rejected 2 × 2 overview and its reduction proof remain available.

PNG screenshots inside the PDF are raster. Panel lettering and editorial
annotations are PDF text. `gallery/*/charts/*.svg` are genuine native vector
charts with saved row metadata; they are not raster images in SVG containers.

## Source and capture records

- `artifacts/presentation_v1/historical_inventory.json`: starting commit and hashes.
- `artifacts/presentation_v1/source_manifest.json`: case selection, original IDs,
  source hashes, layout, deduplication and chart paths.
- `artifacts/presentation_v1/gallery/*/presentation.json`: selected evidence,
  original specification, claims, provenance and new mapping.
- `artifacts/presentation_v1/capture_manifest.json`: browser state, crops and hashes.
- `artifacts/presentation_v1/figure_manifest.json`: physical geometry, panel-to-capture
  mapping, fonts and raster/vector accounting.
- `artifacts/presentation_v1/verification.json`: old numerical validation/replay and
  historical immutability checks.
- `artifacts/presentation_v1/inspection/browser_verification.json`: browser links,
  source-bound displayed values, SVG text bounds and paper-proof checks.

Captions and the content/provenance contract are in this directory. This stage
does not resolve the Stage 6 scoring caveat or authorize final validation.
