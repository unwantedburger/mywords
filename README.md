# nodict — slim Norwegian ⇄ English dictionary + active-vocab drills

Offline, plain-JSON, hand-editable. A *genuine* dictionary with the trivial
basics trimmed out, plus your Beeminder word-of-day list for writing drills.

```
$ nodict glissen
glissen (adj)  🇳🇴→🇬🇧
   spread out, not crowded

$ nodict --throw 5          # 5 random items from your word-of-day list
  🇬🇧  Behind the power curve
  🇳🇴  Stilt på prøve
  ...
$ nodict --throw 5 -k idiom # phrases/idioms only
```

## Two stores (both plain JSON)

- **`dict.json`** — the dictionary. Norwegian→English is the strong direction
  (Wiktionary glosses via kaikki.org + Apertium pairs). English→Norwegian is
  best-effort for now. Basics trimmed by word frequency (`wordfreq`, Zipf ≥ 4.5
  dropped) so lookups land on words worth checking.
- **`wordofday.json`** — your active-vocabulary target list, ingested + cleaned
  from Beeminder `wordofday` (deduped, noise/empties dropped). Kept separate from
  the dictionary. `--throw N` serves random items for a writing session.

## Use / install

```
ln -s ~/dev/nodict/nodict ~/.local/bin/nodict     # then: nodict <word>
```

Runtime needs only python3 — `dict.json` + `wordofday.json` ship ready to use.

## Rebuild / refresh

```
# dictionary (needs kaikki-nob.jsonl + the .buildenv venv with wordfreq):
.buildenv/bin/python build.py
# refresh the word-of-day list from Beeminder (token read in-process):
python3 ingest-wordofday.py
```

`kaikki-nob.jsonl` (78 MB Wiktionary source) is gitignored — re-download from
kaikki.org's Norwegian Bokmål page. Tune `TRIM_ZIPF` in build.py to trim
more/fewer basics.

## Licence

Wiktionary/kaikki = CC-BY-SA; Apertium = GPL. Fine for personal use; keep
attribution + share-alike if ever redistributed.
