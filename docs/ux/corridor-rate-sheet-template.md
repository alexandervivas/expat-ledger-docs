# Corridor rate sheet — structure and synthetic example

| Field | Value |
| --- | --- |
| **Lane** | Discovery — Product Evolution |
| **Source issue** | [expat-ledger-docs#46](https://github.com/alexandervivas/expat-ledger-docs/issues/46) |
| **Feeds** | The real-spreadsheet lean product ([expat-ledger-docs#39](https://github.com/alexandervivas/expat-ledger-docs/issues/39)) — this page is the recruitment-call artifact promised there |

> **Synthetic data only.** Every figure below is invented for illustration.
> The owner's twelve-receipt Remitly test (docs#46) runs this same structure
> against real receipts in a private, local sheet — those real amounts never
> enter this repository, this page, or any linked issue. See
> `docs/governance/evidence-archive.md` and the privacy note on docs#46 for
> the rule this page follows.

## Capture columns

Six columns are captured per transfer, one row per transfer:

| Column | What it records |
| --- | --- |
| Debited | Amount taken from the sender's account, in the sending currency. |
| Converted | Amount actually applied to the FX conversion, in the sending currency — i.e. debited minus the provider's explicit up-front fee. |
| Received | Amount the recipient gets in hand, in the receiving currency, after any payout-method deduction. |
| Payout method | How the recipient collects the funds (e.g. bank deposit, cash pickup, mobile wallet). |
| Speed | Time from send to funds available (e.g. instant, same day, 1–2 days). |
| Provider | The remittance provider used for the transfer. |

Two figures are **derived**, never captured directly:

- **Fee** = Debited − Converted, in the sending currency. An absent Converted
  value is unknown, not zero — never assume Fee is zero when Converted is
  missing.
- **Effective rate** = Received ÷ Converted — the exchange rate the provider
  actually applied, isolated from its up-front fee.
- **All-in rate** = Received ÷ Debited — what the sender truly got per unit
  of sending currency, blending the fee and the FX spread into one number
  comparable across providers and corridors.

No external reference or mid-market rate is used anywhere in this sheet —
both rates are computed exactly from the transfer's own observed values.

## Synthetic example (twelve transfers)

| # | Debited (EUR) | Converted (EUR) | Fee (EUR) | Received (COP) | Payout method | Speed | Provider | Effective rate | All-in rate |
| - | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 500.00 | 495.10 | 4.90 | 2,150,010 | Bank deposit | Same day | Remitly | 4,342.58 | 4,300.02 |
| 2 | 500.00 | 495.10 | 4.90 | 2,146,890 | Bank deposit | Same day | Remitly | 4,336.28 | 4,293.78 |
| 3 | 750.00 | 743.20 | 6.80 | 3,229,890 | Bank deposit | Instant | Remitly | 4,345.92 | 4,306.52 |
| 4 | 500.00 | 493.90 | 6.10 | 2,138,470 | Cash pickup | Instant | Remitly | 4,329.76 | 4,276.94 |
| 5 | 500.00 | 495.30 | 4.70 | 2,155,140 | Bank deposit | Same day | Remitly | 4,351.18 | 4,310.28 |
| 6 | 1,000.00 | 991.40 | 8.60 | 4,315,020 | Bank deposit | 1–2 days | Remitly | 4,352.45 | 4,315.02 |
| 7 | 500.00 | 494.70 | 5.30 | 2,148,660 | Bank deposit | Same day | Remitly | 4,343.36 | 4,297.32 |
| 8 | 500.00 | 493.50 | 6.50 | 2,131,110 | Cash pickup | Instant | Remitly | 4,318.36 | 4,262.22 |
| 9 | 500.00 | 495.60 | 4.40 | 2,161,280 | Bank deposit | Same day | Remitly | 4,360.94 | 4,322.56 |
| 10 | 750.00 | 742.50 | 7.50 | 3,238,410 | Bank deposit | Instant | Remitly | 4,361.49 | 4,317.88 |
| 11 | 500.00 | 494.90 | 5.10 | 2,161,120 | Bank deposit | Same day | Remitly | 4,366.78 | 4,322.24 |
| 12 | 500.00 | 495.20 | 4.80 | 2,165,010 | Bank deposit | Same day | Remitly | 4,371.99 | 4,330.02 |

This is the shape a trend read against a kill criterion runs on: twelve rows,
each with its derived fee and its two derived rates, read across the run for
drift rather than compared transfer-by-transfer. The real test (docs#46)
reports its verdict — hook confirmed or hook weaker than assumed — as a
comment, never as figures.

## Recruitment-call use

For interview participants, this same six-column structure (with the
derived Fee, Effective rate, and All-in rate columns filled in
automatically) is the artifact traded for a 20-minute research call:
participants fill in their own transfers and see their own trend, with
nothing of the owner's history ever shown to them. Delivery mechanism
(public template vs. an individual copy per participant) is an open
question on docs#39 and is not decided by this page.
