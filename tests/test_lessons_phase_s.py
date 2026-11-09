"""Tests for the rewritten Phase S: bundled data, sliders and the lesson checks."""

import numpy as np
import pandas as pd

from course import data, stats, widgets
from course.checking import RESULTS
from course.checks import s0_1, s0_2, s0_3, s1_1, s1_2, s1_3


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


def test_s0_3_known_numbers():
    f = s0_3.zipf_counts()
    assert (f[9], f[999]) == (1100, 10)
    s = s0_3.journal_so_far()
    assert (s[2012], s[2013], s[2024]) == (9, 32, 314)


def test_s0_3_right_answers_pass():
    s0_3.ex1(lambda p: 2 + 0.35 * p, np.floor((20 - 2) / 0.35))
    s0_3.ex2(-2, 9, -11)
    s = s0_3.journal_so_far()
    b = (s[2024] - s[2013]) / 11
    s0_3.ex3(b, s[2013] - b, s[2013] - b + 18 * b)
    s0_3.ex4("LPEPEP")
    k = (np.log10(5) - np.log10(500)) / (np.log10(1000) - np.log10(10))
    s0_3.ex5(k, 500 / 10 ** k, 500 / 10 ** k * 100 ** k)
    f = s0_3.zipf_counts()
    s0_3.ex6(f[9] / f[999], 100, np.log10(f[9] / f[999]) / 2)
    x, curves = s0_3.mystery_curves()
    y = curves["A"]
    s0_3.ex7("PLE", (np.log10(y[-1]) - np.log10(y[0])) / (np.log10(x[-1]) - np.log10(x[0])))
    assert [status("S0.3", k) for k in range(1, 8)] == ["pass"] * 7


def test_s0_3_typical_mistakes_get_hints(capsys):
    def unfinished(pages):
        return ...
    s0_3.ex1(unfinished, ...)
    assert status("S0.3", 1) == "todo"
    s0_3.ex1(lambda p: 2 * 0.35 * p, 18 / 0.35)
    out = capsys.readouterr().out
    assert "don't multiply" in out and "round down" in out
    s0_3.ex2(2, 5, -20)
    out = capsys.readouterr().out
    assert "same order" in out and "y minus slope" in out
    s0_3.ex4("LPEEEP")
    assert "x to the power −1" in capsys.readouterr().out
    s0_3.ex4(42)
    assert status("S0.3", 4) == "fail"
    f = s0_3.zipf_counts()
    s0_3.ex6(f[10] / f[1000], 100, 1.1)
    assert "counts from 0" in capsys.readouterr().out
    s0_3.ex7("PEL", 0.75)
    out = capsys.readouterr().out
    assert "not straight on semi-log" in out and "negative" in out


def test_s1_1_known_numbers():
    assert s1_1.page_counts().sum() == 9045
    kw = s1_1.keyword_pairs()
    assert (len(kw), kw.nunique(), kw.value_counts().index[0]) == (1062, 515, "library history")


def test_s1_1_right_answers_pass():
    bib = data.bibliothecae()
    t = bib.article_reference
    s1_1.ex1(len(t), len(t.drop_duplicates()), t["id"].nunique())
    s1_1.ex2("NIORNRRO")
    vol = bib.articles["volume"]
    pc = s1_1.page_counts()
    s1_1.ex3(vol.max(), vol.astype(int).max(), pc, pc.sum())
    kw = s1_1.keyword_pairs()
    s1_1.ex4(len(kw), kw.nunique(), kw.value_counts().index[0])
    s1_1.ex5("PSSP")
    r = bib.references
    y = pd.to_numeric(r["date"], errors="coerce")
    miss, bad = (r["date"] == "").sum(), ((y < 1400) | (y > 2025)).sum()
    s1_1.ex6(miss, bad, (miss + bad) / len(r))
    no_year, has_author = r["date"] == "", r["author"] != ""
    w, wo = no_year[has_author].mean(), no_year[~has_author].mean()
    s1_1.ex7(w, wo, wo / w)
    assert [status("S1.1", k) for k in range(1, 8)] == ["pass"] * 7
    assert (miss, bad) == (503, 403)


def test_s1_1_typical_mistakes_get_hints(capsys):
    bib = data.bibliothecae()
    pc = s1_1.page_counts()
    s1_1.ex3(14, 9, pc - 1, pc.sum() - len(pc))
    out = capsys.readouterr().out
    assert "before any conversion" in out and "add 1" in out and "one page short" in out
    s1_1.ex2("NIORNRRR")
    assert "H, first or second issue" in capsys.readouterr().out
    s1_1.ex4(1062, 514, "Library history")
    assert status("S1.1", 4) == "pass"
    s1_1.ex4(1062, 515, 98)
    assert "the keyword itself" in capsys.readouterr().out
    s1_1.ex5("PPPP")
    assert status("S1.1", 5) == "fail"
    r = bib.references
    no_year, has_author = r["date"] == "", r["author"] != ""
    w, wo = no_year[has_author].mean(), no_year[~has_author].mean()
    s1_1.ex7(wo, w, w / wo)
    out = capsys.readouterr().out
    assert "swapped" in out and "larger share" in out
    s1_1.ex6(..., ..., ...)
    assert status("S1.1", 6) == "todo"


def test_s1_2_known_numbers():
    t = s1_2.reference_types().value_counts()
    assert t.to_dict() == {"book or other": 3994, "periodical": 1812, "chapter": 1378, "web": 323}
    bp = s1_2.type_by_period()
    assert round(bp.loc["chapter", "2021-2025"] - bp.loc["chapter", "2016-2020"], 2) == 3.01


def test_s1_2_right_answers_pass():
    bib = data.bibliothecae()
    s = bib.articles["section"]
    s1_2.ex1(s.value_counts(), s.value_counts(normalize=True), s.value_counts(normalize=True).iloc[:3].sum())
    y = s1_2.years()
    py = y.value_counts().sort_index()
    cs = py.cumsum() / py.sum()
    s1_2.ex2(py, cs, cs[cs >= 0.5].index[0])
    pc = s1_2.page_counts()
    s1_2.ex3(y.value_counts().idxmax(), y.value_counts().max(), pc.value_counts().idxmax(), pc.value_counts().max())
    period = pd.Series(np.where(y <= 2018, "2012-2018", "2019-2025"), index=y.index, name="period")
    table = pd.crosstab(s, period, margins=True)
    s1_2.ex4(table, table.loc["Essays", "2019-2025"], table.loc["All", "2019-2025"])
    essay, other = s == "Essays", bib.articles["langLabel"] != "Italian"
    s1_2.ex5(essay[other].mean(), other[essay].mean(), essay[~other].mean())
    t = s1_2.reference_types()
    bp = s1_2.type_by_period()
    e, l = bp.loc["chapter", "2016-2020"], bp.loc["chapter", "2021-2025"]
    s1_2.ex6(t.value_counts(normalize=True)["web"], e, l, l - e)
    assert [status("S1.2", k) for k in range(1, 7)] == ["pass"] * 6
    assert (cs[cs >= 0.5].index[0], y.value_counts().idxmax(), pc.value_counts().idxmax()) == (2019, 2020, 6)


def test_s1_2_typical_mistakes_get_hints(capsys):
    bib = data.bibliothecae()
    s = bib.articles["section"]
    s1_2.ex1(s.value_counts(normalize=True), s.value_counts(), 286)
    out = capsys.readouterr().out
    assert "these are shares" in out and "these are counts" in out and "divide by the 321" in out
    y = s1_2.years()
    s1_2.ex2(y.value_counts(), y.value_counts().cumsum() / len(y), 2018)
    out = capsys.readouterr().out
    assert "time order" in out and "only" in out
    period = pd.Series(np.where(y <= 2018, "2012-2018", "2019-2025"), index=y.index, name="period")
    s1_2.ex4(pd.crosstab(s, period), 55, 321)
    out = capsys.readouterr().out
    assert "margins=True" in out and "earlier period" in out and "every article" in out
    essay, other = s == "Essays", bib.articles["langLabel"] != "Italian"
    s1_2.ex5(other[essay].mean(), essay[other].mean(), essay[~other].mean())
    assert "other direction" in capsys.readouterr().out
    s1_2.ex6(..., ..., ..., ...)
    assert status("S1.2", 6) == "todo"


def test_s1_3_known_numbers():
    r = s1_3.refs()
    assert (len(r), r.nunique(), r.min(), r.max()) == (201, 76, 1, 234)
    assert np.histogram(r, bins=np.arange(0, 250, 10))[0][:4].tolist() == [25, 37, 32, 38]
    assert r.quantile([0.25, 0.5, 0.75]).tolist() == [16, 30, 48]
    z = s1_3.refs_since_2016()
    assert (len(z), (z == 0).sum()) == (257, 56)
    assert pd.Series(s1_3.WAITS).quantile([0.25, 0.5, 0.75]).tolist() == [8, 12, 20]


def test_s1_3_right_answers_pass():
    r, p = s1_3.refs(), s1_3.page_counts()
    edges = np.arange(0, 250, 10)
    counts = np.histogram(r, bins=edges)[0]
    s1_3.ex1(edges, counts, counts[:2].sum(), edges[counts.argmax()])
    k = int(np.ceil(1 + np.log2(len(r))))
    s1_3.ex2(k, (r.max() - r.min()) / k, int(np.ceil(1 + np.log2(len(p)))))
    uneven = [0, 10, 20, 30, 50, 100, 250]
    c, w = np.histogram(r, bins=uneven)[0], np.diff(uneven)
    d = c / (len(r) * w)
    s1_3.ex3(c, w, d, uneven[d.argmax()])
    s1_3.ex4("right-skewed", "Left skewed", "bimodal")
    q1, q3 = r.quantile(0.25), r.quantile(0.75)
    upper = q3 + 1.5 * (q3 - q1)
    s1_3.ex5(q1, q3, upper, (r > upper).sum())
    values, shares = stats.ecdf(r)
    s1_3.ex6(lambda x, t: np.mean(np.asarray(x) <= t), (r <= 30).mean(), values[shares >= 0.9][0])
    assert [status("S1.3", k) for k in range(1, 7)] == ["pass"] * 6
    assert (edges[counts.argmax()], k, uneven[d.argmax()], upper, values[shares >= 0.9][0]) == (30, 9, 10, 96, 69)


def test_s1_3_typical_mistakes_get_hints(capsys):
    r = s1_3.refs()
    short = np.arange(0, 240, 10)
    s1_3.ex1(short, np.histogram(r, bins=short), (r <= 20).sum(), 38)
    out = capsys.readouterr().out
    assert "stops before" in out and "keep the counts" in out and "exactly 20" in out and "how many" in out
    s1_3.ex2(1 + np.log2(len(r)), r.max() / 9, 9)
    out = capsys.readouterr().out
    assert "round up" in out and "range" in out and "rounds up, not down" in out
    uneven = [0, 10, 20, 30, 50, 100, 250]
    c = np.histogram(r, bins=uneven)[0]
    s1_3.ex3(c, np.diff(uneven), c / len(r), 30)
    out = capsys.readouterr().out
    assert "these are shares" in out and "largest count" in out
    s1_3.ex4("left-skewed", "right skewed", "right-skewed")
    out = capsys.readouterr().out
    assert out.count("named after the side of its tail") == 2 and "bar at zero" in out
    s1_3.ex4("skewed", ..., 3)
    out = capsys.readouterr().out
    assert "write one of" in out and "should be a string" in out
    q1, q3 = r.quantile(0.25), r.quantile(0.75)
    s1_3.ex5(q3, q1, 1.5 * q3, (r >= q3 + 1.5 * (q3 - q1)).sum())
    out = capsys.readouterr().out
    assert "third quartile" in out and "not 1.5 times Q3" in out and "exactly on the fence" in out
    s1_3.ex6(lambda x, t: np.mean(np.asarray(x) < t), (r <= 30).sum(), 0.9)
    out = capsys.readouterr().out
    assert "use <= rather than <" in out and "that is a count" in out and "that is the share" in out


def test_s1_3_unfinished_and_broken_functions_are_handled(capsys):
    def ecdf_at(x, t):
        return ...
    s1_3.ex6(ecdf_at, ..., ...)
    assert status("S1.3", 6) == "todo"
    s1_3.ex6(lambda x, t: 1 / 0, (s1_3.refs() <= 30).mean(), 69)
    out = capsys.readouterr().out
    assert "ZeroDivisionError" in out and status("S1.3", 6) == "fail"


def test_boxplot_helper_draws_sideways_without_warnings():
    import warnings

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from course import plots
    fig, ax = plt.subplots()
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        out = plots.boxplot(ax, [1, 2, 3, 10], widths=0.5)
    assert len(out["boxes"]) == 1
    assert out["boxes"][0].get_path().vertices[:, 0].max() > 2      # the box spans x, not y
    plt.close(fig)
