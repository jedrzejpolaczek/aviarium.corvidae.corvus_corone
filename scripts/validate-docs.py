#!/usr/bin/env python3
"""
validate-docs.py — Automated documentation integrity checker for aviarium.corvidae.corvus_corone

Checks:
  1. All internal markdown links resolve to files that exist on disk
  2. Known bad string patterns (monolithic data-format refs, old specs/ paths, etc.)
  3. C3 component breadcrumb correctness
  4. GLOSSARY relative-path depth correctness from inside 01-data-format/

Usage:
    python scripts/validate-docs.py
    python scripts/validate-docs.py --fix-hints   # print suggested replacement for each bad pattern

Exit code: 0 if no issues found, 1 otherwise.
"""

import io
import re
import sys
from pathlib import Path

# Force UTF-8 output on Windows so box-drawing chars and emoji don't crash
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent
DOCS_ROOT = REPO_ROOT / "docs"

# ---------------------------------------------------------------------------
# 1.  Bad string patterns
#     Each entry: (regex, description, hint)
# ---------------------------------------------------------------------------
BAD_PATTERNS = [
    # Monolithic data-format file references (split into individual files)
    (
        r"(?<!/)\bdata-format\.md\b(?![\w/-])",
        "Reference to non-existent monolithic data-format.md",
        "Replace with the appropriate split file under docs/03-technical-contracts/01-data-format/\n"
        "  §2.1 → 02-problem-instance.md  §2.2 → 03-algorithm-instance.md\n"
        "  §2.3 → 04-study.md             §2.4 → 05-experiment.md\n"
        "  §2.5 → 06-run.md               §2.6 → 07-performance-record.md\n"
        "  §2.7 → 08-result-aggregate.md  §2.8 → 09-report.md\n"
        "  §3   → 10-file-formats.md      §4   → 11-interoperability-mappings.md\n"
        "  §5   → 12-cross-entity-validation.md  §6 → 13-schema-versioning.md",
    ),
    # Old specs/ directory (moved to docs/03-technical-contracts/)
    (
        r"\bspecs/",
        "Reference to old specs/ directory (no longer exists)",
        "Replace with docs/03-technical-contracts/02-interface-contracts/, "
        "docs/03-technical-contracts/01-data-format/, or docs/03-technical-contracts/03-metric-taxonomy/",
    ),
    # Wrong C2 containers index filename
    (
        r"01-c2-containers\.md",
        "Reference to non-existent 01-c2-containers.md",
        "Replace with 01-index.md (the C2 containers index)",
    ),
    # Wrong C3 overview filename (old short form)
    (
        r"(?<!\w)01-c3-components\.md(?!\w)",
        "Reference to non-existent 01-c3-components.md",
        "Replace with the correct C3 overview path: "
        "docs/02-design/02-architecture/04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md",
    ),
    # C3 component breadcrumb pattern (wrong relative path)
    (
        r"\.\./01-c3-components\.md",
        "C3 breadcrumb points to non-existent ../01-c3-components.md",
        "Replace with ../01-c4-l3-components/01-c4-l3-components.md",
    ),
    # Non-existent TASKS.md
    (
        r"\bTASKS\.md\b",
        "Reference to docs/05-community/TASKS.md which does not exist",
        "Remove the reference or update to the correct file if created",
    ),
    # SRS at wrong path (old root-level srs.md) — excludes 01-SRS.md (the correct filename)
    (
        r"(?<![/\w\d-])(?:srs|SRS)\.md(?!\w)",
        "Reference to old srs.md / SRS.md without correct path",
        "Replace with docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md",
    ),
    # Old single use-cases file
    (
        r"01-use-cases\.md\b",
        "Reference to old monolithic 01-use-cases.md",
        "Replace with 01-index.md (the use-cases index)",
    ),
    # Wrong GLOSSARY relative depth from inside 01-data-format/ (one ../ too few)
    (
        r"(?<=01-data-format/)(?:\.\./)GLOSSARY\.md",
        "GLOSSARY link from inside 01-data-format/ uses wrong relative depth (../GLOSSARY.md)",
        "Replace with ../../GLOSSARY.md",
    ),
    # Old c1-context wrong path (missing level directories)
    (
        r"02-c4-leve1-context/01-c1-context\.md",
        "C1 context path missing intermediate directories",
        "Replace with docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md",
    ),
    # Wrong old-style c1 context path (pre-renaming)
    (
        r"02-c1-context\.md\b",
        "Reference to old 02-c1-context.md (renamed with C4 level prefix)",
        "Replace with docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md",
    ),
]

# ---------------------------------------------------------------------------
# 2.  FR label consistency map
#     Authoritative descriptions from the FR definition files.
#     Used to detect wrong labels in C2 container files.
# ---------------------------------------------------------------------------
FR_CANONICAL = {
    "FR-01": "store ProblemInstance with required fields",
    "FR-02": "reject ProblemInstance missing required fields",
    "FR-03": "version ProblemInstance on update",
    "FR-04": "deprecate ProblemInstance without deletion",
    "FR-05": "store AlgorithmInstance with 13 required fields",
    "FR-06": "reject unpinned code_reference",
    "FR-07": "store configuration_justification",
    "FR-08": "enforce pre-registration gate — lock Study fields before Run execution",
    "FR-09": "assign all Run seeds from declared seed_strategy",
    "FR-10": "record full execution environment (OS, hardware, Python version, dependencies)",
    "FR-11": "enforce Run isolation — no shared mutable state between Runs",
    "FR-12": "record failed Run with failure_reason, not silently skip",
    "FR-13": "compute all four Standard Reporting Set metrics per (problem, algorithm) pair",
    "FR-14": "record PerformanceRecords at log-scale + improvement schedule for anytime curves",
    "FR-15": "enforce all three analysis levels (exploratory, confirmatory, practical significance)",
    "FR-16": "apply multiple-testing correction when >1 hypothesis; include adjusted p-values in report",
    "FR-17": "every entity carries a UUID; no file paths as entity identifiers",
    "FR-18": "produce Artifact archive for any completed Experiment",
    "FR-19": "cross-entity references use entity IDs only — no file paths",
    "FR-20": "generate HTML Researcher and Practitioner reports",
    "FR-21": "include mandatory limitations section in every report",
    "FR-22": "export report data in open formats",
    "FR-23": "support export in at least one external benchmark platform format",
    "FR-24": "generate information-loss manifest before producing any export file",
    "FR-25": "reject unsupported export format requests with informative error",
    "FR-26": "include information-loss manifest in export output",
    "FR-27": "produce algorithm visualizations (search trajectory, heatmap, genealogy, animation)",
    "FR-28": "Corvus Pilot answers Learner questions using study data and algorithm documentation",
    "FR-29": "Corvus Pilot Socratic mode guides Learner via questions, not direct answers",
    "FR-30": "present algorithm genealogy (historical lineage) on request",
    "FR-31": "produce Learner-scoped summary from completed study on request",
    "FR-32": "validate minimum 5 Problem Instances per Study (D-1 diversity rule)",
    "FR-33": "validate dimensionality and noise coverage diversity (D-2, D-3 rules)",
}

# ---------------------------------------------------------------------------
# 3.  Known wrong FR labels found in C2 container files
#     Format: (file_relative, fr_id, wrong_description_fragment)
#     The script searches for these exact patterns and flags them.
# ---------------------------------------------------------------------------
WRONG_FR_LABELS = [
    # 07-study-orchestrator.md
    ("03-c4-leve2-containers/07-study-orchestrator.md", "FR-10", "run isolation"),
    ("03-c4-leve2-containers/07-study-orchestrator.md", "FR-17", "locking and immutability"),
    ("03-c4-leve2-containers/07-study-orchestrator.md", "FR-18", "resume interrupted experiments"),
    ("03-c4-leve2-containers/07-study-orchestrator.md", "FR-19", "execution environment capture"),
    # 08-experiment-runner.md
    ("03-c4-leve2-containers/08-experiment-runner.md", "FR-10", "run isolation"),
    ("03-c4-leve2-containers/08-experiment-runner.md", "FR-11", "evaluation budget enforcement"),
    ("03-c4-leve2-containers/08-experiment-runner.md", "FR-19", "execution environment capture"),
    # 09-analysis-engine.md
    ("03-c4-leve2-containers/09-analysis-engine.md", "FR-14", "statistical tests"),
    ("03-c4-leve2-containers/09-analysis-engine.md", "FR-15", "scoped conclusions"),
    # 12-results-store.md
    ("03-c4-leve2-containers/12-results-store.md", "FR-17", "immutability and locking"),
    ("03-c4-leve2-containers/12-results-store.md", "FR-18", "resume interrupted experiments"),
    ("03-c4-leve2-containers/12-results-store.md", "FR-19", "execution environment capture"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def iter_md_files():
    for path in sorted(DOCS_ROOT.rglob("*.md")):
        yield path


def extract_links(text):
    """Return list of (link_text, raw_target) for all markdown links in text.
    Skips links inside backtick code spans to avoid false positives."""
    # Remove inline code spans before extracting links
    text_no_code = re.sub(r"`[^`]*`", lambda m: " " * len(m.group()), text)
    return re.findall(r"\[([^\]]*)\]\(([^)]+)\)", text_no_code)


def is_external(target):
    return (
        target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
    )


def resolve_link(source_file: Path, target: str) -> Path | None:
    """Resolve a relative markdown link to an absolute path, stripping anchors."""
    target = target.split("#")[0].strip()
    if not target:
        return None  # anchor-only link
    if is_external(target):
        return None
    if target.startswith("/"):
        return REPO_ROOT / target.lstrip("/")
    return (source_file.parent / target).resolve()


# ---------------------------------------------------------------------------
# Check passes
# ---------------------------------------------------------------------------


def check_links(issues):
    for md_file in iter_md_files():
        text = md_file.read_text(encoding="utf-8", errors="replace")
        for _link_text, raw_target in extract_links(text):
            if is_external(raw_target):
                continue
            resolved = resolve_link(md_file, raw_target)
            if resolved is None:
                continue
            if not resolved.exists():
                rel_file = md_file.relative_to(REPO_ROOT)
                rel_target = raw_target.split("#")[0]
                issues.append(
                    {
                        "category": "LINK",
                        "file": str(rel_file),
                        "detail": f"Broken link → {rel_target}  (resolved: {resolved})",
                    }
                )


def check_bad_patterns(issues):
    for md_file in iter_md_files():
        text = md_file.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        rel_file = str(md_file.relative_to(REPO_ROOT))
        for pattern, description, hint in BAD_PATTERNS:
            for lineno, line in enumerate(lines, 1):
                # Skip HTML comment lines for pattern checks that are cosmetic-only
                # (CONNECTS TO blocks are informational; broken links are still reported)
                if re.search(pattern, line):
                    issues.append(
                        {
                            "category": "PATTERN",
                            "file": rel_file,
                            "line": lineno,
                            "detail": description,
                            "hint": hint,
                            "excerpt": line.strip()[:120],
                        }
                    )


def check_fr_labels(issues):
    """Check for known wrong FR label descriptions in C2 container files."""
    for rel_path, fr_id, wrong_fragment in WRONG_FR_LABELS:
        full_path = DOCS_ROOT / "02-design/02-architecture" / rel_path
        if not full_path.exists():
            continue
        text = full_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        for lineno, line in enumerate(lines, 1):
            # Check that the wrong fragment appears right after fr_id "(", not elsewhere on the line
            if re.search(
                re.escape(fr_id) + r"\s*\(" + re.escape(wrong_fragment), line, re.IGNORECASE
            ):
                correct = FR_CANONICAL.get(fr_id, "see FR definition file")
                issues.append(
                    {
                        "category": "FR_LABEL",
                        "file": str(full_path.relative_to(REPO_ROOT)),
                        "line": lineno,
                        "detail": (
                            f"{fr_id} is labeled '{wrong_fragment}' — wrong. "
                            f"Correct: {fr_id} = {correct}"
                        ),
                        "excerpt": line.strip()[:120],
                    }
                )


def check_glossary_depth(issues):
    """
    Files inside docs/03-technical-contracts/01-data-format/ that link to
    ../GLOSSARY.md resolve to docs/03-technical-contracts/GLOSSARY.md (wrong).
    Correct is ../../GLOSSARY.md.
    """
    data_format_dir = DOCS_ROOT / "03-technical-contracts" / "01-data-format"
    for md_file in data_format_dir.glob("*.md"):
        text = md_file.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            # Match ../GLOSSARY.md but NOT ../../GLOSSARY.md (the correct depth)
            if re.search(r"(?<![./])\.\.\/GLOSSARY\.md", line):
                issues.append(
                    {
                        "category": "GLOSSARY_DEPTH",
                        "file": str(md_file.relative_to(REPO_ROOT)),
                        "line": lineno,
                        "detail": "GLOSSARY link ../GLOSSARY.md resolves to non-existent "
                        "docs/03-technical-contracts/GLOSSARY.md; correct is ../../GLOSSARY.md",
                        "excerpt": line.strip()[:120],
                    }
                )


def check_c3_breadcrumbs(issues):
    """
    C3 component 01-index.md files use breadcrumb:
      > C3 Index: [../01-c3-components.md](../01-c3-components.md)
    This resolves to e.g. 04-c4-leve3-components/03-experiment-runner/01-c3-components.md
    which does not exist.  Correct: ../01-c4-l3-components/01-c4-l3-components.md
    """
    c3_root = DOCS_ROOT / "02-design" / "02-architecture" / "04-c4-leve3-components"
    for md_file in c3_root.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            if re.search(r"\.\./01-c3-components\.md", line):
                issues.append(
                    {
                        "category": "C3_BREADCRUMB",
                        "file": str(md_file.relative_to(REPO_ROOT)),
                        "line": lineno,
                        "detail": "C3 breadcrumb ../01-c3-components.md resolves to non-existent file",
                        "hint": "Replace with ../01-c4-l3-components/01-c4-l3-components.md",
                        "excerpt": line.strip()[:120],
                    }
                )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    issues = []

    print("Running docs validation checks…\n")
    print(f"  Docs root : {DOCS_ROOT}")
    print(f"  MD files  : {sum(1 for _ in iter_md_files())}")
    print()

    check_links(issues)
    check_bad_patterns(issues)
    check_fr_labels(issues)
    check_glossary_depth(issues)
    check_c3_breadcrumbs(issues)

    if not issues:
        print("✓ No issues found.")
        return 0

    # Group by category
    by_cat = {}
    for issue in issues:
        by_cat.setdefault(issue["category"], []).append(issue)

    cat_labels = {
        "LINK": "Broken internal links",
        "PATTERN": "Bad string patterns (monolithic refs, old paths)",
        "FR_LABEL": "Wrong FR label descriptions in C2 container files",
        "GLOSSARY_DEPTH": "Wrong GLOSSARY relative path depth",
        "C3_BREADCRUMB": "Wrong C3 component breadcrumb",
    }

    total = 0
    for cat, label in cat_labels.items():
        cat_issues = by_cat.get(cat, [])
        if not cat_issues:
            continue
        print(f"── {label} ({len(cat_issues)}) ──────────────────────────────────────")
        for i, issue in enumerate(cat_issues, 1):
            loc = issue["file"]
            if "line" in issue:
                loc += f":{issue['line']}"
            print(f"  [{i:03d}] {loc}")
            print(f"        {issue['detail']}")
            if "excerpt" in issue:
                print(f"        ↳ {issue['excerpt']}")
            if "hint" in issue:
                for hint_line in issue["hint"].splitlines():
                    print(f"        💡 {hint_line}")
            print()
        total += len(cat_issues)

    print(f"{'─' * 60}")
    print(f"  Total issues: {total}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
