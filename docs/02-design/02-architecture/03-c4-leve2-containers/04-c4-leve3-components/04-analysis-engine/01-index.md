# C3: Components — Analysis Engine

> C2 Container: [09-analysis-engine.md](../../09-analysis-engine.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Analysis Engine turns Performance Records into Result Aggregates and statistical conclusions.
It runs in batch after every Run of an Experiment has reached a terminal status (SRS §1.4,
boundary B-02), and it produces all three analysis levels or none: FR-15 makes a report
impossible without exploratory summaries, confirmatory tests and effect sizes together.

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| Metric Dispatcher | Selects the calculator for each requested metric and assembles the Result Aggregate | [`03-metric-taxonomy/`](../../../../../03-technical-contracts/03-metric-taxonomy/01-index.md), [`05-analyzer-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/05-analyzer-interface.md) |
| Statistical Tester | Applies the pre-registered test and computes the effect size that accompanies it | [`05-analyzer-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/05-analyzer-interface.md); `02-statistical-methodology.md` §3 |
| Scope Annotator | Attaches the conditions under which each conclusion holds, which the Analyzer contract makes non-optional | [`05-analyzer-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/05-analyzer-interface.md) |
| Interpolation Strategy | Reconstructs `best_so_far` at an evaluation count that was not logged | ADR-003, ADR-023; [`05-analyzer-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/05-analyzer-interface.md) |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| `analyze`, `compare`, `compute_metrics`, `InterpolationStrategy` | [`02-interface-contracts/05-analyzer-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/05-analyzer-interface.md) |
| Metric identifiers and their computation procedures | [`03-metric-taxonomy/01-index.md`](../../../../../03-technical-contracts/03-metric-taxonomy/01-index.md) |
| Result Aggregate fields | [`01-data-format/08-result-aggregate.md`](../../../../../03-technical-contracts/01-data-format/08-result-aggregate.md) |
| Test selection, correction procedure, pitfalls | `04-scientific-practice/01-methodology/02-statistical-methodology.md` §3 (authoritative for the procedures, per ADR-026) |

The interpolation strategy reads `best_so_far` and never `objective_value`: carrying the raw
result of one evaluation forward would propagate a value worse than the best already seen
(ADR-023). LOCF is exact rather than approximate, which is the argument in ADR-003.
