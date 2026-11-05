"""Build the in-browser version of the course (JupyterLite) into _build/html/lite.

    python tools/build_lite.py

Steps: copy the lessons into a staging folder, build a wheel of the `course`
package so that `piplite.install("personal-course")` works from the site
itself, and run `jupyter lite build`. Run it after `jupyter-book build`, which
recreates _build/html.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "_build"


def main() -> int:
    stage, wheels, out = BUILD / "lite-contents", BUILD / "wheels", BUILD / "html" / "lite"
    for folder in (stage, wheels, out):
        shutil.rmtree(folder, ignore_errors=True)
    stage.mkdir(parents=True)

    shutil.copytree(ROOT / "lessons", stage / "lessons",
                    ignore=shutil.ignore_patterns("private", "first-draft", ".ipynb_checkpoints", "*.md"))
    (stage / "data").mkdir()
    shutil.copy(ROOT / "data" / "README.md", stage / "data" / "README.md")

    subprocess.run([sys.executable, "-m", "pip", "wheel", str(ROOT), "--no-deps", "--quiet",
                    "--wheel-dir", str(wheels)], check=True)
    wheel = next(wheels.glob("personal_course-*.whl"))

    subprocess.run(["jupyter", "lite", "build",
                    "--contents", str(stage),
                    "--piplite-wheels", str(wheel),
                    "--output-dir", str(out)],
                   check=True, cwd=BUILD)
    print(f"JupyterLite built in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
