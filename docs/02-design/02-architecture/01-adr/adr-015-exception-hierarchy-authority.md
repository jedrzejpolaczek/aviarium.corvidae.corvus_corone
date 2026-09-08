# ADR-015: Exception Hierarchy Authority

<!--
STORY ROLE: Resolves which of two incompatible exception hierarchies is the real one, and
adopts into it the classes that other contracts invented without a parent.

CONNECTS TO:
  → docs/03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md : the taxonomy
  → docs/03-technical-contracts/04-public-api-contract.md : the competing hierarchy, corrected
  → docs/02-design/02-architecture/03-c4-leve2-containers/02-cli-spec.md : exit codes keyed by class
-->

---

**Status:** Accepted

**Date:** 2026-09-08

**Deciders:** Core maintainers, technical lead

---

## Context

Two exception hierarchies are specified for the same system.

`02-interface-contracts/07-cross-cutting-contracts.md` defines a tree rooted at `CorvusError`
with eighteen classes grouped by failure kind: `ValidationError`, `BudgetError`,
`ReproducibilityError`, `StorageError`, `IntegrationError` and `AnalysisError`. Every exception
carries `error_code`, `message` and `context`. The implementation in
`packages/corvus-corone-lib/src/corvus_corone/exceptions.py` reproduces this tree name for name.

`04-public-api-contract.md` defines a different tree rooted at `CorvusCoroneError` with eight
classes. Five do not exist in the taxonomy. `NotFoundError` overlaps `EntityNotFoundError`. A
single `StudyLockedError` conflates `StudyNotLockedError` and `StudyAlreadyLockedError`, which
signal opposite conditions and, after ADR-013, are both reachable.

Six further classes are raised by contracts but defined in neither tree: `SchemaVersionError`,
`MetricUndefinedError`, `RunNotCompleteError`, `UnsupportedFormatError`, `ExportValidationError`
and `InterfaceViolationError`, the last introduced by the algorithm author tutorial.

---

## Decision

**`07-cross-cutting-contracts.md` holds the single exception taxonomy. Its root is
`CorvusError`.**

The six homeless classes are adopted into it:

| Class | Parent | Raised when |
|---|---|---|
| `SchemaVersionError` | `StorageError` | Artifact schema version is newer or a different major version than supported |
| `MetricUndefinedError` | `AnalysisError` | A metric is undefined for the given data, for example ECDF_AREA on a cell with fewer than two Runs |
| `RunNotCompleteError` | `AnalysisError` | The Analyzer is given a Run whose status is not `"completed"` |
| `UnsupportedFormatError` | `IntegrationError` | Export requested in a format the Ecosystem Bridge does not produce |
| `ExportValidationError` | `IntegrationError` | Source data is incomplete for the requested export |
| `InterfaceViolationError` | `ValidationError` | A registered Algorithm or Problem does not satisfy its interface |

`04-public-api-contract.md` adopts these names. `CorvusCoroneError`, `NotFoundError` and the
public-API-only `StudyLockedError` are removed from it.

**The re-export decision from DQ-5 is kept.** Exceptions remain defined in
`corvus_corone.exceptions` and are re-exported from `corvus_corone.__init__`, so both
`cc.EntityNotFoundError` and `from corvus_corone.exceptions import EntityNotFoundError` work.
Naming is unified; ergonomics are not sacrificed.

---

## Rationale

The taxonomy is the more complete of the two, it is organised by failure kind rather than by
whichever surface happens to raise the error, and it is already implemented together with its
tests. Choosing it turns the correction into a rename inside one document instead of a rewrite
of a module.

The names it displaces are also the weaker ones. `EntityNotFoundError` states what was not
found. `StudyNotLockedError` and `StudyAlreadyLockedError` distinguish two failures that a
single `StudyLockedError` cannot.

The public API contract's real contribution was DQ-5: a researcher writing
`import corvus_corone as cc` should not need a second import to catch an exception. That
observation is correct and survives unchanged.

**Trade-off accepted:** the public exception surface is larger than eight classes. That is the
cost of naming failures precisely, and the grouping means a caller can catch `StorageError`
without enumerating its children.

---

## Alternatives Considered

### Keep both, with the public set as a facade over the taxonomy

**Description:** Public functions raise the eight simplified classes; internal layers raise the
taxonomy.

**Why rejected:** Requires a translation at every public entry point, and the translation
destroys information exactly where the caller needs it, collapsing "not locked" and "already
locked" into one class. It also doubles the number of names a contributor must learn.

---

## Consequences

**Positive:**

- One name per failure across contracts, architecture, tutorials and code.
- The vocabulary check in `scripts/check_docs.py` gains a closed set to validate against.
- Six classes previously raised by contracts but defined nowhere acquire a parent and a
  documented trigger.

**Negative / Trade-offs:**

- `04-public-api-contract.md` needs edits to its exception tree and its message format table.
- The CLI exit code table in `02-cli-spec.md` is keyed by exception class and must be remapped.

**Risks:**

- **Risk:** The exit code table and the taxonomy drift apart again.
  **Mitigation:** Both are normative under ADR-012, and the exit code table cites class names
  that the vocabulary check validates against the taxonomy.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md` | The authoritative taxonomy; extended by this ADR |
| `docs/03-technical-contracts/04-public-api-contract.md` | Corrected by this ADR |
| `docs/02-design/02-architecture/03-c4-leve2-containers/02-cli-spec.md` | Exit code table keyed by exception class |
| `adr-013-study-lifecycle-draft-then-locked.md` | Makes both study-lock exceptions reachable |
