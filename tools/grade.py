"""Run answer notebooks and summarise their exercise checks.

    python tools/grade.py                                  # every notebook in answers/
    python tools/grade.py answers/s1-1-centre-spread-shape.ipynb

Prints a Markdown summary and, on GitHub Actions, adds it to the job summary.
Executed notebooks are saved in _build/graded/. Grading informs; it always
exits with status 0 unless a notebook cannot be read at all.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import nbformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbrun import execute, exercise_count  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ICON = {"pass": "✅", "fail": "❌", "todo": "⬜", "partial": "⬜", "error": "⚠️"}


def grade(path: Path, out_dir: Path) -> str:
    nb = nbformat.read(path, as_version=4)
    n = exercise_count(nb)
    executed, results, errors = execute(nb, path.parent)
    out_dir.mkdir(parents=True, exist_ok=True)
    nbformat.write(executed, out_dir / path.name)

    done = sum(r["status"] == "pass" for r in results.values())
    lines = [f"### {path.name}", "", f"**{done} of {max(n, len(results))} exercises done.**", ""]
    if results:
        lines += ["| Exercise | Status | Feedback |", "| --- | --- | --- |"]
        for r in sorted(results.values(), key=lambda r: (r["lesson"], r["exercise"])):
            feedback = " · ".join(r["lines"]).replace("|", "\\|")
            if len(feedback) > 220:
                feedback = feedback[:217] + "..."
            lines.append(f"| {r['lesson']} · {r['exercise']} {r['title']} | {ICON[r['status']]} | {feedback} |")
    else:
        lines.append("No exercise checks ran. Is the setup cell intact?")
    if errors:
        lines += ["", "Cells that raised an error:", ""] + [f"- `{e}`" for e in errors]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("notebooks", nargs="*", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "_build" / "graded")
    args = parser.parse_args(argv)
    paths = args.notebooks or sorted(p for p in (ROOT / "answers").glob("**/*.ipynb")
                                     if "private" not in p.parts and ".ipynb_checkpoints" not in p.parts)
    if not paths:
        print("No notebooks to grade in answers/.")
        return 0
    report = "## Exercise checks\n\n" + "\n".join(grade(p, args.out) for p in paths)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
