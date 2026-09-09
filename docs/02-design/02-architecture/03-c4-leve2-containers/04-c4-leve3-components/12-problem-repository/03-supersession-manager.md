# Supersession Manager

> Container: [Problem Repository](../../11-problem-repository.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Record the lineage between a Problem Instance and the registration that replaces it, so that a
correction never alters what an archived Study resolves to.

---

## Interface

> **Descriptive document (ADR-012).** The authoritative definition is the contract cited
> below. This page explains only how that contract is grouped into a component and why the
> boundary falls where it does. It does not define signatures.

The surface is `register_problem()`, `deprecate_problem()`, `get_problem()` and
`list_problems()` on the `ProblemRepository` contract in
[`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md).
This component adds no methods of its own.

The behaviour is the mirror of
[Algorithm Registry — Supersession Manager](../11-algorithm-registry/03-supersession-manager.md)
and is governed by the same
[ADR-020](../../../01-adr/adr-020-entity-versioning-immutable-entities.md): a revision is a new
entity with a new UUID, and the old entity carries `deprecated`, `deprecation_reason` and
`superseded_by`.

---

## Dependencies

- **Entity Store** — all reads and writes are delegated there

---

## Key Behaviors

The five behaviours of the Algorithm Registry's Supersession Manager apply unchanged to Problem
Instances. One obligation is specific to this repository:

**A Study's problem set must stay byte-identical for the Study's lifetime (FR-04).** Deprecating
a Problem Instance therefore does not, and cannot, affect any locked Study that references it.
Deprecation changes what `list_problems()` offers to a Researcher composing a *new* Study; it
changes nothing that a locked Study resolves.

---

## State

Stateless. All lineage is stored on the entities themselves.

---

## Implementation Reference

`corvus_corone/problem_repository/supersession_manager.py`

---

## SRS Traceability

- FR-03 (revision produces a new record): modifying a Problem Instance produces a new entity
  rather than overwriting the existing one.
- FR-04 (referenced entities stay byte-identical): supersession is what makes that guarantee
  hold without freezing the repository.
