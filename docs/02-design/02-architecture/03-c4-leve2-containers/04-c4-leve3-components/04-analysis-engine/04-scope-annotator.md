# Scope Annotator

> Container: [Analysis Engine](../../03-c4-leve2-containers/09-analysis-engine.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Tag every MetricResult and TestResult with the full problem+algorithm+budget scope metadata, enabling downstream query filtering without re-joining against the registry.

---

## Interface

Called after Statistical Tester by the analysis pipeline:

```python
class ScopeAnnotator:
    def annotate(
        self,
        test_results: list[TestResult],
        raw_metric_results: list[RawMetricResult],
        registry: AlgorithmRegistry,
        repo: ProblemRepository,
    ) -> list[AnnotatedResult]:
        """
        Enriches each result with full scope metadata.
        Returns AnnotatedResult objects ready for persistence.
        """
```

`AnnotatedResult` fields: all `TestResult` fields + `problem_name`, `problem_dimension`, `problem_noise_level`, `algorithm_family`, `algorithm_version`, `budget_fraction` (budget/max_budget).

---

## Dependencies

- **Algorithm Registry** — resolves algorithm IDs to full metadata (family, version)
- **Problem Repository** — resolves problem IDs to full metadata (name, dimension, noise level)
- No external libraries required

---

## Key Behaviors

1. **Scope resolution** — for each result, calls `registry.get_algorithm(algorithm_id)` and `repo.get_problem(problem_id)` to fetch full metadata. Attaches relevant fields to the result.

2. **Budget fraction computation** — computes `budget_fraction = budget / problem.max_budget` for each result. This normalises budget across problems with different scales.

3. **Missing entity handling** — if an entity cannot be resolved (e.g., algorithm was deregistered after the study ran), the annotator fills the missing fields with `null` and sets `data_quality.missing_metadata = True`. It does not raise an error.

4. **Denormalisation by design** — deliberately duplicates metadata (e.g., `algorithm_family`) into each result. This is intentional: query performance in the Results Store does not require joins. The Results Store is append-only; denormalisation trades storage for query speed.

5. **Batch processing** — processes all results in a single pass; does not call the registry or repository per-result (batches registry calls to avoid N+1 lookups).

---

## State

No persistent state. All data is fetched from the registry/repository and embedded in the output.

---

## Implementation Reference

`corvus_corone/analysis_engine/scope_annotator.py`

---

## SRS Traceability

- FR-A-03 (scope annotation): every stored result must be queryable by problem, algorithm, and budget without joins.
- UC-05 (filter and explore results): scope annotation enables the filtering use case.
