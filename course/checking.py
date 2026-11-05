"""Friendly exercise checks.

A check never raises. It prints a verdict line and a few notes, and records
the result in RESULTS so that tools/grade.py can summarise a notebook.

Verdicts: ✅ done · ❌ not yet · ⬜ not attempted (or only partly) · ⚠️ the check itself failed.
"""

from __future__ import annotations

import contextlib
import functools
import math
import numbers
import warnings
from types import ModuleType

import numpy as np
import pandas as pd

ICON = {"pass": "✅", "fail": "❌", "todo": "⬜", "partial": "⬜", "error": "⚠️"}
MARK = {"pass": "✓", "fail": "✗", "todo": "…", "info": "→", "error": "!"}
RESULTS: dict[str, dict] = {}


@contextlib.contextmanager
def quiet():
    """Silence library warnings (e.g. powerlaw's optimiser) inside a check."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield


class Todo(Exception):
    """The learner has not answered (part of) the exercise yet."""


class Wrong(Exception):
    """The learner's answer cannot be checked further (wrong type, crash...)."""


def describe(value) -> str:
    """Short description of a value, for feedback messages."""
    if value is None:
        return "None"
    if isinstance(value, str):
        return f"the string {value[:30]!r}"
    if isinstance(value, pd.DataFrame):
        return f"a DataFrame of shape {value.shape}"
    if isinstance(value, pd.Series):
        return f"a pandas Series of length {len(value)}"
    if isinstance(value, np.ndarray):
        return f"a numpy array of shape {value.shape}"
    if isinstance(value, (list, tuple, dict, set)):
        return f"a {type(value).__name__} of length {len(value)}"
    return f"a {type(value).__name__}"


def as_number(value) -> float:
    """Convert a scalar answer (int, float, numpy scalar, 1-element array) to float."""
    if isinstance(value, (bool, np.bool_)):
        raise Wrong(f"expected a number but got {value!r} (a boolean)")
    if isinstance(value, numbers.Number):
        return float(value)
    if isinstance(value, (np.ndarray, pd.Series)) and value.size == 1:
        return float(np.asarray(value).ravel()[0])
    raise Wrong(f"expected a single number but got {describe(value)}")


class Feedback:
    """Collects the lines of feedback for one exercise."""

    def __init__(self):
        self.lines: list[tuple[str, str]] = []

    # raw lines
    def ok(self, text):
        self.lines.append(("pass", text))

    def no(self, text):
        self.lines.append(("fail", text))

    def todo(self, text):
        self.lines.append(("todo", text))

    def info(self, text):
        self.lines.append(("info", text))

    def error(self, text):
        self.lines.append(("error", text))

    # helpers
    def number(self, name, value, expected, *, abs_tol=0.0, rel_tol=1e-6,
               diagnose=None, fmt="{:,.4g}") -> bool:
        """Check a scalar answer; returns True if it is right."""
        if value is ...:
            self.todo(f"{name}: replace the ... with your answer")
            return False
        try:
            v = as_number(value)
        except Wrong as e:
            self.no(f"{name}: {e}")
            return False
        if math.isnan(v):
            self.no(f"{name} is NaN (not a number): look for an empty selection or missing values")
            return False
        if math.isclose(v, float(expected), rel_tol=rel_tol, abs_tol=abs_tol):
            self.ok(f"{name} = {fmt.format(v)}")
            return True
        hint = diagnose(v) if diagnose else None
        self.no(f"{name} = {fmt.format(v)} is not right yet" + (f": {hint}" if hint else "."))
        return False

    def call(self, name, func, *args, **kwargs):
        """Call the learner's function; turn 'not written yet' and crashes into feedback."""
        if func is ...:
            raise Todo(f"define {name} first")
        if not callable(func):
            raise Wrong(f"{name} should be a function, but it is {describe(func)}")
        try:
            out = func(*args, **kwargs)
        except Exception as e:  # the learner's code crashed
            if _unfinished(func, e):
                raise Todo(f"{name} still contains ...: complete it, then run the cell again") from None
            raise Wrong(f"calling {name} raised {type(e).__name__}: {e}") from None
        if out is None or out is ...:
            raise Todo(f"{name} returns nothing yet: complete its body and `return` the result")
        if isinstance(out, (tuple, list)) and any(part is ... for part in out):
            raise Todo(f"{name} still returns ...: complete it, then run the cell again")
        return out

    # verdict
    def status(self) -> str:
        kinds = {k for k, _ in self.lines}
        if "error" in kinds:
            return "error"
        if "fail" in kinds:
            return "fail"
        if "todo" in kinds:
            return "partial" if "pass" in kinds else "todo"
        return "pass" if "pass" in kinds else "todo"


def _unfinished(func, error: Exception) -> bool:
    """True if the crash happened while the learner's function still held a `...` placeholder."""
    code = getattr(func, "__code__", None)
    tb = error.__traceback__
    while tb is not None:
        if tb.tb_frame.f_code is code and any(v is ... for v in tb.tb_frame.f_locals.values()):
            return True
        tb = tb.tb_next
    return False


def exercise(lesson: str, number: int, title: str):
    """Decorator that turns `check(fb, *answers)` into a safe, printing check."""

    def decorate(check):
        @functools.wraps(check)
        def run(*args, **kwargs):
            fb = Feedback()
            try:
                check(fb, *args, **kwargs)
            except Todo as e:
                fb.todo(str(e))
            except Wrong as e:
                fb.no(str(e))
            except Exception as e:  # a bug in the check, not in your answer
                fb.error(f"the check itself failed ({type(e).__name__}: {e}). Your answer may be fine.")
            _report(lesson, number, title, fb)

        run.lesson, run.number, run.title = lesson, number, title
        run.__doc__ = f"Check {lesson} · Exercise {number} · {title}"
        return run

    return decorate


def _report(lesson, number, title, fb: Feedback):
    status = fb.status()
    head = f"{ICON[status]} {lesson} · Exercise {number} · {title}"
    if status == "partial":
        head += " (partly done)"
    lines = [head]
    lines += [f"   {MARK.get(kind, '·')} {text}" for kind, text in fb.lines]
    print("\n".join(lines))
    RESULTS[f"{lesson}/{number}"] = {
        "lesson": lesson, "exercise": number, "title": title, "status": status,
        "lines": [text for _, text in fb.lines],
    }


def exercises_of(module: ModuleType):
    """The check functions defined in a checks module, in exercise order."""
    found = [v for v in vars(module).values() if callable(v) and hasattr(v, "lesson")]
    return sorted(found, key=lambda f: f.number)


def progress(module: ModuleType) -> pd.DataFrame:
    """Print and return the status of every exercise of a lesson in this session."""
    rows = []
    for f in exercises_of(module):
        r = RESULTS.get(f"{f.lesson}/{f.number}")
        status = r["status"] if r else "todo"
        rows.append({"exercise": f.number, "title": f.title, "status": status})
    table = pd.DataFrame(rows)
    done = int((table["status"] == "pass").sum()) if len(table) else 0
    lesson = exercises_of(module)[0].lesson if rows else "?"
    print(f"{lesson}: {done} of {len(table)} exercises done")
    for row in rows:
        print(f"  {ICON[row['status']]} Exercise {row['exercise']} · {row['title']}")
    return table
