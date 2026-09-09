# Seed Manager

> Container: [Experiment Runner](../../08-experiment-runner.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Derive a deterministic seed for each Run from the Study's `root_seed`, hand it to the Run record for persistence, and inject it into every relevant random-number source in the Run subprocess before any algorithm code executes.

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
- **Results Store — RunRepository** — `Run.seed` is persisted and read back as a field of the Run record. This component holds no filesystem path (ADR-001, ADR-017).

---

## Key Behaviors

1. **Deterministic seed derivation** — `SeedSequence(Study.root_seed)` is spawned once per Run, in the run-plan order problem → algorithm → repetition, and the first 32-bit word of the child sequence is that Run's seed (ADR-017). The same Study produces the same assignment because the spawn order is a property of the plan, not of execution timing.

2. **Seed injection** — sets seeds on all known random sources before the algorithm's `__init__` is called. The injection order is fixed: `random.seed()` → `numpy.random.seed()` → `torch.manual_seed()` (if torch is importable).

3. **Collision detection** — before a Run executes, its seed is checked against the seeds already assigned within the Experiment for the same problem and algorithm pair. A repeat raises `SeedCollisionError`. The check is explicit and is not skipped on the grounds that the derivation should not collide (ADR-017).

4. **Resume path** — a resumed Run reads `Run.seed` through `RunRepository.get_run()` rather than re-deriving it. Re-deriving would depend on the spawn order being reconstructed identically, which a partial resume cannot guarantee (ADR-017, Risks).

5. **No global state** — the Seed Manager holds no state after `inject_seeds()` completes. All state is on the filesystem or in the Python interpreter's random modules.

---

## State

The set of seeds already assigned within the current Experiment, held for the collision check and discarded when the Experiment ends. Seed values themselves live on the Run record.

---

## Implementation Reference

`corvus_corone/experiment_runner/seed_manager.py`

---

## SRS Traceability

Reproducibility requirement — MANIFESTO Principle 18. Required for:
- FR-09 (system-assigned seeds): every Run seed is derived from the Study's declared `seed_strategy`; the Researcher does not choose individual seed values.
- UC-02 (run study): each Run in a Study receives a unique, reproducible seed.
