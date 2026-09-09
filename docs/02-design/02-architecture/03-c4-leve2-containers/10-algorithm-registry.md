# Container: Algorithm Registry

> Index: [01-index.md](01-index.md)

**Responsibility:** Store, version, and serve `AlgorithmInstance` records — the registry of
all algorithm implementations available for benchmarking. Validates new registrations against
the Algorithm Interface contract, enforces version-pinned `code_reference` fields, and exposes
filtering and lookup for use during study design and Run execution.

**Technology:** Python.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Algorithm lookup | `get_algorithm(id)` / `list_algorithms(filters)` | Public API (`cc.list_algorithms()`, `cc.get_algorithm()`), Experiment Runner (loads instance per Run), Algorithm Visualization Engine (reads metadata for labelling) |
| Algorithm registration | `register_algorithm(algorithm)` → `id` | Algorithm Author (via `cc.register_algorithm()` or `corvus verify`) |
| Algorithm deprecation | `deprecate_algorithm(id, reason, superseded_by)` | Maintainer |

Full interface contract: [`../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md`](../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) (§ AlgorithmRepository)

**Dependencies:** None. The Algorithm Registry is a leaf component in the dependency graph;
it depends only on the persistence layer (local file store in V1).

**Data owned:** All `AlgorithmInstance` records and their supersession lineage. Stored under the
`LocalFileRepository` root (`algorithms/<id>/`).

**Versioning:** entities are immutable and there is no `version` parameter (ADR-020).
`get_algorithm(id)` returns the same bytes forever; a revision is registered as a new entity
with a new UUID, and the old one carries `superseded_by`. `list_algorithms()` excludes
deprecated entities; `get_algorithm(id)` still retrieves them, which is what study
reproduction needs (MANIFESTO Principle 19). The `version` field remains on the record as
human-readable metadata for display and citation, never as an addressing key.

**Actors served:** Algorithm Author (primary — registration and verification, UC-02);
Researcher (study design reads); Experiment Runner (execution-time instance loading);
Learner (algorithm metadata for visualizations).

**Relevant SRS section:** FR-05 (algorithm registration with validation), FR-06 (algorithm
versioning and deprecation), FR-07 (list and filter algorithms).
