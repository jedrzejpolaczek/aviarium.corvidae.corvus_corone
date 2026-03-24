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
  ../02-use-cases/01-use-cases.md                     : UC-01 through UC-06
  ../03-functional-requirements/01-functional-requirements.md : FR-01 through FR-26
  ../04-non-functional-requirements/01-non-functional-requirements.md : NFR-REPRO-01 through NFR-USABILITY-01
  ../05-constraints/01-constraints.md                 : CONST-SCI-XX, CONST-COM-XX, CONST-TECH-XX
  ../06-interface-requirements/01-interface-requirements.md : per-external-system interface specifications
  ../07-acceptance-test-strategy/01-acceptance-test-strategy.md : test categories and FR→test mapping
  ../08-traceability-matrix/01-traceability-matrix.md : full cross-reference (MANIFESTO ↔ UC ↔ FR ↔ NFR ↔ test)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                              : principles are the source of requirements
  ← docs/02-design/02-architecture/02-c1-context.md            : actors become stakeholders; external systems become interface requirements
  ← docs/02-design/02-architecture/03-c4-leve2-containers/01-c2-containers.md : container grouping organizes functional-requirements.md
  → docs/03-technical-contracts/01-data-format/01-data-format.md : interface-requirements.md data requirements are detailed there
  → docs/03-technical-contracts/02-interface-contracts/         : interface-requirements.md specifications are formalized there
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md : NFR-STAT-01 operationalized there
  → docs/05-community/02-versioning-governance.md               : NFR-REPRO-01 and CONST-COM-XX operationalized there
  → docs/02-design/02-architecture/01-adr/                      : when a requirement drives an architectural decision, link the ADR
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

What is explicitly out of scope is defined in `docs/02-design/02-architecture/02-c1-context.md` — Explicit Scope Exclusions. The most important exclusion: this system does not produce algorithm rankings.

### Relationship to MANIFESTO

This document operationalizes `docs/01-manifesto/MANIFESTO.md`. Where the MANIFESTO states values ("we value X over Y"), this SRS states verifiable requirements. Every requirement in §4–§5 must trace to at least one MANIFESTO Principle; a requirement without a source is a candidate for removal. The traceability matrix in §9 makes this relationship explicit.

### Document Status

**Version:** 0.3 — UC-01–UC-06 expanded; FR-01–FR-26 defined; NFRs (6) and Constraints (CONST-SCI 6, CONST-COM 3, CONST-TECH 7) fully defined; §7 Interface Requirements complete for COCO, IOHprofiler, and Nevergrad (REF-TASK-0012); §8 Acceptance Test Strategy complete with FR→test file mapping, NFR→test mapping, and formal reproducibility procedure (REF-TASK-0013). Measurable NFR criteria pending (`REF-TASK-0010`).

---

## 2. System Overview

The Corvus Corone: HPO Algorithm Benchmarking Platform is a Python library designed to serve the discovery of truth about hyperparameter optimization algorithm performance. A researcher wraps their algorithm in a thin adapter implementing the Algorithm Interface, specifies a Study (research question, problem selection, experimental design), and receives in return: automated execution of reproducible Runs, full Anytime Performance curves, three-level statistical analysis, and multi-audience reports — all without manual instrumentation.

The system prioritizes scientific validity over convenience: it enforces pre-registration of hypotheses, controls and records all sources of randomness, and scopes every conclusion to the Problem Instances actually tested. It does not tell the researcher which algorithm is "best"; it helps them answer the specific question they asked.

For context on who uses the system and what surrounds it, see `docs/02-design/02-architecture/02-c1-context.md`. For the values that shaped these design choices, see `docs/01-manifesto/MANIFESTO.md`.

---

## 3. Stakeholders and Use Cases

Full use case descriptions — main flow, preconditions, postconditions, failure scenarios, and cross-document connections — are in **[`02-use-cases/01-use-cases.md`](../02-use-cases/01-use-cases.md)**.

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

Requirements FR-01 through FR-26 are defined in **[`03-functional-requirements/01-functional-requirements.md`](../03-functional-requirements/01-functional-requirements.md)**, grouped by C2 container:

| Group | Container | Requirements | File |
|---|---|---|---|
| §4.1 | Problem Repository | FR-01 – FR-04 | [02-fr-4.1-problem-repository.md](../03-functional-requirements/02-fr-4.1-problem-repository.md) |
| §4.2 | Algorithm Registry | FR-05 – FR-07 | [03-fr-4.2-algorithm-registry.md](../03-functional-requirements/03-fr-4.2-algorithm-registry.md) |
| §4.3 | Experiment Runner | FR-08 – FR-12 | [04-fr-4.3-experiment-runner.md](../03-functional-requirements/04-fr-4.3-experiment-runner.md) |
| §4.4 | Measurement & Analysis Engine | FR-13 – FR-16 | [05-fr-4.4-measurement-and-analysis.md](../03-functional-requirements/05-fr-4.4-measurement-and-analysis.md) |
| §4.5 | Reproducibility Layer | FR-17 – FR-19 | [06-fr-4.5-reproducibility-layer.md](../03-functional-requirements/06-fr-4.5-reproducibility-layer.md) |
| §4.6 | Reporting & Visualization | FR-20 – FR-22 | [07-fr-4.6-reporting-and-visualization.md](../03-functional-requirements/07-fr-4.6-reporting-and-visualization.md) |
| §4.7 | Ecosystem Integration | FR-23 – FR-26 | [08-fr-4.7-ecosystem-integration.md](../03-functional-requirements/08-fr-4.7-ecosystem-integration.md) |

---

## 5. Non-Functional Requirements

NFR-REPRO-01 through NFR-USABILITY-01 are defined in **[`04-non-functional-requirements/01-non-functional-requirements.md`](../04-non-functional-requirements/01-non-functional-requirements.md)**.

| ID | Quality attribute | Source | File |
|---|---|---|---|
| NFR-REPRO-01 | Reproducibility | MANIFESTO 19–22 | [02-nfr-repro-01.md](../04-non-functional-requirements/02-nfr-repro-01.md) |
| NFR-STAT-01 | Statistical validity | MANIFESTO 13, 15 | [03-nfr-stat-01.md](../04-non-functional-requirements/03-nfr-stat-01.md) |
| NFR-INTEROP-01 | Ecosystem interoperability | MANIFESTO 26 | [04-nfr-interop-01.md](../04-non-functional-requirements/04-nfr-interop-01.md) |
| NFR-OPEN-01 | Open data and code | MANIFESTO 20, 22 | [05-nfr-open-01.md](../04-non-functional-requirements/05-nfr-open-01.md) |
| NFR-MODULAR-01 | Extensibility | MANIFESTO Value 6, Principle 27 | [06-nfr-modular-01.md](../04-non-functional-requirements/06-nfr-modular-01.md) |
| NFR-USABILITY-01 | Minimal onboarding friction | MANIFESTO 28 | [07-nfr-usability-01.md](../04-non-functional-requirements/07-nfr-usability-01.md) |

> **`TODO: REF-TASK-0010`** — Add measurable pass/fail thresholds to each NFR.

---

## 6. Constraints

CONST-SCI-XX, CONST-COM-XX, and CONST-TECH-XX are defined in **[`05-constraints/01-constraints.md`](../05-constraints/01-constraints.md)**.

| Group | Count | Source | File |
|---|---|---|---|
| Scientific Constraints | 6 (CONST-SCI-01–06) | MANIFESTO anti-patterns | [02-const-scientific.md](../05-constraints/02-const-scientific.md) |
| Community Constraints | 3 (CONST-COM-01–03) | MANIFESTO 20, 22 | [03-const-community.md](../05-constraints/03-const-community.md) |
| Technical Constraints | 7 (CONST-TECH-01–07) | ADR-001, ADR-006 | [04-const-technical.md](../05-constraints/04-const-technical.md) |

---

## 7. Interface Requirements

Per-interface specifications for all 5 external systems are in **[`06-interface-requirements/01-interface-requirements.md`](../06-interface-requirements/01-interface-requirements.md)**.

| Interface | Direction | Status | File |
|---|---|---|---|
| §7.1 COCO Export | Export → COCO | ✅ Complete (REF-TASK-0005, REF-TASK-0012) | [02-ir-7.1-coco-export.md](../06-interface-requirements/02-ir-7.1-coco-export.md) |
| §7.2 IOHprofiler Export | Export → IOHprofiler | ✅ Complete (REF-TASK-0007, REF-TASK-0012) | [03-ir-7.2-iohprofiler-export.md](../06-interface-requirements/03-ir-7.2-iohprofiler-export.md) |
| §7.3 Nevergrad Algorithm | Import ← Nevergrad | ✅ Complete (REF-TASK-0006, REF-TASK-0012) | [04-ir-7.3-nevergrad-algorithm.md](../06-interface-requirements/04-ir-7.3-nevergrad-algorithm.md) |
| §7.4 HPC/Cloud Job Submission | Integration → scheduler | V2 Horizon; blocked on V2 design | [05-ir-7.4-hpc-cloud.md](../06-interface-requirements/05-ir-7.4-hpc-cloud.md) |
| §7.5 Artifact Repository Publication | Export → open repository | V1 archive production defined; V2 automated publish pending | [06-ir-7.5-artifact-repository.md](../06-interface-requirements/06-ir-7.5-artifact-repository.md) |

---

## 8. Acceptance Test Strategy

Test categories, FR→test file mapping (FR-01–FR-26), NFR→test procedure mapping, and the formal reproducibility test procedure are in **[`07-acceptance-test-strategy/01-acceptance-test-strategy.md`](../07-acceptance-test-strategy/01-acceptance-test-strategy.md)**. ✅ Complete (REF-TASK-0013).

---

## 9. Requirements Traceability Matrix

The full cross-reference table — every requirement ID mapped to its MANIFESTO source, Use Case, C2 container, and test category — is in **[`08-traceability-matrix/01-traceability-matrix.md`](../08-traceability-matrix/01-traceability-matrix.md)**.
