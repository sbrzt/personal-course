"""Checks for S0.2 · Powers, exponentials and logarithms."""

import functools
import sys

import numpy as np
import pandas as pd

from .. import bibliothecae, data, stats
from ..checking import Todo, Wrong, describe, exercise, progress

LESSON = "S0.2"


def _close(v, target, tol=1e-6):
    return bool(np.isclose(v, target, rtol=tol, atol=1e-9))


def _array(fb, name, value, target, wrong=()) -> bool:
    """Check an array answer; `wrong` lists (array, hint) pairs for likely mistakes."""
    if value is ...:
        fb.todo(f"{name}: replace the ... with your answer")
        return False
    try:
        arr = np.asarray(value, dtype=float)
    except (TypeError, ValueError):
        fb.no(f"{name} should hold numbers, but it is {describe(value)}")
        return False
    target = np.asarray(target, dtype=float)
    if arr.shape != target.shape:
        fb.no(f"{name} should hold {target.size} numbers, one per value, but it is {describe(value)}")
        return False
    if np.allclose(arr, target, rtol=1e-6, atol=1e-9):
        fb.ok(f"{name} is right")
        return True
    for other, hint in wrong:
        other = np.asarray(other, dtype=float)
        if other.shape == arr.shape and np.allclose(arr, other, rtol=1e-6, atol=1e-9, equal_nan=True):
            fb.no(f"{name} is not right yet: {hint}")
            return False
    fb.no(f"{name} is not right yet: compare a few of its values with what you get by hand")
    return False


@functools.lru_cache(maxsize=1)
def canto_chances():
    """Chances of the words of the first line, and of the whole first canto, of Inferno."""
    words = stats.tokenize(data.commedia())
    chance = pd.Series(words).value_counts(normalize=True)
    lines = data.commedia(headings=True).splitlines()
    canto = "\n".join(lines[lines.index("INFERNO · CANTO I") + 1:lines.index("INFERNO · CANTO II")])
    first = canto.strip().splitlines()[0]
    return chance.loc[stats.tokenize(first)].to_numpy(), chance.loc[stats.tokenize(canto)].to_numpy()


def corpus_sizes() -> pd.Series:
    """The six sizes of section 7, in the lesson's order."""
    bib = data.bibliothecae()
    text = data.commedia()
    return pd.Series({
        "references, median article": bibliothecae.refs_per_article(bib).median(),
        "articles": len(bib.articles),
        "authors cited": len(bibliothecae.cited_author_counts(bib)),
        "references": len(bib.references),
        "words of the Commedia": len(stats.tokenize(text)),
        "characters of the Commedia": len(text),
    })


def cited_decades() -> pd.Series:
    """Citations by the decade of publication of the cited work."""
    years = bibliothecae.cited_years(data.bibliothecae())
    return (years // 10 * 10).value_counts().sort_index()


@exercise(LESSON, 1, "Powers in Python")
def ex1(fb, two_10, milli, root_81, cube_root, fifth):
    fb.number("two_10", two_10, 2 ** 10, fmt="{:,.6g}", diagnose=lambda v:
              "^ is not a power in Python (2 ^ 10 gives 8): use **" if _close(v, 2 ^ 10) else
              "* multiplies; ** raises to a power" if _close(v, 20) else None)
    fb.number("milli", milli, 1e-3, fmt="{:g}", diagnose=lambda v:
              "a negative exponent divides: 10 ** -3 is 1 / 10 ** 3, a small positive number"
              if _close(v, -1000) else
              "* multiplies; ** raises to a power" if _close(v, -30) else
              "you need a negative exponent: 10 ** -3" if _close(v, 1000) else None)
    fb.number("root_81", root_81, 9, fmt="{:g}", diagnose=lambda v:
              "brackets: 81 ** 1/2 computes (81 ** 1) / 2; write 81 ** (1 / 2)" if _close(v, 40.5) else
              "that is 81 squared; the square root is 81 ** (1 / 2)" if _close(v, 81 ** 2) else None)
    fb.number("cube_root", cube_root, 10, fmt="{:g}", diagnose=lambda v:
              "brackets: 1000 ** 1/3 computes (1000 ** 1) / 3; write 1000 ** (1 / 3)"
              if _close(v, 1000 / 3) else None)
    fb.number("fifth", fifth, 440 * 2 ** (7 / 12), fmt="{:.2f}", diagnose=lambda v:
              "brackets: 2 ** 7/12 computes (2 ** 7) / 12; write 2 ** (7 / 12)"
              if _close(v, 440 * 2 ** 7 / 12) else
              "multiply by 440, concert A's frequency" if _close(v, 2 ** (7 / 12)) else None)
    if fb.status() == "pass":
        fb.info("Python may print 1000 ** (1/3) as 9.999999999999998: computers store most fractions "
                "with a tiny rounding error. np.cbrt(1000) gives exactly 10.")


@exercise(LESSON, 2, "Adding or multiplying")
def ex2(fb, added, multiplied, first):
    t = np.arange(0, 31)
    a, m = 1000 + 500 * t, 1000 * 1.2 ** t
    _array(fb, "added", added, a, wrong=[
        (500 * t, "start from 1,000: 1000 + 500 * t"),
        (1000 + 500 ** t, "plan A adds 500 each year, so it needs 500 * t, not a power"),
    ])
    _array(fb, "multiplied", multiplied, m, wrong=[
        (1000 * 0.2 ** t, "the growth factor is 1 + 0.2 = 1.2, not 0.2"),
        (1000 * 20 ** t, "20% is 0.2, so the growth factor is 1 + 0.2 = 1.2"),
        (1000 * 1.2 * t, "use ** t: the factor 1.2 is applied once per year, t times"),
        (1000 + 1.2 ** t, "multiply the starting 1,000 by the factor: 1000 * 1.2 ** t"),
        (1000 + 1000 * 0.2 * t, "that adds 20% of the starting collection each year, which is growth by adding"),
    ])
    k = int(t[m > a][0])
    fb.number("first", first, k, fmt="{:g}", diagnose=lambda v:
              "in year 0 both plans have 1,000 items: look for the first year where plan B has more (>)"
              if _close(v, 0) else
              f"in year {k - 1} plan A is still ahead ({a[k - 1]:,} items against {m[k - 1]:,.0f})"
              if _close(v, k - 1) else
              "t already counts from 0, so its values are the years: take t[...][0]" if _close(v, k + 1) else None)
    if fb.status() == "pass":
        fb.info(f"Plan B overtakes plan A in year {k}. After 30 years it has {m[30]:,.0f} items, "
                f"against plan A's {a[30]:,}.")


@exercise(LESSON, 3, "Logarithms in Python")
def ex3(fb, a, b, c, d, questions):
    fb.number("a", a, 4, fmt="{:.4g}", diagnose=lambda v:
              "np.log is the natural log (base e); use np.log10" if _close(v, np.log(10_000)) else None)
    fb.number("b", b, -3, fmt="{:.4g}", diagnose=lambda v:
              "1/8 is below 1, so its log is negative" if _close(v, 3) else
              "use base 2: np.log2" if _close(v, np.log10(1 / 8)) or _close(v, np.log(1 / 8)) else None)
    fb.number("c", c, 5, fmt="{:.4g}", diagnose=lambda v:
              "ln is np.log, the natural log; np.log10 is base 10" if _close(v, np.log10(np.exp(5))) else
              "that is e to the 5 itself; take its natural log" if _close(v, np.exp(5)) else None)
    fb.number("d", d, 4, fmt="{:.4g}", diagnose=lambda v:
              "divide the other way: ln 81 / ln 3" if _close(v, np.log(3) / np.log(81)) else
              "divide the logs, don't multiply them" if _close(v, np.log(81) * np.log(3)) else
              "that is log base 3 of 3; you want 81" if _close(v, 1) else None)
    q = float(np.ceil(np.log2(321)))
    fb.number("questions", questions, q, fmt="{:.4g}", diagnose=lambda v:
              "part of a question is still a whole question: round up with np.ceil" if _close(v, np.log2(321)) else
              f"2 to the {q - 1:.0f} is {2 ** (q - 1):.0f}, fewer than 321: round up, not down"
              if _close(v, q - 1) else
              "count halvings: use the log in base 2" if _close(v, np.ceil(np.log10(321))) else None)
    if fb.status() == "pass":
        fb.info(f"{q:.0f} yes/no questions find one article among 321, because 2 to the {q:.0f} "
                f"is {2 ** q:.0f}, the first power of 2 above 321.")


@exercise(LESSON, 4, "True or false?")
def ex4(fb, answer):
    if answer is ...:
        raise Todo('set answer to the letters of the true statements, for example "AB"')
    if not isinstance(answer, str):
        raise Wrong(f'answer should be a string of letters such as "AB", not {describe(answer)}')
    picked = {ch for ch in answer.upper() if ch.isalpha()}
    unknown = picked - set("ABCDEF")
    if unknown:
        raise Wrong(f"use only the letters A to F (you wrote {', '.join(sorted(unknown))})")
    if not picked:
        raise Todo("answer holds no letters yet")
    true = set("ACEF")
    if picked == true:
        fb.ok("A, C, E and F: the rules of logarithms, and log 1 = 0 in every base")
        return
    why = {
        "B": "B is false: there is no rule for the log of a sum. In base 10, log(10 + 100) = log 110 = 2.04, "
             "but log 10 + log 100 = 3",
        "D": "D is false: the log of a quotient is a difference of logs, not a quotient. In base 10, "
             "log(100 / 10) = 1, but log 100 / log 10 = 2",
    }
    for letter in sorted(picked - true):
        fb.no(why[letter])
    missing = len(true - picked)
    if missing:
        fb.no(f"{missing} true statement{'s are' if missing > 1 else ' is'} missing: test every statement "
              "with numbers, for example a = 10 and b = 100")


@exercise(LESSON, 5, "The chance of a canto")
def ex5(fb, prod_line, prod_canto, log_canto):
    p_line, p_canto = canto_chances()
    fb.number("prod_line", prod_line, np.prod(p_line), fmt="{:.3g}", diagnose=lambda v:
              "that is the sum; the chance of the line is the product: np.prod" if _close(v, p_line.sum()) else None)
    fb.number("prod_canto", prod_canto, np.prod(p_canto), fmt="{:g}", diagnose=lambda v:
              "that is the sum; the chance of the canto is the product: np.prod" if _close(v, p_canto.sum()) else None)
    if isinstance(log_canto, (np.ndarray, pd.Series, list)) and np.size(log_canto) > 1:
        fb.no("log_canto should be one number: add up the logs with .sum()")
    else:
        target = np.log10(p_canto).sum()
        fb.number("log_canto", log_canto, target, abs_tol=0.01, fmt="{:,.2f}", diagnose=lambda v:
                  "that is in base e; use np.log10 to read the answer as a power of 10"
                  if _close(v, np.log(p_canto).sum()) else
                  "that is the log of 0.0, minus infinity: take the log of each chance first, "
                  "np.log10(p_canto), then add them" if np.isinf(v) else None)
    if fb.status() == "pass":
        fb.info(f"The first line has a chance of {np.prod(p_line):.1e}; the whole canto about 10 to the "
                f"power {np.log10(p_canto).sum():,.0f}, a number the computer can store only as its log.")


@exercise(LESSON, 6, "Orders of magnitude")
def ex6(fb, logs, orders, gap):
    s = corpus_sizes().to_numpy(dtype=float)
    lg = np.log10(s)
    _array(fb, "logs", logs, lg, wrong=[
        (np.log(s), "np.log is the natural log; use np.log10"),
        (np.log2(s), "use base 10: np.log10"),
    ])
    _array(fb, "orders", orders, np.floor(lg), wrong=[
        (np.round(lg), "round down with np.floor: 7,507 is in the thousands (order 3), although its log is 3.9"),
        (np.ceil(lg), "round down with np.floor, not up"),
        (lg, "round the logs down to whole numbers with np.floor"),
    ])
    g = lg[4] - lg[0]
    fb.number("gap", gap, g, abs_tol=1e-3, fmt="{:.3f}", diagnose=lambda v:
              "use the logs themselves, not the rounded orders" if _close(v, np.floor(lg[4]) - np.floor(lg[0])) else
              "that is the ratio of the two sizes; take its log in base 10" if _close(v, s[4] / s[0]) else
              "subtract the smaller log from the larger one" if _close(v, -g) else None)
    if fb.status() == "pass":
        fb.info(f"The Commedia has {s[4] / s[0]:,.0f} times as many words as the median article has "
                f"references: {g:.2f} orders of magnitude.")


@exercise(LESSON, 7, "Reading a log axis")
def ex7(fb, top, mid_log, mid_lin):
    fb.number("top", top, 10 ** 2.5, fmt="{:.2f}", diagnose=lambda v:
              "each step multiplies by 10, so 2.5 steps multiply by 10 ** 2.5" if _close(v, 25) else
              "that is the height on the axis, the log; the value is 10 to that power" if _close(v, 2.5) else None)
    fb.number("mid_log", mid_log, 40, fmt="{:.4g}", diagnose=lambda v:
              "that is the middle on a linear axis; on a log axis, average the logs" if _close(v, 50) else
              "that is the log of the answer: turn it back into a value with 10 ** ..."
              if _close(v, (np.log10(20) + np.log10(80)) / 2) else None)
    fb.number("mid_lin", mid_lin, 50, fmt="{:.4g}", diagnose=lambda v:
              "that is the middle on a log axis; on a linear axis it is the plain average" if _close(v, 40) else None)
    if fb.status() == "pass":
        fb.info("On a log axis, the middle of 20 and 80 is their geometric mean, the square root of "
                "20 × 80 = 1,600, which is 40.")


@exercise(LESSON, 8, "How fast does the cited literature double?")
def ex8(fb, factor, g_year, doubling):
    d = cited_decades()
    f = d[2010] / d[1950]
    g = f ** (1 / 60)
    t = np.log(2) / np.log(g)
    fb.number("factor", factor, f, fmt="{:.3f}", diagnose=lambda v:
              "divide the later count (2010s) by the earlier one (1950s)" if _close(v, 1 / f) else None)
    fb.number("g_year", g_year, g, fmt="{:.4f}", diagnose=lambda v:
              "that is the factor per decade; the 2010s come 60 years after the 1950s, so take the 60th "
              "root: ** (1 / 60)" if _close(v, f ** (1 / 6)) else
              "growth multiplies, so share it out with a root, ** (1 / 60), not with a division"
              if _close(v, f / 60) or _close(v, 1 + (f - 1) / 60) else None)
    fb.number("doubling", doubling, t, abs_tol=0.01, fmt="{:.2f}", diagnose=lambda v:
              "that is in decades: use the yearly factor" if _close(v, np.log(2) / np.log(f ** (1 / 6))) else
              "divide by the log of g_year, not by g_year itself" if _close(v, np.log(2) / g) else None)
    if fb.status() == "pass":
        fb.info(f"The cited literature grows about {100 * (g - 1):.1f}% a year and doubles every "
                f"{t:.0f} years. The rule of 70 gives 70 / {100 * (g - 1):.1f} = {70 / (100 * (g - 1)):.0f}.")


def summary():
    """Show which S0.2 exercises you have done in this session."""
    return progress(sys.modules[__name__])
