# Deferred: hardening

Found during a scope review on 2026-10-11 and consciously deferred in favour of a
component sprint. Each item is written down because a deferred item that is not
written down is not deferred, it is forgotten.

Ordered by what bites first.

---

## 1. No licence on a public repository

**Evidence:** `gh repo view` reports `licence=none`, visibility `PUBLIC`.

**Why it bites:** a public repository without a licence is "all rights reserved"
by default. Another EDHEC team that clones this and hands in a deck built from it
has no legal permission to do so. The repository exists to be reused, and right now
reuse is the one thing it does not permit.

**Fix:** add an MIT or CC-BY licence file. One commit.

**Caveat to check first:** `design/edhec-logo.svg` is the school's trademark and is
not ours to relicense. Whatever licence covers the code, the logo needs an explicit
carve-out line saying it belongs to EDHEC and is included for use by EDHEC members.

---

## 2. Two files share 431 lines of CSS

**Evidence:** `slides/slides.html` and `slides/gallery.html` share 431 byte-identical
CSS lines. Measured, not assumed: **0 lines currently differ** between the shared
parts, so this has not yet caused a bug.

**Why it bites:** it has not bitten *yet*. The first time somebody fixes a component
in one file and not the other, the gallery stops being a faithful catalogue of what
the deck can do, and the drift is invisible because both files still render fine.

**Fix options, cheapest first:**
- A check in `build.sh` that extracts the shared block from both files and fails the
  build if they differ. Keeps both files self-contained, costs ten lines of shell.
- A build-time inline step: one `design/deck.css`, inlined into each template on
  build. Removes the duplication but introduces the authoring build step the README
  explicitly promises not to have. Only do this if the promise is renegotiated.

The first option is the one that fits the stated constraints.

---

## 3. Slide overflow is documented but not detected

**Evidence:** `docs/EXPORT.md` names silent clipping past 720 px as the most
dangerous failure mode. Nothing in `build.sh`, `extract_layout.mjs` or either
Python tool checks for it.

**Why it bites:** a slide that overflows still exports, still looks plausible in a
thumbnail, and loses its last line. Somebody hands that in.

**Fix:** the layout extractor already walks every element with its exact geometry.
Add a pass that flags any element whose bottom edge exceeds 720 px minus the footer,
and make `build.sh` exit non-zero with the slide number and the offending element.
The measurement already exists; only the assertion is missing.

---

## 4. Build outputs are committed and can go stale

**Evidence:** 18 tracked `.pdf`, `.pptx` and `.png` files, 5.7 MB of a 6.2 MB
repository.

**Nuance:** this is not simply wrong. `docs/img/*` must stay committed or the README
renders broken on GitHub, and the example is an archive that should not move. The
questionable ones are the template's own outputs: `slides/slides.pdf`,
`slides/slides.pptx`, `slides/slides-pictures.pptx`, `slides/gallery.pdf`,
`paper/paper.pdf`. They are regenerable, they will silently stop matching their
sources, and a reader cannot tell.

**Fix:** either gitignore those five and let `./build.sh` produce them, or add a CI
job that rebuilds and fails if the committed copy differs.

---

## 5. Nothing verifies the build still works

**Evidence:** no `.github/workflows`.

**Why it bites:** the toolchain depends on a Chrome build, poppler, Node 22 and
python-pptx. A change to any of them breaks the export, and the first person to find
out is whoever is exporting at midnight before a hand-in.

**Fix:** a GitHub Action that runs `./build.sh` on push and uploads the PDF and PPTX
as artefacts. It doubles as the preview mechanism for teammates who do not clone.

---

## 6. The logo vanishes from a mailed deck

**Evidence:** `slides.html` references `edhec-logo.svg` three times as a relative
`url()`. Four byte-identical copies of the file exist, one beside each template.

**Why it bites:** the README promises one file that opens offline. Mail just the
HTML to a jury and the logo is gone from the title slide and every slide mark.
Because it is a CSS background there is no broken-image icon, only white space,
so nobody notices until it is in front of the room.

**Fix:** inline it as a data URI into a `<style id="assets">` at the end of the
document, keeping `design/edhec-logo.svg` as the master.

**Gate:** do this in the same pull request as the licence (item 1). Base64-embedding
a trademark into every forked file is the licence question again, louder.

---

## 7. Four contrast pairings fail WCAG AA

**Evidence, recomputed from the shipped tokens:**

| Selector | Pairing | Ratio |
|---|---|---|
| `.verdict.warm`, `.cellflag.warm` | white on `--orange` | 3.04:1 |
| `td.i2` | white on `--int2` | 3.99:1 |
| `.band.green` | white on `--olive` | 4.14:1 |

AA needs 4.5:1 for body text. The core of the palette is strong and not at issue:
burgundy on white is 12.49:1, white on `--deep` is 17.73:1.

**Fix:** three of the four need no new token. Moving the warm chips to
`--orange-dark` gives 5.57:1. `--int2` needs a slightly darker value that keeps the
intensity ramp monotone.

---

## 8. Rotated text lies flat in the native PowerPoint

**Evidence:** `.quad-y span` in `gallery.html` uses `transform:rotate(-90deg)`.
`make_pptx_native.py` never sets a shape or text rotation, and the extractor reads
no transform at all.

**Why it has not bitten yet:** the gallery is not exported to PPTX, so the only
rotated label in the repo never reaches the exporter. It bites the first time
somebody copies the two-by-two into their own deck, and the PDF will look correct,
so they will not check.

**Fix in CSS, not the exporter:** put the axis label above the axis, left aligned.
Add it to `docs/EXPORT.md` as a seventh trap.

---

## 9. Ancestor debris in the tokens

**Evidence:** `--olive:#7A8300` and `--olive-dark:#5F6600` are the TUM olive from
the deck this design descends from. The colour migration did not map them because
they were not in the mapping table. Several component classes that use them have
zero usages in any shipped file.

**Checked and NOT true:** a review agent also claimed TUM blue `#0065BD` and orange
`#E37222` survive in the stylesheet. They do not; the migration caught both.

**Fix:** delete the dead classes rather than retinting them, and either remove the
olive tokens or map them into the burgundy ramp.

---

## 10. Slide overflow still undetected

Already listed as item 3. Kept here as a pointer because a 32-agent review ranked
it first among everything proposed, ahead of every new component.

---

## Not deferred, decided against

These were proposed and rejected. The reason is recorded so they are not
re-proposed every term.

- **Radar and Sankey charts** — both must be SVG, so they arrive in PowerPoint as
  dead pictures on exactly the slide where somebody wants to argue with the shape.
- **A CSV data file beside the HTML** — breaks self-containment.
- **A charting library** — a dependency, and canvas output hits no branch in the
  extractor, so the chart returns as an empty rectangle.
- **AI deck generation from a prompt** — unwinnable against tools that do it free
  in ninety seconds, and off-mission.
- **npm, Vite, Tailwind or a Markdown authoring layer** — violates no-npm and
  no-build-step. A Markdown converter also has to guess the layout, and the layout
  is the point.
- **Speaker notes moved into the deck markup** — the supporting evidence turned out
  to be a misread attribute.
- **A runtime that computes figures from a declared source** — fails on the very
  slide it was invented for. Only a build-time checker survives.
- **Business Model Canvas as a component** — nine unequal cells is a worksheet, not
  a finding, and does not fit 1280x720 at legible type.
- **More themes and a light/dark toggle** — multiplies the design surface without
  serving any moment in a team's week.
