# What was found, and what was decided against

Nothing is currently deferred. Every item from the 2026-10-11 scope review is
closed, and each is kept below with its reasoning, because a repository that
forgets why it did something does it again.

If you add an item, put it above this line with its evidence. A deferred item
that is not written down is not deferred, it is forgotten.

---

## Closed

Kept so the reasoning survives.

- **No licence on a public repository** — MIT with an explicit trademark
  carve-out for `design/edhec-logo.svg`.
- **Two files share 431 lines of CSS** — `design/components.css` is the master,
  `tools/sync_components.py` writes it into both templates, `./build.sh` fails
  on drift. It also turned out the chart CSS was in the gallery *only*, so every
  chart copied into the deck arrived unstyled. The drift risk was theoretical;
  that one was live.
- **The logo vanishes from a mailed deck** — inlined as a percent-encoded data
  URI by `tools/inline_assets.py`, which also refuses to run if a template
  declares the `--logo` token itself.
- **Four contrast pairings fail WCAG AA** — all fixed, plus two the original
  review missed: a gold gradient whose light end was 3.04:1, and
  `design/tokens.css` still carrying the failing value after the templates had
  moved. Token agreement is now checked by `./build.sh`.
- **Rotated text lies flat in the native PowerPoint** — the 2x2 y-axis label sits
  above the axis now, left aligned, and the reason is in the CSS.
- **Ancestor debris in the tokens** — `--olive`, `--optA` to `--optD` and their
  dead classes deleted. Two of the four were not EDHEC colours at all.
- **Slide overflow is documented but not detected** — `tools/check_slides.py`
  measures every box against the 1280x720 canvas from the geometry Chrome
  actually rendered, and `./build.sh` fails on any that runs past it. This was
  ranked first by a 32-agent review, ahead of every new component, and it was
  right to be.
- **The gallery is not exported to PowerPoint** — the extractor now runs over
  the gallery as well. No `.pptx` ships from it, but its geometry is checked,
  which turns the catalogue into a test. The two contrast failures below were
  found the hour after this went in, and both were gallery-only.
- **Build outputs are committed and can go stale** — CI rebuilds on every push
  and fails if a committed PDF or README picture no longer matches its source.
  Neither check could use the obvious comparison. PDFs carry a Chrome-generated
  `/ID` so bytes always differ, and `pdftotext -layout` always differs too,
  which the first CI run demonstrated with a one-blank-line diff at identical
  page counts. Pictures are rasterised, so bytes always differ there as well,
  and mean pixel difference turned out to miss a real edit by an order of
  magnitude. Both now measure what staleness would actually change.
- **Nothing verifies the build still works** — `.github/workflows/build.yml`
  runs the whole build on every push and uploads the deliverables for 30 days,
  which doubles as the preview for teammates who do not clone. This was not
  hypothetical: a Playwright upgrade moved `chromium-1223` to `chromium-1234`
  mid-session and the toolchain stopped with "No such file or directory".
- **The worked example was outside every check, and failing** — `examples/` is
  the file students copy. It had 3 live AA failures, 51 text runs below the
  11.5px floor, and committed outputs stale by a full commit. `build.sh` now
  builds and gates it like everything else.
- **The documented rebrand did not work** — TRADEMARKS.md told a forker to
  change the burgundy in `tokens.css` and run `sync_components.py`. The script
  only wrote the component block, so the colour stayed in five files and the
  next build failed with no hint why. This is the MIT-fork path the trademark
  carve-out depends on. The script now writes tokens into all four templates.
- **Content ran under the footer, undetected** — not an overflow, so the canvas
  test said nothing and the PDF merely looked cramped. `check_slides.py` now
  derives the footer from what repeats across the document and flags
  collisions. The first version took the highest text in the bottom band and
  flagged every chart axis label, which is why it derives rather than assumes.
- **Nothing enforced the 11.5px floor** — claimed in three documents, checked
  nowhere. Now part of `check_slides.py`.
- **`check_images.py` passed after comparing nothing** — a wrong path, a
  renamed folder or the wrong cwd printed "every picture still matches" and
  exited 0, and it is the only staleness gate on the README.
- **A gradient stop of `transparent` killed the build** — `ValueError` on a
  traceback naming neither the slide nor the rule. Unparseable colours are now
  reported as unmeasured, and the summary line says so rather than claiming a
  clean pass.
- **The `.pptx` had no staleness guard** — the headline deliverable, and a deck
  edit committed without it left the PowerPoint contradicting the PDF beside
  it. CI now compares the text runs.
- **Two white-on-gold pairings carried text** — `.funnel .f.s5` and
  `.quad .bub.accent` set a `--orange` background under inherited white text,
  3.04:1. They survived three contrast reviews because the colour and the
  background are set in different selectors and `slides.html` never rendered
  either one. Grepping CSS could not have found this; measuring the rendered
  page did, on the first run. Now checked on every build.

## Not deferred, decided against

Proposed and rejected. The reason is recorded so they are not re-proposed every
term.

- **Radar and Sankey charts** — both must be SVG, so they arrive in PowerPoint as
  dead pictures on exactly the slide where somebody wants to argue with the shape.
- **A CSV data file beside the HTML** — breaks self-containment.
- **A charting library** — a dependency, and canvas output hits no branch in the
  extractor, so the chart returns as an empty rectangle.
- **AI deck generation from a prompt** — unwinnable against tools that do it free
  in ninety seconds, and off-mission.
- **npm, Vite, Tailwind or a Markdown authoring layer** — violates no-npm and
  no-build-step. A Markdown converter also has to guess the layout, and the
  layout is the point.
- **Speaker notes moved into the deck markup** — the supporting evidence turned
  out to be a misread attribute.
- **A runtime that computes figures from a declared source** — fails on the very
  slide it was invented for. Only a build-time checker survives.
- **Business Model Canvas as a component** — nine unequal cells is a worksheet,
  not a finding, and does not fit 1280x720 at legible type.
- **More themes and a light/dark toggle** — multiplies the design surface without
  serving any moment in a team's week.
- **A phone mockup for the README** — nobody reads a 1280x720 deck on a phone.
  The picture would be honest about nothing.
