"""Checks for S1.2 · Concentration and association."""

import sys

import numpy as np
import pandas as pd

from ... import data, stats
from ...checking import Wrong, describe, exercise, progress

LESSON = "S1.2"


def _close(v, target, tol=1e-6):
    return bool(np.isclose(v, target, rtol=tol, atol=1e-9))


@exercise(LESSON, 1, "Top shares")
def ex1(fb, top10_share, top1_share):
    x = data.citation_counts()
    for name, answer, q in [("top10_share", top10_share, 0.10), ("top1_share", top1_share, 0.01)]:
        target = stats.top_share(x, q)
        bottom = np.sort(x)[: int(np.ceil(q * x.size))].sum() / x.sum()
        fb.number(name, answer, target, abs_tol=0.002, diagnose=lambda v, t=target, b=bottom:
                  "give a share between 0 and 1, not a percentage" if _close(v, 100 * t) else
                  "that is the share of the LEAST cited papers: sort from most to least cited"
                  if _close(v, b) else
                  "close, but not exact: with ties at the threshold, selecting by a percentile "
                  "picks more or fewer papers than you want. Sort and take exactly the top k papers"
                  if abs(v - t) < 0.05 else None)
    if fb.status() == "pass":
        fb.info(f"The top 10% of papers receive {stats.top_share(x, .1):.0%} of all citations; "
                f"the top 1% receive {stats.top_share(x, .01):.0%}.")


@exercise(LESSON, 2, "Your own Gini coefficient")
def ex2(fb, my_gini):
    cases = [([1, 1, 1, 1], 0.0, "everyone equal"),
             ([0, 0, 0, 1], 0.75, "one holder takes all"),
             ([1, 2, 3, 4, 5], 4 / 15, "1 to 5")]
    good = True
    for values, target, label in cases:
        v = fb.call("my_gini", my_gini, np.array(values, dtype=float))
        n = len(values)
        fb.number(f"my_gini({values})  [{label}]", v, target, rel_tol=1e-6, diagnose=lambda v, t=target, n=n:
                  "that is the 'sample' Gini, n/(n-1) times the usual one. Use the formula in the lesson"
                  if _close(v, t * n / (n - 1)) else
                  "negative: is your array sorted from smallest to largest?" if v < 0 else
                  "that looks like 1 minus the Gini" if _close(v, 1 - t) else None)
        good = good and fb.status() == "pass"
    if not good:
        return
    x = data.citation_counts()
    v = fb.call("my_gini", my_gini, x)
    fb.number("my_gini(cites)", v, stats.gini(x), rel_tol=1e-6)
    if fb.status() == "pass":
        fb.info(f"Gini of citations: {stats.gini(x):.2f}; of reference counts: "
                f"{stats.gini(data.reference_counts()):.2f}.")


@exercise(LESSON, 3, "Pearson or Spearman?")
def ex3(fb, pearson_all, spearman_all, pearson_articles, spearman_articles):
    df = data.refs_and_cites()
    art = df[df["type"] == "article"]
    ref = {
        "pearson_all": df["references"].corr(df["citations"]),
        "spearman_all": df["references"].corr(df["citations"], method="spearman"),
        "pearson_articles": art["references"].corr(art["citations"]),
        "spearman_articles": art["references"].corr(art["citations"], method="spearman"),
    }
    answers = dict(pearson_all=pearson_all, spearman_all=spearman_all,
                   pearson_articles=pearson_articles, spearman_articles=spearman_articles)
    for name, answer in answers.items():
        other = ref[name.replace("pearson", "TMP").replace("spearman", "pearson").replace("TMP", "spearman")]
        fb.number(name, answer, ref[name], rel_tol=1e-4, diagnose=lambda v, o=other, n=name:
                  "that is the other coefficient: Pearson and Spearman are swapped" if _close(v, o, 1e-4) else
                  "check which rows you kept" if "articles" in n else None, fmt="{:.3f}")
    if fb.status() == "pass":
        fb.info(f"One review article lifts Pearson's r from {ref['pearson_articles']:.2f} to "
                f"{ref['pearson_all']:.2f}; Spearman's rho barely moves "
                f"({ref['spearman_articles']:.2f} → {ref['spearman_all']:.2f}).")


def _as_wide(by_field):
    """Accept the field-by-OA table as wide (fields x {False, True}) or long (MultiIndex)."""
    if isinstance(by_field, pd.Series) and isinstance(by_field.index, pd.MultiIndex):
        by_field = by_field.unstack()
    if not isinstance(by_field, pd.DataFrame):
        raise Wrong(f"by_field should be a DataFrame with one row per field, but it is {describe(by_field)}")
    if set(by_field.index) == {False, True}:
        by_field = by_field.T
    return by_field


@exercise(LESSON, 4, "Simpson's paradox")
def ex4(fb, overall, by_field):
    oa = data.oa_articles()
    ref_overall = oa.groupby("oa")["citations"].mean()
    ref_field = oa.groupby(["field", "oa"])["citations"].mean().unstack()
    if overall is ...:
        fb.todo("overall: replace the ... with your answer")
    elif not isinstance(overall, pd.Series) or set(overall.index) != {False, True}:
        fb.no(f"overall should be a Series indexed by oa (False, True), but it is {describe(overall)}")
    else:
        med = oa.groupby("oa")["citations"].median()
        for key, label in [(False, "closed"), (True, "open access")]:
            fb.number(f"overall[{key}] ({label})", overall[key], ref_overall[key], rel_tol=1e-6,
                      diagnose=lambda v, k=key: "that is the median; use the mean here"
                      if _close(v, med[k]) else None, fmt="{:.2f}")
    if by_field is ...:
        fb.todo("by_field: replace the ... with your answer")
    else:
        wide = _as_wide(by_field)
        if set(wide.index) != set(ref_field.index) or not {False, True} <= set(wide.columns):
            fb.no("by_field should have one row per field and columns False and True")
        else:
            # reindex treats [False, True] as labels (a .loc list of booleans would be a mask)
            mine = wide.reindex(index=ref_field.index, columns=[False, True]).to_numpy(float)
            theirs = ref_field.reindex(columns=[False, True]).to_numpy(float)
            ok = np.allclose(mine, theirs)
            if ok:
                fb.ok("by_field matches: mean citations for each field and access type")
            else:
                fb.no("by_field values differ from the means by field and access type")
    if fb.status() == "pass":
        fb.info(f"Overall, open-access articles average {ref_overall[True]:.1f} citations against "
                f"{ref_overall[False]:.1f}, yet within each field they average fewer.")


@exercise(LESSON, 5, "Field-normalised citation scores")
def ex5(fb, mncs):
    oa = data.oa_articles()
    ncs = oa["citations"] / oa.groupby("field")["citations"].transform("mean")
    ref = ncs.groupby(oa["oa"]).mean()
    overall_norm = (oa["citations"] / oa["citations"].mean()).groupby(oa["oa"]).mean()
    if mncs is ...:
        fb.todo("mncs: replace the ... with your answer")
        return
    if not isinstance(mncs, pd.Series) or set(mncs.index) != {False, True}:
        raise Wrong(f"mncs should be a Series indexed by oa (False, True), but it is {describe(mncs)}")
    for key, label in [(False, "closed"), (True, "open access")]:
        fb.number(f"mncs[{key}] ({label})", mncs[key], ref[key], rel_tol=1e-6, diagnose=lambda v, k=key:
                  "you divided by the overall mean; divide each paper by the mean of ITS field "
                  "(groupby('field') with transform('mean'))" if _close(v, overall_norm[k]) else None,
                  fmt="{:.3f}")
    if fb.status() == "pass":
        raw = oa.groupby("oa")["citations"].mean()
        fb.info(f"Raw ratio, open access to closed: {raw[True] / raw[False]:.2f}. "
                f"Field-normalised ratio: {ref[True] / ref[False]:.2f}.")


def summary():
    """Show which S1.2 exercises you have done in this session."""
    return progress(sys.modules[__name__])
