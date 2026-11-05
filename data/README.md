# Private data

Git ignores everything in this folder except this file, so data placed here never reach the public repository.

## Bibliothecae.it

Put the seven CSV files from `bib_data_output.zip` in `data/bibliothecae/`, or the zip itself in `data/`:

```text
data/
├── README.md
└── bibliothecae/
    ├── articles.csv
    ├── article_authors.csv
    ├── references.csv
    ├── reference_authors.csv
    ├── relations_article_author.csv
    ├── relations_article_reference.csv
    └── relations_reference_author.csv
```

`course.data.bibliothecae()` looks, in order, at the path you pass it, at the environment variable `BIBLIOTHECAE_DATA`, and then at `data/bibliothecae/`, `data/bib_data_output.zip` and `bib_data_output.zip` in the current folder and each folder above it. If it finds nothing, it returns a simulated stand-in with the same tables and columns, and says so.
