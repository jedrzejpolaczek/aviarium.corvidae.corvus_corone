# §1 Problem Interface

> Index: [01-interface-contracts.md](01-interface-contracts.md)

Any class that provides a benchmark problem MUST implement all methods in this section.
The Problem Interface is the boundary between the benchmark objective and the Runner.
Problems are evaluated sequentially by the Runner; the Runner owns the execution loop.

→ Used by: Experiment Runner (§3 — [04-runner-interface.md](04-runner-interface.md))

**Design decisions recorded here:**
- Problems are **stateful** — a Problem instance holds evaluation count and RNG state
  across calls within one Run. This simplifies the evaluate-and-record loop for the Runner.
- The Problem owns its RNG internally. The seed is provided by the Runner via `reset(seed)`
  before each Run — the seed (a value) is passed to the reset method, and the Problem creates
  its internal RNG from it. This satisfies the cross-cutting randomness isolation rule (§6)
  while keeping noise logic encapsulated in the Problem.
- Each Run gets its own Problem instance, or the same instance reset via `reset()` before
  the Run begins. Shared mutable state across Runs is forbidden (isolation contract, §3).

---

### evaluate(solution: Solution) → EvaluationResult

**Signature:**
- `solution: Solution` — a point in the search space (type defined by `get_search_space()`)
- returns: `EvaluationResult` — `{ objective_value: float, metadata: dict, evaluation_number: int }`

**Semantics:**
Evaluates the objective function at the given solution.
Increments the internal evaluation counter by exactly 1.
For stochastic problems, applies noise from the Problem's internal RNG (seeded via `reset()`).

**Preconditions:**
- `reset()` has been called at least once before the first `evaluate()` call
- `solution` is within the bounds declared by `get_search_space()`
- `get_remaining_budget() > 0`

**Postconditions:**
- `evaluation_number` in the returned result equals the previous value + 1
- for deterministic problems (`noise_level == "deterministic"`), the same `solution` always
  returns the same `objective_value` within the same Run
- `get_remaining_budget()` decreases by 1

**Exceptions:**
- `BudgetExhaustedError` — if `get_remaining_budget() == 0` before the call
- `InvalidSolutionError` — if `solution` violates search space constraints (wrong dimension
  or values outside bounds)
- `RuntimeError` — if `reset()` has not been called before the first `evaluate()`

**Isolation:**
Each Run gets its own `reset()` call. State from prior Runs MUST NOT affect evaluations
in the current Run. The Runner is responsible for calling `reset()` before each Run.

---

### get_search_space() → SearchSpace

**Signature:**
- returns: `SearchSpace` — → data-format.md §2.1 `variables` field

**Semantics:**
Returns the complete description of the search space for this problem.
The search space is fixed for the lifetime of the Problem instance.

**Postconditions:**
- result is immutable — calling `evaluate()` does not change the search space
- `dimensions` in the returned `SearchSpace` equals `len(variables)`

---

### get_metadata() → ProblemInstance

**Signature:**
- returns: `ProblemInstance` — → data-format.md §2.1

**Semantics:**
Returns the full Problem Instance record for this problem, including provenance,
landscape characteristics, and objective type.

**Postconditions:**
- returned record is complete and valid per data-format.md §2.1 validation rules
- `objective.known_optimum` is populated for all synthetic problems

---

### get_remaining_budget() → int

**Signature:**
- returns: `int` — remaining evaluation count for the current Run

**Semantics:**
Returns the number of `evaluate()` calls remaining before `BudgetExhaustedError` is raised.

**Postconditions:**
- result is non-negative; `0` means budget exhausted
- result equals `budget - evaluation_count` where `evaluation_count` is the number of
  successful `evaluate()` calls since the last `reset()`

---

### reset(seed: int) → None

**Signature:**
- `seed: int` — run-specific seed provided by the Runner

**Semantics:**
Resets internal state for a new Run. The Problem creates a fresh internal RNG from `seed`
and resets its evaluation counter to 0. This method is the mechanism by which the Runner
injects reproducible randomness into the Problem (cross-cutting contract §6).

**Preconditions:**
- `seed` is the Runner-assigned seed for this Run (never generated inside the Problem itself)

**Postconditions:**
- `get_remaining_budget()` returns the full budget
- subsequent `evaluate()` calls start from `evaluation_number = 1`
- all noise in subsequent evaluations is deterministically derived from `seed`
- any state from prior Runs (eval count, RNG state, cached values) is discarded
