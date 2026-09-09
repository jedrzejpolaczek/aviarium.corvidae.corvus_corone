# Supersession Manager

> Container: [Algorithm Registry](../../10-algorithm-registry.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Record the lineage between an Algorithm Instance and the registration that replaces it, so
that a revision never alters what an archived Study resolves to.

---

## Interface

> **Descriptive document (ADR-012).** The authoritative definition is the contract cited
> below. This page explains only how that contract is grouped into a component and why the
> boundary falls where it does. It does not define signatures.

The surface is `register_algorithm()`, `deprecate_algorithm()`, `get_algorithm()` and
`list_algorithms()` on the `AlgorithmRepository` contract in
[`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md).
This component adds no methods of its own; it is where the supersession half of those four is
implemented.

[ADR-020](../../../01-adr/adr-020-entity-versioning-immutable-entities.md) governs it.
Entities are immutable: a revision is a **new entity with a new UUID**, and the old entity
records the relationship through `deprecated`, `deprecation_reason` and `superseded_by`. There
is no `version` parameter on `get_algorithm()`, and `VersionNotFoundError` is not in the
taxonomy. The `version` field survives on the entity as human-readable metadata for display
and citation, and is not an addressing key.

---

## Dependencies

- **Entity Store** — all reads and writes are delegated there

---

## Key Behaviors

1. **Registration creates, never replaces** — `register_algorithm()` assigns a fresh UUID and
   writes a new record. There is no code path that modifies a stored Algorithm Instance, so no
   duplicate-key check is needed and none exists.

2. **Supersession is recorded on the old entity** — `deprecate_algorithm(id, reason,
   superseded_by)` sets `deprecated`, `deprecation_reason` and, when a replacement exists,
   `superseded_by` holding the replacement's UUID. The record is not deleted.

3. **Deprecated entities stay retrievable** — `get_algorithm(id)` returns a deprecated entity
   unchanged, because an archived Run references it by UUID and must keep resolving. Only
   `list_algorithms()` excludes them, being the discovery surface rather than the retrieval one.

4. **Lineage is a chain, not a tree** — following `superseded_by` from any entity reaches at
   most one successor. A registration that supersedes two entities is a design decision the
   contributor has to make explicitly by choosing which chain it continues; the manager does
   not merge chains.

5. **Cycles are rejected** — `superseded_by` must not close a loop back onto an entity already
   in the chain. A cycle would make "the current entity" undefined, and is refused with
   `ValidationError` naming the two identifiers involved.

---

## State

Stateless. All lineage is stored on the entities themselves.

---

## Implementation Reference

`corvus_corone/algorithm_registry/supersession_manager.py`

---

## SRS Traceability

- FR-05 (schema-conforming storage): a superseding registration is stored as a full Algorithm
  Instance record, not as a delta against its predecessor.
- MANIFESTO Principle 18 (reproducibility): an old Study is re-executable because the UUID it
  recorded never changes meaning.
