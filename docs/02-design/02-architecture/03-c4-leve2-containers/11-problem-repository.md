# Container: Problem Repository

> Index: [01-index.md](01-index.md)

**Responsibility:** Store, version, and serve `ProblemInstance` records — the catalogue of
all benchmark problems available for use in Studies. Validates new registrations against the
Problem Interface contract, supports filtering by problem characteristics (dimensionality,
landscape type, provenance), and exposes the instances needed by the Experiment Runner at
execution time.

**Technology:** Python.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Problem lookup | `get_problem(id)` / `list_problems(filters)` | Public API (`cc.list_problems()`, `cc.get_problem()`), Experiment Runner (loads instance per Run) |
| Problem registration | `register_problem(problem)` → `id` | Community Contributor (via `corvus verify`, UC-04) |
| Problem deprecation | `deprecate_problem(id, reason, superseded_by)` | Maintainer |

Full interface contract: [`../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md`](../../../03-technical-contracts/02-interface-contracts/06-repository-interface.md) (§ ProblemRepository)

**Dependencies:** None. The Problem Repository is a leaf component; it depends only on the
persistence layer (local file store in V1).

**Data owned:** All `ProblemInstance` records and their supersession lineage. Stored under the
`LocalFileRepository` root (`problems/<id>/`).

**Versioning:** entities are immutable and there is no `version` parameter (ADR-020).
`get_problem(id)` returns the same bytes forever; a revision is registered as a new entity
with a new UUID, and the old one carries `superseded_by`. `list_problems()` excludes
deprecated entities; `get_problem(id)` still retrieves them, which is what study
reproduction needs (MANIFESTO Principle 19). The `version` field remains on the record as
human-readable metadata for display and citation, never as an addressing key.

**Actors served:** Researcher (study design — problem selection); Experiment Runner
(execution-time instance loading); Community Contributor (registration, UC-04).

**Relevant SRS section:** FR-01 (problem registration with validation), FR-02 (problem
versioning and deprecation), FR-03 (list and filter problems), FR-04 (problem interface
contract enforcement).
