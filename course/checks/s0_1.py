"""Checks for S0.1 · Reading formulas."""

import sys

import numpy as np

from .. import data
from ..checking import Todo, Wrong, describe, exercise, progress

LESSON = "S0.1"


def _close(v, target, tol=1e-6):
    return bool(np.isclose(v, target, rtol=tol, atol=1e-9))


def six_essays() -> np.ndarray:
    """Reference counts of the first six essays of vol. 12, no. 2 (2023), in page order."""
    bib = data.bibliothecae()
    counts = bib.article_reference.drop_duplicates().groupby("id").size()
    a = bib.articles
    issue = a[(a["volume"] == "12") & (a["issue"] == "2") & (a["section"] == "Essays")]
    issue = issue.assign(first_page=issue["pages"].str.split("-").str[0].astype(int))
    ids = issue.sort_values("first_page").head(6)["id"]
    return counts.reindex(ids).to_numpy()


def _counts():
    bib = data.bibliothecae()
    return bib.article_reference.drop_duplicates().groupby("id").size()


@exercise(LESSON, 1, "Subscripts in Python")
def ex1(fb, x3, xn, i_max):
    x = six_essays()
    fb.number("x3", x3, x[2], diagnose=lambda v:
              "that is x₄: Python counts positions from 0, so x₃ is x[2]" if _close(v, x[3]) else
              "that is x₂: x₃ is the third value, x[2] in Python" if _close(v, x[1]) else None, fmt="{:g}")
    fb.number("xn", xn, x[-1], diagnose=lambda v:
              "that is the number of values, n; x_n is the last value, x[n - 1] or x[-1]"
              if _close(v, len(x)) else None, fmt="{:g}")
    pos = int(np.argmax(x))
    fb.number("i_max", i_max, pos + 1, diagnose=lambda v:
              "that is the Python position; a subscript counts from 1, so add 1" if _close(v, pos) else
              "that is the largest value itself; we want its position" if _close(v, x.max()) else None,
              fmt="{:g}")


@exercise(LESSON, 2, "From formula to code")
def ex2(fb, sum_x, sum_sq, sq_sum, sum_dev):
    x = six_essays()
    a, b, c, d = x.sum(), (x ** 2).sum(), x.sum() ** 2, (x - 50).sum()
    fb.number("sum_x", sum_x, a, fmt="{:,.0f}")
    fb.number("sum_sq", sum_sq, b, fmt="{:,.0f}", diagnose=lambda v:
              "that is the square of the sum: square each value first, then add" if _close(v, c) else None)
    fb.number("sq_sum", sq_sum, c, fmt="{:,.0f}", diagnose=lambda v:
              "that is the sum of the squares: add first, then square the total" if _close(v, b) else None)
    fb.number("sum_dev", sum_dev, d, fmt="{:,.0f}", diagnose=lambda v:
              "you subtracted 50 once; the formula subtracts it from every value, six times in all"
              if _close(v, a - 50) else None)
    if fb.status() == "pass":
        fb.info(f"Σ(x_i − 50) = Σx_i − 6 × 50 = {a} − 300 = {d}: a number inside the sum is added (or "
                "subtracted) once per value.")


@exercise(LESSON, 3, "From code to formula")
def ex3(fb, answer):
    if answer is ...:
        raise Todo("set answer to \"A\", \"B\" or \"C\"")
    choice = str(answer).strip().upper()
    if choice not in {"A", "B", "C"}:
        raise Wrong(f"answer should be \"A\", \"B\" or \"C\", not {describe(answer)}")
    if choice == "B":
        fb.ok("B: inside the loop, 10 is taken from each value and the result squared, then added to the total")
    elif choice == "A":
        fb.no("A subtracts 10² once, after the sum. In the loop, 10 is taken from every value before squaring")
    else:
        fb.no("C squares once, at the end. In the loop, every value is squared before it is added")


@exercise(LESSON, 4, "A product")
def ex4(fb, prod_p, prod_x3):
    p = np.array([0.5, 0.2, 0.9, 0.4])
    x = six_essays()
    fb.number("prod_p", prod_p, np.prod(p), fmt="{:g}", diagnose=lambda v:
              "that is the sum; Π multiplies" if _close(v, p.sum()) else None)
    fb.number("prod_x3", prod_x3, np.prod(x[:3]), fmt="{:,.0f}", diagnose=lambda v:
              "that is the sum; Π multiplies" if _close(v, x[:3].sum()) else
              "use the first three values, x[0] to x[2]" if _close(v, np.prod(x[1:4])) else None)


@exercise(LESSON, 5, "A formula in six steps")
def ex5(fb, xbar, dev, sq, total, s):
    x = six_essays()
    m = x.mean()
    fb.number("xbar", xbar, m, fmt="{:.4g}", diagnose=lambda v:
              "that is the sum; divide it by n" if _close(v, x.sum()) else None)
    for name, value, target in [("dev", dev, x - m), ("sq", sq, (x - m) ** 2)]:
        if value is ...:
            fb.todo(f"{name}: replace the ... with your answer")
            continue
        arr = np.asarray(value, dtype=float)
        if arr.shape != target.shape:
            fb.no(f"{name} should hold one number per value (6), but it is {describe(value)}")
        elif np.allclose(arr, target):
            fb.ok(f"{name} = {np.round(arr, 1).tolist()}")
        elif name == "sq" and np.allclose(arr, np.abs(x - m)):
            fb.no("sq holds the absolute deviations: square them instead (** 2)")
        else:
            fb.no(f"{name} is not right yet: compare it with the step in the list above")
    t = ((x - m) ** 2).sum()
    fb.number("total", total, t, fmt="{:,.2f}")
    target_s = np.sqrt(t / (len(x) - 1))
    fb.number("s", s, target_s, fmt="{:.4f}", diagnose=lambda v:
              "you divided by n; the formula divides by n − 1" if _close(v, np.sqrt(t / len(x))) else
              "take the square root at the end" if _close(v, t / (len(x) - 1)) else None)
    if fb.status() == "pass":
        fb.info(f"s = {target_s:.2f}. np.std(x, ddof=1) gives the same number in one call.")


@exercise(LESSON, 6, "Counting with a condition")
def ex6(fb, n_articles, n_long, share_long):
    c = _counts()
    fb.number("n_articles", n_articles, len(c), fmt="{:g}")
    k = int((c >= 50).sum())
    fb.number("n_long", n_long, k, fmt="{:g}", diagnose=lambda v:
              "use ≥ (at least 50): >= in Python, not >" if _close(v, (c > 50).sum()) else None)
    fb.number("share_long", share_long, k / len(c), fmt="{:.3f}", diagnose=lambda v:
              "give a proportion between 0 and 1, not a percentage" if _close(v, 100 * k / len(c)) else
              "divide by the number of articles with references, not by all 321 articles"
              if _close(v, k / 321) else None)
    if fb.status() == "pass":
        fb.info(f"{k} of the {len(c)} articles with references cite at least 50 works: "
                f"{k / len(c):.1%} of them.")


@exercise(LESSON, 7, "Points or percent?")
def ex7(fb, share_old, share_new, diff_points, rel_change):
    a = data.bibliothecae().articles
    year = a["date"].str[:4].astype(int)
    has = (a["abstract"] != "").to_numpy()
    old, new = has[(year <= 2018).to_numpy()].mean(), has[(year > 2018).to_numpy()].mean()
    dp, rc = 100 * (new - old), 100 * (new - old) / old
    fb.number("share_old", share_old, old, abs_tol=5e-4, fmt="{:.4f}", diagnose=lambda v:
              "give a proportion between 0 and 1 (percentages come next)" if _close(v, 100 * old, 1e-3) else None)
    fb.number("share_new", share_new, new, abs_tol=5e-4, fmt="{:.4f}", diagnose=lambda v:
              "give a proportion between 0 and 1 (percentages come next)" if _close(v, 100 * new, 1e-3) else None)
    fb.number("diff_points", diff_points, dp, abs_tol=0.05, fmt="{:.2f}", diagnose=lambda v:
              "multiply the difference of the proportions by 100 to express it in percentage points"
              if _close(v, new - old, 1e-3) else
              "that is the relative change; percentage points are new % minus old %" if _close(v, rc, 1e-3) else None)
    fb.number("rel_change", rel_change, rc, abs_tol=0.05, fmt="{:.2f}", diagnose=lambda v:
              "multiply by 100 to express it in percent" if _close(v, rc / 100, 1e-3) else
              "that is the difference in points; the relative change divides it by the old value"
              if _close(v, dp, 1e-3) else
              "divide by the old value, not the new one" if _close(v, 100 * (new - old) / new, 1e-3) else None)
    if fb.status() == "pass":
        fb.info(f"Abstracts rose from {old:.1%} to {new:.1%} of articles: up {dp:.1f} percentage points, "
                f"a relative increase of {rc:.0f}%.")


def summary():
    """Show which S0.1 exercises you have done in this session."""
    return progress(sys.modules[__name__])
