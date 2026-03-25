# Entity Store

> Container: [Algorithm Registry](../../03-c4-leve2-containers/10-algorithm-registry.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Persist AlgorithmInstance objects as JSON files, resolve algorithm IDs to instances, and support querying by family, deprecated status, and version.

---

## Interface

```python
class AlgorithmEntityStore:
    def write(self, instance: AlgorithmInstance) -> None: ...
    def get(self, algorithm_id: str, version: str | None = None) -> AlgorithmInstance: ...
    def list_all(self, include_deprecated: bool = False) -> list[AlgorithmInstance]: ...
    def update_deprecated(self, algorithm_id: str, version: str, deprecated: bool, reason: str) -> None: ...
    def exists(self, algorithm_id: str, version: str) -> bool: ...
```

---

## Dependencies

- `json` stdlib
- `pathlib.Path` stdlib

---

## Key Behaviors

1. **Storage layout** — stores each AlgorithmInstance as `{registry_dir}/{algorithm_id}/{version}.json`. The directory structure mirrors the `(id, version)` key.

2. **ID resolution** — `get(algorithm_id)` without a version returns the latest non-deprecated version (delegates to Version Manager logic). `get(algorithm_id, version)` returns the exact version.

3. **Atomic writes** — uses write-to-tmp-then-rename for all writes (same as Results Store JSON Entity Store).

4. **Query support** — `list_all()` globs all `.json` files, deserialises each, and filters by `include_deprecated`. Supports further filtering by `algorithm_family` passed as a keyword argument.

5. **Genealogy data** — if a `genealogy.json` file exists alongside the instance file, it is loaded and attached to the `AlgorithmInstance.genealogy` field on read.

---

## State

No in-memory cache. All reads hit the filesystem. (A read cache may be added in V2 if registry size grows.)

---

## Implementation Reference

`corvus_corone/algorithm_registry/entity_store.py`

---

## SRS Traceability

- FR-R-05 (persistent registry): registry must survive process restart.
- UC-10 (algorithm genealogy): genealogy data loaded from JSON alongside instance.
