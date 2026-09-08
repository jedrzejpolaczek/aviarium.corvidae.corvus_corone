# Version Manager

> Container: [Problem Repository](../../03-c4-leve2-containers/11-problem-repository.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Manage version history for registered ProblemInstances, enforce immutability of registered versions, and support deprecation without deletion — mirroring the Algorithm Registry's Version Manager architecture.

---

## Interface

```python
class ProblemVersionManager:
    def register(self, instance: ProblemInstance, entity_store: ProblemEntityStore) -> None: ...
    def deprecate(self, problem_id: str, version: str, reason: str, entity_store: ProblemEntityStore) -> None: ...
    def get_current_version(self, problem_id: str, entity_store: ProblemEntityStore) -> ProblemInstance: ...
    def list_versions(self, problem_id: str, entity_store: ProblemEntityStore) -> list[ProblemInstance]: ...
```

---

## Dependencies

- **Entity Store** — all reads and writes delegated here

---

## Key Behaviors

Identical architecture to [Algorithm Registry — Version Manager](../11-algorithm-registry/version-manager.md), applied to ProblemInstances:

1. **Immutability enforcement** — duplicate `(id, version)` raises `ProblemAlreadyExistsError`.
2. **Deprecation without deletion** — sets `deprecated=True` on the stored entity.
3. **Current version resolution** — returns latest non-deprecated version.
4. **Version format validation** — same semver / date-based validation as Algorithm Registry.
5. **History preservation** — deprecated problem versions remain resolvable for old Study reproducibility.

---

## State

No in-memory state.

---

## Implementation Reference

`corvus_corone/problem_repository/version_manager.py`

---

## SRS Traceability

- FR-R-07 (versioned problem repository): problem versions must be immutable and historically preserved.
- MANIFESTO Principle 18 (reproducibility): old Studies must be re-executable with the same problem version.
