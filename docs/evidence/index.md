# Evidence Register

Every walked run of an Expat Ledger surface — founder tests, design reviews,
accessibility passes — with the screenshots that evidence what was observed.
Newest first.

The application repositories are private, so their images cannot render in an
issue. These pages are public and stable, which is what makes a screenshot
linkable from an issue in any of the three repositories. The naming convention
and the privacy rules that govern this archive are in
[Evidence Archive Convention](../governance/evidence-archive.md).

Runs are **immutable**: a re-walk gets a new dated folder rather than replacing
an old one, so the before and after stand side by side.

| Run | Date | Feature | Kind | Verdict |
| --- | --- | --- | --- | --- |
| [Start your ledger, end to end (final re-walk)](2026-08-31-start-your-ledger-founder-test-final/index.md) | 2026-08-31 | `start-your-ledger` | Founder test | **Yes** — a real ABN AMRO (NL) account created with its actual IBAN, end to end, with no blocker remaining. No findings. Closes expat-ledger-frontend#142. |
| [Start your ledger, end to end (re-walk)](2026-08-31-start-your-ledger-founder-test-rewalk/index.md) | 2026-08-31 | `start-your-ledger` | Founder test | **Yes, with one new finding** — sign-up/sign-in/tenant-isolation and the ABN AMRO (NL) bank preset (backend#305) all confirmed fixed; a new defect found where the account itself cannot be created with a real IBAN. One finding filed. |
| [Start your ledger, end to end (re-walk)](2026-08-28-start-your-ledger-founder-test-rewalk/index.md) | 2026-08-28 | `start-your-ledger` | Founder test | **Yes, with one new finding** — all ten prior blockers confirmed fixed; a new defect found where two of three corridor bank presets (ABN AMRO, ING — both Netherlands) cannot be created. One finding filed. |
| [Start your ledger, end to end](2026-08-20-start-your-ledger-founder-test/index.md) | 2026-08-20 | `start-your-ledger` | Founder test | **No** — a new user can sign up, sign in and gets a correctly isolated tenant, but the first screen after onboarding is an error rather than their own empty position. Eleven findings filed. |

Each run's page carries its own verdict, the findings it produced, and a caption
against every image naming the finding that image evidences.
