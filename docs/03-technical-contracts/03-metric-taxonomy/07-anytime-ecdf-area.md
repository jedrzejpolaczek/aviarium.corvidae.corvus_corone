# ANYTIME-ECDF_AREA

> Index: [01-metric-taxonomy.md](01-metric-taxonomy.md)

**Display name:** Area Under the ECDF Curve

**Definition:** The normalized area under the Empirical Cumulative Distribution Function (ECDF) of best objective values over the evaluation sequence, integrated across the Budget. Captures the full Anytime Performance profile in a single scalar — how quickly and how reliably the algorithm improves over time.

*Formally:* for a single Run, define the anytime best value $b(k) = \min_{i \leq k} f(x_i)$ at evaluation $k$. The ECDF at evaluation $k$ is $F_k(v) = P(b(k) \leq v)$ across Runs. The area under the ECDF integrated over $k \in [1, B]$ and normalized to $[0, 1]$ gives ANYTIME-ECDF_AREA.

> **`TODO: REF-TASK-0016`** — Formalize the exact ECDF area computation procedure, including:
> normalization bounds (use known optimum or empirical bounds?), handling of censored data,
> and aggregation across problems. Owner: methodology lead. Acceptance: two independent
> implementations produce identical results on the same dataset.

**Unit and scale:** Normalized to $[0, 1]$ when bounds are available. Unitless.

**Interpretation:** Higher is better. An algorithm with high ANYTIME-ECDF_AREA reaches good solutions early and consistently across many budget levels.

**Required inputs:** Full sequence of Performance Records (`evaluation_number` and `objective_value`) for all Runs. This is the primary reason Performance Records must be stored at every evaluation, not just at the endpoint.

**Statistical treatment:** Distribution depends on normalization; non-parametric tests generally appropriate. See `docs/04-scientific-practice/01-methodology/02-statistical-methodology.md` §5 (Anytime Analysis).

**When to use:** As a primary metric for any study where optimization dynamics matter — i.e., almost always. This is the most information-dense single metric available because it captures quality, speed, and reliability in one number.

**Limitations:** Requires full Performance Record data. Sensitive to the choice of normalization bounds — results are only comparable across studies that use identical normalization.

**Statistics keys in `AggregateValue.statistics`:**

| Key | Description |
|---|---|
| `mean` | Mean ECDF area across Runs |
| `std` | Standard deviation across Runs |
| `median` | Median across Runs |
| `q25` | 25th percentile |
| `q75` | 75th percentile |

**Related metrics:**
- *Complements:* All other metrics — ANYTIME-ECDF_AREA is a summary; other metrics provide interpretable components
- *Recommended as default primary metric* for most research questions
