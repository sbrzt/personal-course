"""Reference versions of the statistics taught in Phase S.

Some lessons ask you to write one of these functions yourself. After that
exercise, the lesson switches to the version in this module, so later cells
work even if your own attempt is unfinished. Try the exercise before reading
this file: it contains the answers.
"""

from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np
import pandas as pd

__all__ = [
    "summary", "ecdf", "ccdf", "lorenz", "gini", "top_share",
    "sample_power_law", "alpha_mle", "alpha_se",
    "productivity", "lotka_share_single", "bradford_zones",
    "WORD", "tokenize", "rank_frequency", "year_of", "price_index",
]


def _values(x) -> np.ndarray:
    """Return x as a flat float array without missing values."""
    a = np.asarray(x, dtype=float).ravel()
    return a[~np.isnan(a)]


# Centre, spread and shape ---------------------------------------------------

def summary(x) -> pd.Series:
    """Count, mean, standard deviation, percentiles and IQR of x."""
    a = _values(x)
    p10, p25, p50, p75, p90, p99 = np.percentile(a, [10, 25, 50, 75, 90, 99])
    return pd.Series({
        "n": a.size, "mean": a.mean(), "sd": a.std(ddof=1), "min": a.min(),
        "p10": p10, "p25": p25, "median": p50, "p75": p75, "p90": p90,
        "p99": p99, "max": a.max(), "iqr": p75 - p25,
    })


def ecdf(x):
    """Sorted values and the share of observations <= each value."""
    a = np.sort(_values(x))
    return a, np.arange(1, a.size + 1) / a.size


def ccdf(x):
    """Distinct values v and the share of observations >= v.

    This is the complementary cumulative distribution function, P(X >= v).
    Its first value is always 1, because every observation is >= the minimum.
    """
    a = np.sort(_values(x))
    values, first = np.unique(a, return_index=True)
    return values, 1.0 - first / a.size


# Concentration ----------------------------------------------------------------

def lorenz(x):
    """Points of the Lorenz curve: cumulative share of units, cumulative share of the total."""
    a = np.sort(_values(x))
    total = np.concatenate([[0.0], np.cumsum(a)])
    return np.linspace(0.0, 1.0, a.size + 1), total / total[-1]


def gini(x) -> float:
    """Gini coefficient of non-negative values.

    0 means everyone holds the same amount; (n - 1) / n means one unit holds
    everything. Uses the sorted-values formula
    G = 2 * sum(i * x_(i)) / (n * sum(x)) - (n + 1) / n, with i = 1..n.
    """
    a = np.sort(_values(x))
    n = a.size
    if n == 0 or a.sum() == 0:
        return 0.0
    i = np.arange(1, n + 1)
    return float(2.0 * np.sum(i * a) / (n * a.sum()) - (n + 1) / n)


def top_share(x, q: float = 0.1) -> float:
    """Share of the total held by the top q fraction of units (at least one unit)."""
    a = np.sort(_values(x))[::-1]
    k = max(1, math.ceil(q * a.size))
    return float(a[:k].sum() / a.sum())


# Power laws ---------------------------------------------------------------------

def sample_power_law(n: int, alpha: float, xmin: float = 1.0, rng=None) -> np.ndarray:
    """Draw n values from a continuous power law p(x) ~ x**-alpha, x >= xmin.

    Inverse-transform sampling: if U ~ Uniform(0, 1), then
    X = xmin * (1 - U) ** (-1 / (alpha - 1)) has the power-law distribution.
    """
    rng = np.random.default_rng(rng)
    u = rng.random(n)
    return xmin * (1.0 - u) ** (-1.0 / (alpha - 1.0))


def alpha_mle(x, xmin: float) -> float:
    """Maximum-likelihood exponent of a continuous power law fitted to x >= xmin.

    alpha_hat = 1 + n / sum(ln(x_i / xmin))   (Clauset, Shalizi and Newman 2009, eq. 3.1)
    """
    a = _values(x)
    a = a[a >= xmin]
    return float(1.0 + a.size / np.sum(np.log(a / xmin)))


def alpha_se(alpha: float, n: int) -> float:
    """Standard error of the maximum-likelihood exponent: (alpha - 1) / sqrt(n)."""
    return (alpha - 1.0) / math.sqrt(n)


# The bibliometric laws ------------------------------------------------------------

def productivity(authorship: pd.DataFrame, author: str = "author", work: str = "article") -> pd.Series:
    """Lotka's table: how many authors wrote k works, for each k.

    authorship has one row per (work, author) pair; duplicates are ignored.
    """
    per_author = authorship.drop_duplicates([work, author]).groupby(author).size()
    table = per_author.value_counts().sort_index()
    table.index.name = "works"
    return table.rename("authors")


def lotka_share_single(n: float) -> float:
    """Share of one-work authors predicted by Lotka's law with exponent n: 1 / zeta(n)."""
    k = np.arange(1, 200_001, dtype=float)
    tail = 200_000.0 ** (1 - n) / (n - 1)          # integral approximation of the rest
    return float(1.0 / (np.sum(k ** -n) + tail))


def bradford_zones(counts, n_zones: int = 3) -> np.ndarray:
    """Number of journals in each Bradford zone.

    Journals are ranked by their number of articles (largest first). Each
    journal goes to the zone where its block of articles starts: zone
    floor(n_zones * articles_before_it / total), so every zone holds about
    the same number of articles.
    """
    c = np.sort(np.asarray(counts, dtype=float))[::-1]
    before = np.cumsum(c) - c
    zone = np.floor(n_zones * before / c.sum()).astype(int)
    return np.bincount(np.minimum(zone, n_zones - 1), minlength=n_zones)


# Words ------------------------------------------------------------------------------

WORD = re.compile(r"[^\W\d_]+")
"""A word is a run of letters (accented letters included); apostrophes split words."""


def tokenize(text: str) -> list[str]:
    """Lower-case the text and return its words."""
    return WORD.findall(text.lower())


def rank_frequency(tokens) -> np.ndarray:
    """Word frequencies sorted from most to least frequent."""
    return np.array(sorted(Counter(tokens).values(), reverse=True))


# Dates and citation age ---------------------------------------------------------------

def year_of(values) -> pd.Series:
    """First four-digit number in each value, as a float year (NaN when there is none)."""
    s = pd.Series(values, dtype="string")
    return pd.to_numeric(s.str.extract(r"(\d{4})", expand=False), errors="coerce").astype(float)


def price_index(ages, window: int = 5) -> float:
    """Share of references at most `window` years older than the citing work (Price 1970)."""
    a = _values(ages)
    return float(np.mean(a <= window))
