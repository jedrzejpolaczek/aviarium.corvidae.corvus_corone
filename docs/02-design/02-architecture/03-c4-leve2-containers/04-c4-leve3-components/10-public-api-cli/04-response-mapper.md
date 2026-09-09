# Response Mapper

> Container: [Public API + CLI](../../04-public-api-cli.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility


---

## Interface

```python
class ResponseMapper:
    def map_study_result(self, study: Study, experiment: Experiment, runs: list[Run]) -> Experiment: ...
    def map_algorithm_summary(self, instance: AlgorithmInstance) -> AlgorithmInstanceSummary: ...
    def map_algorithm_detail(self, instance: AlgorithmInstance) -> AlgorithmInstance: ...
    def map_result_aggregates(self, metric_results: list[MetricResult]) -> ResultAggregates: ...
```

---

## Dependencies

- `dataclasses` stdlib — API return type construction
- No other dependencies (pure transformation logic)

---

## Key Behaviors

1. **Schema stability** — API return types (e.g., `Experiment`, `AlgorithmInstanceSummary`) are stable across library versions. Internal domain objects may change; the Response Mapper absorbs those changes and maintains the API contract.

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

- FR-28 (stable public API): the Response Mapper is the enforcement mechanism for API stability.

> **Post-V1 surface removed.** Earlier revisions listed three visualization and
> genealogy functions here, together with the view types they return. They belong to
> the Algorithm Visualization Engine, which SRS 1 places outside the V1 release, and no
> contract defines them. They are added back when that container enters scope, together
> with the contracts that define them (ADR-012).
