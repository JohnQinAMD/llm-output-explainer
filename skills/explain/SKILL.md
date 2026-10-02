---
name: explain
description: Explain something in the format that is fastest to understand, from controlled English (ASD-STE100 style), to a diagram, to an interactive HTML page, to a narrated explainer video. Check facts against their sources before writing. Use when the user wants to understand a substantial concept, algorithm, code change, pull request, paper, benchmark result, or agent output, or asks for an explainer, diagram, HTML explanation, STE, or video. Not for one-line answers, drafting a pull request description, or code review.
---

# LLM output explainer

Make a subject easy to understand, and make sure every statement in the explanation is true.

## 1. Choose the format

| Format | Use when | Output |
|---|---|---|
| **Controlled English** (80% ASD-STE100) | answers, summaries, procedures; the default in chat | the reply |
| **Diagram** | the point is a structure: data flow, before/after, states | a one-figure page |
| **Interactive HTML page** | several parts, numbers, a mechanism worth playing with; something to share | a private Artifact when available, otherwise a standalone .html file |
| **Video** | only when asked: intuition that unfolds over time | an .mp4 |

If the user names a format, use it. In chat, answer in controlled English. When a richer format would clearly help, offer it in one line.

## 2. Check facts before writing

A clear explanation of a wrong fact misleads more than a vague one.

- **Read primary sources:** the code that runs (dispatch, launch sites, constants), the logs, the paper. Comments, old PR bodies and memory describe some earlier state.
- **Check live state first.** For a PR, run `scripts/pr_facts.sh <owner/repo> <N> [checkout] [body-file]`, which reads the PR from the GitHub API. A PR can merge after your notes were written.
- **Keep a claim ledger:** one line per fact, with its source (`file:line`, commit, URL) and a status. The statuses are verified, corrected, unsupported, and unverifiable. "Corrected" also covers a claim made more precise. A fact computed from sourced inputs counts as verified. Cut unsupported claims. Label unverifiable ones on the page.
- **Figures are claims too.** Every arrow, label and on-screen number needs a source.
- **Numbers keep their conditions:** hardware, settings, the version measured, and what it was compared against.
- **Simulated data gets labeled.** When you simulate, run the real algorithm on made-up inputs.
- **For code changes:**
  - Trace the baseline as it runs today on the base branch.
  - Trust launch and dispatch code over comments.
  - Read every commit's diff; "Rebase onto main" commits can change behavior.
  - For a merged PR, describe the code as merged. If main changed it later, add a one-line "after the merge" note.
  - In a blobless clone, read old commits with `git -c gc.auto=0 ...`, so reading doesn't start a background gc.

## 3. Know the reader

| Reader | Start with | Density | Leave out |
|---|---|---|---|
| The user | the answer | high | what they already told you |
| A peer (reviewer) | what changes and why, in two sentences | high, every claim cited | the work history; noise the user's rules exclude |
| An outsider (manager, other team) | the outcome and its number | low, 3 to 5 points | internals |

A new reader needs a new outline; changing the wording is not enough. To meet a common wrong idea, take it from a source (a review comment, a corrected ledger line). Otherwise say it is a guess. For other readers, check memory for the user's rules about that audience, and apply them. Where they conflict with this skill, the user's rules win: for example, cut an unverifiable claim from reviewer text instead of labeling it.

## 4. Produce

- **Controlled English:** `references/ste-writing.md` (Issue 9 rules). `scripts/ste_lint.py [--strict] file` flags common breaks.
- **Diagram or page:** read `references/html-page.md`. Start from `assets/skeleton.html`, check with `scripts/check_page.py`, then publish as an Artifact or deliver a standalone file, according to the tools available.
- **Video:** `references/video.md`.

## 5. Deliver

Before sending, check four things:
- the first screen answers the question;
- every term the reader may not know is defined before its first use;
- a concrete example comes early, right after the one-line answer;
- every number has its condition.

Then:
- If the reader is someone else, start with one line: "Written for: …".
- Give the link or file, and a short list of what it shows.
- Name any claim you corrected while checking, especially one from the user's own notes.
- If you publish an Artifact, say that it is private until the user shares it. If you create a standalone file, give its path.
- Update memory when you learned something durable, such as a PR merging or a baseline fact that was wrong.
