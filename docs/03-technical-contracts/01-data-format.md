# Data Format Specification

<!--
STORY ROLE: The "common language" of the system.
Every component, every external integration, every stored artifact speaks this language.
This document defines the vocabulary that makes interoperability and reproducibility possible.
Without agreed-upon schemas, MANIFESTO Principles 19–22 (Reproducibility) are aspirational.

NARRATIVE POSITION:
  SRS §7 (interface requirements) → Data Format Spec → (concrete schemas and formats)
  → specs/interface-contracts.md : interfaces operate on the entities defined here
  → specs/metric-taxonomy.md     : metric values are stored in Result Aggregate entities here

CONNECTS TO:
  ← SRS §4, §7             : requirements that drove these format decisions
  ← MANIFESTO Principles 7, 8, 19–22 : directly operationalized by this document
  → specs/interface-contracts.md : method signatures use entity types from here
  → specs/metric-taxonomy.md     : metric definitions must match Result Aggregate fields here
  → community/versioning-governance.md : how schema versions are managed and deprecated
  → architecture/adr/            : format choices (e.g., JSON vs HDF5) should have ADRs

GLOSSARY: All entity names used here are defined in docs/GLOSSARY.md.
Use exact glossary terms — do not introduce synonyms.
-->

---

## 1. Entity Overview

### Server-Compatibility Design Constraint

> **Architectural decision (ADR-001):** All entity schemas in this document are designed to be server-compatible from V1. This is a hard constraint, not a preference.

This means every entity definition in §2 MUST satisfy all of the following:

| Requirement | Rationale |
|---|---|
| **Globally unique ID (UUID format)** | Entity references use IDs, not local file paths. The same ID is valid in local file storage (V1) and in a server database (V2) without migration. |
| **JSON-serializable primary schema** | No binary-only fields in the canonical entity representation. JSON is required for REST API compatibility (V2) and for COCO/IOHprofiler/Nevergrad interoperability (NFR-INTEROP-01). |
| **Cross-entity references by ID only** | No field may reference another entity by file path or local directory structure. All foreign keys are entity IDs. |
| **No file system assumptions** | Entity schemas do not encode directory layout, file naming, or path separators. Storage layout is an implementation detail of the `Repository` (see `interface-contracts.md`). |

Bulk data storage (e.g., high-volume Performance Records) may use efficient binary formats (Parquet, HDF5) as a secondary representation, but the primary schema remains JSON. This is a separate ADR decision (`TODO: REF-TASK-0024`).

<!--
  Provide a diagram (Mermaid entity-relationship or similar) showing all core entities
  and their relationships before defining them individually.

  Entities to include (adjust based on design decisions):
    ProblemInstance → has → SearchSpace
    AlgorithmInstance → has → Configuration
    Study → contains → ProblemInstance (many)
    Study → contains → AlgorithmInstance (many)
    Experiment → realizes → Study
    Experiment → produces → Run (many)
    Run → produces → PerformanceRecord (many)
    Run → produces → ResultAggregate (one, at end of run)

  Each relationship should show cardinality and which entity "owns" which.
  → Ownership determines where data is stored and who controls its lifecycle.
-->

---

## 2. Entity Definitions

### 2.1 Problem Instance

<!--
  What this represents: → see GLOSSARY: Problem Instance

  Fields to define (for each field: name, type, required/optional, semantics, validation rule):

  Identity:
    - id          : globally unique identifier, format to be decided (UUID? namespaced string?)
    - name        : human-readable name
    - version     : schema version + content version → community/versioning-governance.md §1
    - provenance  : source of this problem (real ML task, synthetic, adapted from X)

  Search space:
    - dimensions  : number of hyperparameters
    - variables   : list of variable descriptors (name, type: continuous/integer/categorical, bounds/choices)
    - dependencies: known interactions between variables (if any)

  Objective:
    - type        : minimize / maximize
    - noise_level : deterministic / stochastic (with characterization)
    - known_optimum: value if known, null otherwise

  Evaluation:
    - budget_type : evaluation_count / wall_time / combined
    - default_budget: recommended budget for this problem

  Metadata for analysis:
    - landscape_characteristics: modality, separability, etc. (if known)
    - real_or_synthetic: enum
    - domain: what ML/optimization domain does this represent?

  Provenance:
    - created_by, created_at, last_updated
    - source_reference: paper or system this problem comes from

  Validation rules:
    - dimensions must equal len(variables)
    - variable bounds must be valid (lower < upper for continuous)
    - Hint: what makes a Problem Instance record "complete enough to reproduce"?
-->

### 2.2 Algorithm Instance

<!--
  What this represents: → see GLOSSARY: Algorithm Instance

  Fields:
  Identity:
    - id, name, version
    - algorithm_family: the abstract Algorithm concept (e.g., "Random Search", "TPE", "CMA-ES")

  Configuration:
    - hyperparameters: key-value map of configuration parameter name → value
    - configuration_justification: why this configuration? (for fairness, Principle 10)

  Implementation:
    - code_reference: pointer to the Implementation artifact (git commit, package version)
    - language, framework, framework_version
    - known_assumptions: what problem properties does this algorithm assume?
      (e.g., "assumes continuous search space", "assumes noise-free evaluations")

  Provenance:
    - contributed_by, created_at

  Validation rules:
    - all hyperparameter names must match the algorithm's declared parameter schema
    - code_reference must be resolvable and version-pinned
-->

### 2.3 Study

<!--
  What this represents: → see GLOSSARY: Study / Benchmarking Study

  Fields:
    - id, name, version
    - research_question: the motivating research question (free text + structured tags)
    - problem_instances: list of Problem Instance IDs (with versions)
    - algorithm_instances: list of Algorithm Instance IDs (with versions)
    - experimental_design:
        repetitions: number of independent runs per (problem, algorithm) pair
        seed_strategy: how seeds are generated and assigned
        budget_allocation: how budget is distributed across runs
        stopping_criteria: what terminates a run
    - pre_registered_hypotheses: list of hypotheses to be tested (Principle 16 pre-specification)
    - created_by, created_at

  Validation rules:
    - at least 2 algorithm instances (single-algorithm studies are analysis, not comparison)
    - repetitions must be stated before data collection begins (not adjusted post-hoc)
-->

### 2.4 Experiment

<!--
  What this represents: an executed Study — → see GLOSSARY: Experiment

  Fields:
    - id, study_id (reference to Study)
    - status: planned / running / completed / failed
    - execution_environment: platform, OS, hardware specs (for reproducibility)
    - started_at, completed_at
    - run_ids: list of Run IDs produced

  Note: Experiment is separate from Study because the same Study may be re-executed
  (e.g., for verification), producing a new Experiment from the same Study plan.
-->

### 2.5 Run

<!--
  What this represents: → see GLOSSARY: Run
  The atomic unit of the system. One algorithm, one problem, one seed.

  Fields:
    - id
    - experiment_id, study_id
    - problem_instance_id (with version)
    - algorithm_instance_id (with version)
    - seed: exact integer seed used
    - budget_used: actual evaluations / time consumed
    - status: completed / failed / budget_exhausted
    - started_at, completed_at

  Validation rules:
    - seed must be unique within an Experiment for a given (problem, algorithm) pair
    - a failed Run must record the failure reason
-->

### 2.6 Performance Record

<!--
  What this represents: a single performance snapshot during a Run (enables anytime curves)
  → MANIFESTO Principle 14: full performance curves, not just endpoints

  Fields:
    - id, run_id
    - evaluation_number: how many evaluations have been performed so far
    - elapsed_time: wall-clock time since run start
    - objective_value: current best objective value
    - current_solution: the solution achieving this value (optional, may be large)
    - is_improvement: boolean — is this better than the previous record?

  Hint: not every evaluation needs a record — define a sampling/logging strategy.
  Trade-off: granularity vs. storage cost. → Consider an ADR for this decision.
-->

### 2.7 Result Aggregate

<!--
  What this represents: aggregated statistics across multiple Runs of the same
  (algorithm, problem) combination within an Experiment.

  Fields:
    - id, experiment_id, problem_instance_id, algorithm_instance_id
    - n_runs: how many runs were aggregated
    - metrics: map of metric_name → AggregateValue
      AggregateValue: { mean, std, median, q25, q75, min, max, n_successful }
    - anytime_curves: summarized performance curves (mean ± spread at each evaluation)

  Metric names used here must exactly match names in specs/metric-taxonomy.md.
  → This is a hard contract between this document and metric-taxonomy.md.
-->

---

## 3. File Formats and Storage

<!--
  For each entity type, specify:
    - Primary storage format (JSON / JSONL / Parquet / HDF5 / CSV / other)
    - Why this format? → create an ADR if the choice is non-obvious
    - Schema file location (JSON Schema, Avro schema, Pydantic model, etc.)
    - Compression / encoding for large data (PerformanceRecord can be voluminous)
    - File naming conventions and directory structure

  Hint — considerations:
    - Human readability vs. performance (JSON vs. Parquet)
    - Tool ecosystem: what can COCO/IOHprofiler/Nevergrad already read?
    - Long-term archival: open formats preferred (Principle 22)
-->

---

## 4. Interoperability Mappings

<!--
  For each external platform the system integrates with (from C1):

  ### [Platform Name] (e.g., IOHprofiler, COCO, Nevergrad)

  Direction: export / import / both

  Mapping table:
    | Our Entity / Field          | Their Entity / Field        | Notes / Losses            |
    |-----------------------------|-----------------------------|---------------------------|
    | Run.seed                    | [their equivalent]          | exact match / approximate |
    | PerformanceRecord.eval_num  | [their equivalent]          | ...                       |

  Data loss / gain:
    What information is lost when converting to their format?
    What information do we gain when importing from their format?
    → Reference SRS NFR-INTEROP for acceptance criteria

  Version compatibility:
    Which versions of their format do we support?
    → Link to ADR if a compatibility decision was made
-->

---

## 5. Validation Rules (Cross-Entity)

<!--
  Invariants that span multiple entities — cannot be expressed as per-field rules.

  Examples of invariants to consider:
    - Every Run.problem_instance_id must reference a Problem Instance with the same version
      as declared in the parent Study
    - Seeds within an Experiment must be unique per (problem, algorithm) pair
    - A Result Aggregate's n_runs must equal the count of completed Runs for that combination
    - Every Performance Record's evaluation_number must be monotonically increasing within a Run

  For each invariant:
    - State it precisely
    - When is it checked? (at write time, at read time, in analysis)
    - What is the consequence of violation? (reject, warn, flag)
-->

---

## 6. Schema Versioning

<!--
  How are schema versions managed?
    → policy: community/versioning-governance.md §1

  What constitutes a breaking schema change?
    (adding a required field, renaming a field, changing a type)

  How are old-format files handled?
    (migration scripts, compatibility shims, rejection with clear error)

  Where are schema files stored and how are they versioned?
    (alongside code, in a separate schema registry, etc.)
-->
