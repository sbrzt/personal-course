"""Tests for the rewritten Phase S: bundled data, sliders and the S0.1 checks."""

import numpy as np

from course import data, widgets
from course.checking import RESULTS
from course.checks import s0_1


def status(lesson, n):
    return RESULTS[f"{lesson}/{n}"]["status"]


def test_bundled_bibliothecae_tables():
    bib = data.bibliothecae()
    assert len(bib.articles) == 321
    assert len(bib.references) == 7507
    assert not bib.demo
    bib.articles.loc[0, "label"] = "changed"
    assert data.bibliothecae().articles.loc[0, "label"] != "changed"  # fresh copies


def test_explore_runs_once_when_static(monkeypatch):
    monkeypatch.setenv("COURSE_STATIC", "1")
    calls = []
    widgets.explore(lambda k, s: calls.append((k, s)), k=(1, 10, 1, 3), s=(0.0, 1.0, 0.1, 0.5, "share"))
    assert calls == [(3, 0.5)]


def test_s0_1_six_essays():
    assert s0_1.six_essays().tolist() == [170, 53, 10, 102, 22, 13]


def test_s0_1_right_answers_pass():
    x = s0_1.six_essays()
    n = len(x)
    s0_1.ex1(x[2], x[-1], np.argmax(x) + 1)
    s0_1.ex2(x.sum(), (x ** 2).sum(), x.sum() ** 2, (x - 50).sum())
    s0_1.ex3("B")
    s0_1.ex4(np.prod([0.5, 0.2, 0.9, 0.4]), np.prod(x[:3]))
    m = x.mean()
    s0_1.ex5(m, x - m, (x - m) ** 2, ((x - m) ** 2).sum(), np.sqrt(((x - m) ** 2).sum() / (n - 1)))
    bib = data.bibliothecae()
    c = bib.article_reference.drop_duplicates().groupby("id").size()
    s0_1.ex6(len(c), (c >= 50).sum(), (c >= 50).mean())
    year = bib.articles["date"].str[:4].astype(int)
    has = bib.articles["abstract"] != ""
    old, new = has[year <= 2018].mean(), has[year > 2018].mean()
    s0_1.ex7(old, new, 100 * (new - old), 100 * (new - old) / old)
    assert [status("S0.1", k) for k in range(1, 8)] == ["pass"] * 7


def test_s0_1_typical_mistakes_get_hints(capsys):
    x = s0_1.six_essays()
    s0_1.ex1(x[3], x[-1], np.argmax(x))
    out = capsys.readouterr().out
    assert status("S0.1", 1) == "fail"
    assert "Python counts positions from 0" in out and "add 1" in out
    s0_1.ex2(x.sum(), x.sum() ** 2, (x ** 2).sum(), x.sum() - 50)
    out = capsys.readouterr().out
    assert "square each value first" in out and "six times" in out
    s0_1.ex3("a")
    assert status("S0.1", 3) == "fail"
    s0_1.ex7(..., ..., ..., ...)
    assert status("S0.1", 7) == "todo"
