# Entity Store

> Container: [Problem Repository](../../03-c4-leve2-containers/11-problem-repository.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Persist ProblemInstance objects as JSON files, resolve problem IDs to instances, and support querying by objective type, dimension, and deprecated status.

---

## Interface

```python
class ProblemEntityStore:
    def write(self, instance: ProblemInstance) -> None: ...
    def get(self, problem_id: str, version: str | None = None) -> ProblemInstance: ...
    def list_all(self, include_deprecated: bool = False, filters: dict = {}) -> list[ProblemInstance]: ...
    def update_deprecated(self, problem_id: str, version: str, deprecated: bool, reason: str) -> None: ...
    def exists(self, problem_id: str, version: str) -> bool: ...
```

---

## Dependencies

- `json` stdlib
- `pathlib.Path` stdlib

---

## Key Behaviors

Identical architecture to [Algorithm Registry — Entity Store](../11-algorithm-registry/entity-store.md), applied to ProblemInstances:

1. **Storage layout** — `{repo_dir}/{problem_id}/{version}.json`.
2. **ID resolution** — `get(problem_id)` returns latest non-deprecated version; `get(problem_id, version)` returns exact version.
3. **Atomic writes** — write-to-tmp-then-rename.
4. **Query support** — `list_all()` supports filtering by `objective_type` and `dimension` in addition to `include_deprecated`.
5. **No in-memory cache** — all reads hit the filesystem.

---

## State

No in-memory cache.

---

## Implementation Reference

`corvus_corone/problem_repository/entity_store.py`

---

## SRS Traceability

- FR-R-08 (persistent problem repository): repository must survive process restart.
