# §6 Schema Versioning

> Index: [01-index.md](01-index.md)

This section defines how the data format schema is versioned, what changes require a version bump,
how the version identifier is stored, and how artifacts produced under older schemas are handled.
The full governance policy (notice periods, deprecation authority, long-term storage) is in
[`docs/05-community/02-versioning-governance.md`](../../05-community/02-versioning-governance.md).

---

## 6.1 Version Identifier Format

Schema versions follow **semantic versioning** `MAJOR.MINOR.PATCH`:

| Component | When to increment | Examples |
|---|---|---|
| `MAJOR` | A **breaking change** — any stored artifact from the previous version will fail validation under the new schema | `1.0.0` → `2.0.0` |
| `MINOR` | A **non-breaking addition** — new optional fields or new entity types; old artifacts remain valid | `1.0.0` → `1.1.0` |
| `PATCH` | A **correction** — typo fixes, clarifying text, no structural change | `1.0.0` → `1.0.1` |

The current schema version is declared in the callout block at the top of
[`01-index.md`](01-index.md) (immediately before §1 Entity Overview).

---

## 6.2 Breaking vs. Non-Breaking Changes

### Breaking changes (increment MAJOR)

The following mutations to any entity schema are **always breaking**:

- Removing a field that was previously required
- Renaming a field (equivalent to remove + add)
- Changing the type of an existing field (e.g., `string` → `list[string]`)
- Changing a validation constraint in a way that rejects previously valid values
  (e.g., tightening the `version` regex, making an optional field required)

A breaking change requires:
1. A MAJOR version bump
2. An Architecture Decision Record documenting the reason
3. A migration guide for existing artifacts (see §6.4)
4. A deprecation notice for the previous MAJOR version
   (see [`02-versioning-governance.md`](../../05-community/02-versioning-governance.md) §3)

### Non-breaking changes (increment MINOR)

- Adding a new **optional** field to an existing entity
- Adding a new entity type
- Relaxing a validation constraint so that previously invalid values become valid

Old artifacts remain fully valid under the new MINOR version; no migration is needed.

### Corrections (increment PATCH)

- Fixing typos or formatting in field descriptions
- Clarifying a definition without changing its meaning
- No structural or validation changes

---

## 6.3 The `schema_version` Field

Every stored artifact **must** include a `schema_version` field recording the schema version
under which it was created. This field is part of the provenance record for every entity
(→ `docs/05-community/02-versioning-governance.md` §2):

```
Problem Instance record:    schema_version
Algorithm Instance record:  schema_version
Study record:               schema_version
Experiment record:          schema_version  (+ runner_version, platform details)
Run record:                 inherited from Experiment
ResultAggregate:            schema_version
Report:                     schema_version
```

The full reproducibility provenance tuple stored in an Experiment record is:

```
(problem_version, algorithm_version, schema_version, runner_version)
```

This tuple is the artifact the reproducibility guarantee rests on
(MANIFESTO Principles 19–21). Given an Experiment ID, the system must be able to
enumerate all artifact versions involved and confirm they are still available.

---

## 6.4 Handling Artifacts Created Under Older Schemas

When the system reads an artifact whose `schema_version` differs from the current schema version:

| Situation | Handling |
|---|---|
| `PATCH` difference only | Accept without modification. |
| `MINOR` difference (artifact is older) | Accept; new optional fields are absent — treat as `null` or default. |
| `MINOR` difference (artifact is newer) | Reject with a clear error: `SchemaVersionError: artifact schema X.Y.Z is newer than supported X.Y'.Z'` |
| `MAJOR` difference | Reject with a clear error: `SchemaVersionError: artifact schema MAJOR.y.z is incompatible with current MAJOR'.y'.z'`. A migration script must be applied first. |

**Migration scripts**, when required, are stored under `tools/migrations/` and named
`migrate_vX_to_vY.py`. Each script converts a stored artifact from MAJOR version X to
MAJOR version Y and updates the `schema_version` field. Running a migration is an
explicit, operator-initiated action — the system never silently mutates stored data.

---

## 6.5 Where Schemas Are Stored and Versioned

- **Canonical definition:** this document tree (`docs/03-technical-contracts/01-data-format/`)
- **Machine-readable schemas:** `schemas/` directory at the repository root, named
  `entity-name.v{MAJOR}.{MINOR}.schema.json` (e.g., `problem-instance.v1.0.schema.json`)
- **Versioned alongside code:** schema files are committed to the same repository as the
  library code. A schema MAJOR version bump is always accompanied by a library MAJOR version bump.
- **No separate schema registry** is used in V1. The repository is the registry.

> **Decision:** The narrative tables in this document tree are the canonical schema definition for V1.
> Machine-readable JSON Schema files under `schemas/` are a post-V1 enhancement — they would
> enable tooling (IDE validation, automated round-trip tests) but are not required for V1
> correctness. No separate schema registry is introduced in V1.
