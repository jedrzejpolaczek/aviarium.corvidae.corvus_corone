# ADR-024: ECDF_AREA Integration Domain

<!--
STORY ROLE: Fixes a normalisation defect in the ANYTIME-ECDF_AREA procedure. The formula
divided by the Budget while integrating over a domain of width Budget minus one, so the
metric could not reach its stated upper bound and the best value of every Run was excluded
from the sum entirely.

CONNECTS TO:
  → docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md : the procedure
  → adr-007-ecdf-area-normalization.md : the value-axis bounds, unchanged by this ADR
  → adr-023-performance-record-value-fields.md : the field the reconstruction reads
-->

---

**Status:** Accepted

**Date:** 2026-09-09

**Deciders:** Core maintainers, methodology lead

---

## Context

The ANYTIME-ECDF_AREA procedure normalises on two axes. ADR-007 fixed the value axis: the
bounds are the empirical `y_max` and `y_min` of the cell. The evaluation axis was fixed in the
procedure document itself, and was fixed wrongly.

The sum runs over `i = 1 .. m-1`, that is over the intervals between consecutive grid points
from `k_1 = 1` to `k_m = B`. Those intervals have a combined width of `B - 1`. The divisor is
`B · (y_max − y_min)`. The two disagree.

Two consequences follow, both verified against the procedure's own reference case.

**The metric cannot reach 1.** Its maximum is `(B − 1) / B`. With the reference case's budget of
4 the ceiling is 0.75, and the document states "= 1 if every Run achieves `y_min` from evaluation
1". For a budget of 10 the ceiling is 0.9. The systematic compression depends on the budget, so
two studies with different budgets are not comparable even in principle, which is a stronger
restriction than the cross-study incomparability ADR-007 already documents.

**The final value of every Run is discarded.** The document explains this deliberately: row
`k = B` "does not contribute to the sum because it is the right endpoint of the last interval".
For a metric whose purpose is to reward reaching good values, excluding the best value each Run
ever attained is not a rounding detail.

Both boundary cases the document states are additionally unreachable for a separate reason.
"Every Run achieves `y_min` from evaluation 1" forces `y_max = max_r b_r(1) = y_min`, and "every
Run never improves from `y_max`" forces `y_min = y_max`; ADR-007 makes the metric undefined in
both cases.

---

## Decision

**The integration domain is the whole Budget, treated as `B` unit-width steps.**

Under LOCF the reconstructed curve is a step function whose value at evaluation `k` holds for
that evaluation. Evaluation `k` therefore occupies the half-open interval `[k, k+1)`, and the
domain is `[1, B+1)`, of width `B`. The sum runs over all `m` grid points, the width of the last
interval being `B + 1 − k_m = 1`:

```
ECDF_AREA = 1 / (B · (y_max − y_min))
            · Σ_{i=1..m} w_i · (y_max − b̄(k_i))

where w_i = k_{i+1} − k_i  for i < m
      w_m = B + 1 − k_m    ( = 1 )
```

The divisor is unchanged. The per-Run formula in §6 changes identically.

**The reference test case value changes from `0.21875` to `0.4375`.** Any implementation that
reproduces the old value is now non-compliant.

**The two boundary claims are withdrawn** and replaced by a statement of what the extremes mean
without asserting they are attainable.

---

## Rationale

The step-function reading is the one already used everywhere else in the procedure. §1 defines
`b_r(k)` at every evaluation `k` in `1 .. B`, not on the intervals between them. §5 calls the sum
"exact, not an approximation" precisely because the curve is piecewise constant. A piecewise
constant function defined at `B` points, each holding for one evaluation, integrates over a
domain of width `B`. Summing only the gaps between points contradicts the reading that makes the
sum exact in the first place.

It also fixes the substantive defect rather than the arithmetic one. The alternative, changing
the divisor to `B − 1`, would make the range attainable but would still throw away `b̄(B)`, so an
algorithm that found its best solution on the final evaluation would receive no credit for it.

The reference value is recomputed here so that the change is checkable:

| k | b̄(k) | w | y_max − b̄(k) | contribution |
|---|---|---|---|---|
| 1 | 1.00 | 1 | 0.00 | 0.00 |
| 2 | 0.90 | 1 | 0.10 | 0.10 |
| 3 | 0.75 | 1 | 0.25 | 0.25 |
| 4 | 0.65 | 1 | 0.35 | 0.35 |

Sum = 0.70, divisor = `4 × 0.4` = 1.6, ECDF_AREA = **0.4375**.

Sanity check on the ceiling: if every Run sat at `y_min` throughout, each contribution would be
`0.4` and the sum `1.6`, giving exactly 1. The range is now attainable at the top.

**Trade-off accepted:** the metric is not comparable with any value computed under the previous
formula. No study has been run, so no published value exists.

---

## Alternatives Considered

### Change the divisor to `B − 1`

**Description:** Keep the sum over `i = 1 .. m-1` and divide by `(B − 1) · (y_max − y_min)`.

**Why rejected:** Restores the range but keeps the last grid point out of the sum, so the best
value each Run achieved never enters the metric. It also breaks for `B = 1`, where the divisor
is zero.

---

### Leave the formula and correct only the documented range

**Description:** State that the metric lies in `[0, (B−1)/B]` and move on.

**Why rejected:** Makes the metric budget-dependent by construction, so a study at budget 50 and
one at budget 500 produce values on different scales for identical behaviour. That defeats the
purpose of normalising at all.

---

## Consequences

**Positive:**

- The metric attains its full `[0, 1]` range and stops being budget-scaled.
- The final, best value of every Run contributes to the score.
- The reference case becomes a real conformance test rather than a test of a broken formula.

**Negative / Trade-offs:**

- The reference value changes, so the procedure document and any implementation must be updated
  together.
- ADR-007's cross-study incomparability warning still stands; this ADR does not make values
  comparable across studies, it only removes a second, avoidable source of incomparability.

**Risks:**

- **Risk:** An implementation is written against the old reference value found in an older
  revision of the document.
  **Mitigation:** the procedure document states the ADR that set the value, and the value is
  covered by the acceptance test strategy.

---

## Related Documents

| Document | Relationship |
|---|---|
| `docs/03-technical-contracts/03-metric-taxonomy/07-anytime-ecdf-area.md` | Procedure and reference value changed by this ADR |
| `adr-007-ecdf-area-normalization.md` | Value-axis bounds, unchanged |
| `adr-003-anytime-curve-interpolation.md` | LOCF, the step function this ADR integrates |
| `adr-023-performance-record-value-fields.md` | The field the reconstruction reads |
