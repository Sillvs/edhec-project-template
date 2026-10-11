# Exporting

Three outputs come out of one HTML file. This page says how, and then lists the
traps that cost us real time, so you do not rediscover them.

## PDF

The authoritative export. Everything else is derived from it.

```bash
CHROME=$(tools/find-chrome.sh)
"$CHROME" --headless --disable-gpu --no-sandbox \
          --print-to-pdf=slides/slides.pdf --no-pdf-header-footer \
          --virtual-time-budget=12000 "file://$PWD/slides/slides.html"
```

`tools/find-chrome.sh` resolves Chrome at run time. Never hardcode the path: it
used to point at one Playwright build number, a routine upgrade renamed that
directory, and the whole toolchain started failing with a bare "No such file or
directory" that gives no hint Chrome is the missing piece. Override with
`CHROME=/path/to/chrome` if you want a specific one.

By hand in Chrome: press `P`, choose **Save as PDF**, set **Margins: none** and
**Background graphics: on**. Both give one slide per page at 16:9.

`--no-pdf-header-footer` matters for the paper as well: the page numbers come
from CSS, and Chrome's own footer would print a second set on top.

## Editable PowerPoint

```bash
node tools/extract_layout.mjs slides/slides.html .build/slides.json
python3 tools/make_pptx_native.py .build/slides.json slides/slides.pptx
```

The deck is a fixed 1280×720 canvas, so the browser itself can report the exact
position of every box, text block and icon. The extractor drives Chrome over the
DevTools protocol, reads that geometry, and the builder turns it into real
PowerPoint shapes and real text boxes.

**What stays editable:** shapes, fills, gradients, table bands, every word of
text. A box and its own text are a single object, so moving the box moves the
text and the text stays centred when you rewrite it.

**What does not:** the line icons and the logo remain pictures. They are
drawings, not content.

**What shifts:** PowerPoint re-wraps text with its own font metrics, so a line
here and there can break differently. Single-line blocks get a few pixels of
slack to prevent it. The HTML stays the master; the PPTX is an export.

## Picture PowerPoint

```bash
python3 tools/make_pptx.py slides/slides.pdf      # -> slides-pictures.pptx
```

One full-bleed image per slide. Pixel-identical to the PDF, not editable. Use it
when someone only needs to project the deck and you do not want surprises on a
machine with different fonts. `--dpi 200` for very large screens.

---

## Traps

Each of these produced a wrong file that still looked plausible.

### The print stylesheet is the real one

On screen every slide but the active one is `visibility: hidden`. Measure the
deck without switching Chrome to print media and you get one slide and 13 empty
ones. The extractor calls `Emulation.setEmulatedMedia({media: "print"})` before
reading anything.

### Capture icons in isolation

Screenshotting an icon straight off the page bakes whatever sits behind it into
the picture. We lost an afternoon to a footer that appeared twice: a decorative
strip spanning the bottom of the slide had captured a pixel copy of the footer
text, which then collided with the real text box. Icons are now captured with
everything else hidden, on a transparent background.

### Inline elements belong to their paragraph

A `<b>` inside a sentence is part of the parent's runs. Emit it a second time as
its own text block and the two overlap. Only elements that are not
`display: inline` get walked separately.

### `spAutoFit` draws the paragraph twice

python-pptx writes it by default. With it, the frame resizes to the text and
renderers paint the paragraph both before and after. Every text frame is set to
`MSO_AUTO_SIZE.NONE`.

### Letter spacing plus text transparency truncates

Set `spc` and a colour `alpha` on the same run and LibreOffice drops the last
characters. "OUR RECOMMENDATION" rendered as "OUR RECOMMENDA". Text alpha is
therefore resolved against the nearest opaque background at extraction time, and
the file never carries a translucent run.

### Only left-aligned text may be indented

An icon or a chip in front of the text shifts the first line, and that shift has
to be reproduced as a paragraph indent. For **centred** text the same gap is
just the centring, and treating it as an indent pushes the line off to the right
a second time. The indent is applied only when the paragraph is left-aligned.

---

## Checking the result

Never trust that an export worked. Slides overflow silently: content past 720 px
is simply clipped with no error.

```bash
# every slide at a glance
pdftoppm -png -r 46 slides/slides.pdf /tmp/pg
montage /tmp/pg-*.png -tile 4x4 -geometry +4+4 /tmp/contact.png

# one slide, full size, straight from the browser
chrome --headless --window-size=1280,720 --screenshot=/tmp/s.png \
       "file://$PWD/slides/slides.html#8"
```

To check the PowerPoint, convert it back and look at it:

```bash
soffice --headless --convert-to pdf slides/slides.pptx
```

LibreOffice needs `libreoffice-impress` installed or it refuses every `.pptx`
with "source file could not be loaded", which reads like a corrupt file and is
not.
