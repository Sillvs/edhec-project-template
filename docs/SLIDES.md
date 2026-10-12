# Slide craft

`docs/COMPONENTS.md` says what exists. `docs/FRAMEWORKS.md` says which shape to
build. This page is about whether the slide **says anything**: one finding, in
one line, with room to breathe.

Most of it is numbers, because this repository can check numbers. Everything in
the first half is measurable at 1280×720, and most of it is a few lines on top
of the geometry `./build.sh` already reads out of Chrome.

---

## How to read the attributions

Slide advice is full of rules attributed to firms that never published them. The
labels below are used throughout, and the [Sources](#sources) table at the
bottom lists every URL with what it actually says.

| Tag | Means |
|---|---|
| **[primary]** | the named author or firm published this; the link goes to their document |
| **[practitioner]** | a named ex-consultant wrote it down; it is **not** a firm document |
| **[measured]** | measured in this repository, in the renderer `build.sh` uses |
| **[convention]** | craft convention with no source found. Said so rather than invented one |

Three things this page deliberately does **not** claim:

- **No source recommends a one-line headline.** Every documented source says one
  or two lines. One line is this repository's house rule, and
  [§1](#1-one-line-for-the-headline) says why.
- **"Action title" has no documented origin at BCG or anywhere else.** The
  "coined at BCG in the 1990s" story appears on template-vendor blogs with no
  citation. Treat it as folklore.
- **The 6×6 rule has no empirical basis we could find.** Vendor pages invoke
  Miller and Mayer; none cites a study of 6×6 itself. Use the numbers below,
  which have sources or measurements.

---

# Part 1 — The three rules the build can enforce

## 1. One line for the headline

**The geometry.** `.action` is 26px at weight 700, line-height 1.22, so one line
is **31.7px** tall and renders as a 32px box. The branding block narrows it to
`max-width:980px`, because the logo sits at the top right. The headline box is
therefore **980 × 32px at x=64, y=84** on every content slide. **[measured]**

**What fits.** Measured in the Chromium `build.sh` prints with, where the font
stack resolves to Liberation Sans (Arial metrics): **[measured]**

| | One line |
|---|---|
| Characters of mixed English prose | up to **74**; 78 wraps |
| Words | **12 to 14** |
| Safe drafting limit | **70 characters, or 12 words** |

> **Author on a Mac, wrap in CI.** Real Helvetica Neue Bold is narrower: the same
> box takes about 83 characters. A 78-character headline looks fine on a MacBook
> and arrives as two lines in the PDF. This is why the gate is the **rendered
> line count**, not a character count. Draft to 70 and stop guessing.

**Why one line here and not the documented two.** Alley's assertion-evidence
checklist says "no more than two lines" **[primary]**; Doumont's slide checklist
says "no more than 12 words or so, well-balanced on up to two lines"
**[primary]**; Slideworks, written by an ex-McKinsey and an ex-BCG founder, says
"Ideally, they should fit within one or max two lines, up to 15 words… NEVER have
a title that is longer than two lines" **[practitioner]**. Nobody says one.

One line is stricter for two reasons, one cosmetic and one real:

- The body band runs from the headline's bottom edge (y=116) to the content floor
  (y=656): **540px**. A second headline line takes 32px of it, about 6%.
- The usual reason a headline needs two lines is that it is carrying **two
  findings**. The cap catches that at drafting time, which is the only time it is
  cheap to fix.

**When it does not fit, split the slide.** Do not reduce the font: "The wrong way
to handle this is to shrink the title font size. The right way is to either
divide that one slide into several slides with their own key takeaways, or to
delete the data and information on the slide that is not contributing to the key
takeaway." **[practitioner]**

**Checkable.** `tools/extract_layout.mjs` already records a true rendered
`lines` count per text box, from client rects. Add `cls` to the text item (the
`svg` branch already captures it) and the check is three lines:

```
HEADLINE  slide 7: the action title renders on 2 lines. Cut it to one, or split
          the slide. Shrinking the font is not the fix.
```

Worth checking alongside it: exactly one `.action` per content slide, and every
`.action` run at exactly 26px, which catches the shrink-to-fit cheat.

**Known deviation.** Six of the twelve content headlines in
`examples/auditcert-france-2026/` run to two lines. Two of those six join two
claims with a semicolon, which is the tell. The example predates this rule and
has not been re-cut; it is not evidence that two lines are fine. **[measured]**

**Goes wrong as:** a three-line headline that pushes the exhibit down, which the
author then fixes by dropping the body to 10px — breaking the type floor and the
contrast budget in one move.

---

## 2. Clean spacing, in pixels

A 16:9 PowerPoint slide is 13.333 × 7.5in. At 1280 × 720 that is exactly
**96 px/in**, so 1px = 0.75pt and **half an inch = 48px**. Every number below
comes from that conversion or from the rendered deck.

| Band | Value | Where it comes from |
|---|---|---|
| Side margins | **64px** (5% of width) | `.pad` padding, measured on every content slide |
| Top of content | **y=44** | `.pad` padding |
| Content floor | **y=656** | `.pad` bottom padding, ~22px of air above the footer rule |
| Headline box | **x=64, y=84, w=980, h=32** | measured |
| Gap below the headline | **≥48px** | Alley: "leave at least a half-inch of white space below the headline" **[primary]** |

**The gap below the headline is the one that slips.** `.action` carries only a
22px bottom margin; `.grow` centres the body in what is left, so the real gap
varies. Measured on the starter deck: **55, 119, 102 and 30px**. The roadmap
slide at 30px misses the half-inch and reads as though the headline were a
caption on the plan. **[measured]**

**Group spacing is a ratio, not a value.** Kosslyn: "Comprehension is impaired by
spurious groups, which form accidentally because of the grouping laws", and
"Labels initially are seen as applying to the closest graphic element."
**[primary]** So uniform spacing is a bug. Keep the gap **between** groups at
least 1.5× the gap **inside** a group, and never leave a label equidistant
between the thing it describes and the thing it does not.

**Checkable.** Gap below the headline: topmost body `rect` minus headline bottom,
warn under 48px. Safe area: every content box inside x 64–1216 and y 44–656.
Group ratio: for each sibling set, max intra-group gap against min inter-group
gap. All three are bounding-box arithmetic on the existing JSON.

Overflow past 1280×720 and anything crossing the footer rule are **already
enforced** by `tools/check_slides.py`. Clean spacing is the part that passes
those gates and still looks cramped.

**Goes wrong as:** a slide where headline and chart touch, so the claim reads as
a chart caption, and the eye never separates assertion from evidence.

---

## 3. Nothing overloaded: the budgets

### Words

The research baseline is a lecture slide, not a consulting exhibit, and the gap
matters:

| Measured | Words per slide |
|---|---|
| Common-practice engineering slides (Garner & Alley, n=110) | **41.5** **[primary]** |
| Their assertion-evidence version of the same talk | **21.2** **[primary]** |
| Alley's later assertion-evidence set | **19.3** **[primary]** |
| This repository's starter deck, every visible word | **97** **[measured]** |
| `examples/auditcert-france-2026/`, every visible word | **160** **[measured]** |

A raw word count on this template is meaningless: most of those "words" are table
cells, axis ticks, verdict chips and gate labels. Count **prose** — running text
at 15.5–19px in boxes of five words or more:

| Measured | Prose words per slide |
|---|---|
| Starter deck | mean **13** **[measured]** |
| Worked example | mean **33**, max **92** **[measured]** |

**The budget for this template.** Headline ≤ 12 words. Prose ≤ 40 words on an
exhibit slide, ≤ 25 on a slide whose evidence is a chart. Calibrated to the
measured range above, not to Alley's lecture slides. **[convention]**

**Price it in seconds.** Adult silent reading of English non-fiction averages
**238 wpm** across 190 studies and 18,573 participants **[primary]**. Forty words
is ten seconds of a room reading instead of listening, and you will spend them on
your own transition.

### Lists

Kosslyn: "we can hold in working memory only about four such units", and in his
survey of real decks **91.4%** broke the four-item limit, and the same share put
more than two lines in an item **[primary]**. Alley: "Keep lists to two, three,
or four items" **[primary]**.

**Four items per group, one line per item.** A fifth item means the grouping is
wrong, the slide is two slides, or the list is really a chart.

> **Known deviation.** `.pts` renders two columns, and the worked example runs
> **ten** bullets on slides 3 and 7. That is over the cap however you count the
> columns. Named here rather than quietly excepted. **[measured]**

`docs/COMPONENTS.md` already caps the components that carry lists — three or four
tiles, four chain steps, six or seven table rows. Those caps and this one are the
same rule seen from different ends.

### One claim, one exhibit

think-cell: "each slide should have just one message supported by one action
title" **[practitioner]** — think-cell is the charting add-in the firms use, not
a firm. Doumont: "Does the slide make (reasonable) sense on its own? Can the
audience get the point just by looking at it?" **[primary]**

Two mechanical tells that a slide is carrying two claims: an `and` joining a
second finite verb in the headline, and a semicolon. Both appear in the worked
example. Splitting the clause is usually how a two-line headline becomes one.

**Checkable.** Prose-word budget per slide, conditional on whether the slide
holds a chart. List length per sibling group. One `.action` and one chart root
per slide. Reader-seconds printed next to the pass line, so the author sees
`slide 7: 46 prose words, 11.6 reader-seconds` and does the arithmetic once.

**Goes wrong as:** a seven-bullet slide that fits the canvas, clears AA and the
type floor, and communicates nothing.

---

# Part 2 — Writing the headline

## State the finding, not the topic

The template already says it: "`Why invest in AI and why do it now?` is a topic.
`Cloud wins five of six criteria` is a finding." The support:

- **Evidence, not taste.** Alley, Schreiber, Ramsdell and Muffo changed phrase
  headlines to sentence headlines in four sections of the same course, around 200
  students each. On the questions whose answers sat in the headline, scores went
  from **46% to 63%**, significant at p<.005. On questions whose answers sat in
  the body in both versions, the scores were the same. **The promotion to the
  headline is the mechanism** — a better body did not help. **[primary]**
- MIT's EECS Communication Lab: "Strong titles tend to be full sentences, since
  you need a full sentence to tell a message. Weak titles tend to be nouns like
  'Background'." **[primary]**
- Doumont's checklist: "Does the title convey the message (the so what)? Is it a
  complete sentence, with a subject and a verb?" **[primary]**

## Five headline shapes to reject

| Shape | Example | Fix |
|---|---|---|
| **Topic label** | `Cost structure` | the conclusion the slide proves |
| **X by Y** | `Revenue by region` | what the breakdown shows |
| **Intellectual blank** | `The company faces three problems` | what the three have in common. Minto's term, and her example **[primary, secondary copy]** |
| **The activity, not the finding** | `We interviewed 13 customers` | `Customers take three times longer to onboard than with competitors` **[practitioner]** |
| **The axis label, promoted** | `Three-year TCO, € thousand` | that belongs in the subhead, not the headline |

The intellectual blank is also a thinking check: a group you cannot summarise is
a group you have not finished thinking about.

## Assertion on top, units underneath

The headline should not have to absorb scope, units and date — that is what
balloons it past one line. Split the two jobs:

```html
<div class="action">Most AI roadblocks involve people, not models</div>
<div class="small">Key challenges named by respondents (%), n = 1,250</div>
```

That two-part structure is visible in BCG's published 2025 AI report: Exhibit 10
reads "Most AI Roadblocks Involve People, Organization, and Processes", with
"Key challenges named by respondents (%)" set small beneath it. **[primary]**

The template has no dedicated subhead slot, which is why the units keep ending up
in the headline. Use what is there: `.action` for the claim, a `.small` line
under it or the `.qtag` legend on the block for scope and units, and `.srcline`
at the foot for provenance. A `.small` line is 15.5px and takes about 22px of the
body band against the 32px a second headline line takes — and it reads as scope
rather than as part of the claim, which is the point.

## Case and full stops: pick one, then check it

There is no cross-firm standard, and anyone who tells you there is has not
looked. BCG's published report uses **Title Case with no full stop**
**[primary]**. Michael Alley's example headline is sentence case with no full
stop **[primary]**. Consultants Mind puts it correctly: "If you have a period (.)
at the end of the title, do that for all of them." **[practitioner]**

**House choice: sentence case, no full stop.** Sentence case is narrower, which
matters in a 980px box, and it reads as a sentence rather than a label.

**Checkable, and trivially.** Count headlines ending in `.` — the answer must be
0 or all of them. Classify each headline as sentence or title case and fail if
the deck contains both. A small per-project allowlist handles acronyms and proper
nouns.

## Every number in the headline appears in the body

"There should be nothing in the action title that's not in the slide body, and
nothing in the slide body that is irrelevant to the action title."
**[practitioner]**

The first half is the most valuable cheap check on this list: extract every
numeric token from the headline — percentages, currency, multiples, years — and
fail if it is absent from that slide's other text. A headline claiming 18% over a
chart from which 18% cannot be read is the error that reads as fabrication rather
than sloppiness.

**Goes wrong as:** headlines that are captions. The deck is factually correct and
decision-free, and the room asks "and therefore?" after every slide.

---

# Part 3 — The argument across slides

## One governing thought

Barbara Minto, on her own site: "Your thinking will be easy for a reader to grasp
if you present the ideas organized as a pyramid under a single point."
**[primary]** Write that single sentence before building anything. Every headline
is then a reason for it or a consequence of it, and a slide that supports nothing
above it is deleted rather than demoted.

Her three rules for the structure: ideas at any level summarise the ideas grouped
below them; ideas in a grouping are the same kind of idea; ideas in a grouping are
logically ordered. **[primary, via a secondary summary]** On a slide, rule one is
the headline test and rules two and three are the list test — same kind of thing,
in a deliberate order.

**MECE** is hers too: coined at McKinsey in the late 1960s, and in her McKinsey
interview she traces the underlying logic to Aristotle and claims only the
abbreviation. **[primary]** Build it with `.tree`; `docs/FRAMEWORKS.md` has the
failure modes.

**Situation, Complication, Question** is also documented on her site, as the
"SCQ Framework™", for finding the question in the reader's mind. **[primary]**
One setup slide, then the answer, then the support.

> **What Minto did not write.** Her site never mentions slides or slide titles.
> "Horizontal flow", "action title" and "the titles are the argument" are
> consultant usage reported by ex-MBB authors. Useful, widely taught, and not
> Minto. **[practitioner]**

## Read the headlines alone

"Your audience should be able to read only your action titles all the way through
the presentation and a) understand what the main conclusions are and b)
understand how you got to those main conclusions." **[practitioner]** The same
test, in an academic setting: "The audience should be able to follow your story
just by reading the slide titles." **[primary]**

**Checkable as an artefact, which is what makes it actually happen.** Have the
build emit `headlines.txt` — slide number and headline, in deck order — and fail
on a missing headline or two identical ones. The read is human; printing the list
makes it free.

## Write the headlines first

"Best practice when crafting action titles is to write them as the first step of
creating a presentation." **[practitioner]** The stronger version of the same
habit is a flat outline: one line per slide for the claim, indented lines under
it for the evidence that proves it. A claim with no evidence lines is cut; a
claim with nine is two slides. Consultants call this a dot-dash; the term appears
on practitioner blogs rather than in anything a firm published. **[convention]**

If you keep that outline as a file, `build.sh` can assert that every rendered
headline matches its line in the outline, which turns a planning document into a
maintained one.

**Goes wrong as:** thirty finished slides defending a story nobody agreed to.
Feedback arrives as "this whole section should go", and a week of chart work is
thrown away.

---

# Part 4 — Charts that carry the claim

`docs/COMPONENTS.md` lists the thirteen charts and what each is for.
`docs/FRAMEWORKS.md` maps frameworks to components. Four craft rules on top.

**Write the sentence before choosing the chart.** Zelazny, *Say It With Charts*:
"It depends entirely on *what your message is* in terms of how you want the data
plotted." **[primary]** His five comparisons — component, item, time series,
frequency distribution, correlation — come from the sentence, not from the shape
of the data. Trigger words give it away: *share of* → component, *larger than* →
item, *grew* → time series, *increases with* → correlation. For anything outside
those five, the FT's Visual Vocabulary is the maintained superset, with nine
families: deviation, correlation, ranking, distribution, change over time,
part-to-whole, magnitude, spatial, flow. **[primary]**

**Label the series on the chart and delete the legend.** The EU's data
visualisation guide: "Separate legends create unnecessary cognitive load for the
chart reader: they require readers to look back and forth between the chart and
the legend", and the fix is "direct labelling: integrating the names of elements
and categories in the chart". **[primary]** It is also the spatial-contiguity
effect, d=0.48 **[primary]**. Where direct labels crowd, cut series or highlight
one and grey the rest before reaching for a legend.

**Mute the scaffolding, and state the units.** The same guide: numerical and date
axes should have "at least 2 labels and up to 8 at most. More than 8 labels will
create busy axes", and gridlines "especially need to be muted" — grey, thin,
optionally dashed. **[primary]** Units go on the axis or in the subhead, once,
unambiguously. A number without a unit is not a finding.

> **Do not "fix" a faint gridline by darkening it.** `check_slides.py` measures
> **text runs** against the colour painted behind them. Gridlines are not text
> and are not in scope. AA is a floor for things people read, not an instruction
> to make the furniture loud.

**Erase ink that encodes nothing.** Tufte's list: "Above all else show the data.
Maximize the data-ink ratio. Erase non-data-ink. Erase redundant data-ink."
**[primary]** Concretely: no chart border, no plot-area fill, no 3D, no shadows
or gradients on bars, no value label on every point, no number printed twice.
Doumont's version is one question: "Did you omit whatever adds little
(background, logo, decoration)?" **[primary]** Cole Nussbaumer, on labels:
"Labeling every data point creates a cluttered visual." **[practitioner]** Label
the two or three values the headline depends on.

> **The honest limit.** Strict data-ink maximisation is contested, not settled:
> "Chartjunk is a popular yet contentious topic. Previous studies have shown that
> extreme minimalism is not always best, and that visual embellishments can be
> useful depending on the context." **[primary]** The defensible rule is
> purpose-driven rather than minimum-driven: every mark must encode data, aid
> decoding, or direct attention. Decoration that does none of the three goes.

**Checkable.** `box-shadow`, `text-shadow` and gradients on data marks; a
non-transparent plot-area background; data stroke thinner than the gridline
stroke; tick-label count outside 2–8; a `.legend` element where the series count
is five or fewer; a value label on every point where there are more than eight.
All readable from computed styles in the pass that already runs.

**Goes wrong as:** a five-series line chart with a legend in the corner. The room
spends the slide doing lookup while the speaker talks over the top of it.

---

# Part 5 — The slide and the spoken track

**Do not put your spoken sentences on a slide that also carries a graphic.**
Mayer and Moreno's effect-size table, from their own experiments: **[primary]**

| Move | Effect | d (experiments) |
|---|---|---|
| Say it instead of printing it, when a graphic is present | modality | **1.17** (6) |
| Break one long thing into learner-paced segments | segmentation | **1.36** (1) |
| Cut interesting but irrelevant material | coherence | **0.90** (5) |
| Remove on-screen text that duplicates the narration | redundancy | **0.69** (3) |
| Put labels next to what they label | spatial contiguity | **0.48** (1) |

**The nuance most slide advice omits.** The redundancy penalty only applies when
something is competing for the eyes: "When no animation is presented, students
learn better from a presentation of concurrent narration and on-screen text (i.e.
verbal redundancy) than from a narration-only presentation." **[primary]** So the
word budget should be tiered, not flat — a chart slide wants a near-empty text
layer; a statement slide can carry its sentence. That is why [§3](#words) sets
25 words on chart slides and 40 elsewhere.

**Checkable, and this repo has the files for it.** The worked example ships
`speaker-notes.html`, and its README already claims "Speaker notes that do not
repeat the slides." Tokenise both, compare shingles, and fail a slide whose body
text is more than ~60% contained in its own notes. That is a mechanical test for
"the slide is the script".

**The counterweight: more slides, not a longer monologue.** The modality
advantage holds for short spoken explanations and reverses for long ones, because
speech is transient — to make sense of a later sentence the listener has to hold
an earlier one. Leahy & Sweller, *Applied Cognitive Psychology* 25 (2011),
943–951. **Verified through secondary summaries only** — the publisher refused
the fetch. Treat the direction as sound and the numbers as unchecked.

**Goes wrong as:** a clean three-word slide held on screen through four minutes
of unsegmented narration. The slide is blameless and the room is lost anyway.

---

# Part 6 — What this style costs

A document that only sells the method is weaker. Six real costs.

## An assertive headline can be confidently wrong

The NASA Debris Assessment slide was headlined "Review of Test Data Indicates
Conservatism for Tile Penetration". Six levels of bullets down, the engineers
noted that the debris estimate "was 640 times larger than the data used to
calibrate the model". Tufte's reading was that the honest headline would have
been "Review of Test Data Indicates Irrelevance of Two Models", and the Columbia
Accident Investigation Board concluded that it "views the endemic use of
PowerPoint briefing slides instead of technical papers as an illustration of the
problematic methods of technical communication at NASA." **[primary]**

The one-line action title is a format that makes a claim sound settled. So:
**if the finding is a limitation, the limitation is the headline.** The rule that
every number in the headline must appear in the body is the mechanical half of
this; the other half is human review of claim against evidence.

## Minimal slides measurably cost detail recall

In Garner and Alley's own comparison, the topic-subtopic audience recalled
**69%** of secondary statistics against the assertion-evidence audience's
**39%** — for the plain reason that those numbers were printed on their slides.
Primary statistics, written on both versions, scored **87% and 87%**.
**[primary]**

The minimal style wins on understanding and loses on magnitudes. If a figure must
be remembered exactly, write it down somewhere: `paper/onepager.html` is the
leave-behind, and an appendix slide costs nothing. Saying it is not enough.

## The type floor is a backstop, not a readability target

| | px here | pt in the export |
|---|---|---|
| `.action` headline | 26 | **19.5** |
| Body text | 19 | 14.25 |
| `.small` | 15.5 | 11.6 |
| Floor | 11.5 | 8.6 |

Kosslyn's survey counts text under **20pt** as a violation and found 66% of real
decks breaking it **[primary]**. Alley's tested design is 28pt headline, 18–24pt
body, 12–14pt for references — **37px over 24–32px** on this canvas
**[primary]**. Kawasaki's floor is 30pt, i.e. 40px **[practitioner]**.

By those numbers this template's whole scale is small, and the headline is just
under the 20pt line. That is a density trade-off: a consulting exhibit carries
more objects than a lecture slide. Two consequences worth stating plainly:

- **11.5px passing the gate does not mean readable.** It is 8.6pt. Reserve 11.5px
  and 13px for footers, sources and provenance — never for a finding.
- **The fix for a slide that does not fit is not smaller type.** Kawasaki's two
  reasons people shrink fonts are that they do not know the material well enough
  and that they think more text is more convincing **[practitioner]**. Cut
  content or split the slide. An error message that says "reduce size" teaches
  the wrong lesson, which is why the overflow failure in `check_slides.py` says
  what it says.

## Answer-first invites confirmation bias

Writing the answer early is good practice and a known trap: "when trying to solve
a problem, both individuals and groups are prone to generating one plausible
hypothesis and then seeking only evidence that supports it." The suggested
countermeasure is structural — "What alternatives did you consider? At what stage
were they discarded?" Kahneman, Lovallo and Sibony, HBR, June 2011. **[primary]**

Carry an alternatives slide, in the deck or the appendix, with at least two
rejected options and the reason each was dropped. In this template that is
`table.dark` with a verdict column, or the off-ramp pattern the worked example
uses for cloud versus on-premise.

## Deciding what to leave out is an exercise of power

The same discipline that makes a deck clear lets an author simplify past
usefulness and quietly drop the inconvenient interview, the contradicting case,
or a teammate's analysis. **[convention]** Keep a cut list beside the deck: one
line per removed finding, with the reason. It turns a silent deletion into a
reviewable one, and it is the thing a jury's hardest question is usually about.

## Some problems are not slide-shaped

A clean deck can make an unresolved problem look resolved. Carry one slide that
states what the analysis cannot settle, and hand over prose — a memo, a written
appendix, `paper/paper.html` — where the reasoning does not survive compression.

**And apply the rest as a method, not a liturgy.** `AGENTS.md` already has the
right posture: a gate that fails is information, not an obstacle. The honest
implementation of everything above is two severities — hard failures for
geometry, contrast and the type floor, warnings for judgement calls that an
author may override **with the reason recorded in the markup**. A suppressed
warning is noise; a warning with a stated reason is a decision.

---

# The checklist

| Rule | The number at 1280×720 | Status |
|---|---|---|
| Nothing overflows the canvas | 1280 × 720 | **enforced** |
| Nothing runs under the footer | content floor y=656 | **enforced** |
| Every text run clears WCAG AA | 4.5:1, 3:1 for large | **enforced** |
| No text below the floor | 11.5px | **enforced** |
| One headline per content slide | exactly one `.action` | needs `cls` in the extractor |
| Headline on one line | rendered `lines == 1`; draft to 70 chars / 12 words | needs `cls`; `lines` already extracted |
| Headline not shrunk to fit | every `.action` run at 26px | needs `cls` |
| Headline is a claim, not a label | finite verb present; label stoplist | lint, warn |
| Headline case and full stops consistent | 0 or all | string check |
| Numbers in the headline appear in the body | every numeric token | string check |
| Clear space below the headline | ≥48px measured | bounding boxes |
| Group spacing | between-group gap ≥1.5× within-group | bounding boxes |
| Safe area | x 64–1216, y 44–656 | bounding boxes |
| List length | ≤4 items per group, 1 line each | needs `cls` |
| Prose words | ≤25 on a chart slide, ≤40 otherwise | needs `cls` |
| One exhibit per slide | one chart root | needs `cls` |
| Axis labels | 2 to 8 | needs `cls` |
| Slide is not the script | <60% shingle overlap with its speaker notes | needs notes parsing |
| Headlines read as the argument | `headlines.txt` artefact; no duplicates | artefact, human read |

Everything in the right-hand column that is not yet enforced is bounding-box
arithmetic or a string match over `.build/*.json`, plus one field — `cls` on text
items in `tools/extract_layout.mjs`, which the `svg` branch already captures.

---

## Sources

Where a link is a secondary copy or summary, it says so.

**How far this was verified.** An adversarial fact-check of all 81 attributed
claims was planned and **did not run**: every verifier hit a session limit. Four
primary sources were then re-fetched and checked by hand, and all four matched
verbatim:

| Source | Checked |
|---|---|
| Alley, *Checklist* | "no more than two lines" · "at least a half-inch of white space below the headline" · "lists to two, three, or four items" · "28 point type for the headline, 18–24 point type for the body" · "no more than 20 words per minute" |
| Doumont, *Checklist for slides* | "no more than 12 words or so, well-balanced on up to two lines, surrounded by sufficient space" · "Is it a complete sentence, with a subject and a verb?" |
| Garner & Alley (2013) | "the mean number of words per slide for the common-practice version was 41.5" · "for this condition was 21.2" · 19.3, d=0.89, 3.61 and 3.01 all present |
| Kosslyn et al. (2012) | "Comprehension is impaired by spurious groups…" · "Labels initially are seen as applying to the closest graphic element." · "only about four such units" |

The remaining sources in this table are **not** hand-checked. Treat a quote you
intend to repeat in front of an examiner as unverified until you open the link.
That caveat is the point of the attribution tags: a rule can be good and its
famous name still wrong.

**Documented, primary**

| Source | What it is | Evidence for |
|---|---|---|
| [Alley, *Checklist for Assertion–Evidence Slides*](http://www.writing.engr.psu.edu/AE_checklist.pdf) | Penn State, from *The Craft of Scientific Presentations* (2013) | two-line headline max, half-inch below the headline, lists of 2–4, 20 words/minute, 28/18–24/12–14pt |
| [Alley, Schreiber, Ramsdell & Muffo (2006)](https://www.writing.engr.psu.edu/ae_headlines.pdf) | *Technical Communication* 53(2) | 46% → 63% recall, p<.005, and the null for body-only questions |
| [Garner & Alley (2013)](https://writing.engr.psu.edu/ae_comprehension.pdf) | *Int. J. Engineering Education* 29(6), 1564–1579 | 41.5 vs 21.2 words/slide; d=0.89 delayed transfer; mental effort 3.61 vs 3.01 |
| [Garner & Alley (2011)](https://peer.asee.org/assertion-evidence-slides-appear-to-lead-to-better-comprehension-and-recall-of-more-complex-concepts.pdf) | ASEE AC 2011-900 | secondary statistics 69% vs 39%, p<0.000; primary 87% vs 87%; 19.3 words/slide |
| [Kosslyn, Kievit, Russell & Shephard (2012)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3398435/) | *Frontiers in Psychology* 3:230 | ~4 units in working memory; 20pt and 4-item violation rates; spurious groups; labels attach to the nearest element |
| [Mayer & Moreno (2003)](https://www.uky.edu/~gmswan3/544/9_ways_to_reduce_CL.pdf) | *Educational Psychologist* 38(1), 43–52 | modality 1.17, segmentation 1.36, coherence 0.90, redundancy 0.69, contiguity 0.48; the no-animation exception |
| [Doumont, *Checklist for slides*](https://principiae.be/pdfs/TM&Th-3.3-checklist.pdf) | from *Trees, maps, and theorems* | title conveys the message, complete sentence, ≤12 words on up to two lines, surrounded by space, omit decoration |
| [Minto](https://www.barbaraminto.com/) | her own site | the single point; SCQ Framework™. Note: no mention of slides |
| [MECE](https://en.wikipedia.org/wiki/MECE_principle) | encyclopaedia, citing her McKinsey interview | coined at McKinsey in the late 1960s; traced back to Aristotle |
| [CAIB report, quoted in Alley's teaching exercises](http://writing.engr.psu.edu/teaching_slide_design/exercises.pdf) | Columbia Accident Investigation Board, Vol. 1 | the Debris Assessment slide, the 640-fold detail, Tufte's alternative headline |
| [Kahneman, Lovallo & Sibony (2011)](https://faculty.washington.edu/pathaksd/BBUS549/Required%20Readings/Before%20You%20Make%20that%20Big%20Decision.pdf) | *HBR*, June 2011, reprint R1106B | one plausible hypothesis; the alternatives questions |
| [Brysbaert (2019)](https://gwern.net/doc/psychology/linguistics/2019-brysbaert.pdf) | *J. Memory and Language* 109 (2019) 104047 | 238 wpm non-fiction, 183 wpm oral; 190 studies, 18,573 participants |
| [EU data visualisation guide](https://data.europa.eu/apps/data-visualisation-guide/axes-grids-and-legends) | Publications Office of the EU | legends and cognitive load, direct labelling, 2–8 axis labels, muted gridlines |
| [EU guide, chart titles](https://data.europa.eu/apps/data-visualisation-guide/understandable-chart-titles) | same | generic versus communicative titles |
| [BCG, *The Widening AI Value Gap* (2025)](https://media-publications.bcg.com/The-Widening-AI-Value-Gap-Sept-2025.pdf) | BCG's own report | exhibit headline + unit subhead; Title Case, no full stop |
| [Tufte's principles, as taught](https://websites.umich.edu/~jpboyd/eng403_chap2_tuftegospel.pdf) | lecture notes quoting *The Visual Display of Quantitative Information* | show the data, maximise data-ink, erase non-data-ink and redundant data-ink |
| [Parsons & Shukla (2020)](https://arxiv.org/abs/2009.02634) | IEEE VIS short paper | chartjunk is contentious; extreme minimalism is not always best |
| [Zelazny, *Say It With Charts*](https://www.informit.com/articles/article.aspx?p=170392&seqNum=30) | excerpt | the message decides the plot; the five comparisons |
| [FT Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md) | Financial Times | the nine relationship families |
| [MIT EECS Communication Lab](https://mitcommlab.mit.edu/eecs/commkit/slideshow/) | MIT | full-sentence titles; follow the story from the titles alone |

**Practitioner, named, not a firm document**

| Source | Who | Evidence for |
|---|---|---|
| [Slideworks, how McKinsey consultants make presentations](https://slideworks.io/resources/how-mckinsey-consultants-make-presentations) | Mats Stigzelius, ex-McKinsey | action title and the so-what; read the titles alone; two lines or less and one font size; fixed title position; nothing in the title that is not in the body |
| [Slideworks, how to write action titles](https://slideworks.io/resources/how-to-write-action-titles-like-mckinsey) | with Alexandra Hazard Kampmann, ex-BCG | one or max two lines, up to 15 words; split rather than shrink; summary versus conclusion; write titles first |
| [think-cell](https://www.thinkcell.com/en/resources/content-hub/using-the-pyramid-principle-to-build-better-powerpoint-presentations) | the charting add-in vendor | one message per slide, one action title; outline from the titles |
| [Consultants Mind](https://www.consultantsmind.com/2020/04/14/consulting-tip-writing-good-titles/) | ex-consultant blog | be consistent about title length and full stops |
| [Kawasaki, 10/20/30](https://guykawasaki.com/the_102030_rule/) | venture capitalist | 30pt floor; the two reasons people shrink type |
| [Storytelling with Data](https://www.storytellingwithdata.com/blog/2012/06/drawing-attention-with-data-labels) | Cole Nussbaumer | labelling every point creates clutter |
| [Pyramid Principle summary](https://astimen.wordpress.com/wp-content/uploads/2012/03/the-pyramid-principle-by-barbara-minto.pdf) | a third-party summary of Minto's book, by ConsultingMethodology.com | the three pyramid rules; intellectual blanks; limit the introduction to what the listener accepts. **Secondary copy** — the book is the source |

**Could not source**

| Claim | Status |
|---|---|
| A one-line headline | No source found. House rule, measured here |
| "BCG coined 'action title' in the 1990s" | Uncited vendor blogs only. Folklore |
| The 6×6 rule | [No test of the rule found](https://slidemodel.com/6x6-rule-powerpoint/); pages invoke Miller and Mayer without citing one |
| "Horizontal flow" as Minto's term | Practitioner usage. Her site never mentions slides |
| Leahy & Sweller (2011), transient information | Publisher refused the fetch. Summaries only |
| 48px, and the px↔pt table | Derived from 1280px ÷ 13.333in = 96 px/in, not quoted |

---

## Read next

| | |
|---|---|
| **[COMPONENTS.md](COMPONENTS.md)** | what each component is, the type and spacing scale, the contrast rules |
| **[FRAMEWORKS.md](FRAMEWORKS.md)** | nine frameworks, what to build each from, and how each goes wrong |
| **[EXPORT.md](EXPORT.md)** | exporting, and the traps that silently break the output |
| **[PAPER.md](PAPER.md)** | the long-form version, for the reasoning that does not fit a slide |

---

## The copy filter

This page is about **structure**: what a slide claims and how much room the
claim gets. It says little about the words themselves, because that job belongs
to [antislop](https://github.com/miqdadbadjuber/anti-slop), which this
repository adopts as its filter and `AGENTS.md` wires in.

The two overlap on exactly one point, from opposite directions:

- This page says a headline must state a **finding**, so a slide carrying no
  finding has nowhere to hide.
- antislop says anything presented as fact is **real and verifiable or it is not
  shown**, so a finding that is invented has nowhere to hide either.

Together those close the loop. A deck can fail by saying nothing, or by saying
something it cannot support. Coursework is graded on both.
