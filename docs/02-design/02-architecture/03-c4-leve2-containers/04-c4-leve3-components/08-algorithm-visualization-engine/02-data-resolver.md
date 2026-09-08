# Data Resolver

> Container: [Algorithm Visualization Engine](../../03-c4-leve2-containers/06-algorithm-visualization-engine.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Fetch algorithm metadata from the Algorithm Registry and, if an `experiment_id` is provided, study performance data from the Results Store. Provide a labeled fallback (synthetic data) when no study data is available, ensuring all renderers always have a complete `VisualizationData` object to work with.

---

## Interface

```python
class DataResolver:
    def resolve(
        self,
        algorithm_id: str,
        viz_type: VizType,
        experiment_id: str | None,
        registry: AlgorithmRegistry,
        record_reader: PerformanceRecordReader | None,
    ) -> VisualizationData:
        """
        Returns VisualizationData with algorithm metadata + study data (or fallback).
        Raises EntityNotFoundError if algorithm_id not in registry.
        """
```

`VisualizationData` fields: `algorithm_metadata`, `study_data` (or `None`), `fallback_used` (bool), `fallback_reason` (str or None).

---

## Dependencies

- **Algorithm Registry** — `get_algorithm(algorithm_id)` for metadata
- **Results Store — Performance Record Reader** — `read_experiment(experiment_id)` for study data (optional)

---

## Key Behaviors

1. **Algorithm validation** — calls `registry.get_algorithm(algorithm_id)`. If the algorithm is not found, raises `EntityNotFoundError` immediately with the available algorithm IDs.

2. **Study data resolution** — if `experiment_id` is provided, calls `record_reader.read_experiment(experiment_id)` to load PerformanceRecords. If the experiment is not found, falls back (does not raise).

3. **Fallback activation** — fallback is used when: (a) `experiment_id` is not provided, (b) the experiment has no records, or (c) the experiment does not include the requested `algorithm_id`. Fallback generates synthetic illustrative data using the algorithm's declared `known_assumptions` and `hyperparameters`.

4. **Fallback labeling** — sets `fallback_used=True` and `fallback_reason` to one of: `"No experiment_id provided"`, `"No study data found for this algorithm"`, `"Algorithm not included in experiment"`. This label is passed through to the visualization output and report metadata.

5. **Genealogy data resolution** — for `viz_type="genealogy"`, does not attempt to load study data. Returns algorithm registry metadata only (genealogy is always metadata-only).

---

## State

No persistent state.

---

## Implementation Reference

`corvus_corone/algorithm_visualization_engine/data_resolver.py`

---

## SRS Traceability

- UC-07 Failure Scenario F1 (no study data): fallback activation is implemented here.
- UC-07 Failure Scenario F2 (algorithm not registered): `EntityNotFoundError` raised here.
- UC-10: genealogy data resolution (metadata-only path).
