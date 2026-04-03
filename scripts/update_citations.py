#!/usr/bin/env python3
"""Fetch citation counts from Google Scholar and update docs/index.html."""

import re
import sys

try:
    from scholarly import scholarly
except ImportError:
    print("scholarly not installed", file=sys.stderr)
    sys.exit(1)

AUTHOR_ID = "Izu1c6oAAAAJ"

# (data-doi value, lowercase keyword present in the Google Scholar title)
PAPERS = [
    ("10.1103/PhysRevApplied.9.034021", "metasurface"),
    ("10.1103/PhysRevB.107.115409", "band nesting"),
    ("10.1038/s41467-019-09008-0", "gas identification"),
    ("10.1103/PhysRevApplied.13.011002", "nanoribbon"),
    ("phd-thesis-tunable", "tunable hyperbolicity"),
    ("10.1109/ICECE.2012.6471671", "ballistic modeling"),
    ("10.1109/ICIEV.2012.6317387", "ballistic modeling"),
]

HTML_PATH = "docs/index.html"


def main():
    print("Fetching Google Scholar author profile…")
    try:
        author = scholarly.search_author_id(AUTHOR_ID)
        author = scholarly.fill(author, sections=["basics", "publications"])
    except Exception as exc:
        # Exit 0 so the action doesn't mark the run as failed on a Scholar block
        print(f"Could not fetch Scholar data: {exc}", file=sys.stderr)
        sys.exit(0)

    total = author.get("citedby", 0)
    print(f"Total citations: {total}")

    pub_map = {
        pub.get("bib", {}).get("title", "").lower(): pub.get("num_citations", 0)
        for pub in author.get("publications", [])
    }

    with open(HTML_PATH, encoding="utf-8") as fh:
        html = fh.read()

    changed = False

    for doi, keyword in PAPERS:
        count = next(
            (c for title, c in pub_map.items() if keyword in title), None
        )
        if count is None:
            print(f"  No match for doi={doi} keyword='{keyword}' — skipping")
            continue

        # Look for the citation count span within the article tag that has the matching data-doi
        pattern = (
            rf'(<article[^>]*data-doi="{re.escape(doi)}".*?)'
            r'(<span class="citation-count">)\d+(</span>)'
        )
        
        # If the span doesn't exist yet (like for the PhD thesis), we need a different pattern to insert it
        if not re.search(pattern, html, flags=re.DOTALL):
            # Try to insert it before the first <a> or </div> in that article
            insert_pattern = rf'(<article[^>]*data-doi="{re.escape(doi)}".*?)(<a|<div|/article>)'
            updated = re.sub(
                insert_pattern,
                rf'\g<1><p class="card-meta"><strong><span class="citation-count">{count}</span> citations</strong></p>\g<2>',
                html,
                count=1,
                flags=re.DOTALL
            )
        else:
            updated = re.sub(pattern, rf"\g<1>\g<2>{count}\g<3>", html, flags=re.DOTALL)
        
        if updated != html:
            html = updated
            changed = True
            print(f"  {doi}: {count}")

    def _replace_total(m):
        suffix = "+" if "+" in m.group(0) else ""
        return m.group(1) + str(total) + suffix + m.group(2)

    updated = re.sub(
        r'(<span class="citation-total">)\d+\+?(</span>)', _replace_total, html
    )
    if updated != html:
        html = updated
        changed = True
        print(f"citation-total spans updated: {total}")

    if changed:
        with open(HTML_PATH, "w", encoding="utf-8") as fh:
            fh.write(html)
        print("docs/index.html written.")
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()
