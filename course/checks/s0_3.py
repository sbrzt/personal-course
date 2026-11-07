"""Checks for S0.3 · Functions and graphs."""

import functools
import sys

import numpy as np

from .. import data, stats
from ..checking import Todo, Wrong, describe, exercise, progress

LESSON = "S0.3"


def _close(v, target, tol=1e-6):
    return bool(np.isclose(v, target, rtol=tol, atol=1e-9))


def journal_so_far():
    """Articles published up to the end of each year."""
    year = data.bibliothecae().articles["date"].str[:4].astype(int)
    return year.value_counts().sort_index().cumsum()


@functools.lru_cache(maxsize=1)
def zipf_counts():
    """Word counts of the Commedia, from the most to the least frequent word."""
    return stats.rank_frequency(stats.tokenize(data.commedia()))


def mystery_curves():
    """The three curves of Exercise 7: x, and a dict of y values for A, B and C."""
    x = np.arange(1, 21)
    return x, {"A": 200 * x ** -0.75, "B": 40 + 3 * x, "C": 5 * 1.4 ** x}


def _letters(answer, n, allowed, example, name="answer"):
    """The letters of a string answer, or Todo/Wrong if it is not usable."""
    if answer is ...:
        raise Todo(f'set {name} to {n} letters, for example "{example}"')
    if not isinstance(answer, str):
        raise Wrong(f'{name} should be a string of letters such as "{example}", not {describe(answer)}')
    letters = [ch for ch in answer.upper() if ch.isalpha()]
    if len(letters) != n:
        raise Wrong(f"write exactly {n} letters, one per item (you wrote {len(letters)})")
    wrong = sorted(set(letters) - set(allowed))
    if wrong:
        raise Wrong(f"use only the letters {', '.join(allowed)} (you wrote {', '.join(wrong)})")
    return letters


@exercise(LESSON, 1, "A function in Python")
def ex1(fb, colour, pages_for_20):
    out = {p: fb.call("colour", colour, p) for p in (0, 10, 100)}
    try:
        vals = {p: float(v) for p, v in out.items()}
    except (TypeError, ValueError):
        raise Wrong(f"colour should return a number, but colour(10) gives {describe(out[10])}") from None
    target = {p: 2 + 0.35 * p for p in out}
    if all(_close(vals[p], target[p]) for p in out):
        arr = fb.call("colour", colour, np.array([0, 10, 100]))
        if np.allclose(np.asarray(arr, dtype=float), [2, 5.5, 37]):
            fb.ok("colour gives 2 € for 0 pages, 5.50 € for 10 and 37 € for 100, also for an array of inputs")
        else:
            fb.no("colour works on single numbers but not on an array: avoid loops and use * and +")
    elif _close(vals[10], 2 * 0.35 * 10):
        fb.no("add the fee to the price of the pages; don't multiply by it")
    elif _close(vals[0], 0):
        fb.no("an order of 0 pages still pays the 2 € fee: colour(0) should be 2")
    elif _close(vals[10], 0.35 + 2 * 10):
        fb.no("the fee and the page price are swapped: 2 € once, plus 0.35 € a page")
    elif _close(vals[10], 2 + 35 * 10):
        fb.no("35 cents is 0.35 €")
    else:
        fb.no(f"colour(10) gives {vals[10]:g}, but 10 colour pages cost 2 + 0.35 × 10 = 5.50 €")
    fb.number("pages_for_20", pages_for_20, 51, fmt="{:g}", diagnose=lambda v:
              "part of a page cannot be printed: round down with np.floor" if _close(v, 18 / 0.35) else
              "take the 2 € fee away from the 20 € first" if _close(v, 20 / 0.35) or _close(v, 57) else
              "52 pages would cost 20.20 €: round down, not up" if _close(v, 52) else None)


@exercise(LESSON, 2, "A line through two points")
def ex2(fb, slope, intercept, y_10):
    fb.number("slope", slope, -2, fmt="{:g}", diagnose=lambda v:
              "subtract in the same order above and below: (-1 - 7) / (5 - 1)" if _close(v, 2) else
              "rise over run: the change in y goes on top" if _close(v, -0.5) else None)
    fb.number("intercept", intercept, 9, fmt="{:g}", diagnose=lambda v:
              "the intercept is y minus slope times x: 7 - (-2) × 1" if _close(v, 5) else None)
    fb.number("y_10", y_10, -11, fmt="{:g}", diagnose=lambda v:
              "the value at x = 10 is intercept + slope × 10" if _close(v, -20) or _close(v, -2 * 10 * 9) else None)


@exercise(LESSON, 3, "The journal's line")
def ex3(fb, per_year, start, in_2030):
    s = journal_so_far()
    b = (s[2024] - s[2013]) / 11
    a = s[2013] - b
    fb.number("per_year", per_year, b, fmt="{:.2f}", diagnose=lambda v:
              "2024 is 11 years after 2013, not 12" if _close(v, (s[2024] - s[2013]) / 12) else
              "subtract in the same order above and below" if _close(v, -b) else None)
    fb.number("start", start, a, fmt="{:.2f}", diagnose=lambda v:
              "measure x in years since 2012: 2013 is x = 1, not 2013" if _close(v, s[2013] - b * 2013) else
              f"the intercept is the line's value at x = 0, not the count of 2012 ({s[2012]})"
              if _close(v, s[2012]) else None)
    fb.number("in_2030", in_2030, a + b * 18, fmt="{:.1f}", diagnose=lambda v:
              "2030 is 18 years after 2012, so x = 18" if _close(v, a + b * 2030) or _close(v, a + b * 19) else
              "add the intercept: start + per_year × 18" if _close(v, b * 18) else None)
    if fb.status() == "pass":
        fb.info(f"The line adds {b:.1f} articles a year and predicts {a + b * 18:.0f} articles by the end "
                "of 2030, if the journal keeps its pace.")


@exercise(LESSON, 4, "Line, power or exponential?")
def ex4(fb, answer):
    letters = _letters(answer, 6, "LPE", "LLLLLL")
    truth = "LPEPEP"
    why = {
        0: "A, 4 + 0.5x: a fixed number plus a fixed number times x is a straight line",
        1: "B, 3x²: x is the base and 2 the exponent, so it is a power function",
        2: "C, 2 to the x divided by 5: x is in the exponent, so it is exponential (0.2 × 2 to the x)",
        3: "D, 1/x: this is x to the power −1, a power function",
        4: "E, 10 × 0.5 to the x: x is in the exponent, so it is exponential (decay, since 0.5 is below 1)",
        5: "F, the square root of x: this is x to the power 1/2, a power function",
    }
    if "".join(letters) == truth:
        fb.ok("LPEPEP: D and F are power functions in disguise, and E is exponential decay")
        return
    for i, (got, want) in enumerate(zip(letters, truth)):
        if got != want:
            fb.no(f"not {got} for {why[i]}")


@exercise(LESSON, 5, "Slope on log–log axes")
def ex5(fb, k, c, y_100):
    fb.number("k", k, -1, fmt="{:.4g}", diagnose=lambda v:
              "y falls as x grows, so the slope is negative: subtract in the same order" if _close(v, 1) else
              "take the logs first: on log–log axes the slope is between logs" if _close(v, (5 - 500) / (1000 - 10)) else None)
    fb.number("c", c, 5000, fmt="{:.4g}", diagnose=lambda v:
              "divide by x to the power k: c = 500 / 10 ** k" if _close(v, 50) else None)
    fb.number("y_100", y_100, 50, fmt="{:.4g}", diagnose=lambda v:
              "y = c × x to the power k, with x = 100: c * 100 ** k" if _close(v, 5000 * 100) else None)
    if fb.status() == "pass":
        fb.info("y = 5000 / x: a tenth as large for each step of 10 in x.")


@exercise(LESSON, 6, "Zipf's exponent")
def ex6(fb, ratio_f, ratio_r, s):
    f = zipf_counts()
    rf = f[9] / f[999]
    fb.number("ratio_f", ratio_f, rf, fmt="{:.4g}", diagnose=lambda v:
              "Python counts from 0: rank 10 is freq[9], and rank 1,000 is freq[999]"
              if _close(v, f[10] / f[1000]) else
              "divide the larger count (rank 10) by the smaller one (rank 1,000)" if _close(v, 1 / rf) else None)
    fb.number("ratio_r", ratio_r, 100, fmt="{:g}", diagnose=lambda v:
              "divide the larger rank by the smaller one: 1000 / 10" if _close(v, 0.01) else None)
    target = np.log(rf) / np.log(100)
    fb.number("s", s, target, abs_tol=1e-3, fmt="{:.3f}", diagnose=lambda v:
              "divide the logs, not the ratios themselves" if _close(v, rf / 100) else
              "s is positive: the slope is −s" if _close(v, -target) else None)
    if fb.status() == "pass":
        fb.info(f"s = {target:.2f}: between ranks 10 and 1,000 the Commedia follows Zipf's law closely.")


@exercise(LESSON, 7, "Three mystery curves")
def ex7(fb, families, k_power):
    letters = _letters(families, 3, "LEP", "LLL", name="families")
    where = {"L": "ordinary axes", "E": "semi-log axes", "P": "log–log axes"}
    truth = "PLE"
    for name, got, want in zip("ABC", letters, truth):
        if got == want:
            fb.ok(f"{name} is straight on {where[want]}")
        else:
            fb.no(f"{name} is not straight on {where[got]}: look again at its three plots")
    fb.number("k_power", k_power, -0.75, abs_tol=1e-3, fmt="{:.3f}", diagnose=lambda v:
              "the power curve falls, so its exponent is negative" if _close(v, 0.75) else None)


def summary():
    """Show which S0.3 exercises you have done in this session."""
    return progress(sys.modules[__name__])
