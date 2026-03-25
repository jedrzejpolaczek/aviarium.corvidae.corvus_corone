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
  ← docs/02-design/02-architecture/02-c1-context.md                  : external system definitions
  ← functional-requirements.md                                        : FR-23–FR-26 are implemented here
  → docs/03-technical-contracts/01-data-format.md §4                 : field mappings for each platform
  → docs/03-technical-contracts/02-interface-contracts.md            : method signatures for each adapter
  → non-functional-requirements.md                                    : NFR-INTEROP-01
  → use-cases.md                                                       : UC-06 exercises all export interfaces
  → docs/ROADMAP.md                                                    : V2 interfaces are V2 Horizon items

NOTE ON MAPPING STATUS:
  Field-level format mappings (data-format.md §4) are complete.
  REF-TASK-0005 (COCO), REF-TASK-0006 (Nevergrad), REF-TASK-0007 (IOHprofiler) delivered.
  REF-TASK-0012 delivered — this document is now fully specified.
-->

---

## Interface Index

| Section | Interface | Direction | Status | File |
|---|---|---|---|---|
| §7.1 | COCO Export | Export → COCO | ✅ Complete | [02-ir-7.1-coco-export.md](02-ir-7.1-coco-export.md) |
| §7.2 | IOHprofiler Export | Export → IOHprofiler | ✅ Complete | [03-ir-7.2-iohprofiler-export.md](03-ir-7.2-iohprofiler-export.md) |
| §7.3 | Nevergrad Algorithm | Import ← Nevergrad (bidirectional) | ✅ Complete | [04-ir-7.3-nevergrad-algorithm.md](04-ir-7.3-nevergrad-algorithm.md) |
| §7.4 | HPC / Cloud Job Submission | Integration → scheduler | V2 Horizon — not in V1 scope | [05-ir-7.4-hpc-cloud.md](05-ir-7.4-hpc-cloud.md) |
| §7.5 | Artifact Repository Publication | Export → open repository | V1 manual; V2 automated | [06-ir-7.5-artifact-repository.md](06-ir-7.5-artifact-repository.md) |
