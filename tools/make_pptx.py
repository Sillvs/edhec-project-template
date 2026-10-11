#!/usr/bin/env python3
"""Build the picture fallback: one full-bleed image per slide.

    python3 tools/make_pptx.py slides/slides.pdf

Pixel-identical to the PDF but not editable. The editable deck comes from
make_pptx_native.py; this one is written next to the PDF as *-pictures.pptx
for anyone who only needs to project it.

    python3 make_pptx.py            # both decks
    python3 make_pptx.py --dpi 200  # sharper, larger file

Requires pdftoppm (poppler) and python-pptx.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import tempfile

from pptx import Presentation
from pptx.util import Emu




# 16:9 widescreen in the exact EMU values PowerPoint itself writes
# (Inches(13.333) rounds to 12191695 and leaves a hairline gap on the right)
SLIDE_W, SLIDE_H = Emu(12192000), Emu(6858000)


def slide_titles(html: pathlib.Path) -> list[str]:
    """Slide names from the deck, used as speaker notes for navigation."""
    if not html.exists():
        return []
    return re.findall(r'data-title="([^"]*)"', html.read_text(encoding="utf-8"))


def build(pdf_path: str, dpi: int) -> None:
    pdf = pathlib.Path(pdf_path)
    if not pdf.exists():
        raise SystemExit(f"missing {pdf}: export the PDF first")

    titles = slide_titles(pdf.with_suffix(".html"))

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["pdftoppm", "-png", "-r", str(dpi), str(pdf), f"{tmp}/pg"],
            check=True,
        )
        pages = sorted(pathlib.Path(tmp).glob("pg-*.png"))
        if not pages:
            raise SystemExit("pdftoppm produced no pages")

        prs = Presentation()
        prs.slide_width, prs.slide_height = SLIDE_W, SLIDE_H
        blank = prs.slide_layouts[6]  # no placeholders

        for i, page in enumerate(pages):
            slide = prs.slides.add_slide(blank)
            slide.shapes.add_picture(str(page), 0, 0, width=SLIDE_W, height=SLIDE_H)
            if i < len(titles):
                slide.notes_slide.notes_text_frame.text = titles[i]

        # python-pptx keeps the 4:3 label from its default template
        prs.slide_master  # noqa: B018  (touch, so the part is loaded before save)
        sld_sz = prs.part._element.find(
            "{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz")
        if sld_sz is not None:
            sld_sz.set("type", "screen16x9")

        prs.core_properties.title = pdf.stem

        out = pdf.with_name(pdf.stem + "-pictures.pptx")
        prs.save(str(out))
        size = out.stat().st_size / 1e6
        print(f"{out.name}: {len(pages)} slides, {size:.1f} MB, {dpi} dpi")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="the exported slide PDF")
    ap.add_argument("--dpi", type=int, default=150,
                    help="render resolution, 150 covers a 1920x1080 projector")
    args = ap.parse_args()
    if not shutil.which("pdftoppm"):
        raise SystemExit("pdftoppm not found, install poppler-utils")
    build(args.pdf, args.dpi)


if __name__ == "__main__":
    main()
