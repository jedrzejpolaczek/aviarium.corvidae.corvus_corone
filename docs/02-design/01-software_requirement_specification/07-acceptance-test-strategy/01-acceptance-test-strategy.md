# Acceptance Test Strategy — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: Defines how each requirement is verified. A requirement without a test is a wish,
not a commitment. This document maps every requirement class to a test category and states
what "accepted" means for each class.

NARRATIVE POSITION:
  Functional Requirements → Test Categories → Test files (when C3 is designed)
  Non-Functional Requirements → NFR-specific test categories → measurable thresholds
  Use Cases → End-to-end integration tests + tutorials

CONNECTS TO:
  ← functional-requirements.md                                : every FR must be covered by a test category
  ← non-functional-requirements.md                            : every NFR has a designated test category
  ← constraints.md                                            : CONST-XX constraints have enforcement tests
  ← use-cases.md                                              : every UC must have an end-to-end test
  → docs/02-design/02-architecture/c3-components.md           : test file paths defined when C3 is designed
  → docs/05_community/TASKS.md                                : REF-TASK-0013 tracks test file assignment

NOTE ON TEST FILE PATHS:
  Test file paths are not yet assigned — this requires C3 component design to be complete.
  REF-TASK-0026 (C2 descriptions) unblocks C3 design, which unblocks REF-TASK-0013.
  This document establishes the test categories and acceptance criteria; file paths follow later.
-->

---

## Test Categories

A requirement is considered accepted when its designated test category passes. The categories below are stable — they will not change when C3 is designed. Only test file paths will be added.

| Category | Purpose | Requirement IDs covered | UC coverage |
|---|---|---|---|
| Unit tests | Each C3 component behaves correctly in isolation | All FR-XX (per component once C3 is designed) | — |
| Integration tests | C2 container interactions produce correct data flows | FR-08 (gate), FR-09 (seeds), FR-13 (metrics), FR-15 (analysis chain) | UC-01 end-to-end |
| Reproducibility tests | Same Study → identical Result Aggregates on re-execution from archived Artifacts | NFR-REPRO-01; FR-09, FR-10, FR-17, FR-18 | UC-05 |
| Statistical validity tests | No report is produced if any analysis level is missing or bypassed | NFR-STAT-01; FR-15, FR-16 | UC-01 Step 8 |
| Pre-registration gate tests | Modification of Study plan after locking is rejected and logged | FR-08 | UC-01 F3 |
| Validation rejection tests | Invalid entity registrations are rejected with specific errors | FR-02, FR-06, FR-07 | UC-02 F1–F4; UC-04 F1 |
| Interoperability tests | Export round-trips produce loadable files; information-loss manifest is produced | NFR-INTEROP-01; FR-23, FR-24, FR-25, FR-26 | UC-06 |
| Plugin tests | New Algorithm Instance and Problem Instance can be contributed and used without modifying core library | NFR-MODULAR-01; FR-01–FR-07 | UC-02, UC-04 |
| Constraint enforcement tests | CONST-SCI-01 through CONST-SCI-06 cannot be violated by any API path | `constraints.md` Scientific Constraints | UC-03 F1 |
| Usability tests | Timed tutorial completion within stated targets | NFR-USABILITY-01 | UC-01, UC-02 |
| Open format compliance tests | Raw Data export formats are on the approved open-format list | NFR-OPEN-01; FR-22; CONST-COM-03 | UC-01 Step 10 |

---

## Acceptance Criteria per Requirement Class

### Functional Requirements (FR-XX)

Accepted when the integration test covering the corresponding UC step passes without error and produces the expected entity records in the correct format with the correct field values.

### Non-Functional Requirements (NFR-XX)

Accepted when the NFR-specific test category passes at the defined threshold. Thresholds are to be set when `REF-TASK-0010` is resolved. Until then, the test category is established but the pass/fail line is not drawn.

### Constraints (CONST-XX)

Accepted when the constraint enforcement test confirms that every API path that could violate the constraint is blocked at the system boundary — not by documentation, but by code that rejects the violating call.

### Use Cases (UC-XX)

Accepted when all three of the following hold:
1. All Main Flow steps produce their expected postconditions in an automated end-to-end integration test
2. Each named Failure Scenario is exercised and the system produces the expected rejection or warning (not a silent failure or an incorrect success)
3. A corresponding tutorial in `docs/06_tutorials/` demonstrates the UC for a human user and a representative user can complete it within the stated time target

---

> **`TODO: REF-TASK-0013`** — Assign test file paths to each category and automate each category once C3 component design is complete (`REF-TASK-0026`). Owner: QA / technical lead.
