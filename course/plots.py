"""Plotting helpers with one quiet, consistent style.

Colours: blue, orange and aqua from a colour-blind-checked palette, in that
fixed order. Text stays in neutral ink; gridlines stay faint.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from . import stats

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SERIES = [BLUE, ORANGE, AQUA]
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def use_style():
    """Apply the course style to every following matplotlib figure."""
    mpl.rcParams.update({
        "figure.figsize": (6.4, 4.0),
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titlelocation": "left",
        "axes.labelcolor": INK,
        "axes.edgecolor": INK_2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.prop_cycle": mpl.cycler(color=SERIES),
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "text.color": INK,
        "lines.linewidth": 1.8,
        "legend.frameon": False,
    })


def _ax(ax):
    return ax if ax is not None else plt.subplots()[1]


def ccdf(x, ax=None, label=None, color=None, **kwargs):
    """Plot P(X >= x) on log-log axes (zeros cannot be shown on a log axis and are skipped)."""
    ax = _ax(ax)
    values, p = stats.ccdf(x)
    keep = values > 0
    ax.loglog(values[keep], p[keep], marker="o", markersize=3, linewidth=0,
              label=label, color=color, **kwargs)
    ax.set_xlabel("x")
    ax.set_ylabel("share of observations ≥ x")
    return ax


def lorenz(x, ax=None, label=None, color=None, equality=True):
    """Plot the Lorenz curve of x, by default with the line of perfect equality."""
    ax = _ax(ax)
    pop, share = stats.lorenz(x)
    if equality:
        ax.plot([0, 1], [0, 1], color=INK_2, linewidth=1, linestyle="--", label="perfect equality")
    ax.plot(pop, share, label=label, color=color)
    ax.set_xlabel("share of units, from least to most")
    ax.set_ylabel("share of the total")
    ax.set_aspect("equal")
    return ax


def log_histogram(x, ax=None, bins=30, label=None, color=None):
    """Histogram of positive values with logarithmically spaced bins, as a density."""
    ax = _ax(ax)
    a = np.asarray(x, dtype=float)
    a = a[a > 0]
    edges = np.logspace(np.log10(a.min()), np.log10(a.max() * 1.0001), bins + 1)
    if np.allclose(a, np.round(a)):
        # whole numbers: put the edges between integers, so that no bin is empty
        # just because it falls between two consecutive counts
        edges = np.unique(np.round(edges)) - 0.5
        edges = np.append(edges[edges > 0], a.max() + 0.5)
        edges = np.unique(edges)
    ax.hist(a, bins=edges, density=True, label=label, color=color,
            edgecolor="white", linewidth=0.6)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylabel("density")
    return ax


def rank_frequency(freqs, ax=None, label=None, color=None):
    """Plot frequency against rank on log-log axes (Zipf plot)."""
    ax = _ax(ax)
    f = np.sort(np.asarray(freqs))[::-1]
    ax.loglog(np.arange(1, f.size + 1), f, label=label, color=color)
    ax.set_xlabel("rank")
    ax.set_ylabel("frequency")
    return ax
