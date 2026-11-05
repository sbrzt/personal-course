# Bundled data

## commedia.txt

Dante Alighieri, *La Divina Commedia* (Inferno, Purgatorio, Paradiso; 100 cantos). The text is in the public domain.

- **Source:** the UTF-8 transcription published as Project Gutenberg eBook #1000 (released August 1997, updated 28 January 2021), taken from the GITenberg mirror on GitHub. The edition it follows is not stated there.
- **Changes:**
  - The Project Gutenberg header, licence, footer and table of contents were removed.
  - Each canto heading was rewritten as one line, for example `INFERNO · CANTO I`.
  - Runs of blank lines were collapsed, and line endings normalised to `\n`.
- **Use:** word frequencies (Zipf's law) in lesson S1.3, and language models in later lessons.

`course.data.commedia()` returns the text without the heading lines; `commedia(headings=True)` keeps them.
