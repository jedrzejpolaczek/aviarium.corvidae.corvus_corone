# LOCF Interpolator

> Container: [Analysis Engine](../../03-c4-leve2-containers/09-analysis-engine.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Fill missing evaluation observations in convergence time-series using the Last Observation Carried Forward (LOCF) method, ensuring consistent time-series length across all Runs before metric computation.

---

## Interface

Called by the Metric Dispatcher before metric computation:

```python
class LOCFInterpolator:
    def interpolate(
        self,
        records: list[PerformanceRecord],
        budget: int,
        max_gap: int = 10,
    ) -> list[PerformanceRecord]:
        """
        Returns a complete time-series of length `budget`.
        Gaps are filled by carrying the last observed value forward.
        Gaps larger than `max_gap` are flagged with data_quality.large_gap=True.
        """
```

---

## Dependencies

- `numpy` — array construction and gap detection
- No external libraries required

---

## Key Behaviors

1. **Gap detection** — scans the `iteration` field of the input records to find missing evaluation indices (gaps between consecutive `iteration` values > 1).

2. **LOCF fill** — for each gap, inserts synthetic PerformanceRecords with `value = last_observed_value`, `best_so_far = last_best_so_far`, and `status = "interpolated"`. The `interpolated` flag is carried in the PerformanceRecord and preserved in the MetricResult.

3. **Max-gap policy** — if a gap is longer than `max_gap` evaluations, the gap is still filled (LOCF continues), but the filled records are additionally flagged with `data_quality.large_gap = True`. This allows downstream consumers to exclude suspicious data.

4. **Absent runs** — if an entire Run has zero records (subprocess crashed before recording), the interpolator returns an empty list for that Run (it does not fabricate an entire time-series from nothing). The Metric Dispatcher then excludes this Run from analysis.

5. **Idempotency** — applying the interpolator twice on an already-complete time-series produces the same output. Interpolated records already present are not duplicated.

---

## State

No persistent state. Stateless per invocation.

---

## Implementation Reference

`corvus_corone/analysis_engine/locf_interpolator.py`

---

## SRS Traceability

- FR-A-04 (missing data handling): LOCF is the default interpolation method.
- MANIFESTO Principle 18 (reproducibility): interpolated records are flagged, not silently substituted, ensuring the analysis is auditable.
