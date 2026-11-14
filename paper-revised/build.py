"""Build the revised paper and a readable red/blue comparison to the submission.

Requires pdfLaTeX, BibTeX, latexdiff and Poppler. Does not run experiments.
Run: python3 paper-revised/build.py
"""
import difflib
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ORIGINAL = ROOT / "paper/draft_v1"


def run(args):
    result = subprocess.run(args, cwd=HERE, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(result.stdout[-6000:])
    return result.stdout


def compile_pdf(stem):
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", stem + ".tex"])
    run(["bibtex", stem])
    for _ in range(2):
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", stem + ".tex"])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    old = (ORIGINAL / "main.tex").read_text()
    new = (HERE / "main.tex").read_text()
    for label, pattern in [
        ("title", r"\\title\{([^\n]+)\}"),
        ("abstract", r"\\abstract\{(.*?)\}\n\\onecolumn"),
        ("introduction", r"\\section\{\\uppercase\{Introduction\}\}(.*?)\\section\{\\uppercase\{Related Work\}\}"),
    ]:
        assert re.search(pattern, old, re.S).group(1).strip() == re.search(pattern, new, re.S).group(1).strip(), label
    for block in ("numbers", "outcomes"):
        pattern = r"% BEGIN GENERATED: " + block + r"\n(.*?)% END GENERATED: " + block
        assert re.search(pattern, old, re.S).group(1) == re.search(pattern, new, re.S).group(1), block
    for name in ("article.cls", "SCITEPRESS.sty", "apalike.sty", "apalike.bst", "references.bib"):
        assert sha(HERE / name) == sha(ORIGINAL / name), name
    freeze = json.loads((ROOT / "artifacts/stage6/protocol/freeze.json").read_text())
    assert all(sha(ROOT / name) == value for name, value in freeze["files"].items())
    compile_pdf("main")
    info = run(["pdfinfo", "main.pdf"])
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    assert pages <= 8, "Short-paper page limit exceeded: " + str(pages)
    log = (HERE / "main.log").read_text()
    assert not re.search(r"Overfull|undefined|LaTeX Warning:|Missing character", log), "Inspect main.log"
    delta = subprocess.run(["latexdiff", "--graphics-markup=none",
                            str(ORIGINAL / "main.tex"), str(HERE / "main.tex")],
                           text=True, capture_output=True, check=True)
    # Deleted floats have no labels in latexdiff's output. Resolve only those
    # deleted references to their submitted numbers, avoiding unreadable '??'.
    counters = {"figure": 0, "table": 0}
    deleted_refs = {}
    for match in re.finditer(r"\\begin\{(figure\*?|table\*?)\}(.*?)\\end\{\1\}", old, re.S):
        kind = match.group(1).rstrip("*")
        counters[kind] += 1
        label = re.search(r"\\label\{([^}]+)\}", match.group(2))
        if label and "\\label{" + label.group(1) + "}" not in new:
            deleted_refs[label.group(1)] = counters[kind]
    diff_source = delta.stdout
    for label, number in deleted_refs.items():
        diff_source = diff_source.replace("\\ref{" + label + "}", str(number))
    (HERE / "changes.tex").write_text(diff_source)
    compile_pdf("changes")
    assert not re.search(r"Overfull|undefined|LaTeX Warning:|Missing character",
                         (HERE / "changes.log").read_text()), "Inspect changes.log"
    (HERE / "changes.diff").write_text("".join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile="submitted/main.tex", tofile="paper-revised/main.tex")))
    checks = {
        "pages_including_references": pages,
        "short_paper_limit": 8,
        "length_rule": "https://icaart.scitevents.org/Guidelines.aspx",
        "rule_checked_on": "2026-11-14",
        "title_abstract_introduction_unchanged": True,
        "frozen_numbers_and_outcome_table_unchanged": True,
        "official_template_and_bibliography_unchanged": True,
        "frozen_experiment_files_verified": len(freeze["files"]),
        "no_overfull_boxes_missing_glyphs_or_unresolved_references": True,
        "submitted_pdf_sha256": sha(ORIGINAL / "main.pdf"),
        "submitted_tex_sha256": sha(ORIGINAL / "main.tex"),
        "revised_pdf_sha256": sha(HERE / "main.pdf"),
        "revised_tex_sha256": sha(HERE / "main.tex"),
        "diff_pdf_sha256": sha(HERE / "changes.pdf"),
        "diff_deleted_references_use_submitted_numbers": deleted_refs,
        "new_evidence": "Post hoc paired statistics and duplicate sensitivity only; no new inference or human ratings",
    }
    (HERE / "checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
