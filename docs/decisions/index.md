# Site Decisions

Short notes recording structural decisions about this documentation site — how
it is assembled, what it navigates, and where it is hosted.

This repository deliberately does not use ADR tooling or OpenSpec. Decisions
about the *product* are recorded as ADRs in the application repositories and
render under [Reference](../reference/SUMMARY.md); decisions about the *site*
live here.

| Note | Decision |
| --- | --- |
| [0001](0001-aggregation-mechanism.md) | Code-adjacent trees are vendored at build time by a script, not by a plugin or submodule |
| [0002](0002-openspec-specs-not-published.md) | OpenSpec capability specs are not published on the site |
| [0003](0003-no-openspec-in-this-repository.md) | This repository does not adopt OpenSpec for its own workflow |
