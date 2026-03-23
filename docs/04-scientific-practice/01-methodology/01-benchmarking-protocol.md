# Benchmarking Study Protocol

<!--
STORY ROLE: The "recipe book". A researcher follows this to design and execute a valid study.
Operationalizes the principles from MANIFESTO into a concrete workflow.
This document is what a researcher reads BEFORE touching any code.

NARRATIVE POSITION:
  MANIFESTO (values/principles) + SRS (requirements) + Methodology (how to analyze)
  → Benchmarking Protocol → (step-by-step how to run a study)
  → Tutorials: each tutorial should walk through one or more steps of this protocol

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md Principles 1–3, 4–7, 8–11, 16–18 : each step implements these principles
  ← docs/02-design/01-software-requirement-specification/SRS.md §3   : use case UC-01 maps to this protocol
  → docs/04_scientific_practice/methodology/statistical-methodology.md : Steps 7–8 (Analyze, Report) delegate to that guide
  → docs/03-technical-contracts/metric-taxonomy.md §4 : Step 5 (Specify metrics) uses the selection guide there
  → docs/03-technical-contracts/interface-contracts.md : Steps 3–4 (configure algorithms/problems) must follow contracts
  → docs/03-technical-contracts/data-format.md    : every step produces artifacts conforming to schemas there
  → docs/GLOSSARY.md        : exact terms used throughout — Algorithm Instance, Problem Instance, Study, Run, Budget
  → docs/05_community/TASKS.md : each step in a real study should correspond to trackable tasks

USAGE NOTE: This protocol is not a rigid checklist but a structured guide.
Steps may overlap in practice, but the sequence matters for scientific validity —
particularly: hypotheses must be specified (Step 2) BEFORE data is collected (Step 4).
-->

---

## Protocol Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRE-REGISTRATION GATE                        │
│  Steps 1–5 must be fully committed BEFORE Step 6 begins.       │
│  Once execution starts, hypotheses and metrics are locked.      │
└─────────────────────────────────────────────────────────────────┘

Step 1: Formulate Research Question
    ↓
Step 2: Pre-Register Hypotheses  ← hypotheses locked here
    ↓
Step 3: Select Problem Instances
    ↓
Step 4: Configure Algorithm Portfolio
    ↓
Step 5: Specify Measurements  ← metrics and budget locked here
    ↓
══════════════════════ PRE-REGISTRATION GATE ══════════════════════
    ↓
Step 6: Execute the Experiment (data collection)
    ↓
Step 7: Analyze Results  →  statistical-methodology.md (three-level)
    ↓
Step 8: Scope and Report Conclusions
    │
    └──► Post-hoc observations from Step 7 feed back to Step 1
         of a FUTURE study (never retrofit into the current one)
```

**The sequencing constraint is scientific, not bureaucratic.** Any change to hypotheses, metrics, or problem selection after data collection begins invalidates the confirmatory analysis and reduces the study to exploratory work. This is why the system enforces the gate at the data format level: the Study record's hypotheses and experimental design fields are locked when the Experiment begins.

---

## Step 1: Formulate the Research Question

*Implements MANIFESTO Principles 1, 2, 3.*

A valid Research Question (→ GLOSSARY) must contain four elements:

1. **The algorithms or algorithm families** being compared (e.g., "Bayesian optimization methods vs. evolutionary strategies")
2. **The problem characteristics** of interest — not a specific problem set yet, but the class (e.g., "on high-dimensional, noisy search spaces with budget ≤ 200 evaluations")
3. **The performance dimension** being measured at high level (e.g., "solution quality and reliability") — specific metrics are chosen in Step 5
4. **The scope boundary** — what types of problems or conditions are explicitly excluded

**Validity test:** Before proceeding to Step 2, answer these questions:
- Can you state a result that would *support* your hypothesis and a different result that would *refute* it? If no — the question is not falsifiable.
- Is the scope narrow enough that a conclusion will be meaningful? If "all problems" — too broad.
- Does this question address a gap not covered by existing studies in the literature?

**Anti-patterns that invalidate the Research Question at this step:**

| Invalid question | Why invalid | MANIFESTO violation |
|---|---|---|
| "Which algorithm is best?" | No scope; presupposes a universal winner; violates NFL | Principles 2, 30 |
| "Does Algorithm X work?" | Not comparative; not falsifiable | Principle 1 |
| "Let's try Algorithm X on our benchmark" | No research question; this is exploration, not benchmarking | Principle 1 |
| "Which algorithm wins our competition?" | Competition framing; result serves promotion, not understanding | Anti-pattern 3, Principle 29 |

**Output:** A written Research Question stored in the Study record's `research_question` field. The question should fit in 2–4 sentences. Vagueness at this step cascades into invalid analysis at Step 7.

→ Study record format: `docs/03-technical-contracts/data-format.md` §2.3

---

## Step 2: Pre-Register Hypotheses

*Implements MANIFESTO Principle 16 (planning precedes execution).*

**Why this step must come before data collection:**

Hypotheses selected after seeing data are observations, not predictions. They are statistically invalid as confirmatory tests — see `docs/04_scientific_practice/methodology/statistical-methodology.md` §7, Pitfall 1 (Post-hoc hypothesis selection). MANIFESTO Principle 16 is explicit: experimental design is consciously planned before data collection.

**What to specify for each hypothesis:**

1. **H₀ (null hypothesis):** The statement to be tested formally — typically a statement of no difference (e.g., "There is no significant difference in `QUALITY-BEST_VALUE_AT_BUDGET` between Algorithm A and Algorithm B on problem class C")
2. **H₁ (alternative hypothesis):** The directional or non-directional alternative (e.g., "Algorithm A achieves better `QUALITY-BEST_VALUE_AT_BUDGET` than Algorithm B")
3. **Statistical test planned:** Which test will be used — to be filled using the test selection guide in `docs/04_scientific_practice/methodology/statistical-methodology.md` §3 (`TODO: REF-TASK-0020`)
4. **Significance threshold α:** Typically 0.05, but must be stated explicitly
5. **Multiple testing correction:** If more than one hypothesis is tested — state which correction method (`TODO: REF-TASK-0020`)
6. **Metrics involved:** Which metric IDs from `docs/03-technical-contracts/metric-taxonomy.md` are used to evaluate this hypothesis

**System enforcement:**

Pre-registered hypotheses are stored in the Study record before the Experiment begins. The Analyzer (`docs/03-technical-contracts/interface-contracts.md` §4) only tests hypotheses found in this pre-registered list in Level 2 (Confirmatory) analysis. Any hypothesis tested outside this list is automatically labeled "post-hoc / exploratory" in the output and cannot appear in the confirmatory section of the report.

**Exploratory analysis is still valuable — but it is separate:**

Observations from Level 1 analysis may suggest new hypotheses. These are valid and should be documented — but they must be pre-registered in a *future* Study to receive confirmatory status. Never retrofit a post-hoc observation into the current Study's confirmed hypotheses.

→ Storage: `docs/03-technical-contracts/data-format.md` §2.3 `pre_registered_hypotheses` field

---

## Step 3: Select Problem Instances

*Implements MANIFESTO Principles 4, 5, 6, 7.*

**Goal:** Select a set of Problem Instances (→ GLOSSARY) that represent the problem class named in the Research Question — without bias toward or against any specific algorithm.

**Selection criteria:**

| Criterion | What to check | MANIFESTO Principle |
|---|---|---|
| Representativeness | Do the selected instances reflect the real HPO challenges named in the Research Question? | Principle 4 |
| Diversity | Do instances span the characteristics relevant to the question: dimensions, noise levels, landscape types, variable types, budget scales? | Principle 5 |
| Non-overfitting | Are any of these instances known to favor a specific algorithm? If yes — include counterbalancing instances or document the limitation explicitly | Principle 6, 29 |
| Feasibility | Can the full Study (all instances × all algorithms × required repetitions) be completed within available compute? | Principle 17 |
| Known optima | For at least some instances, is the optimum or a reliable best-known value available? (Required for `TIME-EVALUATIONS_TO_TARGET`) | Principle 7 |

**Instance transparency (Principle 7):** For each selected Problem Instance, the record must specify:
- Dimension of the search space
- Variable types (continuous, integer, categorical, mixed)
- Computational Budget
- Noise level (deterministic or stochastic, and its characterization)
- Known optimum or best-known solution, if available
- Landscape characteristics, if known (modality, separability, etc.)

→ These fields are documented in `docs/03-technical-contracts/data-format.md` §2.1.

**Documentation per selected instance:** Record why this instance was selected (representativeness argument) and which diversity characteristics it contributes. This justification is stored in the Problem Instance's `provenance` metadata.

**The critical anti-pattern:** Selecting problems where the researcher's preferred algorithm is already known to perform well — and avoiding problems where it is known to perform poorly. This is a form of cherry-picking that violates Principle 29 (Objectivity over promotion). Even if unintentional, it produces biased conclusions.

> **`TODO: REF-TASK-0021`** — Define minimum diversity requirements once the Problem Repository
> is designed: minimum number of instances per study, required spread across characteristics.
> Owner: methodology lead. Acceptance: constraints documented in SRS §4.1 and enforced by
> the system when validating a Study record.

---

## Step 4: Configure Algorithm Portfolio

*Implements MANIFESTO Principles 8, 9, 10, 11.*

**Goal:** Select Algorithm Instances (→ GLOSSARY) that are relevant to the Research Question and configure each one fairly — not to give any algorithm an artificial advantage or disadvantage.

**What "best reasonable configuration" means (Principle 10):**
- Not the absolute best configuration achievable (finding that would itself require a benchmarking study — a separate one)
- The configuration a knowledgeable practitioner would choose for this problem class, based on algorithm documentation and domain knowledge
- Explicitly documented and justified — arbitrary defaults are not acceptable

**Portfolio diversity (Principle 9):** Where the Research Question permits, include Algorithm Instances from different families to enable cross-paradigm comparison. The three-way distinction from Principle 8 must be maintained for every Algorithm Instance:

| Required documentation | Where stored |
|---|---|
| Algorithm concept (family name, original paper reference) | Algorithm Instance record |
| Algorithm Instance (all configuration parameter values with justification) | Algorithm Instance record |
| Implementation (library name, exact version, code revision reference) | Algorithm Instance record |

→ Full record format: `docs/03-technical-contracts/data-format.md` §2.2

**Configuration fairness checklist:**
- [ ] All Algorithm Instances receive exactly the same computational Budget
- [ ] No Algorithm Instance has been pre-tuned on Problem Instances that appear in this Study
- [ ] Every configuration choice is documented with a justification (not "default settings")
- [ ] If an algorithm makes assumptions about the problem type (e.g., "assumes continuous space"), these assumptions are recorded in `known_assumptions`

**Sensitivity documentation (Principle 11):**

For Algorithm Instances with important configuration parameters, a sensitivity check should accompany the main study — not replace it. This means: vary one key parameter across a reasonable range and report how much performance changes. An algorithm that is highly sensitive to its configuration requires stronger justification for the chosen setting.

This sensitivity check is not part of the core Experiment but should be included in the study report. It makes the configuration justification defensible.

> **`TODO: REF-TASK-0022`** — Define the sensitivity documentation format once interface contracts
> are designed. Owner: methodology lead. Acceptance: the Algorithm Instance record schema includes
> a `sensitivity_report` field or linked document.

---

## Step 5: Specify Measurements

*Implements MANIFESTO Principles 12, 14, 16 (planning precedes execution).*

**Metric selection must happen before data collection.** Choosing metrics after seeing the data enables cherry-picking — selective reporting that violates MANIFESTO Principle 29 (Objectivity over promotion). The metric list is locked when the Experiment begins, along with the rest of the Study record.

**Required metrics — Standard Reporting Set:**

All four metrics from `docs/03-technical-contracts/metric-taxonomy.md` §3 must be included in every study. No exceptions:

| Metric | Why mandatory |
|---|---|
| `QUALITY-BEST_VALUE_AT_BUDGET` | The most basic outcome measure — every study has a budget |
| `RELIABILITY-SUCCESS_RATE` | Reliability matters independently of peak quality |
| `ROBUSTNESS-RESULT_STABILITY` | Principle 15: report spread, not only averages |
| `ANYTIME-ECDF_AREA` | Principle 14: full performance curves, not only endpoints |

**Optional additional metrics:**

Use the Metric Selection Guide (`docs/03-technical-contracts/metric-taxonomy.md` §4) to select metrics appropriate for your Research Question type. For each additional metric, document *why* it was chosen — metric selection that cannot be justified from the Research Question is a sign of post-hoc cherry-picking and will be flagged in the Confirmatory analysis step.

**Performance curve sampling strategy:**

Specify at which evaluation counts Performance Records will be stored during each Run. This must be decided now — recording more data is always safe, but recording fewer snapshots may prevent anytime analysis later and cannot be retroactively corrected. The sampling strategy is stored in the Study record and locked before execution begins. See [ADR-002](../../02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md) for the full strategy specification.

The following fields must be set in the Study record at this step:
- `sampling_strategy` — e.g., `log_scale_plus_improvement` (the default)
- `log_scale_schedule` — base points and multiplier (default: `{1,2,5} × 10^i`)
- `improvement_epsilon` — minimum improvement to trigger a record; `null` for strict inequality (see [ADR-004](../../02-design/02-architecture/01-adr/adr-004-improvement-sensitivity-threshold.md))

→ Study schema: `docs/03-technical-contracts/01-data-format.md` §2.3
→ PerformanceRecord schema: `docs/03-technical-contracts/01-data-format.md` §2.6

**Budget specification:**

State the exact evaluation budget for all Algorithm Instances. If different Algorithm Instances receive different budgets — for example, to normalize wall-clock time across algorithms with different per-evaluation costs — document and justify this explicitly. An unjustified differential budget is a configuration fairness violation (MANIFESTO Principle 10) and must appear in the study's limitations section.

**Output of this step:**

A completed and locked Study record containing:
- `experimental_design.stopping_criteria`
- `pre_registered_hypotheses` (from Step 2)
- `problem_instances` and `algorithm_instances` (from Steps 3–4)
- `sampling_strategy`, `log_scale_schedule`, `improvement_epsilon` (from this step)
- The metric list, which becomes the `AnalysisConfig` when Step 7 triggers analysis

→ Study record format: `docs/03-technical-contracts/data-format.md` §2.3

---

## Step 6: Execute the Experiment

<!--
  At this point, the Study record is complete and locked.
  No changes to problems, algorithms, metrics, or hypotheses after execution begins.

  Execution checklist:
    - Seeds are assigned by the Runner, not chosen by the researcher
    - Each Run is executed independently (no shared state)
    - The full execution environment is recorded → data-format.md §2.4 execution_environment
    - Failures are logged, not silently ignored
    - All PerformanceRecords are stored with the sampling frequency from Step 5

  What to do if runs fail:
    - Investigate the cause — do not simply discard and rerun without documentation
    - If a Run fails due to a bug, fix the bug and rerun ALL runs (not just the failed one)
    - If failure is a known limitation of an algorithm on this problem type, document it
    - Do not silently exclude failed runs from analysis without reporting the failure rate

  Checkpointing:
    Long studies should use the Runner's resume capability
    → specs/interface-contracts.md §3 resume()

  → MANIFESTO Principles 16, 17, 18
  → SRS NFR-REPRO (full execution environment recorded)
-->

---

## Step 7: Analyze Results

*Implements MANIFESTO Principles 12, 13, 14, 15.*

**This step does not permit revisiting or modifying Steps 1–6.** The Study plan is locked. The analysis follows the pre-registered hypotheses.

Delegate the full analysis to `docs/04_scientific_practice/methodology/statistical-methodology.md`. The required sequence is the three-level framework (§1 of that document):

**Level 1 — Exploratory Data Analysis:**
Visualize all Run data and Performance curves. Identify anomalies (failed Runs, outliers) and document them. Produce observations — not conclusions. If anomalies indicate a bug or setup error, investigate before proceeding; do not silently exclude problematic Runs.

**Level 2 — Confirmatory Analysis:**
Test **only the hypotheses pre-registered in Step 2**. Do not add or remove hypotheses based on what Level 1 showed. Apply the statistical tests specified in Step 2, with the correction method specified there.

Any observation from Level 1 that suggests an untested hypothesis must be documented as "post-hoc / exploratory" — it is not a confirmatory finding in this Study.

**Level 3 — Practical Significance:**
For every hypothesis where Level 2 produces a statistically significant result, compute the Effect Size (→ GLOSSARY). Report the Effect Size alongside the p-value. A result is only actionable if both levels agree it is significant.

**Standard Reporting Set:**
Compute and report all metrics from the Standard Reporting Set (`docs/03-technical-contracts/metric-taxonomy.md` §3) for every (Algorithm Instance, Problem Instance) combination. These four metrics are non-negotiable:
- `QUALITY-BEST_VALUE_AT_BUDGET`
- `RELIABILITY-SUCCESS_RATE`
- `ROBUSTNESS-RESULT_STABILITY`
- `ANYTIME-ECDF_AREA`

Omitting any of these metrics, even when reporting additional ones, violates MANIFESTO Principle 29 (Objectivity over promotion).

---

## Step 8: Scope and Report Conclusions

*Implements MANIFESTO Principles 3, 19–25.*

This is the step where scientific integrity is most at risk. MANIFESTO Principle 3 is explicit: *"Conclusions about algorithm performance refer exclusively to actually tested problem instances and configurations. Every extrapolation is explicitly marked and carefully justified."*

**Mandatory conclusion scoping:**

Every conclusion in the report MUST state the conditions under which it holds:
- Which **Problem Instances** were tested (not "in general" or "across all HPO problems")
- Which **Algorithm Instances** (with exact configuration — Algorithm name and all hyperparameter values)
- Which **budget level** (conclusions may not hold at different budgets — see ANYTIME analysis)
- Under which **noise / stochasticity conditions**

Any claim beyond these conditions is an **extrapolation**, not a conclusion. Extrapolations must be:
1. Explicitly labeled as extrapolation (not stated as a finding)
2. Justified with reasoning (literature support, theoretical argument, or mechanistic explanation)

**Report structure — three levels (Principle 25):**

| Level | Audience | Content | Length |
|---|---|---|---|
| Practitioner summary | ML engineers, practitioners | Which algorithms worked well and for which problem types — with explicit scope | ~1 page |
| Researcher detail | Other researchers | Full methods, statistical tests, effect sizes, limitations, raw charts | Full document |
| Raw data | Analysts, reproducibility checkers | Complete datasets, analysis scripts, seeds, environment records | Archive |

All three levels must be producible from a single Study/Experiment record. The system generates the first two automatically; raw data is the underlying archive.

**Mandatory limitations section (Principle 24):**

Every report must include an explicit limitations section stating:
- What this study does **not** tell us (scope boundaries)
- Which problem types were **not** tested
- Which configurations were **not** explored
- What assumptions the conclusions depend on

This section is not optional or a gesture toward humility. It is the primary mechanism by which the system prevents over-generalization and respects the No Free Lunch theorem.

**Archival (Principles 19–22):**

Archive the complete Study record + Experiment record + all Run data + analysis scripts under a versioned identifier. Publish to the long-term artifact repository configured in `docs/05_community/versioning-governance.md` §4.

This archival is what makes the study reproducible by a different team years from now — the core scientific value of this system.
