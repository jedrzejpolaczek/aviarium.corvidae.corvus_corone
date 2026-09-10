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
  ← 03-functional-requirements/01-index.md                                : every FR must be covered by a test category
  ← 04-non-functional-requirements/01-index.md                            : every NFR has a designated test category
  ← 05-constraints/01-index.md                                            : CONST-XX constraints have enforcement tests
  ← 02-use-cases/01-index.md                                              : every UC must have an end-to-end test
  → docs/02-design/02-architecture/03-c4-leve2-containers/04-c4-leve3-components/01-c4-l3-components/01-c4-l3-components.md           : test file paths aligned to C3 components
  
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
| Constraint enforcement tests | CONST-SCI-01 through CONST-SCI-06 cannot be violated by any API path | FR-21; `05-constraints/01-index.md` Scientific Constraints | UC-03 F1 |
| Usability tests | Timed tutorial completion within stated targets | NFR-USABILITY-01 | UC-01, UC-02 |
| Open format compliance tests | Raw Data export formats are on the approved open-format list | NFR-OPEN-01; FR-22; CONST-COM-03 | UC-01 Step 10 |
| Guidance quality tests | A rejection states what the researcher has to decide, not only which field is absent: every unresolved decision in one response, the rule each message enforces, and the remedies available | FR-27, FR-29, FR-30 | UC-01 F1–F3 |
| Interface conformance tests | The public surface is exactly the documented one, and the command line is a subset of it rather than a parallel surface | FR-28, FR-39, FR-40, FR-41, FR-42 | UC-01 – UC-06 |

---

## FR-to-Test Mapping

Every FR maps to at least one test file. Files marked ✅ exist; files marked 🚧 are planned
and will be created as the corresponding feature is implemented.

> **On the ✅ marks.** Four rows carried ✅ against
> `tests/e2e/test_uc01_researcher_study.py` and `tests/e2e/test_uc02_contribute_algorithm.py`,
> which do not exist. Those were the interface stubs described under *Acceptance Scenarios*
> below: a temporary instrument for testing whether the contracts were implementable, removed
> once ADR-013 and ADR-017 replaced the lifecycle and seed strategy they encoded. The ticks
> stayed behind. They are corrected here, and the assertions that do exist —
> `tests/unit/test_repository_interface.py`, the IMPL-010 contract suite — are cited where
> they genuinely apply.

| FR | Description (short) | Test Category | Test File |
|---|---|---|---|
| FR-01 | Store ProblemInstance with all required fields | Unit, Validation rejection | ✅ `tests/unit/test_repository_interface.py` (round-trip, deep copy); 🚧 `tests/unit/test_problem_repository.py` (full required-field set) |
| FR-02 | Validate ProblemInstance completeness on registration | Validation rejection | ✅ `tests/unit/test_repository_interface.py` (case c, missing `name`); 🚧 `tests/unit/test_problem_repository.py` (cases a and b) |
| FR-03 | A revision is a new entity; the original stays retrievable and carries `superseded_by` (ADR-020) | Unit | ✅ `tests/unit/test_repository_interface.py` (deprecated entity still retrievable by id); 🚧 `tests/unit/test_problem_repository.py` (`superseded_by` lineage) |
| FR-04 | A Study resolves to the entity it referenced, for the lifetime of the Study (ADR-020) | Integration | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-32 | Validate Study has ≥ 5 Problem Instances before Experiment begins | Unit, Validation rejection | 🚧 `tests/unit/test_problem_repository.py` |
| FR-33 | Validate Study Problem Instance set covers diversity rules (D-2, D-3) | Unit, Validation rejection | 🚧 `tests/unit/test_problem_repository.py` |
| FR-05 | Store AlgorithmInstance with all required fields | Unit, Validation rejection | ✅ `tests/unit/test_repository_interface.py` (round-trip); 🚧 `tests/unit/test_algorithm_registry.py` (every field `03-algorithm-instance.md` marks required) |
| FR-06 | Reject unpinned code_reference | Validation rejection | ✅ `tests/unit/test_repository_interface.py` |
| FR-07 | Require non-empty configuration_justification | Validation rejection | ✅ `tests/unit/test_repository_interface.py` |
| FR-08 | Enforce pre-registration gate; reject modifications after lock | Pre-registration gate | ✅ `tests/unit/test_repository_interface.py` (`StudyAlreadyLockedError` on re-lock, draft → locked transition); 🚧 `tests/e2e/test_uc01_researcher_study.py` (field immutability, timestamped log) |
| FR-09 | Deterministic seed assignment from seed_strategy | Integration, Reproducibility | 🚧 `tests/e2e/test_uc05_reproducibility.py` |
| FR-10 | Auto-capture execution environment per Experiment | Integration, Reproducibility | 🚧 `tests/e2e/test_uc05_reproducibility.py` |
| FR-11 | Run isolation — no shared mutable state between Runs | Integration | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-12 | Record failed Runs with reason; never skip silently | Integration | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-13 | Compute all four Standard Reporting Set metrics | Integration, Statistical validity | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-14 | Record PerformanceRecords at log-scale + improvement schedule | Unit | 🚧 `tests/unit/test_experiment_runner.py` |
| FR-15 | Require all three analysis levels before generating report | Statistical validity | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-16 | Apply multiple-testing correction when declared | Statistical validity | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-17 | All entities carry RFC 4122 UUID; no path-based IDs | Unit, Integration | ✅ `tests/unit/test_repository_interface.py` (every `register`/`create` returns a UUID); 🚧 `tests/unit/test_reproducibility_layer.py` (no path-valued reference fields) |
| FR-18 | Artifact archive contains all required records | Reproducibility | 🚧 `tests/e2e/test_uc05_reproducibility.py` |
| FR-19 | Cross-entity references use IDs only, no file paths | Unit | 🚧 `tests/unit/test_reproducibility_layer.py` |
| FR-20 | Generate ResearcherReport and PractitionerReport with scope field | Integration | 🚧 `tests/e2e/test_uc01_researcher_study.py` |
| FR-21 | Mandatory limitations section; no ranking output | Constraint enforcement | 🚧 `tests/e2e/test_uc03_audience_report.py` |
| FR-22 | Raw Data export in open machine-readable format | Open format compliance | 🚧 `tests/unit/test_reporting.py` |
| FR-23 | Export Experiment data to at least one supported external format | Interoperability | ✅ `tests/interop/test_ioh_export.py` |
| FR-24 | Return non-empty information-loss manifest on every export call | Interoperability | ✅ `tests/interop/test_ioh_export.py` |
| FR-25 | Reject unsupported formats and exports missing mandatory fields | Interoperability | 🚧 `tests/interop/test_ecosystem_bridge.py` |
| FR-26 | No undocumented field mappings in export bridge | Interoperability | 🚧 `tests/interop/test_ecosystem_bridge.py` |
| FR-27 | Report every unresolved design decision in one response, not the first | Guidance quality, Validation rejection | 🚧 `tests/unit/test_study_design_guidance.py` |
| FR-28 | No silent defaults on parameters with methodological consequences | Interface conformance, Validation rejection | 🚧 `tests/unit/test_study_design_guidance.py` |
| FR-29 | Every validation message names the rule, principle or ADR it enforces | Guidance quality | 🚧 `tests/unit/test_study_design_guidance.py` |
| FR-30 | Name the deficient diversity axis and both remedies at `lock_study()` | Guidance quality, Validation rejection | 🚧 `tests/unit/test_study_design_guidance.py` |
| FR-31 | Exploratory Study declarable, and carried into both Report scope statements | Constraint enforcement, Statistical validity | 🚧 `tests/unit/test_study_design_guidance.py` |
| FR-39 | Public namespace equals the function set of `04-public-api-contract.md` | Interface conformance | 🚧 `tests/unit/test_public_api_surface.py` |
| FR-40 | Every CLI command delegates to a facade function; no command-only capability | Interface conformance | 🚧 `tests/cli/test_cli_surface.py` |
| FR-41 | Results on stdout, diagnostics on stderr; error text starts with the class name | Interface conformance | 🚧 `tests/cli/test_cli_surface.py` |
| FR-42 | Exit codes distinguish failure categories; failed Runs still exit `0` | Interface conformance | 🚧 `tests/cli/test_cli_surface.py` |

FR-34 – FR-38 are `[DEFERRED]` (SRS §4.9, Learner actor, ROADMAP Phase 4) and are deliberately absent from this table. A deferred requirement is a decision, not a gap; it enters here when the phase opens.

> **What the nine rows above cost to write.** Nothing: each of those requirements already
> carries an *Accepted when* clause naming a concrete assertion — set equality of the public
> namespace against the contract, the two streams captured separately, exit `0` for an
> Experiment whose individual Runs failed. The rows were missing, not the criteria. They were
> added by REF-TASK-0049 after the consistency audit found that this document claimed to cover
> every FR while covering FR-01 – FR-26, FR-32 and FR-33.

---

## NFR-to-Test Mapping

| NFR | Quality attribute | Test Category | Test file / procedure |
|---|---|---|---|
| NFR-REPRO-01 | Reproducibility | Reproducibility | 🚧 `tests/e2e/test_uc05_reproducibility.py` — formal procedure defined below |
| NFR-STAT-01 | Statistical validity | Statistical validity | 🚧 `tests/e2e/test_uc01_researcher_study.py` — assert `AnalysisIncompleteError` raised when any level skipped |
| NFR-INTEROP-01 | Ecosystem interoperability | Interoperability | ✅ `tests/interop/test_ioh_export.py` — manifest non-empty assertion on every `export()` call |
| NFR-OPEN-01 | Open data and code | Open format compliance | 🚧 `tests/unit/test_reporting.py` — assert export parseable by `json`/`csv` stdlib only |
| NFR-MODULAR-01 | Extensibility | Plugin | 🚧 `tests/e2e/test_uc02_contribute_algorithm.py`; 🚧 `tests/e2e/test_uc04_contribute_problem.py` — register and use a third-party adapter without modifying core |
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

Accepted when the NFR-specific test category passes at the defined threshold. Thresholds are to be
set by the measurable criterion on each NFR (REF-TASK-0010, complete). The test category and the
pass/fail line is not drawn — except for NFR-REPRO-01, whose pass condition is the
bit-identical Result Aggregates assertion defined in the Reproducibility Test Procedure above.

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

## Acceptance Scenarios for UC-01 and UC-02

These scenarios were originally expressed as executable assertions against a set of interface
stubs under `packages/corvus-corone-lib/tests/e2e/`. Those stubs were a temporary instrument for
testing whether the contracts were implementable, not production code, and they encoded a Study
lifecycle and seed strategy that ADR-013 and ADR-017 have since replaced. The scenarios are
recorded here in the form the corrected contracts require, so that they survive the removal of
the instrument and can be reimplemented against the real library.

Each numbered scenario is one acceptance obligation. A scenario is met when an automated test
asserts it against the production implementation.

### UC-01 — Design and execute a reproducible benchmarking Study

**Study lifecycle (ADR-013, ADR-021, FR-08)**

1. `create_study()` returns a Study whose `status` is `"draft"`.
2. `update_study()` on a draft applies the change; the returned Study reflects it.
3. `lock_study()` transitions `status` to `"locked"`.
4. `update_study()` on a locked Study raises `StudyAlreadyLockedError` and leaves the stored
   Study byte-identical.
5. `lock_study()` on a Study with an empty `pre_registered_hypotheses` list raises
   `ValidationError` naming that field and the reason it is required.
6. `run()` on a draft Study raises `StudyNotLockedError`.
7. `research_question` and `pre_registered_hypotheses` are preserved verbatim through the lock
   transition.

**PerformanceRecord strategy (ADR-002, ADR-004, ADR-005)**

8. Every Run produces at least one PerformanceRecord.
9. Exactly one record per Run carries a `trigger_reason` containing `end_of_run`, and its
   `evaluation_number` equals `Run.budget_used`.
10. Every scheduled checkpoint in `Study.log_scale_schedule` up to the budget has a
    corresponding record.
11. `evaluation_number` is strictly increasing within a Run; no duplicates.
12. Every `trigger_reason` value is one of the seven defined in `01-data-format/07-performance-record.md`.
13. A record whose `trigger_reason` contains `improvement` has `is_improvement` true; a record
    whose reason is `scheduled` or `end_of_run` alone may have it false.
14. `best_so_far` is non-increasing across the record sequence of a minimisation Run.
15. An evaluation that is both a scheduled checkpoint and an improvement produces exactly one
    record whose `trigger_reason` is `both`, not two records.

**Improvement epsilon (ADR-004)**

16. With `improvement_epsilon` null, every strict improvement produces an improvement record.
17. With `improvement_epsilon` set to a value larger than the observed improvements, no
    improvement-only records are written.
18. A non-null `improvement_epsilon` appears in the limitations section of both generated
    Reports.

**Storage cap (ADR-005)**

19. Once `max_records_per_run` is reached, no further improvement-only records are written.
20. Scheduled records continue after the cap.
21. The end-of-run record is written regardless of the cap.
22. `Run.cap_reached_at_evaluation` is set to the evaluation at which improvement-only logging
    stopped, and is null when no cap was configured.
23. The cap appears in the limitations section of both generated Reports.

**Reproducibility (ADR-017, MANIFESTO Principle 18)**

24. All Run seeds within an Experiment are unique for a given problem and algorithm pair; a
    duplicate raises `SeedCollisionError`.
25. Two Runs with the same seed, Problem Instance and Algorithm Instance produce identical
    PerformanceRecord sequences.
26. Two Runs differing only in seed produce different objective sequences.
27. Every Run seed is reproducible from `Study.root_seed` alone, by spawning the
    `SeedSequence` in run-plan order.

**Postconditions (FR-09, FR-13, FR-20)**

28. `Experiment.status` is `"completed"` after a successful execution.
29. The number of Runs equals problems x algorithms x repetitions.
30. A ResultAggregate exists for every problem and algorithm pair, with `n_runs` equal to the
    repetition count.
31. Every ResultAggregate carries the four Standard Reporting Set metrics.
32. Exactly two Reports are generated, one `researcher` and one `practitioner` (ADR-019).
33. Both Reports have a non-empty limitations section, and the scope statement names the
    Problem Instances actually tested.
34. Every Run references its Experiment, and every Experiment references its Study.

### UC-02 — Contribute an Algorithm Implementation

**Interface compliance (FR-05, `03-algorithm-interface.md`)**

35. A conforming adapter exposes `initialize`, `suggest`, `observe`,
    `get_supported_variable_types` and `get_metadata`.
36. `suggest()` returns a list of solutions whose length equals `batch_size`, for
    `batch_size` of 1 and greater.
37. Every suggested solution lies within the declared search space bounds.
38. `observe()` returns `None` and does not raise, including for algorithms that ignore
    feedback.
39. `get_supported_variable_types()` returns a non-empty list drawn from `continuous`,
    `integer`, `categorical`, and is stable across calls.

**Registration validation (FR-06, FR-07)**

40. An adapter missing `observe` or `suggest` is rejected with `InterfaceViolationError`
    (UC-02 F1).
41. A `code_reference` that is not version-pinned is rejected with `CodeReferenceError`
    (UC-02 F2).
42. An empty `configuration_justification` is rejected with `ValidationError` (UC-02 F3).
43. A missing required metadata field is rejected with `ValidationError` naming the field
    (UC-02 F4).
44. `supported_variable_types` in the metadata matches the value returned by the method.

**Smoke run and isolation**

45. A registered adapter completes a single Run within budget and produces at least one
    PerformanceRecord, including the end-of-run record.
46. The first record of every Run has `is_improvement` true.
47. The adapter runs on a higher-dimensional Problem Instance without modification.
48. `initialize()` discards all state from a previous Run: the internal generator and any
    cached best solution are reset, and two consecutive Runs with the same seed produce
    identical records.
49. The adapter creates no randomness before `initialize()` is called.
