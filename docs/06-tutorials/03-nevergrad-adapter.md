# Tutorial: Wrap a Nevergrad Optimizer (NevergradAdapter)

**Actor:** Algorithm Author
**Goal:** Register any Nevergrad optimizer as a Corvus Corone Algorithm Instance in ≤15 lines

**Connects to:**
- Interface contract: [§2 Algorithm Interface](../03-technical-contracts/02-interface-contracts/03-algorithm-interface.md)
- Algorithm contribution tutorial: [uc-02-contribute-algorithm.md](uc-02-contribute-algorithm.md)
- Data schema: [§2.2 Algorithm Instance](../03-technical-contracts/01-data-format/03-algorithm-instance.md)
- Interop mapping: [§4.3 Nevergrad](../03-technical-contracts/01-data-format/11-interoperability-mappings.md#43-nevergrad)

---

## Prerequisites

```bash
pip install nevergrad
```

Nevergrad is an **optional** dependency. The core library does not import it;
`NevergradAdapter` defers the import to `initialize()` so the adapter module can
be imported without nevergrad installed.

---

## Overview

`NevergradAdapter` is a generic wrapper that translates between the Corvus Corone
Algorithm Interface (ask-tell) and Nevergrad's optimizer API. Every Nevergrad
optimizer shares the same `ask()` / `tell()` interface, so one adapter class
covers all of them.

| Corvus method | Nevergrad call |
|---|---|
| `initialize(search_space, seed)` | build `ng.p.Dict`, seed parametrization, call `ng.optimizers.registry[name](parametrization, budget)` |
| `suggest(context, batch_size)` | `optimizer.ask()` × `batch_size` |
| `observe(solution, result)` | `optimizer.tell(candidate, loss)` |

Search space variables are translated as follows:

| Corvus variable type | Nevergrad class |
|---|---|
| `continuous` | `ng.p.Scalar(lower=lo, upper=hi)` |
| `integer` | `ng.p.Scalar(lower=lo, upper=hi).set_integer_casting()` |
| `categorical` | `ng.p.Choice(choices)` |

---

## Step 1: Instantiate the adapter

```python
from corvus_corone.algorithms.adapters.nevergrad_adapter import NevergradAdapter

adapter = NevergradAdapter(
    algorithm_id="ngopt-v1",
    optimizer_name="NGOpt",           # any key in ng.optimizers.registry
    budget=200,                        # must match Study's evaluation budget
    configuration_justification=(
        "NGOpt is the recommended default Nevergrad optimizer: it adapts its "
        "internal strategy (DE, CMA-ES, PSO, …) based on problem dimensionality "
        "and budget. Budget=200 matches the Study's allocation for 10-dimensional "
        "mixed search spaces."
    ),
)
```

`optimizer_name` accepts any key from `ng.optimizers.registry`. To list all
available optimizers:

```python
import nevergrad as ng
print(sorted(ng.optimizers.registry.keys()))
```

Common choices:

| Name | Recommended when |
|---|---|
| `"NGOpt"` | General-purpose default; adapts to budget and dimensionality |
| `"NgIohTuned"` | IOH-tuned variant; strong across diverse problem classes |
| `"TwoPointsDE"` | Large parallel worker counts (high `num_workers`) |
| `"CMA"` | Continuous, low-noise, medium-budget (50–1000 evaluations) |
| `"OnePlusOne"` | Discrete or mixed search spaces, small budget |

---

## Step 2: Run it inside a Study

```python
from corvus_corone.registry import AlgorithmRegistry, ProblemRegistry
from corvus_corone.runner import Runner

# 1. Register the algorithm
registry = AlgorithmRegistry(repository_factory)
algorithm_id = registry.register(adapter)

# 2. Run a single smoke test
runner = Runner(repository_factory)
run = runner.run_single(
    problem_id="mixed-5d-v1.0.0",
    algorithm_id=algorithm_id,
    seed=42,
    budget=200,
)
assert run.status == "completed"
print(f"Best value: {run.records[-1].objective_value}")

# 3. Use in a Study as normal
# (see docs/06-tutorials/02-researcher-design-and-execute-study.md)
```

---

## Step 3: Choosing a different optimizer — only one line changes

To swap `NGOpt` for `TwoPointsDE`:

```python
adapter = NevergradAdapter(
    algorithm_id="twopointsde-v1",
    optimizer_name="TwoPointsDE",     # ← only this changes
    budget=200,
    configuration_justification=(
        "TwoPointsDE selected for its robustness under high parallelism. "
        "Evaluated against the same 10-dimensional mixed search space as NGOpt "
        "to directly compare strategies."
    ),
)
```

---

## Step 4: Maximization problems

Nevergrad always minimizes. For problems where `objective.type == "maximize"`, pass
`objective="maximize"` — the adapter negates the loss before `tell()` automatically:

```python
adapter = NevergradAdapter(
    algorithm_id="ngopt-maximize-v1",
    optimizer_name="NGOpt",
    budget=200,
    objective="maximize",             # loss negated internally
    configuration_justification="...",
)
```

---

## What the adapter does NOT do

- **Log Nevergrad's internal state.** Nevergrad's `ParametersLogger` callback
  (which writes a JSON-lines file per `tell()`) is not wired by default. Attach it
  manually if you need Nevergrad-native logs in addition to Corvus `PerformanceRecord`s:

  ```python
  import nevergrad as ng

  # After initialize() is called, attach the logger to the internal optimizer
  logger = ng.callbacks.ParametersLogger("/tmp/ng_log.jsonl")
  adapter._optimizer.register_callback("tell", logger)
  ```

- **Use Nevergrad's `minimize()` convenience wrapper.** The adapter uses the explicit
  `ask()` / `tell()` loop so that the Corvus Runner retains control of the evaluation
  loop (required by the §2 interface contract).

- **Support `num_workers > 1`.** The sequential V1 Runner always calls `suggest()` with
  `batch_size=1`. To use parallel Nevergrad workers, override `suggest()` in a subclass
  and set `num_workers` in `hyperparameters`.

---

## Boilerplate count

The adapter itself is **14 lines of logic** (the five required methods, excluding
comments and blank lines), satisfying NFR-USABILITY-01.

To wrap a *new* optimizer without writing any adapter code at all, instantiate
`NevergradAdapter` directly with any `optimizer_name` from the registry. No subclassing
is required unless you need optimizer-specific behaviour beyond what the generic adapter
provides.
