# Entity Store

> Container: [Problem Repository](../../11-problem-repository.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Persist Problem Instance objects as JSON files, resolve problem UUIDs to instances, and support the queries the `ProblemRepository` contract exposes.

---

## Interface

```python
class ProblemEntityStore:
    def write(self, instance: ProblemInstance) -> None: ...
    def get(self, problem_id: str) -> ProblemInstance: ...
    def list_all(self, include_deprecated: bool = False, filters: dict = {}) -> list[ProblemInstance]: ...
    def update_deprecated(
        self, problem_id: str, reason: str, superseded_by: str | None = None
    ) -> None: ...
    def exists(self, problem_id: str) -> bool: ...
```

---

## Dependencies

- `json` stdlib
- `pathlib.Path` stdlib

---

## Key Behaviors

Identical architecture to [Algorithm Registry — Entity Store](../11-algorithm-registry/04-entity-store.md), applied to ProblemInstances:

1. **Storage layout** — `{repo_dir}/{problem_id}.json`, keyed by the entity's UUID (ADR-020).
2. **ID resolution** — `get(problem_id)` returns the one entity with that UUID, deprecated or not.
3. **Atomic writes** — write-to-tmp-then-rename.
4. **Query support** — `list_all()` applies the `ProblemFilter` fields the contract defines: `provenance`, `real_or_synthetic`, `min_dimensions`, `max_dimensions`, `landscape_characteristics`.
5. **No in-memory cache** — all reads hit the filesystem.

---

## State

No in-memory cache.

---

## Implementation Reference

`corvus_corone/problem_repository/entity_store.py`

---

## SRS Traceability

- FR-01 (schema-conforming storage): every stored record conforms to `02-problem-instance.md`.
- FR-17 (UUID identity): the file name is derived from the entity's UUID.
