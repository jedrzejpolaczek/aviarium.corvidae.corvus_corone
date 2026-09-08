# API Facade

> Container: [Public API + CLI](../../03-c4-leve2-containers/04-public-api-cli.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Expose the Corvus Corone library as a set of stable `cc.*` Python functions, validate all inputs at the system boundary, and delegate to the appropriate internal containers.

---

## Interface

> **Descriptive document (ADR-012).** The authoritative definition is the contract cited
> below. This page explains only how that contract is grouped into a component and why the
> boundary falls where it does. It does not define signatures.

The public function surface is defined in
[`docs/03-technical-contracts/04-public-api-contract.md`](../../../../../03-technical-contracts/04-public-api-contract.md),
which is normative for signatures, parameter names, defaults, return types and exceptions.
The facade implements every function listed there and adds none.

For the V1 release the surface is: `cc.list_problems`, `cc.list_algorithms`, `cc.get_problem`,
`cc.get_algorithm`, `cc.create_study`, `cc.lock_study`, `cc.update_study`, `cc.run`,
`cc.get_experiment`, `cc.get_runs`, `cc.get_result_aggregates`, `cc.generate_reports` and
`cc.export_raw_data`.

`cc.visualize`, `cc.get_algorithm_genealogy` and `cc.get_algorithm_lineage` belong to the
Algorithm Visualization Engine and are outside V1 (SRS 1, V1 Release Scope). `cc.resume` has
no counterpart in the contract and is not part of the surface.

## Dependencies

- **Study Orchestrator** — `cc.create_study()`, `cc.lock_study()`, `cc.run()`
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
