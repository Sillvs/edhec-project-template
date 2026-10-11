# Deferred

Found during a scope review on 2026-10-11 and consciously deferred, because a
deferred item that is not written down is not deferred, it is forgotten.

Ordered by what bites first.

---

## 1. Slide overflow is documented but not detected

**Evidence:** `docs/EXPORT.md` names silent clipping past 720 px as the most
dangerous failure mode. Nothing in `build.sh`, `extract_layout.mjs` or either
Python tool checks for it.

**Why it bites:** a slide that overflows still exports, still looks plausible in
a thumbnail, and loses its last line. Somebody hands that in.

**Fix:** the layout extractor already walks every element with its exact
geometry. Add a pass that flags any element whose bottom edge exceeds 720 px
minus the footer, and make `build.sh` exit non-zero with the slide number and
the offending element. The measurement already exists; only the assertion is
missing.

**Note:** a 32-agent review ranked this first among everything proposed, ahead
of every new component. It is still the top item.

**Partially covered now:** `build.sh` fails if `onepager.pdf` is not exactly one
page, which is the same class of check for the one format where overflow adds a
page rather than clipping. Slides clip silently and are still unchecked.

---

## 2. Build outputs are committed and can go stale

**Evidence:** tracked `.pdf`, `.pptx` and `.png` files make up most of the
repository by size.

**Nuance:** this is not simply wrong. `docs/img/*` must stay committed or the
README renders broken on GitHub, and the example is an archive that should not
move. The questionable ones are the template's own outputs: `slides/slides.pdf`,
`slides/slides.pptx`, `slides/slides-pictures.pptx`, `slides/gallery.pdf`,
`paper/paper.pdf`, `paper/onepager.pdf`. They are regenerable, they will
silently stop matching their sources, and a reader cannot tell.

**Fix:** either gitignore those six and let `./build.sh` produce them, or add a
CI job that rebuilds and fails if the committed copy differs.

---

## 3. Nothing verifies the build still works

**Evidence:** no `.github/workflows`.

**Why it bites:** the toolchain depends on a Chrome build, poppler, Node 22 and
python-pptx. A change to any of them breaks the export, and the first person to
find out is whoever is exporting at midnight before a hand-in. This already
happened once: a Playwright upgrade moved `chromium-1223` to `chromium-1234` and
the whole toolchain stopped with "No such file or directory". Fixed by
`tools/find-chrome.sh`, but only because somebody was watching.

**Fix:** a GitHub Action that runs `./build.sh` on push and uploads the PDF and
PPTX as artefacts. It doubles as the preview mechanism for teammates who do not
clone.

---

## 4. The gallery is not exported to PowerPoint

**Evidence:** `build.sh` runs `extract_layout.mjs` on `slides/slides.html` only.

**Why it bites:** the gallery is the catalogue, so it is the file people copy
from, and it is the one file whose PowerPoint behaviour nobody has ever seen.
The rotation bug lived there undetected for exactly this reason.

**Fix:** run the extractor over the gallery too, even if the `.pptx` is only
ever inspected and never shipped. Cheap, and it turns the catalogue into a test.

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
