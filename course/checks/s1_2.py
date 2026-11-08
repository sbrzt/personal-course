"""Checks for S1.2 · Counting and tables."""

import sys

import numpy as np
import pandas as pd

from .. import bibliothecae, data
from ..checking import describe, exercise, progress

LESSON = "S1.2"


def _close(v, target, tol=1e-6):
    try:
        return bool(np.isclose(float(v), float(target), rtol=tol, atol=1e-9))
    except (TypeError, ValueError):
        return False


def _series(fb, name, value, target, wrong=()) -> bool:
    """Check a Series answer by its labels and values; `wrong` lists (Series, hint) pairs."""
    if value is ...:
        fb.todo(f"{name}: replace the ... with your answer")
        return False
    if not isinstance(value, pd.Series):
        fb.no(f"{name} should be a pandas Series, one value per category, but it is {describe(value)}")
        return False
    if set(value.index) != set(target.index):
        fb.no(f"{name} should have one value for each of the {len(target)} categories, but it has {len(value)}")
        return False
    v = value.reindex(target.index).astype(float)
    if np.allclose(v, target.astype(float)):
        fb.ok(f"{name} is right")
        return True
    for other, hint in wrong:
        if np.allclose(v, other.reindex(target.index).astype(float)):
            fb.no(f"{name} is not right yet: {hint}")
            return False
    fb.no(f"{name} is not right yet: compare a few of its values with the tables above")
    return False


def years() -> pd.Series:
    return data.bibliothecae().articles["date"].str[:4].astype(int).rename("year")


def page_counts() -> pd.Series:
    first_last = data.bibliothecae().articles["pages"].str.split("-", expand=True).astype(int)
    return first_last[1] - first_last[0] + 1


def ref_type(text: str) -> str:
    """The rough rules of section 7."""
    if "«" in text:
        return "periodical"
    if ", in " in text:
        return "chapter"
    if "http" in text or "www." in text:
        return "web"
    return "book or other"


def reference_types() -> pd.Series:
    return data.bibliothecae().references.set_index("reference")["content"].map(ref_type)


def type_by_period() -> pd.DataFrame:
    links = bibliothecae.citation_links(data.bibliothecae())
    links["type"] = links["reference"].map(reference_types())
    links["period"] = np.where(links["citing_year"] <= 2020, "2016-2020", "2021-2025")
    return pd.crosstab(links["type"], links["period"], normalize="columns") * 100


@exercise(LESSON, 1, "Articles by section")
def ex1(fb, counts, shares, share_top3):
    s = data.bibliothecae().articles["section"]
    c, f = s.value_counts(), s.value_counts(normalize=True)
    _series(fb, "counts", counts, c, wrong=[(f, "these are shares; counts are whole numbers: value_counts()")])
    _series(fb, "shares", shares, f, wrong=[
        (c, "these are counts; for shares use value_counts(normalize=True)"),
        (100 * f, "these are percentages; give shares between 0 and 1"),
    ])
    fb.number("share_top3", share_top3, f.iloc[:3].sum(), abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "that is a count; divide by the 321 articles, or add up the shares" if _close(v, c.iloc[:3].sum()) else
              "that is a percentage; give a share between 0 and 1" if _close(v, 100 * f.iloc[:3].sum()) else
              "that adds the three smallest sections; value_counts() puts the largest first"
              if _close(v, f.iloc[-3:].sum()) else None)
    if fb.status() == "pass":
        fb.info(f"Essays, Notes and discussions, and Documentation hold {f.iloc[:3].sum():.0%} of all articles.")


@exercise(LESSON, 2, "Half of the journal")
def ex2(fb, per_year, cum_share, half_by):
    y = years()
    py = y.value_counts().sort_index()
    cs = py.cumsum() / py.sum()
    if _series(fb, "per_year", per_year, py) and not list(per_year.index) == sorted(per_year.index):
        fb.info("per_year has the right counts, but not in time order: add .sort_index()")
    _series(fb, "cum_share", cum_share, cs, wrong=[
        (py.cumsum(), "these are cumulative counts; divide them by the total number of articles"),
        (100 * cs, "these are percentages; give shares between 0 and 1"),
        (y.value_counts().cumsum().reindex(cs.index) / py.sum(),
         "the years must be in time order before .cumsum(): add .sort_index() first"),
    ])
    first = int(cs[cs >= 0.5].index[0])
    fb.number("half_by", half_by, first, fmt="{:g}", diagnose=lambda v:
              f"by the end of {first - 1} only {cs[first - 1]:.0%} had appeared" if _close(v, first - 1) else
              f"by the end of {first} more than half had already appeared" if _close(v, first + 1) else None)
    if fb.status() == "pass":
        fb.info(f"Half of the journal's articles had appeared by the end of {first} ({cs[first]:.0%}).")


@exercise(LESSON, 3, "Modes")
def ex3(fb, mode_year, n_mode_year, mode_pages, n_mode_pages):
    yv, pv = years().value_counts(), page_counts().value_counts()
    fb.number("mode_year", mode_year, yv.idxmax(), fmt="{:g}", diagnose=lambda v:
              "that is how many articles; the mode is the year itself: .idxmax()" if _close(v, yv.max()) else None)
    fb.number("n_mode_year", n_mode_year, yv.max(), fmt="{:g}", diagnose=lambda v:
              "that is the year; give how many articles it has: .max()" if _close(v, yv.idxmax()) else None)
    fb.number("mode_pages", mode_pages, pv.idxmax(), fmt="{:g}", diagnose=lambda v:
              "that is how many articles; the mode is the number of pages itself: .idxmax()"
              if _close(v, pv.max()) else
              "that is the largest number of pages, not the most common one" if _close(v, page_counts().max()) else None)
    fb.number("n_mode_pages", n_mode_pages, pv.max(), fmt="{:g}", diagnose=lambda v:
              "that is the number of pages; give how many articles have it: .max()" if _close(v, pv.idxmax()) else None)


@exercise(LESSON, 4, "A two-way table")
def ex4(fb, table, essays_late, late_total):
    y = years()
    sections = data.bibliothecae().articles["section"]
    period = pd.Series(np.where(y <= 2018, "2012-2018", "2019-2025"), index=y.index, name="period")
    t = pd.crosstab(sections, period, margins=True)
    if table is ...:
        fb.todo("table: replace the ... with your answer")
    elif not isinstance(table, pd.DataFrame):
        fb.no(f"table should be a DataFrame made by pd.crosstab, but it is {describe(table)}")
    else:
        try:
            ok = all(_close(table.loc[r, c], t.loc[r, c]) for r in t.index for c in t.columns)
        except KeyError:
            ok = None
        if ok:
            fb.ok("table is right, margins included")
        elif ok is None and all(r in table.index for r in t.index[:-1]):
            fb.no("table has the counts but no totals: add margins=True")
        elif ok is None:
            fb.no("table should have the sections as rows and the periods as columns: pd.crosstab(sections, period, "
                  "margins=True)")
        else:
            fb.no("table has the right shape but some wrong counts: build it with pd.crosstab(sections, period, "
                  "margins=True)")
    fb.number("essays_late", essays_late, t.loc["Essays", "2019-2025"], fmt="{:g}", diagnose=lambda v:
              "that is the earlier period; you want the column 2019-2025" if _close(v, t.loc["Essays", "2012-2018"]) else
              "that is all the essays; keep only those of 2019-2025" if _close(v, t.loc["Essays", "All"]) else None)
    fb.number("late_total", late_total, t.loc["All", "2019-2025"], fmt="{:g}", diagnose=lambda v:
              "that is the earlier period; you want the column 2019-2025" if _close(v, t.loc["All", "2012-2018"]) else
              "that is every article; read the total of the column 2019-2025, in the row All"
              if _close(v, t.loc["All", "All"]) else None)


@exercise(LESSON, 5, "Which way round?")
def ex5(fb, essays_among_other, other_among_essays, essays_among_italian):
    a = data.bibliothecae().articles
    essay, other = a["section"] == "Essays", a["langLabel"] != "Italian"
    eo, oe, ei = essay[other].mean(), other[essay].mean(), essay[~other].mean()
    fb.number("essays_among_other", essays_among_other, eo, abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "that is the other direction, the share of other languages among the essays: use the row shares"
              if _close(v, oe) else
              "that is a percentage; give a share between 0 and 1" if _close(v, 100 * eo) else None)
    fb.number("other_among_essays", other_among_essays, oe, abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "that is the other direction, the share of essays among other languages: use the column shares"
              if _close(v, eo) else
              "that is a percentage; give a share between 0 and 1" if _close(v, 100 * oe) else None)
    fb.number("essays_among_italian", essays_among_italian, ei, abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "that is the share of Italian articles among the essays; you want the essays among the Italian articles"
              if _close(v, (~other)[essay].mean()) else None)
    if fb.status() == "pass":
        fb.info(f"{eo:.0%} of the articles in other languages are essays, but only {oe:.0%} of the essays are in "
                "other languages: one cell, two totals.")


@exercise(LESSON, 6, "More chapters?")
def ex6(fb, share_web, pct_chapter_early, pct_chapter_late, change):
    t = reference_types()
    sw = (t == "web").mean()
    bp = type_by_period()
    early, late = bp.loc["chapter", "2016-2020"], bp.loc["chapter", "2021-2025"]
    fb.number("share_web", share_web, sw, abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "that is a count; give the share: value_counts(normalize=True)" if _close(v, (t == "web").sum()) else
              "that is a percentage; give a share between 0 and 1" if _close(v, 100 * sw) else None)
    fb.number("pct_chapter_early", pct_chapter_early, early, abs_tol=0.01, fmt="{:.2f}", diagnose=lambda v:
              "that is the later period" if _close(v, late) else
              "that is a share; by_period already holds percentages" if _close(v, early / 100) else None)
    fb.number("pct_chapter_late", pct_chapter_late, late, abs_tol=0.01, fmt="{:.2f}", diagnose=lambda v:
              "that is the earlier period" if _close(v, early) else None)
    fb.number("change", change, late - early, abs_tol=0.01, fmt="{:+.2f}", diagnose=lambda v:
              "subtract the other way round: later minus earlier" if _close(v, early - late) else
              "that is a relative change; the question asks for the difference in percentage points"
              if _close(v, 100 * (late - early) / early) else None)
    if fb.status() == "pass":
        fb.info(f"Chapters went from {early:.1f}% to {late:.1f}% of the citations: {late - early:+.1f} points.")


def summary():
    """Show which S1.2 exercises you have done in this session."""
    return progress(sys.modules[__name__])
