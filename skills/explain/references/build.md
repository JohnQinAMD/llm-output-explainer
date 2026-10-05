# Build a page or video from a brief

The explain skill writes a brief and starts this build in a background subagent, so the conversation can go on. If you are that subagent:
- Work only from the brief.
- Do not ask the user questions, because you cannot reach them.
- Do not do new research.

Paths below are relative to the skill directory, the parent of this file.

## Speed rules

Most build time goes into re-planning, not into writing. The brief already fixes the content, the order and the claims.
- In your first step, read the brief and `references/html-page.md` together, and run `new_page.py`.
- Do not re-plan the page or redesign it. Lay out each section from the outline as you write it.
- Write all content and the page script in one pass, with one splice.
- Do not reread the sources or the ledger's sources, read the scripts' code, or write your own layout checks.

## The brief

The main conversation writes `<work dir>/<name>.brief.md` with these fields:

- **Format:** page, diagram or video.
- **Reader and language.**
- **Title:** the name of the thing, two to four words.
- **Delivery:** a private Artifact when the Artifact tool is available, otherwise a standalone file.
- **Work dir:** where to write files. It must have free space, and any machine that renders must be able to see it.
- **Answer:** the one-line answer.
- **Outline:** the sections, and what each figure must show.
- **Claim ledger:** one line per claim, as `claim | source | status`, then the counts, for example "7 verified, 2 corrected, 1 unverifiable". The builder copies the counts and does not count again.
- **Corrections:** the corrections the page names.
- **Source copies:** local paths of the fetched pages, figures and data. Name each one as its source does, for example "article Figure 2: sources/fig3.jpg", because a file name is not a figure number.
- **Video plan:** for a video, the plan the user approved.

## Page or diagram

1. **Read** `references/html-page.md`. The skeleton already follows the usual diagram and chart rules, so load other design guidance only for a figure type the skeleton does not have.
2. **Start the file:**
   ```
   python3 scripts/new_page.py <work dir>/<name>.html --title "<title>" --palette <signal|trace|ink>
   ```
   For a standalone file, add `--standalone --lang <code>`. Choose the palette by subject:
   - `signal`: the default.
   - `trace`: timelines, hardware and profiles.
   - `ink`: papers, math and algorithms.

   Do not invent colors.
3. **Write only the marked regions:** from `content:start` to `content:end`, and from `page:start` to `page:end`. Use Edit, or one short splice script. Never retype the CSS, the helpers or `selfCheck()`. Use these helpers:
   - `groupedBars`: two series. To switch modes, redraw it.
   - `hBars`: ranked systems.
   - `mulberry32`: seeded simulations.
   - `data-ref`: linked terms.
4. **Use only claims from the ledger.** Copy the brief's counts into the verification strip. For a claim that is not in the ledger, cut it, or label it on the page as background or a guess.
5. **Check:** run `python3 scripts/check_page.py <file>`, with `--standalone` for a standalone file. Fix every FAIL and every placeholder that is left.
6. **Skip the browser look by default,** because the page runs `selfCheck()` in the viewer's browser. Look only if a local browser starts in a few seconds. Then:
   - Run two `--dump-dom` passes, at 390 px and 1280 px wide, in the light theme only.
   - Give each pass a 90 s timeout.
   - Read `<pre id="selfcheck-report">`.
   - Never take a full-page screenshot.
7. **Deliver:**
   - With the Artifact tool, publish the page with an icon and a one-sentence description.
   - Without it, leave the standalone file in the work dir.

## Video

Follow `references/video.md`. The approved plan is in the brief, so do not wait for approval.

## Report

Write at most 6 lines, which the main conversation relays:
- the link or path
- what the page shows, in 3 or 4 items
- the corrections it names
- whether it is private
- anything you skipped
