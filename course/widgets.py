"""Sliders for exploring an idea.

In a running notebook (JupyterLite, Colab, Jupyter) `explore` shows sliders
and redraws its output whenever one moves. When the course site is built,
or if ipywidgets is missing, it runs once with the starting values, so the
page shows a still frame.
"""

from __future__ import annotations

import os

__all__ = ["explore"]


def _static() -> bool:
    """True while the course site is being built (the build sets COURSE_STATIC=1)."""
    return os.environ.get("COURSE_STATIC", "") not in ("", "0")


def explore(func, **controls):
    """Call `func` with a slider for each of its arguments.

    Each control is a tuple (low, high, step, start) or (low, high, step,
    start, label). Whole-number tuples give whole-number sliders.

        def show(k):
            print(k ** 2)

        explore(show, k=(1, 10, 1, 3, "k (a whole number)"))
    """
    start = {name: spec[3] for name, spec in controls.items()}
    if _static():
        func(**start)
        return
    try:
        import ipywidgets as w
    except ImportError:
        print("(Sliders need the ipywidgets package; showing the starting values.)")
        func(**start)
        return
    sliders = {}
    for name, spec in controls.items():
        low, high, step, value = spec[:4]
        label = spec[4] if len(spec) > 4 else name
        whole = all(isinstance(v, int) and not isinstance(v, bool) for v in (low, high, step, value))
        kind = w.IntSlider if whole else w.FloatSlider
        sliders[name] = kind(
            min=low, max=high, step=step, value=value, description=label,
            continuous_update=False, style={"description_width": "initial"},
            layout=w.Layout(width="460px"),
        )
    w.interact(func, **sliders)
