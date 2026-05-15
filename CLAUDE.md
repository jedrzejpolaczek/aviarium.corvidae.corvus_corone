# CLAUDE.md — Project Invariants for aviarium.corvidae.corvus_corone

This file is loaded automatically by Claude Code at the start of every session.
It records project-specific facts that are **not derivable from reading the code alone**
and that every AI-assisted review or edit must respect.

---

## 1. Documentation Validation

Before reporting any findings from a docs review, **run the automated checker first**:

```
python scripts/validate-docs.py
```

This catches all broken links, monolithic-file references, wrong C3 breadcrumbs, wrong
GLOSSARY path depth, and known wrong FR labels in C2 container files.

---

## 2. Data Format — Split File Convention

The data format spec lives at `docs/03-technical-contracts/01-data-format/` as
**individual files per entity**, not a monolithic `01-data-format.md`.

| Old monolithic reference | Correct split file |
|---|---|
| `data-format.md §2.1` | `01-data-format/02-problem-instance.md` |
| `data-format.md §2.2` | `01-data-format/03-algorithm-instance.md` |
| `data-format.md §2.3` | `01-data-format/04-study.md` |
| `data-format.md §2.4` | `01-data-format/05-experiment.md` |
| `data-format.md §2.5` | `01-data-format/06-run.md` |
| `data-format.md §2.6` | `01-data-format/07-performance-record.md` |
| `data-format.md §2.7` | `01-data-format/08-result-aggregate.md` |
| `data-format.md §2.8` | `01-data-format/09-report.md` |
| `data-format.md §3`   | `01-data-format/10-file-formats.md` |
| `data-format.md §4`   | `01-data-format/11-interoperability-mappings.md` |
| `data-format.md §5`   | `01-data-format/12-cross-entity-validation.md` |
| `data-format.md §6`   | `01-data-format/13-schema-versioning.md` |

Any reference to a bare `data-format.md` (with or without `01-` prefix) is **wrong**
— the file does not exist.

---

## 3. Canonical C4 File Paths

| What | Correct path |
|---|---|
| C1 context diagram | `docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md` |
| C2 containers index | `docs/02-design/02-architecture/03-c4-leve2-containers/01-index.md` |
| C3 components overview | `docs/02-design/02-architecture/04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md` |
| SRS | `docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md` |
| Use-cases index | `docs/02-design/01-software-requirement-specification/02-use-cases/01-index.md` |
| FR index | `docs/02-design/01-software-requirement-specification/03-functional-requirements/01-index.md` |
| GLOSSARY | `docs/GLOSSARY.md` |
| Interface contracts index | `docs/03-technical-contracts/02-interface-contracts/01-index.md` |
| Metric taxonomy index | `docs/03-technical-contracts/03-metric-taxonomy/01-index.md` |

**The `specs/` directory no longer exists.** All references to `specs/data-format.md`,
`specs/interface-contracts.md`, or `specs/metric-taxonomy.md` are broken.

---

## 4. GLOSSARY Relative Path Depth

From **inside** `docs/03-technical-contracts/01-data-format/`:

| Wrong | Correct |
|---|---|
| `../GLOSSARY.md` | `../../GLOSSARY.md` |

`../GLOSSARY.md` resolves to `docs/03-technical-contracts/GLOSSARY.md` which does not exist.

---

## 5. C3 Component Breadcrumb Pattern

Every C3 component file under `04-c4-leve3-components/` should breadcrumb to the C3
overview as:

```
> C3 Index: [../01-c4-l3-components/01-c4-l3-components.md](../01-c4-l3-components/01-c4-l3-components.md)
```

The pattern `../01-c3-components.md` is **wrong** — that file does not exist.

---

## 6. FR Number → Canonical Description

Authoritative descriptions from the FR definition files. These are the correct labels
to use in C2 container "Relevant SRS section" lists. Any parenthetical label that
contradicts this table is wrong.

| FR | Canonical one-line description |
|---|---|
| FR-08 | enforce pre-registration gate — lock Study fields before Run execution |
| FR-09 | assign all Run seeds from declared seed_strategy |
| FR-10 | record full execution environment (OS, hardware, Python version, dependencies) |
| FR-11 | enforce Run isolation — no shared mutable state between Runs |
| FR-12 | record failed Run with failure_reason, not silently skip |
| FR-13 | compute all four Standard Reporting Set metrics per (problem, algorithm) pair |
| FR-14 | record PerformanceRecords at log-scale + improvement schedule for anytime curves |
| FR-15 | enforce all three analysis levels (exploratory, confirmatory, practical significance) |
| FR-16 | apply multiple-testing correction when >1 hypothesis; include adjusted p-values |
| FR-17 | every entity carries a UUID; no file paths as entity identifiers |
| FR-18 | produce Artifact archive for any completed Experiment |
| FR-19 | cross-entity references use entity IDs only — no file paths |
| FR-20 | generate HTML Researcher and Practitioner reports |
| FR-21 | include mandatory limitations section in every report |
| FR-22 | export report data in open formats |
| FR-23 | support export in at least one external benchmark platform format (primary export FR) |
| FR-24 | generate information-loss manifest before producing any export file |
| FR-32 | validate minimum 5 Problem Instances per Study (D-1 diversity rule) |
| FR-33 | validate dimensionality and noise coverage diversity (D-2, D-3 rules) |

**Common mislabeling patterns to watch for:**
- FR-10 ≠ "run isolation" (that is FR-11)
- FR-17 ≠ "data immutability/locking" (that is enforced by FR-08)
- FR-18 ≠ "resume interrupted experiments" (that is the Runner's `resume()` contract)
- FR-19 ≠ "execution environment capture" (that is FR-10)
- FR-14 ≠ "statistical tests / Wilcoxon" (those are FR-15/FR-16)

---

## 7. Schema Field Names (Authoritative)

Key field names from the entity schemas — reference these when writing acceptance criteria
or interface documentation:

| Concept | Correct field path |
|---|---|
| Execution OS | `execution_environment.platform` |
| Python version | `execution_environment.language_version` |
| Dependencies list | `software_environment.dependencies` |
| Run isolation status | `Run.status` ∈ `{completed, failed, budget_exhausted}` |
| Experiment status | `Experiment.status` ∈ `{planned, running, completed, failed, aborted}` |
| PerformanceRecord fields | `id, run_id, evaluation_number, elapsed_time, objective_value, current_solution, is_improvement, trigger_reason` (8 fields total) |
| `objective_value` semantics | stores `best_so_far` — NOT the raw per-evaluation output |

---

## 8. Known Intentional Stubs (Do Not Flag)

The following files are intentionally incomplete — do not flag them as missing content:

- `docs/06-tutorials/01-cmd-first-study.md` — tutorial body
- `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` — §4/§5/§6
- `docs/05-community/01-contribution-guide.md` — §1/§4–§8

---

## 9. Review Checklist

When performing a technical review of `docs/`, work through these passes in order:

1. **Run `python scripts/validate-docs.py`** — gets all mechanical issues automatically.
2. **FR label consistency** — check every C2 container file's "Relevant SRS section" against section 6 of this file.
3. **Stale "no existing FR yet" text** — grep for "no existing FR yet" across use-case files; UC-07 through UC-11 all have FRs now (FR-27–FR-31).
4. **Interface-contract body `data-format.md §2.x` references** — grep `data-format\.md` inside `docs/03-technical-contracts/02-interface-contracts/`; every hit is wrong.
5. **Technical accuracy** — field names in acceptance criteria vs. schema files; PerformanceRecord field count (8); FR-23 vs FR-24 assignment for export requirements.
