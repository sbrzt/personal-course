"""Verify lessons: the solutions pass every check, and the blank exercises run cleanly.

    python tools/solve.py lessons/phase-s/*.ipynb            # both checks
    python tools/solve.py --solved-only lessons/phase-s/s1-1-centre-spread-shape.ipynb

For each notebook, the "solved" run copies the code of every ✅ Solution
block into its exercise cell, executes the notebook and expects every check
to pass. The "blank" run executes the notebook as learners get it and
expects no errors, with every check reporting "not attempted". Exits with
status 1 if anything is off.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nbformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nbrun import execute, exercise_count, solved  # noqa: E402


def check_notebook(path: Path, blank: bool = True) -> list[str]:
    problems = []
    nb = nbformat.read(path, as_version=4)
    n = exercise_count(nb)
    runs = [("solved", solved(nb), {"pass"})]
    if blank:
        runs.append(("blank", nb, {"todo"}))
    for label, version, expected in runs:
        _, results, errors = execute(version, path.parent)
        problems += [f"{path.name} [{label}] {e}" for e in errors]
        if len(results) != n:
            problems.append(f"{path.name} [{label}] {len(results)} checks reported, {n} exercise cells")
        for key, r in sorted(results.items()):
            if r["status"] not in expected:
                detail = "; ".join(r["lines"])[:300]
                problems.append(f"{path.name} [{label}] {key} {r['status']}: {detail}")
        print(f"{'✓' if not problems else '·'} {path.name} [{label}] {len(results)}/{n} checks")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("notebooks", nargs="+", type=Path)
    parser.add_argument("--solved-only", action="store_true", help="skip the blank run")
    args = parser.parse_args(argv)
    problems = []
    for path in args.notebooks:
        problems += check_notebook(path, blank=not args.solved_only)
    if problems:
        print("\nProblems:")
        print("\n".join(f"  - {p}" for p in problems))
        return 1
    print("\nAll lessons verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
