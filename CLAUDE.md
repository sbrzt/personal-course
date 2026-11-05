# Notes for Claude: maintaining this course

This repository holds Sebastian Barzaghi's personal course on AI for digital humanities research. The full curriculum lives outside the repository, in his claude.ai project "learning-path"; this repository holds the lessons as they are written. He has no background in statistics: lessons must take nothing for granted. There are no deadlines; give hour estimates only.

Phase S is being rewritten from zero, following the syllabus in `lessons/phase-s/phase-s.md` (42 lessons in parts 0–5). Write the lessons in that order and mark each one "ready" there when it is published.

## Layout

- `lessons/<phase>/` — lessons as `.ipynb` without outputs, plus one overview page per phase (`phase-s.md`). Every published file must be listed in `myst.yml` (`toc`). Phase S lessons are named `sP-L-<slug>.ipynb` (P = part, L = lesson), titled `SP.L · <Title>`. `lessons/phase-s/first-draft/` keeps the superseded first S1: not on the site, not verified.
- `course/` — the package the lessons import: `data` (datasets, including the bundled Bibliothecae.it tables in `resources/bibliothecae/`), `stats` (reference implementations), `models`, `plots`, `widgets` (sliders), `bibliothecae` (standard views of the corpus), `checking` (the check framework) and `checks/sP_L.py` (one module per lesson, `LESSON = "SP.L"`; the first draft's checks are in `checks/draft/`).
- `tools/solve.py` verifies lessons; `tools/grade.py` grades `answers/`; `tools/build_lite.py` builds JupyterLite into `_build/html/lite`.

## Writing a lesson

- Draft as a Jupytext MyST Markdown file, convert with `jupytext --to ipynb`, then remove the `jupytext` metadata and clear outputs. To edit an existing lesson, convert it to MyST Markdown, edit, convert back.
- Start with the H1 title, the "Run this lesson" links (JupyterLite: `https://sbrzt.github.io/personal-course/lite/lab/index.html?path=lessons/<phase>/<file>.ipynb`; Colab: `https://colab.research.google.com/github/sbrzt/personal-course/blob/main/lessons/<phase>/<file>.ipynb`), goals, then the standard setup cell (copy it from an existing lesson; tag it `hide-input`).
- Exercises: a `### ✏️ Exercise N · Title` heading; one code cell tagged `exercise` whose last line is `check.exN(...)`; then `<details><summary>💡 Hint</summary>…</details>` and `<details><summary>✅ Solution</summary>` containing one ```` ```python ```` block with the full solved cell. `tools/solve.py` swaps that block into the exercise cell, so it must be complete.
- In exercise cells, every placeholder is a whole `...` on its own (`x = ...`, never `x = ... + 1` or `a, b = ...`), and nothing outside the check calls the learner's functions. Later cells use `course.stats` or `course.models`, never the learner's answers.
- Every concept follows the same steps: the idea in plain words (an everyday example first); a picture or slider; the formula in a display block, then read aloud and with a table naming each symbol; a tiny example by hand (three to six numbers); the same in code, then on the Bibliothecae.it data.
- Sliders: `from course.widgets import explore`, then `explore(func, name=(low, high, step, start, "label"))`. With `COURSE_STATIC=1` (set by the site build and by `tools/nbrun.py`) `explore` calls `func` once with the start values, so the site shows a still frame. Keep slider functions quick: they rerun on every move, also in the browser.
- Use portable Markdown only (headings, `<details>`, blockquotes for "🤖 Why this matters for AI" and "🔬 Metascience" notes): no MyST directives, because Colab and plain Jupyter do not render them. No maths inside `<details>` blocks: the site does not render it there.
- Write `Bibliothecae\.it` in Markdown prose (MyST otherwise turns it into a link) and link the journal as `https://bibliothecae.unibo.it/`.
- Code lines at most 85 characters. Plots go through `course.plots` (`plots.use_style()`, colours `plots.BLUE`, `ORANGE`, `AQUA`).
- Verify every reference before citing it; quote numbers only after computing them.

## Checks

- Each check is `@exercise(LESSON, number, title)` around `def exN(fb, ...)`. Use `fb.number(...)` for scalars, `fb.call(...)` for learner functions, `fb.ok/no/todo/info` otherwise, and give targeted `diagnose` hints for likely mistakes without revealing the answer.
- Checks must never raise, must treat `...` as "not attempted", and must compute expected values from the data at run time.

## Data

The Bibliothecae.it data are open and ship with the package (`course/resources/bibliothecae/`, CC BY 4.0, see its README); use them freely in lessons, with their known problems left in place for the lessons to find. The repository is public: `data/`, `private/` and `answers/private/` are ignored by git for anything he wants to keep local.

## Before committing

```bash
pytest -q
python tools/solve.py lessons/*/*.ipynb
jupyter-book build --html --execute      # needs api.mystmd.org for the theme
python tools/build_lite.py
```

In a sandbox without access to api.mystmd.org, clone `https://github.com/myst-templates/book-theme` into `_build/templates/site/myst/book-theme` and run `npm install` there first; when running as root, start the build with a Jupyter config that sets `c.ServerApp.allow_root = True`.
