# nodict

Slim offline **Norwegian ⇄ English** dictionary + active-vocabulary drills, as a
single `nodict` CLI. A genuine dictionary with the trivial basics trimmed out,
plus your Beeminder word-of-day list for writing sessions.

```
$ nodict glissen
glissen (adj) → spread out, not crowded

$ nodict sudorific                 # no clean Norwegian word → definition + synonyms
sudorific → inducing perspiration   syn: diaphoretic, sudatory

$ nodict --throw 5                 # 5 random items from your word-of-day list
  🇬🇧  Behind the power curve
  🇳🇴  Stilt på prøve
  ...
$ nodict --throw 5 -k idiom        # phrases/idioms only
```

## Install

```
pipx install git+https://github.com/unwantedburger/nodict.git
# or:  pip install git+https://github.com/unwantedburger/nodict.git
```

Pure-Python, **no runtime dependencies** — the dictionary and word list ship as
JSON inside the package. Gives you a `nodict` command on your PATH.

## What it does

- **Norwegian → English** (the strong direction): Wiktionary glosses (kaikki.org)
  + Apertium pairs.
- **English →**: a clean Norwegian equivalent when one exists, otherwise a short
  **definition + synonyms** (WordNet) — a basic thesaurus.
- The trivial basics are trimmed by word frequency (Zipf ≥ 4.5), so lookups land
  on words worth checking.
- **`--throw N`**: random pulls from `wordofday.json` — your active-vocabulary
  target list, ingested + cleaned from Beeminder, kept separate from the
  dictionary. Work them into today's writing.

Counts: ~80k NO→EN, ~24k EN→NO, ~84k English definitions, ~600 word-of-day items.

## Rebuild / refresh (dev)

Everything under `tools/`. Needs the build venv (`.buildenv`, has `wordfreq` +
`wn`) and the Wiktionary source `tools/kaikki-nob.jsonl` (78 MB, gitignored —
re-download from kaikki.org's Norwegian Bokmål page).

```
.buildenv/bin/python tools/build.py            # rebuild dict.json
python3 tools/ingest-wordofday.py              # refresh word-of-day from Beeminder
```

Tune `TRIM_ZIPF` in `tools/build.py` to trim more/fewer basics.

## Licence

Wiktionary/kaikki = CC-BY-SA; Apertium = GPL; WordNet (OEWN) = CC-BY. Personal
use is fine; keep attribution + share-alike if ever redistributed.
