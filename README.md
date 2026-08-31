# nodict — offline Norwegian ⇄ English dictionary

A single-file SQLite dictionary + a small CLI. Offline, instant, zero-budget.

```
$ nodict hund
🇳🇴 hund
   → dog  (noun)

$ nodict freedom
🇬🇧 freedom
   → frihet  (noun)
   → ytringsfrihet  (noun)   # freedom of speech
```

## What it is

- **Data:** [Apertium `nor-eng`](https://github.com/apertium/apertium-nor-eng)
  — the purpose-built open Norwegian⇄English bilingual lexicon (GPL). Clean
  lemma→lemma pairs with part-of-speech.
- **Store:** `dict.sqlite` — **~2.0 MB**, ~24.9k pairs (~19.6k Norwegian
  headwords, ~17.7k English). Indexed both directions.
- **Access:** `nodict <word>` auto-detects the language and shows translations
  both ways. `-s <prefix>` lists suggestions.

## Install

```
ln -s ~/dev/nodict/nodict ~/.local/bin/nodict   # or /usr/local/bin
# optional short alias in ~/.zshrc:  alias ord='nodict'
```

## Rebuild

```
python3 build.py          # re-parses sources-apertium-nor-eng.dix -> dict.sqlite
```

## Coverage & making it richer

v1 covers ~20k common headwords with clean translations, but no definitions,
senses, or examples, and misses rarer/technical words.

To go deeper there's a bigger source: **Wiktionary via kaikki.org** (the
Norwegian Bokmål extract is ~68 MB of JSONL with definitions, senses, usage
examples, and inflections). Merging it in would:
- add definitions + example sentences + inflected-form lookups,
- widen coverage to 100k+ headwords,
- grow the DB to roughly **15–40 MB** depending on how much is kept.

The schema (`pair` table) is designed to be enriched: a `sense`/`example`
column set can be joined on without changing the CLI. Say the word and I'll wire
the Wiktionary layer in.

## Licence note

Apertium data is GPL; Wiktionary is CC-BY-SA. Fine for personal use; if ever
redistributed, keep attribution + share-alike.
