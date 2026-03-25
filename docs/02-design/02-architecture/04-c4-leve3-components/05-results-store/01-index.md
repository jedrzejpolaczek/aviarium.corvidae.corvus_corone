# C3: Components — Results Store

> C2 Container: [12-results-store.md](../../03-c4-leve2-containers/12-results-store.md)
> C3 Index: [../01-c3-components.md](../01-c3-components.md)

The Results Store persists and retrieves all study artifacts to the local filesystem. PerformanceRecords are stored in dual format: JSONL for streaming write during Run execution, and Parquet/snappy for bulk query after Run completion (ADR-010: 20× write throughput, 9.3× smaller files, 59× faster range queries vs. SQLite).
Actors: written to by Experiment Runner and Analysis Engine; read by Reporting Engine, Analysis Engine, and Public API.

---

## Component Diagram

```mermaid
---
config:
  look: neo
  theme: redux-dark
  themeVariables:
    background: transparent
---
flowchart TB
  subgraph RS["Results Store"]
    lfr["Local File Repository\nBase path management\nDirectory structure"]
    jes["JSON Entity Store\nStudy / Run / Experiment\nJSON files"]
    jw["JSONL Performance Writer\nStreaming append\nper-evaluation write"]
    pw["Parquet Performance Writer\nBatch write after Run\n≥1000 records → Parquet"]
    rr["Performance Record Reader\nUnified read\nJSONL + Parquet detection"]
  end

  er["Experiment Runner"] L_er_jw@--> jw
  jw L_jw_lfr@--> lfr
  pw L_pw_lfr@--> lfr
  jes L_jes_lfr@--> lfr
  rr L_rr_lfr@--> lfr

  orch["Study Orchestrator"] L_orch_jes@--> jes
  ae["Analysis Engine"] L_ae_rr@--> rr
  ae L_ae_jes@--> jes
  rep["Reporting Engine"] L_rep_rr@--> rr
  api["Public API"] L_api_rr@--> rr
  api L_api_jes@--> jes

  jw -.->|"post-Run\n≥1000 records"| pw

  style RS fill:#161616,stroke:#00C853,color:#aaaaaa

  linkStyle 0,1,2,3 stroke:#00C853,fill:none
  linkStyle 4 stroke:#2962FF,fill:none
  linkStyle 5 stroke:#00C853,fill:none
  linkStyle 6 stroke:#2962FF,fill:none
  linkStyle 7 stroke:#00C853,fill:none
  linkStyle 8,9 stroke:#2962FF,fill:none
  linkStyle 10 stroke:#FF6D00,fill:none
  linkStyle 11 stroke:#FF6D00,fill:none

  L_er_jw@{ animation: fast }
  L_jw_lfr@{ animation: fast }
  L_pw_lfr@{ animation: fast }
  L_jes_lfr@{ animation: fast }
  L_rr_lfr@{ animation: fast }
  L_orch_jes@{ animation: fast }
  L_ae_rr@{ animation: fast }
  L_ae_jes@{ animation: fast }
  L_rep_rr@{ animation: fast }
  L_api_rr@{ animation: fast }
  L_api_jes@{ animation: fast }
```

---

## Components

| Component | File | Responsibility |
|---|---|---|
| Local File Repository | [local-file-repository.md](02-local-file-repository.md) | Manages the filesystem path hierarchy and directory structure for all artifacts |
| JSON Entity Store | [json-entity-store.md](03-json-entity-store.md) | Reads and writes domain entities (Study, Experiment, Run) as JSON files |
| JSONL Performance Writer | [jsonl-performance-writer.md](04-jsonl-performance-writer.md) | Streams PerformanceRecord observations to JSONL files during Run execution |
| Parquet Performance Writer | [parquet-performance-writer.md](05-parquet-performance-writer.md) | Converts completed Run JSONL files to Parquet/snappy format post-Run |
| Performance Record Reader | [performance-record-reader.md](06-performance-record-reader.md) | Unified read interface over JSONL and Parquet; detects format automatically |

---

## Cross-Cutting Concerns

### Logging & Observability

File I/O operations are not individually logged (too high volume). The Results Store logs one structured entry per entity write (Study, Run, Experiment) at DEBUG level: `action`, `entity_type`, `entity_id`, `path`, `size_bytes`.

Parquet conversion completion is logged at INFO level: `experiment_id`, `run_id`, `records_converted`, `jsonl_size_bytes`, `parquet_size_bytes`.

### Error Handling

- **Write failures**: if a JSONL write fails mid-Run (e.g., disk full), the writer raises `StorageError` immediately. The Run Isolator catches this and marks the Run `aborted`.
- **Read failures**: if neither JSONL nor Parquet exists for a requested run_id, the reader raises `RecordNotFoundError`. Callers are expected to handle this.
- **Partial Parquet conversion**: if the Parquet writer fails mid-conversion, the JSONL file is preserved (not deleted). The next read operation will fall back to JSONL. The failed Parquet file is deleted to avoid partial reads.

### Randomness / Seed Management

No random state. The Results Store is purely I/O.

### Configuration

| Parameter | Source | Scope |
|---|---|---|
| `results_dir` | StudyConfig / env `CORVUS_RESULTS_DIR` | Global |
| `parquet_threshold` | StudyConfig (default: 1000 records) | Per-Run |
| `compression` | StudyConfig (default: `snappy`) | Per-Run Parquet |

### Testing Strategy

- **Local File Repository**: unit-tested; verifies directory creation, path construction, and cleanup.
- **JSON Entity Store**: unit-tested with all entity types; verifies round-trip serialisation fidelity.
- **JSONL Performance Writer**: unit-tested with synthetic PerformanceRecords; verifies streaming write and flush guarantees.
- **Parquet Performance Writer**: integration-tested; verifies conversion correctness (record count match) and that the JSONL file is preserved if conversion fails.
- **Performance Record Reader**: integration-tested with both JSONL and Parquet sources; verifies identical read results from both formats for the same data.
