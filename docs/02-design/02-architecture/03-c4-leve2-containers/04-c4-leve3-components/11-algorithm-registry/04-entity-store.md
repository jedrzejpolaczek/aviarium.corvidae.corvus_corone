# Entity Store

> Container: [Algorithm Registry](../../10-algorithm-registry.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Persist Algorithm Instance objects as JSON files, resolve algorithm UUIDs to instances, and support the queries the `AlgorithmRepository` contract exposes.

---

## Interface

```python
class AlgorithmEntityStore:
    def write(self, instance: AlgorithmInstance) -> None: ...
    def get(self, algorithm_id: str) -> AlgorithmInstance: ...
    def list_all(self, include_deprecated: bool = False) -> list[AlgorithmInstance]: ...
    def update_deprecated(
        self, algorithm_id: str, reason: str, superseded_by: str | None = None
    ) -> None: ...
    def exists(self, algorithm_id: str) -> bool: ...
```

---

## Dependencies

- `json` stdlib
- `pathlib.Path` stdlib

---

## Key Behaviors

1. **Storage layout** — stores each Algorithm Instance as `{registry_dir}/{algorithm_id}.json`, the file name being the entity's UUID. There is no version segment: a revision is a separate entity with its own UUID (ADR-020).

2. **ID resolution** — `get(algorithm_id)` returns the one entity with that UUID, deprecated or not, and returns the same bytes forever. Following a lineage forward is the caller's business, through `superseded_by`.

3. **Atomic writes** — uses write-to-tmp-then-rename for all writes (same as Results Store JSON Entity Store).

4. **Query support** — `list_all()` globs all `.json` files, deserialises each, and applies the `AlgorithmFilter` fields the contract defines: `algorithm_family`, `supported_variable_types`, `framework`, `contributed_by`. Deprecated entities are excluded unless `include_deprecated` is set.

5. **Genealogy data** — genealogy is FR-37, which SRS 1.4 places outside V1. No genealogy file is read or written until that requirement enters scope.

---

## State

No in-memory cache. All reads hit the filesystem. (A read cache may be added in V2 if registry size grows.)

---

## Implementation Reference

`corvus_corone/algorithm_registry/entity_store.py`

---

## SRS Traceability

- FR-05 (schema-conforming storage): every stored record conforms to `03-algorithm-instance.md`.
- FR-17 (UUID identity): the file name is derived from the entity's UUID; the path is never the identifier.
