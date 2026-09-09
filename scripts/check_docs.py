#!/usr/bin/env python3
"""Integrity checks for the documentation corpus.

The docs/ tree is a cross-referenced graph, not a pile of prose. Two of its
invariants cannot be verified by reading, because a violation appears in one file
as a consequence of an edit to a different file:

  1. Every relative link resolves to a file that exists.
  2. Every requirement identifier cited anywhere is defined somewhere.
  3. No requirement identifier is defined twice.
  4. The descriptive layers coin no boundary vocabulary of their own (ADR-012).

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
ADR-012 (documentation layer normativity) is the rule check 4 enforces. It compares
three families of identifier found in the C2, C3 and C4 documents against the
normative contracts: exception class names, the public facade surface reached through
``cc.``, and types appearing in a parameter or return annotation. Those three are the
boundary vocabulary, and they are where the audit found parallel specifications.

A component's own class and method names are not checked. ADR-012 constrains what the
descriptive layers may *define*, not how they decompose a container into parts, and
demanding that every component class appear in a contract would move implementation
detail into the layer that defines the boundary.
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
    """Read a document with line endings normalised.

    Normalisation matters: several checks match multi-line patterns, and the corpus
    mixes LF and CRLF. Without this the fenced-code-block scan in check 4 silently
    matches nothing on CRLF files.
    """
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", errors="replace").replace("\r\n", "\n")


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
        for m in re.finditer(r"^## (FR-[0-9]+)(?:\s+.*)?$", read(path), re.M):
            defined["FR"].add(m.group(1))

    for path in markdown_files(SRS_DIR + "/04-non-functional-requirements"):
        for m in re.finditer(r"^## (NFR-[A-Z]+-[0-9]+)(?:\s+.*)?$", read(path), re.M):
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
        for m in re.finditer(r"^## (FR-[0-9]+)(?:\s+.*)?$", read(path), re.M):
            seen[m.group(1)].append(path)
    for path in markdown_files(SRS_DIR + "/04-non-functional-requirements"):
        for m in re.finditer(r"^## (NFR-[A-Z]+-[0-9]+)(?:\s+.*)?$", read(path), re.M):
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
# Check 4 — the descriptive layers coin no vocabulary (ADR-012)
# ---------------------------------------------------------------------------

CONTRACTS_DIR = "docs/03-technical-contracts"

DESCRIPTIVE_DIRS = [
    "docs/02-design/02-architecture/03-c4-leve2-containers",
    "docs/02-design/02-architecture/05-c4-level4-code",
]

# Names that belong to Python, the standard library or a declared third-party
# dependency. They are not project vocabulary and the contracts do not define them.
FOREIGN_NAMES = {
    # builtins and stdlib
    "ValueError",
    "RuntimeError",
    "ImportError",
    "TypeError",
    "KeyError",
    "FileNotFoundError",
    "NotImplementedError",
    "OSError",
    "AttributeError",
    "FrozenInstanceError",
    "StopIteration",
    # typing and annotations
    "Literal",
    "Optional",
    "Any",
    "Iterator",
    "Iterable",
    "Sequence",
    "Mapping",
    "Callable",
    "Path",
    "Protocol",
    "TypedDict",
    "Union",
    "None",
    "True",
    "False",
    # third-party
    "ArrowIOError",
    "UndefinedError",
    # prose artefacts that look like annotations
    "H1",
    "H2",
    "H3",
    "Wrap",
    "None",
}


def _iter_identifiers(text: str):
    """Yield (family, name) pairs for the three checked families."""
    # exception class names
    for m in re.finditer(r"\b([A-Z][A-Za-z0-9]*Error)\b", text):
        yield "exception", m.group(1)
    # public facade surface
    for m in re.finditer(r"\bcc" + re.escape(".") + r"([a-z_][a-z0-9_]*)\b", text):
        yield "facade", m.group(1)
    # Types crossing a component boundary, that is names used in a parameter or
    # return annotation inside a fenced code block.
    #
    # A component's own class and method names are deliberately NOT checked. Those
    # are internal structure, and ADR-012 constrains vocabulary, not decomposition:
    # requiring every component class to be pre-declared in the contracts would push
    # implementation detail into the layer that defines the boundary. What must come
    # from the contracts is anything a component hands to, or receives from, another.
    for block in re.findall(r"```(?:python)?\n(.*?)```", text, re.S):
        for m in re.finditer(r":\s*([A-Z][A-Za-z0-9]*)\b", block):
            yield "type", m.group(1)
        for m in re.finditer(r"->\s*([A-Z][A-Za-z0-9]*)\b", block):
            yield "type", m.group(1)


CONTAINERS = [
    "PublicApiCli",
    "StudyOrchestrator",
    "ExperimentRunner",
    "AnalysisEngine",
    "ReportingEngine",
    "AlgorithmVisualizationEngine",
    "AlgorithmRegistry",
    "ProblemRepository",
    "ResultsStore",
    "EcosystemBridge",
    "CorvusPilot",
]


def contract_vocabulary() -> set[str]:
    """Every identifier-shaped token in the contracts, plus the C2 container names.

    A component that names a sibling container as a collaborator is citing the C2
    decomposition, not coining vocabulary. C2 is where containers are named, so those
    names are defined even though they do not appear in the contracts.
    """
    vocabulary: set[str] = set(CONTAINERS)
    for path in markdown_files(CONTRACTS_DIR):
        text = read(path)
        for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", text):
            vocabulary.add(m.group(1))
    return vocabulary


BASELINE_PATH = "scripts/docs_baseline.txt"


def load_baseline() -> set[str]:
    """Violations grandfathered in, if any.

    A corpus that predates its own gate cannot always go green on the first run, so
    known violations may be recorded and worked down. The backlog was cleared on
    2026-09-09 and the file is absent; it exists for the next time a check is
    tightened. The baseline may only shrink: an entry that no longer fires is
    reported so it can be deleted.
    """
    if not os.path.exists(BASELINE_PATH):
        return set()
    out = set()
    for line in read(BASELINE_PATH).splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(line)
    return out


def group_declarations(path: str) -> set[str]:
    """Names declared by the component group the document belongs to.

    A type that one component in a container hands to another component in the same
    container is internal structure, not boundary vocabulary. It is legitimate for the
    group to declare it, so long as it is declared somewhere in the group rather than
    merely used. A name that crosses a container boundary has no such declaration and
    must come from the contracts.
    """
    declared: set[str] = set()
    directory = os.path.dirname(path)
    for sibling in markdown_files(directory):
        text = read(sibling)
        for m in re.finditer(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", text):
            declared.add(m.group(1))
        # declaration by prose, the form used throughout the C3 documents:
        #   `LoopResult` fields: ...   /   `RunResult`: `run_id`, `status`, ...
        for m in re.finditer(r"`([A-Z][A-Za-z0-9]*)`(?:\s+fields)?\s*:", text):
            declared.add(m.group(1))
    return declared


def check_vocabulary() -> list[str]:
    problems = []
    vocabulary = contract_vocabulary()
    for directory in DESCRIPTIVE_DIRS:
        if not os.path.isdir(directory):
            continue
        for path in markdown_files(directory):
            text = read(path)
            if ALLOW_MARKER in text:
                continue
            local = group_declarations(path)
            seen: set[str] = set()
            for family, name in _iter_identifiers(text):
                if name in FOREIGN_NAMES or name in vocabulary or name in seen:
                    continue
                if family == "type" and name in local:
                    continue
                seen.add(name)
                problems.append(
                    f"{path}: {family} '{name}' is not defined in {CONTRACTS_DIR} (ADR-012)"
                )
    return problems


# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    if not os.path.isdir(DOCS):
        print("error: run this from the repository root", file=sys.stderr)
        return 2

    files = markdown_files()
    defined = defined_identifiers()

    if "--write-baseline" in argv:
        entries = sorted(check_vocabulary())
        with open(BASELINE_PATH, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Known uncontracted vocabulary, recorded when check 4 was introduced.\n")
            fh.write("# ADR-012 forbids the descriptive layers from coining identifiers.\n")
            fh.write("# This file may only shrink. Delete a line once the name is either\n")
            fh.write("# promoted into docs/03-technical-contracts or removed from the document.\n")
            for entry in entries:
                fh.write(entry + "\n")
        print(f"wrote {len(entries)} baseline entries to {BASELINE_PATH}")
        return 0

    if "--list" in argv:
        for family in sorted(defined):
            print(f"{family}: {' '.join(sorted(defined[family]))}")
        print()

    link_problems = check_links(files)
    id_problems = check_identifiers(files, defined)
    dup_problems = check_duplicate_definitions()
    vocab_all = check_vocabulary()
    baseline = load_baseline()
    vocab_problems = [v for v in vocab_all if v not in baseline]
    stale = sorted(baseline - set(vocab_all))

    for problem in link_problems + id_problems + dup_problems + vocab_problems:
        print(problem)
    for entry in stale:
        print(f"baseline entry no longer fires, delete it: {entry}")

    total = (
        len(link_problems) + len(id_problems) + len(dup_problems) + len(vocab_problems) + len(stale)
    )
    print()
    print(f"{len(files)} files checked")
    print(f"  dead links:             {len(link_problems)}")
    print(f"  undefined identifiers:  {len(id_problems)}")
    print(f"  duplicate definitions:  {len(dup_problems)}")
    print(
        f"  uncontracted vocabulary:{len(vocab_problems):>4}"
        f"   (baselined: {len(vocab_all) - len(vocab_problems)})"
    )
    if stale:
        print(f"  stale baseline entries: {len(stale)}")

    if total:
        print(f"\nFAILED: {total} violation(s)")
        return 1
    print("\nOK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
