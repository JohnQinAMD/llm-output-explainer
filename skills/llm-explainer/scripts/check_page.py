#!/usr/bin/env python3
"""Static checks for an explainer page.

Usage: check_page.py [--standalone] <page.html>

By default, check an HTML fragment for an Artifact host. With --standalone,
check a complete HTML document that can be opened directly in a browser.
FAIL lines break the page or its delivery contract and must be fixed.
WARN lines are likely problems worth a look. Exit status is 1 if any FAIL.
The JavaScript check installs esprima into ~/.cache/llm-explainer/pylib on
first use, so it works without node.
"""
import os
import re
import subprocess
import sys

ALLOWED_SCRIPT_HOSTS = (
    "https://cdnjs.cloudflare.com/",
    "https://cdn.jsdelivr.net/npm/",
    "https://unpkg.com/",
    "https://cdn.tailwindcss.com",
    "https://code.jquery.com/",
)
ALLOWED_STYLE_HOST = "https://fonts.googleapis.com/"
PYLIB = os.path.expanduser("~/.cache/llm-explainer/pylib")

fails, warns = [], []


def fail(msg):
    fails.append(msg)


def warn(msg):
    warns.append(msg)


def load_esprima():
    if PYLIB not in sys.path:
        sys.path.insert(0, PYLIB)
    try:
        import esprima  # noqa: F401
        return esprima
    except ImportError:
        pass
    os.makedirs(PYLIB, exist_ok=True)
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "--target", PYLIB, "esprima"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    # The path finder cached PYLIB as missing or empty before the install.
    import importlib
    sys.path_importer_cache.pop(PYLIB, None)
    importlib.invalidate_caches()
    try:
        import esprima
        return esprima
    except ImportError:
        return None


def main(path, standalone=False):
    html = open(path, encoding="utf-8").read()
    size = len(html.encode("utf-8"))
    if size > 16 * 1024 * 1024:
        fail(f"page is {size / 2**20:.1f} MiB; the limit is 16 MiB")

    # Title: a name, found in the first 8 KB.
    m = re.search(r"<title>(.*?)</title>", html[:8192], re.S | re.I)
    if not m:
        fail("no <title> in the first 8 KB")
    else:
        title = m.group(1).strip()
        words = len(title.split())
        if re.search(r"[:|]| - | — ", title) or re.search(r"explainer|overview|walkthrough", title, re.I):
            warn(f'title "{title}" reads like a caption; use the name of the thing the PR builds')
        if words > 6:
            warn(f'title "{title}" has {words} words; aim for 2 to 4')

    # Artifact hosts add the document shell. Local files need their own shell.
    shell_tags = {
        "<!doctype html>": r"<!doctype\s+html(?:\s[^>]*)?>",
        "<html>": r"<html(?:\s[^>]*)?>",
        "<head>": r"<head(?:\s[^>]*)?>",
        "<body>": r"<body(?:\s[^>]*)?>",
    }
    if standalone:
        for tag, pattern in shell_tags.items():
            if not re.search(pattern, html, re.I):
                fail(f"standalone page has no {tag}")
    else:
        for tag, pattern in shell_tags.items():
            if re.search(pattern, html, re.I):
                fail(f"page contains {tag}; the Artifact skeleton adds it, so remove it")

    # CDN allowlist.
    for src in re.findall(r"<script[^>]*\bsrc=\"([^\"]+)\"", html, re.I):
        if not src.startswith(ALLOWED_SCRIPT_HOSTS):
            fail(f"script from a blocked host: {src}")
    for tag in re.findall(r"<link[^>]+>", html, re.I):
        if "stylesheet" in tag:
            href = re.search(r"href=\"([^\"]+)\"", tag)
            if href and not href.group(1).startswith(ALLOWED_STYLE_HOST):
                fail(f"stylesheet from a blocked host: {href.group(1)}")
    for url in re.findall(r"fetch\(\s*[\"'](https?://[^\"']+)", html):
        warn(f"fetch of an external URL is blocked by the viewer: {url}")

    # Theme tokens in all three states.
    if not re.search(r":root\s*\{", html):
        fail("no bare :root token block")
    if "prefers-color-scheme: dark" not in html:
        warn("no prefers-color-scheme: dark block; fine only for a deliberate single-theme design")
    elif ':root[data-theme="dark"]' not in html:
        fail('dark tokens exist but :root[data-theme="dark"] does not; the viewer toggle will not apply them')
    if not re.search(r"body\s*\{[^}]*background", html):
        fail("body has no explicit background; the host's theme will show through")

    # Diagrams and charts need a text alternative.
    for svg in re.findall(r"<svg\b[^>]*>", html):
        if 'role="img"' not in svg or "aria-label" not in svg:
            warn(f"svg without role=\"img\" and aria-label: {svg[:80]}")

    # In-page self-check and figure captions (references/html-page.md).
    if "selfCheck" not in html:
        warn("no in-page selfCheck(); copy it from assets/skeleton.html so overflow and label overlap get caught")
    for fig in re.findall(r"<figure\b.*?</figure>", html, re.S):
        if "<figcaption" not in fig and "<svg" in fig:
            warn("a <figure> with an SVG has no <figcaption> stating its claim")
            break

    # Things the viewer refuses.
    for bad, why in (("window.print(", "print is blocked"), ("alert(", "alert is never shown"),
                     ("confirm(", "confirm returns false"), ("<iframe", "other sites cannot be embedded")):
        if bad in html:
            warn(f"{bad} found: {why}")

    # Inline JavaScript must parse.
    scripts = [s for s in re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S | re.I) if s.strip()]
    if scripts:
        esprima = load_esprima()
        if esprima is None:
            warn("could not install esprima; JavaScript was not syntax-checked")
        else:
            for i, js in enumerate(scripts):
                try:
                    esprima.parseScript(js)
                except Exception as e:  # esprima raises its own Error type
                    fail(f"inline script {i + 1} does not parse: {e}")

    for msg in fails:
        print("FAIL", msg)
    for msg in warns:
        print("WARN", msg)
    if fails:
        print(f"FAIL {len(fails)} problem(s) to fix before publishing")
    elif warns:
        print("PASS with warnings")
    else:
        print("PASS all checks")
    return 1 if fails else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    standalone = False
    if "--standalone" in args:
        standalone = True
        args.remove("--standalone")
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(args[0], standalone=standalone))
