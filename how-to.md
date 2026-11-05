# How this course works

## Three ways to run a lesson

Each lesson starts with links to run it. The first code cell of every lesson ("⚙️ Setup") detects where it is running and prepares what it needs, so the rest of the notebook is the same everywhere.

### In your browser (JupyterLite)

Click **in your browser** at the top of a lesson. Nothing is installed on your computer: Python runs inside the browser tab, through Pyodide, and the setup cell installs the course package there. The first run takes up to a minute.

- Your edits are saved **in this browser only**. Use *File → Download* to keep a copy, or to move your work to the repository.
- After a lesson is updated, your saved copy still shows the old version. To get the new one, rename or delete your copy in the file browser and reopen the lesson.
- Your own data can be used too: drag `bib_data_output.zip` into the file browser, next to the notebook.

### In Google Colab

Click **in Google Colab** (you need a Google account). The setup cell installs the course package from GitHub. *File → Save a copy in GitHub* can save your work straight into the `answers/` folder of the repository.

### On your computer (best for the projects)

Your data stay on your computer, and everything runs at full speed:

```bash
git clone https://github.com/sbrzt/personal-course
cd personal-course
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -e ".[lab]"
jupyter lab
```

Then open a lesson in `lessons/`. To use the Bibliothecae\.it data, put the seven CSV files from `bib_data_output.zip` (or the zip itself) in `data/bibliothecae/`. Nothing in `data/` is ever committed, except its README.

## Exercises and checks

Exercise cells are marked ✏️. Replace every `...` with your code and run the cell. Its last line calls a check, which prints:

- ✅ when your answer is right, often with a note on what it means;
- ❌ with a hint when it is not right yet;
- ⬜ while something is still `...` (or only part of the exercise is done);
- ⚠️ if the check itself failed, in which case your answer may well be right.

Each exercise has a 💡 hint and a ✅ solution, folded under it. Try for a few minutes before you open them. `check.summary()` at the end of a lesson lists what you have done.

The checks compare your answers with reference code in the `course` package. Reading that code before you try spoils the exercises, but reading it afterwards is a good way to compare approaches.

## Your answers

Work on a copy of each lesson in `answers/`, with the same file name, and commit it when you are done. A GitHub Action runs your notebook and writes a table of ✅, ❌ and ⬜ per exercise on the run's summary page; for a pull request, the table also appears in the checks tab. Claude can then read your answers in the repository and review them with you.

The repository is **public**. Anything you commit can be read by anyone:

- clear the outputs of notebooks that ran on private data before committing them;
- keep private work in `answers/private/`, or any folder called `private/`, which git ignores.

## Using AI assistants while you learn

This is a course about AI, and you will use AI tools in it, but not as a shortcut through the exercises:

- try every exercise on your own first, then use an assistant to *explain*, not to solve;
- when an assistant helped with an answer, say so in a comment or a Markdown cell, as you would in a paper;
- for the written explanations (✍️), write first and ask for feedback afterwards.

The point of the exercises is the thinking you do while solving them. An answer you did not work out yourself teaches you little.

## When something breaks

- **A lesson does not start in the browser:** reload the page, and check that your browser allows third-party storage for the site. Colab and a local install are the fallbacks.
- **`ModuleNotFoundError: course`:** run the setup cell first. Locally, run Jupyter from inside the `personal-course` folder.
- **A check prints ⚠️:** the check has a bug. Please open an issue with the cell and its output.
- **Anything else:** open an issue on GitHub.
