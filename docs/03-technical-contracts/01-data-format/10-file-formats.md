# §3 File Formats and Storage

> Index: [01-data-format.md](01-data-format.md)

<!--
  For each entity type, specify:
    - Primary storage format (JSON / JSONL / Parquet / HDF5 / CSV / other)
    - Why this format? → create an ADR if the choice is non-obvious
    - Schema file location (JSON Schema, Avro schema, Pydantic model, etc.)
    - Compression / encoding for large data (PerformanceRecord can be voluminous)
    - File naming conventions and directory structure

  Hint — considerations:
    - Human readability vs. performance (JSON vs. Parquet)
    - Tool ecosystem: what can COCO/IOHprofiler/Nevergrad already read?
    - Long-term archival: open formats preferred (Principle 22)
-->

> **Status:** 🚧 Internal Corvus format specs pending.
> Third-party export formats (COCO, IOHprofiler, Nevergrad) are fully specified
> in [§4 Interoperability Mappings](11-interoperability-mappings.md).

## §3.1 IOHprofiler export format

Cross-reference: [§4.2 IOHprofiler mapping](11-interoperability-mappings.md#42-iohprofiler-v033)

The `IOHExporter` class
(`corvus_corone.export.ioh_exporter.IOHExporter`) writes PerformanceRecords to
IOHprofiler v0.3.3+ format.  The output layout under a caller-supplied
`output_dir` is:

```
<output_dir>/
└── <algorithm_id>/
    ├── IOHprofiler_f<func_id>_<func_name>.json   ← JSON sidecar (all dimensions)
    └── data_f<func_id>_<func_name>/
        └── IOHprofiler_f<func_id>_DIM<dim>.dat   ← performance log
```

### .dat file

Two-column tab-separated text file with an unquoted header line repeated at
every run boundary:

```
evaluations raw_y
1 4.2345678901
2 3.1415926536
evaluations raw_y
1 5.0000000000
…
```

| Column | Source | Notes |
|---|---|---|
| `evaluations` | `PerformanceRecord.evaluation_number` | 1-based integer |
| `raw_y` | `PerformanceRecord.best_so_far` (or `objective_value` if absent) | Best-so-far value at this evaluation |

### JSON sidecar

Named `IOHprofiler_f<func_id>_<func_name>.json`, one per (algorithm, function)
pair.  Stores metadata that has no `.dat` equivalent:

| Sidecar field | Source |
|---|---|
| `version` | `"0.3.5"` (hard-coded to spec version) |
| `function_id` | `ProblemMeta.func_id` |
| `function_name` | `ProblemMeta.func_name` |
| `maximization` | `ProblemMeta.maximization` |
| `algorithm.name` | `AlgorithmMeta.name` |
| `corvus_seed` | `RunRecord.seed` (non-standard extension) |
| `corvus_run_id` | `RunRecord.run_id` (non-standard extension) |

Non-standard fields (`corvus_seed`, `corvus_run_id`) are ignored by
IOHanalyzer but preserve Corvus reproducibility metadata.  Full field mapping
and information-loss manifest keys are in
[§4.2](11-interoperability-mappings.md#42-iohprofiler-v033).
