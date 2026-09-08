#!/usr/bin/env python3
"""Integrity checks for the documentation corpus.

The docs/ tree is a cross-referenced graph, not a pile of prose. Two of its
invariants cannot be verified by reading, because a violation appears in one file
as a consequence of an edit to a different file:

  1. Every relative link resolves to a file that exists.
  2. Every requirement identifier cited anywhere is defined somewhere.
  3. No requirement identifier is defined twice.

A file may opt out of the identifier checks by carrying the marker
``<!-- check-docs: allow-undefined -->``. This is for documents that legitimately
quote identifiers as evidence, such as the ADR template and the ADR that records
which invented identifiers were removed.

Both are checked here. Run from the repository root:

    python scripts/check_docs.py          # report and exit non-zero on failure
    python scripts/check_docs.py --list   # also list every defined identifier

Exit codes: 0 clean, 1 violations found, 2 usage error.

References
----------
ADR-012 (documentation layer normativity) is the rule this script will eventually
enforce in full; the vocabulary check that verifies the descriptive layer coins no
new identifiers is deliberately not implemented yet. See audit-2026-09-08.md.
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

DOCS = "docs"
MANIFESTO = "docs/01-manifesto/MANIFESTO.md"
SRS_DIR = "docs/02-design/01-software-requirement-specification"
ADR_DIR = "docs/02-design/02-architecture/01-adr"
METRICS_DIR = "docs/03-technical-contracts/03-metric-taxonomy"

LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def markdown_files(root: str = DOCS) -> list[str]:
    out = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".md"):
                out.append(os.path.join(dirpath, name).replace(os.sep, "/"))
    return sorted(out)


def read(path: str) -> str:
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Check 1 — relative links resolve
# ---------------------------------------------------------------------------


def check_links(files: list[str]) -> list[str]:
    problems = []
    for path in files:
        source_dir = os.path.dirname(path)
        for match in LINK.finditer(read(path)):
            target = match.group(2)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#")[0]
            if not target:
                continue
            resolved = os.path.normpath(os.path.join(source_dir, target))
            if not os.path.exists(resolved):
                problems.append(f"{path}: dead link -> {target}")
    return problems


# ---------------------------------------------------------------------------
# Check 2 — cited identifiers are defined
# ---------------------------------------------------------------------------

CITE_PATTERNS = {
    "FR": re.compile(r"\bFR-(?:[0-9]+|[A-Z]+-[0-9]+)\b"),
    "NFR": re.compile(r"\bNFR-[A-Z]+-[0-9]+\b"),
    "UC": re.compile(r"\bUC-[0-9]+\b"),
    "ADR": re.compile(r"\bADR-[0-9]+\b"),
    "AP": re.compile(r"\bAP-[0-9]+\b"),
    "CONST": re.compile(r"\bCONST-[A-Z]+-[0-9]+\b"),
    "METRIC": re.compile(r"\b(?:QUALITY|TIME|RELIABILITY|ROBUSTNESS|ANYTIME)-[A-Z_]+\b"),
}


def defined_identifiers() -> dict[str, set[str]]:
    """Harvest each identifier family from the file that is authoritative for it."""
    defined: dict[str, set[str]] = defaultdict(set)

    for path in markdown_files(SRS_DIR + "/03-functional-requirements"):
        for m in re.finditer(r"^## (FR-[0-9]+)\s*$", read(path), re.M):
            defined["FR"].add(m.group(1))

    for path in markdown_files(SRS_DIR + "/04-non-functional-requirements"):
        for m in re.finditer(r"^## (NFR-[A-Z]+-[0-9]+)\s*$", read(path), re.M):
            defined["NFR"].add(m.group(1))

    index = os.path.join(SRS_DIR, "02-use-cases", "01-index.md")
    if os.path.exists(index):
        for m in re.finditer(r"^\|\s*(UC-[0-9]+)\s*\|", read(index), re.M):
            defined["UC"].add(m.group(1))

    for name in os.listdir(ADR_DIR):
        m = re.match(r"^adr-([0-9]+)-", name)
        if m:
            defined["ADR"].add("ADR-" + m.group(1))

    if os.path.exists(MANIFESTO):
        for m in re.finditer(r"^\|\s*(AP-[0-9]+)\s*\|", read(MANIFESTO), re.M):
            defined["AP"].add(m.group(1))

    for path in markdown_files(SRS_DIR + "/05-constraints"):
        for m in re.finditer(r"\b(CONST-[A-Z]+-[0-9]+)\b", read(path)):
            defined["CONST"].add(m.group(1))

    for path in markdown_files(METRICS_DIR):
        text = read(path)
        for m in re.finditer(
            r"^#+ .*?\b((?:QUALITY|TIME|RELIABILITY|ROBUSTNESS|ANYTIME)-[A-Z_]+)", text, re.M
        ):
            defined["METRIC"].add(m.group(1))
        for m in re.finditer(
            r"^\*\*Metric ID:\*\*\s*`?((?:QUALITY|TIME|RELIABILITY|ROBUSTNESS|ANYTIME)-[A-Z_]+)",
            text,
            re.M,
        ):
            defined["METRIC"].add(m.group(1))

    return defined


ALLOW_MARKER = "<!-- check-docs: allow-undefined -->"


def check_duplicate_definitions() -> list[str]:
    """A requirement identifier defined in two places is worse than one defined
    nowhere: both definitions look authoritative and citations are ambiguous."""
    problems = []
    seen: dict[str, list[str]] = defaultdict(list)
    for path in markdown_files(SRS_DIR + "/03-functional-requirements"):
        for m in re.finditer(r"^## (FR-[0-9]+)\s*$", read(path), re.M):
            seen[m.group(1)].append(path)
    for path in markdown_files(SRS_DIR + "/04-non-functional-requirements"):
        for m in re.finditer(r"^## (NFR-[A-Z]+-[0-9]+)\s*$", read(path), re.M):
            seen[m.group(1)].append(path)
    for identifier, paths in sorted(seen.items()):
        if len(paths) > 1:
            problems.append(f"{identifier}: defined in {len(paths)} files: {', '.join(paths)}")
    return problems


def check_identifiers(files: list[str], defined: dict[str, set[str]]) -> list[str]:
    problems = []
    for path in files:
        text = read(path)
        if ALLOW_MARKER in text:
            continue
        # LaTeX escapes underscores, which would otherwise split a metric
        # identifier in two and report the prefix as undefined.
        text = text.replace(chr(92) + "_", "_")
        for family, pattern in CITE_PATTERNS.items():
            known = defined.get(family, set())
            if not known:
                continue
            for m in pattern.finditer(text):
                cited = m.group(0)
                if cited not in known:
                    problems.append(f"{path}: undefined {family} identifier {cited}")
    return problems


# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    if not os.path.isdir(DOCS):
        print("error: run this from the repository root", file=sys.stderr)
        return 2

    files = markdown_files()
    defined = defined_identifiers()

    if "--list" in argv:
        for family in sorted(defined):
            print(f"{family}: {' '.join(sorted(defined[family]))}")
        print()

    link_problems = check_links(files)
    id_problems = check_identifiers(files, defined)
    dup_problems = check_duplicate_definitions()

    for problem in link_problems + id_problems + dup_problems:
        print(problem)

    total = len(link_problems) + len(id_problems) + len(dup_problems)
    print()
    print(f"{len(files)} files checked")
    print(f"  dead links:             {len(link_problems)}")
    print(f"  undefined identifiers:  {len(id_problems)}")
    print(f"  duplicate definitions:  {len(dup_problems)}")

    if total:
        print(f"\nFAILED: {total} violation(s)")
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
