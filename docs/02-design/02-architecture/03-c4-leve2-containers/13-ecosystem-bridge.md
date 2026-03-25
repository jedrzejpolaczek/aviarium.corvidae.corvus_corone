# Container: Ecosystem Bridge

> Index: [01-index.md](01-index.md)

**Responsibility:** Translate completed Corvus Corone study artifacts into the file formats
expected by external benchmarking platforms (COCO/BBOB, IOHprofiler, Nevergrad), and publish
versioned datasets to artifact repositories (Zenodo, Figshare). Every export call returns an
explicit information-loss manifest documenting every field that was dropped or approximated
during translation (FR-26, NFR-INTEROP-01).

**Technology:** Python.

**Interfaces exposed:**

| Surface | Form | Who uses it |
|---|---|---|
| Platform export | `export(experiment, format)` → export files + `information_loss_manifest` | Public API (`cc.export_raw_data()` / `corvus export`) |
| Artifact publication | `publish(experiment, target)` → versioned dataset DOI | Researcher (manual trigger, UC-06) |

Full format mapping specifications (field-level, information-loss manifests, version
compatibility): [`../../../03-technical-contracts/01-data-format/11-interoperability-mappings.md`](../../../03-technical-contracts/01-data-format/11-interoperability-mappings.md)

**Supported export targets:**

| Target | Format | Direction | Notes |
|---|---|---|---|
| COCO / BBOB | `BBOBNewDataFormat` (`.info` + `.dat`) | Export only | `cocopp >= 2.6`; requires `ProblemInstance.objective.known_optimum` for gap computation |
| IOHprofiler | v0.3.3+ JSON sidecar + `.dat` | Export only | `ioh >= 0.3.3`; all records exported (improvement + scheduled + end-of-run) |
| Nevergrad | `ParametersLogger` JSON-lines | Bidirectional | Nevergrad results collected natively can be imported into Corvus `PerformanceRecord`s |
| Zenodo / Figshare | Versioned dataset archive | Publish only | Triggered manually; returns DOI |

**Dependencies:**

| Dependency | Reason |
|---|---|
| Results Store | Reads `Study`, `Experiment`, `Run`, `PerformanceRecord`, and `AlgorithmInstance` / `ProblemInstance` artifacts for the target Experiment |

**Data owned:** None. Export files are ephemeral outputs written to a caller-specified
output directory; they are not stored in the Results Store. Published dataset DOIs are
recorded in the `Experiment` record.

**Information-loss contract:** Every `export()` call MUST return an
`information_loss_manifest` listing all `LOSS-*` items that apply to the specific export.
Critical-severity items (e.g., `LOSS-COCO-01` — missing `known_optimum`) are flagged before
the export is produced. The caller confirms before proceeding.

**Actors served:** Researcher (primary — cross-platform comparison and dataset publication,
UC-06).

**Relevant SRS section:** FR-23 (COCO export), FR-24 (IOHprofiler export), FR-25 (Nevergrad
adapter), FR-26 (information-loss manifest), NFR-INTEROP-01 (lossless or documented export).
