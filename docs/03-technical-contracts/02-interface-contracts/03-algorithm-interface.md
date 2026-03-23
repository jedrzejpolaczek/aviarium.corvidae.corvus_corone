# §2 Algorithm Interface

> Index: [01-interface-contracts.md](01-interface-contracts.md)

Any class that provides an HPO algorithm MUST implement all methods in this section.
The Algorithm Interface uses the **ask-tell** pattern: the Runner calls `suggest()` to request
candidate solutions, evaluates them via the Problem Interface, then calls `observe()` to feed
results back. All implementations MUST be stateful within a Run and stateless across Runs.

→ Used by: Experiment Runner (§3 — [04-runner-interface.md](04-runner-interface.md))

**Design decisions recorded here:**
- `observe()` is **required** — all algorithms must implement it (no-op is acceptable for
  non-adaptive algorithms; omitting the method causes `F1: Interface not satisfied`, UC-02)
- Search space variable types must be explicitly declared via `get_supported_variable_types()`
  — the Registry validates compatibility before Study execution
- `suggest()` supports batch proposals (`batch_size` parameter) — sequential runners always
  use `batch_size=1`; parallel runners may request larger batches

---

### suggest(context: RunContext, batch_size: int = 1) → list[Solution]

**Signature:**
- `context: RunContext` — `{ remaining_budget: int, elapsed_evaluations: int }`
- `batch_size: int` — number of solutions to propose; must be ≥ 1; default 1
- returns: `list[Solution]` — always a list; length equals `batch_size`

**Semantics:**
Proposes one or more candidate solutions (configurations) to evaluate.
This is the core "ask" step. When `batch_size=1`, the list contains exactly one solution.
Algorithms that do not natively support batching MUST still accept the parameter and
MAY implement it by invoking their single-suggestion logic `batch_size` times.

**Preconditions:**
- `initialize()` has been called before the first `suggest()` call
- `observe()` has been called for all solutions from the previous `suggest()` call
  (except on the very first call)
- `batch_size ≥ 1`

**Postconditions:**
- returned list length equals `batch_size`
- every Solution in the list is within the search space bounds declared during `initialize()`

**Isolation:**
An Algorithm Instance holds state across `suggest`/`observe` cycles within ONE Run.
State MUST NOT persist across Runs (enforced by `initialize()` resetting all internal state).

---

### observe(solution: Solution, result: EvaluationResult) → None

**Signature:**
- `solution: Solution` — the solution that was evaluated
- `result: EvaluationResult` — outcome from `Problem.evaluate()` (→ §1)
- returns: `None`

**Semantics:**
Updates the algorithm's internal model with the outcome of evaluating a solution.
This is the core "tell" step. **Implementation is required.** Non-adaptive algorithms
(e.g., random search) MUST still implement this method; a no-op body satisfies the contract.

**Preconditions:**
- `solution` was returned by the most recent `suggest()` call
- `result` is a valid `EvaluationResult` (→ data-format.md §2.6 output of Problem.evaluate())

---

### initialize(search_space: SearchSpace, seed: int) → None

**Signature:**
- `search_space: SearchSpace` — the Problem's search space for this Run (→ data-format.md §2.1)
- `seed: int` — run-specific seed injected by the Runner (never generated inside the algorithm)

**Semantics:**
Prepares the algorithm for a new Run on the given search space.
MUST be called once by the Runner before the first `suggest()` call.
MUST reset ALL internal state — no state from prior Runs may persist.

**Preconditions:**
- all variable types in `search_space` are present in `get_supported_variable_types()`
- `seed` is the Runner-assigned seed for this Run (cross-cutting contract §6)

**Postconditions:**
- all internal state is initialized deterministically from `seed`
- subsequent `suggest()`/`observe()` calls are reproducible given the same `seed`
- all state from any prior Run is discarded

---

### get_supported_variable_types() → list[str]

**Signature:**
- returns: `list[str]` — subset of `["continuous", "integer", "categorical"]`

**Semantics:**
Declares which search space variable types this algorithm supports.
The Registry validates Problem variable types against this list before allowing the Algorithm
to be paired with a Problem in a Study. An algorithm that declares only `["continuous"]`
MUST NOT be paired with a Problem whose search space contains `integer` or `categorical`
variables; the Registry rejects such pairings with a clear error message.

**Postconditions:**
- returned list is non-empty
- all values are from the set `{"continuous", "integer", "categorical"}`
- result is stable — returns the same list on every call, regardless of Run state

---

### get_metadata() → AlgorithmInstance

**Signature:**
- returns: `AlgorithmInstance` — → data-format.md §2.2

**Semantics:**
Returns the full Algorithm Instance record for this algorithm, including provenance,
`configuration_justification`, `code_reference`, and `supported_variable_types`.

**Postconditions:**
- `supported_variable_types` in the returned record matches `get_supported_variable_types()`
- `configuration_justification` is non-empty (validated at registration, UC-02 F3)
- `code_reference` is version-pinned (validated at registration, UC-02 F2)
