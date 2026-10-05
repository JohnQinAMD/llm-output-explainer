# Diagrams and interactive pages

A page is one HTML file. Publish it as a private Artifact when an Artifact tool is available. Otherwise, write a standalone HTML file and give the user its path. A diagram is a short page with one figure, a two-sentence intro and a caption.

## Workflow

1. **Choose delivery:** if an Artifact tool is available, use its required document format (an HTML fragment). Otherwise, make a standalone HTML document in the user's workspace. The skeleton already follows the usual page, diagram and chart rules, so load other design guidance only for a figure type the skeleton does not have.
2. **Start the file:** run `python3 scripts/new_page.py <work dir>/<short-name>.html --title "<Name>" --palette <signal|trace|ink>`, with `--standalone --lang <code>` for a standalone document. It copies `assets/skeleton.html`, which has the theme tokens, SVG classes, a tooltip, chart helpers (`groupedBars`, `hBars`), the verification strip, linked terms and the self-check. It also swaps in a validated palette from `assets/palettes.css`. Then edit only the marked regions, `content:start`–`content:end` and `page:start`–`page:end`. Never retype the CSS or scripts. Keep the default fonts unless the subject needs others.
3. **Title:** use the name of the thing ("Online Softmax"), not "X explainer".
4. **Check:** for an Artifact fragment, run `python3 scripts/check_page.py <page.html>`. For a standalone document, add `--standalone`. Fix every FAIL.
5. **Deliver:** publish through the Artifact tool when available. Otherwise, keep the standalone file in the workspace and give the user a clickable file link or path. Do not claim that a local file was published.

## Figures

Pick the figure by what the reader must see:

| The reader must see… | Figure |
|---|---|
| which parts exist and what flows between them | boxes and arrows, left to right |
| what changed between two versions | two lanes, old above new, with columns aligned by function |
| steps in order | a stepper that opens on the complete picture |
| how a result depends on a setting | a live figure redrawn from one `model(settings)` function |
| numbers across sizes or over time | bars or a line chart, with the same numbers in a table |

Rules:
- One claim per figure, stated in the `<figcaption>` and the SVG's `aria-label`.
- A verb on every arrow (`writes`, `reads`); a noun only for data (`Q, KW`).
- One accent color for what is new or what the figure is about.
- Sketch the layout on a grid before writing coordinates. Columns go 200–240 units apart, labels stay under about 18 characters, and labels render at 11 px or more.
- Wide figures go in a `.scroll` wrapper with a `min-width`, so phones scroll instead of shrinking the text.

## Page sections (use only the ones the subject needs)

- **Header:** eyebrow (context), h1 (what it does), a 3-sentence lede, and a strip of 3–4 key facts, each with its condition.
- **Verification strip:** the claim ledger's counts (verified, corrected, unverifiable), plus a fold-out list of corrections with their sources.
- **Before/after diagram:** draw the difference, and say exactly which baseline it shows.
- **Component cards:** one per part, each with its shapes, config and the key trick.
- **Simulation:** the hardest mechanism, running the real algorithm on seeded synthetic data. It opens in its final state and is labeled as simulated.
- **"Which path runs" checker:** form controls in the code's real check order, and the result with the exact log line.
- **Measurements:** the conditions first, then tables; a chart only where the shape matters.
- **Footer:** what the page was built from (commit, paper version).

## Self-check and pitfalls

- The skeleton's `selfCheck()` runs on load. Overflow and overlapping SVG labels FAIL; labels under 10 px WARN. Add `#selfcheck` to the page URL to outline the problems in red. `check_page.py` can't see layout, so this is the only overflow check.
- A headless browser check is optional, and is worth it only when a browser starts in seconds. Run headless Chrome (for example, the `zenika/alpine-chrome` image) with `--dump-dom` at `--window-size=390,2600` and `1280,1700`, in the light theme, with a 90 s timeout on each run. Then read `<pre id="selfcheck-report">`. Do not take full-page screenshots, because a tall window can hang the browser for minutes.
- Long paths or identifiers push the page sideways on phones; give their container `overflow-wrap: anywhere`.
- Color SVG elements through theme-token classes, never literal hex, or dark mode breaks.
- Use `.list > li`, not `.list li`, so nested bullets don't inherit row styles.
