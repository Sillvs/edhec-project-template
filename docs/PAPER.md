# Writing a paper in the same design

`paper/paper.html` is an A4 document that shares the deck's palette, its
components and its logo, but is set for continuous reading rather than
projection.

```bash
./build.sh paper        # -> paper/paper.pdf
```

## What it gives you

- A cover page in the deck's design: burgundy rule, logo, title, authors, a
  dark band at the foot.
- **Real page numbers** and a running head, from CSS, on every page except the
  first.
- Automatic section and figure numbering, so inserting a section in the middle
  does not mean renumbering by hand.
- The deck's components, reset for print: the question frame becomes a callout,
  the note strips and the closing band come across unchanged, tables keep the
  dark header band.

## Page numbers

Chrome supports CSS page-margin boxes, which most of the web says it does not.
This works:

```css
@page{
  size:A4; margin:24mm 22mm 20mm;
  @bottom-center{ content:counter(page); }
  @top-right{ content:"Short running title"; }
}
@page:first{ margin:0; @bottom-center{content:""} @top-right{content:""} }
```

Two conditions. Export with `--no-pdf-header-footer`, or Chrome prints its own
footer on top of yours. And edit the running title in the `@top-right` rule, it
cannot be read out of the document.

`counter(pages)` gives the total if you want "3 of 12".

## Typography

Body text is a serif, headings and tables stay in the deck's sans. A paper is
read continuously and a serif carries that better, while the sans headings,
the rules and the colour keep both documents recognisably one family.

For an all-sans paper, change one line:

```css
html,body{ font-family:var(--sans); }
```

## Keeping blocks together

Everything that should not be split across a page break already carries
`break-inside:avoid`: callouts, strips, tables, figures, tile rows. Headings
carry `break-after:avoid` so none is left alone at the foot of a page.

Force a page break with `class="pagebreak"` on the element that should start
the new page.

## Figures

Drop a PNG or SVG into `paper/` and reference it. Captions number themselves.

A slide makes a good figure:

```bash
chrome --headless --window-size=1280,720 --screenshot=paper/fig-1.png \
       "file://$PWD/slides/slides.html#8"
```

## What this is not

It is not a LaTeX replacement. There is no bibliography engine, no cross
referencing and no automatic table of contents. For a thesis with a hundred
citations, use LaTeX. For a consulting report, a case study or a seminar paper
of twenty pages that has to look like the deck it accompanies, this is faster
and the result matches.

If you want a table of contents, write it by hand on the second page. At this
length that is a five-minute job and it will not drift, because you will write
it last.
