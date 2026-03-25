# Performance Metric Taxonomy

<!--
STORY ROLE: The "dictionary of measurement". Every metric used anywhere in the system
is defined here and only here. Prevents the silent disagreements that undermine science:
two studies using "success rate" that mean different things.

NARRATIVE POSITION:
  MANIFESTO Principle 12 (Multidimensionality) → Metric Taxonomy → (what we can measure)
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md : which metrics get which statistical treatment
  → docs/03-technical-contracts/01-data-format/08-result-aggregate.md §2.7 : metric names in Result Aggregates MUST match names here
  → docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md §4 : Analyzer interface validates metric names against here

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md Principle 12 : "multiple aspects of performance" — this document is the inventory
  ← docs/02-design/01-software-requirement-specification/SRS.md §4.4 : Measurement & Analysis Engine requirements
  → docs/03-technical-contracts/01-data-format/08-result-aggregate.md §2.7 : ResultAggregate.metrics keys must be valid metric IDs from here
  → docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md §4 : Analyzer.compute_metrics() validates against this taxonomy
  → docs/04-scientific-practice/01-methodology/02-statistical-methodology.md : statistical treatment varies by metric type
  → docs/GLOSSARY.md           : terms used here (Budget, Run, Anytime Performance, etc.) are defined there
  → Docstrings                 : analysis code references metric IDs from this document

METRIC ID FORMAT: [CATEGORY]-[NAME] in UPPER_SNAKE_CASE
  Example: QUALITY-BEST_VALUE_AT_BUDGET, TIME-EVALUATIONS_TO_TARGET
  Metric IDs are the stable identifiers. Metric display names may change; IDs must not.
  Once an ID is assigned and used in any published study, it is permanent.
-->

---

## 1. Taxonomy Overview

The five metric categories below are derived directly from MANIFESTO Principle 12:

> *"We measure multiple aspects of performance: **solution quality at fixed budget**, **time to reach target**, **success probability**, **noise robustness**, **result stability**."*

MANIFESTO Principle 14 adds a sixth dimension:

> *"We report not only final values, but **full performance curves over time** (anytime behavior)."*

| Category | Metric ID Prefix | What it captures | Directly from Principle |
|---|---|---|---|
| QUALITY | `QUALITY-` | Best solution value achieved at a fixed Budget | Principle 12: "solution quality at fixed budget" |
| TIME | `TIME-` | Evaluations or time required to reach a target objective value | Principle 12: "time to reach target" |
| RELIABILITY | `RELIABILITY-` | Probability of success and consistency across Runs | Principle 12: "success probability" |
| ROBUSTNESS | `ROBUSTNESS-` | Sensitivity to noise and parameter variations | Principle 12: "noise robustness", "result stability" |
| ANYTIME | `ANYTIME-` | Full performance curve shape and dynamics | Principle 14: "full performance curves over time" |

**Guidance on scope:** Each category should contain 2–5 defined metrics. More metrics dilute analytical focus; fewer miss important performance aspects. The current set reflects the minimum required by the MANIFESTO.

**Implementation reference format (REF-TASK-0015):**

Each metric definition file ends with an `**Implementation reference:**` field. Once
`corvus_corone/analysis/metrics.py` (IMPL-011) is merged, each placeholder is replaced with:

```
**Implementation reference:** `corvus_corone/analysis/metrics.py` → `compute_<metric_id_lower_snake_case>(<signature>)`
```

Where `<metric_id_lower_snake_case>` replaces `-` with `_` and lowercases the metric ID
(e.g., `QUALITY-BEST_VALUE_AT_BUDGET` → `compute_quality_best_value_at_budget`), and
`<signature>` lists the required inputs matching the metric's **Required inputs** field.
Any implementation PR that changes a compute function MUST update the corresponding
implementation reference in this taxonomy as part of the same PR.

> **`TODO: REF-TASK-0014`** — Review and extend metric definitions once the first real studies
> are conducted. Add domain-specific metrics (e.g., for categorical/mixed search spaces) as they
> are identified. Owner: methodology lead. Acceptance: each new metric follows the definition
> template below and is added to §4 Metric Selection Guide.

---

## Contents

| Section | File | Status |
|---|---|---|
| QUALITY-BEST_VALUE_AT_BUDGET | [02-quality-best-value-at-budget.md](02-quality-best-value-at-budget.md) | ✅ Formal definition |
| TIME-EVALUATIONS_TO_TARGET | [03-time-evaluations-to-target.md](03-time-evaluations-to-target.md) | ✅ Formal definition |
| RELIABILITY-SUCCESS_RATE | [04-reliability-success-rate.md](04-reliability-success-rate.md) | ✅ Formal definition |
| ROBUSTNESS-NOISE_SENSITIVITY | [05-robustness-noise-sensitivity.md](05-robustness-noise-sensitivity.md) | ✅ Formal definition |
| ROBUSTNESS-RESULT_STABILITY | [06-robustness-result-stability.md](06-robustness-result-stability.md) | ✅ Formal definition |
| ANYTIME-ECDF_AREA | [07-anytime-ecdf-area.md](07-anytime-ecdf-area.md) | ✅ Formal definition |
| §3 Standard Reporting Set | [08-standard-reporting-set.md](08-standard-reporting-set.md) | ✅ Formal definition |
| §4 Metric Selection Guide | [09-metric-selection-guide.md](09-metric-selection-guide.md) | ✅ Formal definition |
| §5 Deprecated Metrics | [10-deprecated-metrics.md](10-deprecated-metrics.md) | ✅ Formal definition |
