# ADR-014: Entity Identifier Type — UUID String

<!--
STORY ROLE: Resolves the conflict between the integer identifiers in the entity field tables
and the UUID strings required everywhere else. The identifier type is the foundation of the
V1 to V2 migration story in ADR-001, so it cannot be left ambiguous.

CONNECTS TO:
  → docs/03-technical-contracts/01-data-format/ : all entity schemas
  → adr-001-library-with-server-ready-data-layer.md : the migration guarantee that depends on this
  → docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, technical lead

---

## Context

`01-data-format/01-index.md` states a MUST constraint: "Globally unique ID (UUID format).
Entity references use IDs, not local file paths. The same ID is valid in local file storage
(V1) and in a server database (V2) without migration."

The entity field tables in the same directory contradict it. `02-problem-instance.md`,
`04-study.md`, `05-experiment.md`, `06-run.md`, `07-performance-record.md`,
`08-result-aggregate.md` and `09-report.md` all type `id` and every foreign key field as `int`.

Every other layer uses `str`. The repository interface signatures take `id: str`. The public
API view objects declare `id: str` and describe UUID format. Both repository implementations
generate `uuid.uuid4()` strings. The file format specification names files `<uuid>.json`.

ADR-001 rests the entire V1 to V2 migration guarantee on identifiers being valid in both a
local file store and a server database without a migration step.

---

## Decision

**Every entity identifier and every foreign key referencing one is a UUID version 4, serialised
as a string.**

This applies to `id`, `study_id`, `experiment_id`, `run_id`, `problem_instance_id`,
`algorithm_instance_id` and every element of `problem_instance_ids`, `algorithm_instance_ids`
and `run_ids`.

The seven entity field tables in `01-data-format/` are corrected from `int` to `string`. No
other document changes, because no other document said `int`.

---

## Rationale

An autoincrementing integer is unique within one store. ADR-001 requires uniqueness across a
local store and a future shared server holding studies from many researchers, which an integer
counter cannot provide without a renumbering step. Renumbering breaks every archived Run that
references the old identifier, which breaks UC-05, the reproduction of a published study.

The correction is also the smallest available. Seven field tables move to the value that the
constraint statement, the repository contract, the public API contract, the file format
specification and both implementations already use.

**Trade-off accepted:** UUID strings are larger than integers in storage and in every
PerformanceRecord row. ADR-010 already addresses that cost by dictionary-encoding repeated
identifier columns in the Parquet secondary format.

---

## Alternatives Considered

### Integer identifiers with a namespace prefix applied on publication

**Description:** Keep integers locally and rewrite them into a globally unique form when a study
is published to the V2 server.

**Why rejected:** That rewrite is exactly the migration step ADR-001 exists to eliminate. It
also means an archived local artifact and its published counterpart carry different identifiers,
so a reproduction attempt cannot tell whether it is looking at the same entity.

---

### Content-addressed identifiers derived from entity content

**Description:** Derive the identifier from a hash of the entity.

**Why rejected:** Makes identity depend on every field, so a corrected typo in
`configuration_justification` produces a different identifier and orphans every Run that
referenced the entity. Entity identity must survive metadata correction.

**Under what conditions reconsidered:** If content addressing becomes desirable for artifact
archival, it can be added as a separate digest field without changing the identifier.

---

## Consequences

**Positive:**

- The MUST constraint in `01-index.md` becomes true rather than aspirational.
- The ADR-001 migration guarantee becomes verifiable.
- Contract and implementation agree on the primary key type.

**Negative / Trade-offs:**

- Seven files change.
- Identifiers are not human-readable. Documents and CLI output must therefore show `name`
  alongside `id` wherever a person reads them, which `02-cli-spec.md` already does.

**Risks:**

- **Risk:** Example payloads elsewhere in the corpus still show integer identifiers and are
  copied by a reader.
  **Mitigation:** The identifier check in `scripts/check_docs.py` cannot catch this. A one-time
  sweep of the JSON examples in `01-data-format/` is required when applying this ADR.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/01-data-format/01-index.md` | States the constraint this ADR makes true |
| `docs/03-technical-contracts/01-data-format/02-problem-instance.md` .. `09-report.md` | Field tables corrected by this ADR |
| `adr-001-library-with-server-ready-data-layer.md` | The migration guarantee that requires globally unique identifiers |
| `adr-020-entity-versioning-immutable-entities.md` | Depends on identifiers being stable and globally unique |
