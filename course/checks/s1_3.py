"""Checks for S1.3 · Distributions and their shape."""

import sys

import numpy as np
import pandas as pd

from .. import bibliothecae, data, stats
from ..checking import Todo, Wrong, describe, exercise, progress

LESSON = "S1.3"
WAITS = np.array([2, 5, 8, 10, 12, 15, 20, 26, 60])     # the nine waits of section 6
UNEVEN = np.array([0, 10, 20, 30, 50, 100, 250])        # the uneven bins of section 3
SHAPES = ["symmetric", "right-skewed", "left-skewed", "two peaks"]
SYNONYMS = {
    "symmetric": "symmetric", "symmetrical": "symmetric", "bell shaped": "symmetric",
    "right skewed": "right-skewed", "skewed right": "right-skewed",
    "skewed to the right": "right-skewed", "right skew": "right-skewed",
    "positively skewed": "right-skewed", "positive skew": "right-skewed",
    "left skewed": "left-skewed", "skewed left": "left-skewed",
    "skewed to the left": "left-skewed", "left skew": "left-skewed",
    "negatively skewed": "left-skewed", "negative skew": "left-skewed",
    "two peaks": "two peaks", "2 peaks": "two peaks", "bimodal": "two peaks",
    "two humps": "two peaks", "two modes": "two peaks",
}


def _close(v, target, tol=1e-6):
    try:
        return bool(np.isclose(float(v), float(target), rtol=tol, atol=1e-9))
    except (TypeError, ValueError):
        return False


def refs() -> pd.Series:
    """References per article, for the 201 articles that have at least one."""
    return bibliothecae.refs_per_article(data.bibliothecae())


def page_counts() -> pd.Series:
    first_last = data.bibliothecae().articles["pages"].str.split("-", expand=True).astype(int)
    return first_last[1] - first_last[0] + 1


def refs_since_2016() -> pd.Series:
    """References of every article published since 2016, 0 where none were recorded."""
    info = data.bibliothecae().articles.set_index("id")
    year = info["date"].str[:4].astype(int)
    return refs().reindex(year[year >= 2016].index, fill_value=0)


def _array(fb, name, value, target, wrong=(), pair_hint=None) -> bool:
    """Check an array answer; `wrong` lists (array, hint) pairs for likely mistakes."""
    if value is ...:
        fb.todo(f"{name}: replace the ... with your answer")
        return False
    if isinstance(value, tuple) and pair_hint:
        fb.no(f"{name} is a pair of things: {pair_hint}")
        return False
    try:
        a = np.asarray(value, dtype=float).ravel()
    except (TypeError, ValueError):
        fb.no(f"{name} should be an array of numbers, but it is {describe(value)}")
        return False
    target = np.asarray(target, dtype=float)
    if a.shape == target.shape and np.allclose(a, target):
        fb.ok(f"{name} is right")
        return True
    for other, hint in wrong:
        other = np.asarray(other, dtype=float)
        if a.shape == other.shape and np.allclose(a, other):
            fb.no(f"{name} is not right yet: {hint}")
            return False
    if a.shape != target.shape:
        fb.no(f"{name} should hold {target.size} numbers, but it holds {a.size}")
    else:
        fb.no(f"{name} is not right yet: compare a few of its values with the histogram above")
    return False


@exercise(LESSON, 1, "Counting in bins")
def ex1(fb, edges, counts, n_under_20, fullest_start):
    r = refs()
    e = np.arange(0, 250, 10)
    c = np.histogram(r, bins=e)[0]
    short = np.arange(0, 240, 10)
    _array(fb, "edges", edges, e, wrong=[
        (short, "np.arange stops before its second argument, so this ends at 230: "
                "use np.arange(0, 250, 10) to reach 240"),
        (np.arange(10, 250, 10), "start at 0"),
    ])
    _array(fb, "counts", counts, c, pair_hint="np.histogram returns the counts and the edges; "
           "keep the counts with [0]", wrong=[
        (np.histogram(r, bins=short)[0], "these bins end at 230, so the article with 234 "
                                         "references is missing: the last edge must be 240"),
        (np.histogram(r, bins=24)[0], "bins=24 spreads 24 bins from the smallest value to the "
                                      "largest; pass your edges instead: bins=edges"),
        (np.histogram(r, bins=e, density=True)[0], "these are densities; counts are whole "
                                                   "numbers, without density=True"),
    ])
    fb.number("n_under_20", n_under_20, c[:2].sum(), fmt="{:g}", diagnose=lambda v:
              "fewer than 20 leaves out the articles with exactly 20" if _close(v, (r <= 20).sum()) else
              "that is only the first bin, 0–9: add the bin 10–19" if _close(v, c[0]) else
              "that includes the bin 20–29; fewer than 20 means the first two bins"
              if _close(v, c[:3].sum()) else
              "that is a share; give the number of articles" if _close(v, (r < 20).mean()) else None)
    fb.number("fullest_start", fullest_start, e[c.argmax()], fmt="{:g}", diagnose=lambda v:
              "that is how many articles the bin holds; give its left edge" if _close(v, c.max()) else
              "that is the position of the bin; give its left edge: edges[counts.argmax()]"
              if _close(v, c.argmax()) else
              "that is the right edge of the bin; give the left one" if _close(v, e[c.argmax() + 1]) else None)
    if fb.status() == "pass":
        fb.info(f"The fullest bin, {e[c.argmax()]}–{e[c.argmax()] + 9}, holds {c.max()} articles, "
                f"and the bin 10–19 holds {c[1]}: a near tie.")


@exercise(LESSON, 2, "Sturges' rule")
def ex2(fb, k_refs, width_refs, k_pages):
    r, p = refs(), page_counts()
    n, m = len(r), len(p)
    k, kp = int(np.ceil(1 + np.log2(n))), int(np.ceil(1 + np.log2(m)))
    w = (r.max() - r.min()) / k

    def bins_hint(v, size):
        raw = 1 + np.log2(size)
        if _close(v, raw):
            return "round up to a whole number of bins: np.ceil"
        if _close(v, np.floor(raw)):
            return f"for {size} values, 1 + log2({size}) = {raw:.2f}, which rounds up, not down"
        if _close(v, np.ceil(1 + np.log(size))) or _close(v, np.ceil(1 + np.log10(size))):
            return "use the log in base 2: np.log2"
        if _close(v, np.log2(size)) or _close(v, np.ceil(np.log2(size))):
            return "add 1 to the log before rounding up"
        return None

    fb.number("k_refs", k_refs, k, fmt="{:g}", diagnose=lambda v:
              bins_hint(v, n) or ("n is the number of articles in refs, 201, not all 321 articles"
                                  if _close(v, kp) else None))
    fb.number("width_refs", width_refs, w, abs_tol=1e-3, fmt="{:.3f}", diagnose=lambda v:
              "the bins span the range, from the smallest value to the largest: "
              "refs.max() - refs.min()" if _close(v, r.max() / k) else
              "divide by the rounded number of bins, k_refs" if _close(v, (r.max() - r.min()) / (1 + np.log2(n)))
              else None)
    fb.number("k_pages", k_pages, kp, fmt="{:g}", diagnose=lambda v: bins_hint(v, m))
    if fb.status() == "pass":
        first = np.histogram(r, bins="sturges")[0][0]
        fb.info(f"Sturges' rule gives {k} bins {w:.1f} references wide; the first holds {first} of "
                f"the {n} articles.")


@exercise(LESSON, 3, "Densities by hand")
def ex3(fb, bin_counts, widths, density, tallest_start):
    r = refs()
    c = np.histogram(r, bins=UNEVEN)[0]
    w = np.diff(UNEVEN)
    d = c / (len(r) * w)
    _array(fb, "bin_counts", bin_counts, c, pair_hint="np.histogram returns the counts and the edges; "
           "keep the counts with [0]", wrong=[
        (np.histogram(r, bins=UNEVEN, density=True)[0], "these are densities; first count the articles"),
    ])
    _array(fb, "widths", widths, w, wrong=[
        (-w, "subtract each edge from the next one, not the other way round"),
    ])
    _array(fb, "density", density, d, wrong=[
        (c / len(r), "these are shares; divide them by the widths too"),
        (c / w, "these are articles per unit of width; divide by n, the number of articles, too"),
        (100 * d, "these are percentages; a density is a share per unit, so leave out the 100"),
    ])
    fb.number("tallest_start", tallest_start, UNEVEN[d.argmax()], fmt="{:g}", diagnose=lambda v:
              "that bin has the largest count; the question asks for the highest density"
              if _close(v, UNEVEN[c.argmax()]) else
              "that is the position of the bin; give its left edge" if _close(v, d.argmax()) else
              "that is the highest density itself; give the left edge of its bin" if _close(v, d.max()) else
              "that is the right edge of the bin; give the left one" if _close(v, UNEVEN[d.argmax() + 1])
              else None)
    if fb.status() == "pass":
        fb.info(f"The areas add up to {(d * w).sum():g}. The bin 30–49 has the most articles ({c[3]}), "
                f"but the bin 10–19 is the most crowded: {d[1]:.4f} per reference against {d[3]:.4f}.")


def _shape(value):
    """The answer as one of SHAPES, or None if it is not one of them."""
    words = " ".join(value.lower().replace("-", " ").replace("_", " ").split())
    return SYNONYMS.get(words)


@exercise(LESSON, 4, "Name the shape")
def ex4(fb, shape_a, shape_b, shape_c):
    # Simple rules on the data give the expected shapes: the side of the long tail (the mean lies
    # on the side of the tail, away from the median) for A and B, and the spike at zero for C.
    bib = data.bibliothecae()
    r, ref_len, cited = refs_since_2016(), bib.references["content"].str.len(), bibliothecae.cited_years(bib)
    answers = {
        "shape_a": (shape_a, "right-skewed" if ref_len.mean() > ref_len.median() else "left-skewed", {
            "left-skewed": "A's long tail is on the right, towards the longest references: "
                           "a skew is named after the side of its tail",
            "symmetric": "is one side of A's peak much longer than the other?",
            "two peaks": "A has a single hump; after it the bars shrink steadily, far to the right",
        }),
        "shape_b": (shape_b, "left-skewed" if cited.mean() < cited.median() else "right-skewed", {
            "right-skewed": "B's long tail stretches to the left, back to the oldest works: "
                            "a skew is named after the side of its tail",
            "symmetric": "is one side of B's peak much longer than the other?",
            "two peaks": "B has a single peak, in recent years; the low bars on the left are its tail",
        }),
        "shape_c": (shape_c, "two peaks" if (r == 0).mean() > 0.1 else "right-skewed", {
            "right-skewed": "C has a tail on the right too, but look at the bar at zero: it stands "
                            "apart from the hump around 30",
            "symmetric": "look at the bar at zero, and at the hump around 30",
            "left-skewed": "look at the bar at zero, and at the hump around 30",
        }),
    }
    for name, (value, target, hints) in answers.items():
        if value is ...:
            fb.todo(f"{name}: replace the ... with your answer")
        elif not isinstance(value, str):
            fb.no(f'{name} should be a string such as "symmetric", not {describe(value)}')
        elif _shape(value) is None:
            fb.no(f"{name}: write one of " + ", ".join(f'"{s}"' for s in SHAPES))
        elif _shape(value) == target:
            fb.ok(f'{name} = "{target}"')
        else:
            fb.no(f'{name} = "{_shape(value)}" is not right yet: {hints[_shape(value)]}')
    if fb.status() == "pass":
        fb.info(f"C's spike holds the {(r == 0).sum()} articles since 2016 without any recorded "
                "reference: the next cell asks who they are.")


@exercise(LESSON, 5, "The fences")
def ex5(fb, q1, q3, upper, n_above):
    r = refs()
    a, b = r.quantile([0.25, 0.75])
    u = b + 1.5 * (b - a)
    fb.number("q1", q1, a, fmt="{:g}", diagnose=lambda v:
              "that is the third quartile; Q1 is a quarter of the way along: quantile(0.25)"
              if _close(v, b) else "that is the median, quantile(0.5)" if _close(v, r.median()) else None)
    fb.number("q3", q3, b, fmt="{:g}", diagnose=lambda v:
              "that is the first quartile; Q3 is three quarters of the way along: quantile(0.75)"
              if _close(v, a) else "that is the median, quantile(0.5)" if _close(v, r.median()) else None)
    fb.number("upper", upper, u, fmt="{:g}", diagnose=lambda v:
              "the fence is Q3 plus 1.5 times the IQR, not 1.5 times Q3" if _close(v, 1.5 * b) else
              "that adds one IQR; the step is 1.5 times the IQR" if _close(v, b + (b - a)) else
              "that is only the step, 1.5 × IQR: add it to Q3" if _close(v, 1.5 * (b - a)) else
              "that is the lower fence; the upper one adds the step to Q3" if _close(v, a - 1.5 * (b - a))
              else None)

    def above_hint(v):
        if _close(v, (r >= u).sum()):
            return "a value exactly on the fence is not beyond it: use > rather than >="
        if _close(v, (r > u).mean()):
            return "that is a share; give the number of articles"
        try:
            mine = float(upper)
        except (TypeError, ValueError):
            return None
        if not _close(mine, u) and _close(v, (r > mine).sum()):
            return "that is right for your value of upper: fix upper first"
        return None

    fb.number("n_above", n_above, (r > u).sum(), fmt="{:g}", diagnose=above_hint)
    if fb.status() == "pass":
        fb.info(f"The fences are {a - 1.5 * (b - a):g} and {u:g}: {(r > u).sum()} articles are beyond the "
                f"upper one, and {(r == u).sum()} sits exactly on it.")


@exercise(LESSON, 6, "An ECDF of your own")
def ex6(fb, ecdf_at, share_30, p90):
    r = refs()
    try:
        cases = [(WAITS, 10, 4 / 9), (WAITS, 1, 0.0), (WAITS, 60, 1.0), (WAITS, 25, 7 / 9),
                 (np.array([1, 1, 2]), 1, 2 / 3), (r, 30, (r <= 30).mean())]
        got = []
        for x, t, _ in cases:
            out = fb.call("ecdf_at", ecdf_at, x.copy(), t)
            try:
                got.append(float(out))
            except (TypeError, ValueError):
                raise Wrong(f"ecdf_at should return one number, a share, but it returns "
                            f"{describe(out)}") from None
        at_10 = got[0]
        if all(_close(g, want) for g, (_, _, want) in zip(got, cases)):
            fb.ok("ecdf_at is right: for the nine waits it gives 0.444 at 10, 0 below the smallest "
                  "value and 1 at the largest; it also works on refs")
        elif _close(at_10, 3 / 9):
            fb.no("ecdf_at is not right yet: at most t includes t itself, so use <= rather than <")
        elif _close(at_10, 4):
            fb.no("ecdf_at is not right yet: it counts; divide by the number of values, or take the mean")
        elif _close(at_10, 5 / 9) or _close(at_10, 6 / 9):
            fb.no("ecdf_at is not right yet: the ECDF counts the values at most t, not those above it")
        elif all(_close(g, want) for g, (_, _, want) in zip(got[:5], cases[:5])):
            fb.no("ecdf_at works on arrays but not on a pandas Series: np.asarray(x) turns both into arrays")
        else:
            fb.no(f"ecdf_at is not right yet: for the nine waits it gives {at_10:g} at t = 10, but 4 of "
                  "the 9 waits are at most 10, a share of 0.444")
    except Todo as e:
        fb.todo(str(e))
    except Wrong as e:
        fb.no(str(e))
    s = (r <= 30).mean()
    values, shares = stats.ecdf(r)
    p = values[shares >= 0.9][0]
    fb.number("share_30", share_30, s, abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "that is a count; divide by the number of articles, or take the mean" if _close(v, (r <= 30).sum())
              else "at most 30 includes 30 itself: use <=" if _close(v, (r < 30).mean()) else
              "that is a percentage; give a share between 0 and 1" if _close(v, 100 * s) else None)
    fb.number("p90", p90, p, fmt="{:g}", diagnose=lambda v:
              "that is the share; p90 is a number of references" if _close(v, 0.9) else
              "that is how many articles; p90 is a number of references" if _close(v, (r <= p).sum()) else
              "that is the largest value; take the first value at which the ECDF reaches 0.9"
              if _close(v, r.max()) else None)
    if fb.status() == "pass":
        fb.info(f"Half of the articles have at most 30 references ({s:.1%}), and 90% at most {p:g}.")


def summary():
    """Show which S1.3 exercises you have done in this session."""
    return progress(sys.modules[__name__])
