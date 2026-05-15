#!/usr/bin/env python3
"""
fix-docs.py — Apply all mechanical documentation fixes for aviarium.corvidae.corvus_corone

Run this script, then run validate-docs.py to verify zero issues remain.

Exit code: 0 if changes made or no changes needed, non-zero on error.
"""

import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent
DOCS_ROOT = REPO_ROOT / "docs"

changes = 0


def patch(path: Path, old: str, new: str, count: int = -1) -> bool:
    """Replace `old` with `new` in `path`. Returns True if changed."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if old not in text:
        return False
    new_text = text.replace(old, new, count) if count > 0 else text.replace(old, new)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def patch_re(path: Path, pattern: str, replacement: str, flags: int = 0) -> bool:
    """Regex replace in `path`. Returns True if changed."""
    text = path.read_text(encoding="utf-8", errors="replace")
    new_text = re.sub(pattern, replacement, text, flags=flags)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def report(path: Path, changed: bool, what: str = "") -> None:
    global changes
    if changed:
        changes += 1
        rel = path.relative_to(REPO_ROOT)
        print(f"  fixed  {rel}" + (f"  [{what}]" if what else ""))


# ---------------------------------------------------------------------------
# Data format section-to-split-file map
# ---------------------------------------------------------------------------
# Ordered longest-match first so §2.2.1 matches before §2.2
SECTION_MAP = [
    ("§2.2.1",  "03-algorithm-instance.md"),
    ("§2.1",    "02-problem-instance.md"),
    ("§2.2",    "03-algorithm-instance.md"),
    ("§2.3",    "04-study.md"),
    ("§2.4",    "05-experiment.md"),
    ("§2.5",    "06-run.md"),
    ("§2.6",    "07-performance-record.md"),
    ("§2.7",    "08-result-aggregate.md"),
    ("§2.8",    "09-report.md"),
    ("§3",      "10-file-formats.md"),
    ("§4",      "11-interoperability-mappings.md"),
    ("§5",      "12-cross-entity-validation.md"),
    ("§6",      "13-schema-versioning.md"),
    ("§1",      "01-index.md"),
]
DATA_FORMAT_DIR = "docs/03-technical-contracts/01-data-format"


def resolve_data_format_section(section: str) -> str:
    """Return the split-file name for a data-format section reference."""
    for sec, fname in SECTION_MAP:
        if section.startswith(sec):
            return fname
    return "01-index.md"


def replace_data_format_ref(text: str) -> str:
    """
    Replace all data-format.md §X.Y references with specific split-file references.
    Handles the following prefix patterns:
      - 'data-format.md §X.Y'
      - 'docs/03-technical-contracts/01-data-format.md §X.Y'
      - '01-data-format.md §X.Y'
      - 'specs/data-format.md §X.Y'
    References without a section are replaced with the index file.
    """
    # Pattern: optional prefix + data-format.md + optional section
    # We build replacement text that includes the full data-format dir path
    def _replace(m: re.Match) -> str:
        section_part = m.group("section") or ""
        section_part = section_part.strip()
        fname = resolve_data_format_section(section_part) if section_part else "01-index.md"
        return f"{DATA_FORMAT_DIR}/{fname}"

    # Variants with specific section §X[.Y[.Z]]
    patterns = [
        # Full path with section
        r"docs/03-technical-contracts/01-data-format\.md\s*(?P<section>§[\d.]+)",
        # specs/ path with section
        r"specs/data-format\.md\s*(?P<section>§[\d.]+)",
        # bare with section (no path prefix)
        r"(?<![/\w])data-format\.md\s*(?P<section>§[\d.]+)",
        # 01-data-format.md with section
        r"01-data-format\.md\s*(?P<section>§[\d.]+)",
        # Full path without section
        r"docs/03-technical-contracts/01-data-format\.md(?!\s*§)(?P<section>)",
        # specs/ without section
        r"specs/data-format\.md(?!\s*§)(?P<section>)",
        # bare without section (no path prefix, no following section)
        r"(?<![/\w])data-format\.md(?!\s*§)(?P<section>)",
        # 01-data-format.md without section
        r"01-data-format\.md(?!\s*§)(?P<section>)",
    ]
    for pat in patterns:
        text = re.sub(pat, _replace, text)
    return text


# ---------------------------------------------------------------------------
# 1. GLOSSARY depth: ../GLOSSARY.md → ../../GLOSSARY.md
#    Files: docs/03-technical-contracts/01-data-format/*.md
# ---------------------------------------------------------------------------
print("\n[1] GLOSSARY depth in 01-data-format/")
for md in (DOCS_ROOT / "03-technical-contracts" / "01-data-format").glob("*.md"):
    changed = patch(md, "../GLOSSARY.md", "../../GLOSSARY.md")
    report(md, changed, "GLOSSARY depth")


# ---------------------------------------------------------------------------
# 2. C3 sub-component back-links: (index.md) → (01-index.md)
#    Files: all *.md under 04-c4-leve3-components/XX-name/ except 01-index.md itself
# ---------------------------------------------------------------------------
print("\n[2] C3 sub-component index.md → 01-index.md")
c3_root = DOCS_ROOT / "02-design" / "02-architecture" / "04-c4-leve3-components"
for md in c3_root.rglob("*.md"):
    if md.name == "01-index.md":
        continue
    if md.parent == c3_root:
        continue
    # Replace link targets (index.md) but not filenames in text prose
    changed = patch(md, "(index.md)", "(01-index.md)")
    report(md, changed, "C3 sub-component back-link")


# ---------------------------------------------------------------------------
# 3. C3 overview links: XX-name/index.md → XX-name/01-index.md
#    File: 04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md
# ---------------------------------------------------------------------------
print("\n[3] C3 overview XX/index.md → XX/01-index.md")
c3_overview = c3_root / "01-c4-l3-components" / "01-c4-l3-components.md"
if c3_overview.exists():
    changed = patch_re(c3_overview, r"(\d{2}-[^/]+)/index\.md\b", r"\1/01-index.md")
    report(c3_overview, changed, "C3 overview links")


# ---------------------------------------------------------------------------
# 4. C3 breadcrumbs: ../01-c3-components.md → ../01-c4-l3-components/01-c4-l3-components.md
#    Files: all 01-index.md under 04-c4-leve3-components/XX-name/
# ---------------------------------------------------------------------------
print("\n[4] C3 breadcrumbs")
for md in c3_root.rglob("01-index.md"):
    if md.parent == c3_root:
        continue
    changed = patch(
        md,
        "../01-c3-components.md",
        "../01-c4-l3-components/01-c4-l3-components.md",
    )
    report(md, changed, "C3 breadcrumb")


# ---------------------------------------------------------------------------
# 5. Interface-contracts breadcrumbs: 01-interface-contracts.md → 01-index.md
#    Files: docs/03-technical-contracts/02-interface-contracts/*.md
# ---------------------------------------------------------------------------
print("\n[5] Interface-contracts breadcrumbs")
ic_dir = DOCS_ROOT / "03-technical-contracts" / "02-interface-contracts"
for md in ic_dir.glob("*.md"):
    changed = patch(md, "01-interface-contracts.md", "01-index.md")
    report(md, changed, "IC breadcrumb")


# ---------------------------------------------------------------------------
# 6. Metric taxonomy breadcrumbs: 01-metric-taxonomy.md → 01-index.md
#    Files: docs/03-technical-contracts/03-metric-taxonomy/*.md
# ---------------------------------------------------------------------------
print("\n[6] Metric taxonomy breadcrumbs")
mt_dir = DOCS_ROOT / "03-technical-contracts" / "03-metric-taxonomy"
for md in mt_dir.glob("*.md"):
    changed = patch(md, "01-metric-taxonomy.md", "01-index.md")
    report(md, changed, "MT breadcrumb")


# ---------------------------------------------------------------------------
# 7. Metric taxonomy .md file reference from tutorials
#    Replace ../03-technical-contracts/03-metric-taxonomy.md with correct dir index
# ---------------------------------------------------------------------------
print("\n[7] Metric taxonomy broken link from tutorials")
for md in (DOCS_ROOT / "06-tutorials").glob("*.md"):
    changed = patch(
        md,
        "../03-technical-contracts/03-metric-taxonomy.md",
        "../03-technical-contracts/03-metric-taxonomy/01-index.md",
    )
    report(md, changed, "MT tutorial link")


# ---------------------------------------------------------------------------
# 8. C4 level4 code depth: ../../../03-technical-contracts/ → ../../../../03-technical-contracts/
#    Files: docs/02-design/02-architecture/05-c4-level4-code/*/
# ---------------------------------------------------------------------------
print("\n[8] C4 level4 code depth")
c4l4_root = DOCS_ROOT / "02-design" / "02-architecture" / "05-c4-level4-code"
for md in c4l4_root.rglob("*.md"):
    if md.parent == c4l4_root:
        continue
    changed = patch(md, "../../../03-technical-contracts/", "../../../../03-technical-contracts/")
    report(md, changed, "C4L4 depth")


# ---------------------------------------------------------------------------
# 9. C4 level4 wrong sub-directory: ../02-cross-cutting/ → ../02-shared/
#    File: 05-analysis-engine/02-metric-dispatcher.md
# ---------------------------------------------------------------------------
print("\n[9] C4 level4 wrong subdirectory cross-cutting → shared")
md = c4l4_root / "05-analysis-engine" / "02-metric-dispatcher.md"
if md.exists():
    changed = patch(md, "../02-cross-cutting/", "../02-shared/")
    report(md, changed, "C4L4 subdir fix")


# ---------------------------------------------------------------------------
# 10. Corvus-pilot directory link: 02-corvus-pilot.md → 02-corvus-pilot/01-index.md
#     Files: C2 containers and tutorials
# ---------------------------------------------------------------------------
print("\n[10] Corvus-pilot .md → directory/01-index.md")

_corvus_files = [
    DOCS_ROOT / "02-design" / "02-architecture" / "03-c4-leve2-containers" / "14-corvus-pilot.md",
    DOCS_ROOT / "06-tutorials" / "05-learner-socratic-mode.md",
]
for md in _corvus_files:
    if not md.exists():
        continue
    # Fix extra ../docs/ prefix first (socratic-mode has this)
    changed = patch(
        md,
        "../docs/02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot.md",
        "../02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot/01-index.md",
    )
    report(md, changed, "corvus-pilot ../docs fix")
    # Fix regular path to corvus-pilot.md (both from C2 and from docs/)
    changed = patch(
        md,
        "../04-c4-leve3-components/02-corvus-pilot.md",
        "../04-c4-leve3-components/02-corvus-pilot/01-index.md",
    )
    report(md, changed, "corvus-pilot C2 fix")
    changed = patch(
        md,
        "../02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot.md",
        "../02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot/01-index.md",
    )
    report(md, changed, "corvus-pilot tutorial fix")


# ---------------------------------------------------------------------------
# 11. Performance-record ADR link depth: ../02-design → ../../02-design
#     File: docs/03-technical-contracts/01-data-format/07-performance-record.md
# ---------------------------------------------------------------------------
print("\n[11] Performance-record ADR link depth")
md = DOCS_ROOT / "03-technical-contracts" / "01-data-format" / "07-performance-record.md"
if md.exists():
    changed = patch(
        md,
        "../02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md",
        "../../02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md",
    )
    report(md, changed, "perf-record ADR depth")


# ---------------------------------------------------------------------------
# 12. Algorithm registry missing numbered prefix in problem-repository files
#     Files: 12-problem-repository/03-version-manager.md, 04-entity-store.md
# ---------------------------------------------------------------------------
print("\n[12] Algorithm registry links in problem-repository")
pr_dir = c3_root / "12-problem-repository"
md = pr_dir / "03-version-manager.md"
if md.exists():
    changed = patch(md, "../11-algorithm-registry/version-manager.md", "../11-algorithm-registry/03-version-manager.md")
    report(md, changed, "algo-registry prefix")
md = pr_dir / "04-entity-store.md"
if md.exists():
    changed = patch(md, "../11-algorithm-registry/entity-store.md", "../11-algorithm-registry/04-entity-store.md")
    report(md, changed, "algo-registry prefix")


# ---------------------------------------------------------------------------
# 13. C1 context directory links: actors/ → ../02-actors/  and  external-systems/ → ../03-external-systems/
#     File: 02-c4-leve1-context/01-c4-l1-context/01-c1-context.md
# ---------------------------------------------------------------------------
print("\n[13] C1 context directory links")
md = DOCS_ROOT / "02-design" / "02-architecture" / "02-c4-leve1-context" / "01-c4-l1-context" / "01-c1-context.md"
if md.exists():
    changed = patch(md, "(actors/)", "(../02-actors/)")
    report(md, changed, "C1 actors dir")
    changed = patch(md, "(external-systems/)", "(../03-external-systems/)")
    report(md, changed, "C1 external-systems dir")


# ---------------------------------------------------------------------------
# 14. specs/ old path replacements (global across all docs)
#     specs/data-format.md    → docs/03-technical-contracts/01-data-format/01-index.md
#     specs/interface-contracts.md → docs/03-technical-contracts/02-interface-contracts/01-index.md
#     specs/metric-taxonomy.md → docs/03-technical-contracts/03-metric-taxonomy/01-index.md
#     specs/data-format.md §X → docs/03-technical-contracts/01-data-format/FILENAME.md  (handled by data-format replacer below)
# ---------------------------------------------------------------------------
print("\n[14] specs/ old path replacements")
SPECS_REPLACEMENTS = [
    ("specs/interface-contracts.md", "docs/03-technical-contracts/02-interface-contracts/01-index.md"),
    ("specs/metric-taxonomy.md",     "docs/03-technical-contracts/03-metric-taxonomy/01-index.md"),
    # specs/data-format.md is handled by the data-format replacer (step 15)
]
for md in DOCS_ROOT.rglob("*.md"):
    for old, new in SPECS_REPLACEMENTS:
        if old in md.read_text(encoding="utf-8", errors="replace"):
            changed = patch(md, old, new)
            report(md, changed, f"specs/ → {new.split('/')[-2]}")


# ---------------------------------------------------------------------------
# 15. data-format.md section references (text/comment replacements across all docs)
# ---------------------------------------------------------------------------
print("\n[15] data-format.md section references")
for md in DOCS_ROOT.rglob("*.md"):
    text = md.read_text(encoding="utf-8", errors="replace")
    new_text = replace_data_format_ref(text)
    if new_text != text:
        md.write_text(new_text, encoding="utf-8")
        changes += 1
        print(f"  fixed  {md.relative_to(REPO_ROOT)}  [data-format refs]")


# ---------------------------------------------------------------------------
# 16. C1 context path patterns:
#     02-c4-leve1-context/01-c1-context.md → 02-c4-leve1-context/01-c4-l1-context/01-c1-context.md
#     02-c1-context.md → 02-c4-leve1-context/01-c4-l1-context/01-c1-context.md (bare ref)
# ---------------------------------------------------------------------------
print("\n[16] C1 context path pattern fixes")
C1_REPLACEMENTS = [
    (
        "02-c4-leve1-context/01-c1-context.md",
        "02-c4-leve1-context/01-c4-l1-context/01-c1-context.md",
    ),
    (
        "docs/02-design/02-architecture/02-c4-leve1-context/01-c1-context.md",
        "docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md",
    ),
    (
        "02-design/02-architecture/02-c1-context.md",
        "02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md",
    ),
]
for md in DOCS_ROOT.rglob("*.md"):
    text = md.read_text(encoding="utf-8", errors="replace")
    new_text = text
    for old, new in C1_REPLACEMENTS:
        new_text = new_text.replace(old, new)
    if new_text != text:
        md.write_text(new_text, encoding="utf-8")
        changes += 1
        print(f"  fixed  {md.relative_to(REPO_ROOT)}  [C1 path]")


# ---------------------------------------------------------------------------
# 17. 01-c2-containers.md → 01-index.md (in ADR and other files)
# ---------------------------------------------------------------------------
print("\n[17] 01-c2-containers.md → 01-index.md")
for md in DOCS_ROOT.rglob("*.md"):
    changed = patch(md, "01-c2-containers.md", "01-index.md")
    report(md, changed, "C2 index")


# ---------------------------------------------------------------------------
# 18. SRS.md bare path references → full path
#     'SRS.md' (not '01-SRS.md') in text context
# ---------------------------------------------------------------------------
print("\n[18] SRS.md bare path → full path")
SRS_PAIRS = [
    # Full docs path variants
    (
        "docs/02-design/01-software-requirement-specification/SRS.md",
        "docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md",
    ),
    (
        "docs/02-design/01-software-requirement-specification/01-srs/SRS.md",
        "docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md",
    ),
    # Short refs in text (e.g. MANIFESTO.md, SRS.md, ...)
    ("MANIFESTO.md, SRS.md,", "MANIFESTO.md, 01-srs/01-SRS.md,"),
    ("] SRS.md",  "] 01-srs/01-SRS.md"),
    ("/ SRS.md",  "/ 01-srs/01-SRS.md"),
    (" SRS.md §", " 01-srs/01-SRS.md §"),
    ("`SRS.md §", "`01-srs/01-SRS.md §"),
    ("← SRS.md",  "← 01-srs/01-SRS.md"),
    ("→ SRS.md",  "→ 01-srs/01-SRS.md"),
]
for md in DOCS_ROOT.rglob("*.md"):
    # Skip the actual SRS file to avoid self-modification
    if md.name == "01-SRS.md":
        continue
    text = md.read_text(encoding="utf-8", errors="replace")
    new_text = text
    for old, new in SRS_PAIRS:
        new_text = new_text.replace(old, new)
    if new_text != text:
        md.write_text(new_text, encoding="utf-8")
        changes += 1
        print(f"  fixed  {md.relative_to(REPO_ROOT)}  [SRS path]")


# ---------------------------------------------------------------------------
# 19. TASKS.md references — remove the ref (file doesn't exist)
# ---------------------------------------------------------------------------
print("\n[19] TASKS.md references")
TASKS_PAIRS = [
    (
        "→ docs/05-community/TASKS.md                                : REF-TASK-0013 delivered\n",
        "",
    ),
    (
        "→ docs/05-community/TASKS.md : each step in a real study should correspond to trackable tasks\n",
        "",
    ),
    (
        "→ docs/05-community/TASKS.md : REF-TASK-0013 delivered\n",
        "",
    ),
    (
        " TASKS.md,",
        "",
    ),
    (
        " TASKS.md",
        "",
    ),
]
for md in DOCS_ROOT.rglob("*.md"):
    text = md.read_text(encoding="utf-8", errors="replace")
    new_text = text
    for old, new in TASKS_PAIRS:
        new_text = new_text.replace(old, new)
    if new_text != text:
        md.write_text(new_text, encoding="utf-8")
        changes += 1
        print(f"  fixed  {md.relative_to(REPO_ROOT)}  [TASKS.md]")


# ---------------------------------------------------------------------------
# 20. Fix FR labels in C2 container files
# ---------------------------------------------------------------------------
print("\n[20] FR label fixes in C2 container files")

c2_dir = DOCS_ROOT / "02-design" / "02-architecture" / "03-c4-leve2-containers"

# 07-study-orchestrator.md
md = c2_dir / "07-study-orchestrator.md"
if md.exists():
    r = patch(md, "FR-10 (run isolation)", "FR-10 (execution environment recording)")
    report(md, r, "FR-10 label")
    r = patch(md, "FR-17 (reproducibility — locking and immutability)", "FR-17 (UUID entity identification — no file paths as IDs)")
    report(md, r, "FR-17 label")
    r = patch(md, "FR-18 (resume\ninterrupted experiments)", "FR-18 (Artifact archive production)")
    report(md, r, "FR-18 label multiline")
    # Also try single-line variant
    r = patch(md, "FR-18 (resume interrupted experiments)", "FR-18 (Artifact archive production)")
    report(md, r, "FR-18 label")
    r = patch(md, "FR-19 (execution environment capture)", "FR-19 (entity ID cross-references — no file paths)")
    report(md, r, "FR-19 label")

# 08-experiment-runner.md
md = c2_dir / "08-experiment-runner.md"
if md.exists():
    r = patch(md, "FR-10 (run\nisolation)", "FR-10 (execution environment recording)")
    report(md, r, "FR-10 label multiline")
    r = patch(md, "FR-10 (run isolation)", "FR-10 (execution environment recording)")
    report(md, r, "FR-10 label")
    r = patch(md, "FR-11 (evaluation budget enforcement)", "FR-11 (Run isolation — no shared mutable state)")
    report(md, r, "FR-11 label")
    r = patch(md, "FR-19 (execution environment capture)", "FR-19 (entity ID cross-references — no file paths)")
    report(md, r, "FR-19 label")

# 09-analysis-engine.md
md = c2_dir / "09-analysis-engine.md"
if md.exists():
    r = patch(md, "FR-14 (statistical\ntests — Wilcoxon, Kruskal-Wallis)", "FR-14 (PerformanceRecord log-scale recording)")
    report(md, r, "FR-14 label multiline")
    r = patch(md, "FR-14 (statistical tests — Wilcoxon, Kruskal-Wallis)", "FR-14 (PerformanceRecord log-scale recording)")
    report(md, r, "FR-14 label")
    r = patch(md, "FR-15 (scoped conclusions — no global rankings)", "FR-15 (three analysis levels — exploratory, confirmatory, practical significance)")
    report(md, r, "FR-15 label")

# 12-results-store.md
md = c2_dir / "12-results-store.md"
if md.exists():
    r = patch(md, "FR-17 (data immutability and locking)", "FR-17 (UUID entity identification — no file paths as IDs)")
    report(md, r, "FR-17 label")
    r = patch(md, "FR-18 (resume interrupted\nexperiments)", "FR-18 (Artifact archive production)")
    report(md, r, "FR-18 label multiline")
    r = patch(md, "FR-18 (resume interrupted experiments)", "FR-18 (Artifact archive production)")
    report(md, r, "FR-18 label")
    r = patch(md, "FR-19 (execution environment capture and storage)", "FR-19 (entity ID cross-references — no file paths)")
    report(md, r, "FR-19 label")


# ---------------------------------------------------------------------------
# 21. ROADMAP.md: data-format.md update ref
#     The data-format replacer (step 15) may not have caught all ROADMAP refs
#     Do a final targeted pass
# ---------------------------------------------------------------------------
print("\n[21] ROADMAP.md remaining fixes")
roadmap = DOCS_ROOT / "ROADMAP.md"
if roadmap.exists():
    # data-format.md update ref that doesn't have §
    r = patch(roadmap, "data-format.md update", f"{DATA_FORMAT_DIR}/01-index.md update")
    report(roadmap, r, "ROADMAP data-format update")
    # Interface-contracts.md ref that may remain
    r = patch(roadmap, "interface-contracts.md,", "docs/03-technical-contracts/02-interface-contracts/01-index.md,")
    report(roadmap, r, "ROADMAP interface-contracts")
    r = patch(roadmap, "metric-taxonomy.md,", "docs/03-technical-contracts/03-metric-taxonomy/01-index.md,")
    report(roadmap, r, "ROADMAP metric-taxonomy")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print(f"  Total files modified: {changes}")
if changes == 0:
    print("  No changes needed.")
print()
