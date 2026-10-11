#!/usr/bin/env python3
"""Embed the logo into every template so one file really is one file.

    python3 tools/inline_assets.py          # rewrite the templates in place
    python3 tools/inline_assets.py --check  # exit 1 if any relative asset is left

Why this exists: the logo was referenced as a relative `url("edhec-logo.svg")`.
Mail just the HTML to a jury and the mark is gone, and because it is a CSS
background there is no broken-image icon, only white space on the title slide
and every slide mark. The failure path was the delivery path.

The SVG goes in once per file as a `--logo` token and the rules reference it,
rather than three copies of the same data URI. Percent-encoding is used instead
of base64 because for SVG it is about 20% smaller (28.9 KB against 36.1 KB here)
and stays readable in a diff.

`design/edhec-logo.svg` remains the master. Re-run this after replacing it.
"""
import argparse
import pathlib
import re
import sys
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent.parent
MASTER = HERE / "design" / "edhec-logo.svg"
TEMPLATES = [
    HERE / "slides" / "slides.html",
    HERE / "slides" / "gallery.html",
    HERE / "paper" / "paper.html",
]
TOKEN_LINE = "  --logo:url(\"data:image/svg+xml,{}\");\n"
# Scan only OUTSIDE data URIs. An inlined SVG carries its own internal
# fragment references (url(%23clip0...)), which are not external files and
# must not be reported as missing assets.
DATA_URI = re.compile(r'data:[^"\')]+')
CSS_ASSET = re.compile(r'url\(["\']?(?!data:)([^"\')#%]+)["\']?\)')
IMG_ASSET = re.compile(r'src="(?!data:)([^"]+)"')


def data_uri(svg_path: pathlib.Path) -> str:
    raw = svg_path.read_bytes()
    # collapse whitespace between tags only, so no attribute value is touched
    mini = re.sub(rb">\s+<", b"><", raw)
    mini = re.sub(rb"\s{2,}", b" ", mini).strip()
    # '#' MUST be encoded: raw, it starts a fragment identifier and silently
    # truncates the data URI, so the whole logo renders as nothing. '<' and '>'
    # are encoded for the same class of reason, cheaply.
    return urllib.parse.quote(mini.decode("utf-8"), safe="~()*!.'-_ =:/;,")


def inline(path: pathlib.Path, encoded: str) -> str:
    s = path.read_text(encoding="utf-8")
    before = s.count('url("edhec-logo.svg")')
    if before:
        s = s.replace('url("edhec-logo.svg")', "var(--logo)")
    # the token goes at the end of :root so a hand-edited palette stays readable
    if "--logo:" not in s:
        s = re.sub(r"(\n)(\}\n(?:\*\{box-sizing|\s*\n))",
                   lambda m: TOKEN_LINE.format(encoded) + m.group(2),
                   s, count=1)
        if "--logo:" not in s:          # paper.html closes :root differently
            s = s.replace("\n}\n\n@page{", "\n" + TOKEN_LINE.format(encoded) + "}\n\n@page{", 1)
    else:
        s = re.sub(r'  --logo:url\("data:image/svg\+xml,[^"]*"\);\n',
                   TOKEN_LINE.format(encoded), s, count=1)
    path.write_text(s, encoding="utf-8")
    return f"{path.relative_to(HERE)}: {before} reference(s) inlined"


def check() -> int:
    fail, warn = [], []
    for p in TEMPLATES:
        s = DATA_URI.sub("", p.read_text(encoding="utf-8"))
        for m in CSS_ASSET.finditer(s):
            fail.append(f"{p.relative_to(HERE)}: {m.group(1)}")
        for m in IMG_ASSET.finditer(s):
            warn.append(f"{p.relative_to(HERE)}: {m.group(1)}")

    if warn:
        print("Images referenced by file. These are your content, not the design,")
        print("so this is a choice, not a defect. Inline them if the file travels alone:")
        for w in warn:
            print(f"  {w}")
    if fail:
        print("\nDesign assets still referenced by file. A mailed single file loses these")
        print("silently, with no broken-image icon:")
        for b in fail:
            print(f"  {b}")
        return 1
    print("\nEvery design asset is inline: the templates travel alone.")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify only, exit 1 if a relative asset is left")
    args = ap.parse_args()

    if args.check:
        sys.exit(check())

    if not MASTER.exists():
        sys.exit(f"missing {MASTER}")
    encoded = data_uri(MASTER)
    print(f"logo: {MASTER.stat().st_size} bytes -> {len(encoded)} encoded")
    for p in TEMPLATES:
        if p.exists():
            print("  " + inline(p, encoded))


if __name__ == "__main__":
    main()
