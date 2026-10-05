#!/usr/bin/env python3
"""Start a page from assets/skeleton.html, so the CSS and scripts are copied, not retyped.

Usage: new_page.py <out.html> --title "Name" [--palette signal|trace|ink] [--layout "..."] [--lang en] [--standalone] [--force]

It sets the <title>, swaps in a validated palette from assets/palettes.css, and with
--standalone wraps the fragment in a full HTML document. Then edit only the regions
between the markers: content:start/content:end (the page), page:start/page:end (its
script), and the font links and font tokens if the subject needs other faces.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")


def palettes():
    css = open(os.path.join(ASSETS, "palettes.css"), encoding="utf-8").read()
    found = {}
    for m in re.finditer(r"/\* palette: (\w+)[^*]*\*/\n(.*?)/\* end palette \*/", css, re.S):
        found[m.group(1)] = m.group(2).rstrip("\n")
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--title", required=True, help="the name of the thing, two to four words")
    ap.add_argument("--palette", default="signal")
    ap.add_argument("--layout", default="one column of sections; each figure spans the column",
                    help="the one-line layout concept, written into the CSS")
    ap.add_argument("--lang", default="en", help="page language, for --standalone")
    ap.add_argument("--standalone", action="store_true", help="write a full HTML document instead of an Artifact fragment")
    ap.add_argument("--force", action="store_true", help="overwrite an existing file")
    a = ap.parse_args()

    if os.path.exists(a.out) and not a.force:
        sys.exit(f"{a.out} exists; pass --force to overwrite it")
    pals = palettes()
    if a.palette not in pals:
        sys.exit(f"unknown palette {a.palette!r}; choose from {', '.join(sorted(pals))}")

    page = open(os.path.join(ASSETS, "skeleton.html"), encoding="utf-8").read()
    page = re.sub(r"<title>.*?</title>", lambda _: f"<title>{a.title}</title>", page, count=1, flags=re.S)
    page = page.replace("/* Layout: REPLACE with this page's one-line layout concept. */", f"/* Layout: {a.layout}. */", 1)
    start = page.index("/* palette:start")
    start = page.index("*/", start) + 3
    end = page.index("/* palette:end */")
    page = page[:start] + pals[a.palette] + "\n" + page[end:]

    if a.standalone:
        head, sep, body = page.partition("</style>")
        page = (f'<!doctype html>\n<html lang="{a.lang}">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + head + sep + "\n</head>\n<body>\n" + body.lstrip("\n") + "\n</body>\n</html>\n")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(page)
    print(f"wrote {a.out} ({a.palette} palette{', standalone' if a.standalone else ''})")


if __name__ == "__main__":
    main()
