# Evidence Archive Convention

Walked runs — founder tests, design reviews, accessibility passes — produce
screenshots that are the evidence for what was observed. This page states where
that evidence lives, how it is named, and the privacy rules that govern it.

The archive itself is the [Evidence Register](../evidence/index.md).

## Why the evidence lives here

The application repositories are **private**, so `raw.githubusercontent.com`
URLs do not render in an issue body for anyone, including their owner. GitHub
offers no token-authenticated attachment upload either: browser drag-and-drop is
the only path, which means evidence can only ever be posted by a human, is
invisible to tooling, and ends up scattered across comment threads with no
index.

This repository publishes to GitHub Pages, so anything committed under `docs/`
gets a stable public URL that renders in issues in **all three** repositories.
That is the mechanism, and this page is the practice built on it.

## Where a run goes

```text
docs/evidence/
  index.md                                    # the register: every run, newest first
  <YYYY-MM-DD>-<feature-slug>-<run-kind>/
    index.md                                  # what the run was, its verdict, its findings
    NN-<surface>-<observation>.<ext>
```

One folder name answers all three questions worth asking of a screenshot —
*when*, *which flow*, *what kind of run*:

| Token | Meaning |
| --- | --- |
| `<YYYY-MM-DD>` | the date the run was walked, not the date it was committed |
| `<feature-slug>` | the **feature label** (`start-your-ledger`, `import-a-statement`, …), so evidence folders and board labels share one vocabulary |
| `<run-kind>` | `founder-test`, `design-review`, `accessibility-pass`, … — what kind of walk this was |

It sorts chronologically in a plain `ls` and in the site nav, and it matches the
house convention already used for dated design notes.

**Folders are flat and date-prefixed, never nested as `<date>/<flow>/`.**
Same-day runs of different flows are rare; *same-flow runs across dates* are the
comparison that actually matters, because a re-walk after fixes is the whole
point. Flat folders put those side by side, and nesting scatters them across
date directories.

### File names

`NN-<surface>-<observation>.<ext>` — the ordinal preserves walk order, so a
folder reads as the story of the run rather than a bag of images.
`08-dashboard-error-new-user.jpg` is self-describing in a search result, in a
diff, and in an issue link.

## Rules

1. **Runs are immutable.** A re-walk gets a new dated folder. Never overwrite
   and never edit an existing run's images — the before/after *is* the evidence.
2. **Synthetic identities only.** No real name, email address, balance, account
   number, IBAN, address, or statement content. This site is **public**; a
   mistake here is a disclosure, not a tidiness problem. Reserved domains
   (`example.com`) and placeholder identities are the standard.
3. **Redaction must be destructive.** Flatten the pixels. Never a black
   rectangle over a layer, never CSS, never a crop that leaves the data in the
   file. If an image cannot be redacted destructively, it does not get
   committed — exclude it and say so in the run's `index.md`.
4. **Every image is referenced from its run's `index.md`** with a caption naming
   the finding it evidences, so an orphan file is visible as an omission rather
   than passing unnoticed.
5. **Prefer PNG for new captures.** Keep whatever format the capture produced
   and leave it otherwise unedited apart from required redaction — never
   re-encode an existing JPEG to PNG, which inflates the file without recovering
   any quality and means the committed bytes are no longer the originals.
6. **Register the run.** Add a row to the
   [Evidence Register](../evidence/index.md) in the same change that adds the
   folder. An unregistered run is an invisible one.

Review every image against rules 2 and 3 **before** it lands, exactly as
`AGENTS.md` §3 requires of every page that enters this repository.

## Linking evidence into an issue

Reference the published URL, not a repository path — a repository path does not
render for a reader of a private repository:

```markdown
![New user's first screen is an error](https://alexandervivas.github.io/expat-ledger-docs/evidence/2026-08-20-start-your-ledger-founder-test/08-dashboard-error-new-user.jpg)
```

The URL is live once the site rebuilds, which happens on push to `main`, on a
daily schedule, and on manual dispatch.
