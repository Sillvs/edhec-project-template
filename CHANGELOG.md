# Changelog

Notable changes to this template. Dates are the day the work landed on `main`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions are `MAJOR.MINOR.PATCH.MICRO`.

## [1.0.0.0] — 2026-10-12

First tagged release. Everything below already shipped to `main`; this entry
marks the point the template became something another team can rely on.

### Added

- **Three deliverables.** A 1280x720 slide deck, an A4 paper with real page
  numbers and automatic section numbering, and a one-page executive
  leave-behind whose build fails if it ever becomes two pages.
- **Thirteen charts.** Donut, columns, stacked columns, waterfall, trend with a
  dashed forecast, two-by-two, funnel, tile map, Marimekko, tornado, Gantt with
  dependency connectors, sizing ladder, peer dot plot. No charting library:
  every value is a literal number in the markup, so a chart stays correctable
  during a rehearsal and survives the export as editable shapes.
- **Three whole-slide archetypes.** Executive summary, issue tree, section
  divider.
- **A native editable PowerPoint export.** `tools/extract_layout.mjs` drives
  Chrome over the DevTools protocol and reads the rendered geometry;
  `tools/make_pptx_native.py` rebuilds it as real shapes and real text. A
  teammate who has never opened a terminal can fix a typo an hour before the
  talk.
- **Four checks that catch what a thumbnail hides.** `check_slides.py` measures
  overflow past the canvas, content running under the footer, text below the
  11.5px floor, and every text run against the colour actually painted behind
  it. `check_images.py` catches a README picture that stopped matching its
  template. `sync_components.py --check` catches a template that drifted from
  `design/components.css` or from `design/tokens.css`. `inline_assets.py
  --check` catches a design asset referenced by file, which vanishes from a
  mailed single file.
- **CI** that rebuilds on every push and fails if a committed PDF, PowerPoint or
  README picture went stale. Comparison is by word stream and changed pixel
  area, because bytes differ on every build and a check that always fails gets
  switched off.
- **A live site** at <https://sillvs.github.io/edhec-project-template/>, built
  from the repository's own tokens and publishing the templates as themselves.
- **Four documents.** `docs/EXPORT.md` on the traps that silently break output,
  `docs/COMPONENTS.md` on what exists, `docs/FRAMEWORKS.md` mapping nine
  consulting frameworks to the components that carry them, and `docs/SLIDES.md`
  on slide craft, sourced and measured against this renderer.
- **`AGENTS.md`**, with [antislop](https://github.com/miqdadbadjuber/anti-slop)
  adopted as the copy and design filter.
- **A worked example**, `examples/auditcert-france-2026/`, gated like everything
  else.

### Fixed

- **Six WCAG AA failures**, four found by review and two by the checker on its
  first run. The last two had survived three CSS reviews because the rule
  setting the text colour and the rule setting the background live in different
  selectors, and only the gallery rendered them.
- **Thirty-five ad-hoc type sizes** snapped onto a nine-rung scale, nine of them
  below the floor where the PowerPoint export drops under 8.6pt.
- **The chart stylesheet existed only in the gallery**, so every chart copied
  into the deck arrived unstyled. Silent at copy time, loud at rehearsal time.
- **The documented rebrand did not work.** `TRADEMARKS.md` told a forker to
  change one token and run one command; the command only wrote the component
  block, so the colour stayed in five files and the next build failed.
- **A rotated axis label** that the exporter wrote flat, landing on its side in
  the PDF and upright in the PowerPoint.
- **A Chrome path pinned to one Playwright build number**, which a routine
  upgrade broke mid-session.

### Security and privacy

- MIT licence with the EDHEC trademark carved out in `TRADEMARKS.md`.
- No personal data of anyone other than the repository owner, verified across
  the full history.
- `python-pptx` stamps its own author into every file it creates; the exporters
  now clear that.
