# Design Direction Audit — Evidence Record and Defect Register

- Date: 2026-08-06
- Issue: [expat-ledger-frontend#38](https://github.com/alexandervivas/expat-ledger-frontend/issues/38)
- Decision: [ADR-004](/reference/frontend/decisions/ADR-004-design-direction-restructure-over-restyle.md)
- Snapshot: `origin/main` at `5dc7cee`, with `issue-21-live-account-balance-api` in flight (7/10 tasks)

This is the evidence behind ADR-004 and the register the follow-up work draws from. Every entry carries a `file:line`
citation so that drift against a changing codebase is detectable rather than silent. All values shown are synthetic or
computed; no real balance, account identifier, statement, or credential appears here.

## 1. Was the Lovable hypothesis correct?

Partly, and not where it was expected. Summarised verdicts:

| Axis | Verdict | Evidence |
|---|---|---|
| Colour token discipline | **Sound** | 7 raw Tailwind palette-literal utilities repo-wide: 4 in `NotFound.tsx:14-18`, 3 in vendored `ui/toast.tsx:70`. Hand-written code therefore carries 4, all in one file. `src/index.css:10-69` and `:71-127` define a complete semantic set for light and `.dark` |
| Semantic markup | **Sound** | 52 semantic heading elements in hand-written components (54 including vendored `ui/`) |
| State handling (R1.1 surfaces) | **Good — reuse it** | `Dashboard.tsx:473-506`, `:566-584`, `bankLoadStatus.ts`, `:866-871` |
| Chart colour tokens | **Broken** | 5 undefined tokens; see §2.1 |
| Focus ring colour | **Broken** | `src/index.css:48` |
| Dark mode | **Not deliverable** | No toggle anywhere; see §2.2 |
| Type scale | **Undefined** | No `fontSize`/`fontFamily` in `tailwind.config.ts`; no font loaded in `index.html`; 10 distinct text sizes used ad hoc |
| Spacing scale | **Two coexisting systems** | See §3.1 |
| Component reuse | **Weak** | 22 of 48 vendored primitives unused; **12** independent `formatCurrency` definitions |
| Accessibility enforcement | **Absent** | No `jsx-a11y` in `eslint.config.js`; charts expose zero a11y affordances |
| Information architecture | **Wrong for the positioning** | §4 in full |
| Honesty of displayed capability | **Multiple violations** | §4 in full |

**Conclusion.** The generated inheritance is not a styling problem. It is a *content model* problem — a generic
finance-app screen set produced to look complete — plus a small number of genuine token defects.

## 2. Verified-by-execution findings

These were established by running the app, not by reading it. They are recorded separately because inspection alone
gave an ambiguous or wrong answer in each case.

### 2.1 Five chart colour tokens are undefined; five categories render identical black

`CategoryBreakdownChart.tsx:11-19` assigns:

```
INCOME: hsl(var(--success))            GROCERIES: hsl(var(--chart-1))
UTILITIES: hsl(var(--chart-2))         TRANSPORT: hsl(var(--chart-3))
ENTERTAINMENT: hsl(var(--chart-4))     HEALTHCARE: hsl(var(--chart-5))
OTHER: hsl(var(--muted-foreground))
```

`--chart-1` … `--chart-5` are **defined nowhere in the repository**. The only five occurrences of `--chart-` in `src/`
are these five usages; there is no definition in `src/index.css` or `tailwind.config.ts`.

Resolved fills, measured in the running application **with the `dark` class applied** (carried over from the §2.2 test
in the same page session):

| Reference | Computed value |
|---|---|
| `hsl(var(--success))` | `rgb(33, 196, 93)` |
| `hsl(var(--chart-1))` | `rgb(0, 0, 0)` |
| `hsl(var(--chart-2))` | `rgb(0, 0, 0)` |
| `hsl(var(--muted-foreground))` | `rgb(148, 163, 184)` — the `.dark` value (`src/index.css:89`); light is `rgb(101,117,139)` (`:29`) |

The theme state does not affect the finding: `--chart-1` … `--chart-5` are undefined in **both** themes, so the
collapse to black is theme-independent.

**Impact.** Groceries, Utilities, Transport, Entertainment, and Healthcare are indistinguishable in the pie chart and
in the legend swatches (`CategoryBreakdownChart.tsx:117`, which uses the same map for `backgroundColor`). Also present:
a hardcoded Recharts example colour `fill="#8884d8"` at `CategoryBreakdownChart.tsx:86`.

**Recommendation.** Define the five tokens for both themes, validated for categorical distinguishability and contrast,
and add a check that fails on an undefined custom property. Remove the `#8884d8` literal.

### 2.2 FR-016 is a missing toggle, not missing design

- `tailwind.config.ts:4` sets `darkMode: ["class"]`.
- `.dark` tokens are **complete** — `src/index.css:71-127` mirrors every light token.
- `useTheme` appears **only** in the vendored `ui/sonner.tsx:1,7`. No `ThemeProvider` wraps the app; no code anywhere
  calls `documentElement.classList.add/toggle`.
- `dark:` utilities: **0** occurrences in hand-written components; 2 in vendored `ui/`.

Measured in the running app: `document.documentElement.classList` is **empty**. Manually adding `dark` resolved tokens
correctly — `--background: 222 47% 11%`, `--foreground: 210 40% 98%`, `--card: 217 33% 17%`, `--primary: 173 58% 50%` —
and the page rendered as a coherent dark theme.

**Recommendation.** Wire a provider, a persisted preference, and a user-facing control. No design work required.

### 2.3 The app runs today; only authenticated surfaces are gated

`bun dev` starts cleanly (Vite 7.1.11, ready ~1.5s, port 8080). The Landing page renders fully. `/dashboard` redirects
to `/` when unauthenticated, so authenticated surfaces require Auth0 credentials that an agent must not supply.

**Correction to issue #38's premise:** Chrome-driven visual iteration is *not* blocked pending R1.0. It is available
today for unauthenticated surfaces, and requires a human-supplied session for the rest.

### 2.4 Figma MCP entitlement

`whoami`: `tier: starter`, `seat: View`. Per Figma's own `rate-limits-access.md` served by the MCP server: View/Collab
seats get up to **6 tool calls per month on every plan**; Starter has **no Dev/Full seat tier**; write tools
(`generate_figma_design`, `add_code_connect_map`, `whoami`) are exempt from rate limits but require a Full seat.
Code Connect requires Organization or Enterprise. Full cost reasoning in ADR-004 Decision 4.

## 3. Design-system findings

### 3.1 Two coexisting spacing systems

`tailwind.config.ts:73-85` overrides indices 0–10 with a custom ramp (1=2px, 2=4px, 3=8px, 4=16px, 5=24px, 6=32px,
7=40px, 8=48px, 9=64px, 10=80px). Because Tailwind's `extend` merges, indices ≥11 still resolve to Tailwind's stock
rem-based scale.

Consequences:

- Vendored shadcn primitives in `ui/**` were authored against the stock scale, so every `p-2`/`p-4`/`gap-6` in them
  now resolves to a non-stock pixel value project-wide.
- 46 usages of indices ≥11 exist outside `ui/` — e.g. `Landing.tsx:84` (`py-16 md:py-24`), `Landing.tsx:108` (`mb-12`),
  `TransactionList.tsx:145` (`p-12`), `CategoryManagementDialog.tsx:104` (`py-12`). These resolve against the *stock*
  scale, so the codebase mixes two differently-derived ramps.
- 23 arbitrary-value utilities in hand-written components (393 across all of `src/presentation`, the bulk of them in
  the vendored primitives) — `w-[240px]`, `max-h-[80vh]`, `h-[calc(100vh-120px)]`, e.g. `TenantSwitcher.tsx:64`,
  `CategoryManagementDialog.tsx:59`, `ActivityLog.tsx:117`, `TransactionList.tsx:92,103,117`. The dialog and popover
  widths among them suggest the custom ramp's 80px ceiling is inadequate for layout sizing.

**Recommendation.** Low priority, but decide one ramp. This is a latent inconsistency rather than a visible defect.

### 3.2 No type scale

No `fontSize` or `fontFamily` extension in `tailwind.config.ts`; no `@font-face` or family declaration in
`src/index.css`; no font `<link>` in `index.html`. Despite product branding, the app renders in the OS default sans
stack.

Sizes in use: `text-sm` (158), `text-xs` (60), `text-lg` (23), `text-3xl` (18), `text-2xl` (17), `text-xl` (9),
`text-4xl` (3), `text-base` (2), `text-5xl` (2), `text-6xl` (1) — 10 distinct sizes. Weights: `font-semibold` (59),
`font-medium` (57), `font-bold` (45), `font-normal` (5). Headings are semantic but each pairs its own ad-hoc className
combination (e.g. `Landing.tsx:108`), so consistency is by copy-paste rather than by component or layer.

### 3.3 Dead and duplicated surface area

**22 of 48 vendored `ui/` primitives are imported nowhere:** `alert-dialog`, `aspect-ratio`, `breadcrumb`, `carousel`,
`chart`, `checkbox`, `collapsible`, `context-menu`, `drawer`, `form`, `hover-card`, `input-otp`, `menubar`,
`navigation-menu`, `pagination`, `radio-group`, `resizable`, `sidebar`, `slider`, `table`, `textarea`, `toggle-group`.

Note `chart.tsx` is among the unused — the four charts use Recharts directly, which is how the undefined `--chart-*`
tokens went unnoticed.

**Duplications:**

- **`formatCurrency` is independently re-implemented 12 times** — every one a local `const` inside a component:
  `Dashboard.tsx:537`, `TransactionList.tsx:37`, `AccountDetailDialog.tsx:175`, `CategoryManagementDialog.tsx:47`,
  `FinancialInsights.tsx:26`, `ManageObligationsDialog.tsx:107`, `RecurringTransactionDialog.tsx:108`,
  `BudgetManagementDialog.tsx:93`, and all four charts (`CategoryBreakdownChart.tsx:52`,
  `IncomeVsExpensesChart.tsx:46`, `SpendingTrendChart.tsx:50`, `BudgetProgressChart.tsx:73`). Given that ADR-001 and
  ADR-003 exist specifically to protect money semantics, **twelve independent money formatters is the highest-value
  consolidation on this list** — each is a place the display convention can drift from the others, and four of them
  take no currency argument at all.
- Identical hand-rolled spinner markup in `ProtectedRoute.tsx:17` and `Landing.tsx:39`.
- Empty-state strings and wrappers duplicated: `TransactionList.tsx:150`, `AccountDetailDialog.tsx:371`,
  `Dashboard.tsx:806`.

### 3.4 Accessibility posture

Counts across hand-written `src/presentation` (excluding vendored `ui/`): `aria-*` 38, `role=` 33, `sr-only` 2,
`label htmlFor` 22, `alt=` 3. No `<div onClick>`/`<span onClick>` found.

Gaps:

- **Charts expose zero accessibility affordances.** No `aria`, `role`, `sr-only`, `<table>`, or `<caption>` in any of
  the four chart components.
- **No `jsx-a11y`** in `eslint.config.js`. The config enforces TypeScript strictness and the hexagonal boundaries
  (`eslint.config.js:77-97`) but no accessibility rule.
- **`--ring: 231 98% 65%`** (indigo) against `--primary: 173 58% 39%` (teal) — `src/index.css:48`. Orphaned focus-ring
  colour from a different palette.
- No `focus-visible` usage outside vendored `ui/`; app code relies entirely on the primitives.

## 4. Dashboard element classification

Data source is traced to its true origin. "Honest" means backed by delivered capability.

Render sites are as they stood when this audit was written. Four rows have since been **discharged by
[issue #22](https://github.com/alexandervivas/expat-ledger-frontend/issues/22)**, which removed the elements outright
rather than restyling them; see [ADR-005](/reference/frontend/decisions/ADR-005-daily-position-freshness-and-completeness.md). Their line
numbers no longer resolve and are kept only so this audit remains readable against the commit it describes.

| Element | Render site | True source | Honest? |
|---|---|---|---|
| "Total Balance" hero | `Dashboard.tsx:614-628` | LIVE API + DERIVED via identity-only FX matrix | **No** — silent undercount. **Discharged by #22:** removed, replaced by per-currency subtotals that compute no cross-currency figure |
| Growth badge | `Dashboard.tsx:619-622` | DERIVED from LIVE API | Partly — see §5.3. **Discharged by #22:** removed with the hero |
| "Past Due" | `Dashboard.tsx:634-654` | LOCAL-STORAGE | Computation honest; scope undisclosed. Still present and still unaddressed — see §5.5 |
| "Upcoming" | `Dashboard.tsx:656-677` | LOCAL-STORAGE | Computation honest; scope undisclosed. Still present and still unaddressed — see §5.5 |
| "End Month Forecast" | `Dashboard.tsx:679-695` | DERIVED — linear extrapolation | **No** — labelled as forecast. **Discharged by #22:** removed, with the `calculateForecast` call that fed it |
| "Available Space" | `Dashboard.tsx:697-713` | DERIVED — constant 30% | **No**. **Discharged by #22:** removed |
| Quick Actions | `Dashboard.tsx:722-729` | Mixed | Partly — Recurring/Compliance dishonest |
| "Smart Insights" | `Dashboard.tsx:738-742` | DERIVED from LIVE API | **No** — labelled "AI-powered" |
| SpendingTrendChart | `Dashboard.tsx:753` | DERIVED from LIVE API | **No** — zero reads as observed |
| IncomeVsExpensesChart | `Dashboard.tsx:754` | DERIVED from LIVE API | **No** — zero reads as observed |
| CategoryBreakdownChart | `Dashboard.tsx:758` | DERIVED from LIVE API | Empty state correct; colours broken (§2.1) |
| BudgetProgressChart | `Dashboard.tsx:759` | DERIVED from LOCAL-STORAGE | Empty state correct |
| Accounts grid | `Dashboard.tsx:801-896` | LIVE API | **Yes** — exemplary |
| Bank name per account | `Dashboard.tsx:821,851-855` | LIVE API | **Yes** — exemplary |
| Recent Activity list | `Dashboard.tsx:908-914` | LIVE API | **Yes** |
| ComplianceDashboard | `ComplianceDashboard.tsx` | Mixed — 2 of 4 hardcoded | **No** — most serious |
| RecurringTransactionDialog | `RecurringTransactionDialog.tsx` | IN-MEMORY, never persisted | **No** |
| ReportsDialog | `ReportsDialog.tsx:42-238` | DERIVED from LIVE API | Functional; plain-text export |

## 5. Defect register

Ordered by severity. None is fixed in issue #38; each is independently actionable.

### 5.1 Fabricated security assurances — **highest severity**

`ComplianceDashboard.tsx:67-68` hardcodes `{ name: 'Encryption at Rest', passed: true }` and
`{ name: 'Access Control', passed: true }`, both annotated `// Simulated`, rendered with the same affirmative
`CheckCircle2`/"Passed" treatment (`:156-165`) as the two genuinely computed security checks in the same array —
`hasIsolation` and `hasIntegrity`, derived from real transaction data at `:56-66`. (The separate retention and
audit-readiness cards at `:21-53` are computed too, but they are different cards, not the comparison here.) A false
security assurance in a financial product is worse than none, because a user may rely on it.

**Filed as [issue #43](https://github.com/alexandervivas/expat-ledger-frontend/issues/43)** rather than queued behind
the design direction. See ADR-004 Decision 7.

### 5.2 "Total Balance" silently drops accounts — **discharged**

**Discharged by [issue #22](https://github.com/alexandervivas/expat-ledger-frontend/issues/22).** The hero, the
identity-only rate matrix, the `catch` that produced the partial total, and the two cards that consumed it are all
removed. The replacement surface computes no cross-currency figure at all — an absence of computation rather than a
refusal to display, so no consumer can neutralise it the way this defect describes — and every subtotal carries the
count of accounts it actually covers. See [ADR-005](/reference/frontend/decisions/ADR-005-daily-position-freshness-and-completeness.md).
`currencyAggregation.ts` is untouched and remains correct for a future preferred-currency feature with a real rate
source. The open question below is unresolved and simply no longer blocking.

The original finding, retained as written:

`Dashboard.tsx:509-513` defines identity-only rates. `currencyAggregation.ts:47-49` correctly throws
`MissingExchangeRateError` — as `openspec/specs/multi-currency-balance-aggregation/spec.md` requires ("MUST throw a
typed domain error and MUST NOT return a partial total"). `Dashboard.tsx:523-535` catches it and sums only
base-currency accounts, while `:625` still reports the full account count.

**This is the audit's central structural finding:** the domain guarantee is honoured where written and neutralised by
its consumer, because the existing requirement constrains the aggregator and nothing constrained the consumer. Closed
specification-side by `honest-capability-presentation`.

A EUR+COP tenant — the product's canonical user — sees a total omitting whole accounts, with no indication.

**Open question blocking accurate scheduling:** whether a backend FX rate endpoint exists. Nothing in this frontend
wires one; no backend contract was read for this spike.

### 5.3 Honesty and state defects

| # | Defect | Location |
|---|---|---|
| 1 | "Available Space" is `Math.max(0, endOfMonthBalance * 0.3)` — a fixed proportion. Obligations *are* deducted upstream (`:50-56`); budgets are not, and `calculateForecast` has no `budgets` parameter to accept them (`:12-16`) | `forecasting.ts:59,50-56,12-16` |
| 2 | "End Month Forecast" is a 30-day linear extrapolation with `confidence = (txCount/30)*100`; averages divide by a constant 30 regardless of observed days | `forecasting.ts:12-71`, esp. `:41-42,62` |
| 3 | "AI-powered analysis" labels deterministic arithmetic | `Dashboard.tsx:736` |
| 4 | Zero-seeded charts read as observed zero activity; no empty state | `SpendingTrendChart.tsx:20-29`, `IncomeVsExpensesChart.tsx:19-27` |
| 5 | Synthesised `'NONE'` category rendered as top expense category with `formatCurrency(0)` | `FinancialInsights.tsx:65,72,130-131` |
| 6 | Account Health `reduce(...)/length \|\| 0` renders "0%" for both no-data and genuine zero | `FinancialInsights.tsx:104,152` |
| 7 | Recurring transactions held in `useState`, never persisted; nothing is scheduled | `RecurringTransactionDialog.tsx:56` |
| 8 | Growth badge always prefixes `+` even when negative; unrounded float; `0` shown when `totalBalance <= 0` | `Dashboard.tsx:556-559,619-622` |
| 9 | Budgets and obligations are `localStorage`-only; per-browser scope undisclosed on a tenant-shared product | `LocalStorageBudgetRepository.ts:4`, `LocalStorageObligationRepository.ts:4` |

### 5.4 Design-system defects

| # | Defect | Location |
|---|---|---|
| 10 | `--chart-1`…`--chart-5` undefined; 5 categories render identical black | `CategoryBreakdownChart.tsx:11-19` |
| 11 | Hardcoded Recharts example colour `#8884d8` | `CategoryBreakdownChart.tsx:86` |
| 12 | FR-016 not deliverable — no theme provider, toggle, or persistence | app-wide; tokens ready at `src/index.css:71-127` |
| 13 | Orphaned indigo focus ring on a teal-primary product | `src/index.css:48` |
| 14 | No `jsx-a11y` — accessibility entirely unenforced | `eslint.config.js` |
| 15 | Charts expose no text alternative or accessible summary | `src/presentation/components/charts/**` |
| 16 | `formatCurrency` independently re-implemented 12 times | §3.3 |
| 17 | `NotFound.tsx` fully un-tokenized; bare `<a href>` instead of router link | `NotFound.tsx:14-18` |
| 18 | 22 of 48 vendored primitives unused | §3.3 |
| 19 | Two coexisting spacing ramps; 47 arbitrary-value escapes | §3.1 |
| 20 | No type scale or loaded typeface | §3.2 |
| 21 | Lovable OG/Twitter metadata served for a self-branded product | `index.html:13,16,17` |

### 5.5 "Past Due" and "Upcoming" sum across currencies under one symbol — **open**

Added while discharging §5.2, because removing the "Total Balance" hero left the two surviving obligation cards as the
dashboard's only remaining cross-currency figures, and the register should not read as though the dashboard were now
clean.

`Obligation` carries `amount: number` and `currency: string` as separate fields
(`src/domain/models/Obligation.ts:9-10`). `getObligationsSummary` reduces over `o.amount` alone and never reads
`o.currency` (`src/domain/logic/forecasting.ts:84-85`), and `Dashboard.tsx:617,640` renders each result through
`formatCurrency(pastDue, tenantSettings.baseCurrency)`. A tenant with a COP 500,000 obligation and a EUR 100 obligation
therefore sees `€500,100.00` — a figure that is not a quantity of anything, presented with the authority of a currency
symbol. It is the same class of defect as §5.2 in a different feature: the currency dimension dropped, then a single
symbol applied to the result.

| # | Defect | Location |
|---|---|---|
| 22 | Obligation totals sum across currencies and render under the base-currency symbol | `Obligation.ts:9-10`, `getObligationsSummary`, `Dashboard.tsx` "Past Due" / "Upcoming" |

**Pre-existing and outside issue #22's scope** — that issue removed the total-balance hero and did not touch
obligations, whose amounts are a plain `number` rather than `Money` and whose repository is `localStorage`-only
(defect 9). Fixing it means modelling obligation amounts as `Money`, which is its own change. Recorded here so the
claim in `README.md` that §5.2's gap is closed cannot be read as covering the whole dashboard.

## 6. Patterns worth propagating

The restructure must reuse these rather than replace them — they are the standard the new work should meet:

- `Dashboard.tsx:473-506` — distinct blocking-failure, initial-loading, and incomplete-settings states with
  `role="alert"`, `role="status"`, `aria-live`, `aria-busy`.
- `Dashboard.tsx:566-584` — non-blocking refreshing / refresh-failed-with-stale-data banner with retry.
- `presentation/components/bankLoadStatus.ts` with `Dashboard.tsx:780-798` — INCOMPLETE separated from FAILED without
  blanking confirmed financial data.
- `Dashboard.tsx:866-871` — `'No balance yet'` rather than `$0.00`.
- `Dashboard.tsx:515-519` — accounts without a balance excluded from aggregation rather than zeroed, matching the
  domain spec.
- `CategoryBreakdownChart.tsx:69-72`, `BudgetProgressChart.tsx:90-93` — explicit empty states, which the other two
  charts should copy.

## 7. Not determined

Stated rather than assumed:

- Whether a backend FX rate endpoint exists. Outside this repository; no contract read.
- Whether `CategoryManagementDialog.tsx` and `ActivityLog.tsx` persist server-side or are local-only.
- Whether the authenticated dashboard's rendered appearance matches the code reading — deliberately not verified, since
  reaching it requires Auth0 credentials an agent must not supply.
- Visual comparison against stock shadcn spacing was reasoned from `tailwind.config.ts` rather than diffed against
  upstream sources.
- "22 of 48 vendored primitives unused" is a **lower bound**: each of the 22 named was confirmed to have zero
  importers, but the remaining 26 were not each re-checked, so the true unused count may be higher.

## 8. Corrections applied after review

This record was reviewed adversarially before publication and the following claims were corrected. They are listed
because a register whose value is citation accuracy should show where it was wrong.

- **"Available Space" accounts for obligations after all.** The original text said it accounted for neither budgets nor
  obligations. Obligations *are* deducted upstream at `forecasting.ts:50-56`; only budgets are absent, and
  `calculateForecast` has no parameter for them.
- **Three R1 surfaces are unbuilt, not four.** #23 has been delivered and closed. The count was inherited from issue
  #38's text, which predates that merge — while this very document praises #23's output as the standard to reuse.
- **The resolved-fill measurements were taken with the `dark` class applied**, not in the light theme the surrounding
  text implied. The finding is theme-independent; the stated conditions were wrong.
- **12 independent `formatCurrency` definitions, not 5.**
- **7 raw palette-literal utilities, not 4** (4 in hand-written code, 3 vendored).
- **52 headings excludes the vendored primitives**; 54 including them.
- **23 arbitrary-value utilities in hand-written components**, not the 47 originally stated.
- **Seven `file:line` citations were off by a line or pointed at the wrong block**, including the compliance
  comparison, which cited the retention/audit-readiness functions rather than the two genuinely computed *security*
  checks at `ComplianceDashboard.tsx:56-66`. That error had already been published in issue #43 and was corrected
  there too.
