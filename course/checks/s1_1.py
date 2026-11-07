"""Checks for S1.1 · Data, variables and measurement."""

import sys

import numpy as np
import pandas as pd

from .. import data
from ..checking import Todo, Wrong, describe, exercise, progress

LESSON = "S1.1"


def _close(v, target, tol=1e-6):
    return bool(np.isclose(v, target, rtol=tol, atol=1e-9))


def _letters(answer, n, allowed, example):
    """The letters of a string answer, or Todo/Wrong if it is not usable."""
    if answer is ...:
        raise Todo(f'set answer to {n} letters, for example "{example}"')
    if not isinstance(answer, str):
        raise Wrong(f'answer should be a string of letters such as "{example}", not {describe(answer)}')
    letters = [ch for ch in answer.upper() if ch.isalpha()]
    if len(letters) != n:
        raise Wrong(f"write exactly {n} letters, one per item (you wrote {len(letters)})")
    wrong = sorted(set(letters) - set(allowed))
    if wrong:
        raise Wrong(f"use only the letters {', '.join(allowed)} (you wrote {', '.join(wrong)})")
    return letters


def page_counts() -> pd.Series:
    """Number of pages of each article: last page - first page + 1."""
    first_last = data.bibliothecae().articles["pages"].str.split("-", expand=True).astype(int)
    return first_last[1] - first_last[0] + 1


def keyword_pairs() -> pd.Series:
    """One row per article and keyword."""
    return data.bibliothecae().articles.set_index("id")["keywords"].str.split("; ").explode()


@exercise(LESSON, 1, "One row, one link?")
def ex1(fb, n_links, n_distinct, n_citing):
    t = data.bibliothecae().article_reference
    fb.number("n_links", n_links, len(t), fmt="{:,.0f}")
    fb.number("n_distinct", n_distinct, len(t.drop_duplicates()), fmt="{:,.0f}", diagnose=lambda v:
              "that counts different references; count different rows, that is, pairs of article and reference"
              if _close(v, t["reference"].nunique()) else
              "that counts the duplicated rows; count the rows that remain after dropping them"
              if _close(v, t.duplicated().sum()) else None)
    fb.number("n_citing", n_citing, t["id"].nunique(), fmt="{:,.0f}", diagnose=lambda v:
              "that is every article of the journal; count only those that appear in article_reference"
              if _close(v, len(data.bibliothecae().articles)) else None)
    if fb.status() == "pass":
        fb.info(f"{len(t) - len(t.drop_duplicates())} rows are exact duplicates: links counted twice. And only "
                f"{t['id'].nunique()} of the 321 articles have references in the data (section 7 says why).")


@exercise(LESSON, 2, "What type is each variable?")
def ex2(fb, answer):
    letters = _letters(answer, 8, "NOIR", "NNNNNNNN")
    truth = "NIORNRRO"
    why = {
        0: "A, language: categories with no order, so nominal",
        1: "B, year: equal steps, but the year 0 is a convention, not 'no time', so interval",
        2: "C, rank: an order without equal distances, so ordinal",
        3: "D, number of references: a count with a true zero, so ratio",
        4: "E, section: categories with no order, so nominal",
        5: "F, age: 0 years means no time has passed, and 40 years is twice 20, so ratio",
        6: "G, number of pages: a count with a true zero, so ratio",
        7: "H, first or second issue: an order, but no numbers to add, so ordinal",
    }
    if "".join(letters) == truth:
        fb.ok("NIORNRRO: two nominal, one interval, two ordinal and three ratio variables")
        return
    for i, (got, want) in enumerate(zip(letters, truth)):
        if got != want:
            fb.no(f"not {got} for {why[i]}")


@exercise(LESSON, 3, "Text that should be numbers")
def ex3(fb, max_text, max_number, n_pages, total_pages):
    vol = data.bibliothecae().articles["volume"]
    if max_text is ...:
        fb.todo("max_text: replace the ... with your answer")
    elif str(max_text) == vol.max():
        fb.ok(f'max_text is "{vol.max()}": as text, "9" comes after "14"')
    elif isinstance(max_text, (int, float, np.number)) and _close(max_text, vol.astype(int).max()):
        fb.no("max_text should be the largest value as text, before any conversion: bib.articles['volume'].max()")
    else:
        fb.no(f"max_text is {describe(max_text)}; take .max() of the column as it is")
    fb.number("max_number", max_number, vol.astype(int).max(), fmt="{:g}", diagnose=lambda v:
              "that is the largest as text; convert to numbers first with .astype(int)" if _close(v, 9) else None)
    pc = page_counts()
    if n_pages is ...:
        fb.todo("n_pages: replace the ... with your answer")
    else:
        try:
            arr = np.asarray(n_pages, dtype=float)
        except (TypeError, ValueError):
            arr = None
        if arr is None or arr.shape != pc.shape:
            fb.no(f"n_pages should hold one number per article, {len(pc)} in all, but it is {describe(n_pages)}")
        elif np.allclose(arr, pc):
            fb.ok("n_pages is right")
        elif np.allclose(arr, pc - 1):
            fb.no("n_pages is one short for every article: pages 137 to 184 are 48 pages, so add 1")
        elif np.allclose(arr, -(pc - 1)) or np.allclose(arr, -pc):
            fb.no("subtract the first page from the last, not the other way round")
        else:
            fb.no("n_pages is not right yet: compare its first value with the first article's pages, 137-184")
    fb.number("total_pages", total_pages, pc.sum(), fmt="{:,.0f}", diagnose=lambda v:
              "one page short for every article: add 1 to each difference" if _close(v, pc.sum() - len(pc)) else None)
    if fb.status() == "pass":
        fb.info(f"The journal has published {pc.sum():,} pages; the longest article has {pc.max()}.")


@exercise(LESSON, 4, "Tidy keywords")
def ex4(fb, n_pairs, n_distinct, top):
    kw = keyword_pairs()
    fb.number("n_pairs", n_pairs, len(kw), fmt="{:,.0f}", diagnose=lambda v:
              "that is the number of articles; count the rows after .explode()" if _close(v, 321) else None)
    exact, merged = kw.nunique(), kw.str.strip().str.lower().nunique()
    if n_distinct is ...:
        fb.todo("n_distinct: replace the ... with your answer")
    elif _close(n_distinct, exact) or _close(n_distinct, merged):
        fb.ok(f"n_distinct = {exact}" + ("" if _close(n_distinct, exact) else
              f" ({merged} once you merge keywords that differ only in capitals: well spotted)"))
    else:
        fb.number("n_distinct", n_distinct, exact, fmt="{:,.0f}", diagnose=lambda v:
                  "that counts pairs; count the different keywords with .nunique()" if _close(v, len(kw)) else None)
    best = kw.value_counts().index[0]
    if top is ...:
        fb.todo("top: replace the ... with your answer")
    elif isinstance(top, str) and top.strip().lower() == best.lower():
        fb.ok(f'top is "{best}", used by {kw.value_counts().iloc[0]} articles')
    elif isinstance(top, (int, float, np.number)) and _close(top, kw.value_counts().iloc[0]):
        fb.no("that is how often the top keyword is used; top should be the keyword itself: .index[0]")
    else:
        fb.no(f"top is {describe(top)}; take the first name in keywords.value_counts()")


@exercise(LESSON, 5, "Population or sample?")
def ex5(fb, answer):
    letters = _letters(answer, 4, "PS", "PPPP")
    truth = "PSSP"
    why = {
        0: "A asks about the journal's own articles, all of which are in the table: a population",
        1: "B asks about many Italian journals; this journal is only a sample of them",
        2: "C asks about humanities scholars in general; the journal's authors are only a sample of them",
        3: "D asks about the journal's own authors, all of whom appear: a population",
    }
    if "".join(letters) == truth:
        fb.ok("PSSP: the same 321 articles are a population for A and D, and a sample, not a random one, for B and C")
        return
    for i, (got, want) in enumerate(zip(letters, truth)):
        if got != want:
            fb.no(f"not {got}: {why[i]}")


@exercise(LESSON, 6, "Years that cannot be years")
def ex6(fb, n_missing, n_impossible, share_unusable):
    r = data.bibliothecae().references
    y = pd.to_numeric(r["date"], errors="coerce")
    miss = int((r["date"] == "").sum())
    early, late = int((y < 1400).sum()), int((y > 2025).sum())
    fb.number("n_missing", n_missing, miss, fmt="{:,.0f}")
    fb.number("n_impossible", n_impossible, early + late, fmt="{:,.0f}", diagnose=lambda v:
              "that counts only one kind: add the years before 1400 and those after 2025, joined with |"
              if _close(v, early) or _close(v, late) else
              "that also counts the missing years; count only the years that are present but impossible"
              if _close(v, early + late + miss) else None)
    share = (miss + early + late) / len(r)
    fb.number("share_unusable", share_unusable, share, abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "count both the missing and the impossible years" if _close(v, miss / len(r)) or
              _close(v, (early + late) / len(r)) else
              "a share is a number between 0 and 1: divide by the number of references, don't multiply by 100"
              if _close(v, 100 * share) else None)
    if fb.status() == "pass":
        fb.info(f"{share:.1%} of the references have no usable year: about one in eight.")


@exercise(LESSON, 7, "Missing at random?")
def ex7(fb, missing_with, missing_without, times):
    r = data.bibliothecae().references
    no_year, has_author = r["date"] == "", r["author"] != ""
    w, wo = no_year[has_author].mean(), no_year[~has_author].mean()
    fb.number("missing_with", missing_with, w, abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "these are swapped: missing_with is for the references that do have an author" if _close(v, wo) else
              "that is the share for all references; keep only those with an author: no_year[has_author]"
              if _close(v, no_year.mean()) else None)
    fb.number("missing_without", missing_without, wo, abs_tol=1e-4, fmt="{:.4f}", diagnose=lambda v:
              "these are swapped: missing_without is for the references with no author" if _close(v, w) else None)
    fb.number("times", times, wo / w, abs_tol=0.01, fmt="{:.2f}", diagnose=lambda v:
              "divide the larger share by the smaller one: missing_without / missing_with" if _close(v, w / wo) else None)
    if fb.status() == "pass":
        fb.info(f"{wo:.1%} against {w:.1%}: references without an author lack a year {wo / w:.1f} times as often.")


def summary():
    """Show which S1.1 exercises you have done in this session."""
    return progress(sys.modules[__name__])
