# §4 Metric Selection Guide

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

Use this guide when specifying measurements in Step 5 of the Benchmarking Protocol (`docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md`). Metric selection must happen **before** data collection (MANIFESTO Principle 16) to prevent post-hoc cherry-picking.

### Research question: "Which algorithm finds the best solutions given a fixed budget?"
- **Primary:** `QUALITY-BEST_VALUE_AT_BUDGET`
- **Required alongside:** `ROBUSTNESS-RESULT_STABILITY` (stability of that quality), `ANYTIME-ECDF_AREA` (dynamics)
- **Discouraged as sole metric:** `QUALITY-BEST_VALUE_AT_BUDGET` alone, without spread measures — violates Principle 15

### Research question: "Which algorithm reaches acceptable solutions fastest?"
- **Primary:** `TIME-EVALUATIONS_TO_TARGET`, `ANYTIME-ECDF_AREA`
- **Required alongside:** `RELIABILITY-SUCCESS_RATE` (what fraction of Runs reach the target at all)
- **Note:** Target $\tau$ must be pre-specified and ecologically justified

### Research question: "Which algorithm is most reliable and consistent?"
- **Primary:** `RELIABILITY-SUCCESS_RATE`, `ROBUSTNESS-RESULT_STABILITY`
- **Required alongside:** `QUALITY-BEST_VALUE_AT_BUDGET` (context for what level of quality is reliable)

### Research question: "How do algorithms perform under noisy evaluations?"
- **Primary:** `ROBUSTNESS-NOISE_SENSITIVITY`, `RELIABILITY-SUCCESS_RATE`
- **Required:** Problem Instances must include matched noisy/noiseless variants — must be designed into the Study
- **Required alongside:** `QUALITY-BEST_VALUE_AT_BUDGET` on noiseless instances as baseline

### Research question: "How do algorithms compare across different budget levels?"
- **Primary:** `ANYTIME-ECDF_AREA`, full ECDF curves at multiple budget checkpoints
- **Requires:** Full Performance Record data for all Runs
- **Note:** This is the only question type where a single metric (`ANYTIME-ECDF_AREA`) is nearly self-sufficient

> **`TODO: REF-TASK-0018`** — Add research question archetypes as they emerge from actual studies.
> Each archetype should link to a tutorial in `docs/06_tutorials/` demonstrating it end-to-end.
> Owner: methodology lead. Acceptance: each new archetype has a corresponding tutorial.
