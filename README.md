# llm-output-explainer

<p align="center">
  <img src="media/hero.svg" alt="llm-output-explainer: controlled English, diagrams, interactive pages and narrated video, with every claim checked against its source" width="100%">
</p>

<p align="center">
  <a href="https://johnqinamd.github.io/llm-output-explainer/"><b>▶ Live demo</b></a> &nbsp;·&nbsp;
  <a href="#install">Install</a> &nbsp;·&nbsp;
  <a href="#four-formats">Formats</a> &nbsp;·&nbsp;
  <a href="#what-it-adds">What it adds</a>
</p>

<p align="center">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2F62C9">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-D97757">
  <img alt="Codex plugin" src="https://img.shields.io/badge/Codex-plugin-111827">
  <img alt="ASD-STE100 Issue 9" src="https://img.shields.io/badge/ASD--STE100-Issue%209-C9822B">
</p>

A Codex and Claude Code skill that explains code, papers, pull requests and results in the format that is fastest to understand. It checks every claim against its source before it writes anything.

The idea comes from [Andrej Karpathy's post](https://x.com/karpathy/status/2105819303471976479). People spend more and more time reading what language models produce. Writing in a controlled language, drawing diagrams, building interactive pages, and making explainer videos can make that output easier to understand.

## Four formats

| Format | Use it when | Output |
|---|---|---|
| Controlled English, 80% [ASD-STE100](https://www.asd-ste100.org/) | answers, summaries, procedures (the default in chat) | the reply |
| Diagram | the point is a structure: data flow, before and after, states | a page with one figure |
| Interactive HTML page | several parts, numbers, or a mechanism to play with | a private Artifact or a standalone .html file |
| Narrated video | only on request: an idea that unfolds over time | an .mp4 |

The skill picks a format from the request. If you name one ("explain in STE", "make it HTML"), it uses that format.

## What it adds

- **The skill checks facts first.** It keeps a claim ledger: each claim, its source (`file:line`, commit, URL) and a status. Every arrow, label and number in a figure counts as a claim too. The skill cuts unsupported claims and tells you about corrected ones.
- **Live state before notes.** For a pull request, `scripts/pr_facts.sh` reads the current state from the GitHub API. It shows whether the PR merged, the head SHA, each commit, and the trailers on the merge commit.
- **STE rules checked against the standard.** `references/ste-writing.md` cites the rule numbers of ASD-STE100 Issue 9 (2025-01-15). `scripts/ste_lint.py` flags common rule breaks and names the rule for each.
- **Pages check themselves.** The starter page includes `selfCheck()`, which flags overflow, overlapping labels and text that is too small, at any screen width. Add `#selfcheck` to the URL to outline the problems. `scripts/check_page.py` checks the page before you publish it.
- **Written for a reader.** The skill writes differently for you, for a peer reviewer, or for a manager, and it can apply your own rules for each audience.

## Live demo

[**Online softmax**](https://johnqinamd.github.io/llm-output-explainer/) is a page the skill made in a test, from the FlashAttention and Milakov & Gimelshein papers. In the browser you can:

- change the block size and step through one row, block by block.
- watch the running max rise and every earlier weight shrink by the same factor.
- add 100 to every score and see plain float32 softmax overflow while the online sum does not.
- open "What the check corrected" to see the two claims the fact check fixed.

The page passes its own `selfCheck()` at phone and desktop width, in light and dark mode. Its source is [`docs/index.html`](docs/index.html).

## Install

In Codex:

```
codex plugin marketplace add JohnQinAMD/llm-output-explainer
codex plugin add llm-output-explainer@llm-output-explainer
```

Start a new Codex conversation after installation. To install only the skill, copy `skills/explain/` to `~/.codex/skills/explain/`.

In Claude Code:

```
claude plugin marketplace add JohnQinAMD/llm-output-explainer
claude plugin install llm-output-explainer@llm-output-explainer
```

Or copy `skills/explain/` to `~/.claude/skills/explain/`.

## Use

Ask in plain words. The skill loads when the request fits. To call it directly, use `/llm-output-explainer:explain` (plugin) or `/explain` (copied skill).

```
explain in STE how the scheduler picks which requests run in a step
make an interactive page for online softmax
summarize PR 1234 in vllm-project/vllm for the reviewers
```

## Files

```
skills/explain/
├── SKILL.md                    the workflow: format, fact check, reader, delivery
├── references/ste-writing.md   ASD-STE100 Issue 9 rules and dictionary notes
├── references/html-page.md     page workflow, figure rules, page sections
├── references/video.md         narrated video steps
├── assets/skeleton.html        starter page: themes, figures, self-check
└── scripts/
    ├── check_page.py           checks an Artifact fragment or standalone page
    ├── ste_lint.py             flags STE rule breaks
    └── pr_facts.sh             live state of a GitHub pull request
```

`docs/index.html` is the live demo page. GitHub Pages serves it, and you can also open it directly in a browser.

## Requirements

- Python 3 for the scripts. `check_page.py` installs `esprima` into `~/.cache/llm-output-explainer/` the first time it parses JavaScript.
- `curl` for `pr_facts.sh`. To raise the GitHub API rate limit, set `GH_TOKEN_FILE` to a file that holds a token.
- Optional: Docker, for a headless browser check or for video (`manimcommunity/manim`).

## Notes on STE

This project is not affiliated with ASD or STEMG. The skill writes in the style of ASD-STE100. It never claims that a text complies with the standard, because the standard says that no tool can certify that. The standard and its dictionary are free from [asd-ste100.org](https://www.asd-ste100.org/). This repository does not include them.

## Related projects

- [karpathy-output-style](https://github.com/ashryaagr/karpathy-output-style): four skills for the same four formats, with Excalidraw diagrams and ElevenLabs narration.
- [visual-explainer](https://github.com/nicobailon/visual-explainer): HTML diagrams, slides and visual diff reviews.

## License

MIT. See [LICENSE](LICENSE).
