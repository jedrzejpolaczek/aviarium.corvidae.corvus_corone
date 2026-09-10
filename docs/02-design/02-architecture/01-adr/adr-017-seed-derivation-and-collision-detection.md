# ADR-017: Seed Derivation and Collision Detection

<!--
STORY ROLE: Selects one seed derivation mechanism from the four the corpus proposes, and
supplies the collision detection that the Runner contract requires but no component provides.
Run independence and reproducibility both rest on this decision.

CONNECTS TO:
  → docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md : requires SeedCollisionError
  → docs/03-technical-contracts/01-data-format/06-run.md : Run.seed and its uniqueness rule
  → docs/01-manifesto/MANIFESTO.md Principle 18 : independence of runs
  → adr-001-library-with-server-ready-data-layer.md : forbids traversing the store's directory tree
-->

---

**Status:** Accepted; the component document this ADR instructs is absorbed into
[`03-experiment-runner/01-index.md`](../03-c4-leve2-containers/04-c4-leve3-components/03-experiment-runner/01-index.md)

> **Target absorbed.** This ADR requires `03-experiment-runner/02-seed-manager.md` to be
> corrected to the `SeedSequence` mechanism or removed under ADR-012. It was corrected first,
> and [ADR-028](adr-028-consolidate-the-c3-layer-and-remove-c4.md) then consolidated the C3 layer, so the Seed Manager is described in its
> group index. The decision is unchanged; only the document it points at has moved.

**Date:** 2026-09-08

**Deciders:** Core maintainers, technical lead

---

## Context

Four seed mechanisms are specified across the corpus:

| Source | Mechanism |
|---|---|
| `04-c4-leve3-components/03-experiment-runner/02-seed-manager.md` | `hashlib.sha256(f"{base_seed}:{run_id}").digest()[:4]` |
| ROADMAP IMPL-008 and IMPL-016 | `numpy.random.SeedSequence.spawn()` |
| `04-c4-leve3-components/06-study-orchestrator/01-index.md` | `random.randint(0, 2^31)` |
| `04-c4-leve3-components/10-public-api-cli/01-index.md` | `secrets.randbelow(2**31)` |

`04-runner-interface.md` requires that seeds be unique within an Experiment for a given
`(problem_id, algorithm_id)` pair and that `SeedCollisionError` be raised otherwise.
`01-data-format/06-run.md` repeats the uniqueness rule. No component specifies how a collision
is detected. The Seed Manager document opens by calling its output "unique" while describing a
32-bit truncated hash, which cannot guarantee it.

The Seed Manager additionally persists `seed.json` under the Results Store directory tree while
declaring "no direct dependency on Results Store component", which is the traversal ADR-001
forbids. Within that same document the persistence path is given twice, differently.

---

## Decision

**Seeds are derived with `numpy.random.SeedSequence`.**

A Study records one `root_seed`, an integer chosen at lock time and stored in the Study record.
The Runner constructs `SeedSequence(root_seed)` and spawns one child per Run, in a deterministic
order defined by the run plan: problem index, then algorithm index, then repetition index. Each
Run's seed is the first 32-bit word of its child sequence and is written to `Run.seed`.

**Collision detection is explicit.** The Runner keeps the set of seeds already assigned within
the Experiment and raises `SeedCollisionError` before executing a Run whose seed is already
present for the same `(problem_instance_id, algorithm_instance_id)` pair. The check does not
depend on the derivation method being collision-free.

**Seeds are persisted through the repository, not the filesystem.** `Run.seed` is a field of the
Run record. No component writes `seed.json`, and no component constructs a path into the Results
Store directory tree. Resuming a Run reads `Run.seed` through `RunRepository.get_run()`.

`03-experiment-runner/02-seed-manager.md` is corrected to this mechanism or removed under
ADR-012. The two orchestrator and facade documents drop their competing seed expressions.

---

## Rationale

`SeedSequence` is the standard tool for this problem. It produces streams that are independent
by construction, which is what MANIFESTO Principle 18 requires and what a truncated hash does not
provide. It is reproducible from a single recorded integer, so UC-05 needs to archive one number
rather than a table of per-Run seeds.

`random.randint` and `secrets.randbelow` fail the reproducibility requirement outright: neither
can be replayed from a stored root, so a study using them cannot be reproduced from its Study
record.

The truncated SHA-256 is reproducible but gives no independence guarantee between streams and no
collision guarantee. With 32 bits, a study of a few thousand Runs has a non-negligible collision
probability, and the contract makes collisions a hard error rather than a warning.

Explicit collision detection is kept even with `SeedSequence` because the contract promises the
error, and because the promise should not silently depend on a property of the derivation
function that a future change might remove.

Persisting through the repository removes the ADR-001 violation and the internal path
contradiction at the same time, and it means the seed travels with the Run into the V2 server
without a separate file.

**Trade-off accepted:** the Runner must hold the assigned-seed set for the duration of an
Experiment. For the study sizes V1 targets this is a set of a few thousand integers.

---

## Alternatives Considered

### Truncated SHA-256 of `base_seed` and `run_id`

**Description:** Derive each seed by hashing the Run identifier with a study-level base seed.

**Why rejected:** No independence guarantee between derived streams, no collision guarantee at
32 bits, and it makes the seed depend on the Run identifier, so replaying a study requires
archiving every Run identifier rather than one root seed.

**Under what conditions reconsidered:** If Runs ever need seeds derivable without a central
counter, for example under distributed execution in V2, a hash over `(root_seed, problem,
algorithm, repetition)` widened to 64 bits becomes attractive. That is a V2 decision.

---

## Consequences

**Positive:**

- One mechanism, reproducible from one archived integer.
- `SeedCollisionError` becomes reachable and testable rather than promised and unimplemented.
- The ADR-001 traversal violation and the contradictory `seed.json` paths both disappear.

**Negative / Trade-offs:**

- `Study` gains a `root_seed` field, so `01-data-format/04-study.md` changes.
- `numpy` becomes load-bearing for the Runner rather than only for analysis.

**Risks:**

- **Risk:** A resumed Experiment re-spawns the sequence in a different order and assigns
  different seeds.
  **Mitigation:** Spawn order is defined by the run plan, which is derived deterministically
  from the locked Study; and `Run.seed` is authoritative on resume, not recomputation.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/02-interface-contracts/04-runner-interface.md` | Requires the collision error this ADR implements |
| `docs/03-technical-contracts/01-data-format/04-study.md` | Gains `root_seed` |
| `docs/03-technical-contracts/01-data-format/06-run.md` | `Run.seed` is the persisted value |
| `.../04-c4-leve3-components/03-experiment-runner/02-seed-manager.md` | Corrected or removed under ADR-012 |
| `adr-001-library-with-server-ready-data-layer.md` | The traversal rule this ADR stops violating |
