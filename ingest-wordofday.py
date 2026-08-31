#!/usr/bin/env python3
"""ingest-wordofday.py — pull Staale's Beeminder 'wordofday' captures, clean
them, and store them as wordofday.json: his active-vocabulary target list, kept
separate from the dictionary. `nodict --throw N` serves random items from here.

Cleaning: strip, drop empties + pure-punctuation junk, dedupe (case-insensitive,
keeping the first-seen casing). Language is a best guess (æøå or a known
Norwegian headword → 'no', else 'en'); kind is word vs phrase.

Credential (Rule 14): token read in-process from ~/.../secrets.txt and never
printed — not the token, not the built URL.
"""
import json, re, urllib.request, urllib.parse
from pathlib import Path

HERE   = Path(__file__).resolve().parent
DICT   = HERE / "dict.json"
OUT    = HERE / "wordofday.json"
SECRET = Path.home() / "secrets.txt"


def fetch_comments():
    sec, _ = json.JSONDecoder().raw_decode(SECRET.read_text().lstrip())
    tok, user = sec["auth_token"], sec["username"]
    url = (f"https://www.beeminder.com/api/v1/users/{urllib.parse.quote(user)}"
           f"/goals/wordofday/datapoints.json?auth_token={tok}&count=10000")
    with urllib.request.urlopen(url) as r:          # url holds the token — never print it
        pts = json.load(r)
    return [(p.get("comment") or "").strip() for p in pts]


def main():
    no_heads = set()
    if DICT.exists():
        no_heads = set(json.loads(DICT.read_text())["no2en"].keys())

    seen, items = set(), []
    for c in fetch_comments():
        if not c or not re.search(r"[A-Za-zæøåÆØÅ]", c):   # empty / pure punctuation
            continue
        key = c.lower()
        if key in seen:
            continue
        seen.add(key)
        words = re.findall(r"[A-Za-zæøåÆØÅ']+", c)
        is_no = bool(re.search(r"[æøåÆØÅ]", c)) or any(w.lower() in no_heads for w in words)
        items.append({"text": c,
                      "lang": "no" if is_no else "en",
                      "kind": "word" if len(c.split()) == 1 else "phrase"})

    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    nno = sum(1 for i in items if i["lang"] == "no")
    nph = sum(1 for i in items if i["kind"] == "phrase")
    print(f"wrote {OUT.name}: {len(items)} items  ({nph} phrases/idioms, {len(items)-nph} words; "
          f"{nno} tagged NO, {len(items)-nno} EN)  size {OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
