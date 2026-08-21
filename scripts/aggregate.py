#!/usr/bin/env python3
"""Pull the code-adjacent documentation trees from the application repositories.

Contracts and ADRs stay authoritative in `expat-ledger-backend` and
`expat-ledger-frontend`; this script vendors them into `docs/reference/` at
build time so the site can render them without this repository ever owning a
copy. `docs/reference/` is gitignored — see `docs/decisions/`.

Run it before every build, locally and in CI:

    python scripts/aggregate.py && mkdocs build --strict
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCE_DIR = REPO_ROOT / "docs" / "reference"

# Fenced-code language by file extension, for the wrapper pages that make
# non-markdown contract artifacts render instead of merely download.
CODE_LANGUAGES = {
    ".avsc": "json",
    ".proto": "protobuf",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
}


@dataclass(frozen=True)
class Tree:
    """One subtree copied from a source repository into the site."""

    source_path: str
    dest_path: str
    title: str
    # Literal (old, new) link rewrites applied to markdown in this tree.
    # Links that escape the vendored tree would otherwise dangle; each rule is
    # written out explicitly so an upstream move fails the strict build loudly
    # rather than being silently patched by a regex.
    link_rewrites: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Source:
    """One application repository contributing trees to the site."""

    name: str
    title: str
    repo_url: str
    ref: str
    trees: list[Tree] = field(default_factory=list)


SOURCES = [
    Source(
        name="backend",
        title="Backend",
        repo_url="https://github.com/alexandervivas/expat-ledger-backend.git",
        ref="main",
        trees=[
            Tree("docs/architecture/decisions", "backend/decisions", "Architecture Decisions"),
            Tree("docs/contracts", "backend/contracts", "Contracts"),
        ],
    ),
    Source(
        name="frontend",
        title="Frontend",
        repo_url="https://github.com/alexandervivas/expat-ledger-frontend.git",
        ref="main",
        trees=[
            Tree(
                "docs/architecture/decisions",
                "frontend/decisions",
                "Architecture Decisions",
                link_rewrites=(
                    # These narratives migrated into this repository; the ADRs'
                    # sibling-relative links no longer resolve upstream.
                    (
                        "](../design-direction-audit.md)",
                        "](/architecture/frontend/design-direction-audit.md)",
                    ),
                    (
                        "](../backend-authoritative-tenant-membership.md)",
                        "](/architecture/frontend/backend-authoritative-tenant-membership.md)",
                    ),
                ),
            ),
        ],
    ),
]


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)


def fetch(source: Source, workdir: Path) -> Path:
    """Shallow, blobless, sparse checkout of only the trees we need."""
    checkout = workdir / source.name
    run(
        [
            "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
            "--branch", source.ref, source.repo_url, str(checkout),
        ]
    )
    run(["git", "sparse-checkout", "set", *(t.source_path for t in source.trees)], cwd=checkout)
    return checkout


def title_of(markdown_file: Path) -> str:
    """First H1 of a page, falling back to its filename."""
    for line in markdown_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return markdown_file.stem


def wrap_non_markdown(path: Path) -> None:
    """Render a contract artifact as a page instead of a bare download.

    The raw artifact is left in place so it stays downloadable. The wrapper
    cannot be named `<file>.md`: mkdocs renders that to a *directory* named
    `<file>`, which collides with the raw file itself. Flattening the dot
    (`account-created.avsc` -> `account-created-avsc.md`) keeps both.
    """
    language = CODE_LANGUAGES.get(path.suffix, "")
    body = path.read_text(encoding="utf-8")
    page = path.with_name(path.name.replace(".", "-") + ".md")
    page.write_text(
        f"# {path.name}\n\n"
        f"Authoritative source: `{path.name}` in the application repository — "
        f"this page is generated at build time. "
        f"[Download the raw file]({path.name}).\n\n"
        f"```{language}\n{body}\n```\n",
        encoding="utf-8",
    )


def vendor(source: Source, checkout: Path) -> None:
    for tree in source.trees:
        origin = checkout / tree.source_path
        if not origin.is_dir():
            raise SystemExit(f"{source.name}: expected tree {tree.source_path} is missing upstream")

        destination = REFERENCE_DIR / tree.dest_path
        shutil.copytree(origin, destination)

        for path in sorted(destination.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix == ".md":
                if tree.link_rewrites:
                    text = path.read_text(encoding="utf-8")
                    for old, new in tree.link_rewrites:
                        text = text.replace(old, new)
                    path.write_text(text, encoding="utf-8")
            elif path.suffix in CODE_LANGUAGES:
                wrap_non_markdown(path)


def nav_lines(directory: Path, depth: int) -> list[str]:
    """Render one directory as nested mkdocs-literate-nav list items.

    Pages sort with `index.md` first, then alphabetically; subdirectories
    follow as unlinked section headings.
    """
    indent = "    " * depth
    lines: list[str] = []

    pages = sorted(
        (p for p in directory.iterdir() if p.is_file() and p.suffix == ".md"),
        key=lambda p: (p.name != "index.md", p.name.lower()),
    )
    for page in pages:
        href = page.relative_to(REFERENCE_DIR).as_posix()
        lines.append(f"{indent}* [{title_of(page)}]({href})")

    for subdirectory in sorted(d for d in directory.iterdir() if d.is_dir()):
        lines.append(f"{indent}* {subdirectory.name}")
        lines.extend(nav_lines(subdirectory, depth + 1))

    return lines


def write_summary() -> None:
    """Generate the literate-nav SUMMARY consumed by mkdocs.yml.

    Generating the nav is what keeps `--strict` honest: a new upstream ADR
    appears in the navigation automatically instead of becoming an orphan page
    that fails the build.
    """
    lines: list[str] = []
    for source in SOURCES:
        lines.append(f"* {source.title}")
        for tree in source.trees:
            lines.append(f"    * {tree.title}")
            lines.extend(nav_lines(REFERENCE_DIR / tree.dest_path, depth=2))

    (REFERENCE_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    if REFERENCE_DIR.exists():
        shutil.rmtree(REFERENCE_DIR)
    REFERENCE_DIR.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for source in SOURCES:
            print(f"aggregating {source.name} @ {source.ref}", file=sys.stderr)
            vendor(source, fetch(source, workdir))

    write_summary()

    pages = sum(1 for _ in REFERENCE_DIR.rglob("*.md"))
    print(f"aggregated {pages} pages into docs/reference/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as error:
        print(f"command failed: {' '.join(error.cmd)}\n{error.stderr}", file=sys.stderr)
        sys.exit(1)
