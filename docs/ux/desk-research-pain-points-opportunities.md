# Desk research — how people use expat and personal-finance products

| Field | Value |
| --- | --- |
| **Lane** | UX - Design & Research (standing lane, opened 2026-08-20, gate [backend#229](https://github.com/alexandervivas/expat-ledger-backend/issues/229) closed) |
| **Source issue** | [expat-ledger-docs#7](https://github.com/alexandervivas/expat-ledger-docs/issues/7) |
| **Collection window** | 2026-09-03, desk research over public sources only |
| **Method** | Web search over app-store/Trustpilot review aggregators, public forums, and published comparison/teardown articles. No user interviews, surveys, or personal data were collected. |
| **Feeds** | UX reform (pain points below), Marketing - Positioning (gate [backend#230](https://github.com/alexandervivas/expat-ledger-backend/issues/230)), Discovery - Product Evolution (opportunities below) |

> **Confidence note.** This is desk research, not a survey: "recurs across N
> sources" below means N independent public sources surfaced the same
> complaint in one search pass, not a statistically representative sample.
> Treat rankings as directional. Corridor-specific evidence
> (Colombia–Netherlands, COP–EUR) is thin in public sources — see
> [Corridor specifics](#corridor-specifics) — and that gap is reported
> rather than papered over.

## Usage patterns

1. **Balance checking is frequent and habitual, not just reactive.** Industry
   research puts more than half of users checking account balances on a
   smartphone monthly, and two out of three cite the on-the-go check as a
   source of peace of mind, not urgency — a soothing ritual as much as a
   monitoring task.[^quicken] One vendor case study reports 90% of its users
   forming a daily cash-balance-check habit inside the app itself.[^cycb]
   Fintech engagement literature frames this explicitly as a design lever:
   vendors instrument "streaks" and notifications around the balance check
   because it is the single most reliable point of daily contact.[^engagement]
2. **The checking ritual is explicitly time-boxed, not open-ended browsing.**
   Design guidance for finance apps treats the balance-check ritual as a task
   to be *shortened* — one piece cites cutting the task from 42 seconds to
   under 5 via better notifications[^ritual] — which implies the target
   experience is "confirm the number, close the app," not a dashboard users
   linger in.
3. **Multi-currency users run more than one product in parallel rather than
   picking a single winner.** A 2026 comparison of Revolut, Wise, and bunq for
   the Netherlands finds that cross-border European users typically pair two
   apps for different jobs — commonly a local bank plus Wise, or Revolut plus
   Wise — rather than consolidating onto one.[^pairing] This is a usage
   pattern in its own right: the "one app, one number" mental model this
   product targets is not how today's power users actually operate.
4. **Manual reconciliation and categorization correction is routine, not
   exceptional.** An analysis across 17 personal-finance apps found an
   average 31% transaction miscategorization rate, and estimated users spend
   an average of 3.8 hours per month manually fixing miscategorized
   transactions.[^miscat] For multi-currency users specifically, one
   dedicated-tool vendor names transfer-vs-expense misclassification between
   a user's own accounts (moving CHF to EUR recorded as both an expense and
   income) as a distinct, recurring manual-cleanup task.[^tallyroot]
5. **Export and reporting behavior is under-documented in public sources.**
   No app-store review or forum thread surfaced in this sweep described a
   specific export/reporting ritual (e.g. monthly CSV pulls for a
   spreadsheet or accountant); this is a gap, not a negative finding — see
   [Opportunities](#opportunities) below.

## Pain points (ranked, strongest signal first)

1. **Account freezes and holds with little explanation, across nearly every
   competitor.** This is the single most consistent complaint across the
   sweep: Revolut has "frozen accounts and slow customer support" as its
   most cited pain points, with reviewers describing multi-month freezes
   over transfers of a few hundred pounds;[^revolut-freeze] N26 reviewers
   describe "a pattern of frozen or closed accounts, missing or delayed
   funds... and long waits with little explanation," including one case of
   funds held 2.5 months with no communication;[^n26-freeze] Wise reviews
   report "account freezes and verification requests, often triggered
   without warning," disproportionately affecting users with uncommon name
   spellings or activity across multiple countries — directly relevant to a
   dual-country user;[^wise-freeze] and bunq reviewers report accounts
   closed with limited access to the remaining balance.[^bunq-freeze]
   **Recurs across 4 independent competitors**, each with multiple
   corroborating reviews.
2. **Customer support that cannot resolve anything beyond scripted
   responses.** Revolut's support "relies heavily on AI chat," which
   frustrates users on complex issues, with human escalation reported as
   slow;[^revolut-support] N26's "most repeated complaint is support,"
   describing vague chat replies and issues that are "endlessly escalated"
   without follow-up;[^n26-support] Wise reviewers note that "every
   interaction connects you to a new agent," breaking continuity on
   unresolved cases;[^wise-support] bunq reviewers report chat response
   times of up to three days on live issues like fraud disputes and lost
   device access.[^bunq-support] **Recurs across all 4 neobank/fintech
   competitors reviewed**, usually paired with the freeze complaint above —
   the two compound (money is stuck *and* nobody can explain why).
3. **Transaction categorization requires ongoing manual correction.**
   Quantified above at 31% average miscategorization and 3.8 hours/month of
   user cleanup time across 17 apps studied.[^miscat] This is a pain point
   distinct from freezes/support: it is a steady tax on routine use rather
   than an acute incident.
4. **Single-currency budgeting tools actively break on multi-currency use.**
   A dedicated-expat-tool vendor names four concrete failure modes of
   mainstream budgeting apps for this audience: no native handling of
   paid-in-one-currency/spent-in-another transactions, no support for
   multiple accounts across countries, no adjustment for real exchange-rate
   movement (a weakening currency changes real rent cost, but the app
   doesn't know), and — most concretely — misclassifying a transfer between
   a user's own two currency accounts as both an expense and income,
   double-counting it.[^tallyroot] **Recurs as the explicit reason cited by
   at least 2 dedicated expat-finance tools** (Tallyroot, Borderless Budget)
   for existing as separate products rather than users just using YNAB or
   Mint-style trackers.[^bestapps]
5. **Fee and rate opacity, especially where the provider does not disclose a
   mid-market benchmark.** Revolut "doesn't use the mid-market rate
   directly... and hides the margin inside it," plus weekend markup fees of
   0.5–2%;[^revolut-rate] Wise users report surprise fees on specific
   actions (e.g. a cited $20 charge for USD account details) despite Wise's
   general reputation for rate transparency;[^wise-fee] bunq's conversion
   markup (0.5–1.5%) is presented as a separate line item rather than baked
   into a "no fees" claim, which reviewers treat as more honest but still a
   real cost.[^rate-comparison] **Recurs across 3 competitors**, though
   severity varies — this is more "erodes trust" than "acute failure."
6. **Behavioral abandonment: users disengage from the number itself, not
   just the app.** Budgeting-app research attributes churn less to missing
   features than to "monitoring fatigue" and active avoidance — "people stop
   logging... because they don't want to see the number that will
   appear."[^abandon] Industry estimates put abandonment within 3–4 weeks of
   install, with up to 68% of users leaving financial apps entirely over
   time.[^abandon-stat] **This is a single strong source with a supporting
   stat**, not corroborated across multiple independent citations in this
   sweep — flagged as a real but less-verified finding than 1–5 above.

## Opportunities

Each opportunity names the lane that would act on it, per the issue's brief.

1. **A single trustworthy "as of" number, with an honest data-freshness
   signal, instead of a dashboard that invites lingering.** The usage
   pattern is a short, habitual check (5–42 seconds);[^ritual] the product
   already frames its core loop as a daily morning position. The
   opportunity is to design *for* the short check — surface the number and
   what changed since yesterday, and resist adding engagement-bait
   (streaks, badges) that the fintech-engagement literature explicitly
   flags as a symptom of forced engagement rather than a genuine
   habit.[^engagement] — **Owning lane: UX.**
2. **Correct-by-construction transfer handling between a user's own
   accounts.** The double-counting failure mode named by dedicated
   expat-budgeting tools[^tallyroot] is a known, named, solvable defect
   class in this exact product category. If the product already models
   remittances/linkage distinctly from ordinary transactions (see
   `FR-006`), this is a chance to make that correctness visible as a
   differentiator, not just an internal design detail. — **Owning lane:
   UX**, with a **Discovery** angle if it is not already fully modeled for
   every account-to-account movement, not just cross-border remittances.
3. **Position "no frozen funds, ever, because we're not a neobank" as a
   trust claim.** Freezes and slow support are the top pain point across
   every neobank/fintech competitor reviewed, and severity is compounded
   when the product is explicitly a *tracking* layer rather than a
   custodian of funds. If that is true of this product's architecture, it
   is a differentiated, evidence-backed positioning claim rather than a
   generic trust statement. — **Owning lane: Marketing.**
4. **Real exchange-rate movement made visible, not just conversion at a
   point in time.** The single-currency-tool failure mode of not knowing
   that "a weakening currency changed your real rent cost"[^tallyroot]
   points to a feature opportunity beyond simple FX-aware conversion:
   showing purchasing-power drift over time for a COP-earning,
   EUR-spending (or vice versa) household. This goes beyond `AI-003`
   (FX-aware savings insight) if it is not already framed this way. —
   **Owning lane: Discovery.**
5. **Export/reporting is an evidence gap worth closing deliberately.** No
   public source in this sweep documented an export ritual for multi-
   currency users, despite tax-residency tools existing as a clearly
   adjacent, well-populated app category.[^taxtools] This product already
   commits to tax-residency-ready exports (`USP-001`). The gap is an
   argument for treating that export surface as a first-class, demoable
   feature rather than an internal capability — worth validating directly
   with the product's own users once evidence-gathering moves past desk
   research. — **Owning lane: Discovery**, with a **Marketing** angle once
   the feature exists (a claim no competitor reviewed here makes clearly).
6. **A genuinely human, fast resolution path for account/data issues, sized
   to a much smaller product.** Support quality is the second-ranked pain
   point industry-wide, driven at incumbents by scale (AI-first triage,
   agent handoffs). A small product can credibly promise something
   incumbents structurally cannot: a real person, fast, because the user
   base is small. This is a positioning claim that expires as the product
   grows — worth stating honestly now while it is true. — **Owning lane:
   Marketing.**

## Corridor specifics

Public sources on Colombia–Netherlands / COP–EUR money management
specifically are thin — this sweep found general expat-finance and
remittance-corridor material but very little that names this corridor or
currency pair directly. What is supported:

- **Remittance-corridor competition is real and provider quality is
  visibly uneven.** Multiple Colombia–Netherlands transfer providers exist
  (Moneytrans, Instarem, Paysend, Remitly), with cited experiences ranging
  from near-instant Wise transfers at the published market rate to
  forum advice favoring specific providers (Ria, Remitly) over others on
  rate quality.[^remit] This corroborates that FX-rate transparency is a
  live concern for this exact corridor, not just a general expat
  complaint.
- **Cross-border users tend to run parallel tools rather than one
  system**, per the multi-app-pairing pattern in
  [Usage patterns](#usage-patterns) above[^pairing] — directly relevant
  to a product whose value proposition is replacing that parallel-tool
  workflow with one honest view.
- **Dual tax-residency tooling exists as a distinct, populated app
  category** (day-counting and treaty-tie-breaker trackers), evidence that
  users treat tax-residency tracking as a real, recurring task worth a
  dedicated tool rather than a one-off lookup.[^taxtools] This sweep found
  no source describing how such tools integrate — or fail to integrate —
  with everyday balance/transaction tracking, which is itself a gap worth
  flagging to Discovery.
- **What this sweep did not find**: no public review, forum thread, or
  article discussing COP-to-EUR budgeting, ABN AMRO/ING/Bancolombia usage
  patterns together, or Colombia–Netherlands migrant financial behavior
  specifically. Any corridor-specific claim beyond the above should be
  treated as inferred from adjacent expat-finance material, not directly
  evidenced, until first-party research (out of scope for this desk-only
  brief) is done.

## Sources

[^quicken]: Quicken user research, cited in ["Best Budgeting Apps of 2026: Tested And Ranked"](https://www.forbes.com/advisor/banking/best-budgeting-apps/) and related aggregator coverage of mobile balance-check frequency.
[^cycb]: [CYCB — Optimize Expense Habit](https://apps.apple.com/py/app/cycb-optimize-expense-habit/id6449403916), App Store listing citing a 90% daily-check-habit figure for its users.
[^engagement]: [Fintech App Retention Strategies: The Gaming Rewards Layer](https://www.adaction.com/blog/fintech-app-user-retention-strategies) and [StriveCloud — Mobile App Gamification in Fintech](https://www.strivecloud.io/blog/mobile-app-gamification-fintech).
[^ritual]: [Turning Daily Banking into a Personal Finance Check-In: 7 Tips](https://importantcool.com/essential-hacks/turning-daily-banking-into-a-personal-finance-check-in-7-tips/); the 42-second-to-5-second figure is cited in finance-app design guidance surfaced in this search pass and should be treated as an industry claim, not an independently verified statistic.
[^pairing]: [Revolut vs Wise vs bunq Netherlands 2026: Choose by Use Case](https://www.frankx.ai/blog/revolut-vs-wise-vs-bunq-netherlands-2026).
[^miscat]: Categorization-accuracy analysis referenced via [Plaid — Our biggest update to transaction data categorization](https://plaid.com/blog/transactions-categorization-taxonomy/) and corroborating coverage in search results for personal-finance categorization complaints.
[^tallyroot]: [Tallyroot — Best Budget App for Expats (2026): 7 Multi-Currency Apps Compared](https://tallyroot.com/blog/best-budget-app-for-expats/).
[^bestapps]: [Borderless Budget — Best Budgeting Apps for Expats 2026](https://borderlessbudget.com/compare/best-budgeting-apps-for-expats); [Tallyroot](https://tallyroot.com/blog/best-budget-app-for-expats/).
[^revolut-freeze]: [Financer — Revolut Review 2026](https://financer.com/review/revolut/); [Revolut Reviews and Complaints — PissedConsumer](https://revolut.pissedconsumer.com/complaints/RT-P.html).
[^n26-freeze]: [N26 Reviews — Trustpilot](https://www.trustpilot.com/review/n26.com); [N26 Reviews — Apple App Store](https://apps.apple.com/us/app/n26-love-your-bank/id956857223?see-all=reviews&platform=iphone).
[^wise-freeze]: [Wise Reviews — Trustpilot](https://www.trustpilot.com/review/wise.com); [Wise (formerly TransferWise) Reviews — ConsumerAffairs](https://www.consumeraffairs.com/finance/transferwise.html).
[^bunq-freeze]: [bunq Reviews — Trustpilot](https://www.trustpilot.com/review/bunq.com); [Discover What Customers Really Think About Bunq — Kimola](https://kimola.com/reports/discover-what-customers-really-think-about-bunq-trustpilot-en-us-141403).
[^revolut-support]: [Financer — Revolut Review 2026](https://financer.com/review/revolut/).
[^n26-support]: [N26 Reviews — Trustpilot](https://www.trustpilot.com/review/n26.com).
[^wise-support]: [Wise Reviews — Trustpilot](https://www.trustpilot.com/review/wise.com).
[^bunq-support]: [bunq Reviews — Trustpilot](https://www.trustpilot.com/review/bunq.com).
[^revolut-rate]: [Revolut vs Wise vs bunq Netherlands 2026 — FrankX](https://www.frankx.ai/blog/revolut-vs-wise-vs-bunq-netherlands-2026); [Revolut vs. Wise: Which is best for you? 2026 Guide — Wise](https://wise.com/us/blog/revolut-vs-wise).
[^wise-fee]: [Wise (formerly TransferWise) Reviews — ConsumerAffairs](https://www.consumeraffairs.com/finance/transferwise.html).
[^rate-comparison]: [🏦 Which business bank to choose in 2026: Bunq or Wise? — Heropay](https://www.heropay.eu/en/blog/bunq-vs-wise); [Revolut vs Wise vs bunq Netherlands 2026 — FrankX](https://www.frankx.ai/blog/revolut-vs-wise-vs-bunq-netherlands-2026).
[^abandon]: [Beaverise — Why Your Budgeting App Isn't Working (It's Not You)](https://beaverise.com/blog/why-budgeting-apps-dont-work).
[^abandon-stat]: [SpendTrak — Why People Quit Budgeting Apps in 30 Days (2026)](https://spendtrak.app/blog/why-people-quit-budgeting-apps).
[^remit]: [Moneytrans — Money transfer from the Netherlands to Colombia](https://www.moneytrans.eu/netherlands/en/send-money-to-colombia/); [Expat.com forum — Best way to send $$ to Colombia](https://www.expat.com/en/forum/south-america/colombia/1013893-best-way-to-send-dollar-dollar-to-colombia.html); [Remitly — Send money to Bancolombia in Colombia from the Netherlands](https://www.remitly.com/nl/en/providers-colombia/send-money-to-bancolombia).
[^taxtools]: App Store listings for [Visa Day Tracker: Residency](https://apps.apple.com/us/app/-/id6749048224) and [Tax Resident - Days Tracker](https://apps.apple.com/ca/app/tax-resident-days-tracker/id1510629340); [Greenback Tax Services — 7 Key Insights About FATCA from Reddit](https://www.greenbacktaxservices.com/blog/7-key-insights-about-fatca-from-reddit-according-to-americans-abroad/).
