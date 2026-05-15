# Requirements Traceability Matrix — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: The single cross-reference table linking every requirement to its source, its exercising
use case, the container that implements it, and the test category that verifies it. When this matrix
is complete, nothing is untraceable — every commitment has a source and a test.

NARRATIVE POSITION:
  All requirement documents → Traceability Matrix → complete accountability map

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                : MANIFESTO Principles column source
  ← use-cases.md                                   : UC rows and UC exercised column
  ← functional-requirements.md                     : FR rows
  ← non-functional-requirements.md                 : NFR rows
  ← constraints.md                                 : CONST rows
  ← acceptance-test-strategy.md                    : test category column
  → docs/02-design/02-architecture/03-c4-leve2-containers/01-index.md : C2 Container column
-->

---

## Use Cases

| Req ID | MANIFESTO Principles | File | C2 Container | Test Category | Status |
|---|---|---|---|---|---|
| UC-01 | 1, 4–5, 10, 12–16, 18–22, 23–25 | `use-cases.md` | Study Orchestrator, Experiment Runner, Analysis Engine, Reporting Engine | Integration, Reproducibility, Statistical validity | Expanded |
| UC-02 | 8, 10, 11, 19, 31 | `use-cases.md` | Algorithm Registry, Public API | Plugin, Validation rejection | Expanded |
| UC-03 | 2, 3, 24, 25 | `use-cases.md` | Reporting Engine, Public API | Constraint enforcement | Expanded |
| UC-04 | 4, 5, 6, 7, 27 | `use-cases.md` | Problem Repository, Public API | Plugin, Validation rejection | Expanded |
| UC-05 | 19, 20, 21, 22 | `use-cases.md` | Experiment Runner, Results Store | Reproducibility | Expanded |
| UC-06 | 26 | `use-cases.md` | Ecosystem Bridge | Interoperability | Expanded |
| UC-07 | 25, 28 | `02-use-cases/08-uc-07.md` | Algorithm Visualization Engine, Corvus Pilot | Usability | Expanded |
| UC-08 | 25, 28 | `02-use-cases/09-uc-08.md` | Corvus Pilot | Usability | Expanded |
| UC-09 | 28 | `02-use-cases/10-uc-09.md` | Corvus Pilot | Usability | Expanded |
| UC-10 | 25, 28 | `02-use-cases/11-uc-10.md` | Corvus Pilot | Usability | Expanded |
| UC-11 | 3, 21, 23–25, 28 | `02-use-cases/12-uc-11.md` | Corvus Pilot, Reporting Engine, Results Store | Usability, Integration | Expanded |

---

## Functional Requirements

| Req ID | MANIFESTO Principles | File | C2 Container | UC exercised | Test Category | Status |
|---|---|---|---|---|---|---|
| FR-01 | 4, 7 | `functional-requirements.md` §4.1 | Problem Repository | UC-04 | Unit, Validation rejection | Defined |
| FR-02 | 7 | `functional-requirements.md` §4.1 | Problem Repository | UC-04 F1 | Validation rejection | Defined |
| FR-03 | 6, 21 | `functional-requirements.md` §4.1 | Problem Repository | UC-04, UC-05 | Unit | Defined |
| FR-04 | 21 | `functional-requirements.md` §4.1 | Problem Repository, Study Orchestrator | UC-01 | Integration | Defined |
| FR-05 | 8, 10 | `functional-requirements.md` §4.2 | Algorithm Registry | UC-02 | Unit, Validation rejection | Defined |
| FR-06 | 8, 19 | `functional-requirements.md` §4.2 | Algorithm Registry | UC-02 F2 | Validation rejection | Defined |
| FR-07 | 10 | `functional-requirements.md` §4.2 | Algorithm Registry | UC-02 F3 | Validation rejection | Defined |
| FR-08 | 16 | `functional-requirements.md` §4.3 | Study Orchestrator | UC-01 F3 | Pre-registration gate | Defined |
| FR-09 | 18 | `functional-requirements.md` §4.3 | Experiment Runner | UC-01 | Integration, Reproducibility | Defined |
| FR-10 | 19 | `functional-requirements.md` §4.3 | Experiment Runner | UC-01, UC-05 | Integration, Reproducibility | Defined |
| FR-11 | 18 | `functional-requirements.md` §4.3 | Experiment Runner | UC-01 | Integration | Defined |
| FR-12 | 19 | `functional-requirements.md` §4.3 | Experiment Runner | UC-01 F2 | Integration | Defined |
| FR-13 | 12, 14 | `functional-requirements.md` §4.4 | Analysis Engine | UC-01 Step 7 | Integration, Statistical validity | Defined |
| FR-14 | 14 | `functional-requirements.md` §4.4 | Experiment Runner | UC-01 | Unit | Defined |
| FR-15 | 13 | `functional-requirements.md` §4.4 | Analysis Engine | UC-01 Step 8 | Statistical validity | Defined |
| FR-16 | 15 | `functional-requirements.md` §4.4 | Analysis Engine | UC-01 Step 8 | Statistical validity | Defined |
| FR-17 | 19, 21; ADR-001 | `functional-requirements.md` §4.5 | All | UC-01, UC-05 | Integration, Reproducibility | Defined |
| FR-18 | 19 | `functional-requirements.md` §4.5 | Results Store | UC-05 | Reproducibility | Defined |
| FR-19 | ADR-001 | `functional-requirements.md` §4.5 | All | UC-01 | Unit | Defined |
| FR-20 | 25 | `functional-requirements.md` §4.6 | Reporting Engine | UC-01 Step 9, UC-03 | Integration | Defined |
| FR-21 | 24 | `functional-requirements.md` §4.6 | Reporting Engine | UC-01 Step 9, UC-03 | Constraint enforcement | Defined |
| FR-22 | 20, 25 | `functional-requirements.md` §4.6 | Reporting Engine | UC-01 Step 10 | Open format compliance | Defined |
| FR-23 | 26 | `functional-requirements.md` §4.7 | Ecosystem Bridge | UC-06 | Interoperability | Defined |
| FR-24 | 26 | `functional-requirements.md` §4.7 | Ecosystem Bridge | UC-06 | Interoperability | Defined |
| FR-25 | 26 | `functional-requirements.md` §4.7 | Ecosystem Bridge, Algorithm Registry | UC-02, UC-06 | Interoperability, Plugin | Defined |
| FR-26 | 24 | `functional-requirements.md` §4.7 | Ecosystem Bridge | UC-06 | Interoperability | Defined |
| FR-27 *(DEFERRED)* | 25, 28 | `09-fr-4.8-learner-actor.md` | Algorithm Visualization Engine | UC-07 | Usability | Deferred — Phase 4 |
| FR-28 *(DEFERRED)* | 25, 28 | `09-fr-4.8-learner-actor.md` | Corvus Pilot | UC-08 | Usability | Deferred — Phase 4 |
| FR-29 *(DEFERRED)* | 28 | `09-fr-4.8-learner-actor.md` | Corvus Pilot | UC-09 | Usability | Deferred — Phase 4 |
| FR-30 *(DEFERRED)* | 25, 28 | `09-fr-4.8-learner-actor.md` | Algorithm Visualization Engine | UC-10 | Usability | Deferred — Phase 4 |
| FR-31 *(DEFERRED)* | 3, 23–25, 28 | `09-fr-4.8-learner-actor.md` | Corvus Pilot, Reporting Engine, Results Store | UC-11 | Usability, Constraint enforcement | Deferred — Phase 4 |

---

## Non-Functional Requirements

| Req ID | MANIFESTO Principles | File | C2 Container | UC exercised | Test Category | Status |
|---|---|---|---|---|---|---|
| NFR-REPRO-01 | 19–22 | `non-functional-requirements.md` | Reproducibility Layer, Results Store | UC-01, UC-05 | Reproducibility | Defined |
| NFR-STAT-01 | 13, 15 | `non-functional-requirements.md` | Analysis Engine | UC-01 | Statistical validity | Defined |
| NFR-INTEROP-01 | 26 | `non-functional-requirements.md` | Ecosystem Bridge | UC-06 | Interoperability | Defined |
| NFR-OPEN-01 | 20, 22 | `non-functional-requirements.md` | All | UC-01, UC-04 | Open format compliance | Defined |
| NFR-MODULAR-01 | Value 6, Principle 27 | `non-functional-requirements.md` | All | UC-02, UC-04 | Plugin | Defined |
| NFR-USABILITY-01 | 28 | `non-functional-requirements.md` | Public API, CLI | UC-01, UC-02 | Usability | Defined |

---

## Constraints

| Req ID | MANIFESTO Source | File | UC guarded | Enforced by | Status |
|---|---|---|---|---|---|
| CONST-SCI-01 | Anti-pattern 1 | `constraints.md` | UC-03 | FR-21 (no ranking in reports) | Defined |
| CONST-SCI-02 | Anti-pattern 3 | `constraints.md` | All | Design exclusion | Defined |
| CONST-SCI-03 | Anti-pattern 7 | `constraints.md` | UC-03 Step 6 | Design exclusion; no recommendation API | Defined |
| CONST-SCI-04 | Anti-pattern 4 | `constraints.md` | UC-01 | FR-15, FR-16 (inspectable analysis) | Defined |
| CONST-SCI-05 | Anti-pattern 6 | `constraints.md` | UC-01, UC-03 | FR-21 (mandatory limitations section) | Defined |
| CONST-SCI-06 | Principle 3 | `constraints.md` | UC-01, UC-03 | FR-21 (scoped conclusions) | Defined |
| CONST-COM-01 | Principle 20 | `constraints.md` | All | CONST-TECH-06 (licensecheck CI gate); ADR-006 | Defined |
| CONST-COM-02 | Principle 20 | `constraints.md` | UC-01, UC-04 | versioning-governance.md §5 | Defined |
| CONST-COM-03 | Principle 22 | `constraints.md` | UC-01 Step 10 | FR-22 (open format export) | Defined |
| CONST-TECH-01 | ADR-001 | `constraints.md` | All | Repository interface design | Defined |
| CONST-TECH-02 | ADR-001 | `constraints.md` | All | data-format.md §1 | Defined |
| CONST-TECH-03 | ADR-001 | `constraints.md` | All | FR-17, FR-19 | Defined |
| CONST-TECH-04 | ADR-006 | `constraints.md` | All | CI Python 3.10/3.11/3.12 matrix | Defined |
| CONST-TECH-05 | ADR-006 | `constraints.md` | All | CI Linux + macOS blocking; Windows non-blocking | Defined |
| CONST-TECH-06 | ADR-006 | `constraints.md` | All | licensecheck CI step | Defined |
| CONST-TECH-07 | ADR-006 | `constraints.md` | All | pyproject.toml dependency declarations | Defined |
