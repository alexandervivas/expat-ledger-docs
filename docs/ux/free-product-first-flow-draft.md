# Free product first flow — paper draft

| Field | Value |
| --- | --- |
| **Lane** | UX - Design & Research |
| **Source issue** | [expat-ledger-docs#28](https://github.com/alexandervivas/expat-ledger-docs/issues/28) |
| **Method** | Interface first, services after (walk decision 2026-08-28): the flow is defined on paper before any design tool or code. |
| **Status** | **Unvalidated draft.** This page is a starting point for the owner to revise on paper and then walk with 2–3 people — it is not the validated flow, and it does not by itself satisfy issue #28's acceptance criteria. |
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
generic debts — it is the pain point this product exists to answer
correctly (see `docs/requirements/FR-006-remittance-linkage.md` and the
double-counting failure mode named in
[Desk Research: Pain Points & Opportunities](desk-research-pain-points-opportunities.md#pain-points-ranked-strongest-signal-first)).

## Draft question sequence

One question per index card, asked in this order. Each card's answer feeds
the next; nothing is asked twice.

1. **Income this month.** "How much money will you have coming in this
   month, and in what currency?" — a single hand-written number per income
   source (salary, freelance, other), each tagged with its currency.
2. **Fixed debts and obligations.** "What do you already owe or have to pay
   this month, before anything else?" — rent, loan installments,
   subscriptions, anything recurring and non-negotiable.
3. **Family remittance obligation (first-class).** "How much do you send or
   commit to family each month, and to whom?" — asked as its own card,
   never merged into card 2, because it is a distinct commitment with its
   own currency and its own emotional weight (per the founder's own
   arrival experience — see issue #29).
4. **Safety margin (open question — see below).** Whether the flow asks for
   a desired buffer explicitly, or applies a fixed default, is undecided;
   flag it during the walk rather than deciding it here.

## Draft answer

A single number, shown with its breakdown, never as a bare figure:

```
You can commit: [income] − [debts] − [family obligation] − [buffer] = X

Income:            [amount] [currency]
Debts:             [amount] [currency]
Family obligation: [amount] [currency]
Buffer:            [amount or "none applied"]
─────────────────────────────────────────
Committable:       X [currency]
```

Showing the breakdown, not just X, is deliberate: the desk research found
users spend hours a month untangling miscategorized manual entries — the
flow should let a participant see and correct which card produced a wrong
number, not just distrust a total.

## Open questions to resolve before walking

These mirror the open questions still unanswered on issue #39, since both
issues describe the same qualifying flow from different lanes:

1. Whether the safety-margin card is asked explicitly or defaulted, and if
   defaulted, what the default is and how it is disclosed.
2. How multi-currency income/debts/obligation are combined into one
   committable figure — a single base currency chosen up front, or kept
   separate and shown per currency.
3. Whether irregular or variable income (freelance, tips) is asked as a
   single figure or as a range.
4. The precise wording of "family obligation" in the language the
   participant will actually be interviewed in (the recruitment post,
   issue #38, is written in Spanish for the target population).

## Walking it with 2–3 people

1. Print or hand-write the four cards above; nothing digital.
2. Ask the participant to fill each card as if it were their own month,
   using invented numbers — never their real income, debts, or transfers.
3. Do not explain a card before they attempt it; the friction of a
   misread or skipped card is the finding.
4. After all four cards, show the derived answer and ask: "does this match
   what you'd expect to be told?" — record disagreement, not just
   agreement.
5. Capture, per participant: where they hesitated, what they asked to
   clarify, and any card they wanted to answer differently than asked
   (e.g., wanting to give a range instead of one number).

## Out of scope

No design tool, no Claude Design, no high-fidelity mockup — this stays on
paper until the walk is done and a decision comment lands on issue #28
(owner decision, issue #28 criterion 4).
