"""Standard views of the Bibliothecae.it corpus.

These are the reference answers for the S1.4 project, and later lessons
reuse them. Each function takes a `course.data.Corpus` (real or simulated).

Rules, stated once:
- Only the articles listed in `articles` count; relation rows pointing to
  other items are ignored.
- A citation is one (citing article, reference) link.
- A year is the first four-digit number in a date field.
- A cited year is valid if 1400 <= year <= the citing article's year.
- A venue is any text in «guillemets» in a reference, with spaces squeezed,
  outer punctuation stripped and case folded.
"""

from __future__ import annotations

import re

import pandas as pd

from . import stats

VENUE = re.compile(r"«([^»]{2,120})»")


def citation_links(c) -> pd.DataFrame:
    """One row per citation: id, reference, citing_year, cited_year (NaN if no year)."""
    arts = c.articles[["id"]].assign(citing_year=stats.year_of(c.articles["date"]).to_numpy())
    links = c.article_reference.drop_duplicates().merge(arts, on="id", how="inner")
    years = c.references[["reference"]].assign(cited_year=stats.year_of(c.references["date"]).to_numpy())
    return links.merge(years.drop_duplicates("reference"), on="reference", how="left")


def refs_per_article(c) -> pd.Series:
    """Number of references of each article that has at least one."""
    return citation_links(c).groupby("id").size().rename("references")


def citation_ages(c) -> pd.Series:
    """Citing year minus cited year, for citations with a valid cited year."""
    links = citation_links(c)
    ok = (links["cited_year"] >= 1400) & (links["cited_year"] <= links["citing_year"])
    return (links.loc[ok, "citing_year"] - links.loc[ok, "cited_year"]).rename("age")


def cited_author_counts(c) -> pd.Series:
    """Citations received by each cited author (one per citation of a work they wrote)."""
    links = citation_links(c)[["id", "reference"]]
    pairs = links.merge(c.reference_author.drop_duplicates(), on="reference", how="inner")
    return pairs["author"].value_counts().rename("citations")


def author_names(c) -> dict:
    """Author ID -> name, from both author tables."""
    names = dict(zip(c.reference_authors["author"], c.reference_authors["name"]))
    names.update(zip(c.article_authors["author"], c.article_authors["name"]))
    return names


def article_author_productivity(c) -> pd.Series:
    """Lotka's table for the journal's own authors: how many wrote k articles."""
    pairs = c.article_author[c.article_author["id"].isin(c.articles["id"])]
    return stats.productivity(pairs.rename(columns={"id": "article"}))


def normalise_venue(text: str) -> str:
    """Squeeze spaces, strip outer punctuation and fold case: 'AIB  Studi.' -> 'aib studi'."""
    return " ".join(text.split()).strip(" .,;:").casefold()


def venue_counts(c) -> pd.Series:
    """Citations to each venue named in «guillemets»."""
    links = citation_links(c)[["id", "reference"]]
    content = links.merge(c.references[["reference", "content"]].drop_duplicates("reference"), on="reference")
    venues = content["content"].str.findall(VENUE).explode().dropna().map(normalise_venue)
    return venues[venues != ""].value_counts().rename("citations")
