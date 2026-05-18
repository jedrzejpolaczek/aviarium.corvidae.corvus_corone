# Seed Manager

> Container: [Experiment Runner](../../03-c4-leve2-containers/08-experiment-runner.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Generate a unique, deterministic seed for each Run, persist it to the Results Store, and inject it into every relevant random-number source in the Run subprocess before any algorithm code executes.

---

## Interface

Called by the Run Isolator at subprocess startup:

```python
class SeedManager:
    def generate_seed(self, run_id: str, base_seed: int) -> int:
        """Deterministic: hash(run_id + base_seed) → int in [0, 2^32)"""

    def inject_seeds(self, seed: int) -> None:
        """Sets random, numpy.random, torch (if available) to seed."""

    def persist_seed(self, run_id: str, seed: int, results_dir: Path) -> None:
        """Writes seed to {results_dir}/{run_id}/seed.json"""

    def load_seed(self, run_id: str, results_dir: Path) -> int:
        """Reads seed from {results_dir}/{run_id}/seed.json for resume."""
```

---

## Dependencies

- Python `random` stdlib
- `numpy.random`
- `torch` (optional — only if importable in the Run subprocess)
- `json` stdlib (for seed persistence)
- Results Store filesystem path (passed in; no direct dependency on Results Store component)

---

## Key Behaviors

1. **Deterministic seed generation** — given the same `run_id` and `base_seed`, always produces the same seed. Uses `hashlib.sha256(f"{base_seed}:{run_id}".encode()).digest()[:4]` converted to an unsigned int.

2. **Seed injection** — sets seeds on all known random sources before the algorithm's `__init__` is called. The injection order is fixed: `random.seed()` → `numpy.random.seed()` → `torch.manual_seed()` (if torch is importable).

3. **Seed persistence** — writes `{"run_id": ..., "seed": ..., "generated_at": "<ISO8601>"}` to `seed.json` before the evaluation loop starts. This enables run resume without re-generating.

4. **Resume-path load** — if `seed.json` already exists for a `run_id`, `load_seed()` returns the stored value rather than regenerating. This guarantees that a resumed Run uses the same seed as the original attempt.

5. **No global state** — the Seed Manager holds no state after `inject_seeds()` completes. All state is on the filesystem or in the Python interpreter's random modules.

---

## State

No in-memory state after initialization. Seed values are persisted at `{results_dir}/{experiment_id}/runs/{run_id}/seed.json`.

---

## Implementation Reference

`corvus_corone/experiment_runner/seed_manager.py`

---

## SRS Traceability

Reproducibility requirement — MANIFESTO Principle 18. Required for:
- FR-R-01 (reproducible runs): a run re-executed with the same seed must produce the same sequence of objective function evaluations.
- UC-02 (run study): each Run in a Study receives a unique, reproducible seed.
