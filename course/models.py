"""Simulations of how bibliographic distributions arise."""

from __future__ import annotations

import numpy as np

__all__ = ["price", "uniform_attachment"]


def price(n_papers: int = 5000, m: int = 3, a: float = 1.0, seed=None) -> np.ndarray:
    """Price's (1976) cumulative-advantage model of citation.

    Papers arrive one at a time. Each new paper cites m distinct earlier
    papers, choosing paper i with probability proportional to c_i + a, where
    c_i is the number of citations paper i has so far. Returns the final
    citation count of every paper, oldest first.

    For large networks the citation distribution has a power-law tail with
    exponent alpha = 2 + a / m.

    This version is fast: it keeps one "ticket" per citation received, so a
    paper can be drawn in proportion to c_i by drawing a random ticket, and in
    proportion to a by drawing a paper uniformly.
    """
    rng = np.random.default_rng(seed)
    cites = np.zeros(n_papers, dtype=int)
    tickets: list[int] = []
    for t in range(m, n_papers):
        total = len(tickets)
        chosen: set[int] = set()
        while len(chosen) < m:
            if rng.random() * (total + a * t) < total:
                chosen.add(tickets[int(rng.integers(total))])
            else:
                chosen.add(int(rng.integers(t)))
        for j in chosen:
            cites[j] += 1
            tickets.append(j)
    return cites


def uniform_attachment(n_papers: int = 5000, m: int = 3, seed=None) -> np.ndarray:
    """Like price(), but every earlier paper is equally likely to be cited."""
    rng = np.random.default_rng(seed)
    cites = np.zeros(n_papers, dtype=int)
    for t in range(m, n_papers):
        cites[rng.choice(t, size=m, replace=False)] += 1
    return cites
