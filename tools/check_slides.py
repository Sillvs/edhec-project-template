#!/usr/bin/env python3
"""Check rendered slides for the two failures a thumbnail will not show you.

    python3 tools/check_slides.py .build/slides.json [more.json ...]

**Overflow.** A slide that runs past 1280x720 still exports, still looks
plausible in a contact sheet, and loses its last line. Somebody hands that in.

**Contrast.** Every run of text is measured against the colour actually painted
behind it, not against what the CSS appears to say. Two white-on-gold pairings
shipped for weeks because the rules that set the colour and the background live
in different selectors, and the only file that rendered them was the gallery.

Both checks read the geometry the layout extractor pulls out of Chrome, so they
measure what the browser drew rather than what the stylesheet implies. Neither
could be done by grepping CSS, which is exactly why neither was being done.

Exits 1 on any failure, with the slide, the element and the number.
"""
import json
import pathlib
import sys

AA = 4.5
# Below this, text is decoration. The giant slide number sits at 6% opacity
# behind the content and is not meant to be read; holding it to AA would mean
# deleting it, which is the wrong answer to the right question.
DECORATIVE_OPACITY = 0.25
# Large text is allowed 3:1 by WCAG: 24px, or 18.66px at weight 700+.
LARGE_PX, LARGE_BOLD_PX, LARGE_AA = 24.0, 18.66, 3.0


def lum(hex6: str) -> float:
    c = [int(hex6[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def ratio(a: str, b: str) -> float:
    l1, l2 = sorted((lum(a), lum(b)), reverse=True)
    return (l1 + .05) / (l2 + .05)


def over(fg: dict, bg: str) -> str:
    """Flatten a partly transparent colour onto an opaque background."""
    a = fg.get("a", 1)
    if a >= .999:
        return fg["c"]
    f, b = fg["c"], bg
    return "".join(f"{round(int(f[i:i+2],16)*a + int(b[i:i+2],16)*(1-a)):02X}"
                   for i in (0, 2, 4))


def contains(outer, inner) -> bool:
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner[:4]
    cx, cy = ix + iw / 2, iy + ih / 2
    return ox - .5 <= cx <= ox + ow + .5 and oy - .5 <= cy <= oy + oh + .5


def background_under(item, items, idx) -> str:
    """The colour actually painted behind this text.

    Walk backwards through paint order. The last opaque thing drawn under the
    text wins, which is how the browser composites it. A gradient contributes
    whichever of its two stops is worse against the text, because a gradient is
    only as readable as its lightest pixel.
    """
    best = "FFFFFF"
    for other in items[:idx]:
        if other.get("t") != "rect" or other.get("op", 1) < .9:
            continue
        if not contains(other["rect"], item["rect"]):
            continue
        if other.get("grad"):
            g = other["grad"]
            best = (g["from"]["c"], g["to"]["c"])
        elif other.get("fill") and other["fill"].get("a", 0) >= .9:
            best = other["fill"]["c"]
    return best


def check(path: pathlib.Path) -> list:
    doc = json.loads(path.read_text())
    W, H = doc["w"], doc["h"]
    fails = []

    for n, slide in enumerate(doc["slides"], 1):
        where = f"{path.name} slide {n} ({slide.get('title') or 'untitled'})"
        items = slide["items"]

        for it in items:
            x, y, w, h = it["rect"]
            if it.get("op", 1) < .05:
                continue
            if y + h > H + .5 or x + w > W + .5:
                fails.append(
                    f"OVERFLOW  {where}: a {it['t']} ends at "
                    f"{x + w:.0f},{y + h:.0f} past the {W}x{H} canvas. "
                    f"It will be cut off, and the PDF will not say so.")

        for i, it in enumerate(items):
            if it.get("t") != "text" or it.get("op", 1) < DECORATIVE_OPACITY:
                continue
            bg = background_under(it, items, i)
            bgs = bg if isinstance(bg, tuple) else (bg,)
            for run in it.get("runs", []):
                if "f" not in run:
                    continue          # {"br": true} is a line break, not text
                f = run["f"]
                size, weight = f.get("size", 14), f.get("weight", 400)
                need = (LARGE_AA if size >= LARGE_PX
                        or (size >= LARGE_BOLD_PX and weight >= 700) else AA)
                for b in bgs:
                    fg = over(f["colour"], b)
                    r = ratio(fg, b)
                    if r < need:
                        txt = run["s"][:42].strip()
                        fails.append(
                            f"CONTRAST  {where}: \"{txt}\" at {size:g}px/{weight} "
                            f"is #{fg} on #{b}, {r:.2f}:1, needs {need}:1")
                        break
    return fails


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    all_fails, checked = [], 0
    for arg in sys.argv[1:]:
        p = pathlib.Path(arg)
        if not p.exists():
            print(f"   skipped {p}: not extracted")
            continue
        checked += 1
        f = check(p)
        all_fails += f
        doc = json.loads(p.read_text())
        items = sum(len(s["items"]) for s in doc["slides"])
        print(f"   {p.name}: {len(doc['slides'])} slides, {items} boxes, "
              f"{len(f)} problem{'' if len(f) == 1 else 's'}")

    if all_fails:
        print()
        for f in all_fails:
            print(f"   {f}")
        print(f"\n   {len(all_fails)} problem(s). These do not show up in a "
              f"thumbnail, which is why they are checked here.")
        sys.exit(1)
    if checked:
        print("   no overflow, every text run at or above its AA threshold")


if __name__ == "__main__":
    main()
