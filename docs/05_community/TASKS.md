# Documentation Tasks

<!--
STORY ROLE: The connective tissue between documentation and implementation work.
Every incomplete section in every document is represented here as a task with an owner,
acceptance criteria, and a stable identifier that can be referenced in issue trackers.

NARRATIVE POSITION:
  All documents → TASKS.md → (what must be done to complete the documentation story)
  TASKS.md → Issue tracker (GitHub Issues, Jira, etc.) → implementation work

CONNECTS TO:
  ← All documents : every TODO: REF-TASK-dddd in any document is listed here
  → Issue tracker : each task here should have a corresponding issue in the project tracker
  → docs/02_design/01_software_requirement_specification/SRS.md : many tasks complete SRS sections
  → docs/02_design/02_architecture/ : architecture tasks feed C2/C3/C4 documents
  → docs/03_technical_contracts/ : contract tasks complete interface and data format specs
  → docs/05_community/versioning-governance.md : governance tasks complete policy sections

MAINTENANCE RULE:
  When a task is completed, update its Status field to "Done" and add the completion date.
  When a new TODO: REF-TASK-dddd is added to any document, add the corresponding entry here.
  Task IDs are permanent — never reuse an ID, even after completion.
-->

---

## Task Registry

| ID | Name | Owner | Status | Source Document |
|---|---|---|---|---|
| REF-TASK-0001 | Extend glossary from interface contracts | Technical lead | Open | `docs/GLOSSARY.md` |
| REF-TASK-0002 | Verify Schema Version definition against data-format.md | Technical lead | Open | `docs/GLOSSARY.md` |
| REF-TASK-0003 | Decide V1 scope for distributed/HPC execution | Technical lead | Decided (HPC deferred to V2) | `docs/02_design/02_architecture/c1-context.md` |
| REF-TASK-0004 | Define 15-line Algorithm Author onboarding tutorial | Library design lead | Open | `docs/02_design/02_architecture/c1-context.md` |
| REF-TASK-0005 | Define COCO format mapping in data-format.md §3 | Ecosystem integration lead | Open | `docs/02_design/02_architecture/c1-context.md` |
| REF-TASK-0006 | Define Nevergrad adapter pattern and tutorial | Library design lead | Open | `docs/02_design/02_architecture/c1-context.md` |
| REF-TASK-0007 | Define IOHprofiler export format mapping | Ecosystem integration lead | Open | `docs/02_design/02_architecture/c1-context.md` |
| REF-TASK-0008 | Complete SRS §4, §5 (criteria), §7, §8 after C2 design | Technical lead | Blocked (needs C2) | `docs/02_design/01_software_requirement_specification/SRS.md` |
| REF-TASK-0009 | Expand UC-01 and UC-02 into full use case descriptions | Technical lead | Blocked (needs C2) | `docs/02_design/01_software_requirement_specification/SRS.md` |
| REF-TASK-0010 | Add measurable criteria to all NFRs | Technical lead | Blocked (needs architecture) | `docs/02_design/01_software_requirement_specification/SRS.md` |
| REF-TASK-0011 | Define technical constraints (Python version, OS, deps) | Technical lead | Open | `docs/02_design/01_software_requirement_specification/SRS.md` |
| REF-TASK-0012 | Fill SRS §7 Interface Requirements from interface-contracts.md | Ecosystem integration lead | Blocked (needs REF-TASK-0005/0006/0007) | `docs/02_design/01_software_requirement_specification/SRS.md` |
| REF-TASK-0013 | Fill SRS §8 Acceptance Test Strategy from C2/C3 | QA / technical lead | Blocked (needs C2) | `docs/02_design/01_software_requirement_specification/SRS.md` |
| REF-TASK-0014 | Review and extend metric definitions after first studies | Methodology lead | Open (post V1) | `docs/03_technical_contracts/metric-taxonomy.md` |
| REF-TASK-0015 | Add implementation reference to all metric definitions | Analysis lead | Blocked (needs analysis module) | `docs/03_technical_contracts/metric-taxonomy.md` |
| REF-TASK-0016 | Formalize ANYTIME-ECDF_AREA computation procedure | Methodology lead | Open | `docs/03_technical_contracts/metric-taxonomy.md` |
| REF-TASK-0017 | Decide whether TIME-EVALUATIONS_TO_TARGET joins Standard Reporting Set | Methodology lead | Open | `docs/03_technical_contracts/metric-taxonomy.md` |
| REF-TASK-0018 | Add research question archetypes and tutorial links to Metric Selection Guide | Methodology lead | Open (ongoing) | `docs/03_technical_contracts/metric-taxonomy.md` |
| REF-TASK-0019 | Specify required Level 1 visualizations in statistical-methodology.md §2 | Analysis lead | Blocked (needs reporting module design) | `docs/04_scientific_practice/methodology/statistical-methodology.md` |
| REF-TASK-0020 | Specify test selection procedure and correction methods in statistical-methodology.md §3 | Methodology lead | Open | `docs/04_scientific_practice/methodology/statistical-methodology.md` |
| REF-TASK-0021 | Define minimum diversity requirements for Problem Instance selection | Methodology lead | Open | `docs/04_scientific_practice/methodology/benchmarking-protocol.md` |
| REF-TASK-0022 | Define sensitivity documentation format in Algorithm Instance schema | Methodology lead | Blocked (needs data-format.md completion) | `docs/04_scientific_practice/methodology/benchmarking-protocol.md` |
| REF-TASK-0023 | Design the Repository storage abstraction interface | Library design lead | Open | `docs/02_design/02_architecture/c1-context.md`, `ADR-001` |
| REF-TASK-0024 | Decide bulk PerformanceRecord storage format (Parquet vs HDF5) | Technical lead | Open | `docs/03_technical_contracts/data-format.md §1` |

---

## Task Details

---

### REF-TASK-0001: Extend Glossary from Interface Contracts

**Description:** Once `docs/03_technical_contracts/interface-contracts.md` and `docs/03_technical_contracts/data-format.md` are filled with real content, all new terms introduced in those documents (method parameter names, entity field names, error types, protocol-specific concepts) must be added to `docs/GLOSSARY.md` with precise definitions.

**Acceptance criteria:**
- Every public method parameter name in interface-contracts.md has a corresponding GLOSSARY entry if not already defined
- Every entity field name in data-format.md that has domain-specific semantics has a GLOSSARY entry
- No synonyms for existing terms are introduced — new entries either add new terms or refine existing ones
- All GLOSSARY entries are cross-referenced with the documents where they are used

**Owner:** Technical lead
**Depends on:** Completion of interface-contracts.md and data-format.md

---

### REF-TASK-0002: Verify Schema Version Definition Against Data-Format

**Description:** The GLOSSARY definition of "Schema Version" must be verified and updated once `docs/03_technical_contracts/data-format.md` §6 (Schema Versioning) is filled. The definition and the policy must use identical terminology.

**Acceptance criteria:**
- GLOSSARY "Schema Version" definition matches the versioning scheme described in data-format.md §6
- The "Used in" field of the GLOSSARY entry lists all documents that reference Schema Version

**Owner:** Technical lead
**Depends on:** Completion of data-format.md §6

---

### REF-TASK-0003: Decide V1 Scope for Distributed / HPC Execution

**Status: Decided** — Completed 2026-03-02

**Decision:** HPC/distributed execution is deferred to V2. V1 supports local execution only (sequential or Python multiprocessing). The `Runner` interface is designed as an abstraction so distributed backends can be plugged in for V2.

**Evidence:**
- ADR created: `docs/02_design/02_architecture/adr/ADR-001-library-with-server-ready-data-layer.md`
- C1 diagram updated: HPC marked "(V2)"; V2 Platform Server added as future external system
- SRS §4.3 will reflect V1 local-only scope when completed (REF-TASK-0008)
- V2 distributed execution deferred — no new task required; captured in ADR-001 Consequences

**Owner:** Technical lead

---

### REF-TASK-0004: Define Algorithm Author Onboarding Tutorial ("15-line wrapper")

**Description:** The system's core promise to Algorithm Authors is minimal boilerplate: wrap an existing optimizer (e.g., an Optuna sampler) in approximately 10–15 lines of code and submit it for evaluation. A tutorial must demonstrate this concretely.

**Acceptance criteria:**
- Tutorial exists in `docs/06_tutorials/` following the TEMPLATE.md format
- Tutorial shows wrapping an Optuna sampler as an Algorithm Instance in ≤ 15 lines
- Tutorial is self-contained (a reader can complete it without reading other docs first)
- The tutorial references the Algorithm Interface (`docs/03_technical_contracts/interface-contracts.md` §2)

**Owner:** Library design lead
**Depends on:** Completion of interface-contracts.md §2 (Algorithm Interface)

---

### REF-TASK-0005: Define COCO Format Mapping in Data-Format §3

**Description:** Document how this system's data entities (Run, PerformanceRecord, ResultAggregate) map to COCO's data formats. Identify what is preserved and what is lost in translation.

**Acceptance criteria:**
- `docs/03_technical_contracts/data-format.md` §3 contains a COCO mapping table
- A study result can be exported and loaded by COCO's analysis tools without errors
- Any data loss (fields not representable in COCO's format) is explicitly documented
- An interoperability test verifies the round-trip

**Owner:** Ecosystem integration lead
**Depends on:** Completion of data-format.md §2 (entity definitions)

---

### REF-TASK-0006: Define Nevergrad Adapter Pattern and Tutorial

**Description:** Many Algorithm Authors will want to wrap Nevergrad optimizers. Define the standard adapter pattern and document it in a tutorial.

**Acceptance criteria:**
- Adapter utility exists in library (wraps any Nevergrad optimizer as an Algorithm Instance)
- Tutorial in `docs/06_tutorials/` demonstrates wrapping a Nevergrad optimizer
- Nevergrad format mapping documented in `docs/03_technical_contracts/data-format.md` §3

**Owner:** Library design lead
**Depends on:** REF-TASK-0004 (Algorithm Interface tutorial), Nevergrad API investigation

---

### REF-TASK-0007: Define IOHprofiler Export Format Mapping

**Description:** Export Performance Records in IOHprofiler's `.dat` format so researchers can use IOHanalyzer for visualization.

**Acceptance criteria:**
- `docs/03_technical_contracts/data-format.md` §3 contains IOHprofiler mapping table
- Performance Records can be exported to `.dat` format and loaded in IOHanalyzer without errors
- An interoperability test verifies the export

**Owner:** Ecosystem integration lead
**Depends on:** Completion of data-format.md §2.6 (PerformanceRecord)

---

### REF-TASK-0008: Complete SRS After C2 Architecture Design

**Description:** Sections §4 (Functional Requirements), §5 NFR measurable criteria, §7 (Interface Requirements), and §8 (Acceptance Test Strategy) of the SRS require C2 containers to be designed first.

**Acceptance criteria:**
- §4 has formal FR-XX requirements for each C2 container, with MoSCoW priority and acceptance criteria
- §5 has measurable criteria for all 6 NFRs
- §7 lists all external interfaces with format, direction, and failure handling
- §8 maps each requirement to at least one test category
- §9 Traceability Matrix is complete (no "TBD" in Container or Test columns)

**Owner:** Technical lead
**Depends on:** C2 containers designed in `docs/02_design/02_architecture/c2-containers.md`

---

### REF-TASK-0009: Expand Use Cases UC-01 and UC-02

**Description:** UC-01 (Researcher runs a study) and UC-02 (Algorithm Author contributes) are the highest-priority use cases. Expand them into full use case descriptions with main flow, preconditions, postconditions, and failure scenarios.

**Acceptance criteria:**
- Each use case has a numbered main flow, preconditions, postconditions, and at least 2 failure scenarios
- Each use case has a corresponding tutorial in `docs/06_tutorials/`
- Each use case has at least one end-to-end test in the test suite

**Owner:** Technical lead
**Depends on:** REF-TASK-0008 (C2 needed to describe main flows)

---

### REF-TASK-0010: Add Measurable Criteria to All NFRs

**Description:** The 6 Non-Functional Requirements in SRS §5 currently state what quality attribute is required but not how it is measured. Each NFR needs at least one testable, measurable criterion.

**Acceptance criteria:**
- NFR-REPRO-01: criterion states what "identical results" means (bit-for-bit? numerical tolerance? platform constraints?)
- NFR-STAT-01: criterion states what automated checks are applied before generating a report
- NFR-INTEROP-01: criterion states round-trip test conditions for each platform
- NFR-OPEN-01: criterion states approved license types and format allowlist
- NFR-MODULAR-01: criterion states the plugin test procedure
- NFR-USABILITY-01: criterion states what "first study" scenario is used for timing

**Owner:** Technical lead

---

### REF-TASK-0011: Define Technical Constraints

**Description:** The SRS §6 technical constraints section is currently a placeholder. Once the first architectural decisions are made (Python version, OS support, key dependencies), record them here and in ADRs.

**Acceptance criteria:**
- Python minimum version stated and justified in an ADR
- Supported operating systems listed
- Core dependency restrictions defined (e.g., no GPL dependencies if library uses MIT license)
- All constraints recorded as ADRs in `docs/02_design/02_architecture/adr/`

**Owner:** Technical lead

---

### REF-TASK-0012: Fill SRS §7 Interface Requirements

**Description:** Once the external interface format mappings (REF-TASK-0005, 0006, 0007) are defined, fill SRS §7 with formal interface requirements for each external system.

**Acceptance criteria:**
- Each external system from C1 has an interface requirement entry in SRS §7
- Each entry states: direction, data format, protocol, and failure handling
- Requirements reference the detailed specifications in data-format.md §3

**Owner:** Ecosystem integration lead
**Depends on:** REF-TASK-0005, REF-TASK-0006, REF-TASK-0007

---

### REF-TASK-0013: Fill SRS §8 Acceptance Test Strategy

**Description:** Map each requirement to a specific test category and file once the system architecture is designed.

**Acceptance criteria:**
- Every FR-XX requirement maps to at least one test
- Every NFR maps to at least one automated test or benchmark procedure
- The reproducibility test procedure (run same study twice, compare results) is formally defined

**Owner:** QA / technical lead
**Depends on:** REF-TASK-0008 (FR-XX requirements), C3 components designed

---

### REF-TASK-0014: Review and Extend Metric Definitions After First Studies

**Description:** The five initial metrics derive from MANIFESTO Principle 12. After conducting the first real studies, new metrics may be needed (e.g., for categorical/mixed search spaces, for multi-objective HPO). Review and extend.

**Acceptance criteria:**
- Each new metric follows the definition template in metric-taxonomy.md §2
- New metrics are added to the Metric Selection Guide in §4
- Any new metrics that should be in the Standard Reporting Set are proposed and decided via ADR

**Owner:** Methodology lead
**Status:** Post-V1

---

### REF-TASK-0015: Add Implementation References to Metric Definitions

**Description:** Each metric definition in metric-taxonomy.md §2 has a placeholder "Implementation reference" field. Once the analysis module is built, fill these with module/function references.

**Acceptance criteria:**
- Every metric definition has an accurate implementation reference
- When code changes affect a metric computation, the reference is updated as part of the PR
- Stale references are flagged in CI

**Owner:** Analysis lead
**Depends on:** Analysis module implementation

---

### REF-TASK-0016: Formalize ANYTIME-ECDF_AREA Computation Procedure

**Description:** The ANYTIME-ECDF_AREA metric definition acknowledges that normalization bounds and aggregation across problems need formal specification. Two independent implementations must produce identical results on the same dataset.

**Acceptance criteria:**
- Exact computation procedure documented in metric-taxonomy.md §2 (ANYTIME-ECDF_AREA)
- Normalization bounds procedure specified (known optimum vs. empirical bounds, handling of censoring)
- Aggregation across problems defined
- Two reference implementations verified to produce identical results on a shared test dataset

**Owner:** Methodology lead

---

### REF-TASK-0017: Decide Whether TIME-EVALUATIONS_TO_TARGET Joins Standard Reporting Set

**Description:** TIME-EVALUATIONS_TO_TARGET requires a pre-specified target value, which adds planning burden. Weigh this against its scientific value as an efficiency metric. Document the decision in an ADR.

**Acceptance criteria:**
- ADR in `docs/02_design/02_architecture/adr/` recording the decision and MANIFESTO rationale
- Standard Reporting Set in metric-taxonomy.md §3 updated accordingly
- Benchmarking Protocol Step 5 updated if the metric is added to the mandatory set

**Owner:** Methodology lead

---

### REF-TASK-0018: Add Research Question Archetypes and Tutorial Links to Metric Selection Guide

**Description:** The Metric Selection Guide in metric-taxonomy.md §4 currently has 5 archetypes. This should grow as research patterns emerge from actual studies, with each archetype linked to a tutorial.

**Acceptance criteria:**
- Each archetype added to §4 has a corresponding tutorial in `docs/06_tutorials/`
- Tutorials demonstrate the full Protocol workflow for that archetype end-to-end

**Owner:** Methodology lead
**Status:** Ongoing

---

### REF-TASK-0019: Specify Required Level 1 Visualizations

**Description:** Fill `docs/04_scientific_practice/methodology/statistical-methodology.md` §2 with the specific required visualizations for Exploratory Data Analysis, once the reporting module is designed.

**Acceptance criteria:**
- List of required visualization types for Level 1 analysis is documented in §2
- Each visualization: name, what it shows, when it is most useful, how to interpret it
- System generates all required visualizations automatically from Run data without extra configuration

**Owner:** Analysis lead
**Depends on:** Reporting module design (C3)

---

### REF-TASK-0020: Specify Statistical Test Selection Procedure

**Description:** Fill `docs/04_scientific_practice/methodology/statistical-methodology.md` §3 with a decision tree for test selection (parametric vs. non-parametric, paired vs. unpaired, multiple comparison correction methods).

**Acceptance criteria:**
- Decision tree documented for at least: two-algorithm comparison, multi-algorithm comparison, paired vs. unpaired cases
- Recommended correction methods listed with when to prefer each
- References Bartz-Beielstein et al. (2020) for methodology justification
- `docs/03_technical_contracts/metric-taxonomy.md` statistical treatment notes for each metric reference this section

**Owner:** Methodology lead

---

### REF-TASK-0021: Define Minimum Diversity Requirements for Problem Instance Selection

**Description:** The Benchmarking Protocol Step 3 defers defining minimum diversity requirements. These need to be formally specified and enforced by the system when validating a Study record.

**Acceptance criteria:**
- Minimum number of Problem Instances per study defined and justified
- Required spread across diversity characteristics (dimension ranges, noise levels, etc.) specified
- SRS §4.1 (Problem Repository FR) updated with these requirements
- System validates Study record against these criteria before allowing Experiment to begin

**Owner:** Methodology lead

---

### REF-TASK-0022: Define Sensitivity Documentation Format

**Description:** MANIFESTO Principle 11 requires sensitivity documentation alongside Algorithm Instance contributions. The format for this documentation needs to be defined in the Algorithm Instance schema.

**Acceptance criteria:**
- `docs/03_technical_contracts/data-format.md` §2.2 (Algorithm Instance) includes a `sensitivity_report` field or linked document specification
- Benchmarking Protocol Step 4 references the format
- `docs/05_community/contribution-guide.md` §2 requires sensitivity documentation as part of algorithm contribution review

**Owner:** Methodology lead
**Depends on:** Completion of data-format.md §2.2

---

### REF-TASK-0023: Design the Repository Storage Abstraction Interface

**Description:** The `Repository` interface is the storage abstraction that allows switching between `LocalFileRepository` (V1) and `ServerRepository` (V2) without modifying any library code. This interface is the key architectural boundary established by ADR-001. It must be designed before any storage code is written, to prevent leaky abstractions.

**Acceptance criteria:**
- `docs/03_technical_contracts/interface-contracts.md` contains a `Repository` interface specification with methods for all entity types (ProblemInstance, AlgorithmInstance, Study, Experiment, Run, PerformanceRecord, ResultAggregate)
- Interface methods accept and return entity IDs (UUIDs), not file paths
- A `LocalFileRepository` implementation is provided in the library and passes all interface contract tests
- No code outside of `Repository` implementations calls file I/O functions directly (enforced by code review policy documented in contribution-guide.md)
- An integration test demonstrates that swapping `LocalFileRepository` for a mock `ServerRepository` requires zero changes to calling code

**Owner:** Library design lead
**Depends on:** Completion of data-format.md §2 (entity definitions); ADR-001

---

### REF-TASK-0024: Decide Bulk PerformanceRecord Storage Format

**Description:** The primary entity schema for all entities (including PerformanceRecord) is JSON (required by ADR-001 server-compatibility constraint). However, a single large Study may produce millions of PerformanceRecord entries — JSON at that scale has significant storage and read-performance costs. This task decides whether a secondary binary format (Parquet, HDF5, or other) is used for bulk PerformanceRecord storage, and documents the decision in an ADR.

**Acceptance criteria:**
- ADR created in `docs/02_design/02_architecture/adr/` recording the format decision and benchmark evidence
- data-format.md §3 updated to specify: primary schema (JSON), secondary bulk format (if decided), conversion procedure
- The choice does not violate the ADR-001 server-compatibility constraint: the primary schema remains JSON; binary storage is an optimization, not a replacement
- An interoperability test confirms that bulk-stored records produce identical analysis results to JSON-stored records

**Owner:** Technical lead
**Depends on:** data-format.md §2.6 (PerformanceRecord definition); REF-TASK-0023 (Repository interface, which determines how bulk records are accessed)

---

## Adding New Tasks

When adding a new `TODO: REF-TASK-dddd` to any document:

1. Choose the next available 4-digit number from this registry
2. Add the inline reference in the source document: `> **\`TODO: REF-TASK-NNNN\`** — [description]`
3. Add a row to the Task Registry table above
4. Add a full Task Details entry below with: Description, Acceptance Criteria, Owner, Dependencies
5. Create a corresponding issue in the project issue tracker and link it here

**Current highest task ID assigned:** REF-TASK-0024
