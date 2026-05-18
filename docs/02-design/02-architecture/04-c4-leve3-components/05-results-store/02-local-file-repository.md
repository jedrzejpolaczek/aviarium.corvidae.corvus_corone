# Local File Repository

> Container: [Results Store](../../03-c4-leve2-containers/12-results-store.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Manage the filesystem path hierarchy and directory structure for all study artifacts, providing canonical path resolution for all other Results Store components.

---

## Interface

```python
class LocalFileRepository:
    def __init__(self, results_dir: Path) -> None: ...

    def study_dir(self, study_id: str) -> Path: ...
    def experiment_dir(self, study_id: str, experiment_id: str) -> Path: ...
    def run_dir(self, study_id: str, experiment_id: str, run_id: str) -> Path: ...
    def ensure_dirs(self, path: Path) -> None: ...
    def entity_path(self, entity_type: str, entity_id: str) -> Path: ...
    def jsonl_path(self, run_id: str) -> Path: ...
    def parquet_path(self, run_id: str) -> Path: ...
```

---

## Dependencies

- Python `pathlib.Path` stdlib
- Python `os` stdlib

---

## Key Behaviors

1. **Directory hierarchy** — enforces the canonical structure:
   ```
   {results_dir}/
     studies/{study_id}/study.json
     experiments/{experiment_id}/experiment.json
     runs/{run_id}/
       run.json
       seed.json
       performance.jsonl
       performance.parquet (post-conversion)
       run.log
   ```

2. **Lazy creation** — `ensure_dirs()` creates all intermediate directories as needed. Idempotent (safe to call if directory already exists).

3. **Path isolation** — all paths are constructed from the `results_dir` root. No component constructs paths directly — all path resolution goes through this component. This ensures a single point of change if the directory structure evolves.

4. **Conflict detection** — if `entity_path()` is called for an entity that already has a file at the resolved path, it does not raise; callers are responsible for checking existence before writing.

5. **Cleanup support** — provides `delete_run_artifacts(run_id)` for removing a Run's artifacts (used by the resume logic when restarting a failed Run).

---

## State

`results_dir` (set at construction). No other state.

---

## Implementation Reference

`corvus_corone/results_store/local_file_repository.py`

---

## SRS Traceability

- FR-S-02 (filesystem storage): all artifacts stored on local filesystem under `results_dir`.
- Supports all use cases that read or write study data.
