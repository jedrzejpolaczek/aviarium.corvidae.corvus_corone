# Hyperparameter Optimization Algorithm Benchmarking Manifesto

## Preamble

We stand at the threshold of creating a new benchmarking system for hyperparameter optimization algorithms. This system is meant to serve the discovery of truth about algorithm performance, not their promotion. It should support science, not competition. It should build knowledge, not rankings.

Drawing inspiration from experiences in optimization, machine learning, and design of experiments, we formulate the following values and principles that will form the foundation of our system. 
> Note: This document draws primarily from "Benchmarking in Optimization: Best Practice and Open Issues" (Bartz-Beielstein et al., 2020), in the interest of full transparency.

---

## Values

Through our work on the hyperparameter optimization algorithm benchmarking system, we have come to value:

1. **Understanding algorithms** over ranking them by a single metric.
2. **Problem representativeness** over ease of achieving results.
3. **Research reproducibility** over speed of publication.
4. **Experimental space** over single metrics.
5. **Transparency of assumptions** over simplified conclusions.
6. **System adaptability** over rigid standards.

That is, while there is value in the items on the right, we value the items on the left more.

---

## Principles

Guided by the above values, we adopt the following principles:

---

| # | Principle | Category | Key Focus | Description |
|---|-----------|----------|-----------|-------------|
| 1 | Clarity of purpose precedes experiment | Purposefulness | Define research questions before comparing | Every benchmarking study begins with a precise definition of the research question. We do not compare algorithms for the sake of comparison – we seek answers to specific questions about algorithm behavior, performance, and applicability. |
| 2 | Multiple perspectives instead of single ranking | Purposefulness | Investigate context-dependent performance | We abandon the search for the "best algorithm". Instead, we investigate: which algorithms work well in which contexts, why this happens, and what are the limits of their applicability. |
| 3 | Understanding before generalizing | Purposefulness | Limit conclusions to tested instances | Conclusions about algorithm performance refer exclusively to actually tested problem instances and configurations. Every extrapolation is explicitly marked and carefully justified. |
| 4 | Problem representativeness | Problems | Reflect real optimization challenges | Benchmark sets reflect real challenges in hyperparameter optimization. Synthetic problems serve to understand mechanisms, they do not replace real problems. |
| 5 | Diversity of characteristics | Problems | Cover wide spectrum of problem features | The problem set covers a wide spectrum of characteristics: different dimensions of search spaces, different objective function landscapes, different noise levels, different computational budgets, different types of hyperparameter interdependencies. |
| 6 | Evolution of problem sets | Problems | Regular updates, prevent overfitting | Benchmark sets are regularly updated and extended. We document the history of changes to enable long-term comparisons, but prevent overfitting of algorithms to static sets. |
| 7 | Instance transparency | Problems | Specify all problem characteristics | For each problem instance we clearly specify: dimension, variable types, computational budget, presence of noise, known optimum or best solution, landscape characteristics (if known). |
| 8 | Precision of description | Algorithms | Distinguish concepts, instances, implementations | We distinguish algorithms (concepts), algorithm instances (specific configurations), and implementations (code). We report each element separately and with full precision. |
| 9 | Portfolio diversity | Algorithms | Include algorithms from different families | Comparisons include algorithms from different families: random methods, Bayesian, evolutionary, gradient-based (if possible), specialized heuristics. This allows us to discover strengths of different paradigms. |
| 10 | Configuration fairness | Algorithms | Test each algorithm in best reasonable setup | We test each algorithm in its best reasonable configuration for the given problem class. We avoid comparing poorly configured algorithms with well-tuned ones. |
| 11 | Sensitivity documentation | Algorithms | Report robustness to parameter changes | We investigate and report algorithm robustness to parameter changes. Stable algorithms may be preferred over sensitive ones, even with slightly worse peak performance. |
| 12 | Multidimensionality of measurement | Measurement & Analysis | Measure multiple performance aspects | We measure multiple aspects of performance: solution quality at fixed budget, time to reach target, success probability, noise robustness, result stability. |
| 13 | Three-level analysis | Measurement & Analysis | Exploratory, confirmatory, practical significance | We conduct each analysis in three steps: Exploratory data analysis (visualization, pattern recognition), Confirmatory analysis (statistical tests, formal conclusions), Practical significance analysis (effect size, practical utility of differences). |
| 14 | Full performance curves | Measurement & Analysis | Report anytime behavior, not just endpoints | We report not only final values, but full performance curves over time (anytime behavior). This allows understanding optimization dynamics and behavior at different budgets. |
| 15 | Statistical rigor | Measurement & Analysis | Use appropriate methods, report uncertainty | We apply appropriate statistical methods to the nature of the data. We report not only averages, but also spread, quantiles, success probabilities. We correct for multiple testing when necessary. |
| 16 | Planning precedes execution | Experimental | Design experiments before collecting data | Experimental design is consciously planned before data collection. We specify: number of repetitions, resource allocation method, stopping criteria, result aggregation methods. |
| 17 | Resource efficiency | Experimental | Maximize knowledge at minimal cost | We design experiments to maximize knowledge at minimal computational cost. We use intelligent experimental designs, not brute-force grid searches. |
| 18 | Independence of runs | Experimental | Control and document randomness sources | Each algorithm run is independent. We document and control sources of randomness (random generator seeds). |
| 19 | Full reproducibility | Reproducibility | Provide complete code, data, procedures | Every benchmarking study is fully reproducible. We provide: complete code, exact library versions, input data, random seeds, result processing procedures. |
| 20 | Open data and code | Reproducibility | Public availability in standard formats | All experimental data, algorithm code, and analysis scripts are publicly available in standardized formats. We support result reuse and verification. |
| 21 | Artifact versioning | Reproducibility | Version all components, document dependencies | Every version of problem sets, algorithms, and results is unambiguously versioned. We document dependencies between versions. |
| 22 | Long-term availability | Reproducibility | Stable repositories, open formats | Data and code are stored in stable, long-term repositories. We use open and well-documented formats. |
| 23 | Visualization enriches numbers | Presentation | Combine numerical and visual results | We present results both numerically and visually. Good visualization often says more than tables of numbers. |
| 24 | Transparency of limitations | Presentation | Communicate assumptions and context | We clearly communicate limitations and assumptions of our studies. Each conclusion includes context: for which problems, algorithms, and conditions it is valid. |
| 25 | Accessibility for different audiences | Presentation | Multiple levels of detail | We present results at different levels of detail: summaries for practitioners, details for researchers, raw data for analysts. |
| 26 | System interoperability | Ecosystem | Compatibility with existing platforms | The benchmarking system is compatible with existing platforms (COCO, Nevergrad, IOHprofiler). We support common data formats and result exchange. |
| 27 | Community development | Ecosystem | Evolve with contributions | The system evolves with community contributions. We encourage: adding new problems, algorithm implementations, improving analytical tools. |
| 28 | Education and support | Ecosystem | Provide tutorials, examples, guidance | The system serves not only research, but also education. We provide: usage examples, tutorials, result interpretations, guidance for beginners. |
| 29 | Objectivity over promotion | Ethical & Scientific | Serve evaluation, not marketing | Benchmarking serves objective algorithm evaluation, not their marketing. We avoid cherry-picking results and selective reporting. |
| 30 | Acknowledgment of NFL limitations | Ethical & Scientific | Respect No Free Lunch theorems | We respect "No Free Lunch" theorems. There is no best algorithm for all problems. The goal is to map which algorithms work well for which problem classes. |
| 31 | Fairness in comparisons | Ethical & Scientific | Equal conditions, transparent advantages | We compare algorithms under equal conditions. If one algorithm has additional problem knowledge, this is explicitly indicated. |
| 32 | Contribution to theory and practice | Ethical & Scientific | Serve both research and applications | Benchmarking results serve both theory development (inspiration for mathematical analyses) and practice (algorithm selection for applications). |

### Category Legend

The nine categories above are based on the fundamental aspects of benchmarking identified in "Benchmarking in Optimization: Best Practice and Open Issues" (Bartz-Beielstein et al., 2020):

- **Purposefulness** - Derived from "Goals": Why we perform benchmarking studies and what questions we seek to answer
- **Problems** - Direct from paper: How to select and characterize appropriate problem instances for testing
- **Algorithms** - Direct from paper: How to choose and configure algorithm portfolios for comparison
- **Measurement & Analysis** - Synthesized from "Performance" and "Analysis": How to measure and evaluate algorithm performance
- **Experimental** - Derived from "Experimental Design": How to design rigorous and efficient experiments
- **Reproducibility** - Direct from paper: How to ensure scientific validity and long-term impact
- **Presentation** - Direct from paper: How to communicate results effectively to different audiences
- **Ecosystem** - Extended concept: Interoperability with existing platforms and community-driven development
- **Ethical & Scientific** - Extended concept: Objectivity, fairness, and acknowledgment of theoretical limitations (e.g., No Free Lunch theorems)

The first seven categories derive from the paper's eight core aspects — Measurement & Analysis combines 'Performance' and 'Analysis' into one. The last two categories (Ecosystem and Ethical & Scientific) extend the framework to address modern collaborative and ethical considerations in benchmarking practice.

---

## Anti-patterns

The following practices are explicitly rejected by this system. They represent the ways a benchmarking system most commonly undermines its own scientific purpose — each is the direct inverse of one or more Principles above.

Anti-patterns AP-1 and AP-3 through AP-7 drive the design exclusions listed in
`docs/02-design/02-architecture/02-c4-leve1-context/01-c4-l1-context/01-c1-context.md` (Explicit Scope Exclusions).
AP-2 is a scientific validity constraint on problem selection; it does not map to a design exclusion
(the system cannot prevent researchers from passing biased inputs) but must be stated here because
CONST-SCI constraints reference it.

| # | Anti-pattern | Inverse of | Description |
|---|---|---|---|
| AP-1 | Global algorithm rankings and "best algorithm" declarations | Principles 2, 3, 30 | Producing or displaying performance-independent rankings, leaderboards, or "best algorithm" recommendations. Such outputs make claims beyond what the tested problem set can support and serve algorithm promotion rather than scientific understanding. No Free Lunch theorems make universal rankings mathematically invalid. |
| AP-2 | Biased or cherry-picked problem selection | Principles 4, 5, 6 | Constructing or selecting problem sets that are not representative of real optimization challenges, or that are chosen specifically to favor certain algorithms over others. Any conclusion drawn from a biased problem set is scientifically invalid regardless of the rigor applied to the rest of the study. |
| AP-3 | Competition-style framing and scoring | Principles 1, 2 | Structuring a benchmarking study as a competition — with league tables, prize optimizations, or "winning" algorithm declarations — instead of as a scientific inquiry into context-dependent performance. Shifts the goal from understanding algorithm behavior to determining a winner, producing promotion rather than knowledge. |
| AP-4 | Opaque analysis pipelines | Principles 13, 15, 19 | Implementing analysis workflows that cannot be independently inspected, reproduced, or understood by the user. Every statistical test, aggregation, and visualization step must be transparent so that conclusions can be verified and contested. Black-box analysis violates the reproducibility requirements of Principles 19–22. |
| AP-5 | Proprietary or closed data formats | Principles 20, 22, 26 | Storing or producing data in formats that prevent interoperability with the broader benchmarking ecosystem (COCO, IOHprofiler, Nevergrad) or that require proprietary software to read. Closed formats isolate results, break long-term availability guarantees, and contradict the open-data mandate of Principles 20 and 22. |
| AP-6 | Marketing-oriented result presentation | Principles 24, 29 | Generating reports or summaries that emphasize positive findings, downplay limitations, or omit scope conditions — serving algorithm promotion rather than scientific communication. Every conclusion must be accompanied by the conditions under which it holds; cherry-picked highlights are not benchmarking results. |
| AP-7 | Automated algorithm selection as a substitute for researcher judgment | Principles 1, 3, 25 | Making algorithm selection recommendations or decisions on behalf of the user — treating benchmarking output as a recommendation engine rather than as evidence. The system produces structured evidence that a researcher interprets; it does not decide which algorithm a practitioner should use. |

---
