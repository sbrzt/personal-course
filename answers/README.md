# Your answers

Put your worked copy of each lesson here, with the same file name as the lesson, for example `answers/s1-1-centre-spread-shape.ipynb`.

## Getting a copy

- **Locally:** `cp lessons/phase-s/s1-1-centre-spread-shape.ipynb answers/` and open it in Jupyter. Run the setup cell from inside the repository so that it finds the `course` package.
- **In Colab:** open the lesson from the course site, then *File → Save a copy in GitHub*, choose this repository and the path `answers/<lesson name>.ipynb`.
- **In the browser (JupyterLite):** *File → Download*, then upload the file here through GitHub's web interface (*Add file → Upload files*).

## Grading

On every push that changes a notebook here, the **Grade answers** workflow runs it and writes a summary to the run page (Actions tab): one line per exercise with ✅, ❌ or ⬜, plus any errors. The executed notebooks are attached to the run as an artifact. Grading informs; it never blocks a push.

To grade locally: `pip install -e ".[grade]"`, then `python tools/grade.py` (all answers) or `python tools/grade.py answers/<file>.ipynb`.

The workflow does not have your private data, so it runs the S1.4 project on the simulated stand-in. A ✅ there means your code works; the numbers that matter are the ones you get locally.

## Privacy

This repository is public. Before committing a notebook that ran on private data, clear its outputs (*Edit → Clear Outputs of All Cells* in JupyterLab). Work you want to keep private goes in `answers/private/`, which git ignores.
