# Tutorial: Wrap an Optuna Sampler in ≤15 Lines

<!--
STORY ROLE: The interface test disguised as a tutorial. Demonstrates that the Algorithm
Interface has the right surface area for third-party contributors: if wrapping an Optuna
sampler requires more than 15 lines of behavioral code, the interface is too wide.
A new Algorithm Author should be able to complete this tutorial without reading any
other document first.

NARRATIVE POSITION:
  Algorithm Interface (§2) → this tutorial → (running adapter in a Study)
  This is the ENTRY POINT for Algorithm Authors.

CONNECTS TO:
  → docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md §2 : the contract this tutorial implements
  → docs/03-technical-contracts/01-data-format/03-algorithm-instance.md §2.2 : schema for get_metadata()
  → docs/06-tutorials/uc-02-contribute-algorithm.md : full contribution guide (next step after this tutorial)
  → docs/05-community/01-contribution-guide.md §3 : review criteria for submitted algorithms
  → docs/01-manifesto/MANIFESTO.md Principle 10 : default configuration justification
  → docs/01-manifesto/MANIFESTO.md Principle 18 : state reset requirement
-->

---

## Audience

**Role:** Algorithm Author — you have an existing optimizer (here: Optuna) and want it
to be evaluated in a corvus_corone benchmarking Study.

**Prior knowledge assumed:**
- Python: comfortable writing a class with methods
- Optimization: familiar with the concept of a hyperparameter tuner that proposes
  candidates and receives feedback (no HPO theory required)
- System: corvus_corone installed; you have not necessarily read any other documentation

**Not required:** familiarity with the Benchmarking Protocol, metric taxonomy, or
statistical methodology. This tutorial produces a working Algorithm Instance; the rest
of the system handles everything else.

---

## Learning Objective

After completing this tutorial, the reader will be able to wrap any Optuna sampler as
a compliant Algorithm Instance that registers and runs without error in a corvus_corone
Study — writing ≤15 lines of behavioral adapter code.

---

## Prerequisites

```bash
pip install optuna          # tested with optuna>=3.0
pip install corvus_corone   # see installation guide for version
```

No other packages required for this tutorial.

---

## Overview

The corvus_corone Runner drives all optimization loops using an **ask-tell** pattern:

```
runner → algorithm.initialize(search_space, seed)   # once per Run
runner → algorithm.suggest(context)                 # ask for a candidate
runner → problem.evaluate(solution)                 # runner evaluates it
runner → algorithm.observe(solution, result)        # tell the outcome
         ... repeat until budget exhausted ...
```

Your job is to implement three behavioral methods — `initialize`, `suggest`, `observe` —
plus two metadata methods. For Optuna, the three behavioral methods fit in exactly 15 lines.

This tutorial walks through each method, explains the one contract that matters most
(seed isolation), then shows how to register and verify the adapter.

---

## Steps

### Step 1: Understand the three contracts

Before writing any code, read these three rules. They are the only contracts the Runner
enforces at registration time:

**Contract 1 — Seed isolation.**
`initialize()` receives a `seed` integer from the Runner. You MUST create all
randomness from this seed and nowhere else. Never call `random.random()` or
`numpy.random.random()` unseeded. Reason: the same seed must produce the same Run
(MANIFESTO Principle 18).

**Contract 2 — State reset.**
`initialize()` must discard all state from any previous Run. The Runner calls
`initialize()` before EVERY Run, reusing the same object. An adapter that carries
over state from Run 1 into Run 2 silently corrupts the experiment.

**Contract 3 — `observe()` must exist.**
Even if your algorithm ignores feedback (e.g., random search), `observe()` must be
declared. A missing `observe()` raises `InterfaceViolationError` at registration.

For the full method signatures and edge cases, see
[§2 Algorithm Interface](../03-technical-contracts/02-interface-contracts/03-algorithm-interface.md).

---

### Step 2: Write the 15-line behavioral adapter

The three behavioral methods (`initialize`, `suggest`, `observe`) are the adapter.
Everything else is metadata boilerplate.

Create a file `my_tpe_adapter.py`:

```python
import optuna

optuna.logging.set_verbosity(optuna.logging.WARNING)


class OptunaTPEAdapter:
    """Thin adapter: wraps Optuna's TPE sampler in the corvus_corone ask-tell interface."""

    def __init__(self, algorithm_id: str, n_startup_trials: int = 10) -> None:
        self._id = algorithm_id
        self._n = n_startup_trials
        self._study = None    # created fresh in initialize() — never shared across Runs
        self._space = None

    # ── 15-line behavioral core ───────────────────────────────────────────────

    def initialize(self, search_space, seed: int) -> None:          # line 1
        self._space = search_space                                   # line 2
        sampler = optuna.samplers.TPESampler(                        # line 3
            seed=seed,                         # ← Contract 1        # line 4
            n_startup_trials=self._n,                                # line 5
        )                                                            # line 6
        self._study = optuna.create_study(                           # line 7
            sampler=sampler, direction="minimize"                    # line 8
        )                                      # ← Contract 2 (new study = reset)  # line 9

    def suggest(self, context, batch_size: int = 1) -> list:        # line 10
        lo, hi = self._space.lower, self._space.upper               # line 11
        return [                                                     # line 12
            [self._study.ask().suggest_float(f"x{i}", lo, hi)       # line 13
             for i in range(self._space.dimensions)]                 # line 14
            for _ in range(batch_size)                               # line 15
        ]

    def observe(self, solution, result) -> None:                    # ← Contract 3
        self._study.tell(self._study.trials[-1], result.objective_value)

    # ── Metadata boilerplate (not counted in the 15-line limit) ──────────────

    def get_supported_variable_types(self) -> list[str]:
        return ["continuous"]

    def get_metadata(self) -> dict:
        return {
            "id": self._id,
            "name": "OptunaTPE-tutorial",
            "version": "1.0.0",
            "algorithm_family": "TPE",
            "hyperparameters": {"n_startup_trials": self._n},
            "configuration_justification": (
                f"n_startup_trials={self._n} balances random exploration against "
                "model-guided exploitation for budgets of 100–500 evaluations on "
                "5–20 dimensional continuous problems."
            ),
            "code_reference": "optuna==3.6.1",    # ← must be a pinned version
            "language": "python",
            "framework": "optuna",
            "framework_version": "3.6.1",
            "known_assumptions": ["continuous search space", "noise-free evaluations"],
            "contributed_by": "your-name",
            "supported_variable_types": self.get_supported_variable_types(),
        }
```

**Why `observe()` has only 1 line of logic:**
Optuna's `study.tell()` updates the internal model. The Runner already guaranteed that
`suggest()` was called immediately before this `observe()`, so `trials[-1]` is always
the trial we just asked for.

**Why the line count stops at `observe()`:**
`get_supported_variable_types()` and `get_metadata()` are metadata declarations, not
algorithm behavior. They do not affect how the optimizer searches; they exist so the
Registry can store provenance and validate compatibility.

> **Checkpoint:** The file parses without error:
> ```bash
> python -c "from my_tpe_adapter import OptunaTPEAdapter; print('OK')"
> ```

---

### Step 3: Verify the metadata record

`get_metadata()` is validated at registration. Two fields cause the most rejections:

**`code_reference` must be version-pinned:**
```python
# WRONG — floating reference
"code_reference": "git+https://github.com/org/repo@main"

# CORRECT — exact SHA or pinned package version
"code_reference": "optuna==3.6.1"
"code_reference": "git+https://github.com/org/repo@abc1234f"
```

**`configuration_justification` must explain the why:**
```python
# WRONG — content-free
"configuration_justification": "default settings"

# CORRECT — explains the reasoning (MANIFESTO Principle 10)
"configuration_justification": (
    "n_startup_trials=10 chosen for 100–500 evaluation budgets on 5–20 dimensional "
    "problems. Lower values reduce exploration in early phases; higher values delay "
    "model-guided search unnecessarily."
)
```

No other fields require explanation — the others (name, version, framework, language)
are factual and straightforward.

---

### Step 4: Register and smoke-test

```python
from corvus_corone.registry import AlgorithmRegistry, ProblemRegistry
from corvus_corone.runner import Runner
from my_tpe_adapter import OptunaTPEAdapter

# 1. Register
registry = AlgorithmRegistry(repository_factory)
adapter = OptunaTPEAdapter(algorithm_id="tpe-tutorial-v1")
algorithm_id = registry.register(adapter)
print(f"Registered: {algorithm_id}")

# 2. Smoke test against a known simple problem
runner = Runner(repository_factory)
run = runner.run_single(
    problem_id="sphere-5d-v1.0.0",
    algorithm_id=algorithm_id,
    seed=42,
    budget=50,
)

assert run.status == "completed", f"Run failed: {run.failure_reason}"
print(f"Best value at budget=50: {run.records[-1].best_so_far}")
```

If `registry.register()` raises a `ValidationError`, the message identifies the exact
field that failed. The three most common errors are described in Step 3 above.

If the smoke test `run.status` is not `"completed"`, inspect `run.failure_reason` —
it will name which contract was violated (bounds exceeded, missing method, etc.).

> **Checkpoint:** Both `print` statements execute without exception. The best value is a
> float, not `NaN` or `inf`. The same call with `seed=42` always produces the same value
> (seed isolation confirmed).

---

## Expected Outcome

- `registry.register(adapter)` returns an `algorithm_id` string
- `runner.run_single(..., seed=42, ...)` produces `run.status == "completed"`
- Re-running with the same seed produces the identical `best_so_far` value

The adapter is now registered and usable in any Study that includes a `ContinuousVariable`
search space.

---

## What You Learned

- **Ask-tell loop:** `initialize → suggest → observe` is the complete behavioral
  interface. The Runner controls the loop; the adapter only responds.
  → [§2 Algorithm Interface](../03-technical-contracts/02-interface-contracts/03-algorithm-interface.md)

- **Seed isolation:** All randomness must flow from the `seed` injected by `initialize()`.
  The same seed must reproduce the same Run identically.
  → [§6 Cross-Cutting Contracts](../03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md)

- **State reset in `initialize()`:** Creating `self._study` inside `initialize()` (not
  `__init__`) ensures each Run starts from a clean optimizer state.
  → MANIFESTO Principle 18

- **15-line constraint:** The behavioral adapter is ≤15 lines because the interface is
  minimal by design. If your adapter requires significantly more, check whether
  state that belongs in `initialize()` has leaked into `__init__`.

- **`configuration_justification` is mandatory:** "Default settings" is not a
  justification. The field must explain why this configuration is the right choice for
  the intended problem class and budget range.
  → MANIFESTO Principle 10

---

## Further Reading

| What to do next | Where to go |
|---|---|
| Submit this adapter as a community contribution | [contribution-guide.md §3](../05-community/01-contribution-guide.md#3-adding-an-algorithm-implementation) |
| Full contribution walkthrough with checklist | [uc-02-contribute-algorithm.md](uc-02-contribute-algorithm.md) |
| Add a sensitivity report (required for contribution) | [algorithm-instance.md §2.2.1](../03-technical-contracts/01-data-format/03-algorithm-instance.md#221-sensitivityreport-sub-schema) |
| Use your algorithm in a Study | [02-researcher-design-and-execute-study.md](02-researcher-design-and-execute-study.md) |
| Wrap a Nevergrad optimizer instead | [03-nevergrad-adapter.md](03-nevergrad-adapter.md) |
| Full Algorithm Interface specification | [§2 Algorithm Interface](../03-technical-contracts/02-interface-contracts/03-algorithm-interface.md) |
