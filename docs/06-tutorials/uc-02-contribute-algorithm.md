# Tutorial: Contribute an Algorithm Implementation (UC-02)

**Actor:** Algorithm Author
**Goal:** Register a new Algorithm Instance so it is available for fair evaluation in Studies

**Connects to:**
- Use case: [UC-02](../02-design/01-software-requirement-specification/02-use-cases/03-uc-02.md)
- Interface contract: [§2 Algorithm Interface](../03-technical-contracts/02-interface-contracts/03-algorithm-interface.md)
- Data schema: [§2.2 Algorithm Instance](../03-technical-contracts/01-data-format/03-algorithm-instance.md)
- Cross-cutting rules: [§6 Cross-Cutting Contracts](../03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md)

---

## Overview

Contributing an algorithm has four steps:

1. [Read the interface contract](#step-1-read-the-interface-contract)
2. [Implement the adapter](#step-2-implement-the-adapter)
3. [Construct the Algorithm Instance record](#step-3-construct-the-algorithm-instance-record)
4. [Register and (optionally) test](#step-4-register-and-optionally-test)

Most adapters for existing optimizers require **≤15 lines** of adapter code (NFR-USABILITY-01).
The rest of this tutorial shows you exactly what those lines must do.

---

## Step 1: Read the Interface Contract

The Algorithm Interface uses the **ask-tell** pattern. The Runner drives the loop:

```
Runner calls  algorithm.initialize(search_space, seed)   # before every Run
Runner calls  algorithm.suggest(context, batch_size=1)   # ask for a candidate
Runner calls  problem.evaluate(solution)                 # evaluate it
Runner calls  algorithm.observe(solution, result)        # tell the outcome
... repeat until budget exhausted ...
```

Your class must implement exactly these five methods:

| Method | Purpose |
|---|---|
| `initialize(search_space, seed)` | Prepare for a new Run; reset ALL internal state |
| `suggest(context, batch_size=1) → list[Solution]` | Return `batch_size` candidate solutions |
| `observe(solution, result) → None` | Update internal model with evaluation outcome |
| `get_supported_variable_types() → list[str]` | Declare which variable types you handle |
| `get_metadata() → AlgorithmInstance` | Return the full provenance record |

Key contracts you must satisfy before reading further:

- **Seed isolation.** Never call `random.random()` or `numpy.random.random()` without a seed.
  Always create your RNG from the seed injected by `initialize()`. See
  [§6 Randomness Isolation](../03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md).
- **State reset.** `initialize()` must discard all state from prior Runs. A Run that starts with
  stale state from a previous Run violates reproducibility (MANIFESTO Principle 18).
- **`observe()` is required.** Even if your algorithm ignores observations (e.g., random search),
  the method must exist. A missing `observe()` causes **F1: Interface not satisfied** at registration.
- **Bounds compliance.** Every solution returned by `suggest()` must lie within the bounds
  declared in `search_space`.

---

## Step 2: Implement the Adapter

### Minimal example: random search (7 lines of logic)

This is the simplest possible compliant implementation. It demonstrates all five required
methods and the seed isolation pattern.

```python
import random
from typing import Any


class RandomSearchAlgorithm:
    """Uniform random search — samples uniformly from the search space.

    Satisfies Algorithm Interface §2.
    All randomness flows from the seed injected by initialize() (§6).
    """

    def __init__(self, algorithm_id: str) -> None:
        self._id = algorithm_id
        self._search_space = None
        self._rng: random.Random | None = None

    # ── Required: called once by Runner before every Run ─────────────────────

    def initialize(self, search_space, seed: int) -> None:
        self._search_space = search_space          # store for suggest()
        self._rng = random.Random(seed)            # seed-isolated RNG

    # ── Required: ask step ────────────────────────────────────────────────────

    def suggest(self, context: dict[str, Any], batch_size: int = 1) -> list[list[float]]:
        lo, hi = self._search_space.lower, self._search_space.upper
        dims = self._search_space.dimensions
        return [
            [self._rng.uniform(lo, hi) for _ in range(dims)]
            for _ in range(batch_size)
        ]

    # ── Required: tell step ───────────────────────────────────────────────────

    def observe(self, solution, result) -> None:
        pass  # no-op: random search does not adapt

    # ── Required: variable type declaration ──────────────────────────────────

    def get_supported_variable_types(self) -> list[str]:
        return ["continuous"]

    # ── Required: provenance record ───────────────────────────────────────────

    def get_metadata(self) -> dict[str, Any]:
        return {
            "id": self._id,
            "name": "RandomSearch-v1.0.0",
            "version": "1.0.0",
            "algorithm_family": "random",
            "hyperparameters": {},
            "configuration_justification": (
                "Uniform random sampling over the continuous search space. "
                "No hyperparameters to configure. Used as a performance baseline."
            ),
            "code_reference": "git+https://github.com/org/repo@abc1234",
            "language": "python",
            "framework": "stdlib",
            "framework_version": "3.12",
            "known_assumptions": ["continuous search space"],
            "contributed_by": "your-name",
            "supported_variable_types": self.get_supported_variable_types(),
        }
```

### Realistic example: wrapping an existing optimizer (≤15 adapter lines)

If you already have an optimizer object, your adapter typically wraps it in ≤15 lines:

```python
import numpy as np
from typing import Any


class MyOptunaTPEAdapter:
    """Thin adapter wrapping Optuna's TPE sampler.

    The adapter translates between the Corvus Corone ask-tell interface
    and Optuna's internal suggest/tell API. All Optuna state is created
    fresh in initialize() and discarded there on the next call.
    """

    def __init__(self, algorithm_id: str, n_startup_trials: int = 10) -> None:
        self._id = algorithm_id
        self._n_startup_trials = n_startup_trials
        self._sampler = None          # created in initialize()
        self._study = None            # created in initialize()
        self._search_space = None

    def initialize(self, search_space, seed: int) -> None:
        import optuna
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        self._search_space = search_space
        self._sampler = optuna.samplers.TPESampler(
            seed=seed,                                 # ← seed injected by Runner
            n_startup_trials=self._n_startup_trials,
        )
        self._study = optuna.create_study(sampler=self._sampler, direction="minimize")

    def suggest(self, context: dict[str, Any], batch_size: int = 1) -> list[list[float]]:
        solutions = []
        for _ in range(batch_size):
            trial = self._study.ask()
            lo, hi = self._search_space.lower, self._search_space.upper
            point = [
                trial.suggest_float(f"x{i}", lo, hi)
                for i in range(self._search_space.dimensions)
            ]
            solutions.append(point)
        return solutions

    def observe(self, solution, result) -> None:
        # Tell Optuna the outcome of the most recent trial
        trial = self._study.trials[-1]
        self._study.tell(trial, result.objective_value)

    def get_supported_variable_types(self) -> list[str]:
        return ["continuous", "integer", "categorical"]

    def get_metadata(self) -> dict[str, Any]:
        return {
            "id": self._id,
            "name": "OptunaTPE-v3.6.1",
            "version": "1.0.0",
            "algorithm_family": "TPE",
            "hyperparameters": {"n_startup_trials": self._n_startup_trials},
            "configuration_justification": (
                f"n_startup_trials={self._n_startup_trials} chosen to balance "
                "random exploration against model-guided exploitation for budgets "
                "of 100–500 evaluations on 5–20 dimensional problems. "
                "Default Optuna TPE otherwise."
            ),
            "code_reference": "optuna==3.6.1",          # ← pinned version (F2)
            "language": "python",
            "framework": "optuna",
            "framework_version": "3.6.1",
            "known_assumptions": ["continuous search space", "noise-free evaluations"],
            "contributed_by": "your-name",
            "supported_variable_types": self.get_supported_variable_types(),
        }
```

---

## Step 3: Construct the Algorithm Instance Record

The Algorithm Instance record is what the Registry validates and stores. It comes from
`get_metadata()`. Every field in the table below is checked at registration.

| Field | Required | Validation rule |
|---|---|---|
| `id` | yes | unique UUID |
| `name` | yes | human-readable |
| `version` | yes | matches `^\\d+\\.\\d+\\.\\d+$` |
| `algorithm_family` | yes | free text identifying the algorithm class |
| `hyperparameters` | yes | all keys must match the declared parameter schema |
| `configuration_justification` | yes | **non-empty** — explains why this configuration (Principle 10). Blank string causes **F3** |
| `code_reference` | yes | **version-pinned** — git SHA or exact package version. Branch names cause **F2** |
| `language` | yes | e.g. `"python"` |
| `framework` | yes | e.g. `"optuna"` |
| `framework_version` | yes | pinned (e.g. `"3.6.1"`) |
| `known_assumptions` | yes | problem properties your algorithm requires |
| `contributed_by` | yes | author identifier |
| `supported_variable_types` | yes | must match `get_supported_variable_types()` |

### Common mistakes that cause registration failure

**F1 — Interface not satisfied:** The method `observe()` is missing or has the wrong signature.
```python
# WRONG — method missing entirely
class BadAlgorithm:
    def suggest(self, ...): ...
    # ← no observe() → F1

# CORRECT — no-op is fine
class GoodAlgorithm:
    def observe(self, solution, result) -> None:
        pass  # explicitly no-op
```

**F2 — Code reference unresolvable:** Using a branch name instead of a pinned version.
```python
# WRONG
"code_reference": "git+https://github.com/org/repo@main"   # floating ref

# CORRECT
"code_reference": "git+https://github.com/org/repo@abc1234"  # exact SHA
"code_reference": "scipy==1.13.0"                            # pinned package
```

**F3 — Missing configuration justification:** Leaving the field empty.
```python
# WRONG
"configuration_justification": ""          # empty string → F3
"configuration_justification": "default"   # content-free → F3

# CORRECT — explains the why, not just the what
"configuration_justification": (
    "n_startup_trials=10 matches the expected budget range of 100–500 "
    "evaluations; lower values would reduce exploration in early phases."
)
```

**F4 — Hyperparameter schema mismatch:** Declared hyperparameter keys do not match the
algorithm's known schema.
```python
# WRONG — key name differs from what the algorithm actually uses
"hyperparameters": {"n_startup": 10}   # algorithm uses "n_startup_trials"

# CORRECT
"hyperparameters": {"n_startup_trials": 10}
```

---

## Step 4: Register and (Optionally) Test

### Registering

Pass your algorithm instance to the Algorithm Registry:

```python
from corvus_corone.registry import AlgorithmRegistry

registry = AlgorithmRegistry(repository_factory)

algorithm = MyOptunaTPEAdapter(algorithm_id="tpe-v1")
algorithm_instance_id = registry.register(algorithm)
print(f"Registered: {algorithm_instance_id}")
```

The Registry runs all four validation checks (F1–F4) and raises a `ValidationError` or
`CodeReferenceError` with a specific error message if any check fails
(→ [§6 Error Taxonomy](../03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md)).

### Running a smoke test (optional but recommended)

UC-02 Step 6 recommends verifying your adapter against a known Problem Instance before
including it in a Study. The simplest way is to run it through a `run_single()` call:

```python
from corvus_corone.runner import Runner
from corvus_corone.registry import ProblemRegistry

# Retrieve a known problem from the registry
problem = ProblemRegistry(repository_factory).get("sphere-5d-v1.0.0")

runner = Runner(repository_factory)
run = runner.run_single(
    problem_id="sphere-5d-v1.0.0",
    algorithm_id=algorithm_instance_id,
    seed=42,
    budget=50,
)

assert run.status == "completed", f"Run failed: {run.failure_reason}"
print(f"Best value at budget: {run.records[-1].best_so_far}")
```

A completed run with no exception confirms:
- `initialize()` and `suggest()` produce valid solutions within bounds
- `observe()` does not raise
- `get_supported_variable_types()` is compatible with the test problem's variable types
- The seed isolation contract is satisfied (same seed → same run)

---

## Checklist before submitting

- [ ] `initialize()` resets all state (no stale values from prior Runs)
- [ ] RNG is created from the injected `seed`, not from `random.random()` or `numpy.random.random()`
- [ ] `suggest()` always returns a list of length `batch_size`
- [ ] All solutions in the returned list are within `search_space` bounds
- [ ] `observe()` exists (no-op is fine)
- [ ] `get_supported_variable_types()` returns a non-empty subset of `["continuous", "integer", "categorical"]`
- [ ] `code_reference` is version-pinned (no branch names)
- [ ] `configuration_justification` is non-empty and explains the *why*
- [ ] `hyperparameter` keys match the algorithm's declared schema
- [ ] Smoke test against a known Problem Instance passes

---

## What happens after registration

Once registered, the Algorithm Instance is:

1. **Stored** in the Algorithm Registry with full provenance (`contributed_by`, `created_at`,
   `code_reference`).
2. **Available** for inclusion in Study designs (UC-01).
3. **Validated** at Study execution time — the Runner checks that `get_supported_variable_types()`
   is compatible with each Problem's variable types before the run begins.
4. **Version-locked** in every Run that uses it. The `code_reference` stored in the Instance
   record is the artifact the reproducibility guarantee rests on (MANIFESTO Principle 19).

> **Deprecation:** If you later supersede this instance, use `deprecate_algorithm(id, reason,
> superseded_by=new_id)`. Deprecated instances remain retrievable for reproducibility but no
> longer appear in Registry listings.
