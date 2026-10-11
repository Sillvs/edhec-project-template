# Components

`slides/slides.html` is the lean starter. `slides/gallery.html` shows every
component and every chart in place. Copy the markup out of those files rather
than out of this page; this page says what each one is **for**.

## The rules that matter more than the components

**One accent per slide.** The warm gold means "careful": a risk, a deferral, a
constraint, the number that decides. Everything else is burgundy. A slide with
three highlights has none.

**The title is the finding.** `Why invest in AI and why do it now?` is a topic.
`Cloud wins five of six criteria` is a finding. Write the second kind, then the
slide can be read without you in the room.

**Repeated boxes must be the same height.** Normalise the text to the same
number of lines, and pin the height in CSS so a later edit cannot break the row.
Uneven boxes are the single fastest way to look unfinished.

**Say each number once.** If a figure appears on two slides, two people will
present it and the audience will hear a contradiction.

---

## Slide frame

```html
<section class="slide" data-title="Shown in the overview" data-fnum="Q1">
  <span class="slidemark"></span>          <!-- logo, top right -->
  <div class="ghost">1</div>               <!-- the faint numeral -->
  <div class="pad">
    <div class="secrow"><span class="n">Q1</span><span class="t">Section</span></div>
    <div class="action">The finding, in one sentence</div>
    <div class="grow"> … content … </div>
  </div>
  <div class="foot">…</div>
</section>
```

`data-fnum` overrides the footer mark, which is how one question can span two
slides and both still read `Q1`. Leave it out and slides number themselves
`01, 02, …`.

## `.qblock` — the question frame

A bordered block whose legend states the question it answers. This is the
device that keeps a consulting deck honest: if you cannot write the question,
the block does not belong on the slide.

```html
<div class="qblock">
  <span class="qtag">The question this block answers</span>
  …
</div>
```

`.qblock.warm` for a block that carries a caution.

## `.chain` — a process or an argument in steps

Circles, labels, a short line of support, chevrons between. Four steps is the
comfortable maximum. Make the last step the caveat and give it the accent
colour when the chain is an argument rather than a process.

`.chain.sm` for a tighter version when the slide is busy.

## `.pflow` — a process with layers underneath

The audit-process slide in the example: a row of steps, and under each one a
support layer and a change layer. Use the `.pchip` tag to answer a yes/no
question per step at a glance, such as accelerate versus redesign.

## `table.dark` — comparisons

Dark header band, zebra rows, `.num` for right-aligned figures, `tr.tot` for a
total. Add a verdict column with `.verdict` chips (`.yes`, `.part`, `.no`,
`.warm`) when the table is a decision rather than a list.

Keep tables to six or seven rows. Beyond that it is a backup slide or an
appendix, not a slide.

## `.bars` — stacked cost or value bars

Segments `s1`, `s2`, `s3` in widths given as percentages of the widest total,
with `.barmark` as a dashed threshold line. The threshold is what makes the
chart an argument: one bar is below it and the others are not.

## `.tiles` — the three numbers

Three or four, no more. `.n.orange` marks the one that decides.

## `.road` — a phased plan

Each phase has a body and a gate. Write the bodies to the same length and the
gates to the same length, or the dividers will not line up.

## `.sgrid` — scenarios against layers

One column per scenario, one row per layer (solution, organisation, process).
Give the last column the accent and use it for the real constraint.

## `.pts` — bullets with icons

Two columns by default, `.pts.one` for a single column, `.pts.three` for three.
Roughly ten words per bullet. No trailing clause that merely restates the point.

## Strips and bands

- `.note-strip` a qualification; `.note-strip.warm` a caution.
- `.band-navy` the closing statement of a slide, centred.
- `.xband` a compact labelled line.

## Icons

The library sits in one `<svg>` block at the top of the file and is reused with
`<use href="#i-name"/>`. Available: `i-cloud i-server i-shield i-euro i-clock
i-gauge i-people i-cal i-check i-alert i-lens i-doc i-net i-lock i-chart
i-target i-flag i-bulb i-scale i-up i-down i-updown i-coins i-grid i-globe
i-cog i-stop i-book i-pen i-route i-split i-handshake`.

Add one by dropping another `<symbol>` into that block. Keep it line art on a
24×24 viewBox with no fill, so it inherits the stroke colour.

## Closing slide

`.reco-slide` is full-bleed dark burgundy, the same tone as the band on the
title page, so the two bookend the deck. It takes the recommendation, four
numbers and three short blocks. Nothing else: it is the slide people photograph.


---

# Charts

All of them live in `slides/gallery.html`. They are built from divs wherever
possible, because div charts survive the PowerPoint export as native editable
shapes. Only the donut and the trend line need SVG, and those arrive in
PowerPoint as pictures.

There is no charting library and no data file. Every value is a number in the
markup, which means a chart can be corrected in the ten minutes before a
rehearsal, by anybody, without a toolchain.

| Component | Use it for | Do not use it for |
|---|---|---|
| `.donut` | one share of one whole | more than four categories |
| `.cols-chart` | comparing a handful of values | a time series with many points |
| `.stack` | composition changing over time | precise comparison of middle segments |
| `.fall` | bridging a start number to an end number | anything that is not additive |
| `.trend` | a measured series, with a dashed forecast | fewer than four points |
| `.quad` | positioning options against two criteria | more than six bubbles |
| `.funnel` | a conversion or a filter, stage by stage | stages that are not subsets |
| `.carto` | a value per country | precise geography |
| `.bars` | totals split into components, horizontally | more than five bars |

## Reading the markup

Heights and widths are percentages written straight into `style`. A column at
`height:83%` is 83 % of the tallest. Keep the largest value at or near 100 % and
scale the rest by hand, or the chart lies about the differences.

In the waterfall each bar is positioned with `bottom` and `height`, both as
percentages, so a bar that floats is just a bar whose `bottom` is not zero.

In the donut, each segment is a circle with `stroke-dasharray` set to its share
of the circumference and `stroke-dashoffset` set to the sum of the shares before
it. The helper in `tools/mockups.py` is not needed; the numbers are already in
the file.

## The tile map

A tile map gives every country one square. It avoids two problems with a real
outline at once: Luxembourg stays visible, and no map file has to be licensed
and attributed. Each square carries the country code and a shade from `v1` to
`v4`.

If you genuinely need a real outline, drop a public-domain SVG into `slides/`
and inline it. Check the licence first, and note it in the deck.

## Colour in charts

The intensity ramp `--int0` to `--int3` plus `--deep` is the sequential scale.
Use it for anything ordered: low to high, early to late, small to large.

The warm gold is **not** part of the scale. It marks the one series, bar or
bubble the audience should look at. One per chart.
