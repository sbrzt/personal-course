"""Checks for the S1.4 project · The shape of Bibliothecae.it.

Each check recomputes the answer with course.bibliothecae, on the corpus you
pass in (real or simulated). A ❌ here means "your number differs from mine";
if you chose a different rule on purpose, say so in your write-up.
"""

import sys

import numpy as np
import pandas as pd

from .. import bibliothecae as bib
from .. import stats
from ..checking import describe, exercise, progress, quiet

LESSON = "S1.4"


def _series_like(name, value, ref, fb):
    """Compare a Series of counts with the reference, ignoring order."""
    if value is ...:
        fb.todo(f"{name}: replace the ... with your answer")
        return False
    if not isinstance(value, pd.Series):
        fb.no(f"{name} should be a pandas Series, but it is {describe(value)}")
        return False
    a = np.sort(np.asarray(value, dtype=float))
    b = np.sort(np.asarray(ref, dtype=float))
    if a.shape == b.shape and np.allclose(a, b):
        fb.ok(f"{name}: {len(value):,} values, as expected")
        return True
    fb.no(f"{name} has {len(value):,} values summing to {a.sum():,.0f}; I get {len(ref):,} values "
          f"summing to {b.sum():,.0f}. Check the rules at the top of the notebook")
    return False


@exercise(LESSON, 1, "References per article")
def ex1(fb, corpus, refs_per_article, median_refs):
    ref = bib.refs_per_article(corpus)
    _series_like("refs_per_article", refs_per_article, ref, fb)
    fb.number("median_refs", median_refs, ref.median(), fmt="{:g}")


@exercise(LESSON, 2, "How old are the cited works?")
def ex2(fb, corpus, ages, median_age, price_idx):
    ref = bib.citation_ages(corpus)
    _series_like("ages", ages, ref, fb)
    fb.number("median_age", median_age, ref.median(), fmt="{:g}")
    fb.number("price_idx", price_idx, stats.price_index(ref), fmt="{:.3f}", diagnose=lambda v:
              "use age <= 5 (at most five years old)" if np.isclose(v, np.mean(ref < 5)) else None)


@exercise(LESSON, 3, "Who gets cited?")
def ex3(fb, corpus, author_counts, gini_authors, top1_share_authors):
    ref = bib.cited_author_counts(corpus)
    _series_like("author_counts", author_counts, ref, fb)
    fb.number("gini_authors", gini_authors, stats.gini(ref), fmt="{:.3f}")
    fb.number("top1_share_authors", top1_share_authors, stats.top_share(ref, 0.01), fmt="{:.3f}")


@exercise(LESSON, 4, "Power law or lognormal, on your data")
def ex4(fb, corpus, alpha, xmin, R, p):
    import powerlaw

    x = bib.cited_author_counts(corpus).to_numpy()
    with quiet():
        fit = powerlaw.Fit(x, discrete=True, verbose=False)
        R0, p0 = fit.distribution_compare("power_law", "lognormal", normalized_ratio=True)
    fb.number("alpha", alpha, fit.power_law.alpha, rel_tol=1e-3, fmt="{:.3f}")
    fb.number("xmin", xmin, fit.power_law.xmin, fmt="{:g}")
    fb.number("R", R, R0, abs_tol=0.01, fmt="{:.3f}")
    fb.number("p", p, p0, abs_tol=0.01, fmt="{:.3f}")
    xm = fit.power_law.xmin
    n_tail = int((x >= xm).sum())
    if fb.status() == "pass" and n_tail == x.size:
        fb.info(f"xmin = {xm:g}, so the fit covers all {x.size:,} cited authors. With R = {R0:.2f} "
                f"and p = {p0:.2f}, {'the data cannot tell the two models apart' if p0 > 0.1 else 'one model fits better'}.")
    elif fb.status() == "pass":
        fb.info(f"The fitted tail starts at {xm:g} citations and holds {n_tail:,} of {x.size:,} authors "
                f"({n_tail / x.size:.1%}): read alpha as a statement about them only.")


@exercise(LESSON, 5, "Lotka's law for the journal's authors")
def ex5(fb, corpus, table, share_single):
    ref = bib.article_author_productivity(corpus)
    if table is ...:
        fb.todo("table: replace the ... with your answer")
    elif isinstance(table, pd.Series) and np.array_equal(table.sort_index().to_numpy(), ref.to_numpy()) \
            and table.sort_index().index.tolist() == ref.index.tolist():
        fb.ok(f"table matches: {int(ref.loc[1])} authors wrote one article")
    else:
        fb.no("table differs: keep only links to the corpus's articles, then count authors per number of articles")
    fb.number("share_single", share_single, ref.loc[1] / ref.sum(), fmt="{:.3f}")
    if fb.status() == "pass":
        fb.info(f"{ref.loc[1] / ref.sum():.0%} single-article authors, against 61% under Lotka's law "
                f"with exponent 2. The most productive author wrote {int(ref.index.max())} articles.")


@exercise(LESSON, 6, "Bradford's zones for the cited venues")
def ex6(fb, corpus, venues, zones):
    ref = bib.venue_counts(corpus)
    _series_like("venues", venues, ref, fb)
    rz = stats.bradford_zones(ref, 3)
    if zones is ...:
        fb.todo("zones: replace the ... with your answer")
    elif np.array_equal(np.asarray(zones), rz):
        fb.ok(f"zones = {rz.tolist()}")
    else:
        fb.no(f"zones should come from stats.bradford_zones(venues, 3); yours are {np.asarray(zones).tolist()}")


def summary():
    """Show which S1.4 steps you have done in this session."""
    return progress(sys.modules[__name__])
