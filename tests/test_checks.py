"""The checks pass right answers, flag wrong ones, and never raise."""

import numpy as np
import pandas as pd

from course import bibliothecae as bib
from course import data, stats
from course.checking import RESULTS
from course.checks.draft import s1_1, s1_2, s1_3, s1_4


def status(lesson, n):
    return RESULTS[f"{lesson}/{n}"]["status"]


def test_s1_1_right_wrong_and_todo(capsys):
    x = data.reference_counts()
    s1_1.ex1(x.mean(), np.median(x), np.mean(x > x.mean()))
    assert status("S1.1", 1) == "pass"
    s1_1.ex1(np.median(x), np.median(x), 36)
    assert status("S1.1", 1) == "fail"
    assert "that is the median" in capsys.readouterr().out
    s1_1.ex1(..., ..., ...)
    assert status("S1.1", 1) == "todo"
    s1_1.ex1(x.mean(), ..., ...)
    assert status("S1.1", 1) == "partial"


def test_function_exercises_handle_unfinished_and_crashing_code():
    def unfinished(x):
        ...

    def crashing(x):
        raise KeyError("boom")

    s1_1.ex4(unfinished)
    assert status("S1.1", 4) == "todo"
    s1_1.ex4(crashing)
    assert status("S1.1", 4) == "fail"
    s1_1.ex4(stats.ccdf)
    assert status("S1.1", 4) == "pass"


def test_check_never_raises_on_odd_types():
    s1_1.ex3("78", [30])
    assert status("S1.1", 3) == "fail"
    s1_2.ex4(pd.DataFrame(), 3)
    assert status("S1.2", 4) == "fail"


def test_s1_2_gini_and_simpson():
    s1_2.ex2(stats.gini)
    assert status("S1.2", 2) == "pass"
    oa = data.oa_articles()
    long = oa.groupby(["field", "oa"])["citations"].mean()
    s1_2.ex4(oa.groupby("oa")["citations"].mean(), long)  # long format is accepted too
    assert status("S1.2", 4) == "pass"


def test_s1_3_selected():
    s1_3.ex4(stats.alpha_mle)
    assert status("S1.3", 4) == "pass"
    s1_3.ex7(stats.bradford_zones)
    assert status("S1.3", 7) == "pass"


def test_s1_4_on_demo_corpus():
    c = data.demo_corpus()
    r = bib.refs_per_article(c)
    s1_4.ex1(c, r, r.median())
    assert status("S1.4", 1) == "pass"
    v = bib.venue_counts(c)
    s1_4.ex6(c, v, stats.bradford_zones(v))
    assert status("S1.4", 6) == "pass"


def test_progress_lists_every_exercise():
    table = s1_3.summary()
    assert table["exercise"].tolist() == list(range(1, 10))


def test_scaffolds_with_placeholders_count_as_not_attempted():
    def bradford(counts, n_zones=3):
        c = np.sort(np.asarray(counts))[::-1]
        before = ...
        zone = ...
        return np.bincount(zone, minlength=n_zones)

    s1_3.ex7(bradford)
    assert status("S1.3", 7) == "todo"

    def ccdf(x):
        values = ...
        shares = ...
        return values, shares

    s1_1.ex4(ccdf)
    assert status("S1.1", 4) == "todo"

    def price_model(n_papers=2000, m=3, a=1.0, seed=0):
        rng = np.random.default_rng(seed)
        cites = np.zeros(n_papers, dtype=int)
        for t in range(m, n_papers):
            weights = ...
            p = weights / weights.sum()
            cites[rng.choice(t, size=m, replace=False, p=p)] += 1
        return cites

    s1_3.ex1(price_model)
    assert status("S1.3", 1) == "todo"
