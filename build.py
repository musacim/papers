#!/usr/bin/env python3
"""Generate the static site from papers.json.

Usage: python3 build.py

Writes index.html, papers/<slug>.html, sitemap.xml and robots.txt.
Only the Python standard library is required.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = ["slug", "title", "authors", "date", "pdf", "abstract"]


def esc(s):
    return html.escape(str(s), quote=True)


def load():
    data = json.loads((ROOT / "papers.json").read_text(encoding="utf-8"))
    errors = []
    slugs = set()
    for p in data["papers"]:
        name = p.get("slug", "?")
        for key in REQUIRED:
            if not p.get(key):
                errors.append(f"{name}: missing '{key}'")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", p.get("slug", "")):
            errors.append(f"{name}: slug must be lowercase letters, digits and hyphens")
        if name in slugs:
            errors.append(f"{name}: duplicate slug")
        slugs.add(name)
        if not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", p.get("date", "")):
            errors.append(f"{name}: date must be YYYY, YYYY-MM or YYYY-MM-DD")
        if p.get("pdf") and not (ROOT / p["pdf"]).is_file():
            errors.append(f"{name}: PDF not found at {p['pdf']}")
    if errors:
        sys.exit("papers.json errors:\n  " + "\n  ".join(errors))
    # Papers are shown in the order they appear in papers.json.
    return data


def page(site, title, body, head_extra="", depth=0, canonical="", description=""):
    prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description or site['description'])}">
<link rel="canonical" href="{esc(canonical)}">
<link rel="stylesheet" href="{prefix}assets/style.css">
{head_extra}</head>
<body>
<header class="site"><a href="{prefix}index.html">{esc(site['author'])} &middot; {esc(site['title'])}</a></header>
<main>
{body}
</main>
<footer class="site">&copy; {esc(site['author'])}</footer>
<script src="{prefix}assets/site.js"></script>
</body>
</html>
"""


def scholar_meta(site, p):
    base = site["base_url"]
    tags = [("citation_title", p["title"])]
    for a in p["authors"]:
        tags.append(("citation_author", a))
        # Institution tags apply to the author immediately preceding them.
        if p.get("institution"):
            tags.append(("citation_author_institution", p["institution"]))
    tags.append(("citation_publication_date", p["date"].replace("-", "/")))
    tags.append(("citation_online_date", p["date"].replace("-", "/")))
    for key in ("journal_title", "conference_title", "volume", "issue",
                "firstpage", "lastpage", "doi", "arxiv_id", "publisher"):
        if p.get(key):
            tags.append((f"citation_{key}", p[key]))
    tags.append(("citation_language", "en"))
    if p.get("keywords"):
        tags.append(("citation_keywords", "; ".join(p["keywords"])))
    tags.append(("citation_abstract", p["abstract"]))
    tags.append(("citation_abstract_html_url", f"{base}/papers/{p['slug']}.html"))
    tags.append(("citation_pdf_url", f"{base}/{p['pdf']}"))
    out = "".join(f'<meta name="{n}" content="{esc(v)}">\n' for n, v in tags)
    out += f'<meta property="og:type" content="article">\n'
    out += f'<meta property="og:title" content="{esc(p["title"])}">\n'
    out += f'<meta property="og:url" content="{esc(base)}/papers/{esc(p["slug"])}.html">\n'
    return out


def cite_url(site, p):
    return f"{site['base_url']}/papers/{p['slug']}.html"


def bibtex(site, p):
    last = p["authors"][0].split()[-1].lower()
    first_word = re.sub(r"[^a-z0-9]", "", p["title"].split()[0].lower())
    key = f"{last}{p['date'][:4]}{first_word}"
    entry = "article" if p.get("journal_title") else "inproceedings" if p.get("conference_title") else "misc"
    fields = [("title", "{" + p["title"] + "}"),
              ("author", " and ".join(p["authors"])),
              ("year", p["date"][:4])]
    if p.get("journal_title"):
        fields.append(("journal", p["journal_title"]))
    if p.get("conference_title"):
        fields.append(("booktitle", p["conference_title"]))
    if entry == "misc" and p.get("status"):
        fields.append(("note", p["status"]))
    if p.get("doi"):
        fields.append(("doi", p["doi"]))
    fields.append(("url", cite_url(site, p)))
    return f"@{entry}{{{key},\n" + ",\n".join(f"  {k} = {{{v}}}" for k, v in fields) + "\n}"


def links(site, p, prefix):
    items = [f'<a href="{prefix}{esc(p["pdf"])}">PDF</a>']
    if p.get("code"):
        items.append(f'<a href="{esc(p["code"])}">Code</a>')
    if p.get("arxiv_id"):
        items.append(f'<a href="https://arxiv.org/abs/{esc(p["arxiv_id"])}">arXiv</a>')
    return " &middot; ".join(items)


def venue(p):
    return p.get("journal_title") or p.get("conference_title") or ""


def paper_page(site, p):
    base = site["base_url"]
    url = f"{base}/papers/{p['slug']}.html"
    meta_line = esc(p["date"])
    if venue(p):
        meta_line = f"{esc(venue(p))} &middot; " + meta_line
    body = f"""<article class="paper">
<h1>{esc(p['title'])}</h1>
<p class="authors">{esc(', '.join(p['authors']))}</p>
{f'<p class="affil">{esc(p["institution"])}</p>' if p.get('institution') else ''}
<p class="meta">{meta_line}</p>
<p class="links">{links(site, p, '../')}</p>
<h2>Abstract</h2>
<p class="abstract">{esc(p['abstract'])}</p>
{f'<p class="keywords"><strong>Keywords:</strong> {esc(", ".join(p["keywords"]))}</p>' if p.get('keywords') else ''}
<p class="back"><a href="../index.html">&larr; All papers</a></p>
</article>"""
    return page(site, p["title"], body, scholar_meta(site, p), depth=1,
                canonical=url, description=p["abstract"][:300])


def index_page(site, papers):
    items = []
    for p in papers:
        v = f"{esc(venue(p))} &middot; " if venue(p) else ""
        items.append(f"""<li class="entry">
<a class="title" href="papers/{esc(p['slug'])}.html">{esc(p['title'])}</a>
<div class="authors">{esc(', '.join(p['authors']))}</div>
<div class="meta">{v}{esc(p['date'])}</div>
<div class="links">{links(site, p, '')}</div>
<div class="bib-head">BibTeX <button type="button" class="copy" data-copy="bib-{esc(p['slug'])}">Copy</button></div>
<pre class="bibtex" id="bib-{esc(p['slug'])}">{esc(bibtex(site, p))}</pre>
</li>""")
    body = f"<h1>{esc(site['title'])}</h1>\n<ul class=\"papers\">\n" + "\n".join(items) + "\n</ul>"
    return page(site, f"{site['author']} — {site['title']}", body, canonical=site["base_url"] + "/")


def sitemap(site, papers):
    base = site["base_url"]
    newest = max((p["date"] for p in papers), default="")
    urls = [(base + "/", newest)]
    for p in papers:
        urls.append((f"{base}/papers/{p['slug']}.html", p["date"]))
        urls.append((f"{base}/{p['pdf']}", p["date"]))
    rows = "".join(f"  <url><loc>{esc(u)}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")


def main():
    data = load()
    site, papers = data["site"], data["papers"]
    site["base_url"] = site["base_url"].rstrip("/")
    (ROOT / "index.html").write_text(index_page(site, papers), encoding="utf-8")
    for p in papers:
        (ROOT / "papers" / f"{p['slug']}.html").write_text(paper_page(site, p), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(site, papers), encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {site['base_url']}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(papers)} paper page(s), index.html, sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
