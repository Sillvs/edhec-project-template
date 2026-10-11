# Frameworks, and what to build them from

A consulting framework is a way of *thinking*. A slide is a way of *showing*.
They are not the same thing, and most weak decks are a framework copied onto a
slide instead of a finding shown on one.

This page maps the frameworks you will actually be asked for to the components
that carry them, and says what each one looks like when it goes wrong.

Jump to: [Pyramid](#the-pyramid) · [MECE](#mece-and-the-issue-tree) ·
[Market sizing](#market-sizing) · [Porter](#porters-five-forces) ·
[Value chain](#the-value-chain) · [Business case](#the-business-case) ·
[Prioritisation](#prioritisation) · [Competitive position](#competitive-position) ·
[Roadmap](#the-roadmap)

---

## The pyramid

**Answer first, then the support, then the detail.** The single highest-leverage
habit in the whole list, and the one students skip.

| Build it from | Where |
|---|---|
| `.exec` | gallery A1 |
| `.action` titles on every slide | the slide frame |
| `paper/onepager.html` | the leave-behind version |

The action title is the pyramid in miniature. "Cost structure" is a label.
"Cost per engagement rose 23 per cent while price held" is the answer. If your
titles read as labels, the deck has no pyramid, whatever the first slide says.

**Goes wrong as:** a summary slide that summarises the *agenda* rather than the
*findings*. If your executive summary could have been written before the
analysis, it is a contents page.

---

## MECE and the issue tree

**Mutually exclusive, collectively exhaustive.** Split the question into parts
that do not overlap and leave nothing out.

| Build it from | Where |
|---|---|
| `.tree` | gallery A2 |
| `.chain` for a linear decomposition | gallery, slide frame |

Outline the branch your evidence supports, so the audience knows where the next
slide goes.

**Goes wrong as:** three branches that are really one branch and two examples of
it. Test each split by asking whether a finding could land in two boxes. If it
can, the split is not exclusive, and the tree is decoration.

---

## Market sizing

**Top-down, bottom-up, or both meeting in the middle.** You will be asked to
defend every step, not the total.

| Build it from | Where |
|---|---|
| `.ladder` | gallery C4 |
| `.funnel` when the steps are a filter rather than a multiplication | gallery C2 |
| `.mekko` when the finding is "big share of a small market" | gallery C3 |

The ladder exists because a funnel hides the arithmetic. Each rung shows its own
multiplier and its own reason, which is what a jury attacks.

**Goes wrong as:** a number with no visible derivation, or a derivation where one
step is a guess dressed as a percentage. Name the guess. "Share we can win in
three years, assumed" survives a question. A bare `x 0.11` does not.

---

## Porter's five forces

**Five pressures on an industry's profitability.** Useful for structuring the
research. Almost never useful as a slide in its own shape.

| Build it from | Where |
|---|---|
| `table.dark` with a verdict column, one row per force | gallery C1 |
| `.tor` when you can rank the forces by how much they move the answer | gallery C3 |

**Goes wrong as:** the five-box diagram with a paragraph in each box. Nobody
reads it, it says nothing about *this* industry that the template did not already
say, and it costs a whole slide. If three of the five forces are not binding,
show the two that are, and say why the others are not.

---

## The value chain

**Where the margin actually sits along the activity.** A diagnosis tool, not a
picture.

| Build it from | Where |
|---|---|
| `.chain` for the steps | slide frame |
| `.pflow` when layers sit underneath each step | slide frame |
| `.fall` for where margin is gained and lost along it | gallery C1 |

The waterfall is the under-used one here. A value chain that shows *where margin
leaks* is an argument; a value chain that shows *that activities exist* is a
diagram.

**Goes wrong as:** every box the same size and the same colour, which says every
step matters equally. They never do.

---

## The business case

**What it costs, what it returns, when, and what could stop it.**

| Build it from | Where |
|---|---|
| `.tiles` for the three numbers that decide | slide frame |
| `.bars` for the cost split | slide frame |
| `.fall` for the bridge from today's number to the proposed one | gallery C1 |
| `.trend` with a dashed forecast segment | gallery C2 |
| `.tor` for sensitivity | gallery C3 |

**The forecast line must be dashed.** A solid line into the future claims a
precision you do not have, and somebody will hold you to it.

**Goes wrong as:** a single scenario. One number is a guess with a decimal point.
A tornado turns the guess into a range and tells the room which assumption to
argue about, which is a far stronger position than defending a point estimate.

---

## Prioritisation

**What to do first.** The 2x2 is the default and is usually right.

| Build it from | Where |
|---|---|
| `.quad` | gallery C2 |
| `.sgrid` for scenarios against layers | slide frame |
| `table.dark` with a `better fit` column when the criteria are not two | gallery C1 |

Put the axis labels where they read without turning your head: y above the axis,
left aligned, x below and centred. **Do not rotate the y label.** It survives the
PDF and arrives flat in the PowerPoint, and the rotated version is the single
most common reason a copied 2x2 looks broken in `.pptx`.

**Goes wrong as:** bubbles placed to produce a tidy diagonal. If everything lands
on the diagonal, the two axes are measuring the same thing and you have a list.

---

## Competitive position

**Where you sit, and on what.**

| Build it from | Where |
|---|---|
| `.dotplot` | gallery C4 |
| `.carto` for position by country | gallery C2 |
| `table.dark` for a feature or capability comparison | gallery C1 |

The dot plot shows the **spread**. A bar chart of averages destroys the spread,
and the spread is usually the finding: being at the median of a tight field and
the median of a scattered one are different situations with different answers.

**Goes wrong as:** a comparison table where your client wins every row. Nobody
believes it, and one honest weakness buys credibility for the other four rows.

---

## The roadmap

**What happens when, and what waits on what.**

| Build it from | Where |
|---|---|
| `.gantt` with dependency connectors | gallery C4 |
| `.road` for phases without dependencies | slide frame |
| `.agenda` as the divider that tracks the plan | gallery A3 |

**The connectors are the argument.** Bars sitting next to each other say the
calendar decided. Connectors say the work decided, and that is a claim you can
defend.

**Goes wrong as:** a plan with no gate. A roadmap where nothing can stop is a
wish. Put a milestone where the decision actually is, and say what happens if it
fails.

---

## Two rules that outrank all of the above

**One finding per slide, in the title.** If you cannot write the action title,
you do not yet know what the slide is for. The components are there to make a
finding visible, not to fill a frame.

**Pick the chart that matches the claim, not the one that looks best.** A donut
for a share, columns for a comparison, a waterfall for a bridge, a dot plot for a
spread, a tornado for sensitivity. The nicest-looking chart that answers a
question nobody asked is still a wasted slide.

See **[COMPONENTS.md](COMPONENTS.md)** for what each component is and the rules
that keep a deck looking like one deck.
