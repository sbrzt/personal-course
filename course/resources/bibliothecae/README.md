# Bibliothecae.it: articles and references

Bibliographic data about [Bibliothecae.it](https://bibliothecae.unibo.it/) (ISSN 2283-9364), a journal on libraries, bibliography and documentation published by the Department of Cultural Heritage of the University of Bologna. Compiled by Sebastian Barzaghi in November 2026: article metadata were queried from Wikidata through its SPARQL endpoint, and reference lists were scraped from the journal's website.

Load them with `course.data.bibliothecae()`, which returns the seven tables as pandas DataFrames of strings.

| File | One row per | Rows |
| --- | --- | --- |
| `articles.csv` | article published in the journal, 2012–2025 | 321 |
| `article_authors.csv` | author of an article, with name, sex and affiliations | 148 |
| `references.csv` | reference in an article's reference list | 7,507 |
| `reference_authors.csv` | cited author with a local identifier | 3,937 |
| `relations_article_author.csv` | link between an article and one of its authors | 406 |
| `relations_article_reference.csv` | link between an article and one of its references | 7,594 |
| `relations_reference_author.csv` | link between a reference and one of its authors | 6,122 |

Articles and their authors are identified by Wikidata QIDs; references (`REF…`) and most cited authors (`AUTH…`) by local identifiers.

## Known problems

The tables are kept exactly as compiled, problems included, because finding and handling them is part of the lessons:

- references were only collected for articles from 2016 on, and not for every one of them;
- some articles have no author record, and some relation rows point to items outside the 321 articles;
- some reference dates are missing or impossible (before 1400, or after the citing article);
- `relations_article_reference.csv` contains a few exact duplicate rows;
- author names have spelling variants, and some reference strings are fragments.

## Licence

The articles of Bibliothecae.it are published open access under CC BY 4.0, and Wikidata's content is available under CC0. These compiled tables are shared under CC BY 4.0, like the rest of the course content: credit Bibliothecae.it for the reference lists and Wikidata for the article metadata.
