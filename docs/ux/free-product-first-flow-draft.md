# Free product first flow — paper draft

| Field | Value |
| --- | --- |
| **Lane** | UX - Design & Research |
| **Source issue** | [expat-ledger-docs#28](https://github.com/alexandervivas/expat-ledger-docs/issues/28) |
| **Method** | Interface first, services after (walk decision 2026-08-28): the flow is defined on paper before any design tool or code. |
| **Status** | **Provisionally validated (2026-09-17).** Walked with 3 people, synthetic data, via a self-serve digital instrument rather than literal paper — see [Validation findings](#validation-findings-2026-09-16-17) below for what changed, what held, and what the owner explicitly left open. |
| **Feeds** | The owner's paper walk (issue #28); the real-spreadsheet design (issue #39, open questions still unanswered there); user-zero validation (issue #29) |

> **Synthetic data only.** Any example numbers below are invented for
> illustration. Walk participants enter synthetic figures only — see
> `docs/governance/evidence-archive.md` and issue #28's privacy note.

## What this flow qualifies

Per the 2026-08-28 walk decision (recorded in `docs/governance/pm-briefing.md`):
the free product is a distinct product from the paid ledger — new data model,
no statement import, no accounts. It qualifies a user on one question:

> No data in hand → hand-written income, debts, family obligation →
> **how much can I commit this month?**

The family-remittance obligation is first-class input, not folded into
generic debts, per the 2026-08-28 walk decision promoting it to a
first-class citizen of the data model (`docs/governance/pm-briefing.md`).
This is distinct from `docs/requirements/FR-006-remittance-linkage.md`,
which links a *paid-ledger* withdrawal to its matching cross-currency
deposit to prevent double-counting an existing account-to-account
transfer — a different mechanism, in the paid product, for a different
problem than this account-less free flow. The double-counting failure
mode named in
[Desk Research: Pain Points & Opportunities](desk-research-pain-points-opportunities.md#pain-points-ranked-strongest-signal-first)
motivates why this product cares about the distinction at all.

## Draft question sequence

One question per index card, asked in this order. Each card's answer feeds
the next; nothing is asked twice.

1. **Income this month.** "How much money will you have coming in this
   month, and in what currency?" — a single hand-written number per income
   source (salary, freelance, other), each tagged with its currency.
2. **Fixed debts and obligations, excluding family remittance.** "What do
   you already owe or have to pay this month, before anything else?" —
   rent, loan installments, subscriptions, anything recurring and
   non-negotiable, **except whatever you're about to enter on card 3** —
   family remittance is counted once, on its own card, never here. Without
   this exclusion a participant can enter the same commitment on both
   cards and the answer subtracts it twice, undermining the exact
   double-counting problem this product exists to solve.
3. **Family remittance obligation (first-class).** "How much do you send or
   commit to family each month, and what kind of obligation is it?" —
   asked as its own card, never merged into card 2, because it is a
   distinct commitment with its own currency. Record only a synthetic
   category (e.g. "regular support," "one-off help," "a specific debt") —
   never a real recipient's name, relationship, or country; the walk
   collects process descriptions, not identifying details about a
   participant's family.
4. **Safety margin (open question — see below).** Whether the flow asks for
   a desired buffer explicitly, or applies a fixed default, is undecided;
   the walk is how this gets decided, not a detail to settle beforehand
   (see walking instructions below).

## Draft answer

A single number, shown with its breakdown, never as a bare figure. Per the
2026-09-03 product decision (backend#320, Option A) and the no-mixed-
currency-totals rule (2026-08-26 decision; per-currency representation,
2026-09-03 decision 7), the committable amount is answered **in the
income currency**: any debt or family obligation held in a different
currency is converted at the participant's own recent effective rate and
labelled an estimate — amounts are never summed across currencies before
conversion.

If the result would be zero or negative, the answer is not a negative
number — it is **"$0 committable, and a shortfall of Y"**, so the flow
never tells a participant they can commit money they don't have.

```
Income:            [amount] [income currency]
Debts:             [amount] [income currency] (estimate, if converted)
Family obligation: [amount] [income currency] (estimate, if converted)
Buffer:            [amount or "none applied"]
─────────────────────────────────────────────
Committable:       X [income currency]
  — or, if X ≤ 0 —
$0 committable. Shortfall: Y [income currency]
```

Showing the breakdown, not just X, is deliberate: the desk research found
users spend hours a month untangling miscategorized manual entries — the
flow should let a participant see and correct which card produced a wrong
number, not just distrust a total.

## Open questions to resolve before walking

These mirror the open questions still unanswered on issue #39, since both
issues describe the same qualifying flow from different lanes. (Currency
combination is not on this list — it's decided; see Draft answer above.)

1. ~~Whether the safety-margin card is asked explicitly or defaulted, and if
   defaulted, what the default is and how it is disclosed.~~ **Resolved
   for now (2026-09-17):** all 3 walk participants landed on the
   fixed-default variant (10%, disclosed before the buffer is applied);
   the explicit-ask variant went untested by chance, not by decision — see
   [Validation findings](#validation-findings-2026-09-16-17).
2. Whether irregular or variable income (freelance, tips) is asked as a
   single figure or as a range.
3. The precise wording of "family obligation" in the language the
   participant will actually be interviewed in (the recruitment post,
   issue #38, is written in Spanish for the target population).

## Walking it with 2–3 people

1. Print or hand-write cards 1–3; nothing digital. For card 4, print
   **both variants** — one asking for a desired buffer, one applying a
   stated fixed default — and use one per participant, recording which.
   Resolving that open question is what this walk is for.
2. Ask the participant to fill each card as if it were their own month,
   using invented numbers and, on card 3, an invented category — never
   real income, debts, transfers, or a real family member's name,
   relationship, or country.
3. Do not explain a card before they attempt it; the friction of a
   misread or skipped card is the finding.
4. After all cards, show the derived answer and ask: "does this match what
   you'd expect to be told?" — record disagreement, not just agreement.
5. Capture, per participant: which card-4 variant they saw, where they
   hesitated, what they asked to clarify, and any card they wanted to
   answer differently than asked (e.g., wanting to give a range instead of
   one number).

## Validation findings (2026-09-16 / 17)

**Method actually used, and why it differs from the plan above.** The
walk ran as a self-serve digital instrument (a link the owner sent
directly to participants) rather than literal paper, because the goal
shifted to remote, unmoderated testing. This is a deliberate, disclosed
divergence from the "nothing digital" instruction above and from the
2026-08-28 method decision — logistics, not a reversal of "no design
tool": the instrument stayed deliberately plain (no branding, no
product-style polish) rather than becoming a Claude Design or
high-fidelity artifact. The instrument itself went through one
mid-walk revision: the first 2 of 3 responses used a version with
optional free-text reaction fields, and both skipped them entirely,
giving zero friction signal. The instrument was revised to tap-based,
required reactions (a Sí/No plus a reason, and a checklist naming which
card felt confusing, or "none") before the third response arrived.

**What held up, across all 3 participants:**

- The committable-amount arithmetic was correct in every response.
- Family remittance stayed separated from card 2's debts in every
  response — no observed recurrence of the double-counting this design
  exists to prevent.
- The one response that hit the zero/shortfall branch ("$0 committable,
  shortfall of Y") produced a genuine, informative reaction ("no estaba
  preparado jaja" — wasn't prepared for that) rather than confusion or
  distress, which is the evidence this branch's wording was built for.

**What stayed open, by owner decision rather than further testing:**

- **Card 4 variant coverage.** All 3 participants landed on the
  fixed-default variant by chance; the explicit-ask variant has zero
  data. The fixed-default variant is kept as the working choice; the
  explicit-ask variant is deferred to a future validation pass rather
  than blocking this round.
- **Vague category labels persist** (e.g. a debt entered as "Cosas" /
  "Deuda") regardless of whether the field was free text or a select
  with a "something else" escape hatch. Given participants were
  instructed to invent figures, this reads as a low-priority artifact
  of synthetic testing rather than a defect in the flow itself, and
  wasn't pursued further.

**Decision (owner, 2026-09-17):** this validation round is closed on
the evidence above — 3 participants is within the criterion's 2–3
target, the flow's mechanics held, and at least one genuine reaction
was captured. Closing on partial variant coverage is an explicit
choice, not an oversight: user validation now becomes a periodic,
recurring practice rather than a one-time gate before shipping,
coordinated with product planning based on product state going
forward — the deferred variant-A test is expected to be picked up in
that cadence rather than reopening this specific round.

## Out of scope

No design tool, no Claude Design, no high-fidelity mockup — this stays on
paper until the walk is done and a decision comment lands on issue #28
(owner decision, issue #28 criterion 4).
