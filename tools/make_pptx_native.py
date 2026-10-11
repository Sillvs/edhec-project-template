#!/usr/bin/env python3
"""Build an editable PowerPoint from the extracted slide geometry.

    node extract_layout.mjs praesentation.html /tmp/layout.json
    python3 make_pptx_native.py /tmp/layout.json praesentation_editable.pptx

Every box becomes a real PowerPoint shape and every piece of text a real text
box, so both can be edited. Only the line icons and the honeycomb stay pictures,
because they are drawings, not content.

Caveat worth knowing: PowerPoint re-wraps text with its own font metrics, so a
line here and there can break differently from the HTML. The HTML remains the
master; this file is for people who need to edit in PowerPoint.
"""
import json
import pathlib
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

PX = 9525                      # 1 CSS px in EMU (12192000 / 1280)
PT = 0.75                      # 1 CSS px in points
FONT = "Arial"                 # closest universally available to Helvetica Neue

ALIGN = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT,
         "center": PP_ALIGN.CENTER, "justify": PP_ALIGN.JUSTIFY,
         "start": PP_ALIGN.LEFT, "end": PP_ALIGN.RIGHT}


def rgb(c):
    return RGBColor.from_string(c["c"])


def set_alpha(fill_elm, alpha):
    """python-pptx has no transparency API; write the a:alpha child directly."""
    if alpha >= 1:
        return
    srgb = fill_elm.find(qn("a:srgbClr"))
    if srgb is None:
        return
    a = srgb.makeelement(qn("a:alpha"), {"val": str(int(round(alpha * 100000)))})
    srgb.append(a)


def no_shadow(shape):
    shape.shadow.inherit = False


def write_text(tf, it, pad, anchor_middle, centre=False):
    """Pour the runs of a text item into an existing text frame."""
    # inside a shape a one-liner must never wrap: the shape is sized to the text
    tf.word_wrap = (it.get("lines") or 1) > 1 and not it.get("nowrap")
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE if anchor_middle else MSO_ANCHOR.TOP
    tf.margin_left, tf.margin_top = Emu(int(pad[0] * PX)), Emu(int(pad[1] * PX))
    tf.margin_right, tf.margin_bottom = Emu(int(pad[2] * PX)), Emu(int(pad[3] * PX))

    paras = [[]]
    for r in it["runs"]:
        paras.append([]) if r.get("br") else paras[-1].append(r)

    for pi, runs in enumerate(paras):
        p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
        jc = it.get("jc") or ""
        if jc in ("center", "centre"):
            p.alignment = PP_ALIGN.CENTER
        elif jc in ("flex-end", "right", "end"):
            p.alignment = PP_ALIGN.RIGHT
        else:
            p.alignment = ALIGN.get(it.get("align", "left"), PP_ALIGN.LEFT)
        lh = it.get("lh") or 0
        if lh:
            p.line_spacing = Pt(lh * PT)
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        for r in runs:
            f = r["f"]
            run = p.add_run()
            run.text = r["s"].upper() if f.get("upper") else r["s"]
            run.font.name = FONT
            run.font.size = Pt(max(1.0, f["size"] * PT))
            run.font.bold = f["weight"] >= 600
            run.font.italic = bool(f["italic"])
            if f.get("colour"):
                run.font.color.rgb = rgb(f["colour"])
            if f.get("spacing"):
                run.font._rPr.set("spc", str(int(round(f["spacing"] * PT * 100))))


def add_rect(slide, it, inner=None):
    x, y, w, h = it["rect"]
    if w <= 0 or h <= 0:
        return
    rad = it.get("rad") or 0
    # border-radius:50% on a square is a circle; on a wide chip it is a pill,
    # and a pill must stay a rounded rectangle rather than become an oval
    circle = rad >= min(w, h) / 2 - 0.6 and abs(w - h) < 2.5
    kind = (MSO_SHAPE.OVAL if circle else
            MSO_SHAPE.ROUNDED_RECTANGLE if rad > 0.5 else MSO_SHAPE.RECTANGLE)
    shape = slide.shapes.add_shape(
        kind, Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX)))
    no_shadow(shape)
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        shape.adjustments[0] = min(0.5, rad / max(1.0, min(w, h)))

    op = it.get("op", 1) or 1
    grad, fill = it.get("grad"), it.get("fill")

    if grad and grad.get("from") and grad.get("to"):
        shape.fill.gradient()
        stops = shape.fill.gradient_stops
        stops[0].color.rgb = rgb(grad["from"])
        stops[0].position = 0.0
        stops[1].color.rgb = rgb(grad["to"])
        stops[1].position = 1.0
        # CSS 0deg points up and turns clockwise; PowerPoint 0 points right
        shape.fill.gradient_angle = (grad.get("angle", 90) - 90) % 360
    elif fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(fill)
        set_alpha(shape.fill._xPr.find(qn("a:solidFill")), fill.get("a", 1) * op)
    else:
        shape.fill.background()

    bw, bc = it.get("bw") or [0, 0, 0, 0], it.get("bc") or [None] * 4
    bs = it.get("bs") or ["solid"] * 4
    uniform = bw[0] > 0 and len(set(bw)) == 1 and bc[0] is not None
    if uniform:
        shape.line.color.rgb = rgb(bc[0])
        shape.line.width = Emu(int(max(bw[0], 0.75) * PX))
    else:
        shape.line.fill.background()
        # a single coloured edge (the accent bars) becomes its own thin bar
        for i, (width, col) in enumerate(zip(bw, bc)):
            if width <= 0 or col is None:
                continue
            ex, ey, ew, eh = {
                0: (x, y, w, width),
                1: (x + w - width, y, width, h),
                2: (x, y + h - width, w, width),
                3: (x, y, width, h),
            }[i]
            if bs[i] in ("dashed", "dotted"):
                # a dashed rule has to be a line, not a filled sliver, or the
                # dashes disappear and it reads as a solid bar
                x1, y1 = (ex, ey), (ex + ew, ey + eh)
                conn = slide.shapes.add_connector(
                    MSO_CONNECTOR.STRAIGHT,
                    Emu(int(x1[0] * PX)), Emu(int(x1[1] * PX)),
                    Emu(int(y1[0] * PX)), Emu(int(y1[1] * PX)))
                conn.line.color.rgb = rgb(col)
                conn.line.width = Emu(int(max(width, 1.0) * PX))
                conn.line.dash_style = (MSO_LINE_DASH_STYLE.DASH
                                        if bs[i] == "dashed"
                                        else MSO_LINE_DASH_STYLE.ROUND_DOT)
                continue
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Emu(int(ex * PX)), Emu(int(ey * PX)),
                Emu(int(ew * PX)), Emu(int(eh * PX)))
            no_shadow(bar)
            bar.fill.solid()
            bar.fill.fore_color.rgb = rgb(col)
            bar.line.fill.background()

    if inner is not None:
        # the box and its own words become ONE object: it moves as a unit and
        # the text stays centred in it when somebody rewrites the wording
        pad = inner.get("pad") or [0, 0, 0, 0]
        ink = inner.get("trect")
        snug = (inner.get("lines", 1) == 1 and ink
                and (w - pad[0] - pad[2]) - ink[2] < 14)
        write_text(shape.text_frame, inner, pad,
                   anchor_middle=(inner.get("ai") in ("center", "centre"))
                   or (inner.get("lines", 1) == 1 and h <= 56),
                   centre=bool(snug))
    return shape


def add_text(slide, it):
    pad = it.get("pad") or [0, 0, 0, 0]
    ex, ey, ew, eh = it["rect"]
    lines = it.get("lines") or 1
    ink = it.get("trect")
    first_indent = 0.0
    left_margin = 0.0

    # Always use the element's own content box, never a box squeezed around the
    # glyphs: in PowerPoint the text then sits centred or flush inside the box it
    # belongs to and stays that way when somebody edits the wording.
    x, y = ex + pad[0], ey + pad[1]
    w, h = max(8.0, ew - pad[0] - pad[2]), max(8.0, eh - pad[1] - pad[3])
    # Centring is done by PowerPoint, so only LEFT-aligned text may be indented.
    # For centred text the gap between the box edge and the first glyph IS the
    # centring, and treating it as an indent pushes the line off to the right.
    jc = it.get("jc") or ""
    align_left = (jc in ("", "flex-start", "start", "normal")
                  and it.get("align", "left") in ("left", "start", ""))

    if ink:
        y = ink[1]
        offset = (ink[4] - x) if (len(ink) > 4 and align_left) else 0
        if offset > 2:
            # something sits in front of the text: an icon in a flex row pushes
            # every line across, an inline chip only the first one
            if it.get("flex"):
                left_margin = offset
            else:
                first_indent = offset

    if lines <= 1 and not it.get("nowrap"):
        # a couple of pixels of slack so a one-liner cannot tip onto a second
        # line on a machine whose Arial is a hair wider; centred text grows to
        # both sides so that its centre does not move
        if align_left:
            w = min(w + 6.0, 1280.0 - x)
        else:
            x, w = max(0.0, x - 3.0), min(w + 6.0, 1280.0)

    if w <= 1 or h <= 0:
        return
    box = slide.shapes.add_textbox(
        Emu(int(x * PX)), Emu(int(y * PX)),
        Emu(int(w * PX)), Emu(int(max(h, 8) * PX)))
    tf = box.text_frame
    tf.word_wrap = not it.get("nowrap")
    # python-pptx writes spAutoFit by default; with it the box resizes to the
    # text and renderers draw the paragraph twice. The geometry is measured, so
    # the box must stay exactly as placed.
    tf.auto_size = MSO_AUTO_SIZE.NONE
    pad = [0, 0, 0, 0]
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Emu(int(pad[0] * PX))
    tf.margin_top = Emu(int(pad[1] * PX))
    tf.margin_right = Emu(int(pad[2] * PX))
    tf.margin_bottom = Emu(int(pad[3] * PX))

    paras = [[]]
    for r in it["runs"]:
        if r.get("br"):
            paras.append([])
        else:
            paras[-1].append(r)

    for pi, runs in enumerate(paras):
        # tf.paragraphs hands out a fresh proxy each call, so track the index
        p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
        jc = it.get("jc") or ""
        if jc in ("center", "centre"):
            p.alignment = PP_ALIGN.CENTER
        elif jc in ("flex-end", "right", "end"):
            p.alignment = PP_ALIGN.RIGHT
        else:
            p.alignment = ALIGN.get(it.get("align", "left"), PP_ALIGN.LEFT)
        lh = it.get("lh") or 0
        if lh:
            p.line_spacing = Pt(lh * PT)
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        if left_margin or (first_indent and pi == 0):
            pPr = p._pPr if p._pPr is not None else p._p.get_or_add_pPr()
            pPr.set("marL", str(int(left_margin * PX)))
            pPr.set("indent", str(int(first_indent * PX)) if pi == 0 else "0")
        for r in runs:
            f = r["f"]
            run = p.add_run()
            run.text = r["s"].upper() if f.get("upper") else r["s"]
            run.font.name = FONT
            run.font.size = Pt(max(1.0, f["size"] * PT))
            run.font.bold = f["weight"] >= 600
            run.font.italic = bool(f["italic"])
            if f.get("colour"):
                # already flattened at extraction time, never translucent here
                run.font.color.rgb = rgb(f["colour"])
            if f.get("spacing"):
                run.font._rPr.set("spc", str(int(round(f["spacing"] * PT * 100))))
    return box


def build(layout_path, out_path):
    data = json.loads(pathlib.Path(layout_path).read_text())
    icons = pathlib.Path(str(layout_path).replace(".json", "") + "-icons")

    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    blank = prs.slide_layouts[6]

    sld_sz = prs.part._element.find(
        "{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz")
    if sld_sz is not None:
        sld_sz.set("type", "screen16x9")

    counts = {"rect": 0, "text": 0, "svg": 0}
    for s in data["slides"]:
        slide = prs.slides.add_slide(blank)
        rect_ids = {i.get("eid") for i in s["items"] if i["t"] == "rect"}
        own_text = {i["eid"]: i for i in s["items"]
                    if i["t"] == "text" and i.get("solo") and i.get("eid") in rect_ids}
        for it in s["items"]:
            t = it["t"]
            if t == "rect":
                add_rect(slide, it, inner=own_text.get(it.get("eid")))
            elif t == "text":
                if it.get("eid") in own_text:
                    continue          # already written into its own shape
                add_text(slide, it)
            elif t == "svg" and it.get("img"):
                x, y, w, h = it["rect"]
                f = icons / it["img"]
                if f.exists() and w > 0 and h > 0:
                    slide.shapes.add_picture(
                        str(f), Emu(int(x * PX)), Emu(int(y * PX)),
                        Emu(int(w * PX)), Emu(int(h * PX)))
            counts[t] = counts.get(t, 0) + 1
        if s.get("title"):
            slide.notes_slide.notes_text_frame.text = s["title"]

    prs.core_properties.title = pathlib.Path(out_path).stem
    # python-pptx stamps its own author into every file it creates, from the
    # default template it ships. The repository states that no personal data
    # of anyone other than the owner appears in it, so clear it rather than
    # publish a stranger's name in three committed .pptx files.
    cp = prs.core_properties
    cp.author = "EDHEC project template"
    cp.last_modified_by = "EDHEC project template"
    prs.save(out_path)
    mb = pathlib.Path(out_path).stat().st_size / 1e6
    print(f"{pathlib.Path(out_path).name}: {len(data['slides'])} slides, "
          f"{counts['rect']} shapes, {counts['text']} text boxes, "
          f"{counts['svg']} icons, {mb:.1f} MB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: make_pptx_native.py <layout.json> <out.pptx>")
    build(sys.argv[1], sys.argv[2])
