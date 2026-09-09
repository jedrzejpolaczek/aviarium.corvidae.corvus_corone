# Statistical Tester

> Container: [Analysis Engine](../../09-analysis-engine.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Apply pre-registered statistical tests (Wilcoxon signed-rank for two algorithms, Kruskal-Wallis with Holm-Bonferroni correction for more than two) to raw metric distributions, returning test statistics and p-values with effect size estimates.

---

## Interface

Called by the Metric Dispatcher:

```python
class StatisticalTester:
    def test(
        self,
        metric_results: list[RawMetricResult],
        test_config: TestConfig,
        alpha: float = 0.05,
    ) -> list[TestResult]:
        """
        Applies configured tests to pairwise or multi-group metric distributions.
        Returns TestResult per test application.
        """
```

`TestResult` is this component's envelope around the contract's `StatisticalTestResult`.
It carries every field the contract requires, `test_name`, `p_value`, `effect_size`,
`conclusion_scope` and `pre_registered`, plus the routing fields the Analysis Engine
needs: `metric_name`, `algorithm_ids`, `statistic`, `significant`, and `reason` when the
test was not applicable. `conclusion_scope` is not optional: the Analyzer contract
requires every conclusion to state the conditions under which it holds.

---

## Dependencies

- `scipy.stats` — `wilcoxon` and `kruskal`
- `numpy` — array manipulation
- `numpy` — Cliff's delta is computed from the samples directly; no effect-size package
  is required

---

## Key Behaviors

1. **Test selection** — applies the test specified in `TestConfig.test_name`:
   - `wilcoxon`: paired signed-rank test, for two algorithms
   - `kruskal`: Kruskal-Wallis, for more than two algorithms, followed by pairwise Wilcoxon

   The decision tree has exactly these two entries. Benchmarking data is always paired, because
   every algorithm is run on the same Problem Instances, so an unpaired test such as
   Mann-Whitney U does not apply and is not offered
   (`02-statistical-methodology.md` 3.2 and 3.3).

2. **Pre-registration guard** — if `test_config.pre_registered=True` and the test name was not declared in the Study's pre-registration config, raises `ValidationError`.

3. **Precondition validation** — before applying any test, validates sample size requirements:
   - Wilcoxon: requires ≥ 6 paired observations. If fewer, records `test_result=null, reason="insufficient_samples"`.
   - Kruskal-Wallis: requires ≥ 2 observations per group and ≥ 3 groups.

4. **Effect size computation** — computes Cliff's delta, required by
   `02-statistical-methodology.md` 4 for every comparison. It is a rank statistic
   computable directly from the two samples, so it needs no optional dependency and is
   never `null`.

5. **Multiple comparison correction** — applies Holm-Bonferroni to the family of p-values
   before setting `significant`. The methodology names it as the required procedure
   (`02-statistical-methodology.md` 3.6), so it is not a configurable choice.

---

## State

No persistent state. Stateless per invocation.

---

## Implementation Reference

`corvus_corone/analysis_engine/statistical_tester.py`

---

## SRS Traceability

- FR-15 (statistical significance testing): applies the correct test based on pre-registration.
- UC-04 (compare algorithms): p-values and effect sizes enable statistically grounded comparison.
