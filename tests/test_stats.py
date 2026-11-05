"""Tests for the reference statistics and simulations."""

import numpy as np
import pandas as pd
import pytest

from course import data, models, stats


def test_ccdf_small_example():
    values, shares = stats.ccdf([1, 1, 2, 5])
    assert values.tolist() == [1, 2, 5]
    assert shares.tolist() == [1.0, 0.5, 0.25]


def test_ecdf_ends_at_one():
    _, f = stats.ecdf([3, 1, 2])
    assert f[-1] == 1.0


@pytest.mark.parametrize("values, expected", [
    ([1, 1, 1, 1], 0.0),
    ([0, 0, 0, 1], 0.75),
    ([1, 2, 3, 4, 5], 4 / 15),
])
def test_gini_known_values(values, expected):
    assert stats.gini(values) == pytest.approx(expected)


def test_gini_matches_mean_absolute_difference():
    x = np.random.default_rng(0).lognormal(0, 1, 300)
    mad = np.abs(x[:, None] - x[None, :]).mean()
    assert stats.gini(x) == pytest.approx(mad / (2 * x.mean()))


def test_lorenz_endpoints():
    pop, share = stats.lorenz([5, 1, 3])
    assert (pop[0], share[0], pop[-1], share[-1]) == (0, 0, 1, 1)


def test_top_share():
    assert stats.top_share(np.arange(1, 11), 0.1) == pytest.approx(10 / 55)


def test_power_law_round_trip():
    x = stats.sample_power_law(50_000, 2.5, 2.0, rng=1)
    assert x.min() >= 2.0
    assert stats.alpha_mle(x, 2.0) == pytest.approx(2.5, abs=0.03)


def test_lotka_share():
    assert stats.lotka_share_single(2.0) == pytest.approx(6 / np.pi ** 2, abs=1e-4)


def test_bradford_zones_toy():
    assert stats.bradford_zones([10, 5, 5, 3, 2, 2, 1, 1, 1]).tolist() == [1, 2, 6]
    assert stats.bradford_zones([4, 4, 4]).sum() == 3


def test_productivity_counts_each_pair_once():
    au = pd.DataFrame({"article": ["a", "a", "b", "c"], "author": ["x", "x", "x", "y"]})
    assert stats.productivity(au).to_dict() == {1: 1, 2: 1}


def test_tokenize_splits_elisions():
    assert stats.tokenize("Nel mezzo del cammin, l’amor che move!") == \
        ["nel", "mezzo", "del", "cammin", "l", "amor", "che", "move"]


def test_year_of():
    assert stats.year_of(["2017", "s.d.", "c. 1550-1560"]).tolist()[::2] == [2017.0, 1550.0]


def test_price_model_totals():
    c = models.price(n_papers=1000, m=3, a=1.0, seed=0)
    assert c.sum() == 3 * (1000 - 3)
    assert stats.gini(c) > stats.gini(models.uniform_attachment(1000, 3, seed=0))


def test_datasets_are_stable():
    assert data.reference_counts().size == 300
    assert data.citation_counts().size == 5000
    assert data.citation_counts().sum() == 10 * (5000 - 10)
    oa = data.oa_articles()
    overall = oa.groupby("oa")["citations"].mean()
    by_field = oa.groupby(["field", "oa"])["citations"].mean().unstack()
    assert overall[True] > overall[False]
    assert (by_field[True] < by_field[False]).all()  # Simpson's paradox holds


def test_commedia():
    text = data.commedia(headings=True)
    assert text.count(" · CANTO ") == 100
    assert text.startswith("INFERNO · CANTO I\n")
    assert "Gutenberg" not in text
    assert " · CANTO " not in data.commedia()
