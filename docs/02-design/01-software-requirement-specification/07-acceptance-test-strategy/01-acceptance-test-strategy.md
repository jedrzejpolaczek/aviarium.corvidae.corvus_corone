# Acceptance Test Strategy — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: Defines how each requirement is verified. A requirement without a test is a wish,
not a commitment. This document maps every requirement class to a test category and states
what "accepted" means for each class.

NARRATIVE POSITION:
  Functional Requirements → Test Categories → Test files
  Non-Functional Requirements → NFR-specific test categories → measurable thresholds
  Use Cases → End-to-end integration tests + tutorials

CONNECTS TO:
  ← functional-requirements.md                                : every FR must be covered by a test category
  ← non-functional-requirements.md                            : every NFR has a designated test category
  ← constraints.md                                            : CONST-XX constraints have enforcement tests
  ← use-cases.md                                              : every UC must have an end-to-end test
  → docs/02-design/02-architecture/c3-components.md           : test file paths aligned to C3 components
  
NOTE ON TEST FILE PATHS:
  Paths under tests/unit/ and tests/e2e/test_uc03–06/ are planned; they will be created as
  the corresponding FR groups are implemented. Existing files are marked ✅.
  Path convention: packages/corvus-corone-lib/tests/<category>/<file>.py
-->

---

## Test Categories

A requirement is considered accepted when its designated test category passes.

| Category | Purpose | Requirement IDs covered | UC coverage |
|---|---|---|---|
| Unit tests | Each C3 component behaves correctly in isolation | FR-01–FR-03, FR-05–FR-07, FR-14, FR-17, FR-19, FR-32, FR-33 | — |
| Integration tests | C2 container interactions produce correct data flows | FR-04, FR-08–FR-13, FR-15–FR-16, FR-20 | UC-01 end-to-end |
| Reproducibility tests | Same Study → identical Result Aggregates on re-execution from archived Artifacts | NFR-REPRO-01; FR-09, FR-10, FR-17, FR-18 | UC-05 |
| Statistical validity tests | No report is produced if any analysis level is missing or bypassed | NFR-STAT-01; FR-15, FR-16 | UC-01 Step 8 |
| Pre-registration gate tests | Modification of Study plan after locking is rejected and logged | FR-08 | UC-01 F3 |
| Validation rejection tests | Invalid entity registrations are rejected with specific errors | FR-02, FR-06, FR-07 | UC-02 F1–F4; UC-04 F1 |
| Interoperability tests | Export round-trips produce loadable files; information-loss manifest is produced | NFR-INTEROP-01; FR-23, FR-24, FR-25, FR-26 | UC-06 |
| Plugin tests | New Algorithm Instance and Problem Instance can be contributed and used without modifying core library | NFR-MODULAR-01; FR-01–FR-07 | UC-02, UC-04 |
| Constraint enforcement tests | CONST-SCI-01 through CONST-SCI-06 cannot be violated by any API path | FR-21; `constraints.md` Scientific Constraints | UC-03 F1 |
| Usability tests | Timed tutorial completion within stated targets | NFR-USABILITY-01 | UC-01, UC-02 |
| Open format compliance tests | Raw Data export formats are on the approved open-format list | NFR-OPEN-01; FR-22; CONST-COM-03 | UC-01 Step 10 |

---

## FR-to-Test Mapping

Every FR maps to at least one test file. Files marked ✅ exist; files marked 🚧 are planned
and will be created as the corresponding feature is implemented.

| FR | Description (short) | Test Category | Test File |
|---|---|---|---|
| FR-01 | Store ProblemInstance with all required fields | Unit, Validation rejection | 🚧 `tests/unit/test_problem_repository.py` |
| FR-02 | Validate ProblemInstance completeness on registration | Validation rejection | 🚧 `tests/unit/test_problem_repository.py` |
| FR-03 | Problem Instance versioning | Unit | 🚧 `tests/unit/test_problem_repository.py` |
| FR-04 | Reject version mismatch before any Run begins | Integration | ✅ `tests/e2e/test_uc01_researcher_study.py` |
| FR-32 | Validate Study has ≥ 5 Problem Instances before Experiment begins | Unit, Validation rejection | 🚧 `tests/unit/test_problem_repository.py` |
| FR-33 | Validate Study Problem Instance set covers diversity rules (D-2, D-3) | Unit, Validation rejection | 🚧 `tests/unit/test_problem_repository.py` |
| FR-05 | Store AlgorithmInstance with all required fields | Unit, Validation rejection | 🚧 `tests/unit/test_algorithm_registry.py` |
| FR-06 | Reject unpinned code_reference | Validation rejection | ✅ `tests/e2e/test_uc02_contribute_algorithm.py` |
| FR-07 | Require non-empty configuration_justification | Validation rejection | ✅ `tests/e2e/test_uc02_contribute_algorithm.py` |
| FR-08 | Enforce pre-registration gate; reject modifications after lock | Pre-registration gate | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-09 | Deterministic seed assignment from seed_strategy | Integration, Reproducibility | 🚧 `tests/e2e/test_uc05_reproducibility.py` |
| FR-10 | Auto-capture execution environment per Experiment | Integration, Reproducibility | 🚧 `tests/e2e/test_uc05_reproducibility.py` |
| FR-11 | Run isolation — no shared mutable state between Runs | Integration | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-12 | Record failed Runs with reason; never skip silently | Integration | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-13 | Compute all four Standard Reporting Set metrics | Integration, Statistical validity | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-14 | Record PerformanceRecords at log-scale + improvement schedule | Unit | 🚧 `tests/unit/test_experiment_runner.py` |
| FR-15 | Require all three analysis levels before generating report | Statistical validity | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-16 | Apply multiple-testing correction when declared | Statistical validity | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-17 | All entities carry RFC 4122 UUID; no path-based IDs | Unit, Integration | 🚧 `tests/unit/test_reproducibility_layer.py` |
| FR-18 | Artifact archive contains all required records | Reproducibility | 🚧 `tests/e2e/test_uc05_reproducibility.py` |
| FR-19 | Cross-entity references use IDs only, no file paths | Unit | 🚧 `tests/unit/test_reproducibility_layer.py` |
| FR-20 | Generate ResearcherReport and PractitionerReport with scope field | Integration | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-21 | Mandatory limitations section; no ranking output | Constraint enforcement | 🚧 `tests/e2e/test_uc03_audience_report.py` |
| FR-22 | Raw Data export in open machine-readable format | Open format compliance | 🚧 `tests/unit/test_reporting.py` |
| FR-23 | Export Experiment data to at least one supported external format | Interoperability | ✅ `tests/interop/test_ioh_export.py` |
| FR-24 | Return non-empty information-loss manifest on every export call | Interoperability | ✅ `tests/interop/test_ioh_export.py` |
| FR-25 | Reject unsupported formats and exports missing mandatory fields | Interoperability | 🚧 `tests/interop/test_ecosystem_bridge.py` |
| FR-26 | No undocumented field mappings in export bridge | Interoperability | 🚧 `tests/interop/test_ecosystem_bridge.py` |

---

## NFR-to-Test Mapping

| NFR | Quality attribute | Test Category | Test file / procedure |
|---|---|---|---|
| NFR-REPRO-01 | Reproducibility | Reproducibility | 🚧 `tests/e2e/test_uc05_reproducibility.py` — formal procedure defined below |
| NFR-STAT-01 | Statistical validity | Statistical validity | 🚧 `tests/e2e/test_uc01_researcher_study.py` — assert `AnalysisIncompleteError` raised when any level skipped |
| NFR-INTEROP-01 | Ecosystem interoperability | Interoperability | ✅ `tests/interop/test_ioh_export.py` — manifest non-empty assertion on every `export()` call |
| NFR-OPEN-01 | Open data and code | Open format compliance | 🚧 `tests/unit/test_reporting.py` — assert export parseable by `json`/`csv` stdlib only |
| NFR-MODULAR-01 | Extensibility | Plugin | ✅ `tests/e2e/test_uc02_contribute_algorithm.py`; 🚧 `tests/e2e/test_uc04_contribute_problem.py` — register and use a third-party adapter without modifying core |
| NFR-USABILITY-01 | Minimal onboarding friction | Usability | Manual: `docs/06-tutorials/01-cmd-first-study.md` completable in ≤30 min; `NevergradAdapter` in ≤14 boilerplate lines (line-count asserted in 🚧 `tests/interop/test_nevergrad_adapter.py`) |

---

## Reproducibility Test Procedure

**Requirement:** NFR-REPRO-01 — the same Study, executed twice with the same seed strategy and
identical software environment, MUST produce bit-identical Result Aggregates.

**Test file:** 🚧 `tests/e2e/test_uc05_reproducibility.py`

### Procedure

```
Step 1 — First execution
  a. Construct a StudyRecord with:
       - two Algorithm Instances (one native, one NevergradAdapter wrapping a deterministic optimizer)
       - one Problem Instance (deterministic synthetic function; no randomness in evaluate())
       - repetitions = 5, budget = 50
       - seed_strategy = "sequential_from_42"
  b. Lock the Study.
  c. Execute the Study. Capture ExperimentRecord A:
       - all RunRecord.seed values
       - all PerformanceRecord sequences per Run (evaluation_number, objective_value, best_so_far)
       - all ResultAggregate metric values for the four Standard Reporting Set metrics

Step 2 — Second execution (fresh process)
  a. Reconstruct the same StudyRecord from its archived JSON (not from in-memory Python objects).
  b. Execute the Study in a separate Python process (subprocess.run) to guarantee
     no shared in-memory state survives between executions.
  c. Capture ExperimentRecord B using the same fields as Step 1c.

Step 3 — Comparison assertions
  a. For each (problem_id, algorithm_id, repetition_index) triplet:
       assert RunRecord_A.seed == RunRecord_B.seed
  b. For each Run:
       assert PerformanceRecord sequences are element-wise equal:
         evaluation_number, objective_value, best_so_far
  c. For each (problem_id, algorithm_id) pair:
       assert all four Standard Reporting Set metrics are numerically equal (== not ≈):
         QUALITY-BEST_VALUE_AT_BUDGET, RELIABILITY-SUCCESS_RATE,
         ROBUSTNESS-RESULT_STABILITY, ANYTIME-ECDF_AREA

Step 4 — Environment divergence check (informational, non-blocking)
  d. Log a warning if ExperimentRecord_A.execution_environment differs from B
     in any package version field; do not fail the test on environment differences.
```

### Pass condition

All assertions in Step 3 pass without exception. Any assertion failure is a reproducibility
regression and MUST block merge.

### Exclusions

- `elapsed_time` fields are excluded from comparison (wall-clock time is non-deterministic)
- `run_id` and `experiment_id` UUIDs are excluded (generated fresh per execution by design)

---

## Acceptance Criteria per Requirement Class

### Functional Requirements (FR-XX)

Accepted when the test file in the FR-to-Test Mapping table above passes for that FR's row.
For integration tests, "passes" means all expected postconditions hold and no expected rejection
silently succeeds.

### Non-Functional Requirements (NFR-XX)

Accepted when the NFR-specific test category passes at the defined threshold. Measurable
pass/fail criteria for each NFR are in the individual NFR documents
(`04-non-functional-requirements/02-nfr-repro-01.md` through `07-nfr-usability-01.md`).
NFR-REPRO-01 additionally requires the bit-identical Result Aggregates procedure defined above.

### Constraints (CONST-XX)

Accepted when the constraint enforcement test confirms that every API path that could violate the
constraint is blocked at the system boundary — not by documentation, but by code that rejects the
violating call.

### Use Cases (UC-XX)

Accepted when all three of the following hold:
1. All Main Flow steps produce their expected postconditions in an automated end-to-end integration test
2. Each named Failure Scenario is exercised and the system produces the expected rejection or warning (not a silent failure or an incorrect success)
3. A corresponding tutorial in `docs/06-tutorials/` demonstrates the UC for a human user and a representative user can complete it within the stated time target

---

## Pending Use Cases — Learner Actor (UC-07 through UC-11)

UC-07 through UC-11 (Learner actor use cases) are fully expanded with main flows, preconditions, and failure scenarios. Their functional requirements (FR-27..FR-31) are defined in
[`09-fr-4.8-learner-actor.md`](../03-functional-requirements/09-fr-4.8-learner-actor.md) and are
**DEFERRED to Phase 4** (IMPL-044..IMPL-046). They cannot be accepted until implementation is complete.

| UC | Title | FR | Planned test category | ROADMAP ref |
|---|---|---|---|---|
| UC-07 | Algorithm Visualisation | FR-27 | Usability, visualisation rendering tests | IMPL-044 |
| UC-08 | Contextual Algorithm Help | FR-28 | Usability, contextual explanation tests | IMPL-045 |
| UC-09 | Socratic Guided Deduction | FR-29 | Usability, LLM-as-judge Socratic scoring | IMPL-045 |
| UC-10 | Algorithm History and Evolution | FR-30 | Usability, genealogy graph tests | IMPL-046 |
| UC-11 | Learner Explores Study Results | FR-31 | Usability, constraint enforcement, read-only access tests | IMPL-044..046 |

These use cases will be accepted once:
1. FR-27..FR-31 are implemented (Phase 4)
2. The planned test categories above pass
3. Tutorials in `docs/06-tutorials/05` through `07` are verified as completable
