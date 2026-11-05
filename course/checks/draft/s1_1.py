"""Checks for S1.1 · Centre, spread and shape."""

import sys

import numpy as np

from ... import data, stats
from ...checking import Wrong, describe, exercise, progress

LESSON = "S1.1"


def _close(v, target):
    return bool(np.isclose(v, target, rtol=1e-6, atol=1e-9))


@exercise(LESSON, 1, "Mean versus median")
def ex1(fb, mean_refs, median_refs, share_above_mean):
    x = data.reference_counts()
    mean, median = x.mean(), np.median(x)
    share = np.mean(x > mean)
    fb.number("mean_refs", mean_refs, mean, diagnose=lambda v:
              "that is the median; the mean is the sum divided by the count" if _close(v, median) else
              "that is the total; divide it by the number of articles" if _close(v, x.sum()) else None)
    fb.number("median_refs", median_refs, median, diagnose=lambda v:
              "that is the mean; the median is the middle value of the sorted data" if _close(v, mean) else
              "that is the middle of the unsorted array; use np.median, which sorts for you"
              if _close(v, x[len(x) // 2]) else None)
    fb.number("share_above_mean", share_above_mean, share, diagnose=lambda v:
              "give a share between 0 and 1, not a percentage" if _close(v, 100 * share) else
              "that is a count; divide it by the number of articles" if _close(v, (x > mean).sum()) else
              "that is the share at or below the mean; flip the comparison" if _close(v, 1 - share) else None)
    if fb.status() == "pass":
        fb.info(f"Only {share:.0%} of the articles have more references than the 'average' article. "
                "In right-skewed data the mean sits above the typical value.")


@exercise(LESSON, 2, "One bad record")
def ex2(fb, mean_shift, median_shift):
    x = data.reference_counts()
    bad = np.append(x, 2000)
    d_mean, d_median = bad.mean() - x.mean(), np.median(bad) - np.median(x)
    fb.number("mean_shift", mean_shift, d_mean, diagnose=lambda v:
              "the sign is flipped: compute new minus old" if _close(v, -d_mean) else
              "that is the new mean itself; subtract the old mean" if _close(v, bad.mean()) else None)
    fb.number("median_shift", median_shift, d_median, abs_tol=1e-9, diagnose=lambda v:
              "that is the new median itself; subtract the old median" if _close(v, np.median(bad)) else None)
    if fb.status() == "pass":
        fb.info(f"One record out of {bad.size} moved the mean by {d_mean:.1f} references "
                f"({d_mean / x.mean():.0%}) and the median by {d_median:g}.")


@exercise(LESSON, 3, "Percentiles and the IQR")
def ex3(fb, p90, iqr):
    x = data.reference_counts()
    p10, p25, p75, q90 = np.percentile(x, [10, 25, 75, 90])
    fb.number("p90", p90, q90, abs_tol=1.0, diagnose=lambda v:
              "np.percentile takes a number from 0 to 100 (np.quantile takes one from 0 to 1)"
              if _close(v, np.percentile(x, 0.9)) else
              "that is the 10th percentile" if _close(v, p10) else None)
    fb.number("iqr", iqr, p75 - p25, abs_tol=1.0, diagnose=lambda v:
              "that is the 75th percentile alone; subtract the 25th" if _close(v, p75) else
              "that is the range (maximum minus minimum)" if _close(v, x.max() - x.min()) else
              "that is the standard deviation" if _close(v, x.std()) or _close(v, x.std(ddof=1)) else None)
    if fb.status() == "pass":
        fb.info(f"A compact report: median {np.median(x):g} references (IQR {p25:g}–{p75:g}), "
                f"90th percentile {q90:g}, maximum {x.max()}.")


@exercise(LESSON, 4, "Your own CCDF")
def ex4(fb, my_ccdf):
    out = fb.call("my_ccdf", my_ccdf, np.array([1, 1, 2, 5]))
    try:
        values, shares = (np.asarray(part, dtype=float) for part in out)
    except (TypeError, ValueError):
        raise Wrong(f"my_ccdf should return two arrays, (values, shares), but returned {describe(out)}")
    if values.shape != shares.shape:
        raise Wrong("values and shares should have the same length")
    if values.size == 4:
        fb.no("for [1, 1, 2, 5] return each distinct value once, [1, 2, 5]: np.unique helps")
    elif not np.allclose(values, [1, 2, 5]):
        fb.no(f"for [1, 1, 2, 5] the values should be [1, 2, 5]; yours are {values}")
    elif np.allclose(shares, [0.5, 0.25, 0]):
        fb.no("you computed P(X > x). Here we want P(X ≥ x), so the first share must be 1")
    elif np.allclose(shares, [0.5, 0.75, 1]):
        fb.no("that is the CDF, P(X ≤ x). The CCDF counts the observations at or above x")
    elif np.allclose(shares, [1, 0.5, 0.25]):
        fb.ok("my_ccdf([1, 1, 2, 5]) returns values [1, 2, 5] with shares [1, 0.5, 0.25]")
    else:
        fb.no(f"for [1, 1, 2, 5] the shares should be [1, 0.5, 0.25]; yours are {shares}")
    if fb.status() != "pass":
        return
    x = data.citation_counts()
    v2, s2 = (np.asarray(p, dtype=float) for p in fb.call("my_ccdf", my_ccdf, x))
    rv, rs = stats.ccdf(x)
    if v2.shape == rv.shape and np.allclose(v2, rv) and np.allclose(s2, rs):
        fb.ok("it also matches the reference CCDF of the 5,000 citation counts")
    else:
        fb.no("it works on the small example but not on the citation counts: check how you handle repeated values")


@exercise(LESSON, 5, "Reading the tail")
def ex5(fb, share_uncited, share_10_plus, share_100_plus):
    x = data.citation_counts()
    for name, answer, mask, strict in [
        ("share_uncited", share_uncited, x == 0, None),
        ("share_10_plus", share_10_plus, x >= 10, x > 10),
        ("share_100_plus", share_100_plus, x >= 100, x > 100),
    ]:
        target = mask.mean()
        fb.number(name, answer, target, diagnose=lambda v, t=target, m=mask, s=strict:
                  "give a share between 0 and 1, not a percentage" if _close(v, 100 * t) else
                  "that is a count; divide it by the number of papers" if _close(v, m.sum()) else
                  "use ≥ (at least), not >" if s is not None and _close(v, s.mean()) else None)
    if fb.status() == "pass":
        top = np.sort(x)[::-1]
        k = int((x >= 100).sum())
        fb.info(f"{np.mean(x == 0):.0%} of the papers are never cited, while the {k} papers with 100 or more "
                f"citations ({k / x.size:.1%} of all papers) hold {top[:k].sum() / x.sum():.0%} of all citations.")


def summary():
    """Show which S1.1 exercises you have done in this session."""
    return progress(sys.modules[__name__])
