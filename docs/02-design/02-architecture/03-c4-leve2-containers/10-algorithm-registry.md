# Container: Algorithm Registry

> Index: [01-c2-containers.md](01-c2-containers.md)

**Responsibility:** Store, version, and serve `AlgorithmInstance` records — the registry of
all algorithm implementations available for benchmarking. Validates new registrations against
the Algorithm Interface contract, enforces version-pinned `code_reference` fields, and exposes
filtering and lookup for use during study design and Run execution.

**Technology:** Python.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Algorithm lookup | `get_algorithm(id, version)` / `list_algorithms(filters)` | Public API (`cc.list_algorithms()`, `cc.get_algorithm()`), Experiment Runner (loads instance per Run), Algorithm Visualization Engine (reads metadata for labelling) |
| Algorithm registration | `register_algorithm(algorithm)` → `id` | Algorithm Author (via `cc.register_algorithm()` or `corvus verify`) |
| Algorithm deprecation | `deprecate_algorithm(id, reason, superseded_by)` | Maintainer |

Full interface contract: [`../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md`](../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) (§ AlgorithmRepository)

**Dependencies:** None. The Algorithm Registry is a leaf component in the dependency graph;
it depends only on the persistence layer (local file store in V1).

**Data owned:** All `AlgorithmInstance` records and their version history. Stored under the
`LocalFileRepository` root (`algorithms/<id>/`).

**Versioning:** `get_algorithm(id, version=None)` returns the latest non-deprecated version.
An explicit version string returns exactly that version — required for reproducibility
(MANIFESTO Principle 19). Deprecated instances remain retrievable by exact ID for
study reproduction.

**Actors served:** Algorithm Author (primary — registration and verification, UC-02);
Researcher (study design reads); Experiment Runner (execution-time instance loading);
Learner (algorithm metadata for visualizations).

**Relevant SRS section:** FR-05 (algorithm registration with validation), FR-06 (algorithm
versioning and deprecation), FR-07 (list and filter algorithms).
