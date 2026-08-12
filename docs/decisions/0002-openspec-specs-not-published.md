# 0002 — OpenSpec capability specs are not published on the site

**Date:** 2026-08-12 · **Status:** Accepted · **Issue:** [#1](https://github.com/alexandervivas/expat-ledger-docs/issues/1)

## Context

Issue #1 originally listed promoted OpenSpec capability specs alongside
contracts and ADRs as material to pull onto the site at build time. Both
application repositories carry them: 23 in backend, 16 in frontend.

Under the hybrid model's own test — does it change in lockstep with a commit? —
specs clearly stay with the code. But that test only settles *where a document
lives*, not *whether the site renders it*. Contracts and ADRs live with the
code too, and they are published.

## Decision

The site does not aggregate `openspec/specs/`. It aggregates contracts and ADRs
only.

The deciding test is **consumption locus**: where is the reader standing when
they need this document?

- A **contract** is read by someone outside the repository that owns it — a
  frontend developer integrating against the backend's OpenAPI. They may never
  clone it.
- An **ADR** is read by someone who wants the *why*, often without cloning
  anything.
- A **capability spec** is only ever read by an agent or a contributor who is
  already inside that repository, mid-workflow, with the file open on disk. A
  website adds nothing to that transaction.

Specs fail the test that the other two pass. OpenSpec is workflow machinery,
consumed inside the workflow.

## Rejected reasoning

Two tempting arguments were checked and dropped, and are recorded here so they
are not re-litigated:

- *"Specs churn too hard for a published site."* Measured over 90 days in
  backend: `openspec/specs` 11 commits, `docs/architecture/decisions` 11
  commits. Specs and ADRs churn identically. The argument is false.
- *"Specs are too unpolished to publish"* — 19 of the 39 carry a `TBD` Purpose.
  True, but this is a reason to fix them upstream, not a reason for the docs
  site to decide what is fit to exist. Publication quality is the owning
  repository's concern.

## Consequences

- Acceptance criterion 2 of issue #1 was amended to drop "and specs".
- Requirement-to-capability traceability is not available on the site. The
  [traceability matrix](../requirements/TRACEABILITY.md) remains the published
  view of that mapping.
- If specs later acquire an outside-the-repo audience, this note is what should
  be revisited.
