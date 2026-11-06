"""Tests for the rewritten Phase S: bundled data, sliders and the S0.1 checks."""

import numpy as np

from course import data, widgets
from course.checking import RESULTS
from course.checks import s0_1, s0_2


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


def test_s0_2_known_numbers():
    p_line, p_canto = s0_2.canto_chances()
    assert len(p_line) == 7 and len(p_canto) == 993
    assert np.prod(p_canto) == 0.0
    assert round(np.log10(p_canto).sum()) == -2947
    d = s0_2.cited_decades()
    assert (d[1950], d[2010]) == (131, 1766)
    assert s0_2.corpus_sizes().tolist() == [30, 321, 4036, 7507, 101603, 529896]


def test_s0_2_right_answers_pass():
    s0_2.ex1(2 ** 10, 10 ** -3, 81 ** (1 / 2), 1000 ** (1 / 3), 440 * 2 ** (7 / 12))
    t = np.arange(0, 31)
    added, multiplied = 1000 + 500 * t, 1000 * 1.2 ** t
    s0_2.ex2(added, multiplied, t[multiplied > added][0])
    s0_2.ex3(np.log10(10_000), np.log2(1 / 8), np.log(np.exp(5)), np.log(81) / np.log(3),
             np.ceil(np.log2(321)))
    s0_2.ex4("ACEF")
    p_line, p_canto = s0_2.canto_chances()
    s0_2.ex5(np.prod(p_line), np.prod(p_canto), np.log10(p_canto).sum())
    logs = np.log10(s0_2.corpus_sizes())
    s0_2.ex6(logs, np.floor(logs), logs["words of the Commedia"] - logs["references, median article"])
    s0_2.ex7(10 ** 2.5, 10 ** ((np.log10(20) + np.log10(80)) / 2), (20 + 80) / 2)
    d = s0_2.cited_decades()
    f = d[2010] / d[1950]
    s0_2.ex8(f, f ** (1 / 60), np.log(2) / np.log(f ** (1 / 60)))
    assert [status("S0.2", k) for k in range(1, 9)] == ["pass"] * 8


def test_s0_2_typical_mistakes_get_hints(capsys):
    s0_2.ex1(2 ^ 10, 10 ** -3, 81 ** 1 / 2, 1000 ** 1 / 3, 440 * 2 ** 7 / 12)
    out = capsys.readouterr().out
    assert "use **" in out and "brackets" in out
    t = np.arange(0, 31)
    s0_2.ex2(1000 + 500 * t, 1000 * 0.2 ** t, 0)
    out = capsys.readouterr().out
    assert "1.2, not 0.2" in out and "more (>)" in out
    s0_2.ex3(np.log(10_000), 3, 5, 4, np.log2(321))
    out = capsys.readouterr().out
    assert "natural log" in out and "negative" in out and "round up" in out
    s0_2.ex4("AB")
    out = capsys.readouterr().out
    assert status("S0.2", 4) == "fail" and "no rule for the log of a sum" in out
    p_line, p_canto = s0_2.canto_chances()
    with np.errstate(divide="ignore"):
        s0_2.ex5(np.prod(p_line), np.prod(p_canto), np.log10(np.prod(p_canto)))
    assert "log of 0.0" in capsys.readouterr().out
    s0_2.ex6(np.log10(s0_2.corpus_sizes()), np.round(np.log10(s0_2.corpus_sizes())), 4)
    out = capsys.readouterr().out
    assert "np.floor" in out and "rounded orders" in out
    s0_2.ex8(..., ..., ...)
    assert status("S0.2", 8) == "todo"
