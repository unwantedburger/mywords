#!/usr/bin/env python3
"""build.py — build the slim Norwegian<->English dictionary as JSON (no DB).

A *genuine* dictionary (Wiktionary depth) with the trivial basics trimmed away,
so lookups land on words you'd actually stop to check while writing. Output is
plain JSON so it can be inspected and hand-edited.

Sources:
  - kaikki-nob.jsonl : Wiktionary Norwegian Bokmål (kaikki.org). Norwegian
    headwords with English glosses → NO→EN (primary: `nodict glissen`).
  - sources-apertium-nor-eng.dix : Apertium EN↔NO pairs, folded into EN→NO.
  - EN→NO is also mined by inverting short synonym-style NO glosses.

Trim: drop headwords with Zipf frequency (wordfreq) >= TRIM_ZIPF — everyday
basics a fluent speaker never looks up (hund/dog≈4.7). Sophisticated words
(glissen≈2.2) sit well below and stay. Frequencies applied here; runtime needs
nothing. Output → dict.json  = {"no2en": {...}, "en2no": {...}}.
"""
import json, re
from pathlib import Path
import xml.etree.ElementTree as ET
import wordfreq

HERE      = Path(__file__).resolve().parent
KAIKKI    = HERE / "kaikki-nob.jsonl"
DIX       = HERE / "sources-apertium-nor-eng.dix"
OUT       = HERE.parent / "src/mywords/data/dict.json"
TRIM_ZIPF = 4.5
SKIP_POS  = {"name", "suffix", "prefix", "character", "symbol"}


def clean(s):
    return re.sub(r"\s+", " ", s).strip()


def en_terms(g):
    out = []
    for part in re.split(r"[;,/]", g):
        p = re.sub(r"^\s*(to|a|an|the)\s+", "", part.strip().lower())
        p = re.sub(r"\(.*?\)", "", p).strip()
        if p and len(p.split()) <= 2 and re.fullmatch(r"[a-zæøå' -]+", p):
            out.append(p)
    return out


def main():
    no2en = {}            # headword -> {pos, glosses:[...]}
    en2no = {}            # headword -> set(no words)

    for line in open(KAIKKI, encoding="utf-8"):
        o = json.loads(line)
        pos = o.get("pos")
        if pos in SKIP_POS:
            continue
        w = (o.get("word") or "").strip()
        if not w:
            continue
        glosses = []
        for s in o.get("senses", []):
            for g in (s.get("glosses") or []):
                g = clean(g)
                if g and g not in glosses:
                    glosses.append(g)
        if not glosses or wordfreq.zipf_frequency(w.lower(), "nb") >= TRIM_ZIPF:
            continue
        key = w.lower()
        ent = no2en.setdefault(key, {"word": w, "pos": pos or "", "en": []})
        for g in glosses:
            if g not in ent["en"]:
                ent["en"].append(g)
            for t in en_terms(g):
                en2no.setdefault(t, set()).add(w)

    # Apertium clean pairs strengthen BOTH directions (kaikki misses words like
    # 'innfløkt'; Apertium has them). NO→EN glosses from Apertium are the English
    # lemma itself.
    if DIX.exists():
        for e in ET.parse(DIX).getroot().iter("e"):
            p = e.find("p")
            if p is None:
                continue
            l, r = p.find("l"), p.find("r")
            if l is None or r is None:
                continue
            no, en = (l.text or "").strip(), (r.text or "").strip()
            if not (no and en and re.search(r"[a-zæøå]", no.lower()) and re.search(r"[a-z]", en.lower())):
                continue
            en2no.setdefault(en.lower(), set()).add(no)
            if wordfreq.zipf_frequency(no.lower(), "nb") < TRIM_ZIPF:
                ent = no2en.setdefault(no.lower(), {"word": no, "pos": "", "en": []})
                if en not in ent["en"]:
                    ent["en"].append(en)

    en_out = {}
    for en, nos in en2no.items():
        # English headwords only: no Norwegian letters (drops 'rød'→'Rød' noise),
        # and skip the everyday basics.
        if any(c in en for c in "æøå") or wordfreq.zipf_frequency(en, "en") >= TRIM_ZIPF:
            continue
        en_out[en] = {"word": en, "no": sorted(nos)[:10]}

    # English definitions + synonyms (WordNet), pre-extracted so runtime needs no
    # deps. The CLI shows a Norwegian equivalent when one exists, else this.
    endef = {}
    import wn
    W = wn.Wordnet("oewn:2021")
    for lemma in W.words():
        w = lemma.lemma()
        wl = w.lower()
        if wl in endef or " " in wl:
            continue
        ss = W.synsets(w)
        if not ss:
            continue
        d = ss[0].definition()
        syn = []
        for s in ss[:3]:
            for l in s.lemmas():
                if l.lower() != wl and l not in syn:
                    syn.append(l)
        endef[wl] = {"def": d, "syn": syn[:6]}

    OUT.write_text(json.dumps({"no2en": no2en, "en2no": en_out, "endef": endef},
                              ensure_ascii=False), encoding="utf-8")
    print(f"built {OUT.name}: {len(no2en)} NO→EN + {len(en_out)} EN→NO + {len(endef)} EN defs")
    print(f"size: {OUT.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
