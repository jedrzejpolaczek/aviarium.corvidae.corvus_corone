# Product Roadmap — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
Derived from: MANIFESTO.md, 01-srs/01-SRS.md, C1/C2 architecture, ADR-001,
docs/03-technical-contracts/02-interface-contracts/01-index.md, docs/03-technical-contracts/01-data-format/01-index.md, docs/03-technical-contracts/03-metric-taxonomy/01-index.md,
02-statistical-methodology.md, 01-benchmarking-protocol.md,
scripts/create_github_issues.py
Generated: 2026-03-04. Updated: 2026-05-15. Update whenever a milestone closes or a new REF-TASK is created.
-->

---

> **Scope authority.** This document sequences the work. It does not define the V1 release
> scope. That is defined in
> `docs/02-design/01-software-requirement-specification/01-srs/01-SRS.md` §1 V1 Release Scope.
> Corvus Pilot (IMPL Phases 3a and 3b) and the Learner actor (IMPL Phase 4) are outside V1.

## Current State

| Area | Tasks | Status |
|---|---|---|
| MANIFESTO | — | ✅ Principles and anti-patterns AP-1..AP-7 complete |
| C1 System Context | — | ⚠️ Principles complete |
| C2 Containers | — | ⚠️ Principles complete |
| C3 Components | REF-TASK-0041, 0050 | ⚠️ 11 groups; boundary vocabulary reconciled with the contracts (ADR-012), but the Experiment Runner and Study Orchestrator groups describe a failure model no contract defines |
| C4 Code | — | ⚠️ 7 groups drafted; descriptive layer only (ADR-012) |
| Architecture Decision Records | — | ✅ ADR-001..ADR-026 accepted |
| SRS | — | ✅ UC-01..UC-11, FR-01..FR-42, 6 NFRs, 16 constraints, §7 interface requirements, §8 acceptance strategy for every V1 requirement, §9 traceability |
| Statistical methodology | REF-TASK-0043, 0044 | ⚠️ §1–§3 and §7 written; **§4 Level 3, §5 anytime and §6 uncertainty are empty** (HTML comment only) |
| Metric taxonomy | REF-TASK-0014 | ✅ 9 metrics, Standard Reporting Set, selection guide; implementation references land with IMPL-011 |
| Interface contracts | — | ✅ 6 interfaces + cross-cutting; every method carries semantics, preconditions, postconditions and exceptions |
| Data format | — | ✅ 7 entity schemas, file formats, interoperability mappings, CV-001..CV-023, schema version 0.0.3 |
| Ecosystem integration | — | ✅ COCO, IOHprofiler and Nevergrad mappings documented; IOH and Nevergrad bridges implemented |
| Implementation — Core Library | IMPL-000..027 | ⚠️ IMPL-000, 010, 023, 025 done; IMPL-001..009, 011..022, 024, 026, 027 not started |
| Implementation — Researcher Agent (Pilot V2) | IMPL-028..036 | ⛔ Not started *(post-V1)* |
| Implementation — Autonomous (Pilot V3) | IMPL-037..047 | ⛔ Not started *(post-V1)* |
| Learner Actor | REF-TASK-0025..0030, IMPL-044..046 | ⛔ Not started *(post-V1)* |

> **C3 implementability, measured three times.** The test is the audit's verdict criterion: a
> component is specified from the documentation alone, and every point where a decision has to
> be invented rather than read is counted.
>
> | Component | Before the vocabulary sweep | After it | After the semantics pass |
> |---|---|---|---|
> | Study Builder | 10 | 3 | 0 |
> | Evaluation Loop | 11 | 6 | 0 |
> | Statistical Tester | 7 | 5 | 0 |
>
> The middle column corrects an earlier entry here that recorded zero. It was measured against
> the vocabulary gate, which had reached zero, and the two were not the same thing: the gate
> finds an identifier no contract defines, and every count above is a statement that reads
> correctly and says the wrong thing. `alpha: float = 0.05` names nothing uncontracted and is a
> significance threshold chosen after the data exists, which FR-28 forbids. Two of the six
> found in the Evaluation Loop had been introduced by the sweep itself, which split
> `best_so_far` across two documents without saying which owns it.
>
> The eight remaining component groups were read against their contracts on 2026-09-09 and
> repaired; the defects are listed in that commit. What the third column does **not** claim is
> that those eight now measure zero: three components were specified end to end, not eleven.
>
> One gap was not repairable by editing and was opened as REF-TASK-0040: the Public API +
> CLI container was in V1 scope with no functional requirement behind it. Closed the same
> day as FR §4.10.
>
> **Fourth measurement, 2026-09-09 (consistency audit).** Re-measured with the same method but a
> wider reading rule: a citation counts as read only if the *cited section says the same thing*.
>
> | Component | 3rd pass (against its own citations) | 4th pass (against what the citations say) |
> |---|---|---|
> | Statistical Tester | 0 | 12 |
> | Execution Coordinator | not measured | 13 |
> | LOCF Interpolator | not measured | 11 |
>
> The third column does not overturn the second; it measures a wider thing. Eight of the twelve
> for the Statistical Tester are not in `03-statistical-tester.md` at all but in
> `02-statistical-methodology.md`, which it cites — four of them in §4, a section that has no
> content. The other two components were never in the three-component sample; the eight groups
> repaired that day were reconciled with their contracts, which is not the same as being
> measured. The verdict from three components is: not implementable from documentation alone.
>
> The pattern is the same one the second column already recorded, one level further out. The
> gate checks names; the third pass checked sentences in the component document; the fourth
> checks sentences in the documents that component points at. Each level found defects the
> previous one could not see, so the next re-measurement should assume there is another.

---

## GitHub Milestones

Seven milestones group all open documentation and design tasks.

| Milestone | Focus |
|---|---|
| V1 Core — Contracts & Architecture | SRS §4/§5/§7/§8, interface contracts, data format, GLOSSARY, MANIFESTO anti-patterns, CLI spec, report format, competitive differentiation, LocalFileRepository structure — unblocked after Phases 1–2 |
| V1 Methodology — Statistics & Metrics | ECDF computation, test selection, diversity requirements, metric decisions |
| V1 Interoperability — Ecosystem Integration | COCO, Nevergrad, IOHprofiler format mappings and tutorials |
| V1 Infrastructure — ADRs & Technical Constraints | Python version, OS support, bulk storage format decision |
| Post-V1 — Continuous Improvement | Tasks requiring empirical data from real studies before they can be completed |
| Learner Actor — Education Platform *(post-V1)* | New actor: C1/SRS/C2 updates, GLOSSARY, tutorials |
| V1 Consistency — audit follow-up | Ten decisions the 2026-09-09 consistency audit found missing: failure model, four unspecified Repository methods, three empty methodology sections, test-tree scope, ADR-010/ADR-023 reconciliation, the ADR-012 exception, Pilot V3 against AP-4/AP-7, governance document, acceptance-test coverage, and the future of the C3/C4 layers |

---

## Milestone: V1 Core — Contracts & Architecture
> Foundation tasks: SRS functional requirements, interface contracts, data format, GLOSSARY. Unblocked after Phases 1–2 implementation.

### GLOSSARY
- [x] **[REF-TASK-0001] Extend GLOSSARY from interface-contracts and data-format** — all new terms from those documents added with precise definitions
- [x] **[REF-TASK-0002] Verify Schema Version definition against docs/03-technical-contracts/01-data-format/01-index.md** — GLOSSARY entry must use identical terminology to versioning scheme in `docs/03-technical-contracts/01-data-format/13-schema-versioning.md`

### SRS
- [x] **[REF-TASK-0009] Expand UC-01 and UC-02 into full use case descriptions** — main flow, preconditions, postconditions, failure scenarios, end-to-end tests
- [x] **[REF-TASK-0008] §4/§5/§7/§8 complete** — FR-XX from working public methods (§4), measurable NFR criteria (§5), interface requirements (§7), acceptance test strategy (§8)
- [x] **[REF-TASK-0010] §5 NFR measurable criteria** — testable pass/fail criteria for REPRO, STAT, INTEROP, OPEN, MODULAR, USABILITY
- [x] **[REF-TASK-0011] §6 Technical constraints** — Python version, OS support, dependency licensing; record as ADR-006
- [x] **[REF-TASK-0012] §7 Interface requirements** — per external system; requires REF-TASK-0005/0006/0007
- [x] **[REF-TASK-0013] §8 Acceptance test strategy** — every FR-XX maps to at least one test category

### Interface Contracts & Data Format
- [x] **[REF-TASK-0037] Define public API facade contract** — new `docs/03-technical-contracts/04-public-api-contract.md`
- [x] **[REF-TASK-0023] Repository storage abstraction interface** — `LocalFileRepository` spec satisfying ADR-001; document after IMPL-010 is merged
- [x] **[REF-TASK-0036] LocalFileRepository directory structure** — annotated directory tree for a completed study; notes that layout is an implementation detail, not part of the `Repository` interface; document after IMPL-010

### Data format — cross-entity rules and schema version
- [x] **[REF-TASK-0038] Cross-entity validation rules** — `01-data-format/12-cross-entity-validation.md` was an empty comment; now defines CV-001..CV-023, each with the point of check and the consequence of violation (reject, warn, flag). These are the checks the Study Orchestrator performs, so the component was not implementable without them
- [x] **[REF-TASK-0039] Declare the initial schema version** — `schema_version` was named in `13-schema-versioning.md` but present in no entity table, and the pointer to where the current version is declared named a file that does not exist. Version set to `0.0.1`, declared in `01-data-format/01-index.md`, field added to the seven entity schemas; stays below `1.0.0` until the V1 release so pre-release changes owe no migration guide

### MANIFESTO
- [x] **[REF-TASK-0032] Reconcile anti-pattern numbering and add to MANIFESTO** — add Anti-patterns section; resolve missing AP-2; update SRS §6 references from C1 to MANIFESTO

### Architecture — post-implementation specs
- [x] **[REF-TASK-0033] Specify CLI experience** — synopsis, arguments, example terminal output, exit codes for all `corvus` commands; document from working IMPL-017
- [x] **[REF-TASK-0034] Specify report output format** — Practitioner and Researcher report sections, mandatory visualizations, audience language; document from working IMPL-014/015
- [x] **[REF-TASK-0035] Add competitive differentiation statement to SRS §2** — 3–6 sentences grounded in MANIFESTO principles; frames Corvus Corone as complementary to COCO/Nevergrad/IOHprofiler

---

## Milestone: V1 Methodology — Statistics & Metrics
> Scientific methodology: ECDF_AREA formalization, statistical test selection, diversity requirements, sensitivity documentation.

- [x] **[REF-TASK-0016] ANYTIME-ECDF_AREA computation procedure** — exact normalization (ADR-007: empirical min/max; integration domain settled by ADR-024) and aggregation across problems
- [x] **[REF-TASK-0017] TIME-EVALUATIONS_TO_TARGET Standard Reporting Set decision** — weigh pre-specification burden vs. efficiency metric value; create ADR
- [x] **[REF-TASK-0020] Statistical test selection procedure** — decision tree: Wilcoxon (2 algorithms) vs Kruskal-Wallis + Holm-Bonferroni (>2); document in `02-statistical-methodology.md §3`
- [x] **[REF-TASK-0021] Problem instance diversity minimum requirements** — quantitative floor, recorded as ADR-009 D-1..D-3: ≥5 instances, ≥2 dimensionality ranges, ≥1 stochastic + ≥1 deterministic
- [x] **[REF-TASK-0022] Algorithm sensitivity documentation format** — `SensitivityReport` schema field in `AlgorithmInstance`; requires `docs/03-technical-contracts/01-data-format/03-algorithm-instance.md`
- [x] **[REF-TASK-0019] Level 1 required visualizations** — mandatory EDA set (boxplot, convergence curves, ECDF, violin); document in `02-statistical-methodology.md §2`
- [x] **[REF-TASK-0015] Metric implementation references** — link each metric definition to `corvus_corone/analysis/metrics.py`; fulfilled as part of IMPL-011
- [ ] **[REF-TASK-0014] Metric taxonomy extensions** *(Post-V1)* — new metrics after first real studies
- [ ] **[REF-TASK-0018] Research question archetypes** *(Post-V1)* — Metric Selection Guide additions from real study patterns

---

## Milestone: V1 Interoperability — Ecosystem Integration
> COCO, Nevergrad, IOHprofiler format mappings. Spike required before implementation.

- [x] **[REF-TASK-0004] Algorithm Author tutorial** — wrap Optuna sampler in ≤ 15 lines; interface acceptance test
- [x] **[REF-TASK-0005] COCO format mapping** *(spike first)* — map Corvus entities to COCO `.info`/`.dat`/`.tdat`; document data loss; round-trip test
- [x] **[REF-TASK-0006] Nevergrad adapter pattern** *(spike first)* — generic `NevergradAdapter`; tutorial; `docs/03-technical-contracts/01-data-format/10-file-formats.md` mapping
- [x] **[REF-TASK-0007] IOHprofiler export format mapping** — `.dat` export + `.meta.json` sidecar for unsupported fields; full spec + round-trip test

---

## Milestone: V1 Infrastructure — ADRs & Technical Constraints

- [x] **[REF-TASK-0024] Bulk PerformanceRecord storage format decision** *(spike first)* — benchmark JSON vs Parquet vs HDF5 at 150 k records; recorded as ADR-010

---

## IMPL Phase 0 — Project Setup
> Monorepo initialization. Must complete before any implementation task.

- [x] **`[IMPL-000]`** Setup monorepo: uv workspace, `pyproject.toml` (corvus_corone + corvus_corone_pilot), GitHub Actions CI matrix (ubuntu + macos × Python 3.10/3.11/3.12) · *Refs: ADR-006, REF-TASK-0011*

---

## IMPL Phase 1 — corvus_corone Library
> Core library: Problem/Algorithm interfaces, Runner, Storage, Analysis, Reporting, Orchestrator, Public API.

- [ ] **`[IMPL-001]`** Problem Interface — `problems/base.py`: `Problem` ABC, `EvaluationResult`, `SearchSpace`; contract test
- [ ] **`[IMPL-002]`** Problem Repository — `problems/registry.py`: `@registry.register` decorator, `discover()`, fail-early validation
- [ ] **`[IMPL-003]`** SearchSpace types — `problems/search_space.py`: `ContinuousVariable`, `IntegerVariable`, `CategoricalVariable` with Pydantic v2
- [ ] **`[IMPL-004]`** Algorithm Interface — `algorithms/base.py`: `Algorithm` ABC (ask-tell: `suggest`, `observe`, `reset`), `AlgorithmInstanceRecord`, `RunContext`
- [ ] **`[IMPL-005]`** Algorithm Registry + RandomSearch — `algorithms/registry.py`, `algorithms/random_search.py`; `numpy.random.default_rng` seed handling
- [ ] **`[IMPL-006]`** Optuna TPE adapter — `algorithms/adapters/optuna_adapter.py` in ≤ 15 lines; tutorial `docs/06-tutorials/04-algorithm-author-onboarding.md` · *Fulfills: REF-TASK-0004*
- [ ] **`[IMPL-007]`** Experiment Runner — `runner/runner.py`: `deepcopy` isolation per run, determinism test, independence test · *Refs: MANIFESTO Principle 18*
- [ ] **`[IMPL-008]`** Seed Manager — `runner/seed_manager.py`: `generate_seeds()` via `numpy.random.SeedSequence.spawn()`
- [ ] **`[IMPL-009]`** Data entities — `storage/entities.py`: `RunRecord`, `PerformanceRecord`, `StudyRecord` (UUID IDs, JSON round-trip) · *Refs: docs/03-technical-contracts/01-data-format/01-index.md, ADR-001*
- [x] **`[IMPL-010]`** Repository interface + LocalFileRepository — `storage/repository.py`: `Repository` ABC, `LocalFileRepository`, `RepositoryContractTest` · *Fulfills: REF-TASK-0023*
- [ ] **`[IMPL-011]`** Metric taxonomy — `analysis/metrics.py`: `@metric` registry; `QUALITY-BEST_VALUE_AT_BUDGET`, `TIME-EVALUATIONS_TO_TARGET`, `RELIABILITY-SUCCESS_RATE`; implementation refs added to `03-metric-taxonomy/01-index.md` · *Fulfills: REF-TASK-0015*
- [ ] **`[IMPL-012]`** Statistical analysis — `analysis/statistical.py`: three-level (exploratory summary, Wilcoxon/Kruskal-Wallis + Holm-Bonferroni, Cliff's delta); `ThreeLevelAnalysis.analyze()` requires all three levels · *Fulfills: REF-TASK-0020*
- [ ] **`[IMPL-013]`** Anytime performance — `analysis/anytime.py`: `compute_anytime_curve`, `compute_ecdf`, `compute_ecdf_area` (empirical normalization per ADR-007, integration domain per ADR-024; LOCF over `best_so_far` per ADR-003 and ADR-023); basic IOHprofiler `.dat` export · *Fulfills: REF-TASK-0016*
- [ ] **`[IMPL-014]`** Reporting Engine — `reporting/reports.py`: `StudyReport` (required `scope_statement`, `limitations`); Jinja2 templates for researcher + practitioner reports; raises `ValueError` when scope absent · *Fulfills: REF-TASK-0019*
- [ ] **`[IMPL-015]`** Visualizations — `reporting/visualizations.py`: VIZ-L1-01 boxplot, VIZ-L1-02 convergence curves, VIZ-L1-03 ECDF (`plt.step(where='post')`), VIZ-L1-04 violin (n > 50); auto-generated for every report
- [ ] **`[IMPL-016]`** Study Orchestrator — `orchestrator.py`: `StudyConfig`, `StudyOrchestrator.run()`, diversity validation, `SeedSequence` seed generation, Facade over all modules · *Refs: REF-TASK-0021*
- [ ] **`[IMPL-017]`** Public API + CLI — `api.py`, `cli.py` (Click): `corvus run`, `corvus list-problems`, `corvus list-algorithms`; `CliRunner` tests · *Refs: REF-TASK-0004, NFR-MODULAR-01*

---

## IMPL Phase 2 — Repo Closure
> ADRs, bulk storage after spike, ecosystem bridges (IOHprofiler/COCO/Nevergrad), LLM tools.

- [ ] **`[IMPL-017a]`** Study design guidance — FR-27..FR-31: `lock_study()` reports every unresolved decision at once with its consequence; `seed_strategy` and `sampling_strategy` become required; every validation message names the rule it enforces; the ADR-009 diversity floor is checked with the exploratory escape hatch · *Fulfills: FR-27, FR-28, FR-29, FR-30, FR-31; acceptance criterion in NFR-USABILITY-01*
- [ ] **`[IMPL-009a]`** PerformanceRecord carries `best_so_far` alongside `objective_value`; the Runner maintains the running best; anytime reconstruction reads `best_so_far` · *Fulfills: ADR-023*
- [ ] **`[IMPL-013a]`** ECDF_AREA integrates over the full Budget; the reference case asserts `0.4375` · *Fulfills: ADR-024*
- [ ] **`[IMPL-018]`** ADR-006 + ADR-022: Technical constraints — `pyproject.toml` `requires-python = ">=3.10"`, AGPL-3.0-or-later (ADR-022 supersedes the MIT clause of ADR-006), optional extras (`optuna`, `rag`, `all`) · *Fulfills: REF-TASK-0011*
- [ ] **`[IMPL-019]`** ADR-007 + ADR-008: ECDF_AREA normalization (empirical min/max, limitations documented) + Standard Reporting Set definition; update `03-metric-taxonomy/01-index.md §3` · *Fulfills: REF-TASK-0016, REF-TASK-0017*
- [ ] **`[IMPL-020]`** ADR-009 + 02-statistical-methodology.md: diversity requirements (≥5 problems, ≥2 dimensionality ranges); Level 1 VIZ-L1-01..03 spec in §2; Wilcoxon/Kruskal decision tree in §3 · *Fulfills: REF-TASK-0019, REF-TASK-0020, REF-TASK-0021*
- [ ] **`[IMPL-021]`** Sensitivity documentation — `SensitivityReport(BaseModel)` in `storage/entities.py`, `docs/03-technical-contracts/01-data-format/03-algorithm-instance.md`, `01-contribution-guide.md §2` · *Fulfills: REF-TASK-0022*
- [ ] **`[IMPL-022]`** Bulk PerformanceRecord storage — ADR-010 (decided from benchmark evidence); `LocalFileRepository.save_bulk_records()`; round-trip test · *Fulfills: REF-TASK-0024*
- [x] **`[IMPL-023]`** IOHprofiler bridge — `bridge/iohprofiler.py`: full `.dat` export + `.meta.json` sidecar (seed, run_id, wall_time); round-trip test; `docs/03-technical-contracts/01-data-format/10-file-formats.md` mapping table · *Fulfills: REF-TASK-0007*
- [ ] **`[IMPL-024]`** COCO bridge — **blocked on REF-TASK-0005 spike**; `bridge/coco_exporter.py`; continuous-only warning; `docs/03-technical-contracts/01-data-format/10-file-formats.md` mapping with documented data loss · *Fulfills: REF-TASK-0005*
- [x] **`[IMPL-025]`** Nevergrad adapter — **blocked on REF-TASK-0006 spike**; `algorithms/adapters/nevergrad_adapter.py`; `ng.p.Dict` → `SearchSpace`; tutorial; `docs/03-technical-contracts/01-data-format/10-file-formats.md` mapping · *Fulfills: REF-TASK-0006*
- [ ] **`[IMPL-026]`** LLM-as-judge — `analysis/llm_judge.py`: `ManifestoReview` Pydantic model, `StudyDesignJudge.review()`, Ollama structured output; optional `corvus-corone[llm]` extra
- [ ] **`[IMPL-027]`** RAG over `papers/` — `papers_rag.py`: FAISS index, `PapersRAG.why(metric_id)` via Ollama; optional `corvus-corone[rag]` extra; references Bartz-Beielstein 2020

---

## IMPL Phase 3a — Pilot V2 Researcher
> corvus_corone_pilot V2: MCP server, ReAct agent, LangGraph graph, ML foundations, multi-agent system, MLflow tracking.

- [ ] **`[IMPL-028]`** Pilot setup — `corvus_corone_pilot/pyproject.toml` (langgraph, mcp, langchain-ollama, mlflow, xgboost, shap, dvc); uv workspace root updated; CI extended
- [ ] **`[IMPL-029]`** MCP Server — `v2_researcher/mcp_server.py`: `run_study`, `list_problems`, `list_algorithms`, `get_study_results`, `get_algorithm_properties` exposed via `@app.tool()`
- [ ] **`[IMPL-030]`** ReAct agent demo — `v2_researcher/agents/react_demo.py`: manual Thought-Action-Observation loop (~30 lines), `max_steps` circuit breaker, Ollama `tools` parameter
- [ ] **`[IMPL-031]`** LangGraph graph — `v2_researcher/graph.py`: `StudyState(TypedDict)`, nodes (plan → validate → execute → analyze), `interrupt_before=["execute_study"]`, `MemorySaver` checkpointing
- [ ] **`[IMPL-032]`** ML foundations: autograd — `ml_foundations/autograd.py`: `Value` class, operators, `backward()` topological sort, `SimpleNN` (NumPy)
- [ ] **`[IMPL-033]`** ML foundations: surrogate — `ml_foundations/surrogate.py`: `GaussianProcess` (RBF kernel, fit, predict), UCB acquisition, mini Bayesian optimization loop
- [ ] **`[IMPL-034]`** Multi-agent system — `agents/planner.py`, `agents/executor.py`, `agents/analyst.py`; LangGraph supervisor routing; shared `StudyState`; integration test end-to-end
- [ ] **`[IMPL-035]`** ML foundations: predictor — `ml_foundations/predictor.py`: `GradientBoosting` from scratch, `CalibratedPredictor` (XGBoost + isotonic regression), SHAP explanations; returns `None` when confidence < 0.6
- [ ] **`[IMPL-036]`** V2 finalization — `v2_researcher/cli.py` (`corvus-pilot run -q "..." [--auto-approve] [--thread-id]`), `v2_researcher/tracking.py` (MLflow per session), `corvus-pilot history`

---

## IMPL Phase 3b — Pilot V3 Autonomous
> V3: hypothesis generation, meta-analysis, safety module, autonomous cycle with DVC, shadow/canary deployment, agent evaluation harness.

- [ ] **`[IMPL-037]`** Hypothesis generator — `v3_autonomous/hypothesis_gen.py`, `v3_autonomous/memory/long_term_memory.py`: `Hypothesis` Pydantic model (must be falsifiable), LLM structured JSON output; read-only past data
- [ ] **`[IMPL-038]`** Meta-analyst — `v3_autonomous/meta_analyst.py`: `meta_analyze_algorithm_performance()`, inverse-variance weighted Cliff's delta, 95% CI; uses `corvus_corone.analysis.statistical.cliffs_delta`
- [ ] **`[IMPL-039]`** Safety module — `v3_autonomous/safety.py`: `@requires_confirmation(max_repetitions=50, max_budget=200)`, `validate_research_question()` (injection patterns), `LoopDetector`, `ReadOnlyRepository`
- [ ] **`[IMPL-040]`** ML foundations: evaluation — `v3_autonomous/ml_foundations/evaluation.py`: L1/L2 regularization, `kfold_cv()` from scratch, `evaluate_agent_calibration()`, `CalibratedPredictor` with isotonic regression
- [ ] **`[IMPL-041]`** Autonomous cycle — `v3_autonomous/cycle.py`, `dvc.yaml` (stages: fetch_studies → train_predictor → run_autonomous_cycle), `.github/workflows/autonomous.yml` (weekly cron + push trigger)
- [ ] **`[IMPL-042]`** Shadow/canary deployment — `v3_autonomous/deployment.py`: `ModelRouter`, deterministic A/B routing by `md5(thread_id)`, shadow mode (log but never serve), canary (5%→50%→100%)
- [ ] **`[IMPL-043]`** Agent evaluation harness — `v3_autonomous/evals.py`: `pass_at_k(n, c, k)` (Chen et al. 2021), 10 standard test cases; targets: pass@1 ≥ 0.6, safety_violations = 0; CI trigger on PRs to `v3_autonomous/`
- [ ] **`[IMPL-047]`** Portfolio — `README.md` (V1/V2/V3 narrative), `docs/architecture.md` (C1 Mermaid + design philosophy), `demo/demo.py` + `demo/demo_autonomous.py`; demo scripts run in CI <!-- check-docs: planned -->

---

## IMPL Phase 4 — Learner Actor
> Learner implementation: Algorithm Visualization Engine, Socratic Guide (LangGraph node), Algorithm Genealogy module.

- [ ] **`[IMPL-044]`** Algorithm Visualization Engine — `learner/visualization_engine.py`: convergence animation, parameter sensitivity heatmap, search trajectory, Pareto front, algorithm genealogy timeline · *Refs: REF-TASK-0027, UC-07*
- [ ] **`[IMPL-045]`** Socratic Guide — `v2_researcher/agents/socratic_guide.py`: LangGraph node activated by `state["interaction_mode"] == "socratic"`, generates bridging questions, never direct answers; CLI `--mode socratic` · *Fulfills: REF-TASK-0028, UC-09*
- [ ] **`[IMPL-046]`** Algorithm Genealogy — `learner/genealogy.py` + `learner/data/genealogy_data.json`: `AlgorithmNode`, `Genealogy` directed graph, lineage (MAB 1933 → BayesOpt 1998 → TPE 2011) and CMA-ES/NSGA-II history; tutorial `docs/06-tutorials/07-learner-algorithm-genealogy.md` · *Refs: REF-TASK-0030, UC-10*

---

## Learner Actor — Education Platform
> New actor introduced after V1: Learner persona with Algorithm Visualization, Socratic guidance mode, algorithm history/evolution features. Requires C1, SRS, C2, GLOSSARY updates.

- [x] **[REF-TASK-0025] Add Learner actor to C1 context document** — role, goals, gives/gets, relationship to Researcher data flow, C1 diagram update ·
- [x] **[REF-TASK-0026] Add Learner use cases to SRS §3** — UC-07 (visualization), UC-08 (contextual help), UC-09 (Socratic), UC-10 (algorithm history), UC-11 (explore Researcher results). *Numbers corrected 2026-09-09: this line predated the renumbering that made UC-06 the Researcher's export case.* ·
- [x] **[REF-TASK-0027] Add Algorithm Visualization Engine container to C2** — matplotlib/plotly/manim; ADR for technology choice; diagram update ·
- [x] **[REF-TASK-0028] Add Socratic Guide component to C2/C3** — LangGraph `--mode socratic`; guides toward understanding rather than answering ·
- [x] **[REF-TASK-0029] Add Learner terms to GLOSSARY.md** — Learner, Algorithm Visualization, Algorithm Genealogy, Socratic Mode ·
- [x] **[REF-TASK-0030] Add Learner education tutorials** — visualization (`UC-07`), Socratic mode (`UC-09`), algorithm genealogy explorer (`UC-10`) ·

---

## V2 Horizon — Platform & Distributed Execution
> Planned. Not in V1 scope. Enabled by server-ready data layer from ADR-001 — no data migration required.

| Feature | Dependency |
|---|---|
| V2 Platform Server — shared result repository, study discovery | `ServerRepository` implementing same `Repository` interface |
| Persistent identifiers (DOIs) for published studies | Platform Server |
| Cross-researcher comparison and aggregation | Platform Server |
| HPC/Cloud distributed `ExperimentRunner` | `Runner` interface abstraction (already designed) |
| Community governance tooling | Platform Server + governance decisions |

---

## Dependency Graph (critical path)

```
MANIFESTO ──► C1 ──► C2/C3/C4 (complete)
                           │
                           ├──► SRS §4/§8 (REF-TASK-0008, 0013) — unblocked after Phase 1
                           ├──► docs/03-technical-contracts/01-data-format/01-index.md update (REF-TASK-0022) — after IMPL-021
                           └──► 02-interface-contracts/01-index.md (REF-TASK-0023) — after IMPL-010

REF-TASK-0005/0006/0007 spikes ──► IMPL-024/025/023 bridges ──► SRS §7 (REF-TASK-0012)
REF-TASK-0024 spike ──► IMPL-022 bulk storage (ADR-010)

REF-TASK-0037 (public API contract) ──► IMPL-017 (Public API + CLI)

Phase 0 ──► Phase 1 (IMPL-001..017) ──► Phase 2 (IMPL-018..027)
                                                    │
                                          ──► Phase 3a (IMPL-028..036) V2 Researcher
                                          ──► Phase 3b (IMPL-037..043, 047) V3 Autonomous
                                          ──► Phase 4  (IMPL-044..046) Learner Actor

REF-TASK-0016 (ECDF) ──► IMPL-013/019    REF-TASK-0020 (test tree) ──► IMPL-012/020
REF-TASK-0021 (diversity) ──► IMPL-016/020

REF-TASK-0025 ──► 0026 ──► 0027 ──► 0028 ──► 0029 ──► 0030 (Learner doc)
                                                              │
                                               ──► IMPL-044 (Visualization Engine)
                                               ──► IMPL-045 (Socratic Guide)
                                               ──► IMPL-046 (Algorithm Genealogy)
```

---

## Milestone: V1 Consistency — audit follow-up (2026-09-09)
> Ten findings from the consistency audit that could not be closed by editing. Each names a
> decision that does not exist yet, so each needs a decision before any document can state it.
> The editable findings from the same audit were fixed in the commit that opened these.

### Contracts — decisions that are missing

- [ ] **[REF-TASK-0041] Decide the Run and Experiment failure model.** `Study.on_failure`
  (`skip`/`abort`), `Study.max_workers`, `Run.timeout_s`, `Run.memory_limit_mb`,
  `Experiment.skipped_count`, the Run statuses `skipped` and `aborted` and the Experiment
  statuses `partial` and `aborted` are used across the Experiment Runner and Study Orchestrator
  component groups and in `05-c4-level4-code/02-shared/04-study-spec.md`. None of them exists in
  any entity schema: `06-run.md` admits `completed`, `failed`, `budget_exhausted`;
  `05-experiment.md` admits `planned`, `running`, `completed`, `failed`; FR-12 requires a failed
  Run to carry `status="failed"` and a non-empty `failure_reason`. A descriptive document may not
  coin them (ADR-012), so either the contracts gain the model or the components lose it.
  `max_workers` is settled already — SRS §1.4 B-01 reserves it for V2 — and must not return.
  *Blocks IMPL-007, IMPL-016.*

- [x] **[REF-TASK-0042] Specify the four Repository methods that carry only a signature.** *(Closed 2026-09-09.)* All four now carry semantics, preconditions, postconditions and exceptions. The larger finding was underneath: `deprecated`, `deprecation_reason` and `superseded_by` were in neither entity schema, although ADR-020 states that the contract already defines them and both implementations write them. Added, together with the supersession rules the model needs (resolvable, same kind, not self, acyclic) and the removal of the `version must be updated on every field change` rule that ADR-020 had superseded. Schema version 0.0.2 → 0.0.3. Implemented in both backends with 20 contract tests.
  `deprecate_algorithm(id, reason, superseded_by)`, `list_experiments()`,
  `list_result_aggregates()` and `list_reports()` in `06-repository-interface.md` have no
  semantics, preconditions, postconditions or exceptions, against the method template the
  cross-cutting contract requires. `deprecate_algorithm` carries the whole supersession model of
  ADR-020, so it is the one that cannot wait. *Blocks IMPL-002 and the IMPL-010 follow-up.*

- [x] **[REF-TASK-0045] Reconcile the ADR-010 Parquet column table with ADR-023.** *(Closed 2026-09-09 by ADR-025.)* The hole was in the ADR practice rather than in either ADR: the rule said a closed ADR is superseded, never edited, and had no form for superseding *part* of one. ADR-006 had improvised a Status-line clause and ADR-023 had done nothing, which is what an unwritten convention produces. ADR-025 makes the ADR-006 form the rule and applies it. `pyarrow` stays undeclared until IMPL-022 — adding an unused runtime dependency so a file agrees with a document is the wrong direction of fit, and the obligation sits where the import appears. ADR-010 lists
  the bulk-format columns and predates the split of the value field, so it has `objective_value`
  and no `best_so_far`. ADR-023 added the field and did not list ADR-010 among the documents it
  corrects. `10-file-formats.md` now carries the column with a note; the ADR pair still needs a
  superseding record so the next reader is not left comparing two accepted ADRs. Same class of
  defect: ADR-009 and ADR-023 both cited cross-entity rules under a `CEV-` prefix that no rule
  uses (the contract defines `CV-001`..`CV-023`); both citations were corrected in place, and
  `check_docs.py` does not check this identifier family. *Blocks IMPL-022.*

### Methodology — sections that are empty

- [ ] **[REF-TASK-0043] Write §4, §5 and §6 of `02-statistical-methodology.md`.** All three are
  headings whose entire body is an HTML comment: §4 Level 3 Practical Significance, §5 Anytime
  Analysis, §6 Uncertainty Reporting. They are cited as if written by `05-analyzer-interface.md`
  (Cliff's delta → §4), ADR-007 (→ §5), FR-15, NFR-STAT-01, `03-report-format-spec.md` and four
  GLOSSARY entries. The blocking sub-decisions: the interpretation thresholds for Cliff's delta,
  which exist nowhere in the corpus; and whether post-hoc pairwise comparisons report Cliff's
  delta (§4, `03-statistical-tester.md`) or rank-biserial correlation (§3.5.1) — the two sections
  disagree. *Blocks IMPL-012, IMPL-013.*

- [x] **[REF-TASK-0044] Decide whether the parametric branch of §3.3 is in V1.** *(Closed 2026-09-09: it is not.)* The guard was never satisfiable — confirming normality needs a positive Level 1 result, the guard itself said `n < 30 → assume non-normal`, and an ADR-009-compliant Study gives the paired test five per-problem differences, on which Shapiro-Wilk has almost no power to reject. Taking that as permission was the inference the section warned against two paragraphs below the tree that offered it. §3.7's default α went with it: FR-28 forbids a silent default on a parameter with methodological consequences, and 0.05 is now the recommendation a researcher still has to write down. Post-V1 the branch needs three contracted `test_type` values, Cohen's d in §4, and an ADR stating when the guard opens. The test
  selection tree offers paired t-test, repeated-measures ANOVA and Tukey HSD alongside the
  non-parametric path; `03-statistical-tester.md` states the tree "has exactly these two entries"
  and admits only Wilcoxon and Kruskal-Wallis. The names `paired_t_test`, `rm_anova` and
  `tukey_hsd` appear in no contract, so `Study.pre_registered_hypotheses.test_type` cannot express
  them. Either the tree loses the branch or the taxonomy gains the names. Related: §3.7 sets a
  default α of 0.05, which FR-28 forbids for a parameter with methodological consequences, while
  `03-statistical-tester.md` already refuses that default — one of the two is wrong.
  *Blocks IMPL-012.*

### Governance and scope — decisions that were never recorded

- [x] **[REF-TASK-0046] Record the exception ADR-016, ADR-018 and ADR-019 make to ADR-012.** *(Closed 2026-09-09 by ADR-026.)* Amend rather than promote: moving the three surfaces into the contracts would separate each definition from the explanation that makes it a decision, which is clearest for `VIZ-L1-NN` — the identifiers exist to name the four charts Level 1 requires, and the requirement is the section they would be moved out of. Turned out to be three exceptions, not two: `02-statistical-methodology.md` defines the `VIZ-L1-NN` identifiers and no contract mentions them.
  ADR-012 states that C2/C3/C4 are descriptive and may cite but never coin, and `docs/README.md`
  repeats it: `03-technical-contracts/` is the only place that defines identifiers, signatures,
  field names, enumeration values and error classes. ADR-016 then makes `02-cli-spec.md`, a C2
  document, the authority for command names, options, error-message format and exit codes; ADR-018
  and ADR-019 lean on `03-report-format-spec.md` the same way. The later ADR wins, so the exception
  is real — it is written down nowhere, which means a reader applying ADR-012 literally concludes
  the CLI spec is illegal. Either promote those surfaces into the contracts, or amend the
  precedence rule to name the exception.

- [ ] **[REF-TASK-0047] Decide how Corvus Pilot V3 stays on the right side of AP-4 and AP-7.**
  AP-7 rejects automated algorithm selection as a substitute for researcher judgement; AP-4
  rejects analysis pipelines that cannot be independently inspected. IMPL-037 generates hypotheses
  with an LLM, IMPL-041 runs an autonomous research cycle on a weekly cron, IMPL-035 returns a
  calibrated prediction, IMPL-026 has an LLM judge study designs against the MANIFESTO. IMPL-039
  is a safety module against runaway resource use, which answers a different question. Nothing in
  the corpus reconciles the two, and the reconciliation is a decision, not an omission.
  *Post-V1, but the answer shapes IMPL-028 onwards.*

- [ ] **[REF-TASK-0048] Write `05-community/02-versioning-governance.md`.** All six sections —
  artifact types and versioning schemes, dependency tracking, deprecation policy, long-term
  storage, licensing, governance model — have headings and no content. NFR-REPRO-01, FR-03, FR-26,
  CONST-COM and four GLOSSARY entries cite it, including *Schema Version*, which points at "§1–2".
  ADR-020 rests its entity-identity model on a deprecation policy that is not written down. Same
  document family: `01-contribution-guide.md` §2 and §4–§8 are empty, and
  `06-tutorials/01-cmd-first-study.md` is a skeleton, which NFR-USABILITY-01 and the use-case
  acceptance criterion both depend on.

- [x] **[REF-TASK-0049] Extend §8 Acceptance Test Strategy to FR-27..FR-31 and FR-39..FR-42.** *(Closed 2026-09-09.)* Two categories added — Guidance quality and Interface conformance, the second of which the traceability matrix already named without the strategy defining it — and nine mapping rows. Two further defects surfaced while doing it: four rows carried ✅ against `tests/e2e/` stub files removed when ADR-013 and ADR-017 replaced the lifecycle and seed strategy they encoded, and the assertions that do exist (`test_repository_interface.py`, the IMPL-010 suite) were cited nowhere. Both corrected, and the matrix's category column now matches the strategy row for row.
  `01-acceptance-test-strategy.md` declares that every FR maps to at least one test file and
  covers FR-01..FR-26 plus FR-32 and FR-33. The Study Design Guidance group and the Programmatic
  and Command-Line Access group are both V1 and have no test category, while the traceability
  matrix already fills those rows with categories the strategy does not assign — two SRS documents
  claim coverage a third does not provide. FR-34..FR-38 are `[DEFERRED]` and are correctly absent.

- [ ] **[REF-TASK-0050] Decide what happens to the C3 and C4 layers.** ADR-012 considered deleting
  `05-c4-level4-code/` and consolidating the 45 C3 component files into eleven, and deferred it as
  "a separate, independent decision rather than a repair". The 2026-09-09 audit is evidence for
  taking it: every finding of the class "the descriptive layer invented vocabulary" came from
  these two layers, `check_docs.py` enforces three of the seven categories ADR-012 names, and the
  layers describe a library whose core has no code, so nothing can falsify them. Three options,
  all defensible: consolidate to eleven decomposition-only indexes; keep them and close
  REF-TASK-0041 first so the vocabulary exists; or mark the layer `allow-undefined` and stop
  implying it is checked. Choosing none of the three is what produced the 2026-09-09 defect where
  a correct traceability footnote was appended below an uncorrected document body.

---

## Open Tasks Index

### Documentation Tasks (REF-TASK)

All documentation REF-TASKs are tracked by the milestone sections above (✅ = complete, [ ] = pending).
The authoritative status for each task is the checkbox in the relevant milestone section — not this index.

Documentation tasks:
- [ ] **REF-TASK-0014** — Metric taxonomy extensions *(Post-V1, deferred — requires real study data)*
- [ ] **REF-TASK-0018** — Research question archetypes *(Post-V1, deferred — requires real study data)*
- [x] **REF-TASK-0040** — Requirements for the Python facade and the CLI. The Public API + CLI
  container was in V1 scope with no functional requirement behind it: the C3 components cited
  FR-28 and FR-29, which had been renumbered to Study Design Guidance. Closed by FR §4.10
  (FR-39..FR-42), which promotes the decisions already recorded in `04-public-api-contract.md`,
  `02-cli-spec.md` and ADR-015/ADR-016 to the layer that decides what V1 contains.
  *(Found by the C3 semantics pass, 2026-09-09; closed the same day.)*
- [ ] **REF-TASK-0041** — Run and Experiment failure model *(blocks IMPL-007, IMPL-016)*
- [x] **REF-TASK-0042** — semantics for four signature-only Repository methods
- [ ] **REF-TASK-0043** — `02-statistical-methodology.md` §4, §5, §6 *(blocks IMPL-012, IMPL-013)*
- [x] **REF-TASK-0044** — parametric branch of the test selection tree, and the §3.7 default α
- [x] **REF-TASK-0045** — ADR-010 Parquet columns against ADR-023, closed by ADR-025
- [x] **REF-TASK-0046** — record the ADR-016/018/019 exception to ADR-012 normativity, closed by ADR-026
- [ ] **REF-TASK-0047** — Corvus Pilot V3 against AP-4 and AP-7 *(post-V1)*
- [ ] **REF-TASK-0048** — write `02-versioning-governance.md`, finish the contribution guide
- [x] **REF-TASK-0049** — acceptance tests for FR-27..FR-31 and FR-39..FR-42
- [ ] **REF-TASK-0050** — decide the future of the C3 and C4 layers

### Implementation Tasks (IMPL)

| Task | Phase | Key Output |
|---|---|---|
| IMPL-000 — Monorepo setup | Phase 0 | uv workspace, pyproject.toml, CI skeleton |
| IMPL-001 — Problem Interface | Phase 1 | `problems/base.py`, contract test |
| IMPL-002 — Problem Repository | Phase 1 | `problems/registry.py`, `@register` decorator |
| IMPL-003 — SearchSpace types | Phase 1 | `problems/search_space.py`, Pydantic v2 |
| IMPL-004 — Algorithm Interface | Phase 1 | `algorithms/base.py`, ask-tell ABC |
| IMPL-005 — Algorithm Registry + RandomSearch | Phase 1 | `algorithms/registry.py`, `random_search.py` |
| IMPL-006 — Optuna TPE adapter | Phase 1 | `adapters/optuna_adapter.py`, tutorial |
| IMPL-007 — Experiment Runner | Phase 1 | `runner/runner.py`, determinism tests |
| IMPL-008 — Seed Manager | Phase 1 | `runner/seed_manager.py`, SeedSequence |
| IMPL-009 — Data entities | Phase 1 | `storage/entities.py`, UUID + JSON round-trip |
| IMPL-010 — Repository + LocalFileRepository | Phase 1 | `storage/repository.py`, contract tests |
| IMPL-011 — Metric taxonomy | Phase 1 | `analysis/metrics.py`, 03-metric-taxonomy/01-index.md refs |
| IMPL-012 — Statistical analysis | Phase 1 | `analysis/statistical.py`, ThreeLevelAnalysis |
| IMPL-013 — Anytime performance | Phase 1 | `analysis/anytime.py`, ECDF, basic .dat export |
| IMPL-014 — Reporting Engine | Phase 1 | `reporting/reports.py`, Jinja2 templates |
| IMPL-015 — Visualizations | Phase 1 | `reporting/visualizations.py`, VIZ-L1-01..04 |
| IMPL-016 — Study Orchestrator | Phase 1 | `orchestrator.py`, StudyConfig, Facade |
| IMPL-017 — Public API + CLI | Phase 1 | `api.py`, `cli.py`, corvus run/list commands · *Blocked on REF-TASK-0037* |
| IMPL-018 — ADR-006 technical constraints | Phase 2 | ADR-006, pyproject.toml finalized |
| IMPL-019 — ADR-007 + ADR-008 ECDF + SRS | Phase 2 | ADR-007/008, 03-metric-taxonomy/01-index.md §3 |
| IMPL-020 — ADR-009 + statistical-methodology | Phase 2 | ADR-009, 02-statistical-methodology.md §2/§3 |
| IMPL-021 — Sensitivity documentation | Phase 2 | SensitivityReport schema, docs/03-technical-contracts/01-data-format/03-algorithm-instance.md |
| IMPL-022 — Bulk PerformanceRecord storage | Phase 2 | ADR-010, `save_bulk_records()` |
| IMPL-023 — IOHprofiler bridge | Phase 2 | `bridge/iohprofiler.py`, .dat + .meta.json |
| IMPL-024 — COCO bridge | Phase 2 | `bridge/coco_exporter.py` (spike first) |
| IMPL-025 — Nevergrad adapter | Phase 2 | `adapters/nevergrad_adapter.py` (spike first) |
| IMPL-026 — LLM-as-judge | Phase 2 | `analysis/llm_judge.py`, ManifestoReview |
| IMPL-027 — RAG over papers/ | Phase 2 | `papers_rag.py`, FAISS + Ollama |
| IMPL-028 — Pilot setup | Phase 3a | corvus_corone_pilot workspace entry |
| IMPL-029 — MCP Server | Phase 3a | `v2_researcher/mcp_server.py` |
| IMPL-030 — ReAct agent demo | Phase 3a | `agents/react_demo.py`, manual loop |
| IMPL-031 — LangGraph graph | Phase 3a | `v2_researcher/graph.py`, interrupt + checkpoint |
| IMPL-032 — ML foundations: autograd | Phase 3a | `ml_foundations/autograd.py`, Value class |
| IMPL-033 — ML foundations: surrogate | Phase 3a | `ml_foundations/surrogate.py`, GP + UCB |
| IMPL-034 — Multi-agent system | Phase 3a | Planner, Executor, Analyst + supervisor |
| IMPL-035 — ML foundations: predictor | Phase 3a | `ml_foundations/predictor.py`, SHAP |
| IMPL-036 — V2 finalization | Phase 3a | CLI, MLflow tracking, thread memory |
| IMPL-037 — Hypothesis generator | Phase 3b | `v3_autonomous/hypothesis_gen.py` |
| IMPL-038 — Meta-analyst | Phase 3b | `v3_autonomous/meta_analyst.py`, pooled Cliff's δ |
| IMPL-039 — Safety module | Phase 3b | `v3_autonomous/safety.py`, guards + ReadOnlyRepo |
| IMPL-040 — ML foundations: evaluation | Phase 3b | k-fold CV, calibration, L1/L2 from scratch |
| IMPL-041 — Autonomous cycle | Phase 3b | `cycle.py`, `dvc.yaml`, weekly cron workflow |
| IMPL-042 — Shadow/canary deployment | Phase 3b | `deployment.py`, ModelRouter, A/B by md5 |
| IMPL-043 — Agent evaluation harness | Phase 3b | `evals.py`, pass@k, 10 test cases |
| IMPL-044 — Algorithm Visualization Engine | Phase 4 | `learner/visualization_engine.py` |
| IMPL-045 — Socratic Guide | Phase 4 | `agents/socratic_guide.py`, --mode socratic |
| IMPL-046 — Algorithm Genealogy | Phase 4 | `learner/genealogy.py`, genealogy_data.json |
| IMPL-047 — Portfolio | Phase 3b | README, docs/architecture.md, demo scripts | <!-- check-docs: planned -->
