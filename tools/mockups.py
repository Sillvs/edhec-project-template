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

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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


def perspective(im: Image.Image, dst, out_size):
    """Map the image's four corners onto `dst` (tl, tr, br, bl) in out_size.

    PIL's PERSPECTIVE transform wants the coefficients for the INVERSE map,
    output pixel -> input pixel, which is why the system below is solved from
    dst to src and not the other way round. Getting that backwards produces a
    picture that is subtly mirrored rather than obviously broken.
    """
    src = [(0, 0), (im.width, 0), (im.width, im.height), (0, im.height)]
    a, b = [], []
    for (X, Y), (x, y) in zip(dst, src):
        a.append([X, Y, 1, 0, 0, 0, -x * X, -x * Y]); b.append(x)
        a.append([0, 0, 0, X, Y, 1, -y * X, -y * Y]); b.append(y)
    # 8x8 Gaussian elimination with partial pivoting; no numpy dependency
    n = 8
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(a[r][i]))
        a[i], a[piv] = a[piv], a[i]; b[i], b[piv] = b[piv], b[i]
        for r in range(i + 1, n):
            f = a[r][i] / a[i][i]
            for c in range(i, n):
                a[r][c] -= f * a[i][c]
            b[r] -= f * b[i]
    co = [0.0] * n
    for i in range(n - 1, -1, -1):
        co[i] = (b[i] - sum(a[i][c] * co[c] for c in range(i + 1, n))) / a[i][i]
    return im.convert("RGBA").transform(out_size, Image.PERSPECTIVE, co,
                                        Image.BICUBIC)


def poly_shadow(size, pts, blur=26, opacity=105, offset=(0, 0)):
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon([(x + offset[0], y + offset[1]) for x, y in pts],
                                fill=(18, 6, 12, opacity))
    return lay.filter(ImageFilter.GaussianBlur(blur))


def label(canvas, xy, text, size=26, fill=(95, 25, 55), weight="bold"):
    """Draw a caption. Falls back to the bitmap font rather than failing:
    a mockup with a plain label still communicates; a crash does not."""
    d = ImageDraw.Draw(canvas)
    font = None
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                 if weight == "bold" else
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(path, size); break
        except OSError:
            continue
    d.text(xy, text, fill=fill, font=font)
    return d


def laptop_mockup(slide: Image.Image, out: pathlib.Path, width=1700):
    """The deck on a laptop, which is where a teammate first sees it."""
    H = 1080
    canvas = backdrop((width, H), top=(247, 242, 245), bottom=(226, 213, 221))

    # screen, in slight perspective: the lid leans back a few degrees
    sx, sy, sw = 300, 120, 1100
    sh = round(sw * slide.height / slide.width)
    dst = [(sx + 28, sy), (sx + sw - 28, sy),
           (sx + sw, sy + sh), (sx, sy + sh)]
    shp = poly_shadow((width, H), dst, blur=30, opacity=90, offset=(0, 26))
    canvas.paste(shp, (0, 0), shp)

    bez = 16
    lid_dst = [(dst[0][0] - bez, dst[0][1] - bez), (dst[1][0] + bez, dst[1][1] - bez),
               (dst[2][0] + bez, dst[2][1] + bez), (dst[3][0] - bez, dst[3][1] + bez)]
    ImageDraw.Draw(canvas).polygon(lid_dst, fill=(34, 22, 28))
    warped = perspective(slide, dst, (width, H))
    canvas.paste(warped, (0, 0), warped)

    # base: a trapezoid wider than the lid, as a real laptop is
    d = ImageDraw.Draw(canvas)
    by = sy + sh + bez
    base = [(sx - bez - 10, by), (sx + sw + bez + 10, by),
            (sx + sw + bez + 86, by + 30), (sx - bez - 86, by + 30)]
    bsh = poly_shadow((width, H), base, blur=22, opacity=70, offset=(0, 16))
    canvas.paste(bsh, (0, 0), bsh)
    d.polygon(base, fill=(198, 192, 196))
    d.polygon([(sx + sw // 2 - 70, by + 2), (sx + sw // 2 + 70, by + 2),
               (sx + sw // 2 + 76, by + 9), (sx + sw // 2 - 76, by + 9)],
              fill=(176, 169, 174))
    canvas.save(out)
    return out


def room_mockup(slide: Image.Image, out: pathlib.Path, width=1700):
    """Projected in a dim room, which is the condition the contrast rules are for."""
    H = 1000
    canvas = backdrop((width, H), top=(40, 26, 34), bottom=(20, 11, 16))
    d = ImageDraw.Draw(canvas, "RGBA")

    sx, sy, sw = 310, 95, 1080
    sh = round(sw * slide.height / slide.width)
    slide = slide.resize((sw, sh), Image.LANCZOS)

    # the light the projector spills past the screen
    glow = Image.new("RGBA", (width, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rectangle([sx - 120, sy - 90, sx + sw + 120, sy + sh + 90],
                                   fill=(255, 238, 246, 42))
    canvas.paste(glow.filter(ImageFilter.GaussianBlur(70)), (0, 0),
                 glow.filter(ImageFilter.GaussianBlur(70)))

    d.rectangle([sx - 13, sy - 13, sx + sw + 13, sy + sh + 13], fill=(12, 6, 9))
    canvas.paste(slide, (sx, sy))

    # heads along the bottom edge, so the scale of the room is readable
    for cx, r, a in ((430, 78, 235), (700, 92, 255), (1010, 84, 245), (1285, 72, 228)):
        d.ellipse([cx - r, H - r * 1.05, cx + r, H + r * 1.6], fill=(10, 5, 8, a))
        d.ellipse([cx - r * .55, H - r * 2.05, cx + r * .55, H - r * .95],
                  fill=(10, 5, 8, a))
    canvas.save(out)
    return out


def desk_mockup(one: Image.Image, cover: Image.Image, out: pathlib.Path, width=1700):
    """The leave-behind where it actually ends up: face up on somebody's desk."""
    H = 1150
    canvas = backdrop((width, H), top=(238, 230, 226), bottom=(214, 201, 199))

    # the paper, behind and further away
    cw = 560
    ch = round(cw * cover.height / cover.width)
    cdst = [(880, 150), (880 + cw - 40, 112), (880 + cw, 112 + ch), (900, 150 + ch)]
    csh = poly_shadow((width, H), cdst, blur=20, opacity=85, offset=(10, 18))
    canvas.paste(csh, (0, 0), csh)
    cw_img = perspective(cover, cdst, (width, H))
    canvas.paste(cw_img, (0, 0), cw_img)

    # the one-pager, in front, squared up because somebody just put it down
    ow = 610
    oh = round(ow * one.height / one.width)
    odst = [(250, 150), (250 + ow, 130), (250 + ow - 24, 130 + oh), (226, 150 + oh)]
    osh = poly_shadow((width, H), odst, blur=26, opacity=100, offset=(14, 24))
    canvas.paste(osh, (0, 0), osh)
    ow_img = perspective(one, odst, (width, H))
    canvas.paste(ow_img, (0, 0), ow_img)
    canvas.save(out)
    return out


def compare_mockup(before: Image.Image, after: Image.Image, out: pathlib.Path,
                   width=1760):
    """The same finding, laid out two ways. The argument for the whole repo."""
    gap, pad, top = 40, 36, 92
    cw = (width - pad * 2 - gap) // 2
    chh = round(cw * after.height / after.width)
    H = top + chh + 74

    canvas = Image.new("RGB", (width, H), (246, 241, 244))
    for i, (im, cap, col) in enumerate(
            ((before, "Default PowerPoint", (118, 112, 116)),
             (after, "This template", (95, 25, 55)))):
        x = pad + i * (cw + gap)
        im = im.resize((cw, chh), Image.LANCZOS)
        sh_lay = shadow((cw, chh), 6, 20, 2, 70)
        canvas.paste(sh_lay, (x - 40, top - 32), sh_lay)
        canvas.paste(im, (x, top))
        ImageDraw.Draw(canvas).rectangle([x, top, x + cw - 1, top + chh - 1],
                                         outline=(220, 208, 214))
        label(canvas, (x + 2, top - 48), cap.upper(), 25, col)
    label(canvas, (pad + 2, H - 52),
          "Same facts, same five minutes of work. One of them has a finding in the title.",
          21, (122, 112, 118), weight="regular")
    canvas.save(out)
    return out


def social_card(slide: Image.Image, out: pathlib.Path):
    """The 1200x630 card that link previews show on Slack, LinkedIn and X.

    GitHub has no API for a repository's social preview, so this one is used by
    the GitHub Pages site via og:image and uploaded by hand to the repo under
    Settings, General, Social preview. Without it, every shared link renders as
    the grey default and a visual project looks like a config file.
    """
    W, H = 1200, 630
    canvas = backdrop((W, H), top=(252, 250, 251), bottom=(240, 233, 236))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, 7], fill=BURGUNDY)

    sw = 760
    sh = round(sw * slide.height / slide.width)
    im = slide.resize((sw, sh), Image.LANCZOS)
    card = Image.new("RGB", (sw + 2, sh + 2), (222, 208, 215))
    card.paste(im, (1, 1))
    card = rounded(card, 8)
    x, y = (W - sw) // 2, 232
    sh_lay = shadow(card.size, 8, 22, 3, 80)
    canvas.paste(sh_lay, (x - 44, y - 30), sh_lay)
    canvas.paste(card, (x, y), card)

    label(canvas, (64, 74), "EDHEC PROJECT TEMPLATE", 23, BURGUNDY)
    label(canvas, (64, 118), "Hand in work that looks", 46, (26, 36, 48))
    label(canvas, (64, 170), "like you meant it", 46, (26, 36, 48))
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
        social_card(sp[1], OUT / "social.png")
        sp[0].resize((1300, round(1300 * sp[0].height / sp[0].width)),
                     Image.LANCZOS).save(OUT / "slide-title.png")
        sp[-1].resize((1300, round(1300 * sp[-1].height / sp[-1].width)),
                      Image.LANCZOS).save(OUT / "slide-closing.png")
    if gallery.exists():
        gp = pages(gallery)
        for i, p in enumerate(gp, 1):
            p.resize((1300, round(1300 * p.height / p.width)),
                     Image.LANCZOS).save(OUT / f"charts-{i}.png")
    onepager = HERE / "paper" / "onepager.pdf"
    before = HERE / "docs" / "_default-powerpoint.pdf"

    if slides.exists():
        # Trimming the starter deck is the intended use, so never index a
        # slide that may not be there. sp[-1] is the closing slide.
        laptop_mockup(sp[min(2, len(sp) - 1)], OUT / "mockup-laptop.png")
        room_mockup(sp[min(1, len(sp) - 1)], OUT / "mockup-room.png")
        if before.exists():
            compare_mockup(pages(before)[0], sp[min(1, len(sp) - 1)],
                           OUT / "mockup-compare.png")
        else:
            print("   skipped mockup-compare.png: docs/_default-powerpoint.pdf "
                  "not built yet, run ./build.sh docs again")
    if onepager.exists():
        op = pages(onepager, 180)[0]
        op.resize((900, round(900 * op.height / op.width)),
                  Image.LANCZOS).save(OUT / "onepager.png")
        if paper.exists():
            desk_mockup(op, pages(paper, 180)[0], OUT / "mockup-desk.png")

    if paper.exists():
        pp = pages(paper)
        print_mockup(pp[:4], OUT / "mockup-paper.png")  # include the references page
        pp[0].resize((900, round(900 * pp[0].height / pp[0].width)),
                     Image.LANCZOS).save(OUT / "paper-cover.png")
        if len(pp) > 1:
            pp[1].resize((900, round(900 * pp[1].height / pp[1].width)),
                         Image.LANCZOS).save(OUT / "paper-body.png")

    for f in sorted(OUT.glob("*.png")):
        print(f"   {f.relative_to(HERE)}  {f.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
