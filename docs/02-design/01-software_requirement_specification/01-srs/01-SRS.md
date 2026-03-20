# Software Requirements Specification — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: The "contract of capabilities". Translates the WHY (MANIFESTO) into verifiable WHAT.
Every requirement here must be traceable to at least one MANIFESTO principle,
and every MANIFESTO principle should produce at least one requirement.

NARRATIVE POSITION:
  MANIFESTO (WHY) → SRS (index) → child documents (WHAT the system must do)
  C1 (actors) feeds §3 (stakeholders and use cases) → use-cases.md
  C2 (containers) feeds §4 (functional requirement grouping) → functional-requirements.md
  interface-requirements.md feeds → docs/03-technical-contracts/interface-contracts.md and data-format.md (how)
  acceptance-test-strategy.md feeds → tasks/tickets (what to test and verify)

FILE STRUCTURE — this SRS is an index document; detailed content lives in:
  use-cases.md                  : UC-01 through UC-06 (full flows, preconditions, failure scenarios)
  functional-requirements.md    : FR-01 through FR-26 (grouped by C2 container)
  non-functional-requirements.md: NFR-REPRO-01 through NFR-USABILITY-01
  constraints.md                : CONST-SCI-XX, CONST-COM-XX, CONST-TECH-XX
  interface-requirements.md     : per-external-system interface specifications
  acceptance-test-strategy.md   : test categories, acceptance criteria per requirement class
  traceability-matrix.md        : full cross-reference (MANIFESTO ↔ UC ↔ FR ↔ NFR ↔ test)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                              : principles are the source of requirements
  ← docs/02-design/02-architecture/c1-context.md               : actors become stakeholders; external systems become interface requirements
  ← docs/02-design/02-architecture/c2-containers.md            : container grouping organizes functional-requirements.md
  → docs/03-technical-contracts/data-format.md                  : interface-requirements.md data requirements are detailed there
  → docs/03-technical-contracts/interface-contracts.md          : interface-requirements.md specifications are formalized there
  → docs/04_scientific_practice/methodology/statistical-methodology.md : NFR-STAT-01 operationalized there
  → docs/05_community/versioning-governance.md                  : NFR-REPRO-01 and constraints.md CONST-COM-XX operationalized there
  → docs/02-design/02-architecture/adr/                         : when a requirement drives an architectural decision, link the ADR
  → docs/05_community/TASKS.md                                  : each requirement ID (FR-XX, NFR-XX) should be referenced in tasks
  → docs/GLOSSARY.md                                            : all terms used in requirement descriptions are defined there
-->

---

## 1. Introduction

### Purpose

This document specifies the software requirements for the Corvus Corone: HPO Algorithm Benchmarking Platform — a Python library that enables rigorous, reproducible benchmarking of hyperparameter optimization algorithms. It is intended for:

- **Library developers** implementing the system
- **Community contributors** designing new features or extending the platform
- **Researchers** evaluating the system's fitness for their scientific needs
- **External reviewers** assessing compliance with benchmarking best practices

### Scope

The system is a **Python library** that a user integrates by providing an algorithm Implementation; the library then handles Study execution, measurement, statistical analysis, and report generation automatically. The core value proposition is: *wrap your algorithm, get rigorous benchmarking*.

What is explicitly out of scope is defined in `docs/02-design/02-architecture/c1-context.md` — Explicit Scope Exclusions. The most important exclusion: this system does not produce algorithm rankings.

### Relationship to MANIFESTO

This document operationalizes `docs/01-manifesto/MANIFESTO.md`. Where the MANIFESTO states values ("we value X over Y"), this SRS states verifiable requirements. Every requirement in §4–§5 must trace to at least one MANIFESTO Principle; a requirement without a source is a candidate for removal. The traceability matrix in §9 makes this relationship explicit.

### Document Status

**Version:** 0.2 — UC-01–UC-06 expanded; FR-01–FR-26 defined; NFRs, Constraints, Interface Requirements, Acceptance Test Strategy, and Traceability Matrix structured. Measurable NFR criteria pending (`REF-TASK-0010`); test file paths pending C3 design (`REF-TASK-0013`).

> **`TODO: REF-TASK-0008`** (Partial) — FR-01–FR-26 defined in `functional-requirements.md`; §7 structured in `interface-requirements.md`; §8 categories defined in `acceptance-test-strategy.md`. Remaining: measurable NFR criteria (`REF-TASK-0010`); test file path assignment (`REF-TASK-0013`).
> Owner: technical lead.

---

## 2. System Overview

The Corvus Corone: HPO Algorithm Benchmarking Platform is a Python library designed to serve the discovery of truth about hyperparameter optimization algorithm performance. A researcher wraps their algorithm in a thin adapter implementing the Algorithm Interface, specifies a Study (research question, problem selection, experimental design), and receives in return: automated execution of reproducible Runs, full Anytime Performance curves, three-level statistical analysis, and multi-audience reports — all without manual instrumentation.

The main goal was to create framework/platform that allow researchers to concentrate on algorithm implementation not serroudings to measure it.

The system prioritizes scientific validity over convenience: it enforces pre-registration of hypotheses, controls and records all sources of randomness, and scopes every conclusion to the Problem Instances actually tested. It does not tell the researcher which algorithm is "best"; it helps them answer the specific question they asked.

For context on who uses the system and what surrounds it, see `docs/02-design/02-architecture/c1-context.md`. For the values that shaped these design choices, see `docs/01-manifesto/MANIFESTO.md`.

---

## 3. Stakeholders and Use Cases

Full use case descriptions — main flow, preconditions, postconditions, failure scenarios, and cross-document connections — are in **[`use-cases.md`](use-cases.md)**.

### Use Case Summary

| ID | Actor | Trigger | Goal |
|---|---|---|---|
| UC-01 | Researcher | Has a research question about HPO algorithm behavior | Design and execute a reproducible benchmarking Study; receive a statistically valid analysis report |
| UC-02 | Algorithm Author | Has a new HPO algorithm or wants to wrap an existing one | Contribute an Implementation; see it fairly evaluated against other Algorithm Instances |
| UC-03 | Practitioner | Needs to select an HPO algorithm for an ML project | Find performance summaries scoped to problem characteristics matching their application |
| UC-04 | Community Contributor | Discovers a missing Problem Instance type | Contribute a new Problem Instance to the benchmark set |
| UC-05 | Researcher | Wants to verify a published study | Reproduce an existing Experiment from its archived Artifacts |
| UC-06 | Researcher | Has completed a Study | Export results to IOHprofiler / COCO format for cross-platform comparison |

---

## 4. Functional Requirements

Requirements FR-01 through FR-26 are defined in **[`functional-requirements.md`](functional-requirements.md)**, grouped by C2 container:

| Group | Container | Requirements |
|---|---|---|
| §4.1 | Problem Repository | FR-01 – FR-04 |
| §4.2 | Algorithm Registry | FR-05 – FR-07 |
| §4.3 | Experiment Runner | FR-08 – FR-12 |
| §4.4 | Measurement & Analysis Engine | FR-13 – FR-16 |
| §4.5 | Reproducibility Layer | FR-17 – FR-19 |
| §4.6 | Reporting & Visualization | FR-20 – FR-22 |
| §4.7 | Ecosystem Integration | FR-23 – FR-26 |

---

## 5. Non-Functional Requirements

NFR-REPRO-01 through NFR-USABILITY-01 are defined in **[`non-functional-requirements.md`](non-functional-requirements.md)**.

| ID | Quality attribute | Source |
|---|---|---|
| NFR-REPRO-01 | Reproducibility | MANIFESTO 19–22 |
| NFR-STAT-01 | Statistical validity | MANIFESTO 13, 15 |
| NFR-INTEROP-01 | Ecosystem interoperability | MANIFESTO 26 |
| NFR-OPEN-01 | Open data and code | MANIFESTO 20, 22 |
| NFR-MODULAR-01 | Extensibility | MANIFESTO Value 6, Principle 27 |
| NFR-USABILITY-01 | Minimal onboarding friction | MANIFESTO 28 |

> **`TODO: REF-TASK-0010`** — Add measurable criteria to each NFR.

---

## 6. Constraints

CONST-SCI-XX, CONST-COM-XX, and CONST-TECH-XX are defined in **[`constraints.md`](constraints.md)**.

| Group | Count | Source |
|---|---|---|
| Scientific Constraints | 6 (CONST-SCI-01–06) | MANIFESTO anti-patterns |
| Community Constraints | 3 (CONST-COM-01–03) | MANIFESTO 20, 22 |
| Technical Constraints | 3 established + 4 pending ADRs | ADR-001; `REF-TASK-0011` |

---

## 7. Interface Requirements

Per-interface specifications for all 5 external systems are in **[`interface-requirements.md`](interface-requirements.md)**.

| Interface | Direction | Status |
|---|---|---|
| 7.1 COCO Export | Export | Defined; field mapping pending (`REF-TASK-0005`) |
| 7.2 IOHprofiler Export | Export | Defined; field mapping pending (`REF-TASK-0007`) |
| 7.3 Nevergrad Algorithm | Import/Wrap | Defined; field mapping pending (`REF-TASK-0006`) |
| 7.4 HPC/Cloud Job Submission | Integration | V2 Horizon; blocked on V2 design |
| 7.5 Artifact Repository Publication | Export | V1 archive production defined; V2 direct publish pending |

---

## 8. Acceptance Test Strategy

Test categories, acceptance criteria per requirement class, and the mapping from requirements to test categories are in **[`acceptance-test-strategy.md`](acceptance-test-strategy.md)**.

> **`TODO: REF-TASK-0013`** — Assign test file paths once C3 component design is complete (`REF-TASK-0026`).

---

## 9. Requirements Traceability Matrix

The full cross-reference table — every requirement ID mapped to its MANIFESTO source, Use Case, C2 container, and test category — is in **[`traceability-matrix.md`](traceability-matrix.md)**.
