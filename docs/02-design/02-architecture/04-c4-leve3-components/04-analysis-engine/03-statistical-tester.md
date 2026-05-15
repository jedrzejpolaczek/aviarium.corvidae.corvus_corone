# Statistical Tester

> Container: [Analysis Engine](../../03-c4-leve2-containers/09-analysis-engine.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Apply pre-registered statistical tests (Wilcoxon signed-rank, Mann-Whitney U, Kruskal-Wallis) to raw metric distributions, returning test statistics and p-values with effect size estimates.

---

## Interface

Called by the Metric Dispatcher:

```python
class StatisticalTester:
    def test(
        self,
        metric_results: list[RawMetricResult],
        test_config: StatisticalTestConfig,
        alpha: float = 0.05,
    ) -> list[TestResult]:
        """
        Applies configured tests to pairwise or multi-group metric distributions.
        Returns TestResult per test application.
        """
```

`TestResult` fields: `metric_name`, `algorithm_ids`, `test_name`, `statistic`, `p_value`, `effect_size`, `significant`, `reason` (if test not applicable).

---

## Dependencies

- `scipy.stats` — `wilcoxon`, `mannwhitneyu`, `kruskal` functions
- `numpy` — array manipulation
- `pingouin` (optional) — for effect size computation (Cohen's d, rank-biserial correlation)

---

## Key Behaviors

1. **Test selection** — applies the test specified in `StatisticalTestConfig.test_name`:
   - `wilcoxon`: paired signed-rank test for paired Run comparisons (same problem instance, same budget, different algorithms)
   - `mannwhitneyu`: unpaired test for independent samples
   - `kruskal`: non-parametric multi-group comparison (3+ algorithms)

2. **Pre-registration guard** — if `test_config.pre_registered=True` and the test name was not declared in the Study's pre-registration config, raises `PreRegistrationViolationError`.

3. **Precondition validation** — before applying any test, validates sample size requirements:
   - Wilcoxon: requires ≥ 6 paired observations. If fewer, records `test_result=null, reason="insufficient_samples"`.
   - Mann-Whitney U: requires ≥ 3 observations per group.
   - Kruskal: requires ≥ 2 observations per group and ≥ 3 groups.

4. **Effect size computation** — computes rank-biserial correlation (for Wilcoxon/Mann-Whitney) or epsilon-squared (for Kruskal) as the effect size estimate. If `pingouin` is not installed, effect size is `null` (not an error).

5. **Multiple comparison correction** — if `test_config.multiple_comparison_correction` is set (e.g., Bonferroni, Holm-Sidak), applies the correction to the p-values before setting the `significant` flag.

---

## State

No persistent state. Stateless per invocation.

---

## Implementation Reference

`corvus_corone/analysis_engine/statistical_tester.py`

---

## SRS Traceability

- FR-A-02 (statistical significance testing): applies the correct test based on pre-registration.
- UC-04 (compare algorithms): p-values and effect sizes enable statistically grounded comparison.
