# ADR-020: Entity Versioning — Immutable Entities With Supersession

<!--
STORY ROLE: Resolves the incompatibility between the versioned retrieval promised by the
repository contract and the one-file-per-identifier storage model mandated by the same contract
set. Reproducibility depends on which way this is settled.

CONNECTS TO:
  → docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md : get_*(id, version)
  → docs/03-technical-contracts/01-data-format/10-file-formats.md §3.2 : one file per identifier
  → docs/03-technical-contracts/01-data-format/13-schema-versioning.md : schema versions, unaffected
  → adr-014-entity-identifier-type.md : identifiers must be stable and globally unique
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, technical lead

---

## Context

`02-interface-contracts/06-repository-interface.md` promises version-addressed retrieval:
`get_problem(id, version=None)` returns the latest non-deprecated entity, and
`get_problem(id, version="X.Y.Z")` returns exactly that version or raises `VersionNotFoundError`.
The same semantics are specified for algorithms and studies. C2 Flow 6, the reproduction of a
published study, calls `get_algorithm(id, version="<pinned>")` and
`get_problem(id, version="<pinned>")` in steps 7 and 8.

`01-data-format/10-file-formats.md` §3.2 mandates the storage layout: one file per identifier,
`problems/<uuid>.json`. That layout cannot hold two versions of one identifier.

The implementation resolved the contradiction by ignoring the parameter. Both repository
backends accept `version` and never read it. `VersionNotFoundError` is defined in
`exceptions.py` and raised nowhere. No test passes the argument. A caller requesting a pinned
version silently receives whatever is stored, which is the failure mode most damaging to the
system's purpose: a reproduction attempt that appears to succeed while using different inputs.

This is a finding produced by the implementation acting as a test of the contract. The contract,
not the code, is what needs to change.

---

## Decision

**Entities are immutable. Versioning is expressed by supersession, not by version-addressed
retrieval.**

A Problem Instance, Algorithm Instance or Study is never modified after registration. A revision
is registered as a **new entity with a new UUID**. The relationship is recorded on the old
entity, using the fields the contract already defines: `deprecated`, `deprecation_reason` and
`superseded_by`, the last holding the UUID of the replacement.

The `version` parameter is removed from `get_problem()`, `get_algorithm()` and `get_study()`.
`VersionNotFoundError` is removed from the taxonomy. The `version` field remains on entities as
human-readable metadata for display and citation, and is no longer an addressing key.

Reproduction works by identifier alone: a Run references the exact UUID of the entities it used,
that UUID never changes meaning, and `get_problem(id)` returns the same bytes forever. C2 Flow 6
drops the `version=` arguments.

**Schema versioning is unaffected.** `13-schema-versioning.md` governs the format of records, not
the identity of entities, and continues unchanged.

---

## Rationale

Immutable entities give a stronger reproducibility guarantee than versioned retrieval, not a
weaker one. Under versioned retrieval, `problem-A version 1.2.0` is a mutable coordinate: a
correction to that version changes what an archived Run resolves to, and nothing in the Run
record detects it. Under supersession, the Run points at a UUID whose content is fixed by
construction, which is exactly what MANIFESTO Principles 19 and 21 require.

The model is also half built. `deprecate_problem(id, reason, superseded_by)` and
`deprecate_algorithm(...)` already exist in the contract and in both implementations, and
`list_*` already excludes deprecated entities while `get_*` still retrieves them by identifier.
That is precisely the behaviour supersession needs. What has to be removed is the parallel
mechanism that was never built.

Removing the parameter also removes the contradiction with the storage layout, so
`10-file-formats.md` needs no change.

**Trade-off accepted:** a lineage of ten revisions is ten entities rather than one entity with
ten versions, and a user asking "what is the current version of this problem" follows
`superseded_by` links rather than reading a version string. `list_*` returning only
non-deprecated entities makes the common case a single call.

---

## Alternatives Considered

### Keep versioned retrieval and change the storage layout

**Description:** Store `problems/<uuid>/<version>.json` with a pointer to the latest, as the C3
registry documents already sketch, and implement `get_*(id, version)` properly.

**Why rejected:** Preserves the mutable-coordinate problem described above, and adds a second
identity concept alongside the UUID, so every reference in every entity must carry two fields to
be unambiguous. It also invalidates the file format specification and both implementations,
where the immutable model invalidates neither.

**Under what conditions reconsidered:** If entities acquire genuinely mutable metadata that must
not change identity, for example curator annotations added years after registration, a version
axis becomes useful again. Such metadata could instead live in a separate annotation entity.

---

### Leave the contract as written and implement versioned retrieval later

**Description:** Keep the promise and treat the gap as unfinished work.

**Why rejected:** The gap is not unfinished work, it is a contradiction between two clauses of
the same contract set. Leaving it means the corpus continues to specify something that cannot be
built as specified, and the silent wrong-version behaviour stays in the code meanwhile.

---

## Consequences

**Positive:**

- A Run's inputs are immutable by construction, so UC-05 reproduction is exact rather than
  best-effort.
- The contract stops contradicting the storage layout.
- The silent wrong-version failure is removed rather than documented.
- Three method signatures and one exception class leave the public surface.

**Negative / Trade-offs:**

- `06-repository-interface.md` changes three signatures; `07-cross-cutting-contracts.md` loses
  `VersionNotFoundError`; C2 Flow 6 drops two arguments.
- Registry lineage becomes a graph to traverse rather than a list to sort.
- Storage grows with revisions, since nothing is overwritten. For entity records, which are
  small JSON documents, this is not a practical constraint.

**Risks:**

- **Risk:** A contributor registers a corrected Problem Instance as a new entity and studies
  keep referencing the old one indefinitely.
  **Mitigation:** `list_problems()` excludes deprecated entities, so new studies see only the
  replacement; existing studies referencing the old entity is the intended behaviour.
- **Risk:** Users read the retained `version` metadata field as an addressing key.
  **Mitigation:** `01-data-format/` must state explicitly that `version` is descriptive, and the
  GLOSSARY entry for Schema Version must not be confused with it.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md` | Three signatures corrected by this ADR |
| `docs/03-technical-contracts/01-data-format/10-file-formats.md` | The layout this ADR stops contradicting |
| `docs/03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md` | Loses `VersionNotFoundError` |
| `docs/03-technical-contracts/01-data-format/13-schema-versioning.md` | Unaffected; governs record format, not entity identity |
| `adr-014-entity-identifier-type.md` | Supplies the stable globally unique identifier this model needs |
