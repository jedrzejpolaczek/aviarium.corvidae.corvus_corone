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
