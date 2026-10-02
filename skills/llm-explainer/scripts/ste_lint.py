#!/usr/bin/env python3
"""Heuristic ASD-STE100 (Issue 9) checks for explanation text.

Usage: ste_lint.py [--strict] [file]   (reads stdin when no file is given)

Flags, with the Issue 9 rule each one relates to:
  sentences over 20 words (instructions, R5.1) or 25 (descriptions, R6.3),
  likely passives (R3.6), progressive/perfect tenses (R3.2/3.4), semicolons
  (R8.1), unapproved words with a dictionary alternative (Part 2), figurative
  phrasal verbs (R9.3; all phrasal verbs with --strict), plain-English swaps
  (80% mode), and -ing words (R3.5, --strict only).
Word counts are rough: an inline code span counts as one word (close to R8.6),
but numbers with units and quoted text are not merged. Markdown fences and
URLs are ignored. Every flag is a prompt to look, not a verdict.
"""
import re
import sys

# Unapproved words whose approved alternative was checked in the Issue 9 dictionary.
STE_DICT = {
    "commence": "START", "ensure": "MAKE SURE", "utilize": "USE", "utilise": "USE",
    "prior to": "BEFORE", "terminate": "STOP", "facilitate": "HELP",
}
# Not dictionary entries; plain-English preferences for 80% mode.
PLAIN = {
    "in order to": "to", "leverage": "use", "numerous": "many",
    "a number of": "some / the number", "in the event that": "if",
    "under the hood": "say what happens", "ballpark": "approximately",
}
FIGURATIVE_PHRASAL = ["kick off", "figure out", "end up", "come up with", "look into",
                      "boil down", "spin up", "tease out", "dig into", "rule out"]
LITERAL_PHRASAL = ["turn off", "turn on", "set up", "carry out", "find out", "point out",
                   "go through", "fill in", "take out", "put in", "check out", "shut down",
                   "pick up", "break down", "back up", "write down", "fall back", "roll back"]
IMPERATIVE_START = re.compile(
    r"^(add|apply|build|check|copy|delete|do|fix|install|keep|make|move|open|put|read|"
    r"remove|run|set|start|stop|turn|use|write|load|pick|give|send|tell|drain|close|push)\b", re.I)
PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being|gets|got)\s+(\w+ly\s+)?(\w+ed|\w+en|built|made|done|run|set|put|kept|sent|held|found|known|shown|written|read)\b", re.I)
PROGRESSIVE = re.compile(r"\b(is|are|was|were|be|been)\s+\w+ing\b", re.I)
PERFECT = re.compile(r"\b(has|have|had)\s+(\w+ly\s+)?(\w+ed|been|done|made|written|run|set|built|shown)\b", re.I)
ING_OK = {"string", "thing", "nothing", "something", "anything", "everything", "during",
          "bring", "ring", "king", "spring", "wing", "ceiling", "sibling", "padding",
          "embedding", "routing", "caching", "scheduling", "sampling", "training", "logging",
          "warning", "setting", "settings", "existing", "following", "remaining"}


def clean(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "IDENT", text)
    text = re.sub(r"https?://\S+", "URL", text)
    text = re.sub(r"^\s*\|.*$", "\n", text, flags=re.M)                    # table rows: not prose
    text = re.sub(r"^\s*#.*$", "\n", text, flags=re.M)                      # headings: not sentences
    text = re.sub(r"^\s*([-*_=]\s*){3,}$", "\n", text, flags=re.M)        # rules: paragraph break
    text = re.sub(r"^(\s*)(\d+\.|[-*+])\s+", r"\n\1", text, flags=re.M)  # each list item stands alone
    text = re.sub(r"\[[^\]]{1,20}\]\s*", "", text)                       # tags like [no log]
    text = re.sub(r"^\s*[>|#]+\s*", "", text, flags=re.M)
    text = re.sub(r"[*_]{1,2}", "", text)                                   # bold / italic markers
    return text


def sentences(text):
    out = []
    for block in re.split(r"\n\s*\n|\n(?=\s*(?:\d+\.|[-*])\s)", text):
        block = " ".join(block.split())
        out += [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"(])", block) if s.strip()]
    return out


def has(phrase, low):
    return re.search(r"\b" + re.escape(phrase) + r"\b", low) is not None


def main():
    strict = "--strict" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--strict"]
    text = open(args[0], encoding="utf-8").read() if args else sys.stdin.read()
    flagged = 0
    for i, s in enumerate(sentences(clean(text)), 1):
        if len(re.findall(r"[\u3000-\u9fff\uac00-\ud7af]", s)) > len(s) * 0.2:
            continue  # mostly CJK: not English text, skip
        words = re.findall(r"[A-Za-z0-9][\w'’/.-]*", s)
        low = s.lower()
        notes = []
        instr = bool(IMPERATIVE_START.match(s))
        limit = 20 if instr else 25
        if len(words) > limit:
            notes.append(f"{len(words)} words > {limit} (R{'5.1' if instr else '6.3'})")
        m = PASSIVE.search(s)
        if m:
            notes.append(f"passive? '{m.group(0)}' (R3.6)")
        m = PROGRESSIVE.search(s)
        if m:
            notes.append(f"progressive '{m.group(0)}' (R3.2)")
        m = PERFECT.search(s)
        if m:
            notes.append(f"perfect tense '{m.group(0)}' (R3.2/3.4)")
        if ";" in s:
            notes.append("semicolon (R8.1)")
        for bad, good in STE_DICT.items():
            if has(bad, low):
                notes.append(f"'{bad}' -> {good} (Part 2)")
        for bad, good in PLAIN.items():
            if has(bad, low):
                notes.append(f"'{bad}' -> {good} (plain English)")
        for pv in FIGURATIVE_PHRASAL + (LITERAL_PHRASAL if strict else []):
            if has(pv, low):
                notes.append(f"phrasal verb '{pv}' (R9.3)")
        if strict:
            ings = [w for w in re.findall(r"\b[a-z]+ing\b", low) if w not in ING_OK]
            if ings and not PROGRESSIVE.search(s):
                notes.append(f"-ing word {ings[0]!r}: only in technical nouns (R3.5)")
        if notes:
            flagged += 1
            short = s if len(s) <= 110 else s[:107] + "..."
            print(f"[{i}] {short}\n     " + "; ".join(notes))
    print(f"{flagged} sentence(s) flagged" if flagged else "no flags")


if __name__ == "__main__":
    main()
