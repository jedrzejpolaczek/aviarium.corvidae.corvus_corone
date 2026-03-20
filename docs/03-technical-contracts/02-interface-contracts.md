# Interface Contracts

<!--
STORY ROLE: The "handshake specification". Defines the boundaries between components.
A module is only as modular as its interface contracts are precise.
This document enables Value 6 (System adaptability): anyone can implement an interface
and plug into the system without reading other implementations.

NARRATIVE POSITION:
  C3 (component boundaries) → Interface Contracts → (formal boundary definitions)
  → C4 (code): concrete classes implement these contracts
  → community/contribution-guide.md: contributors implement these contracts

CONNECTS TO:
  ← C3                          : each component boundary visible there is formalized here
  ← SRS §4, §7                  : requirements for interoperability and modularity
  → specs/data-format.md        : all input/output types reference entities defined there
  → specs/metric-taxonomy.md    : metric-related return types reference taxonomy names
  → community/contribution-guide.md : all contribution types must implement a contract here
  → C4                          : code-level abstractions implement these contracts
  → Docstrings                  : every public method must have docstrings that document
                                  the contracts stated here (pre/postconditions, exceptions)

GLOSSARY: All terms from docs/GLOSSARY.md apply. Use exact glossary terms.

CONTRACT FORMAT for each method:
  - Signature: parameter names and types (reference data-format.md for complex types)
  - Semantics: what does this method DO? (not how — that is implementation detail)
  - Preconditions: what must be true BEFORE calling this method?
  - Postconditions: what is guaranteed to be true AFTER a successful call?
  - Exceptions: what error conditions does this method raise and when?
  - Thread/isolation safety: can this be called concurrently?
  - Docstring requirement: what sections are mandatory in the implementing class?
-->

---

## 1. Problem Interface

<!--
  What must every benchmark Problem Instance expose to the system.
  Any class, module, or service that provides a benchmark problem MUST implement this interface.
  → Used by: Experiment Runner (§3 below)

  ### evaluate(solution) → EvaluationResult
    Signature:
      solution: a point in the search space (type defined by get_search_space() output)
      returns: EvaluationResult { objective_value: float, metadata: dict, evaluation_number: int }
    Semantics:
      Evaluates the objective function at the given solution.
      Records evaluation in the Performance Record stream (→ data-format.md §2.6).
    Preconditions:
      - solution must be within the bounds declared by get_search_space()
      - budget has not been exhausted (check get_remaining_budget() > 0)
    Postconditions:
      - returned objective_value is deterministic for the same solution IF noise_level == "deterministic"
      - evaluation_number increments by exactly 1 per call
    Exceptions:
      - BudgetExhaustedException if budget is exhausted
      - InvalidSolutionException if solution violates search space constraints
    Isolation:
      Each Run gets its own Problem Instance; shared state across runs is forbidden.

  ### get_search_space() → SearchSpace
    Semantics: returns the complete description of the search space
    → SearchSpace type: data-format.md §2.1 variables field
    Postconditions: result is immutable; calling evaluate() does not change the search space

  ### get_metadata() → ProblemInstance
    Semantics: returns the full Problem Instance record for this problem
    → ProblemInstance type: data-format.md §2.1
    Postconditions: returned record is complete and valid per data-format.md validation rules

  ### get_remaining_budget() → int | float
    Semantics: returns the remaining evaluation budget for the current Run
    Postconditions: result is non-negative; 0 means budget exhausted

  ### reset(seed: int)
    Semantics: resets internal state for a new Run with the given seed
    Postconditions: subsequent calls to evaluate() start from evaluation_number = 0
    Note: This is the mechanism by which the Runner injects reproducible randomness.

  Additional hints:
    - Should Problems be stateless or stateful? → record decision in an ADR
    - How is noise injected? Does the Problem own the random state, or is it injected?
-->

---

## 2. Algorithm Interface

<!--
  What must every Algorithm Implementation expose to the system.
  → Used by: Experiment Runner (§3 below)

  ### suggest(context: RunContext) → Solution
    Signature:
      context: RunContext { remaining_budget: int, elapsed_evaluations: int }
      returns: Solution (a point in the search space, matching the Problem's search space)
    Semantics:
      Proposes the next configuration (solution) to evaluate.
      This is the core "ask" step in the ask-tell interface pattern.
    Preconditions:
      - observe() has been called for all previously suggested solutions (or this is the first call)
      - The Algorithm has been initialized for the current problem's search space
    Postconditions:
      - returned Solution is within the search space bounds declared during initialization
    Isolation:
      An Algorithm Instance holds state across suggest/observe cycles within ONE Run.
      State MUST NOT persist across Runs.

  ### observe(solution: Solution, result: EvaluationResult) → None
    Semantics:
      Updates the algorithm's internal model with the outcome of evaluating a solution.
      This is the core "tell" step.
    Preconditions:
      - solution was returned by the most recent call to suggest()
      - result is a valid EvaluationResult from the Problem Interface

  ### initialize(search_space: SearchSpace, seed: int) → None
    Semantics:
      Prepares the algorithm for a new Run on the given search space.
      Must be called once before the first suggest() call.
    Postconditions:
      - All internal state is initialized deterministically from seed
      - Subsequent suggest()/observe() calls are reproducible given same seed

  ### get_metadata() → AlgorithmInstance
    → AlgorithmInstance type: data-format.md §2.2

  Additional hints:
    - Ask-tell vs. ask-only interface: should observe() be required? → ADR candidate
    - How does the algorithm declare which search space types it supports?
      (e.g., "only continuous", "categorical OK") → part of AlgorithmInstance.known_assumptions
    - Batch suggestions: should suggest() support returning multiple solutions at once?
-->

---

## 3. Runner Interface

<!--
  The Experiment Runner orchestrates Problems and Algorithms to produce Runs.
  → Used by: researcher (via CLI/API), Experiment container (C2)

  ### run_study(study: Study) → Experiment
    Semantics:
      Executes all Runs defined by the Study plan.
      For each (problem, algorithm, repetition) combination: initializes, runs, records.
    Returns: a completed Experiment record with all Run IDs populated
    → Study type: data-format.md §2.3
    → Experiment type: data-format.md §2.4

  ### run_single(problem_id, algorithm_id, seed, budget) → Run
    Semantics:
      Executes a single Run. Lower-level than run_study().
      Used for: debugging, incremental execution, custom orchestration.

  ### resume(experiment_id: str) → Experiment
    Semantics:
      Resumes an interrupted Experiment from its last checkpoint.
      → MANIFESTO Principle "Checkpoint and restart" (from notes.md)
    Preconditions:
      - experiment exists in the Results Store
      - incomplete Runs are identifiable from stored state

  Isolation contract (critical for reproducibility):
    - Each Run executes in isolation: no shared mutable state between runs
    - Seeds are injected by the Runner, never generated inside Problem or Algorithm
    - The Runner records the full execution environment → data-format.md §2.4
    → SRS NFR-REPRO

  Additional hints:
    - Parallel execution: how does the Runner manage concurrent runs?
      Shared-memory parallelism vs. process isolation vs. distributed? → ADR candidate
    - How are failures handled? Retry? Skip? Abort study?
    - What is logged at the Runner level vs. at the Problem level?
-->

---

## 4. Analyzer Interface

<!--
  The Measurement & Analysis Engine consumes Run data and produces Results and insights.
  → Used by: researcher (via API/reports), Reporting Layer (C2)

  ### analyze(experiment_id: str, config: AnalysisConfig) → AnalysisReport
    Semantics:
      Runs the three-level analysis (→ methodology/statistical-methodology.md) on all
      Runs in the specified Experiment.
    Returns: AnalysisReport containing Result Aggregates, statistical test results,
             visualizations, and scoped conclusions.
    → AnalysisConfig specifies: which metrics to compute, which statistical tests to apply,
      which hypothesis list to test (pre-registered in the Study)

  ### compute_metrics(run_ids: list, metric_names: list) → list[ResultAggregate]
    Semantics:
      Computes specified metrics for specified Runs.
      Metric names must be valid entries from specs/metric-taxonomy.md.
    Postconditions:
      - every metric_name in input is present in every ResultAggregate in output
      - ResultAggregate.n_runs equals len(run_ids)

  ### compare(experiment_id, algorithm_ids, metric_name, test_config) → StatisticalTestResult
    Semantics:
      Applies a specified statistical test to compare algorithms on a metric.
      → methodology/statistical-methodology.md §2 (test selection)
    Returns: StatisticalTestResult { test_name, p_value, effect_size, conclusion_scope }
    Postconditions:
      - conclusion_scope explicitly states which problems and conditions the conclusion applies to
        (prevents over-generalization, Principle 3)

  Additional hints:
    - Should analysis be streaming (incremental as runs complete) or batch (after all runs)?
    - How are pre-registered hypotheses enforced? (system-level check vs. convention?)
      → If system-enforced, this is a significant design decision → ADR candidate
-->

---

## 5. Repository Interface

<!--
  How does code read/write Problems, Algorithms, Experiments, and Results.
  → Used by: all containers that need to access stored artifacts

  ### get_problem(id: str, version: str | None) → ProblemInstance
  ### list_problems(filters: ProblemFilter) → list[ProblemInstanceSummary]
  ### register_problem(problem: ProblemInstance) → str  (returns assigned ID)
  ### deprecate_problem(id: str, reason: str, superseded_by: str | None)

  Similarly for: Algorithm, Study, Experiment, Run, ResultAggregate

  Versioning semantics:
    - get_*(id, version=None) returns the latest non-deprecated version
    - get_*(id, version="1.2.3") returns exactly that version (for reproducibility)
    → versioning policy: community/versioning-governance.md §1

  Hint: should this be a single repository interface or separate interfaces per entity type?
  → ADR candidate: monolithic repository vs. domain-specific repositories
-->

---

## 6. Cross-Cutting Contracts

<!--
  Contracts that apply to ALL interface implementations in this system.
  These are the system-wide rules that make the whole greater than the sum of its parts.

  ### Structured Logging
    Every implementation of every interface MUST emit structured logs at defined points.
    Log format: [to be defined — JSON? structured text?]
    Mandatory log events: method entry/exit for public methods, exceptions raised,
    seed used, budget consumed.
    → This enables audit trails and debugging without breaking reproducibility.

  ### Randomness Isolation
    No implementation may generate random numbers without receiving a seed from outside.
    All randomness must flow from seeds injected by the Runner (§3).
    Forbidden: calling random.random(), np.random.random(), etc. without a seed parameter.
    → MANIFESTO Principle 18; SRS NFR-REPRO

  ### Error Taxonomy
    Define the error/exception hierarchy that all interfaces use.
    Hint — top-level categories:
      - ValidationError (input does not conform to contract)
      - BudgetError (budget exhausted or invalid)
      - ReproducibilityError (seed not set, state not isolated)
      - StorageError (repository unavailable or corrupt)
      - IntegrationError (external system unavailable)
    All exceptions must carry: error_code, human-readable message, context dict.

  ### Version Declaration
    Every implementation must expose a declared_version() → str method.
    This version is recorded in the AlgorithmInstance / ProblemInstance record.
    → data-format.md §2.1 and §2.2 provenance fields

  ### Docstring Requirements
    Every public method of every interface implementation MUST have docstrings containing:
      - One-line summary
      - Parameters section (name, type, semantics for each)
      - Returns section (type and semantics)
      - Raises section (each exception from §Error Taxonomy that this method raises)
      - At least one Example section
      - References to relevant specs (metric name → metric-taxonomy.md, etc.)
    → C4 code documents specify additional per-component docstring requirements
-->
