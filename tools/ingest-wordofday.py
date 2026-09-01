#!/usr/bin/env python3
"""ingest-wordofday.py — pull Staale's Beeminder 'wordofday' captures, clean
them, and store them as wordofday.json: his active-vocabulary target list, kept
separate from the dictionary. `nodict --throw N` serves random items from here.

Cleaning: strip, drop empties + pure-punctuation junk, dedupe (case-insensitive,
keeping the first-seen casing). Language is a best guess; kind is word vs phrase.

Language detection (see detect_lang): æøå → 'no' outright, else score tokens
against the NO vs EN dictionaries and only call it Norwegian when it clearly
leans NO. The old "any token is a Norwegian headword → no" test mis-tagged ~23%
of the (mostly-English) corpus because English phrases routinely contain a word
that also exists as a Norwegian headword ("as", "under", "regime", "hat"…).
Default is English; a mislabel-as-English just shows unmarked, which is the safe
failure. (Fixed 2026-09-01 after Staale flagged the flags as "off in a terrible
way".)

Credential (Rule 14): token read in-process from ~/.../secrets.txt and never
printed — not the token, not the built URL.
"""
import json, re, urllib.request, urllib.parse
from pathlib import Path

HERE   = Path(__file__).resolve().parent
DICT   = HERE.parent / "src/mywords/data/dict.json"
OUT    = HERE.parent / "src/mywords/data/wordofday.json"
SECRET = Path.home() / "secrets.txt"


def fetch_comments():
    sec, _ = json.JSONDecoder().raw_decode(SECRET.read_text().lstrip())
    tok, user = sec["auth_token"], sec["username"]
    url = (f"https://www.beeminder.com/api/v1/users/{urllib.parse.quote(user)}"
           f"/goals/wordofday/datapoints.json?auth_token={tok}&count=10000")
    with urllib.request.urlopen(url) as r:          # url holds the token — never print it
        pts = json.load(r)
    return [(p.get("comment") or "").strip() for p in pts]


def detect_lang(text, no_heads, en_heads):
    """Best-guess 'no'/'en'. æøå is decisive; otherwise the text must lean
    clearly Norwegian (more NO-dictionary hits than EN, and at least half its
    tokens in the NO dictionary) — else it defaults to English. Conservative by
    design: an unmarked Norwegian item is far less jarring than a mislabelled one."""
    if re.search(r"[æøåÆØÅ]", text):
        return "no"
    toks = [t for t in re.findall(r"[A-Za-zæøåÆØÅ']+", text.lower()) if len(t) > 1]
    if not toks:
        return "en"
    no_hits = sum(t in no_heads for t in toks)
    en_hits = sum(t in en_heads for t in toks)
    return "no" if (no_hits > en_hits and no_hits >= max(1, len(toks) // 2)) else "en"


def main():
    no_heads, en_heads = set(), set()
    if DICT.exists():
        d = json.loads(DICT.read_text())
        no_heads = set(d["no2en"].keys())
        en_heads = set(d.get("endef", {}).keys()) | set(d.get("en2no", {}).keys())

    seen, items = set(), []
    for c in fetch_comments():
        if not c or not re.search(r"[A-Za-zæøåÆØÅ]", c):   # empty / pure punctuation
            continue
        key = c.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append({"text": c,
                      "lang": detect_lang(c, no_heads, en_heads),
                      "kind": "word" if len(c.split()) == 1 else "phrase"})

    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    nno = sum(1 for i in items if i["lang"] == "no")
    nph = sum(1 for i in items if i["kind"] == "phrase")
    print(f"wrote {OUT.name}: {len(items)} items  ({nph} phrases/idioms, {len(items)-nph} words; "
          f"{nno} tagged NO, {len(items)-nno} EN)  size {OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
