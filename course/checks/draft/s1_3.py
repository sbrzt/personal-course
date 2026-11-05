"""Checks for S1.3 · Heavy tails and the laws of bibliometrics."""

import sys

import numpy as np
import pandas as pd

from ... import data, models, stats
from ...checking import Wrong, describe, exercise, progress, quiet

LESSON = "S1.3"


def _close(v, target, tol=1e-6):
    return bool(np.isclose(v, target, rtol=tol, atol=1e-9))


def _spearman(a, b):
    return float(pd.Series(a).corr(pd.Series(b), method="spearman"))


@exercise(LESSON, 1, "Simulating cumulative advantage")
def ex1(fb, price_model):
    try:
        out = fb.call("price_model", price_model, n_papers=2000, m=3, a=1.0, seed=1)
    except Wrong as e:
        if "NaN" in str(e) or "probabilit" in str(e):
            raise Wrong(f"{e}. Hint: papers with no citations yet get weight 0, and at the start every "
                        "weight is 0. That is why Price adds a to every count.") from None
        raise
    c = np.asarray(out)
    if c.shape != (2000,):
        raise Wrong(f"price_model(n_papers=2000, ...) should return 2000 counts, but returned {describe(out)}")
    if not np.all(c >= 0) or not np.allclose(c, np.round(c)):
        raise Wrong("citation counts should be non-negative whole numbers")
    total = 3 * (2000 - 3)
    if c.sum() == total:
        fb.ok(f"every paper from the 4th on cites 3 earlier papers: {total:,} citations in all")
    else:
        fb.no(f"there should be 3 x 1997 = {total:,} citations in all, but your counts add up to {int(c.sum()):,}")
    g = stats.gini(c)
    g_uniform = stats.gini(models.uniform_attachment(2000, 3, seed=1))
    if g > 0.7:
        fb.ok(f"citations are concentrated (Gini {g:.2f}, against {g_uniform:.2f} when every paper is equally likely)")
    else:
        fb.no(f"Gini is only {g:.2f}, close to random citing ({g_uniform:.2f}): the weight of a paper should "
              "grow with the citations it already has")
    rho = _spearman(np.arange(2000), c)
    if rho < -0.5:
        fb.ok(f"older papers collect more citations (Spearman rho between age rank and citations: {rho:.2f})")
    else:
        fb.no(f"older papers should be cited more (rho between paper index and citations is {rho:.2f})")


@exercise(LESSON, 2, "Luck versus advantage")
def ex2(fb, gini_by_a):
    keys = [0.1, 1, 10, 1000]
    if gini_by_a is ...:
        fb.todo("gini_by_a: replace the ... with your dictionary")
        return
    if not isinstance(gini_by_a, dict) or not all(k in gini_by_a for k in keys):
        raise Wrong(f"gini_by_a should be a dict with keys {keys}, but it is {describe(gini_by_a)}")
    vals = [gini_by_a[k] for k in keys]
    if any(v is ... for v in vals):
        fb.todo("some values are still ...")
        return
    ref = {k: stats.gini(models.price(n_papers=3000, m=3, a=k, seed=1)) for k in keys}
    for k in keys:
        fb.number(f"gini_by_a[{k}]", gini_by_a[k], ref[k], abs_tol=0.04, fmt="{:.3f}")
    vals = [float(v) for v in vals]
    if all(x > y for x, y in zip(vals, vals[1:])):
        fb.ok("inequality falls as a grows")
    else:
        fb.no("inequality should fall as a grows; check that each run uses its own value of a")


@exercise(LESSON, 3, "Sampling a power law")
def ex3(fb, sample_power_law):
    x = np.asarray(fb.call("sample_power_law", sample_power_law, 20000, 2.5, 1.0, np.random.default_rng(0)),
                   dtype=float)
    if x.shape != (20000,):
        raise Wrong(f"sample_power_law(20000, ...) should return 20,000 values, not {describe(x)}")
    if x.min() < 1.0:
        raise Wrong(f"some values are below xmin = 1 (minimum {x.min():.3g}): check the sign of the exponent")
    a_hat = stats.alpha_mle(x, 1.0)
    if abs(a_hat - 2.5) < 0.06:
        fb.ok(f"the exponent fitted to your sample is {a_hat:.3f}, as it should be (2.5)")
    elif abs(a_hat - 3.5) < 0.1:
        fb.no(f"your sample has exponent {a_hat:.2f}, not 2.5: use -1 / (alpha - 1) in the exponent, not -1 / alpha")
    else:
        fb.no(f"your sample has exponent {a_hat:.2f}, not 2.5: compare your formula with the inverse transform in the lesson")
    y = np.asarray(fb.call("sample_power_law", sample_power_law, 5000, 3.0, 10.0, np.random.default_rng(1)),
                   dtype=float)
    if y.min() < 10.0:
        fb.no(f"with xmin = 10 some values fall below 10 (minimum {y.min():.3g}): multiply by xmin")
    elif abs(stats.alpha_mle(y, 10.0) - 3.0) < 0.12:
        fb.ok("it also works with xmin = 10 and alpha = 3")
    else:
        fb.no(f"with xmin = 10 and alpha = 3 the fitted exponent is {stats.alpha_mle(y, 10.0):.2f}, not 3")


@exercise(LESSON, 4, "The maximum-likelihood exponent")
def ex4(fb, alpha_mle):
    x = stats.sample_power_law(5000, 2.2, 3.0, rng=7)
    target = stats.alpha_mle(x, 3.0)
    v = fb.call("alpha_mle", alpha_mle, x, 3.0)
    fb.number("alpha_mle(sample, xmin=3)", v, target, rel_tol=1e-6, diagnose=lambda v:
              "you are 1 short: alpha_hat = 1 + n / sum(log(x / xmin))" if _close(v, target - 1) else
              "use the natural logarithm (np.log), not log10" if _close(v, 1 + (target - 1) * np.log(10)) else None,
              fmt="{:.4f}")
    if fb.status() != "pass":
        return
    with_small = np.concatenate([x, [1.0, 2.0, 2.5]])
    v2 = fb.call("alpha_mle", alpha_mle, with_small, 3.0)
    fb.number("alpha_mle ignores values below xmin", v2, target, rel_tol=1e-6, diagnose=lambda v:
              "keep only the values x >= xmin before fitting" if not _close(v, target) else None, fmt="{:.4f}")


def _reference_fit(x):
    import powerlaw

    with quiet():
        fit = powerlaw.Fit(x, discrete=True, verbose=False)
        R, p = fit.distribution_compare("power_law", "lognormal", normalized_ratio=True)
    return fit, float(R), float(p)


@exercise(LESSON, 5, "Power law or lognormal?")
def ex5(fb, alpha_hat, xmin_hat, R, p):
    fit, R0, p0 = _reference_fit(data.citation_counts())
    a0, x0 = fit.power_law.alpha, fit.power_law.xmin
    fb.number("alpha_hat", alpha_hat, a0, rel_tol=1e-3, fmt="{:.3f}", diagnose=lambda v:
              "fit with discrete=True: citation counts are whole numbers" if abs(v - a0) < 0.5 else None)
    fb.number("xmin_hat", xmin_hat, x0, rel_tol=1e-9, fmt="{:g}")
    fb.number("R", R, R0, abs_tol=0.01, fmt="{:.3f}", diagnose=lambda v:
              "the sign is flipped: compare in the order ('power_law', 'lognormal')" if _close(v, -R0, 1e-2) else
              "pass normalized_ratio=True" if abs(v) > 3 * abs(R0) + 1 else None)
    fb.number("p", p, p0, abs_tol=0.01, fmt="{:.3f}")
    if fb.status() == "pass":
        verdict = "neither model is clearly better" if p0 > 0.1 else (
            "the power law fits better" if R0 > 0 else "the lognormal fits better")
        fb.info(f"R = {R0:.2f} with p = {p0:.2f}: {verdict}.")


@exercise(LESSON, 6, "Lotka's law")
def ex6(fb, table, share_single):
    au = data.authorship()
    ref = stats.productivity(au)
    if table is ...:
        fb.todo("table: replace the ... with your answer")
    elif not isinstance(table, pd.Series):
        fb.no(f"table should be a pandas Series (index: number of articles, values: number of authors), "
              f"but it is {describe(table)}")
    elif not pd.api.types.is_numeric_dtype(table.index):
        fb.no("that looks like the number of articles per author (one row per author). Now count how many "
              "authors have each number (value_counts), and sort by the number of articles")
    else:
        t = table.sort_index()
        if t.index.tolist() == ref.index.tolist() and np.array_equal(t.to_numpy(), ref.to_numpy()):
            fb.ok(f"table matches: {int(ref.loc[1])} authors wrote one article, {int(ref.loc[2])} wrote two, ...")
        else:
            fb.no("table differs: count each author once per article, then count authors per number of articles")
    share = ref.loc[1] / ref.sum()
    fb.number("share_single", share_single, share, diagnose=lambda v:
              "give a share between 0 and 1, not a percentage" if _close(v, 100 * share) else
              "that is a count; divide it by the number of authors" if _close(v, ref.loc[1]) else
              "divide by the number of authors, not of articles" if _close(v, ref.loc[1] / au["article"].nunique())
              else None)
    if fb.status() == "pass":
        fb.info(f"{share:.1%} of authors wrote a single article; Lotka's law with exponent 2 predicts "
                f"{stats.lotka_share_single(2.0):.1%}.")


@exercise(LESSON, 7, "Bradford's zones")
def ex7(fb, my_bradford_zones):
    toy = [10, 5, 5, 3, 2, 2, 1, 1, 1]
    z_toy = np.asarray(fb.call("my_bradford_zones", my_bradford_zones, toy, 3))
    if z_toy.shape == (3,) and np.array_equal(z_toy, stats.bradford_zones(toy, 3)):
        fb.ok(f"my_bradford_zones({toy}) = {z_toy.tolist()}")
    else:
        fb.no(f"for {toy} the zones should hold {stats.bradford_zones(toy, 3).tolist()} journals, "
              f"but you return {z_toy.tolist() if z_toy.ndim else z_toy}")
        return
    counts = data.journal_counts()
    ref = stats.bradford_zones(counts, 3)
    z = np.asarray(fb.call("my_bradford_zones", my_bradford_zones, counts, 3))
    if np.array_equal(z, ref):
        fb.ok(f"on the 250 journals: {ref.tolist()} journals per zone")
    else:
        fb.no(f"on the 250 journals you get {z.tolist()}: did you sort from most to least productive?")


@exercise(LESSON, 8, "Counting Dante's words")
def ex8(fb, tokens, freqs, hapax_share):
    ref_tokens = stats.tokenize(data.commedia())
    ref_freqs = stats.rank_frequency(ref_tokens)
    if tokens is ...:
        fb.todo("tokens: replace the ... with your answer")
    elif not isinstance(tokens, (list, tuple, np.ndarray, pd.Series)):
        fb.no(f"tokens should be a list of words, but it is {describe(tokens)}")
    elif len(tokens) == len(ref_tokens):
        fb.ok(f"{len(tokens):,} tokens")
    else:
        fb.no(f"{len(tokens):,} tokens instead of {len(ref_tokens):,}: lower-case the text and use the WORD pattern")
    if freqs is ...:
        fb.todo("freqs: replace the ... with your answer")
    else:
        f = np.asarray(freqs)
        if f.shape == ref_freqs.shape and np.array_equal(f, ref_freqs):
            fb.ok(f"{f.size:,} distinct words (types), the most frequent used {f[0]:,} times")
        elif f.shape == ref_freqs.shape and np.array_equal(f, ref_freqs[::-1]):
            fb.no("freqs is sorted from least to most frequent: reverse it")
        else:
            fb.no(f"freqs should hold one count per distinct word, most frequent first ({ref_freqs.size:,} values)")
    share = np.mean(ref_freqs == 1)
    fb.number("hapax_share", hapax_share, share, diagnose=lambda v:
              "that is the hapaxes' share of all tokens; we want their share of distinct words (types)"
              if _close(v, np.sum(ref_freqs == 1) / ref_freqs.sum()) else
              "give a share between 0 and 1, not a percentage" if _close(v, 100 * share) else None)
    if fb.status() == "pass":
        fb.info(f"{share:.0%} of Dante's distinct words occur exactly once (hapax legomena).")


@exercise(LESSON, 9, "Zipf's exponent")
def ex9(fb, alpha_words, zipf_s):
    import powerlaw

    freqs = stats.rank_frequency(stats.tokenize(data.commedia()))
    with quiet():
        a0 = powerlaw.Fit(freqs, discrete=True, verbose=False).power_law.alpha
    fb.number("alpha_words", alpha_words, a0, rel_tol=1e-3, fmt="{:.3f}")
    fb.number("zipf_s", zipf_s, 1 / (a0 - 1), rel_tol=2e-3, fmt="{:.3f}", diagnose=lambda v:
              "use s = 1 / (alpha - 1)" if _close(v, a0 - 1, 1e-3) or _close(v, 1 / a0, 1e-3) else None)
    if fb.status() == "pass":
        fb.info(f"Zipf exponent s = {1 / (a0 - 1):.2f}: close to the classic value of 1.")


def summary():
    """Show which S1.3 exercises you have done in this session."""
    return progress(sys.modules[__name__])
