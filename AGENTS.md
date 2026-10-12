# Working in this repository

For AI coding agents, and for anyone who wants the rules in one place.
Read this before changing anything.

## What this is

Slide, paper and one-pager templates in plain HTML, plus a toolchain that
exports them to PDF and to a **native editable PowerPoint** by reading rendered
geometry out of Chrome.

It is coursework infrastructure. The user is a student with a deadline, not a
developer. Optimise for *their deck still opening in five years*, not for
elegance.

## The one command

```bash
PY=.venv/bin/python ./build.sh
```

It must pass before anything is committed. It fails on things a thumbnail will
not show you:

| Gate | What it catches |
|---|---|
| `check_slides.py` | overflow past 1280×720, content under the footer, text below 11.5px, any run that misses WCAG AA against the colour **actually painted behind it** |
| `sync_components.py --check` | a template that drifted from `design/components.css`, or disagrees with `design/tokens.css` |
| `inline_assets.py --check` | a design asset referenced by file, which vanishes from a mailed single file |
| `check_images.py` | a README picture that no longer matches the template |
| page-count check | a one-pager that became two pages |

A gate that fails is information, not an obstacle. Do not route around one.

## Hard rules

**Never author inside a generated block.** `/* SHARED COMPONENTS */ … /* END */`
is written by `sync_components.py`. Edit `design/components.css` and re-run it.

**Never declare `--logo` yourself.** The tool owns that token. Write
`url("edhec-logo.svg")` in the rule that needs it.

**Never use `transform: rotate()` on text.** The exporter reads the rotated
bounding box and writes the text flat, so it lands on its side in the PDF and
upright in the `.pptx`.

**Never build a shape out of borders on a zero-size box.** A CSS triangle
arrives in PowerPoint as an empty rectangle. Use a filled div or a circle.

**Never add a font size off the scale.** Nine type sizes, ten spacing steps,
three radii, all listed in `docs/COMPONENTS.md`. They are values to pick from,
not CSS variables, and `11.5px` is the floor because the exporter maps 1 CSS px
to 0.75 pt.

**The bright gold `--orange` never carries text.** White on it is 3.04:1. Use
`--orange-dark` (5.57:1) or `--orange-mid` (4.52:1) for anything with a label.

Every one of these exists because it already went wrong once. The reasoning is
in `TODO.md` under *Closed*.

## House style

**One finding per slide, stated in the title.** "Cost structure" is a label.
"Cost per engagement rose 23 per cent while price held" is a finding. If you
cannot write the action title, the slide does not yet know what it is for.

**The accent is a raised eyebrow, not a highlight.** Burgundy is the voice. Use
the warm gold at most once per slide, and only where it means *careful*. A deck
where everything is highlighted highlights nothing.

**Every chart value is a literal number in the markup.** No charting library, no
data file. A chart has to be correctable during a rehearsal.

See `docs/COMPONENTS.md` for what exists and `docs/FRAMEWORKS.md` for which
framework to build from what.

## The copy and design filter: antislop

This repository uses **[antislop](https://github.com/miqdadbadjuber/anti-slop)**
by Miqdad Badjuber (MIT) as its filter against generic, AI-shaped output. It is
not vendored here, because a copied rulebook goes stale. Install it into your
agent:

```bash
npx antislop-ai
```

Version 3.2.20 at the time of writing. `npx antislop-ai --update` refreshes it,
`--mode during` keeps it active while you work rather than only at review time.

It is a **filter, not a style guide**: it removes, it does not prescribe
colours, fonts or layout. Direction stays yours. That division of labour is
exactly right for this repo, which already supplies the direction in
`design/tokens.css`.

The rules that bite hardest on slides and papers, as opposed to web UI:

- **Evidence over claims.** Anything presented as fact is real and verifiable,
  or it is not shown. In coursework this is not a style question, it is the
  thing being graded. If a figure is an assumption, the slide says so.
- **No invented numbers.** No "10K+ users", no "99.9%", no placeholder
  statistic that survives into the hand-in because nobody replaced it.
- **No filler copy.** Cut "in today's fast-paced environment", "leverage",
  "seamless", "cutting-edge". If a sentence would survive being deleted, delete
  it.
- **No decorative arrows, sparkles or badges.** An arrow on every button is
  decoration. A pill above the headline that repeats the headline is decoration.
- **Intentionality.** Every visual decision has a reason you can state. "It is
  the default" is a red flag, not a reason.

**The filter rejects technique without purpose, not technique itself.** If a
technique it names serves a real hierarchy or readability goal, keep it and
*write the reason down in a comment*. There is a worked example of exactly this
in `site/index.html`, where the eyebrow above the H1 survives with its
justification recorded.

## Things already decided against

Do not re-propose these. The reasoning is in `TODO.md`.

npm as a **project dependency**, Vite, Tailwind, a Markdown authoring layer, a
charting library, radar and Sankey charts, a CSV data file beside the HTML, AI
deck generation from a prompt, more themes, a light/dark toggle.

The no-npm rule is about what this repository *ships*: there is no
`package.json`, no `node_modules`, and a clone builds without one. Running a
tool with `npx` is a different thing. antislop installs into your agent, not
into the deck, and nothing it does is required to build.

## When you are not sure

Measure it. This repository prefers a number to an opinion, and nearly every
rule above exists because somebody measured something and was surprised.
