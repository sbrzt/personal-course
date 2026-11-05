# AI in digital humanities research

A project-based course on working with, talking about and reasoning about AI, for research in the digital humanities, metascience and bibliographic data. The lessons are Jupyter notebooks with self-checking exercises; they run in the browser, in Google Colab or locally.

**Course site:** <https://sbrzt.github.io/personal-course/>

## Contents

| Folder | What it holds |
| --- | --- |
| `lessons/` | The lessons, one folder per phase. Phase S (statistics and probability) comes first. |
| `course/` | The Python package the lessons import: datasets, reference statistics, simulations, plotting helpers and the exercise checks. |
| `answers/` | Your worked copies of the lessons. A GitHub Action grades them on every push. |
| `data/` | Your private data (ignored by git). See `data/README.md`. |
| `tools/` | `solve.py` verifies the lessons, `grade.py` grades answers, `build_lite.py` builds the in-browser version. |
| `tests/` | Tests for the `course` package. |

## Quick start

Open the course site and click **in your browser** at the top of any lesson. To work locally instead:

```bash
git clone https://github.com/sbrzt/personal-course
cd personal-course
python -m venv .venv && source .venv/bin/activate
pip install -e ".[lab]"
jupyter lab
```

The site's [How this course works](https://sbrzt.github.io/personal-course/how-to) page explains exercises, checks, answers and data.

## For maintainers

```bash
pip install -e ".[dev]"
pytest                                   # the course package
python tools/solve.py lessons/*/*.ipynb  # solutions pass, blank exercises run
jupyter-book build --html --execute      # the site, in _build/html
python tools/build_lite.py               # JupyterLite, in _build/html/lite
```

On every push to `main`, the `Site` workflow runs these steps and publishes the result to GitHub Pages; the `Grade answers` workflow runs the notebooks in `answers/`. Lessons are stored as `.ipynb` without outputs. To edit one as text, convert it with `jupytext --to myst` and back.

## Licences and AI assistance

Lesson text and figures are under [CC BY 4.0](LICENSE-CONTENT.md); code is under the [MIT licence](LICENSE). The text of Dante's *Commedia* in `course/resources/` is in the public domain.

The materials were drafted with Claude (Anthropic) and are reviewed and revised by the author, Sebastian Barzaghi. See `CITATION.cff` to cite them.
