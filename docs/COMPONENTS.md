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

## Charts for a second question

Four charts answer questions the first eight cannot.

**`.mekko` — Marimekko.** Column width is one share, segment height is another.
Reach for it when the finding is "a big share of a small market", which a bar
chart has to say in two charts and a sentence. The widths must total 100, and
nothing checks that for you.

**`.tor` — tornado.** Sensitivity. One row per driver, sorted widest first, so
the eye stops where the drivers stop mattering. Five rows is plenty; below the
fourth, nothing is changing the decision.

**`.gantt` — a plan with dependencies.** The connectors are the argument. A plan
where the bars merely sit next to each other says the calendar decided; a plan
with connectors says the work decided. Rows are `.gline`, **not** `.grow` —
`.grow` is the slide content area and a row that inherits `flex:1` collapses the
chart. Dependency coordinates are x in per cent of the track and y in px from
the top of the first row.

The connectors end in a **dot, not an arrowhead**, on purpose. A CSS triangle is
borders on a zero-size box, which the exporter reads as an empty rectangle, so
the arrow would disappear in exactly the file somebody opens to edit.

**`.ladder` — sizing ladder.** TAM to SAM to SOM, except every step shows its own
multiplier and its own reason. A funnel hides the arithmetic. A ladder makes each
step arguable on its own, which is what a jury attacks.

**`.dotplot` — peers.** One row per measure, the peers on the ramp, you in the
accent. It shows the spread. A bar chart of averages destroys the spread, and the
spread is usually the finding.

## Slide archetypes

Whole-slide layouts. Copy the entire `<section>` from the gallery, not the inner
div.

**`.exec` — executive summary.** Situation, complication, answer, because, ask.
The answer row is the only one in the brand colour, because a summary with four
emphases has none. Four rows is the ceiling: a fifth means you are holding two
summaries and should split them.

**`.tree` — issue tree.** One question split into parts that do not overlap and
leave nothing out. Outline the branch the evidence supports, so the audience
knows where the next slide goes. Three branches is the limit at 1280x720; a
fourth drops the type below the floor.

**`.agenda` — section divider.** Where the audience is. The dot carries done
against still to come, so the distinction never rests on a grey too light to read
from the back of a room. The minutes are for you, and they also tell a jury you
rehearsed.

## One stylesheet, two files

`design/components.css` is the master. Both templates carry a **generated copy**
of it, between markers:

```
/* ==== SHARED COMPONENTS -- generated from design/components.css ==== */
...
/* ==== END SHARED COMPONENTS ==== */
```

Do not edit inside that block. Edit the master and run:

```bash
python3 tools/sync_components.py
```

`./build.sh` runs `--check` and fails if a template has drifted.

Why generate rather than link: the chart stylesheet used to live only in
`gallery.html`. The gallery's whole job is to be copied from, so every chart
copied into `slides.html` arrived unstyled — a donut as a bare number, a
waterfall as a stack of empty divs. Silent at copy time, loud at rehearsal time.
Each template still carries a full copy, so one file still opens offline on its
own.

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

## The scale: nine sizes, ten gaps, three radii

Every size in the templates comes from a fixed set. The tokens are at the top of
each template and in `design/tokens.css`:

| | Values | Token |
|---|---|---|
| Type | 11.5 · 13 · 14 · 15.5 · 17 · 19 · 23 · 30 · 46 px | `--t1` … `--t9` |
| Gaps and padding | 4 · 6 · 8 · 12 · 16 · 20 · 24 · 32 · 48 · 64 px | `--s1` … `--s10` |
| Corner radius | 4 · 6 · 10 px | `--r1` … `--r3` |

**Use a rung.** Picking 12.5px because a line nearly fits is how the previous
version ended up with 35 different font sizes, which is why type that should
have looked the same across two slides did not.

Two rules behind the numbers:

- **11.5px is the floor.** The exporter maps 1 CSS px to 0.75 pt, so 11.5px
  arrives in PowerPoint at 8.6pt. Below that nobody reads it from the back of a
  room. Anything smaller in the old files was raised, not snapped down.
- **A handful of display sizes sit off the scale on purpose** — the big slide
  number in the corner, the title-slide wordmark. They are decoration at one
  known position, not text in a system, and they are listed as exceptions in the
  token comment rather than silently different.

Check a change before you commit it:

```bash
grep -o 'font-size:[0-9.]*px' slides/slides.html | sort | uniq -c | sort -rn
```

Anything outside the nine rungs should be a display size you can name.

## Contrast

Every text-on-colour pairing in the templates meets WCAG AA (4.5:1). That is not
an accessibility box-tick: a projector in a bright room costs you far more
contrast than a laptop screen suggests, and the pairing that fails is always the
one carrying the number you came to show.

Two consequences you will hit if you add colours:

- White on the warm gold `--orange` is **3.04:1** and fails. Use `--orange-dark`
  for any chip or band with text on it. The bright gold is for fills without text.
- The intensity ramp carries white text only from `--int2` down. `--int0` and
  `--int1` are too light; put dark text on those.
