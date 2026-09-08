# Response Mapper

> Container: [Public API + CLI](../../03-c4-leve2-containers/04-public-api-cli.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Transform internal domain objects (Study, Run, MetricResult, AlgorithmInstance, etc.) into stable, versioned API return types (StudyResult, AlgorithmSummary, VisualizationResult, etc.) that form the public API contract.

---

## Interface

```python
class ResponseMapper:
    def map_study_result(self, study: Study, experiment: Experiment, runs: list[Run]) -> StudyResult: ...
    def map_algorithm_summary(self, instance: AlgorithmInstance) -> AlgorithmSummary: ...
    def map_algorithm_detail(self, instance: AlgorithmInstance) -> AlgorithmDetail: ...
    def map_result_aggregates(self, metric_results: list[MetricResult]) -> ResultAggregates: ...
    def map_visualization_result(self, viz_output: VizOutput) -> VisualizationResult: ...
    def map_genealogy(self, genealogy_data: dict) -> AlgorithmGenealogy: ...
    def map_lineage(self, lineage_data: dict) -> AlgorithmLineage: ...
```

---

## Dependencies

- `dataclasses` stdlib — API return type construction
- No other dependencies (pure transformation logic)

---

## Key Behaviors

1. **Schema stability** — API return types (e.g., `StudyResult`, `AlgorithmSummary`) are stable across library versions. Internal domain objects may change; the Response Mapper absorbs those changes and maintains the API contract.

2. **Field selection** — API return types expose only the fields needed by callers; internal implementation details (e.g., file paths, internal status enums) are excluded or renamed to user-friendly names.

3. **Type coercion** — converts internal types (e.g., `datetime` → ISO8601 string, `Path` → string, `Enum` → string value) for JSON-serialisability.

4. **Null handling** — optional internal fields that are `None` are included in the API response as `null` (not omitted). This ensures stable deserialization for callers who check field presence.

5. **Versioning** — each API return type includes a `_schema_version` field (e.g., `"1.0"`). If the schema changes in a breaking way, the version is incremented and a deprecation warning is emitted.

---

## State

Stateless.

---

## Implementation Reference

`corvus_corone/api/response_mapper.py`

---

## SRS Traceability

- FR-API-01 (stable public API): the Response Mapper is the enforcement mechanism for API stability.
