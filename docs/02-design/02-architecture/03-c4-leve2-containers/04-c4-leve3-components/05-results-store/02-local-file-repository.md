# Local File Repository

> Container: [Results Store](../../12-results-store.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Manage the filesystem path hierarchy and directory structure for all study artifacts, providing canonical path resolution for all other Results Store components.

---

## Interface

> **Descriptive document (ADR-012).** The authoritative definition is the contract cited
> below. This page explains only how that contract is grouped into a component and why the
> boundary falls where it does. It does not define signatures.

`LocalFileRepository` implements the `RepositoryFactory` contract defined in
[`06-repository-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md):
the seven domain repository properties and their methods. That is the whole of its public
surface.

The on-disk layout it produces is specified in
[`10-file-formats.md`](../../../../../03-technical-contracts/01-data-format/10-file-formats.md)
3.2. Per ADR-001 that layout is an implementation detail of this component: no path-resolution
method is exposed, and no other component may construct a path into the store or traverse it.
Components that need artifacts obtain them through the repository properties.

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
