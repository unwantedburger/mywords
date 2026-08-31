"""mywords — slim Norwegian<->English dictionary + active-vocab drills.

  mywords glissen          # NO->EN
  mywords sudorific        # EN: Norwegian equiv if clean, else definition + synonyms
  mywords --throw 5        # random items from your word-of-day list
  mywords --throw 5 -k idiom
"""
import argparse, json, random, sys
from importlib.resources import files

DATA = files("mywords") / "data"


def _load(name):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"mywords: missing data file {name}")


def lookup(word):
    d = _load("dict.json")
    w = word.strip().lower()
    out = []

    e = d["no2en"].get(w)
    if e:
        pos = f" ({e['pos']})" if e.get("pos") else ""
        out.append(f"\033[1m{e['word']}\033[0m{pos} → " + "; ".join(e["en"][:3]))

    e = d["en2no"].get(w)
    if e:                                   # clean Norwegian equivalent exists
        out.append(f"\033[1m{e['word']}\033[0m → " + ", ".join(e["no"][:6]))
    elif w in d["endef"]:                   # else: definition + synonyms
        de = d["endef"][w]
        line = f"\033[1m{w}\033[0m → {de['def']}"
        if de.get("syn"):
            line += f"   \033[2msyn: {', '.join(de['syn'])}\033[0m"
        out.append(line)

    if not out:
        pool = list(d["no2en"]) + list(d["en2no"]) + list(d["endef"])
        sug = sorted({k for k in pool if k.startswith(w)})[:10]
        print(f"'{word}' not found." + (f"  did you mean: {', '.join(sug)}" if sug else ""))
        sys.exit(1)
    print("\n".join(out))


def throw(n, kind):
    items = _load("wordofday.json")
    if kind in ("idiom", "word"):
        want = "phrase" if kind == "idiom" else "word"
        items = [i for i in items if i["kind"] == want]
    if not items:
        sys.exit("mywords: no matching word-of-day items")
    for i in random.sample(items, min(n, len(items))):
        flag = "🇳🇴" if i["lang"] == "no" else "🇬🇧"
        print(f"  {flag}  {i['text']}")


def main():
    ap = argparse.ArgumentParser(prog="mywords",
                                 description="Norwegian<->English dictionary + vocab drills")
    ap.add_argument("word", nargs="*", help="word or phrase to look up")
    ap.add_argument("-t", "--throw", type=int, metavar="N",
                    help="serve N random items from your word-of-day list")
    ap.add_argument("-k", "--kind", choices=["word", "idiom", "any"], default="any",
                    help="with --throw: restrict to words or idioms")
    args = ap.parse_args()

    if args.throw is not None:
        throw(args.throw, args.kind)
    elif args.word:
        lookup(" ".join(args.word))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
