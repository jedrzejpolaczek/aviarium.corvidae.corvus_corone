# ADR-001: Python Library with Server-Ready Data Layer

<!--
STORY ROLE: ADRs are the "how we got here" chapters. They explain WHY the system
looks the way it does. Without them, future contributors face a black box of
decisions that appear arbitrary, leading to well-intentioned but destructive changes.

NARRATIVE POSITION:
  ADRs are cross-cutting. Every other document may reference an ADR.
  They are written when a decision is made and referenced where the decision is visible.

CONNECTS TO:
  → docs/02_design/02_architecture/c1-context.md  : delivery form shapes the actor interactions and system boundary
  → docs/03_technical_contracts/data-format.md §1 : server-compatibility is a design constraint on all entity schemas
  → docs/03_technical_contracts/interface-contracts.md : storage interface defined as abstraction (§ TBD)
  → docs/02_design/01_software_requirement_specification/SRS.md : satisfies NFR-MODULAR-01, NFR-USABILITY-01
  → docs/05_community/TASKS.md : resolves REF-TASK-0003; creates REF-TASK-0023

NAMING CONVENTION: ADR-[zero-padded number]-[kebab-case-title].md
-->

---

**Status:** Accepted

**Date:** 2026-03-02

**Deciders:** Core maintainers, technical lead

---

## Context

The system must satisfy two goals that are in tension:

**Goal 1 — Developer experience (MANIFESTO Principle 28, NFR-USABILITY-01):** A researcher familiar with Python must be able to install the library and run their first benchmarking Study in under 30 minutes. An Algorithm Author must wrap an existing optimizer in approximately 15 lines. Any required infrastructure deployment (servers, databases, cloud accounts) would immediately violate this goal.

**Goal 2 — Community capabilities (MANIFESTO Principles 20–22, 27):** The system must support open data publication, long-term artifact availability, shared result repositories, and community comparison across studies. A library that writes local files and nothing else cannot fulfill these requirements — once a researcher closes their laptop, the results are isolated and not discoverable by others.

The question is: what is the right delivery form for V1, and how do we avoid building ourselves into a dead end for V2?

**Constraints:**
- No funding for server infrastructure in V1
- Target audience includes researchers with no DevOps background
- MANIFESTO Principle 22 (long-term availability) implies eventual public archival, which a local library alone cannot provide
- MANIFESTO Principle 8 requires exact Implementation provenance — this depends on stable, shareable artifact identifiers, not local file paths

**Status quo problem:** If V1 is a naïve Python library (direct file I/O, local paths), every entity reference is a file path. When a V2 server is introduced, all stored data must be migrated and all library code that reads/writes storage must be rewritten. This is a migration, not a plug-in — and it risks breaking reproducibility of archived V1 studies.

---

## Decision

**V1 is a Python library with no server deployment requirement.** Local file storage is the default and only backend in V1.

**The storage layer is designed as an abstraction from day one.** The library never calls file I/O functions directly. All persistence is mediated through a `Repository` interface (defined in `docs/03_technical_contracts/interface-contracts.md`). V1 ships with a `LocalFileRepository` implementation. A `ServerRepository` implementation that delegates to a REST API can be plugged in without changing any other library code or any stored data format.

**All entity schemas are designed for server-compatibility:**
- Every entity has a globally unique ID (UUID format), not a local file path
- All entities are JSON-serializable (no binary-only fields in the primary schema)
- Foreign key references between entities use IDs, not file paths
- No entity contains assumptions about local directory structure

This means a V2 server can store the same JSON entities in a database and serve them via a REST API without any schema migration for studies run in V1.

---

## Rationale

**Why library-first:**
- Zero deployment friction — `pip install corvus-corone` is the entire setup
- Compatible with existing Python ML ecosystem (Optuna, SMAC, HyperOpt all work immediately as wrapping targets)
- Researchers do not need DevOps skills; Algorithm Authors can contribute without standing up infrastructure
- Satisfies NFR-USABILITY-01 directly

**Why server-ready schemas from day one:**
- MANIFESTO Principles 20 and 22 require open data in stable repositories with persistent identifiers (DOIs). A local file path is not a persistent identifier; a UUID stored in a shared repository is.
- UUID-based entity references work identically in local file storage and in a database. File path references work only in local storage.
- JSON serialization is a prerequisite for a REST API. Making schemas JSON-first costs nothing in V1 and saves a migration in V2.
- `repository.get_problem(id)` vs. `open("./problems/X.json")`: the former is testable, mockable, and swappable; the latter is not.

**Which MANIFESTO principles this decision best supports:**
- Principle 28 (education and support): library form minimizes onboarding friction
- Principles 19–22 (reproducibility, open data): server-ready schemas preserve the path to open archival
- Principle 27 (community development): the repository abstraction allows community-hosted shared repositories without forking the library

**Trade-offs accepted:**
- The `Repository` abstraction adds design complexity to V1 that would not exist in a simpler "write files here" approach
- The storage interface must be kept stable across versions — it becomes a public API surface
- Contributors must resist the temptation to bypass the abstraction with direct file I/O (to be enforced via code review policy)

---

## Alternatives Considered

### Pure library with direct local file I/O

**Description:** The simplest possible approach — the library writes JSON/CSV files to a directory structure on disk, no abstraction layer. All entity references are file paths relative to a configurable root directory.

**Why rejected:** This is a V1-to-V2 migration trap. When a community server is introduced (which MANIFESTO Principles 20–22 require), every stored entity must have its path references replaced with IDs, and every piece of library code that touches storage must be rewritten. This risks breaking reproducibility of all V1 studies because the stored format is not forward-compatible.

**Under what conditions would this be reconsidered:** Only if the MANIFESTO community requirements (Principles 20–22) were descoped, which would change the fundamental mission of the project.

---

### Library + server deployed from V1

**Description:** Deploy a server from the very first release. The library communicates with a local or remote server via REST API. Local-only operation is not supported.

**Why rejected:** Infrastructure deployment is an insurmountable barrier for the target audience. Researchers running experiments on laptops or HPC clusters cannot be required to deploy and maintain a web server. This would violate NFR-USABILITY-01 (30-minute onboarding) on first contact. Early adoption is critical for a community-driven platform; eliminating the zero-friction path eliminates early adoption.

**Under what conditions would this be reconsidered:** If the system were commercially hosted (a SaaS offering) where the infrastructure is maintained by the project team. This is not the open-source community model targeted by the MANIFESTO.

---

### Hybrid: local files + optional sync to a server

**Description:** Library writes local files as the primary storage, with an optional sync command that pushes to a server. Entities are identified by file paths locally and assigned UUIDs when synced.

**Why rejected:** This creates two identity systems — local paths and UUIDs — which means every entity can have two different "identities" depending on context. Reproducibility references must choose one. If a paper cites a local path, the study cannot be retrieved by others. If a paper cites a UUID, the entity must have been synced before publication. The ID assignment is a one-way migration, not a design property of the entity itself. This is worse than either pure local or pure server.

**Under what conditions would this be reconsidered:** Never — the dual-identity problem is a fundamental flaw, not a trade-off.

---

## Consequences

**Positive:**
- V1 ships with no infrastructure requirements and satisfies NFR-USABILITY-01
- V2 server introduction is a plug-in, not a migration: `LocalFileRepository` is swapped for `ServerRepository`, existing study records are valid without modification
- The `Repository` abstraction improves testability — unit tests mock the repository; no file system required
- JSON-first schemas make COCO/IOHprofiler/Nevergrad interoperability (NFR-INTEROP-01) natural — the internal format is already JSON

**Negative / Trade-offs:**
- The storage abstraction must be designed carefully as a public API; breaking changes to the `Repository` interface after V1 release require a deprecation cycle
- Contributors must be educated not to bypass the abstraction; direct file I/O in library code is a code review rejection criterion
- UUID generation for entities adds a small runtime overhead compared to path-based references

**Risks:**
- **Risk:** The storage interface is underspecified, leading to leaky abstractions that embed file system assumptions. **Mitigation:** The interface must be designed before any storage code is written. `REF-TASK-0023` tracks this work.
- **Risk:** The `LocalFileRepository` becomes tightly coupled to a specific directory structure, making it hard for the `ServerRepository` to replicate. **Mitigation:** Directory structure is an implementation detail of `LocalFileRepository`, not part of the public interface. The public interface uses entity IDs only.
- **Risk:** JSON-only schemas are insufficient for high-volume Performance Record storage (millions of records per large study). **Mitigation:** The `PerformanceRecord` bulk storage format (e.g., Parquet, HDF5) is a separate ADR decision. The primary entity schema is JSON; bulk data storage is a separate concern.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/02_design/02_architecture/c1-context.md` | Delivery form shapes actor interactions; V2 Platform Server added as a future planned external system |
| `docs/03_technical_contracts/data-format.md §1` | Server-compatibility is a design constraint on all entity schemas defined there |
| `docs/03_technical_contracts/interface-contracts.md` | `Repository` interface must be defined here (blocked by `REF-TASK-0023`) |
| `docs/02_design/01_software_requirement_specification/SRS.md §5` | NFR-MODULAR-01 (extensibility) and NFR-USABILITY-01 (onboarding friction) both informed this decision |
| `docs/05_community/TASKS.md` | Resolves `REF-TASK-0003`; creates `REF-TASK-0023` (storage abstraction design) |
