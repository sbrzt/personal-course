"""Datasets for the lessons.

The Bibliothecae.it tables and the text of the Commedia ship with the package.
Simulated datasets are seeded, so everyone gets the same numbers.
"""

from __future__ import annotations

import functools
import io
import os
import zipfile
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

import numpy as np
import pandas as pd

from . import models

__all__ = [
    "reference_counts", "citation_counts", "refs_and_cites", "oa_articles",
    "authorship", "journal_counts", "commedia", "bibliothecae", "Corpus", "demo_corpus",
]


# Simulated datasets ------------------------------------------------------------------

def reference_counts() -> np.ndarray:
    """Number of references in each of the 300 articles of a simulated humanities journal."""
    rng = np.random.default_rng(3)
    return np.maximum(1, np.round(rng.lognormal(np.log(30), 0.7, 300))).astype(int)


@functools.lru_cache(maxsize=None)
def _citations() -> np.ndarray:
    return models.price(n_papers=5000, m=10, a=8.0, seed=1976)


def citation_counts() -> np.ndarray:
    """Citations received by 5,000 papers of a simulated field, oldest paper first.

    Generated with Price's cumulative-advantage model (lesson S1.3): every
    paper cites 10 earlier papers, preferring those already cited.
    """
    return _citations().copy()


def refs_and_cites() -> pd.DataFrame:
    """References given and citations received by 401 simulated articles.

    The last row is a long review article.
    """
    rng = np.random.default_rng(1)
    n = 400
    refs = np.maximum(1, np.round(rng.lognormal(np.log(30), 0.6, n))).astype(int)
    mu = np.exp(0.6 + 0.45 * np.log(refs))
    cites = rng.negative_binomial(1.2, 1.2 / (1.2 + mu))
    df = pd.DataFrame({"references": refs, "citations": cites, "type": "article"})
    review = pd.DataFrame({"references": [640], "citations": [1450], "type": ["review"]})
    return pd.concat([df, review], ignore_index=True)


def oa_articles() -> pd.DataFrame:
    """Field, open-access status and citations of 2,400 simulated articles.

    Constructed to show Simpson's paradox; it is not real evidence about open access.
    """
    rng = np.random.default_rng(3)
    spec = {
        "Humanities": dict(n=1200, p_oa=0.25, mu_oa=2.6, mu_closed=3.0, k=0.9),
        "Life sciences": dict(n=1200, p_oa=0.75, mu_oa=21.0, mu_closed=24.0, k=1.1),
    }
    parts = []
    for name, s in spec.items():
        is_oa = rng.random(s["n"]) < s["p_oa"]
        mu = np.where(is_oa, s["mu_oa"], s["mu_closed"])
        cites = rng.negative_binomial(s["k"], s["k"] / (s["k"] + mu))
        parts.append(pd.DataFrame({"field": name, "oa": is_oa, "citations": cites}))
    return pd.concat(parts, ignore_index=True)


def authorship() -> pd.DataFrame:
    """Simulated (article, author) pairs for a journal, one row per authorship."""
    rng = np.random.default_rng(1926)
    k = np.arange(1, 61)
    prod = rng.choice(k, size=800, p=k ** -2.0 / np.sum(k ** -2.0))
    slots = np.repeat(np.arange(800), prod)
    rng.shuffle(slots)
    sizes = rng.choice([1, 2, 3, 4], size=len(slots), p=[0.70, 0.20, 0.07, 0.03])
    ends = np.cumsum(sizes)
    ends = ends[ends < len(slots)]
    article = np.zeros(len(slots), dtype=int)
    article[ends] = 1
    article = np.cumsum(article)
    df = pd.DataFrame({"article": [f"art{a + 1:04d}" for a in article],
                       "author": [f"auth{a + 1:03d}" for a in slots]})
    return df.drop_duplicates().reset_index(drop=True)


def journal_counts() -> pd.Series:
    """Articles on one topic found in each of 250 simulated journals (for Bradford's law)."""
    rng = np.random.default_rng(1934)
    r = np.arange(1, 251)
    counts = np.maximum(1, np.round(400 / r * rng.lognormal(0, 0.25, r.size))).astype(int)
    counts = np.sort(counts)[::-1]
    names = [f"Journal {i:03d}" for i in rng.permutation(r)]
    return pd.Series(counts, index=pd.Index(names, name="journal"), name="articles")


# Text ----------------------------------------------------------------------------------

def commedia(headings: bool = False) -> str:
    """Dante Alighieri, *La Divina Commedia* (public domain).

    Lines such as "INFERNO · CANTO I" mark the cantos; they are removed unless
    headings=True.
    """
    text = resources.files("course").joinpath("resources/commedia.txt").read_text(encoding="utf-8")
    if headings:
        return text
    return "\n".join(line for line in text.splitlines() if " · CANTO " not in line)


# Bibliothecae.it -------------------------------------------------------------------------

TABLES = {
    "articles": "articles.csv",
    "article_authors": "article_authors.csv",
    "references": "references.csv",
    "reference_authors": "reference_authors.csv",
    "article_author": "relations_article_author.csv",
    "article_reference": "relations_article_reference.csv",
    "reference_author": "relations_reference_author.csv",
}

@dataclass
class Corpus:
    """The Bibliothecae.it tables, as pandas DataFrames of strings."""

    articles: pd.DataFrame
    article_authors: pd.DataFrame
    references: pd.DataFrame
    reference_authors: pd.DataFrame
    article_author: pd.DataFrame
    article_reference: pd.DataFrame
    reference_author: pd.DataFrame
    source: str = ""
    demo: bool = False
    notes: list = field(default_factory=list)

    def __repr__(self) -> str:
        sizes = ", ".join(f"{k}={len(getattr(self, k)):,}" for k in TABLES)
        kind = "DEMO (simulated)" if self.demo else "Bibliothecae.it"
        return f"Corpus[{kind}] from {self.source}\n  {sizes}"


def _read_csv(data) -> pd.DataFrame:
    return pd.read_csv(data, dtype=str, keep_default_na=False)


def _from_dir(folder: Path) -> Corpus | None:
    hits = sorted(folder.glob("**/articles.csv"))
    if not hits:
        return None
    base = hits[0].parent
    if not all((base / f).exists() for f in TABLES.values()):
        return None
    tables = {k: _read_csv(base / f) for k, f in TABLES.items()}
    return Corpus(**tables, source=str(base))


def _from_zip(path: Path) -> Corpus | None:
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith("articles.csv") and "__MACOSX" not in n]
        if not names:
            return None
        prefix = names[0][: -len("articles.csv")]
        tables = {}
        for key, f in TABLES.items():
            if prefix + f not in z.namelist():
                return None
            tables[key] = _read_csv(io.BytesIO(z.read(prefix + f)))
    return Corpus(**tables, source=str(path))


@functools.lru_cache(maxsize=1)
def _bundled_tables() -> dict:
    folder = resources.files("course").joinpath("resources/bibliothecae")
    return {k: _read_csv(io.BytesIO(folder.joinpath(f).read_bytes())) for k, f in TABLES.items()}


def bibliothecae(path=None) -> Corpus:
    """Load the Bibliothecae.it tables.

    By default this is the copy that ships with the course, in
    course/resources/bibliothecae/ (see the README there). To load another
    version, pass a folder of CSVs or a zip as `path`, or set the environment
    variable BIBLIOTHECAE_DATA. Each call returns fresh copies of the tables, so
    changing one in a notebook never changes what the next call returns.
    """
    target = path or os.environ.get("BIBLIOTHECAE_DATA")
    if target:
        p = Path(target)
        corpus = _from_dir(p) if p.is_dir() else _from_zip(p) if p.suffix == ".zip" else None
        if corpus is None:
            raise FileNotFoundError(f"no Bibliothecae.it tables found in {p}")
        return corpus
    tables = {k: v.copy() for k, v in _bundled_tables().items()}
    return Corpus(**tables, source="the copy bundled with the course")


# A simulated corpus with the same columns as the real one ----------------------------------

_SYL = ["ber", "to", "li", "ca", "na", "ri", "mon", "tel", "ghi", "ra", "si", "fa",
        "lo", "ve", "ro", "mar", "chi", "ni", "gal", "pe", "sa", "bru", "del", "co"]
_END = ["ni", "lli", "tti", "ri", "si", "ghi", "ne"]
_FIRST = ["Anna", "Paolo", "Maria", "Luca", "Giulia", "Marco", "Elena", "Andrea",
          "Chiara", "Giorgio", "Laura", "Stefano", "Silvia", "Franco", "Rita", "Alberto"]
_WORDS = ["biblioteca", "libro", "catalogo", "manoscritto", "edizione", "stampa",
          "lettura", "collezione", "archivio", "inventario", "tipografia", "lettori"]
_TOPICS = ["bibliografia", "biblioteconomia", "storia del libro", "filologia", "archivistica",
           "storia della stampa", "paleografia", "codicologia", "studi umanistici", "cultura",
           "letteratura", "storia", "erudizione", "informazione", "documentazione"]
_FORMS = ["Rivista di", "Annali di", "Bollettino di", "Quaderni di", "Studi di",
          "Archivio di", "Giornale di", "Nuova rivista di", "Atti di", "Miscellanea di"]
_CITIES = [("Firenze", "Olschki"), ("Milano", "Bibliografica"), ("Roma", "AIB"),
           ("Bologna", "il Mulino"), ("Torino", "Einaudi"), ("Venezia", "Marsilio")]


def _surname(rng) -> str:
    stem = "".join(rng.choice(_SYL, size=int(rng.integers(1, 3))))
    return (stem + rng.choice(_END) + rng.choice(["i", "o", "a"])).capitalize()


def _zipf_weights(n: int, s: float) -> np.ndarray:
    w = np.arange(1, n + 1, dtype=float) ** -s
    return w / w.sum()


@functools.lru_cache(maxsize=None)
def _demo_tables() -> dict:
    rng = np.random.default_rng(2012)
    # articles: 300 articles, 2012-2025
    years = np.sort(rng.integers(2012, 2026, size=300))
    art_ids = [f"Q9{100000 + i}" for i in range(300)]
    articles = pd.DataFrame({
        "id": art_ids,
        "doi": [f"10.0000/DEMO.{i + 1}" for i in range(300)],
        "label": [f"Articolo dimostrativo {i + 1}" for i in range(300)],
        "date": [f"{y}-07-01T00:00:00Z" for y in years],
        "langLabel": rng.choice(["Italian", "English"], size=300, p=[0.85, 0.15]),
        "pages": "", "volume": (years - 2011).astype(str), "issue": "1",
        "keywords": ["; ".join(rng.choice(_WORDS, size=2, replace=False)) for _ in range(300)],
        "section": rng.choice(["Essays", "Documentation", "Notes and discussions"], size=300),
        "abstract": "",
    })
    # article authors: one prolific founder-editor, many one-off contributors
    n_people = 400
    auth_ids = [f"Q8{100000 + i}" for i in range(n_people)]
    people = [f"{rng.choice(_FIRST)} {_surname(rng)}" for _ in range(n_people)]
    w_people = _zipf_weights(n_people - 1, 0.35)
    pairs = []
    for a in art_ids:
        if rng.random() < 0.16:
            pairs.append((a, auth_ids[0]))
        else:
            k = 1 if rng.random() < 0.85 else 2
            for j in rng.choice(np.arange(1, n_people), size=k, replace=False, p=w_people):
                pairs.append((a, auth_ids[j]))
    article_author = pd.DataFrame(pairs, columns=["id", "author"]).drop_duplicates()
    used = article_author["author"].unique()
    known = used[rng.random(used.size) < 0.65]
    name_of = dict(zip(auth_ids, people))
    article_authors = pd.DataFrame({
        "author": known, "name": [name_of[a] for a in known],
        "sex": rng.choice(["female", "male"], size=known.size),
        "affiliations": rng.choice(["University of Bologna", "University of Rome", "University of Pisa"],
                                   size=known.size),
    })
    # cited authors and journals, with long flat tails
    n_cited = 9000
    cited_ids = [f"AUTH{i + 1:04d}" for i in range(n_cited)]
    cited_names = [f"{rng.choice(_FIRST)} {_surname(rng)}" for _ in range(n_cited)]
    w_cited = _zipf_weights(n_cited, 0.55)
    journals = [f"{f} {t}" for f in _FORMS for t in _TOPICS]
    while len(journals) < 3000:
        journals.append(f"{rng.choice(_FORMS)} {rng.choice(_TOPICS)} {_surname(rng)}")
    journals = list(dict.fromkeys(journals))
    rng.shuffle(journals)
    w_j = _zipf_weights(len(journals), 0.6)
    # references: none before 2016, as in the real data
    refs, art_ref, ref_auth = [], [], []
    r = 0
    for a, y in zip(art_ids, years):
        if y < 2016:
            continue
        n_refs = int(np.clip(np.round(rng.lognormal(np.log(31), 0.75)), 1, 250))
        for _ in range(n_refs):
            r += 1
            rid = f"REF{r:05d}"
            u = rng.random()
            if u < 0.10:
                cy = str(int(rng.integers(1450, 1900)))
            elif u < 0.16:
                cy = ""                                          # date missing
            elif u < 0.17:
                cy = str(int(rng.choice([1023, 1201, y + 7, 2999])))  # impossible years
            else:
                cy = str(int(y - min(120, np.floor(rng.lognormal(np.log(17), 0.9)))))
            if rng.random() < 0.015:
                who, names = [auth_ids[0]], [name_of[auth_ids[0]]]
            else:
                k = 1 if rng.random() < 0.8 else 2
                idx = rng.choice(n_cited, size=k, replace=False, p=w_cited)
                who = [cited_ids[i] for i in idx]
                names = [cited_names[i] for i in idx]
            title = f"{rng.choice(_WORDS).capitalize()} e {rng.choice(_WORDS)}"
            year_txt = cy or "s.d."
            if rng.random() < 0.25:
                venue = journals[rng.choice(len(journals), p=w_j)]
                content = f"{' - '.join(names)}, {title}, «{venue}», {year_txt}"
            else:
                city, pub = _CITIES[rng.integers(len(_CITIES))]
                content = f"{' - '.join(names)}, {title}, {city}, {pub}, {year_txt}"
            refs.append((rid, content, "; ".join(names), cy))
            art_ref.append((a, rid))
            ref_auth.extend((rid, w) for w in who)
    references = pd.DataFrame(refs, columns=["reference", "content", "author", "date"])
    reference_authors = pd.DataFrame({"author": cited_ids, "name": cited_names})
    return dict(
        articles=articles, article_authors=article_authors, references=references,
        reference_authors=reference_authors, article_author=article_author,
        article_reference=pd.DataFrame(art_ref, columns=["id", "reference"]),
        reference_author=pd.DataFrame(ref_auth, columns=["reference", "author"]),
    )


def demo_corpus() -> Corpus:
    """A simulated corpus with the same tables and columns as the Bibliothecae.it data."""
    tables = {k: v.copy() for k, v in _demo_tables().items()}
    return Corpus(**tables, source="simulated stand-in (course.data.demo_corpus)", demo=True)
