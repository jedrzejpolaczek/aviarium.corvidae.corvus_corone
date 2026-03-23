# Glossary — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: The "shared vocabulary" of the entire system.
Every other document and every docstring MUST use the terms defined here.
When a term is used for the first time in any document, it should link here.

NARRATIVE POSITION:
  This document is a reference, not a chapter. It has no position in the narrative flow
  but underpins the precision of every other document.

CONNECTS TO:
  → All documents : terms used anywhere in the documentation must be defined here
  → Docstrings    : implementation code uses these exact terms in parameter names and descriptions
  → Tasks/issues  : task titles and descriptions use these terms to prevent ambiguity

MAINTENANCE RULE:
  When an ADR changes the meaning or scope of a term, update this glossary first.
  When a new interface is defined in docs/03-technical-contracts/interface-contracts.md, add any new terms here first.
  If a term appears in more than one document with slightly different meanings, that is a bug —
  resolve it here, then update all documents.
-->

---

## How to Use This Glossary

When to add a term:
- It is used in more than one document, or
- It has a precise meaning here that differs from common usage in ML / optimization literature, or
- It is one of a family of related terms requiring careful distinction (e.g., Algorithm / Instance / Implementation).

Format for each entry:

> **Definition:** one precise sentence.
> **Distinguished from:** related terms that could be confused with this one.
> **Used in:** documents where this term is load-bearing.
> **Example:** *(optional)* a concrete case that makes the definition tangible.

Terms are listed alphabetically within sections.

> **`TODO: REF-TASK-0001`** — Extend this glossary with terms introduced by
> `docs/03-technical_contracts/interface-contracts.md` and
> `docs/03-technical_contracts/data-format.md` once those documents are filled.
> Owner: technical lead. Acceptance: all public method parameter names and entity field names
> used in those documents appear here with definitions that match their docstrings.

---

## Core Concepts

### Algorithm

**Definition:** An abstract computational strategy for hyperparameter optimization — the concept or method family, independent of any specific configuration or code.

**Distinguished from:** *Algorithm Instance* (the same strategy with all hyperparameters fixed), *Implementation* (the executable code artifact).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 8, `docs/02-design/01-software-requirement-specification/srs.md`, `docs/03-technical-contracts/interface-contracts.md`.

**Example:** "Tree-structured Parzen Estimator (TPE)" is an Algorithm. A specific instantiation of TPE with `n_startup_trials=10` and `gamma=0.25` is an Algorithm Instance.

---

### Algorithm Instance

**Definition:** An Algorithm with a fully specified configuration — all hyperparameters fixed to concrete values — such that two Runs of the same Algorithm Instance must produce identical results given the same seed.

**Distinguished from:** *Algorithm* (the abstract method concept), *Implementation* (the concrete code that executes it).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 8, `docs/03-technical-contracts/data-format.md` §2.2, `docs/03-technical_contracts/interface-contracts.md` §2.

**Example:** TPE with `n_startup_trials=10, gamma=0.25, seed=42` is an Algorithm Instance. The same TPE strategy with `gamma=0.5` is a different Algorithm Instance.

---

### Implementation

**Definition:** The concrete, versioned code artifact that executes a specific Algorithm Instance on a computing platform, including library dependencies, platform requirements, and code revision.

**Distinguished from:** *Algorithm* (the concept), *Algorithm Instance* (the configured concept). Two Implementations of the same Algorithm Instance may produce different numerical results due to floating-point differences or library version changes — this is why Implementation must be reported separately (Principle 8).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 8, `docs/03-technical_contracts/data-format.md` §2.2, `docs/05-community/contribution-guide.md`.

---

### Benchmark Problem

**Definition:** A class of hyperparameter optimization challenge — defined by a problem type and variable structure — used to evaluate and compare algorithm behavior. May be synthetic (designed to isolate specific landscape properties) or real (derived from actual ML model training tasks).

**Distinguished from:** *Problem Instance* (a fully specified, concrete parameterization of a Benchmark Problem with all characteristics fixed).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principles 4–7, `docs/02-design/02-architecture/c1-context.md`, `docs/03-technical-contracts/data-format.md` §2.1.

**Example:** "SVM hyperparameter tuning on a classification task" is a Benchmark Problem. That same problem with a fixed dataset, 5-dimensional search space, evaluation budget of 100, and Gaussian noise σ=0.01 is a Problem Instance.

---

### Problem Instance

**Definition:** A fully specified, concrete optimization task: a Benchmark Problem with all characteristics fixed — search space dimension, variable types and bounds, computational Budget, noise level, and known optimum or best known solution if available.

**Distinguished from:** *Benchmark Problem* (the problem class from which instances are drawn). A Problem Instance is the specific object that an Algorithm Instance evaluates during a Run.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 7, `docs/03-technical_contracts/data-format.md` §2.1, `docs/03-technical_contracts/interface-contracts.md` §1, `docs/04-scientific_practice/methodology/benchmarking-protocol.md` Step 3.

---

### Study / Benchmarking Study

**Definition:** A pre-planned scientific investigation that compares the behavior of one or more Algorithm Instances on a defined set of Problem Instances, motivated by a specific Research Question, with experimental design fully specified before data collection begins.

**Distinguished from:** *Experiment* (the execution of a Study — the actual Runs performed). A Study is the plan; an Experiment is the realized plan.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 16, `docs/03-technical_contracts/data-format.md` §2.3, `docs/04_scientific-practice/methodology/benchmarking-protocol.md`.

---

### Experiment

**Definition:** The executed instance of a Study — the complete set of Runs performed according to the Study plan, with all outcomes recorded and traceable to the originating Study.

**Distinguished from:** *Study* (the plan), *Run* (a single execution unit within the Experiment). The same Study may produce multiple Experiments if re-executed for verification purposes.

**Used in:** `docs/03-technical-contracts/data-format.md` §2.4, `docs/03-technical-contracts/interface-contracts.md` §3.

---

### Run

**Definition:** A single, independent execution of one Algorithm Instance on one Problem Instance using one specific seed, consuming a defined Budget and producing a sequence of Performance Records.

**Distinguished from:** *Experiment* (the full set of Runs). The Run is the atomic unit of reproducibility — given the same seed, the same Algorithm Instance, and the same Problem Instance, a Run must produce identical results.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 18, `docs/03-technical-contracts/data-format.md` §2.5, `docs/03-technical-contracts/interface-contracts.md` §3.

---

### Performance Record

**Definition:** A single timestamped snapshot of a Run's progress, capturing the evaluation count, elapsed wall-clock time, current best objective value, and whether that value is an improvement over all prior snapshots. A sequence of Performance Records for one Run forms its anytime performance curve.

**Distinguished from:** *Run* (the full execution that produces Performance Records), *Result Aggregate* (statistics computed across multiple Runs). A Performance Record is raw per-evaluation data; a Result Aggregate is a derived summary.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 14, `docs/03-technical-contracts/01-data-format.md` §2.6.

---

### Result Aggregate

**Definition:** A derived record of aggregated statistics computed across all Runs of the same (Algorithm Instance, Problem Instance) combination within an Experiment. Captures central tendency, spread, and summarized anytime curves so that comparisons can be made without re-processing raw Performance Records.

**Distinguished from:** *Performance Record* (raw per-evaluation snapshot within a single Run), *Run* (a single execution). A Result Aggregate is always computed — never directly recorded during execution.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principles 12–14, `docs/03-technical-contracts/01-data-format.md` §2.7, `docs/03-technical-contracts/03-metric-taxonomy.md`.

---

### Report

**Definition:** A system-generated document produced for every completed Experiment, presenting findings in one of two forms: a *Researcher Report* (full statistical analysis, effect sizes, confirmatory test results, methodology details) or a *Practitioner Report* (practical guidance scoped to the tested Problem Instances and Algorithm Instances, without global rankings). Every Report must include a mandatory limitations section.

**Distinguished from:** *Result Aggregate* (the underlying computed statistics from which Reports are derived). A Result Aggregate is a data record; a Report is a human-readable artifact generated from one or more Result Aggregates.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principles 24–25, `docs/02-design/01-software-requirement-specification/03-functional-requirements/07-fr-4.6-reporting-and-visualization.md` FR-20–FR-22, `docs/03-technical-contracts/01-data-format.md` §2.8.

---

## Performance & Measurement

### Anytime Performance

**Definition:** The measurable quality of an algorithm's best-found solution at any evaluation count during a Run — captured as a continuous curve over the full Budget rather than reported only at termination.

**Distinguished from:** final-budget performance (a single endpoint value). Anytime Performance reveals optimization dynamics, early convergence, and performance at any intermediate budget level.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 14, `docs/03-technical-contracts/metric-taxonomy.md` §2 (ANYTIME category), `docs/04_scientific_practice/methodology/statistical-methodology.md` §5.

---

### Budget

**Definition:** The resource limit allocated to a single Run, expressed as a maximum number of objective function evaluations, a wall-clock time limit, or both — agreed upon before the Run begins and held constant across all Algorithm Instances in a fair comparison.

**Distinguished from:** wall-clock time alone. Evaluation budget and time budget are different constraints; a fair study uses the same budget type for all algorithms.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 12, `docs/03-technical-contracts/data-format.md` §2.1, `docs/03-technical-contracts/interface-contracts.md` §1.

---

### Performance Metric

**Definition:** A scalar quantity derived from one or more Runs that quantifies a specific aspect of algorithm behavior. All Performance Metrics used in this system are formally defined in `docs/03-technical-contracts/metric-taxonomy.md`.

**Distinguished from:** raw objective function values (which are unaggregated outputs of individual evaluations). A Performance Metric is always computed from the results of one or more complete Runs.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 12, `docs/03-technical-contracts/metric-taxonomy.md`, `docs/04_scientific_practice/methodology/statistical-methodology.md`.

---

### Effect Size

**Definition:** A quantitative measure of the practical magnitude of a performance difference between Algorithm Instances, computed independently of statistical significance, used to determine whether a statistically detected difference is large enough to matter in practice.

**Distinguished from:** p-value (which measures statistical evidence for a difference, not its magnitude). A difference can be highly statistically significant yet have a negligible Effect Size.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 13, `docs/04_scientific_practice/methodology/statistical-methodology.md` §4.

---

## Scientific Concepts

### No Free Lunch (NFL)

**Definition:** The theoretical result stating that no optimization algorithm outperforms all others across all possible problem distributions when performance is averaged uniformly — implying that algorithm superiority is always conditional on the problem class.

**Implication for this system:** Global algorithm rankings are scientifically invalid. Every conclusion about algorithm performance must be scoped to the specific Problem Instances tested. The goal of this system is to map which algorithms work well for which problem characteristics, not to crown a winner.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 30, `docs/02-design/01-software-requirement-specification/SRS.md` §6 (Constraints).

---

### Research Question

**Definition:** A precisely scoped scientific question that motivates a Study by naming: the Algorithm Instances or families to compare, the Problem Instance characteristics of interest, and the specific performance aspects to measure — stated before any data is collected.

**Distinguished from:** an informal motivation ("let's see how algorithm X does"). A valid Research Question is falsifiable, scoped, and drives the entire experimental design.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 1, `docs/03-technical-contracts/data-format.md` §2.3, `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Step 1.

---

### Reproducibility

**Definition:** The property that a Study can be independently re-executed by a different team, using the archived Artifacts — complete code, exact library versions, input data, seeds, and result processing procedures — and produce the same Experiment results.

**Distinguished from:** *Replicability* (same team, different data), *Generalizability* (same method applied to new problems). This system targets Reproducibility as a hard requirement, not an aspiration.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principles 19–22, `docs/02-design/01-software-requirement-specification/SRS.md` §5 NFR-REPRO, `docs/05_community/versioning-governance.md`.

---

## Ecosystem Terms

### Artifact

**Definition:** Any versioned, stored product of the system — a Problem Instance specification, Algorithm Implementation, Experiment record, Results dataset, or Analysis output — subject to the versioning and governance policy in `docs/05_community/versioning-governance.md`.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 21, `docs/05_community/versioning-governance.md`, `docs/03-technical-contracts/data-format.md`.

---

### Schema Version

**Definition:** The version identifier of the data format specification (`docs/03-technical-contracts/data-format.md`) under which a stored Artifact was created, enabling the system to validate, migrate, or reject Artifacts as the format evolves.

**Used in:** `docs/03-technical-contracts/data-format.md` §6, `docs/05_community/versioning-governance.md` §1.

> **`TODO: REF-TASK-0002`** — Once `docs/03-technical-contracts/data-format.md` §6 (Schema Versioning)
> is filled, verify that the Schema Version definition above matches the versioning scheme adopted there.
> Owner: technical lead. Acceptance: definition and data-format.md §6 use identical terminology.
