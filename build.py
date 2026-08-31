#!/usr/bin/env python3
"""build.py — parse the Apertium nor-eng bilingual dictionary into SQLite.

Source: apertium-nor-eng (GPL), the purpose-built Norwegian<->English bilingual
lexicon. Each <e> in the 'main' section pairs a Norwegian lemma (<l>) with an
English lemma (<r>), each carrying POS tags (<s n=.../>). We flatten those into
one indexed table so lookups in either direction are instant and offline.

Optionally enriched later from Wiktionary (kaikki.org) for glosses/examples.
"""
import re, sqlite3, sys
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
DIX  = HERE / "sources-apertium-nor-eng.dix"
DB   = HERE / "dict.sqlite"


def side_text(el):
    """Lemma text from an <l>/<r>: text + multiword blanks (<b/>) + glue (<g>),
    stopping the lemma at the POS tags (<s>). Returns (lemma, first_pos)."""
    parts, pos = [], None
    if el.text:
        parts.append(el.text)
    for child in el:
        tag = child.tag
        if tag == "s":
            if pos is None:
                pos = child.get("n")
        elif tag == "b":
            parts.append(" ")
        elif tag == "g":            # glued multiword: keep inner text
            if child.text:
                parts.append(child.text)
        if child.tail:
            parts.append(child.tail)
    lemma = re.sub(r"\s+", " ", "".join(parts)).strip()
    return lemma, pos


def main():
    if not DIX.exists():
        sys.exit(f"missing source: {DIX}")
    tree = ET.parse(DIX)
    root = tree.getroot()

    rows = []
    for section in root.findall("section"):
        for e in section.findall("e"):
            restrict = e.get("r", "")          # '', 'LR', or 'RL'
            p = e.find("p")
            if p is None:
                continue
            l, r = p.find("l"), p.find("r")
            if l is None or r is None:
                continue
            no, no_pos = side_text(l)
            en, en_pos = side_text(r)
            if not no or not en:               # skip paradigm/tag-only entries
                continue
            if not re.search(r"[a-zA-ZæøåÆØÅ]", no) or not re.search(r"[a-zA-Z]", en):
                continue
            rows.append((no, no_pos or "", en, en_pos or "", restrict))

    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE pair(
        no TEXT, no_pos TEXT, en TEXT, en_pos TEXT, restrict TEXT)""")
    con.executemany("INSERT INTO pair VALUES (?,?,?,?,?)", rows)
    # normalized lookup columns + indexes for fast case-insensitive both-way search
    con.execute("ALTER TABLE pair ADD COLUMN no_lc TEXT")
    con.execute("ALTER TABLE pair ADD COLUMN en_lc TEXT")
    con.execute("UPDATE pair SET no_lc=lower(no), en_lc=lower(en)")
    con.execute("CREATE INDEX idx_no ON pair(no_lc)")
    con.execute("CREATE INDEX idx_en ON pair(en_lc)")
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM pair").fetchone()[0]
    uno = con.execute("SELECT COUNT(DISTINCT no_lc) FROM pair").fetchone()[0]
    uen = con.execute("SELECT COUNT(DISTINCT en_lc) FROM pair").fetchone()[0]
    con.close()
    print(f"built {DB.name}: {n} pairs  ({uno} distinct NO headwords, {uen} distinct EN)")
    print(f"size: {DB.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
