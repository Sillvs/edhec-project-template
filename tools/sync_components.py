#!/usr/bin/env python3
"""Put the same component stylesheet into every template.

    python3 tools/sync_components.py          # write design/components.css into each template
    python3 tools/sync_components.py --check  # exit 1 if any template has drifted

Why this exists, twice over:

1. The chart stylesheet lived only in `gallery.html`. The gallery's whole job
   is to be copied from, so every chart copied into `slides.html` arrived
   unstyled: a donut as a bare number, a waterfall as a stack of empty divs.
   The failure was silent at copy time and loud at rehearsal time.

2. The two templates already shared 431 byte-identical lines of CSS with
   nothing holding them together. The first fix applied to one file and not
   the other would have left the gallery claiming components the deck does
   not have, and both files would still have rendered fine.

Each template keeps its own full copy, so one file still opens offline on its
own. That is the promise the repository makes, and it is worth a generated
block. `./build.sh` runs `--check` so drift fails the build rather than the
presentation.
"""
import argparse
import difflib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
MASTER = HERE / "design" / "components.css"
TEMPLATES = [HERE / "slides" / "slides.html", HERE / "slides" / "gallery.html"]

OPEN = "/* =====================================================================\n   SHARED COMPONENTS"
CLOSE = "/* ==== END SHARED COMPONENTS ==== */\n"


def block() -> str:
    return MASTER.read_text(encoding="utf-8").rstrip() + "\n\n" + CLOSE


def split(text: str, path: pathlib.Path):
    """Return (before, current_block, after). The block is '' if absent."""
    i = text.find(OPEN)
    if i == -1:
        j = text.rindex("</style>")        # first run: insert at the end of the sheet
        return text[:j], "", text[j:]
    k = text.find(CLOSE, i)
    if k == -1:
        sys.exit(f"{path.name}: shared block opened but never closed. "
                 f"Restore the '{CLOSE.strip()}' line or re-run without --check.")
    k += len(CLOSE)
    return text[:i], text[i:k], text[k:]


TOKENS = HERE / "design" / "tokens.css"
TOKEN_RE = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")


def check_tokens() -> list:
    """design/tokens.css calls itself the reference. Verify that it is one.

    It drifted once already: the templates had --int2 raised to clear AA and
    an obsolete --olive deleted, while the reference still carried both. A
    reference nobody verifies is a second opinion, and the next template built
    from it inherits the failure.
    """
    if not TOKENS.exists():
        return []
    want = dict(TOKEN_RE.findall(TOKENS.read_text(encoding="utf-8")))
    bad = []
    for p in TEMPLATES:
        text = p.read_text(encoding="utf-8")
        root = text[text.index(":root{"):text.index("}", text.index(":root{"))]
        have = dict(TOKEN_RE.findall(root))
        for k, v in want.items():
            if k in have and have[k].strip() != v.strip():
                bad.append(f"  {p.relative_to(HERE)}: {k} is {have[k].strip()}, "
                           f"tokens.css says {v.strip()}")
    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify only, exit 1 if a template has drifted")
    args = ap.parse_args()

    if not MASTER.exists():
        sys.exit(f"missing {MASTER}")
    want = block()
    drifted = []

    for p in TEMPLATES:
        text = p.read_text(encoding="utf-8")
        before, have, after = split(text, p)
        name = p.relative_to(HERE)

        if args.check:
            if have == want:
                print(f"  {name}: in sync")
            else:
                drifted.append(name)
                diff = list(difflib.unified_diff(
                    want.splitlines(), have.splitlines(),
                    "design/components.css", str(name), lineterm="", n=1))
                print(f"  {name}: DRIFTED, {sum(1 for d in diff if d[:1] in '+-' and d[1:2] != '-')} lines differ")
                for d in diff[2:12]:
                    print(f"      {d}")
            continue

        p.write_text(before + want + after, encoding="utf-8")
        print(f"  {name}: {'updated' if have else 'block inserted'} "
              f"({len(want.splitlines())} lines)")

    if args.check:
        tokens = check_tokens()
        if tokens:
            print("\ndesign/tokens.css disagrees with a template:")
            print("\n".join(tokens))
            print("\nFix whichever is wrong. tokens.css is meant to be the reference,")
            print("so a template that is right and a reference that is stale is the")
            print("worse of the two failures: the next template inherits the stale value.")
        else:
            print("  design/tokens.css: agrees with both templates")
        if drifted or tokens:
            if drifted:
                print("\nA template was edited inside the generated block, or")
                print("design/components.css changed without a sync. Run:")
                print("    python3 tools/sync_components.py")
            sys.exit(1)


if __name__ == "__main__":
    main()
