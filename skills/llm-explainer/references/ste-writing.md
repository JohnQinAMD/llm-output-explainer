# Controlled English (ASD-STE100 style)

ASD-STE100 Simplified Technical English (STE) is a controlled language from aerospace maintenance manuals. Its rules force short, literal, unambiguous sentences. They suit any technical explanation, and readers who don't use English as their first language benefit most.

**Baseline:** ASD-STE100 **Issue 9, 2025-01-15**, the current issue. The PDF is free from the official site, https://www.asd-ste100.org/ (Downloads). Rule numbers below were checked against that PDF on 2026-10-02. The standard has two parts: 53 writing rules (Part 1) and a dictionary of about 900 approved words (Part 2).

## Two strengths

- **80% (default, including when the user just says "STE" or "STE style"):** Karpathy's "80% of the way to ASD-STE100". Follow every sentence, paragraph and structure rule below. Relax the dictionary: words outside it are fine, but still use the swaps in the dictionary notes below (for example APPROXIMATELY, not "about"). Technical vocabulary and ordinary verbs are fine, and an occasional passive, -ing form or literal phrasal verb is fine when it reads more naturally. "80%" describes a style, not a measured compliance score. Use it for explanations in chat and on pages.
- **Strict:** every rule, including Part 2 word by word. Use it only when the user says "strict" or the text is a procedure people will follow step by step.

## Verification boundary

Never call output "STE compliant". STEMG states that no tool replaces the standard and that they certify no tool (FAQ, "language checking tools"). Strict compliance needs a word-by-word check against Part 2 and the reader's approved technical terms.
- For a strict draft, say which issue you used and which checks you did: rules checked, dictionary checked or not.
- If the PDF isn't at hand, label the text "STE-style draft" and say the dictionary check is pending.
- To get the PDF: `curl -A "Mozilla/5.0" -O https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf`. It is AES-encrypted with an empty password, so pypdf needs `cryptography` to read it. For a strict check, extract the word list locally and check each word. Keep the list out of any repo, because ASD does not allow redistribution.

## Writing rules (Issue 9, Part 1)

| Rule | What it says | In practice |
|---|---|---|
| 1.2–1.4 | approved words, only as their part of speech, meaning and forms | strict only; see the dictionary notes below |
| 1.11 | one technical noun per item | never vary a term for style: "kernel", "launch" and "op" are three different things to a reader |
| 2.1 | multi-word nouns of at most three words | "user session cache cleanup job" → "the job that removes old sessions from the cache" |
| 3.2 | verb forms: infinitive, imperative, simple present, simple past, simple future, past participle as adjective | no progressive ("is running") and no perfect ("has written") |
| 3.4 | no auxiliary verbs to build complex verb constructions | "should have been checked" → "check" or "we did not check" |
| 3.5 | "-ing" only in a technical noun or its modifier | "the routing table" is fine; "routing the request" is not (strict) |
| 3.6 | active voice; passive in descriptions only when the agent is unknown | "The kernel writes the cache", not "The cache is written" |
| 3.7 | use a verb for an action, not a noun | "do an installation of" → "install" |
| 4.2 | don't omit words or use contractions to shorten sentences | keep "the", "a" and "that"; telegraphic text is ambiguous |
| 4.3 | vertical lists for complex text | steps, options and parallel items go in lists; number a list only when order matters |
| 4.4 | connecting words between sentences that are related | approved: "and", "but", "then", "thus", "as a result", "at the same time". "so" is not approved |
| 5.1 | instructions: at most 20 words per sentence | split anything longer |
| 5.2 | one instruction per sentence, unless the actions are simultaneous | "Remove the cover. Disconnect the cable." |
| 5.3 | instructions in the imperative | "Run the test", not "You should run the test" |
| 5.4 | a condition the reader must know comes first, then a comma | "If the build fails, read the log." |
| 6.1–6.2 | give information gradually; key words give structure | main idea first, then detail |
| 6.3 | descriptions: at most 25 words per sentence | |
| 6.5–6.6 | one topic per paragraph, at most six sentences | topic sentence first |
| 7.1–7.3 | safety text: signal word, then a clear command or condition, then the risk | put a warning before the step it applies to |
| 8.1 | no semicolons | split the sentence |
| 8.5–8.7 | word counting: a number with its unit, an identifier, quoted text or a parenthetical each count as one word; a hyphenated word counts as one | so `fp8_paged_mqa_logits` and "128 KB" count as one word each |
| 9.3 | no phrasal verbs | strict: "turn off" → "stop"; 80%: literal ones are fine, figurative ones never ("kick off", "figure out") |
| 9.4 | consistent style | same structure for the same kind of sentence |

## Software words

In text about software, verbs for computer processes (run a test, call a function, return a value, log a message) are technical verbs: Rule 1.12, category 2, "computer processes and applications". Code names (`parse_args`, `MAX_RETRIES`) are technical nouns. List the technical words you relied on when the user asks for strict STE. Outside software, the dictionary replaces "run" with OPERATE.

Keep notes about the text, such as which checks you did or which claims you corrected, outside the STE body. STE has no "I", so these notes read badly inside it.

## Dictionary notes (Part 2), checked in the Issue 9 PDF

These swaps are in the dictionary as unapproved words with their approved alternative:

| Unapproved | Approved | Example in the dictionary |
|---|---|---|
| commence | START (v) | |
| ensure | MAKE SURE (v) | MAKE SURE THAT THE… |
| utilize | USE (v) | THE SOFTWARE USES… |
| prior to | BEFORE (conj/prep) | BEFORE YOU… |
| terminate | STOP (v) | STOP THE TEST |
| facilitate | HELP (v) | |

Watch the trap: **APPROXIMATELY (adv) is approved**, and **ABOUT is approved only as a preposition meaning "concerned with"** (Part 2, entries ABOUT and APPROXIMATELY). The dictionary's own example turns "Drain about 2 liters of fuel" into "DRAIN APPROXIMATELY 2 LITERS OF FUEL". Some STE cheat sheets get this backwards.

Plain-English swaps that the dictionary does not list, useful in 80% mode only: "in order to" → "to", "leverage" → "use", "numerous" → "many", "a number of" → "some" or the number.

## Before and after

Before (28 words, two passives, a perfect tense, "in order to", "ensure"):
> In order to ensure that stale entries are not returned to clients, the cache is invalidated by the writer whenever a record has been updated by the service.

After (80% STE):
> The service updates a record. Then the writer removes that record from the cache. Thus, clients do not get old data.

## Check

`scripts/ste_lint.py <file>` (or text on stdin; add `--strict` for strict mode) flags these breaks, with the rule number for each: sentences over 20/25 words, likely passives, progressive and perfect tenses, semicolons, the dictionary swaps above, common phrasal verbs, and -ing words (strict only). It counts words roughly, not by the Rule 8.6 conventions, and it can't check meaning or the dictionary as a whole. Read each flag and decide.
