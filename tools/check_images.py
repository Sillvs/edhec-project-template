#!/usr/bin/env python3
"""Are the README pictures still the ones the templates produce?

    python3 tools/check_images.py docs/img

`docs/img/*` has to stay committed, or the README renders broken on GitHub. So
it can go stale in exactly the way the committed PDFs can: somebody edits a
slide, never runs `./build.sh docs`, and the picture on the front page quietly
stops being the thing it claims to show.

**Why not `git diff --quiet`.** Because it fails every time, everywhere. These
PNGs are rasterised from a Chrome render, and sub-pixel layout and antialiasing
differ between Chrome builds, so a byte comparison between a laptop and a CI
runner reports every file as changed even when nothing was edited. A check that
always fails gets switched off within a week, which is worse than no check.

So compare the pixels, but measure **area changed**, not average difference.
Mean difference was tried first and is useless here: re-colouring a chip on one
slide of a contact sheet moved the mean by 0.13 of a level out of 255, because
averaging over 1700x1080 pixels dilutes any local edit into nothing. A
threshold loose enough to ignore renderer jitter would have ignored the edit
too.

What works: blur both images by 1.5px to collapse sub-pixel and antialiasing
jitter, then count the pixels that still differ by more than 16 levels, as a
fraction of the image. Measured here: an unchanged rebuild gives 0.0000%, and
that same one-chip edit gives 0.0965% and 0.0392% on the two pictures that
contain it. The threshold sits between, nearer the floor.

Needs pillow. Reads the committed version out of git, so it works on a dirty
tree.
"""
import io
import pathlib
import subprocess
import sys

from PIL import Image, ImageChops, ImageFilter

BLUR = 1.5        # px, enough to absorb sub-pixel layout and antialiasing
LEVELS = 16       # a pixel must shift this much after blurring to count
TOLERANCE = 0.0002  # 0.02% of pixels. Floor measured at 0%, signal at 0.04%.


def committed(path: pathlib.Path):
    """The version in HEAD, or None if the file is new."""
    r = subprocess.run(["git", "show", f"HEAD:{path}"],
                       capture_output=True)
    if r.returncode:
        return None
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def changed_area(a: Image.Image, b: Image.Image) -> float:
    """Fraction of pixels that still differ once jitter is blurred away."""
    a = a.filter(ImageFilter.GaussianBlur(BLUR))
    b = b.filter(ImageFilter.GaussianBlur(BLUR))
    mask = (ImageChops.difference(a, b).convert("L")
            .point(lambda v: 255 if v > LEVELS else 0))
    hist = mask.histogram()
    same, differ = hist[0], hist[255]
    return differ / (same + differ) if same + differ else 0.0


def main() -> None:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/img")
    stale, checked = [], 0

    for path in sorted(root.glob("*.png")):
        old = committed(path)
        if old is None:
            print(f"   {path.name}: new, nothing to compare")
            continue
        new = Image.open(path).convert("RGB")
        checked += 1
        if old.size != new.size:
            stale.append(f"{path.name}: {old.size[0]}x{old.size[1]} committed, "
                         f"{new.size[0]}x{new.size[1]} built. The layout moved.")
            continue
        d = changed_area(old, new)
        if d > TOLERANCE:
            stale.append(f"{path.name}: {d * 100:.4f}% of pixels changed, "
                         f"tolerance {TOLERANCE * 100:.2f}%. The template moved "
                         f"and this picture did not.")

    print(f"   {checked} picture(s) compared against HEAD")
    if stale:
        print()
        for s in stale:
            print(f"   {s}")
        print("\n   Run ./build.sh docs and commit the result.")
        sys.exit(1)
    print("   every picture still matches the templates")


if __name__ == "__main__":
    main()
