# Version Manager

> Container: [Algorithm Registry](../../03-c4-leve2-containers/10-algorithm-registry.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Manage version history for registered AlgorithmInstances, enforce immutability of registered versions, and support the deprecation lifecycle without deleting historical registrations.

---

## Interface

```python
class AlgorithmVersionManager:
    def register(self, instance: AlgorithmInstance, entity_store: AlgorithmEntityStore) -> None:
        """Registers a new version. Raises AlgorithmAlreadyExistsError if id+version exists."""

    def deprecate(self, algorithm_id: str, version: str, reason: str, entity_store: AlgorithmEntityStore) -> None:
        """Marks a version as deprecated. Does not delete it."""

    def get_current_version(self, algorithm_id: str, entity_store: AlgorithmEntityStore) -> AlgorithmInstance:
        """Returns the latest non-deprecated version."""

    def list_versions(self, algorithm_id: str, entity_store: AlgorithmEntityStore) -> list[AlgorithmInstance]:
        """Returns all versions (including deprecated) sorted by registration date."""
```

---

## Dependencies

- **Entity Store** — all reads and writes delegated here

---

## Key Behaviors

1. **Immutability enforcement** — if an AlgorithmInstance with the same `(id, version)` already exists in the Entity Store, raises `AlgorithmAlreadyExistsError`. Existing registrations can never be modified, only deprecated.

2. **Deprecation without deletion** — marking a version deprecated sets `deprecated=True` and `deprecated_reason` on the stored entity. The entity remains queryable (for reproducibility of old Studies). Deprecated versions are excluded from `list_algorithms()` by default but included with `include_deprecated=True`.

3. **Current version resolution** — `get_current_version()` returns the most recently registered non-deprecated version. If all versions are deprecated, returns the most recent deprecated version with a deprecation warning.

4. **Version string format** — validates that version strings follow semantic versioning (`MAJOR.MINOR.PATCH`) or date-based versioning (`YYYY-MM-DD`). Rejects free-text versions.

5. **Version history preservation** — old Studies reference specific `(id, version)` pairs. The Version Manager ensures these pairs remain resolvable indefinitely, even after deprecation.

---

## State

No in-memory state. All state is in the Entity Store.

---

## Implementation Reference

`corvus_corone/algorithm_registry/version_manager.py`

---

## SRS Traceability

- FR-R-04 (versioned registry): algorithm versions must be immutable and historically preserved.
- MANIFESTO Principle 18 (reproducibility): old Studies must be re-executable with the same algorithm version.
