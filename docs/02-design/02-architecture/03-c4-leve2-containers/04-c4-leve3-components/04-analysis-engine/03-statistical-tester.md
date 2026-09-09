# Statistical Tester

> Container: [Analysis Engine](../../09-analysis-engine.md)
> C3 Index: [01-index.md](01-index.md)

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
    ) -> list[TestResult]:
        """
        Applies the declared tests to pairwise or multi-group metric distributions.
        Returns one TestResult per test application.

        `alpha` has no default here. `TestConfig` is the contract's
        `{ test: str, alpha: float }` (05-analyzer-interface.md 4), carrying the
        values declared in the Study plan before data collection. A significance
        threshold chosen after the data exists is not a threshold, and FR-28
        forbids a silent default for it.
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

2. **Pre-registration guard** — the test must appear in the Study's pre-registered hypotheses, which ADR-021 makes mandatory before a Study can be locked. A test name absent from them raises `ValidationError` naming ADR-021 (FR-29). The one admitted exception is a hypothesis whose `test_type` is `none`, declaring the Study exploratory (FR-31); its results are scoped as exploratory and carry no p-value.

3. **Precondition validation** — before applying any test, validates sample size requirements:
   - Wilcoxon: requires ≥ 6 paired observations.
   - Kruskal-Wallis: requires ≥ 2 observations per group and ≥ 3 groups.

   A failed precondition is never a silent skip and never an error. Either test returns a
   `TestResult` with a null `p_value` and `reason="insufficient_samples"`, stating the
   count it had and the count it needed. The Scope Annotator carries that reason into the
   report's limitations section, where the reader can see which comparison was not made.

4. **Effect size computation** — computes Cliff's delta, required by
   `02-statistical-methodology.md` 4 for every comparison. It is a rank statistic
   computable directly from the two samples, so it needs no optional dependency and is
   never `null` for a pairwise comparison.

   Cliff's delta is pairwise and has no omnibus form. The Kruskal-Wallis result therefore
   carries no `effect_size`; the effect sizes for that family are those of the pairwise
   Wilcoxon tests that follow it, which is what the reader is being asked to interpret.

5. **Multiple comparison correction** — applies the correction method the Study plan
   declares, to the family of p-values, before setting `significant`. FR-16 requires the
   method to be declared and the adjusted p-values to appear in the Researcher Report.
   `02-statistical-methodology.md` 3.6 bounds the choice: Holm-Bonferroni is the default,
   Bonferroni is accepted as a conservative alternative, and BH/FDR is excluded from
   confirmatory analysis. Uncorrected and corrected p-values are both reported.

---

## State

No persistent state. Stateless per invocation.

---

## Implementation Reference

`corvus_corone/analysis_engine/statistical_tester.py`

---

## SRS Traceability

- FR-15 (Level 2, confirmatory): this component is the confirmatory level; a report cannot be produced without it, nor without Levels 1 and 3.
- FR-16 (multiple-testing correction): applied whenever the family holds more than one hypothesis, with adjusted p-values reported.
- UC-04 (compare algorithms): p-values and effect sizes enable statistically grounded comparison.
