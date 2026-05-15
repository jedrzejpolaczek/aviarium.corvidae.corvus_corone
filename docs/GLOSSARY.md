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

---

## Core Concepts

### Algorithm

**Definition:** An abstract computational strategy for hyperparameter optimization — the concept or method family, independent of any specific configuration or code.

**Distinguished from:** *Algorithm Instance* (the same strategy with all hyperparameters fixed), *Implementation* (the executable code artifact).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 8, `docs/02-design/01-software-requirement-specification/srs.md`, `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`.

**Example:** "Tree-structured Parzen Estimator (TPE)" is an Algorithm. A specific instantiation of TPE with `n_startup_trials=10` and `gamma=0.25` is an Algorithm Instance.

---

### Algorithm Family

**Definition:** The abstract class or method type to which an Algorithm Instance belongs, describing its general approach to optimization independent of specific hyperparameter values. Stored in the `algorithm_family` field of the Algorithm Instance record and used to categorize and filter entries in the Algorithm Registry.

**Distinguished from:** *Algorithm* (the fully abstract concept), *Algorithm Instance* (a fully configured member of the family). Two Algorithm Instances can share the same Algorithm Family while differing in hyperparameters.

**Used in:** `docs/03-technical-contracts/01-data-format/03-algorithm-instance.md`, `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md`.

**Example:** `"TPE"`, `"CMA-ES"`, `"Random Search"`, `"Bayesian Optimization"` are Algorithm Families. A specific TPE with `n_startup_trials=10` is an Algorithm Instance of the `"TPE"` family.

---

### Algorithm Instance

**Definition:** An Algorithm with a fully specified configuration — all hyperparameters fixed to concrete values — such that two Runs of the same Algorithm Instance must produce identical results given the same seed.

**Distinguished from:** *Algorithm* (the abstract method concept), *Implementation* (the concrete code that executes it).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 8, `docs/03-technical-contracts/01-data-format/03-algorithm-instance.md`, `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`.

**Example:** TPE with `n_startup_trials=10, gamma=0.25` is an Algorithm Instance. The same TPE strategy with `gamma=0.5` is a different Algorithm Instance.

---

### Ask-Tell Pattern

**Definition:** The interaction protocol between the Runner and an Algorithm Instance in which the Runner "asks" for candidate solutions by calling `suggest()`, evaluates them via the Problem Interface, and "tells" the Algorithm the outcome by calling `observe()`. All Algorithm implementations must follow this pattern regardless of whether they are adaptive.

**Distinguished from:** direct optimization APIs (such as `scipy.optimize.minimize`) that receive the objective function directly and manage their own evaluation loop. In the Ask-Tell pattern the Runner owns the evaluation loop; the Algorithm only proposes candidates and receives feedback.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`, `docs/06-tutorials/uc-02-contribute-algorithm.md`.

---

### Benchmark Problem

**Definition:** A class of hyperparameter optimization challenge — defined by a problem type and variable structure — used to evaluate and compare algorithm behavior. May be synthetic (designed to isolate specific landscape properties) or real (derived from actual ML model training tasks).

**Distinguished from:** *Problem Instance* (a fully specified, concrete parameterization of a Benchmark Problem with all characteristics fixed).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principles 4–7, `docs/02-design/02-architecture/02-c1-context.md`, `docs/03-technical-contracts/01-data-format/02-problem-instance.md`.

**Example:** "SVM hyperparameter tuning on a classification task" is a Benchmark Problem. That same problem with a fixed dataset, 5-dimensional search space, evaluation budget of 100, and Gaussian noise σ=0.01 is a Problem Instance.

---

### EvaluationResult

**Definition:** The structured outcome of a single call to `Problem.evaluate(solution)`, containing the raw `objective_value`, the 1-indexed `evaluation_number`, and optional metadata. The Runner passes the EvaluationResult to `Algorithm.observe()` after each evaluation.

**Distinguished from:** a raw objective value (only the scalar float component). An EvaluationResult also carries the evaluation count and metadata that the Algorithm may use for model updates.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/02-problem-interface.md`, `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`.

---

### Execution Environment

**Definition:** The complete hardware and software context in which an Experiment ran: operating system version, hardware specification (CPU, RAM, GPU), and programming language version. Recorded in the Experiment entity to enable exact reproduction and to explain performance differences attributable to infrastructure variation.

**Distinguished from:** the Algorithm Implementation (the code and library versions). The Execution Environment is the infrastructure on which the Implementation runs, not the Implementation itself.

**Used in:** `docs/03-technical-contracts/01-data-format/05-experiment.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`.

---

### Experiment

**Definition:** The executed instance of a Study — the complete set of Runs performed according to the Study plan, with all outcomes recorded and traceable to the originating Study.

**Distinguished from:** *Study* (the plan), *Run* (a single execution unit within the Experiment). The same Study may produce multiple Experiments if re-executed for verification purposes.

**Used in:** `docs/03-technical-contracts/01-data-format/05-experiment.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`.

---

### Implementation

**Definition:** The concrete, versioned code artifact that executes a specific Algorithm Instance on a computing platform, including library dependencies, platform requirements, and code revision.

**Distinguished from:** *Algorithm* (the concept), *Algorithm Instance* (the configured concept). Two Implementations of the same Algorithm Instance may produce different numerical results due to floating-point differences or library version changes — this is why Implementation must be reported separately (Principle 8).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 8, `docs/03-technical-contracts/01-data-format/03-algorithm-instance.md`, `docs/05-community/01-contribution-guide.md`.

---

### Performance Record

**Definition:** A single timestamped snapshot of a Run's progress, capturing the evaluation count, elapsed wall-clock time, current best objective value, and whether that value is an improvement over all prior snapshots. A sequence of Performance Records for one Run forms its anytime performance curve.

**Distinguished from:** *Run* (the full execution that produces Performance Records), *Result Aggregate* (statistics computed across multiple Runs). A Performance Record is raw per-evaluation data; a Result Aggregate is a derived summary.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 14, `docs/03-technical-contracts/01-data-format/07-performance-record.md`.

---

### Problem Instance

**Definition:** A fully specified, concrete optimization task: a Benchmark Problem with all characteristics fixed — search space dimension, variable types and bounds, computational Budget, noise level, and known optimum or best known solution if available.

**Distinguished from:** *Benchmark Problem* (the problem class from which instances are drawn). A Problem Instance is the specific object that an Algorithm Instance evaluates during a Run.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 7, `docs/03-technical-contracts/01-data-format/02-problem-instance.md`, `docs/03-technical-contracts/02-interface-contracts/02-problem-interface.md`, `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md` Step 3.

---

### Report

**Definition:** A system-generated document produced for every completed Experiment, presenting findings in one of two forms: a *Researcher Report* (full statistical analysis, effect sizes, confirmatory test results, methodology details) or a *Practitioner Report* (practical guidance scoped to the tested Problem Instances and Algorithm Instances, without global rankings). Every Report must include a mandatory limitations section.

**Distinguished from:** *Result Aggregate* (the underlying computed statistics from which Reports are derived). A Result Aggregate is a data record; a Report is a human-readable artifact generated from one or more Result Aggregates.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principles 24–25, `docs/02-design/01-software-requirement-specification/03-functional-requirements/07-fr-4.6-reporting-and-visualization.md` FR-20–FR-22, `docs/03-technical-contracts/01-data-format/09-report.md`.

---

### Result Aggregate

**Definition:** A derived record of aggregated statistics computed across all Runs of the same (Algorithm Instance, Problem Instance) combination within an Experiment. Captures central tendency, spread, and summarized anytime curves so that comparisons can be made without re-processing raw Performance Records.

**Distinguished from:** *Performance Record* (raw per-evaluation snapshot within a single Run), *Run* (a single execution). A Result Aggregate is always computed — never directly recorded during execution.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principles 12–14, `docs/03-technical-contracts/01-data-format/08-result-aggregate.md`, `docs/03-technical-contracts/03-metric-taxonomy/01-metric-taxonomy.md`.

---

### Run

**Definition:** A single, independent execution of one Algorithm Instance on one Problem Instance using one specific seed, consuming a defined Budget and producing a sequence of Performance Records.

**Distinguished from:** *Experiment* (the full set of Runs). The Run is the atomic unit of reproducibility — given the same seed, the same Algorithm Instance, and the same Problem Instance, a Run must produce identical results.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 18, `docs/03-technical-contracts/01-data-format/06-run.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`.

---

### RunContext

**Definition:** The dynamic contextual information passed to `Algorithm.suggest()` on each call, representing the Run's current state. Contains `remaining_budget` (evaluations still available) and `elapsed_evaluations` (evaluations completed so far). Updated by the Runner before every `suggest()` call.

**Distinguished from:** the Search Space (the static structural description of valid inputs, fixed for the duration of the Run) and the Seed (the randomness initialization value, fixed at Run start). RunContext is the only input to `suggest()` that changes during a Run.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`.

---

### Search Space

**Definition:** The domain in which candidate solutions are proposed and evaluated, defined by a list of variables each with a type (`continuous`, `integer`, or `categorical`) and associated bounds or choices. The Search Space is declared in the Problem Instance and passed to the Algorithm via `initialize()` before every Run.

**Distinguished from:** the Problem Instance itself (which also includes the objective function, evaluation budget, and noise specification). The Search Space is only the structural description of valid inputs.

**Used in:** `docs/03-technical-contracts/01-data-format/02-problem-instance.md`, `docs/03-technical-contracts/02-interface-contracts/02-problem-interface.md`, `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`.

---

### Seed

**Definition:** An integer value injected by the Runner into a Problem Instance (via `reset(seed)`) and an Algorithm Instance (via `initialize(search_space, seed)`) before each Run to initialize all internal random number generators. Using a fixed Seed guarantees that the Run is reproducible.

**Distinguished from:** *Seed Strategy* (the policy by which the Runner assigns seeds across Runs in an Experiment). A Seed is the concrete integer value; the Seed Strategy is the procedure that produces it.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`, `docs/03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md`, `docs/03-technical-contracts/01-data-format/06-run.md`.

**Example:** The Runner assigns seed `42` to Run 7. Both `problem.reset(42)` and `algorithm.initialize(search_space, 42)` are called with this value before execution begins. Re-running with seed `42` on the same instances produces byte-identical Performance Records.

---

### Solution

**Definition:** A single candidate configuration — a point in the Search Space — represented as a list of values corresponding to the variables declared in the Search Space. Returned by `Algorithm.suggest()` and passed to `Problem.evaluate()`.

**Distinguished from:** the objective value (the scalar output produced by evaluating a Solution), and the EvaluationResult (the full outcome record that includes the objective value and metadata). A Solution is the input; the EvaluationResult is the output.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/02-problem-interface.md`, `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`.

---

### Study / Benchmarking Study

**Definition:** A pre-planned scientific investigation that compares the behavior of one or more Algorithm Instances on a defined set of Problem Instances, motivated by a specific Research Question, with experimental design fully specified before data collection begins.

**Distinguished from:** *Experiment* (the execution of a Study — the actual Runs performed). A Study is the plan; an Experiment is the realized plan.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 16, `docs/03-technical-contracts/01-data-format/04-study.md`, `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md`.

---

## Performance & Measurement

### Anytime Performance

**Definition:** The measurable quality of an algorithm's best-found solution at any evaluation count during a Run — captured as a continuous curve over the full Budget rather than reported only at termination.

**Distinguished from:** final-budget performance (a single endpoint value). Anytime Performance reveals optimization dynamics, early convergence, and performance at any intermediate budget level.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 14, `docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md`, `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §5.

---

### best_so_far

**Definition:** The minimum objective value (for minimization problems) or maximum (for maximization) observed across all evaluations from the start of a Run up to and including the current Evaluation Number. The `objective_value` field of a Performance Record always stores `best_so_far`, not the raw evaluation output at that step.

**Distinguished from:** the raw objective value of a single evaluation (which may be worse than previous evaluations). `best_so_far` is a monotonically non-increasing sequence for minimization problems throughout a Run.

**Used in:** `docs/03-technical-contracts/01-data-format/07-performance-record.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`, `docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md`.

---

### Budget

**Definition:** The resource limit allocated to a single Run, expressed as a maximum number of objective function evaluations, a wall-clock time limit, or both — agreed upon before the Run begins and held constant across all Algorithm Instances in a fair comparison.

**Distinguished from:** wall-clock time alone. Evaluation budget and time budget are different constraints; a fair study uses the same budget type for all algorithms.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 12, `docs/03-technical-contracts/01-data-format/02-problem-instance.md`, `docs/03-technical-contracts/02-interface-contracts/02-problem-interface.md`.

---

### cap_reached_at_evaluation

**Definition:** The Evaluation Number at which the Runner stopped writing improvement-triggered Performance Records for a Run because the `max_records_per_run` limit was reached. Set on the Run record when suppression begins; `null` if the cap was never hit. When set, the generated Report automatically includes a limitations note (FR-21).

**Distinguished from:** `budget_used` (the total evaluations consumed by the Run). `cap_reached_at_evaluation` is an early-stop marker for *improvement records only*; scheduled records continue to be written after it.

**Used in:** `docs/03-technical-contracts/01-data-format/06-run.md`, ADR-005.

---

### Effect Size

**Definition:** A quantitative measure of the practical magnitude of a performance difference between Algorithm Instances, computed independently of statistical significance, used to determine whether a statistically detected difference is large enough to matter in practice.

**Distinguished from:** p-value (which measures statistical evidence for a difference, not its magnitude). A difference can be highly statistically significant yet have a negligible Effect Size.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 13, `docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md`, `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §4.

---

### Evaluation Number

**Definition:** The 1-indexed count of objective function evaluations completed within a single Run, serving as the primary time axis for all anytime performance measurements. The first call to `Problem.evaluate()` within a Run yields `evaluation_number=1`; the last completed evaluation equals `budget_used`.

**Distinguished from:** wall-clock time (also recorded as `elapsed_time` in the Performance Record). The Evaluation Number is the canonical budget axis because it is deterministic and hardware-independent, enabling reproducible comparison across machines.

**Used in:** `docs/03-technical-contracts/01-data-format/07-performance-record.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`, `docs/03-technical-contracts/03-metric-taxonomy/`.

---

### Improvement Epsilon (ε)

**Definition:** The minimum reduction in `best_so_far` required for an evaluation to qualify as an improvement and fire the `improvement` trigger. When `null`, any strictly better value triggers a Performance Record. Non-null values suppress sub-threshold improvements, reducing storage volume but potentially hiding fine-grained convergence detail; non-null values must be scientifically justified and disclosed in the Report's limitations section (FR-21).

**Distinguished from:** the Sampling Strategy (the broader recording policy). Improvement Epsilon is a single parameter within the `improvement` trigger component of the `log_scale_plus_improvement` strategy.

**Used in:** `docs/03-technical-contracts/01-data-format/04-study.md`, ADR-004.

---

### is_improvement

**Definition:** A boolean field on a Performance Record that is `true` if the record's `best_so_far` value is strictly better (subject to Improvement Epsilon) than all previous Performance Records in the same Run, `false` otherwise. The first record of every Run is always `is_improvement=true`.

**Distinguished from:** the `trigger_reason` field. `is_improvement` describes the quality outcome; `trigger_reason` describes why the record was written. A record with `trigger_reason="scheduled"` and `is_improvement=false` is valid — a scheduled checkpoint that did not coincide with a quality improvement.

**Used in:** `docs/03-technical-contracts/01-data-format/07-performance-record.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`.

---

### Log-Scale Schedule

**Definition:** The set of Evaluation Numbers at which a `scheduled` Performance Record is written, constructed by the formula `base_points[i] × multiplier_base^j` for increasing `j`. The canonical parameters (`base_points=[1,2,5]`, `multiplier_base=10`) produce the COCO/IOHprofiler preferred-number series: 1, 2, 5, 10, 20, 50, 100, …

**Distinguished from:** the Sampling Strategy (the overall recording policy) and the `improvement` trigger (which fires on quality progress, not at predetermined points).

**Used in:** `docs/03-technical-contracts/01-data-format/04-study.md`, ADR-002.

---

### Performance Metric

**Definition:** A scalar quantity derived from one or more Runs that quantifies a specific aspect of algorithm behavior. All Performance Metrics used in this system are formally defined in `docs/03-technical-contracts/03-metric-taxonomy/01-metric-taxonomy.md`.

**Distinguished from:** raw objective function values (unaggregated outputs of individual evaluations). A Performance Metric is always computed from the results of one or more complete Runs.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 12, `docs/03-technical-contracts/03-metric-taxonomy/01-metric-taxonomy.md`, `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md`.

---

### Sampling Strategy

**Definition:** The named policy that governs which evaluations within a Run cause the Runner to write a Performance Record. Declared in the Study before execution begins and immutably locked with the Study. The canonical strategy is `log_scale_plus_improvement`, which combines a Log-Scale Schedule with an improvement trigger and a mandatory end-of-run record (ADR-002).

**Distinguished from:** the Log-Scale Schedule (which specifies the checkpoint positions within the `scheduled` trigger) and the Improvement Epsilon (which sets the sensitivity of the `improvement` trigger). The Sampling Strategy names the overall policy; the other two are parameters within it.

**Used in:** `docs/03-technical-contracts/01-data-format/04-study.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`, ADR-002.

---

### Trigger Reason

**Definition:** A string field on a Performance Record that identifies the condition or combination of conditions that caused the Runner to write the record. Atomic values are `scheduled`, `improvement`, and `end_of_run`; compound values encode simultaneous triggers: `both` (scheduled + improvement), `scheduled_end_of_run`, `improvement_end_of_run`, `all` (all three). Must be queried with a set-membership function, not substring matching, to avoid errors with compound values.

**Distinguished from:** `is_improvement` (a boolean indicating quality outcome). The Trigger Reason identifies *why* a record was written; `is_improvement` indicates *whether* the record represents a new quality peak.

**Used in:** `docs/03-technical-contracts/01-data-format/07-performance-record.md`, ADR-002.

---

## Scientific Concepts

### Conclusion Scope

**Definition:** The explicit, bounded domain to which a conclusion applies: the specific Problem Instances tested, the Budget level used, and any other conditions that constrain generalization. Every conclusion in a Report must carry a Conclusion Scope to prevent over-generalization (MANIFESTO Principle 3).

**Distinguished from:** the conclusion itself (the claim about algorithm performance). The Conclusion Scope is the mandatory boundary statement that accompanies the claim, making clear what the claim does *not* cover.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 3, `docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md`, `docs/03-technical-contracts/01-data-format/09-report.md`.

---

### Landscape Characteristics

**Definition:** Documented structural properties of a Problem Instance's objective function that influence algorithm selection and performance interpretation, stored as a list of string tags in the Problem Instance record. Derived from theoretical analysis or prior empirical study — not computed automatically during evaluation.

**Distinguished from:** the objective function itself and from the Search Space structure. Landscape Characteristics are human-readable annotations (e.g., `multimodal`, `separable`, `noisy`, `ill-conditioned`) that describe what is known about the problem's difficulty before running any algorithms.

**Used in:** `docs/03-technical-contracts/01-data-format/02-problem-instance.md`, `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md`.

**Example:** `["multimodal", "non-separable", "ill-conditioned"]`

---

### No Free Lunch (NFL)

**Definition:** The theoretical result stating that no optimization algorithm outperforms all others across all possible problem distributions when performance is averaged uniformly — implying that algorithm superiority is always conditional on the problem class.

**Implication for this system:** Global algorithm rankings are scientifically invalid. Every conclusion about algorithm performance must be scoped to the specific Problem Instances tested. The goal of this system is to map which algorithms work well for which problem characteristics, not to crown a winner.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 30, `docs/02-design/01-software-requirement-specification/SRS.md` §6 (Constraints).

---

### Pre-Registered Hypothesis

**Definition:** A specific statistical claim about expected algorithm behavior — formally declared in the Study record before any data is collected — against which the Analyzer's results are later tested. Separates confirmatory analysis (testing what was pre-specified) from exploratory analysis (post-hoc comparisons). The Report marks each comparison as `"pre_registered": true` or `false`.

**Distinguished from:** a post-hoc exploratory comparison (which the system still supports but marks as exploratory). Pre-registration is a scientific integrity practice enforced by convention, not by technical prevention (MANIFESTO Principle 16).

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 16, `docs/03-technical-contracts/01-data-format/04-study.md`, `docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md`.

---

### Provenance

**Definition:** The documented origin of a Problem Instance: whether it was derived from a real ML task, adapted from an existing benchmark suite, or created synthetically — plus a citation or URL to the originating source. Required for tracing the scientific lineage of any experimental result back to its source.

**Distinguished from:** `created_by` (who registered the instance in this system) and `code_reference` (where the implementation artifact is stored). Provenance describes the intellectual and scientific origin of the problem; `created_by` records technical authorship.

**Used in:** `docs/03-technical-contracts/01-data-format/02-problem-instance.md`, `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md`.

**Example:** `provenance="adapted_from_coco"` with `source_reference="https://coco.github.io"` indicates the problem was adapted from the COCO benchmark suite.

---

### Reproducibility

**Definition:** The property that a Study can be independently re-executed by a different team, using the archived Artifacts — complete code, exact library versions, input data, seeds, and result processing procedures — and produce the same Experiment results.

**Distinguished from:** *Replicability* (same team, different data), *Generalizability* (same method applied to new problems). This system targets Reproducibility as a hard requirement, not an aspiration.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principles 19–22, `docs/02-design/01-software-requirement-specification/SRS.md` §5 NFR-REPRO, `docs/05-community/02-versioning-governance.md`.

---

### Research Question

**Definition:** A precisely scoped scientific question that motivates a Study by naming: the Algorithm Instances or families to compare, the Problem Instance characteristics of interest, and the specific performance aspects to measure — stated before any data is collected.

**Distinguished from:** an informal motivation ("let's see how algorithm X does"). A valid Research Question is falsifiable, scoped, and drives the entire experimental design.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 1, `docs/03-technical-contracts/01-data-format/04-study.md`, `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md` Step 1.

---

### Seed Strategy

**Definition:** The named policy by which the Runner assigns integer Seed values to Runs within an Experiment. Declared in the Study before execution and locked with the Study. All seeds within an Experiment must be unique per `(problem_instance_id, algorithm_instance_id)` pair to guarantee statistically independent Runs.

**Distinguished from:** a Seed (the concrete integer value assigned to one Run). The Seed Strategy is the assignment policy; a Seed is a single outcome of applying that policy.

**Used in:** `docs/03-technical-contracts/01-data-format/04-study.md`, `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md`.

**Example:** `"sequential"` assigns seeds 0, 1, 2, … in scheduling order. `"latin-hypercube"` distributes seeds for better statistical coverage across the seed space.

---

## Ecosystem Terms

### Artifact

**Definition:** Any versioned, stored product of the system — a Problem Instance specification, Algorithm Implementation, Experiment record, Results dataset, or Analysis output — subject to the versioning and governance policy in `docs/05-community/02-versioning-governance.md`.

**Used in:** `docs/01-manifesto/MANIFESTO.md` Principle 21, `docs/05-community/02-versioning-governance.md`, `docs/03-technical-contracts/01-data-format/01-data-format.md`.

---

### BBOB (Black-Box Optimization Benchmarking)

**Definition:** A standardized suite of 24 single-objective continuous test functions distributed with the COCO framework, designed to evaluate optimizer behavior across a representative range of landscape properties including unimodal/multimodal, separable/non-separable, ill-conditioned, and noisy variants. Each function is parameterized by dimension and instance number; the instance number seeds random affine transformations (rotation, translation, scaling) of the base function, ensuring that different algorithm runs explore equivalent but non-identical problem realizations.

**Distinguished from:** *COCO* (the surrounding framework for experiment execution, data format, and post-processing — BBOB is one of several suites within COCO). Also distinct from `bbob-noisy` (stochastic variant), `bbob-mixint` (mixed-integer variant), and `bbob-biobj` (bi-objective variant).

**Used in:** `docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md` §4.1 (COCO export mapping).

---

### batch_size

**Definition:** The number of candidate Solutions requested from `Algorithm.suggest()` in a single call. All Algorithm implementations must accept any `batch_size ≥ 1`; implementations that do not natively support batching may invoke their single-suggestion logic `batch_size` times. The sequential V1 Runner always passes `batch_size=1`.

**Distinguished from:** parallelism (running multiple evaluations simultaneously). `batch_size` controls how many solutions are requested in one ask step; it does not imply concurrent evaluation in V1.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md`, `docs/06-tutorials/uc-02-contribute-algorithm.md`.

---

### code_reference

**Definition:** A version-pinned pointer to the executable Implementation of an Algorithm Instance — either a git commit SHA (e.g., `git+https://github.com/org/repo@abc1234`) or a pinned package version string (e.g., `optuna==3.6.1`). The `code_reference` is the reproducibility anchor for every Run: it must be resolvable and refer to an immutable artifact; branch names and `HEAD` are forbidden.

**Distinguished from:** `framework` and `framework_version` fields (which describe the library environment). The `code_reference` points to the exact artifact that produced experimental results; the framework fields provide environment context for reproduction.

**Used in:** `docs/03-technical-contracts/01-data-format/03-algorithm-instance.md`, `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md`, UC-02 F2.

---

### configuration_justification

**Definition:** A mandatory non-empty, human-readable explanation of why specific hyperparameter values were chosen for an Algorithm Instance — stated at registration time and stored in the Algorithm Instance record. Prevents undisclosed hyperparameter tuning to specific benchmarks and ensures fair comparison (MANIFESTO Principle 10).

**Distinguished from:** algorithm documentation or parameter descriptions. The `configuration_justification` is specific to *this configuration* registered *for this use case* — it must explain the scientific or practical rationale for the chosen values, not merely describe what the parameters mean.

**Used in:** `docs/03-technical-contracts/01-data-format/03-algorithm-instance.md`, `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md`, UC-02 F3.

---

### Deprecation

**Definition:** The act of marking an Algorithm Instance or Problem Instance as superseded, preventing it from appearing in new Study designs while preserving it indefinitely for exact reproduction of historical Experiments. A deprecated entity remains retrievable by explicit ID and version; it is excluded only from Registry listing results.

**Distinguished from:** deletion (which would break reproducibility of historical Experiments). Deprecation is a status change that preserves access for reproducibility; entities are never deleted from the Registry.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md`, `docs/05-community/02-versioning-governance.md`.

---

### Error Taxonomy

**Definition:** The hierarchy of typed exceptions that all interface implementations must use when reporting failures, rooted at `CorvusError`. Every exception carries `error_code` (string identifier), `message` (human-readable description), and `context` (dict of relevant field values at the time of failure). Using the taxonomy enables callers to catch specific failure categories without string parsing.

**Distinguished from:** Python's built-in exception hierarchy. Corvus Corone exceptions are domain-specific and replace bare `ValueError`, `RuntimeError`, etc. when the failure has a defined semantic meaning in the system. All exceptions are importable from `corvus_corone.exceptions`.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md`, all interface implementations.

---

### Information-Loss Manifest

**Definition:** A non-empty list of structured entries returned by every `export()` call, documenting every field, relationship, or semantic meaning that could not be fully preserved when converting Corvus Corone entities to a target external format. Each entry carries a manifest key (e.g., `LOSS-COCO-01`), a severity level (`critical`, `warning`, or `informational`), the condition under which the loss applies, and a human-readable description. The manifest is always non-empty — at minimum informational entries are present for every export — so that callers can make informed decisions about whether the output is fit for their downstream use case.

**Distinguished from:** error messages or exceptions (which indicate an operation that *failed*). The Information-Loss Manifest is returned on *success*; it documents completeness and semantic fidelity issues rather than failures. A `critical` severity entry may cause the export to be blocked unless the caller provides an explicit override mapping; `warning` entries require acknowledgement; `informational` entries are advisory only.

**Used in:** FR-26 (manifest delivery requirement), NFR-INTEROP-01 (non-empty manifest acceptance criterion), `docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md` §4.1.2 (COCO manifest items), §4.2–4.3 (pending).

---

### InterpolationStrategy

**Definition:** An abstract pluggable component held by the Analyzer that reconstructs the `best_so_far` value at an Evaluation Number that was not directly logged. The default implementation is **Last Observation Carried Forward** (LOCF): the value from the most recent Performance Record at or before the requested evaluation number. Non-default strategies must be declared in the Study record before execution and labeled in the Report's limitations section (ADR-003).

**Distinguished from:** the Sampling Strategy (which governs *which* evaluations are recorded). The InterpolationStrategy fills gaps *after* recording; the Sampling Strategy decides what to record in the first place.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md`, ADR-003.

---

### RepositoryFactory

**Definition:** The single object that groups all seven domain-specific repositories (Problem, Algorithm, Study, Experiment, Run, ResultAggregate, Report) and serves as the sole persistence access point passed to components needing cross-entity data access. Components receive a `RepositoryFactory` rather than individual repositories, keeping storage layout an implementation detail.

**Distinguished from:** a generic factory pattern. The RepositoryFactory is specifically the Corvus Corone persistence boundary that encapsulates the V1 local-file layout and will accommodate V2 server-backed storage without changing the interface contract.

**Used in:** `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md`.

---

### Schema Version

**Definition:** A `MAJOR.MINOR.PATCH` semantic version identifier stored in every Artifact record, recording the version of the data format specification (`docs/03-technical-contracts/01-data-format/`) under which the Artifact was created. The system uses this identifier to decide whether to accept, migrate, or reject an Artifact: same MAJOR → compatible (MINOR/PATCH differences are handled automatically); different MAJOR → incompatible, a migration script must be applied first.

**Format:** `MAJOR.MINOR.PATCH` where MAJOR increments on breaking changes (removed/renamed fields, type changes), MINOR increments on non-breaking additions (new optional fields, new entity types), and PATCH increments on corrections only.

**Used in:** `docs/03-technical-contracts/01-data-format/13-schema-versioning.md` §6.3–6.4, `docs/05-community/02-versioning-governance.md` §1–2; present in every entity record (Problem Instance, Algorithm Instance, Study, Experiment, Run, ResultAggregate, Report).

---

## Learner Actor & Education Platform

### Algorithm Genealogy

**Definition:** The historical lineage of an optimization method — what problem it was designed to solve, what methods preceded it, and what methods it inspired — presented as a directed graph from ancestor algorithms to descendants.

**Distinguished from:** an algorithm's *mathematical specification* (which describes how it works, not where it came from) and from *Algorithm Visualization* (which depicts how an algorithm searches, not its historical context). Algorithm Genealogy answers "where did this algorithm come from?"; Algorithm Visualization answers "how does it behave?".

**Used in:** `docs/02-design/01-software-requirement-specification/02-use-cases/11-uc-10.md` (UC-10: Algorithm History), `docs/02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot.md`. IMPL-046.

**Example:** The CMA-ES genealogy includes Evolution Strategies (1960s–1970s) as ancestors, CMA (1996) as the covariance-matrix refinement, and variants such as BIPOP-CMA-ES and separable CMA-ES as descendants. The genealogy records the design problem each step solved (e.g., "how to adapt step size without manual tuning").

---

### Algorithm Visualization

**Definition:** A graphical representation of an HPO algorithm's mechanics designed to serve two audiences: mathematically precise (for the Researcher and Algorithm Author who need exact characterization) and intuitively understandable (for the Learner who needs geometric or animated intuition). May be static (PNG/SVG), animated (GIF), or interactive (HTML).

**Distinguished from:** *Report visualizations* (the four Level 1 mandatory charts — VIZ-L1-01..04 — which compare algorithm *performance* across Runs). Algorithm Visualization depicts how an algorithm *searches* mechanically; Report visualizations compare how much *progress* different algorithms made. Algorithm Visualization is produced by the Algorithm Visualization Engine; Report visualizations are produced by the Reporting Engine.

**Used in:** `docs/02-design/01-software-requirement-specification/02-use-cases/08-uc-07.md` (UC-07: Algorithm Visualisation), `docs/02-design/02-architecture/03-c4-leve2-containers/06-algorithm-visualization-engine.md`, `docs/02-design/02-architecture/01-adr/adr-011-visualization-technology.md`. IMPL-044.

**Example:** A search trajectory scatter plot showing where TPE sampled candidates across a 2D search space is an Algorithm Visualization. A box-plot comparing QUALITY-BEST_VALUE_AT_BUDGET across three algorithms is a Report visualization.

---

### Learner

**Definition:** A user who consumes Researcher study results and algorithm documentation for educational purposes — to understand HPO algorithm behavior, mechanics, and historical context — rather than to conduct primary research or make operational algorithm selection decisions.

**Distinguished from:** *Researcher* (who conducts and reports Studies), *Practitioner* (who selects algorithms based on Study results for deployment), and *Algorithm Author* (who contributes implementations). The Learner is a **downstream read-only consumer** of artifacts produced by the Researcher. The Learner does not create or modify any Study, Experiment, or Report entity.

**Used in:** `docs/02-design/02-architecture/02-c4-leve1-context/01-c1-context.md` (C1 actor definition), `docs/02-design/01-software-requirement-specification/02-use-cases/01-use-cases.md` (UC-07..UC-11), `docs/02-design/02-architecture/03-c4-leve2-containers/06-algorithm-visualization-engine.md`, `docs/02-design/02-architecture/03-c4-leve2-containers/14-corvus-pilot.md`.

**Example:** A graduate student who has completed a benchmarking study with their supervisor and now wants to understand *why* CMA-ES outperformed random search on ill-conditioned problems is acting as a Learner. They read the Report produced by the Researcher, explore Algorithm Visualizations, and use Socratic mode to reason through the mechanism independently.

---

### Socratic Mode

**Definition:** An interaction mode in Corvus Pilot where the system guides the Learner toward understanding through targeted bridging questions rather than providing direct answers. Named after the Socratic method of inquiry. The system identifies the Learner's current knowledge state, identifies the gap between that state and the target understanding, and generates one question per turn that moves the Learner one reasoning step forward.

**Distinguished from:** *direct-answer mode* (the default Corvus Pilot mode, which answers factual and task queries immediately). Socratic Mode is explicitly opt-in: activated by the `--mode socratic` CLI flag or by `mode: "socratic"` in `PilotState`. The two modes differ in routing, output structure (question vs answer), and goal (maximise Learner's independent reasoning vs minimise turns to resolution). Socratic Mode is implemented as a separate LangGraph node (`socratic_guide`), not as a prompt modification of the direct-answer node.

**Used in:** `docs/02-design/01-software-requirement-specification/02-use-cases/10-uc-09.md` (UC-09: Socratic Guided Deduction), `docs/02-design/02-architecture/03-c4-leve2-containers/14-corvus-pilot.md`, `docs/02-design/02-architecture/04-c4-leve3-components/02-corvus-pilot.md` (Socratic Guide Node, Query Router), `docs/06-tutorials/05-learner-socratic-mode.md`. IMPL-045.

**Example:** Learner asks: "Why does CMA-ES use a covariance matrix?" Socratic Mode response: "What does the covariance matrix represent geometrically? Think about what information it encodes about the search space." The system does not answer the original question; it asks a question that helps the Learner derive the answer themselves.
