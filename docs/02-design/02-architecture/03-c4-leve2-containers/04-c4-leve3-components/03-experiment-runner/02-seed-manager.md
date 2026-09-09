# Seed Manager

> Container: [Experiment Runner](../../08-experiment-runner.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Generate a unique, deterministic seed for each Run, persist it to the Results Store, and inject it into every relevant random-number source in the Run subprocess before any algorithm code executes.

---

## Interface

> **Descriptive document (ADR-012).** The authoritative definition is the contract cited
> below. This page explains only how that contract is grouped into a component and why the
> boundary falls where it does. It does not define signatures.

Seed derivation is defined by
[ADR-017](../../../01-adr/adr-017-seed-derivation-and-collision-detection.md): the Study
records one `root_seed`, and the Runner spawns one child `numpy.random.SeedSequence` per Run
in run-plan order, taking the first 32-bit word as that Run's seed.

Two obligations follow, both stated in
[`04-runner-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/04-runner-interface.md):

1. **Collision detection is explicit.** The Runner holds the set of seeds already assigned in
   the Experiment and raises `SeedCollisionError` before executing a Run whose seed is already
   present for the same problem and algorithm pair. The check does not rely on the derivation
   being collision-free.
2. **Seeds are persisted through the repository.** `Run.seed` is a field of the Run record.
   This component writes no file and constructs no path into the Results Store, which ADR-001
   forbids. Resuming a Run reads `Run.seed` through `RunRepository.get_run()`.

Seed injection into the Run process sets the seeded generators required by
`07-cross-cutting-contracts.md` 6: unseeded global random calls are forbidden.

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
- FR-09 (reproducible runs): a run re-executed with the same seed must produce the same sequence of objective function evaluations.
- UC-02 (run study): each Run in a Study receives a unique, reproducible seed.
