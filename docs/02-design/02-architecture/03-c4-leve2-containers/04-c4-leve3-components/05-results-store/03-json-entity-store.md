# JSON Entity Store

> Container: [Results Store](../../03-c4-leve2-containers/12-results-store.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Read and write domain entities (Study, Experiment, Run metadata) as JSON files on the filesystem, providing typed read/write operations over the Local File Repository.

---

## Interface

```python
class JsonEntityStore:
    def write(self, entity: Study | Experiment | Run) -> None: ...
    def read_study(self, study_id: str) -> Study: ...
    def read_experiment(self, experiment_id: str) -> Experiment: ...
    def read_run(self, run_id: str) -> Run: ...
    def list_experiments(self, study_id: str) -> list[Experiment]: ...
    def list_runs(self, experiment_id: str) -> list[Run]: ...
    def update_run_status(self, run_id: str, status: str, error: str | None = None) -> None: ...
```

---

## Dependencies

- **Local File Repository** — path resolution
- `json` stdlib
- `dataclasses` stdlib (entity serialisation)

---

## Key Behaviors

1. **Entity serialisation** — uses `dataclasses.asdict()` + `json.dumps()` with `indent=2` for human-readable output. Enum fields are serialised as their string values.

2. **Entity deserialisation** — uses `json.loads()` + dataclass constructors with type coercion for dates (`datetime.fromisoformat`) and enums.

3. **Atomic writes** — writes to a `.tmp` file first, then renames to the target path. This prevents partial reads during concurrent access.

4. **`update_run_status()`** — a targeted update operation: reads the Run JSON, updates only the `status` and `error` fields, and writes back. Used by the Run Isolator to update Run status without a full entity round-trip.

5. **`list_*` operations** — glob-based: lists all `{entity_type}.json` files under the relevant directory and deserialises each. Sorted by `created_at` field.

---

## State

No in-memory state. All state is on the filesystem.

---

## Implementation Reference

`corvus_corone/results_store/json_entity_store.py`

---

## SRS Traceability

- FR-S-03 (entity persistence): Study, Experiment, Run metadata must survive process restart.
- UC-01 (create study): Study entity is created and persisted here.
