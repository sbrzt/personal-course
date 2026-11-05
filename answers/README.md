# Your answers

Put your worked copy of each lesson here, with the same file name as the lesson, for example `answers/s0-1-reading-formulas.ipynb`.

## Getting a copy

- **Locally:** `cp lessons/phase-s/s0-1-reading-formulas.ipynb answers/` and open it in Jupyter. Run the setup cell from inside the repository so that it finds the `course` package.
- **In Colab:** open the lesson from the course site, then *File → Save a copy in GitHub*, choose this repository and the path `answers/<lesson name>.ipynb`.
- **In the browser (JupyterLite):** *File → Download*, then upload the file here through GitHub's web interface (*Add file → Upload files*).

## Grading

On every push that changes a notebook here, the **Grade answers** workflow runs it and writes a summary to the run page (Actions tab): one line per exercise with ✅, ❌ or ⬜, plus any errors. The executed notebooks are attached to the run as an artifact. Grading informs; it never blocks a push.

To grade locally: `pip install -e ".[grade]"`, then `python tools/grade.py` (all answers) or `python tools/grade.py answers/<file>.ipynb`.

## Privacy

This repository is public: anything you commit here can be read by anyone. Work you want to keep to yourself goes in `answers/private/`, which git ignores.
