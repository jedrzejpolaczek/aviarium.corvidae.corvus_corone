# Functional Requirements — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: The precise WHAT. Each FR states a verifiable capability the system must provide.
Every FR traces to a MANIFESTO principle and to at least one Use Case that exercises it.

NARRATIVE POSITION:
  MANIFESTO (WHY) → Use Cases (HOW actors interact) → Functional Requirements (WHAT system does)
  Functional Requirements → C2/C3 design (WHERE in the architecture it lives)
  Functional Requirements → Acceptance Tests (HOW we verify it)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                         : each FR cites the principle that requires it
  ← use-cases.md                                           : each FR is exercised by at least one UC
  → docs/02-design/02-architecture/c2-containers.md        : container responsible for each FR group
  → docs/03-technical-contracts/data-format.md             : entity schemas that FRs operate on
  → docs/03-technical-contracts/interface-contracts.md     : interfaces that implement FRs
  → docs/03-technical-contracts/metric-taxonomy.md         : metrics required by §4.4 FRs
  → docs/04_scientific_practice/methodology/              : methodology documents that FRs operationalize
  → docs/05_community/versioning-governance.md             : versioning FRs connect here
  → acceptance-test-strategy.md                            : each FR has a designated test category
  → traceability-matrix.md                                 : full cross-reference table

NOTE ON CONTAINER MAPPING:
  The subsection groupings (4.1–4.7) correspond to C2 container responsibilities defined in
  docs/02-design/02-architecture/c2-containers.md. When C2 container descriptions are complete
  (REF-TASK-0026), each FR should be linked to the specific container responsible for it.
-->

---

## 4.1 Problem Repository

*Stores, retrieves, versions, and validates benchmark Problem Instances. Source: MANIFESTO Principles 4–7.*
*Connects to: `docs/03-technical-contracts/data-format.md` §2.1; `docs/03-technical-contracts/interface-contracts.md` Problem interface; `use-cases.md` UC-04.*

**FR-01:** The system MUST store Problem Instance records conforming to the schema defined in `docs/03-technical-contracts/data-format.md` §2.1, including all required fields: `id` (UUID), `name`, `version`, search space descriptors, objective specification, evaluation budget, landscape characteristics, and provenance.
- Source: MANIFESTO Principles 4, 7
- Connects to: `docs/03-technical-contracts/data-format.md` §2.1; `docs/03-technical-contracts/interface-contracts.md` Problem interface

**FR-02:** The system MUST validate Problem Instance completeness on registration: `dimensions` must equal `len(variables)`; variable bounds must be valid (lower < upper for continuous); all required fields must be present. Invalid submissions MUST be rejected with a specific error message identifying the violation.
- Source: MANIFESTO Principle 7
- Connects to: `docs/03-technical-contracts/data-format.md` §2.1 validation rules

**FR-03:** The system MUST support Problem Instance versioning — modifying a Problem Instance produces a new version rather than overwriting the existing record. A Study references a specific version; that version MUST remain retrievable for the lifetime of the Study.
- Source: MANIFESTO Principles 6, 21
- Connects to: `docs/03-technical-contracts/data-format.md` §2.1; `docs/05_community/versioning-governance.md`

**FR-04:** The system MUST prevent inclusion of a Problem Instance version that differs from the version declared in the parent Study plan.
- Source: MANIFESTO Principle 21
- Connects to: `docs/03-technical-contracts/data-format.md` §2.3 (Study), §2.1 (Problem Instance)

---

## 4.2 Algorithm Registry

*Registers, configures, and manages Algorithm Implementations. Enforces the Algorithm / Algorithm Instance / Implementation distinction. Source: MANIFESTO Principles 8–11.*
*Connects to: `docs/03-technical-contracts/data-format.md` §2.2; `docs/03-technical-contracts/interface-contracts.md` Algorithm interface; `use-cases.md` UC-02.*

**FR-05:** The system MUST store Algorithm Instance records conforming to the schema defined in `docs/03-technical-contracts/data-format.md` §2.2, including: `id` (UUID), `name`, `algorithm_family`, `hyperparameters`, `configuration_justification`, `code_reference` (version-pinned), `language`, `framework`, `framework_version`, `known_assumptions`, and provenance fields.
- Source: MANIFESTO Principles 8, 10
- Connects to: `docs/03-technical-contracts/data-format.md` §2.2; `docs/03-technical-contracts/interface-contracts.md` Algorithm interface

**FR-06:** The system MUST reject Algorithm Instance registration if the `code_reference` is not resolvable or is not version-pinned. An unpinned reference (e.g., a branch name rather than a commit hash or package version) MUST be rejected with an explicit error.
- Source: MANIFESTO Principles 8, 19
- Connects to: `docs/03-technical-contracts/data-format.md` §2.2 validation rules

**FR-07:** The system MUST require a non-empty `configuration_justification` for every Algorithm Instance. A registration with an empty or missing justification MUST be rejected.
- Source: MANIFESTO Principle 10 (configuration fairness)
- Connects to: `docs/03-technical-contracts/data-format.md` §2.2

---

## 4.3 Experiment Runner

*Executes Studies, manages seeds, enforces Run independence and the pre-registration gate. Source: MANIFESTO Principles 16–18.*
*Connects to: `docs/03-technical-contracts/data-format.md` §2.4–§2.6; `docs/03-technical-contracts/interface-contracts.md` Runner interface; `docs/04_scientific_practice/methodology/benchmarking-protocol.md`; `use-cases.md` UC-01.*

**FR-08:** The system MUST enforce the pre-registration gate: the Study's problem set, algorithm set, experimental design, and hypotheses MUST be locked before any Run is executed. Any attempt to modify these fields after locking MUST be rejected and logged with a timestamp.
- Source: MANIFESTO Principle 16; `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Steps 1–5
- Connects to: `docs/03-technical-contracts/data-format.md` §2.3 (Study)

**FR-09:** The system MUST assign all Run seeds — the Researcher MUST NOT control individual seed values. Seeds MUST be assigned deterministically from the Study's declared `seed_strategy` before any Run begins.
- Source: MANIFESTO Principle 18
- Connects to: `docs/03-technical-contracts/data-format.md` §2.5 (Run); `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Step 6

**FR-10:** The system MUST record the full execution environment for each Experiment: operating system, hardware specification, Python version, and dependency versions. This record MUST be captured automatically, not entered manually.
- Source: MANIFESTO Principle 19
- Connects to: `docs/03-technical-contracts/data-format.md` §2.4 (Experiment.execution_environment)

**FR-11:** Each Run MUST execute without any shared mutable state with other Runs in the same Experiment. The runner MUST enforce process isolation or equivalent isolation guarantee.
- Source: MANIFESTO Principle 18
- Connects to: `docs/03-technical-contracts/data-format.md` §2.5 (Run); `docs/03-technical-contracts/interface-contracts.md` Runner interface

**FR-12:** The system MUST record a failed Run with its failure reason and timestamp rather than silently skipping it. A Study with failed Runs MUST NOT be reported as if all planned Runs completed.
- Source: MANIFESTO Principle 19
- Connects to: `docs/03-technical-contracts/data-format.md` §2.5 (Run.status, Run.failure_reason)

---

## 4.4 Measurement & Analysis Engine

*Collects Performance Records, computes metrics, and runs three-level statistical analysis. Source: MANIFESTO Principles 12–15.*
*Connects to: `docs/03-technical-contracts/metric-taxonomy.md`; `docs/04_scientific_practice/methodology/statistical-methodology.md`; `docs/03-technical-contracts/data-format.md` §2.6–§2.7; `use-cases.md` UC-01.*

**FR-13:** The system MUST compute all four Standard Reporting Set metrics for every completed set of Runs for a (problem, algorithm) pair: `QUALITY-BEST_VALUE_AT_BUDGET`, `RELIABILITY-SUCCESS_RATE`, `ROBUSTNESS-RESULT_STABILITY`, `ANYTIME-ECDF_AREA`. Results MUST be stored in the Result Aggregate record.
- Source: MANIFESTO Principles 12, 14
- Connects to: `docs/03-technical-contracts/metric-taxonomy.md` Standard Reporting Set; `docs/03-technical-contracts/data-format.md` §2.7

**FR-14:** The system MUST record Performance Records at sufficient granularity to reconstruct full anytime performance curves. The logging strategy (every evaluation vs. sampled) MUST be declared and archived as part of the Study plan.
- Source: MANIFESTO Principle 14
- Connects to: `docs/03-technical-contracts/data-format.md` §2.6 (Performance Record)

**FR-15:** The system MUST NOT produce a Study report without completing all three levels of analysis: Level 1 (exploratory: summary statistics, visualizations), Level 2 (confirmatory: pre-registered hypothesis tests), Level 3 (practical significance: effect sizes). Skipping any level MUST be treated as an analysis error.
- Source: MANIFESTO Principle 13; NFR-STAT-01
- Connects to: `docs/04_scientific_practice/methodology/statistical-methodology.md`; `docs/03-technical-contracts/metric-taxonomy.md`

**FR-16:** When confirmatory analysis involves more than one hypothesis, the system MUST apply multiple-testing correction using the method declared in the Study plan. The correction method and adjusted p-values MUST appear in the Researcher Report.
- Source: MANIFESTO Principle 15
- Connects to: `docs/04_scientific_practice/methodology/statistical-methodology.md`; `docs/03-technical-contracts/data-format.md` §2.7

---

## 4.5 Reproducibility Layer

*Versions all Artifacts, supports open data publication, and enables long-term re-execution. Source: MANIFESTO Principles 19–22; ADR-001.*
*Connects to: `docs/03-technical-contracts/data-format.md` §1; `docs/05_community/versioning-governance.md`; `docs/02-design/02-architecture/adr/ADR-001-library-with-server-ready-data-layer.md`; `use-cases.md` UC-05.*

**FR-17:** Every entity (Study, Experiment, Run, Algorithm Instance, Problem Instance, Result Aggregate) MUST carry a globally unique identifier in UUID format. Local file paths MUST NOT serve as entity identifiers.
- Source: MANIFESTO Principles 19, 21; ADR-001 (server-compatibility constraint)
- Connects to: `docs/03-technical-contracts/data-format.md` §1; `docs/02-design/02-architecture/adr/ADR-001-library-with-server-ready-data-layer.md`

**FR-18:** The system MUST be capable of producing an Artifact archive for any completed Experiment containing: Study plan record, all Algorithm Instance records (with `code_reference`), all Problem Instance records (versioned), all Run records (with seeds and `execution_environment`), and all Result Aggregates.
- Source: MANIFESTO Principle 19
- Connects to: `docs/03-technical-contracts/data-format.md` §2.3–§2.7; `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Step 8

**FR-19:** Cross-entity references MUST use entity IDs only — no entity field may reference another entity by file path, directory structure, or local naming convention.
- Source: ADR-001 (server-compatibility constraint)
- Connects to: `docs/03-technical-contracts/data-format.md` §1; `docs/03-technical-contracts/interface-contracts.md`

---

## 4.6 Reporting & Visualization

*Generates multi-audience reports with explicit limitations and raw data export. Source: MANIFESTO Principles 23–25.*
*Connects to: `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Steps 7–8; `use-cases.md` UC-01, UC-03; `REF-TASK-0034`.*

**FR-20:** The system MUST produce at minimum two distinct report types per completed Experiment:
- **Researcher Report:** full methodology description, all computed metrics, statistical test outputs with adjusted p-values and effect sizes, and a mandatory limitations section.
- **Practitioner Report:** performance summaries per problem characteristic, explicit scope statements, algorithm behavior descriptions — without raw statistical tables.
- Source: MANIFESTO Principle 25
- Connects to: `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Step 7; `REF-TASK-0034`

**FR-21:** Every system-generated report MUST include an explicit limitations section that states: which Problem Instances were tested, which Algorithm Instances were compared, the budget used, and the boundary of valid conclusions. Claims that exceed this boundary MUST NOT appear in system-generated outputs (CONST-SCI-06).
- Source: MANIFESTO Principle 24; `constraints.md` CONST-SCI-05, CONST-SCI-06
- Connects to: `constraints.md` Scientific Constraints

**FR-22:** The system MUST provide a Raw Data export alongside reports: all Result Aggregates and Performance Records in a machine-readable, open format that allows independent analysis without the Corvus Corone library.
- Source: MANIFESTO Principles 20, 25
- Connects to: `docs/03-technical-contracts/data-format.md` §3; `non-functional-requirements.md` NFR-OPEN-01

---

## 4.7 Ecosystem Integration

*Provides COCO, Nevergrad, and IOHprofiler compatibility. Source: MANIFESTO Principle 26.*
*Connects to: `docs/03-technical-contracts/data-format.md` §4; `docs/03-technical-contracts/interface-contracts.md` Ecosystem Bridge; `use-cases.md` UC-06; `non-functional-requirements.md` NFR-INTEROP-01.*

**FR-23:** The system MUST support export of Experiment results to COCO archive format. The export MUST conform to the field mapping defined in `docs/03-technical-contracts/data-format.md` §4 (COCO mapping). (`REF-TASK-0005`)
- Source: MANIFESTO Principle 26; NFR-INTEROP-01
- Connects to: `docs/03-technical-contracts/data-format.md` §4 COCO mapping

**FR-24:** The system MUST support export of Performance Records to IOHprofiler `.dat` format, loadable without error in IOHanalyzer. The export MUST conform to the field mapping in `docs/03-technical-contracts/data-format.md` §4 (IOHprofiler mapping). (`REF-TASK-0007`)
- Source: MANIFESTO Principle 26; NFR-INTEROP-01
- Connects to: `docs/03-technical-contracts/data-format.md` §4 IOHprofiler mapping

**FR-25:** The system MUST support wrapping of Nevergrad optimizers as Algorithm Instances via the Algorithm interface defined in `docs/03-technical-contracts/interface-contracts.md`. The adapter MUST allow Nevergrad-wrapped algorithms to participate in Studies identically to native Algorithm Instances. (`REF-TASK-0006`)
- Source: MANIFESTO Principle 26; NFR-INTEROP-01
- Connects to: `docs/03-technical-contracts/interface-contracts.md` Algorithm interface; `docs/03-technical-contracts/data-format.md` §4 Nevergrad mapping

**FR-26:** Every export operation MUST produce an information-loss manifest: a structured record listing every field dropped or approximated during format mapping, with the reason. The manifest MUST accompany the export file.
- Source: MANIFESTO Principle 24 (transparency of limitations); NFR-INTEROP-01
- Connects to: `docs/03-technical-contracts/data-format.md` §4
