# papers

Source for <https://musacim.github.io/papers/> — a static site listing research papers,
with one page per paper carrying Google Scholar (`citation_*`) metadata.

## Adding a paper

1. Copy the PDF into `papers/` with a short, lowercase, hyphenated name, e.g.
   `papers/my-new-paper.pdf` (no spaces).
2. Add an entry to the `papers` list in `papers.json`. Papers are shown on the site in the
   order they appear in this list, so put the entry where you want it:

   ```json
   {
     "slug": "my-new-paper",
     "title": "Exact Title From the PDF",
     "authors": ["First Author", "Second Author"],
     "institution": "Institution as printed in the PDF",
     "date": "2026-11-15",
     "pdf": "papers/my-new-paper.pdf",
     "keywords": ["optional", "keywords"],
     "code": "https://github.com/... (optional)",
     "abstract": "Abstract text exactly as in the PDF."
   }
   ```

   Required: `slug`, `title`, `authors`, `date` (`YYYY`, `YYYY-MM` or `YYYY-MM-DD`), `pdf`, `abstract`.
   Optional, emitted as Scholar tags when present: `institution`, `keywords`, `code`,
   `journal_title`, `conference_title`, `volume`, `issue`, `firstpage`, `lastpage`,
   `doi`, `arxiv_id`, `publisher`.
   BibTeX-only (not a Scholar tag): `status` (e.g. `Preprint`, written as the BibTeX `note`). The DOI is kept in BibTeX and the `citation_doi` tag but not shown as a link.
3. Run `python3 build.py` (standard library only). It validates the entries and regenerates
   `index.html`, `papers/<slug>.html`, `sitemap.xml` and `robots.txt`.
4. Commit and push. GitHub Pages redeploys automatically.

Keep the title and author names identical to the PDF's first page — Google Scholar
checks that they match.

## Google Scholar notes

- Each paper page has `citation_title`, `citation_author`, `citation_publication_date`,
  `citation_pdf_url`, `citation_abstract_html_url` and related tags.
- Indexing is not instant: Scholar typically picks up new pages within weeks.
- This is a project site under `/papers/`, so crawlers read `robots.txt` from the host root
  (`musacim.github.io/robots.txt`), not this one. Submit `sitemap.xml` via
  Google Search Console to make sure it is seen.
