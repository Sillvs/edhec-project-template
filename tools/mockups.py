#!/usr/bin/env python3
"""Render the screenshots and mockups used in the README.

    python3 tools/mockups.py

Reads the exported PDFs, writes PNGs into docs/img/. Everything is generated,
so the pictures in the README can never drift away from the templates.

Needs poppler (pdftoppm) and pillow.
"""
import pathlib
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter

HERE = pathlib.Path(__file__).resolve().parent.parent
OUT = HERE / "docs" / "img"
BURGUNDY = (95, 25, 55)


def pages(pdf: pathlib.Path, dpi: int = 150) -> list[Image.Image]:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), str(pdf), f"{tmp}/p"],
                       check=True)
        return [Image.open(f).convert("RGB").copy()
                for f in sorted(pathlib.Path(tmp).glob("p-*.png"))]


def rounded(im: Image.Image, r: int) -> Image.Image:
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1],
                                           radius=r, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def shadow(size, r, blur, spread, opacity=90):
    w, h = size
    lay = Image.new("RGBA", (w + blur * 4, h + blur * 4), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(
        [blur * 2 - spread, blur * 2 - spread, blur * 2 + w + spread, blur * 2 + h + spread],
        radius=r, fill=(20, 8, 14, opacity))
    return lay.filter(ImageFilter.GaussianBlur(blur))


def backdrop(size, top=(250, 246, 248), bottom=(233, 222, 228)):
    w, h = size
    base = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)],
               fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return base


def screen_mockup(slide: Image.Image, out: pathlib.Path, width=1700):
    """The deck as it looks on a presentation screen."""
    pad, bezel = 90, 16
    sw = width - pad * 2
    sh = round(sw * slide.height / slide.width)
    slide = slide.resize((sw, sh), Image.LANCZOS)

    frame = Image.new("RGB", (sw + bezel * 2, sh + bezel * 2), (26, 14, 20))
    frame.paste(slide, (bezel, bezel))
    frame = rounded(frame, 14)

    canvas = backdrop((width, sh + pad * 2 + 46))
    sx, sy = pad - bezel, pad - bezel
    sh_lay = shadow(frame.size, 14, 26, 6, 95)
    canvas.paste(sh_lay, (sx - 52, sy - 40), sh_lay)
    canvas.paste(frame, (sx, sy), frame)

    # a stand, so it reads as a screen rather than a floating rectangle
    d = ImageDraw.Draw(canvas)
    cx = width // 2
    foot = sy + frame.height
    d.rounded_rectangle([cx - 70, foot, cx + 70, foot + 16], radius=5, fill=(214, 200, 208))
    d.rounded_rectangle([cx - 150, foot + 14, cx + 150, foot + 24], radius=6, fill=(198, 182, 192))
    canvas.save(out)
    return out


def print_mockup(pgs: list[Image.Image], out: pathlib.Path, width=1700):
    """Two printed pages, as they look on a desk."""
    canvas = backdrop((width, 1180))
    page_w = 620
    spots = [(150, 150, -4.0), (560, 250, 3.0), (980, 170, -1.5)]
    for (x, y, ang), src in zip(spots, pgs):
        pw = page_w
        ph = round(pw * src.height / src.width)
        pg = src.resize((pw, ph), Image.LANCZOS)
        card = Image.new("RGB", (pw + 2, ph + 2), (226, 216, 221))
        card.paste(pg, (1, 1))
        card = rounded(card, 4).rotate(ang, expand=True, resample=Image.BICUBIC)
        sh_lay = shadow(card.size, 6, 22, 2, 80).rotate(0)
        canvas.paste(sh_lay, (x - 44, y - 30), sh_lay)
        canvas.paste(card, (x, y), card)
    canvas.save(out)
    return out


def contact_sheet(pgs: list[Image.Image], out: pathlib.Path, cols=4, cell=440, pad=14):
    rows = (len(pgs) + cols - 1) // cols
    ch = round(cell * pgs[0].height / pgs[0].width)
    canvas = Image.new("RGB", (cols * cell + pad * (cols + 1),
                               rows * ch + pad * (rows + 1)), (244, 238, 241))
    for i, p in enumerate(pgs):
        thumb = p.resize((cell, ch), Image.LANCZOS)
        bordered = Image.new("RGB", (cell, ch), (255, 255, 255))
        bordered.paste(thumb, (0, 0))
        x = pad + (i % cols) * (cell + pad)
        y = pad + (i // cols) * (ch + pad)
        canvas.paste(bordered, (x, y))
        ImageDraw.Draw(canvas).rectangle([x, y, x + cell - 1, y + ch - 1],
                                         outline=(222, 208, 215))
    canvas.save(out)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    slides = HERE / "slides" / "slides.pdf"
    gallery = HERE / "slides" / "gallery.pdf"
    paper = HERE / "paper" / "paper.pdf"

    if slides.exists():
        sp = pages(slides)
        screen_mockup(sp[1], OUT / "mockup-screen.png")
        contact_sheet(sp, OUT / "slides-overview.png")
        sp[0].resize((1300, round(1300 * sp[0].height / sp[0].width)),
                     Image.LANCZOS).save(OUT / "slide-title.png")
        sp[-1].resize((1300, round(1300 * sp[-1].height / sp[-1].width)),
                      Image.LANCZOS).save(OUT / "slide-closing.png")
    if gallery.exists():
        gp = pages(gallery)
        for i, p in enumerate(gp, 1):
            p.resize((1300, round(1300 * p.height / p.width)),
                     Image.LANCZOS).save(OUT / f"charts-{i}.png")
    if paper.exists():
        pp = pages(paper)
        print_mockup(pp[:3], OUT / "mockup-paper.png")
        pp[0].resize((900, round(900 * pp[0].height / pp[0].width)),
                     Image.LANCZOS).save(OUT / "paper-cover.png")
        pp[1].resize((900, round(900 * pp[1].height / pp[1].width)),
                     Image.LANCZOS).save(OUT / "paper-body.png")

    for f in sorted(OUT.glob("*.png")):
        print(f"   {f.relative_to(HERE)}  {f.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
