# Interface Requirements — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: States what the system owes each external system — the boundary contracts at the
system edge. Each interface requirement describes direction, format, behaviour, and failure handling.

NARRATIVE POSITION:
  C1 context (external systems) → Interface Requirements (what each boundary must support)
  Interface Requirements → data-format.md §4 (field-level mappings)
  Interface Requirements → interface-contracts.md (method signatures)
  Interface Requirements → Functional Requirements (FR-23 through FR-26)

CONNECTS TO:
  ← docs/02-design/02-architecture/c1-context.md                    : external system definitions
  ← functional-requirements.md                                       : FR-23–FR-26 are implemented here
  → docs/03-technical-contracts/data-format.md §4                   : field mappings for each platform
  → docs/03-technical-contracts/interface-contracts.md               : method signatures for each adapter
  → non-functional-requirements.md                                   : NFR-INTEROP-01
  → use-cases.md                                                      : UC-06 exercises all export interfaces
  → docs/ROADMAP.md                                                   : V2 interfaces are V2 Horizon items

NOTE ON MAPPING STATUS:
  Field-level format mappings (data-format.md §4) are not yet written.
  REF-TASK-0005 (COCO), REF-TASK-0006 (Nevergrad), REF-TASK-0007 (IOHprofiler) track this work.
  This document records the interface requirements; data-format.md §4 will record the field details.
-->

---

## 7.1 COCO Export Interface

**Direction:** Export (Corvus Corone → COCO)
**Format:** COCO archive format (`.zip` containing `.info` and `.dat` files per the COCO benchmark suite convention)
**Requirement:** FR-23
**Data mapping:** `docs/03-technical-contracts/data-format.md` §4 COCO mapping (`REF-TASK-0005` — mapping not yet written)

**Behavior:**
- The system converts a completed Experiment's Performance Records and Result Aggregates to COCO format
- Fields without a COCO equivalent are listed in the information-loss manifest (FR-26)
- The export MUST be loadable by the COCO post-processing tools without modification

**Failure handling:**
- If a mandatory COCO field has no source in the Corvus Corone schema, the export is rejected with an explicit error identifying the missing field
- Partially written archives MUST be cleaned up on failure; no corrupt partial exports should be left on disk

**Connects to:** FR-23, FR-26, NFR-INTEROP-01, `use-cases.md` UC-06, `REF-TASK-0005`

---

## 7.2 IOHprofiler Export Interface

**Direction:** Export (Corvus Corone → IOHprofiler)
**Format:** IOHprofiler `.dat` performance files, loadable in IOHanalyzer
**Requirement:** FR-24
**Data mapping:** `docs/03-technical-contracts/data-format.md` §4 IOHprofiler mapping (`REF-TASK-0007` — mapping not yet written)

**Behavior:**
- The system converts Performance Records (anytime curves) to IOHprofiler `.dat` format
- One `.dat` file is produced per (problem, algorithm) pair per Experiment
- Fields without an IOHprofiler equivalent are listed in the information-loss manifest (FR-26)

**Failure handling:**
- Reject export if the `.dat` file cannot represent the Performance Records without critical data loss (e.g., missing evaluation counter)

**Connects to:** FR-24, FR-26, NFR-INTEROP-01, `use-cases.md` UC-06, `REF-TASK-0007`

---

## 7.3 Nevergrad Algorithm Interface

**Direction:** Import (Nevergrad optimizer → Corvus Corone Algorithm Instance)
**Format:** Python adapter class implementing the Corvus Corone Algorithm interface (→ `docs/03-technical-contracts/interface-contracts.md`)
**Requirement:** FR-25
**Data mapping:** `docs/03-technical-contracts/data-format.md` §4 Nevergrad mapping (`REF-TASK-0006` — mapping not yet written)

**Behavior:**
- A Nevergrad optimizer is wrapped by implementing the Algorithm interface; the adapter delegates to the Nevergrad optimizer internally
- The wrapped optimizer participates in Studies identically to a native Algorithm Instance
- The Algorithm Instance record's `framework` field is set to `"nevergrad"` and `framework_version` is pinned

**Failure handling:**
- If the Nevergrad optimizer raises an exception during a Run, it is captured as a Run failure (FR-12); the Study continues

**Connects to:** FR-25, FR-26, NFR-INTEROP-01, `use-cases.md` UC-02 (wrapping path), UC-06, `REF-TASK-0006`

---

## 7.4 HPC / Cloud Job Submission Interface

**Direction:** Integration (Corvus Corone Experiment Runner → HPC/Cloud scheduler)
**Format:** TBD — depends on target scheduler (SLURM, Kubernetes, etc.)
**Requirement:** V2 Horizon feature; not in Milestone 1 or 2 scope
**Status:** Blocked on V2 Platform design

**Notes:**
- The `Runner` interface abstraction (→ `docs/03-technical-contracts/interface-contracts.md`) is designed to allow a `DistributedRunner` implementation for V2 without changing the public API
- No scheduler-specific code is permitted in V1

**Connects to:** `docs/02-design/02-architecture/adr/ADR-001-library-with-server-ready-data-layer.md` (server-ready data layer enables this); `docs/ROADMAP.md` V2 Horizon

---

## 7.5 Artifact Repository Publication Interface

**Direction:** Export (Corvus Corone → external open data repository)
**Format:** Open archive format compatible with DOI-issuing repositories (e.g., Zenodo, Figshare); specific format TBD as an ADR
**Requirement:** FR-18 (complete Artifact archive); NFR-OPEN-01 (open availability)
**Status:** Publication tooling is V2 scope; FR-18 archive production is V1

**Behavior:**
- V1: The system produces a self-contained Artifact archive (local directory or `.zip`) that can be uploaded to a repository manually
- V2: The system publishes directly to a configured open repository and records the DOI in the Study record

**Connects to:** FR-18, NFR-OPEN-01, CONST-COM-01, CONST-COM-02, `docs/05_community/versioning-governance.md`

---

> **`TODO: REF-TASK-0012`** — Complete field-level format specifications for each interface once `docs/03-technical-contracts/data-format.md` §4 mappings are written (blocked on `REF-TASK-0005`, `REF-TASK-0006`, `REF-TASK-0007`). Owner: ecosystem integration lead.
