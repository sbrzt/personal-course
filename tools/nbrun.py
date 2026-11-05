"""Shared helpers: execute a notebook and collect the results of its exercise checks."""

from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
MARKER = "@@COURSE-RESULTS@@"
SOLUTION = re.compile(r"<summary>\s*✅\s*Solution\s*</summary>(.*?)</details>", re.S)
PYTHON = re.compile(r"```python\n(.*?)```", re.S)


def is_exercise(cell) -> bool:
    return cell.cell_type == "code" and "exercise" in cell.metadata.get("tags", [])


def solved(nb):
    """A copy of nb in which every exercise cell holds the code of its solution."""
    nb = copy.deepcopy(nb)
    cells = nb.cells
    for i, cell in enumerate(cells):
        if not is_exercise(cell):
            continue
        for later in cells[i + 1:]:
            if is_exercise(later):
                break
            if later.cell_type != "markdown":
                continue
            block = SOLUTION.search(later.source)
            if block:
                code = PYTHON.search(block.group(1))
                if code:
                    cell.source = code.group(1).rstrip()
                break
    return nb


def with_results_cell(nb):
    nb = copy.deepcopy(nb)
    nb.cells.append(nbformat.v4.new_code_cell(
        "import json\n"
        "from course.checking import RESULTS\n"
        f"print({MARKER!r} + json.dumps(RESULTS))"
    ))
    return nb


def execute(nb, cwd: Path, timeout: int = 900):
    """Run nb in cwd; return (executed notebook, check results, list of cell errors)."""
    # make the course package importable from any folder, installed or not
    paths = [str(ROOT)] + [p for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p]
    os.environ["PYTHONPATH"] = os.pathsep.join(dict.fromkeys(paths))
    nb = with_results_cell(nb)
    client = NotebookClient(nb, timeout=timeout, kernel_name="python3", allow_errors=True,
                            resources={"metadata": {"path": str(cwd)}})
    client.execute()
    results, errors = {}, []
    for idx, cell in enumerate(nb.cells):
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                errors.append(f"cell {idx}: {out.get('ename')}: {out.get('evalue')}")
            text = out.get("text", "")
            if out.get("output_type") == "stream" and MARKER in text:
                results = json.loads(text.split(MARKER, 1)[1].strip())
    nb.cells.pop()  # drop the results cell
    return nb, results, errors


def exercise_count(nb) -> int:
    return sum(1 for c in nb.cells if is_exercise(c))
