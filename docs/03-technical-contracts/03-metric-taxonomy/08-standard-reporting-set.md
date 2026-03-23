# §3 Standard Reporting Set

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

Every benchmarking study produced or exported by this system **MUST** include at minimum the following metrics. A researcher may report additional metrics but cannot report fewer. This enforces MANIFESTO Principle 29 (Objectivity over promotion) by preventing metric cherry-picking.

| Metric ID | Why Mandatory |
|---|---|
| `QUALITY-BEST_VALUE_AT_BUDGET` | Every study has a budget; final quality is the most basic outcome measure |
| `RELIABILITY-SUCCESS_RATE` | Reliability matters independently of peak quality; omitting it can hide fragile algorithms |
| `ROBUSTNESS-RESULT_STABILITY` | Spread across Runs is required by MANIFESTO Principle 15 ("not only averages, but spread") |
| `ANYTIME-ECDF_AREA` | Full performance curves required by MANIFESTO Principle 14; this is its scalar summary |

**Enforcement:** The Analyzer interface (`docs/03-technical-contracts/02-interface-contracts/05-analyzer-interface.md` §4) must validate that all four metrics are computed before producing any study report.

**Connection to protocol:** `docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md` Step 5 references this set as the non-negotiable minimum when specifying measurements.

> **`TODO: REF-TASK-0017`** — Consider whether TIME-EVALUATIONS_TO_TARGET should be added to the
> Standard Reporting Set. It requires a pre-specified target $\tau$, which adds planning burden.
> Owner: methodology lead. Acceptance: decision documented in an ADR with MANIFESTO principle rationale.
