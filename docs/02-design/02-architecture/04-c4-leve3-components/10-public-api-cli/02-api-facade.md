# API Facade

> Container: [Public API + CLI](../../03-c4-leve2-containers/04-public-api-cli.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Expose the Corvus Corone library as a set of stable `cc.*` Python functions, validate all inputs at the system boundary, and delegate to the appropriate internal containers.

---

## Interface

Primary public API surface:

```python
# Study execution
cc.run(study_config: dict | StudyConfig) -> StudyResult
cc.resume(study_id: str) -> StudyResult

# Entity queries
cc.list_algorithms(filters: dict = {}) -> list[AlgorithmSummary]
cc.get_algorithm(algorithm_id: str) -> AlgorithmDetail
cc.list_problems(filters: dict = {}) -> list[ProblemSummary]
cc.get_problem(problem_id: str) -> ProblemDetail

# Results
cc.get_result_aggregates(experiment_id: str) -> ResultAggregates
cc.get_run_results(run_id: str) -> RunResults

# Visualization
cc.visualize(
    algorithm_id: str,
    viz_type: str,
    experiment_id: str | None = None,
    format: str = "png",
    output_path: str | None = None,
    output_dir: str | None = None,
) -> VisualizationResult | list[VisualizationResult]

# Genealogy
cc.get_algorithm_genealogy(algorithm_id: str) -> AlgorithmGenealogy
cc.get_algorithm_lineage(algorithm_id: str) -> AlgorithmLineage

# Export
cc.export(experiment_id: str, format: str, output_dir: str) -> ExportResult
```

---

## Dependencies

- **Study Orchestrator** — `cc.run()`, `cc.resume()`
- **Algorithm Registry** — `cc.list_algorithms()`, `cc.get_algorithm()`
- **Problem Repository** — `cc.list_problems()`, `cc.get_problem()`
- **Results Store** — `cc.get_result_aggregates()`, `cc.get_run_results()`
- **Algorithm Visualization Engine** — `cc.visualize()`
- **Ecosystem Bridge** — `cc.export()`
- **Response Mapper** — all return values pass through here

---

## Key Behaviors

1. **Input validation** — validates all function arguments before calling any internal container. Raises `CorvusValidationError` with a complete list of errors. Examples: unknown `algorithm_id` format, invalid `viz_type` string, missing required `StudyConfig` fields.

2. **StudyConfig coercion** — `cc.run()` accepts both raw `dict` and `StudyConfig` objects. If a dict is provided, it is coerced via `StudyConfig.from_dict()` before passing to the Study Orchestrator.

3. **Response mapping** — all return values pass through the Response Mapper before being returned to the caller. The API Facade never returns raw domain objects.

4. **`cc.visualize()` multiplexing** — if `viz_type="all"`, calls the Algorithm Visualization Engine for each known viz type and returns a `list[VisualizationResult]`. Otherwise returns a single `VisualizationResult`.

5. **Thread safety** — the API Facade is stateless. Multiple concurrent `cc.run()` calls are safe as long as their `study_id` values differ (Results Store uses per-study directories).

---

## State

Stateless. No instance variables.

---

## Implementation Reference

`corvus_corone/__init__.py` (public API surface)
`corvus_corone/api/facade.py` (implementation)

---

## SRS Traceability

- Entry point for all user-facing use cases (UC-01 through UC-10).
- FR-API-01 (stable public API): the facade is the versioned API surface — internal refactors do not break callers.
