# Product Roadmap — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
Derived from: MANIFESTO.md, SRS.md, C1/C2 architecture, ADR-001,
interface-contracts.md, data-format.md, metric-taxonomy.md,
statistical-methodology.md, benchmarking-protocol.md, TASKS.md,
scripts/create_github_issues.py
Generated: 2026-03-04. Updated: 2026-03-20. Update whenever a milestone closes or a new REF-TASK is created.
-->

---

## Current State

| Area | Tasks | Status |
|---|---|---|
| MANIFESTO | REF-TASK-0032 | ⚠️ Principles complete; anti-patterns section pending |
| C1 System Context | — | ⚠️ Principles complete |
| C2 Containers | — | ⚠️ Principles complete |
| C3 Components | — | ⛔ Not started |
| C4 Code | — | ⛔ Not started |
| Architecture Decision Records | REF-TASK-0011, 0024 | ⚠️ ADR-001 decided; technical constraints and bulk storage format pending |
| SRS | REF-TASK-0008..0013, 0033..0035 | ⚠️ Use cases and FR-01..26 drafted; NFRs, interface requirements, acceptance tests, CLI spec, report format, competitive differentiation open |
| Statistical methodology | REF-TASK-0016..0021 | ⚠️ 3-level framework drafted; ECDF, test selection, diversity requirements open |
| Metric taxonomy | REF-TASK-0014, 0015 | ⚠️ Drafted; implementation references pending |
| Interface contracts | REF-TASK-0023, 0036 | ⚠️ Drafted; LocalFileRepository structure and post-implementation update pending |
| Data format | REF-TASK-0022 | ⚠️ Drafted; post-implementation update pending |
| Ecosystem integration | REF-TASK-0004..0007 | ⛔ Not started (spikes required) |
| Implementation — Core Library | IMPL-000..027 | ⛔ Not started |
| Implementation — Researcher Agent (Pilot V2) | IMPL-028..036 | ⛔ Not started |
| Implementation — Autonomous (Pilot V3) | IMPL-037..047 | ⛔ Not started |
| Learner Actor | REF-TASK-0025..0030, IMPL-044..046 | ⛔ Not started |

---

## GitHub Milestones

Six milestones group all open documentation and design tasks.

| Milestone | Focus |
|---|---|
| V1 Core — Contracts & Architecture | SRS §4/§5/§7/§8, interface contracts, data format, GLOSSARY, MANIFESTO anti-patterns, CLI spec, report format, competitive differentiation, LocalFileRepository structure — unblocked after Phases 1–2 |
| V1 Methodology — Statistics & Metrics | ECDF computation, test selection, diversity requirements, metric decisions |
| V1 Interoperability — Ecosystem Integration | COCO, Nevergrad, IOHprofiler format mappings and tutorials |
| V1 Infrastructure — ADRs & Technical Constraints | Python version, OS support, bulk storage format decision |
| Post-V1 — Continuous Improvement | Tasks requiring empirical data from real studies before they can be completed |
| Learner Actor — Education Platform | New actor: C1/SRS/C2 updates, GLOSSARY, tutorials |

---

## Milestone: V1 Core — Contracts & Architecture
> Foundation tasks: SRS functional requirements, interface contracts, data format, GLOSSARY. Unblocked after Phases 1–2 implementation.

### GLOSSARY
- [x] **[REF-TASK-0001] Extend GLOSSARY from interface-contracts and data-format** — all new terms from those documents added with precise definitions
- [x] **[REF-TASK-0002] Verify Schema Version definition against data-format.md** — GLOSSARY entry must use identical terminology to versioning scheme in `data-format.md §6`

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

### MANIFESTO
- [x] **[REF-TASK-0032] Reconcile anti-pattern numbering and add to MANIFESTO** — add Anti-patterns section; resolve missing AP-2; update SRS §6 references from C1 to MANIFESTO

### Architecture — post-implementation specs
- [x] **[REF-TASK-0033] Specify CLI experience** — synopsis, arguments, example terminal output, exit codes for all `corvus` commands; document from working IMPL-017
- [x] **[REF-TASK-0034] Specify report output format** — Practitioner and Researcher report sections, mandatory visualizations, audience language; document from working IMPL-014/015
- [x] **[REF-TASK-0035] Add competitive differentiation statement to SRS §2** — 3–6 sentences grounded in MANIFESTO principles; frames Corvus Corone as complementary to COCO/Nevergrad/IOHprofiler

---

## Milestone: V1 Methodology — Statistics & Metrics
> Scientific methodology: ECDF_AREA formalization, statistical test selection, diversity requirements, sensitivity documentation.

- [x] **[REF-TASK-0016] ANYTIME-ECDF_AREA computation procedure** — exact normalization (ADR-007 *(planned)*: empirical min/max) and aggregation across problems
- [x] **[REF-TASK-0017] TIME-EVALUATIONS_TO_TARGET Standard Reporting Set decision** — weigh pre-specification burden vs. efficiency metric value; create ADR
- [x] **[REF-TASK-0020] Statistical test selection procedure** — decision tree: Wilcoxon (2 algorithms) vs Kruskal-Wallis + Holm-Bonferroni (>2); document in `statistical-methodology.md §3`
- [x] **[REF-TASK-0021] Problem instance diversity minimum requirements** — quantitative floor (ADR-008 *(planned)* candidate: ≥5 instances, ≥2 dimensionality ranges, ≥1 noise + ≥1 deterministic)
- [x] **[REF-TASK-0022] Algorithm sensitivity documentation format** — `SensitivityReport` schema field in `AlgorithmInstance`; requires `data-format.md §2.2`
- [x] **[REF-TASK-0019] Level 1 required visualizations** — mandatory EDA set (boxplot, convergence curves, ECDF, violin); document in `statistical-methodology.md §2`
- [x] **[REF-TASK-0015] Metric implementation references** — link each metric definition to `corvus_corone/analysis/metrics.py`; fulfilled as part of IMPL-011
- [ ] **[REF-TASK-0014] Metric taxonomy extensions** *(Post-V1)* — new metrics after first real studies
- [ ] **[REF-TASK-0018] Research question archetypes** *(Post-V1)* — Metric Selection Guide additions from real study patterns

---

## Milestone: V1 Interoperability — Ecosystem Integration
> COCO, Nevergrad, IOHprofiler format mappings. Spike required before implementation.

- [x] **[REF-TASK-0004] Algorithm Author tutorial** — wrap Optuna sampler in ≤ 15 lines; interface acceptance test
- [x] **[REF-TASK-0005] COCO format mapping** *(spike first)* — map Corvus entities to COCO `.info`/`.dat`/`.tdat`; document data loss; round-trip test
- [x] **[REF-TASK-0006] Nevergrad adapter pattern** *(spike first)* — generic `NevergradAdapter`; tutorial; `data-format.md §3` mapping
- [x] **[REF-TASK-0007] IOHprofiler export format mapping** — `.dat` export + `.meta.json` sidecar for unsupported fields; full spec + round-trip test

---

## Milestone: V1 Infrastructure — ADRs & Technical Constraints

- [x] **[REF-TASK-0024] Bulk PerformanceRecord storage format decision** *(spike first)* — benchmark JSON vs Parquet vs HDF5 at 150 k records; create ADR-009

---

## IMPL Phase 0 — Project Setup
> Monorepo initialization. Must complete before any implementation task.

- [x] **`[IMPL-000]`** Setup monorepo: uv workspace, `pyproject.toml` (corvus_corone + corvus_corone_pilot), GitHub Actions CI matrix (ubuntu + macos × Python 3.10/3.11/3.12) · *Refs: ADR-006 *(planned)*, REF-TASK-0011*

---

## IMPL Phase 1 — corvus_corone Library
> Core library: Problem/Algorithm interfaces, Runner, Storage, Analysis, Reporting, Orchestrator, Public API.

- [ ] **`[IMPL-001]`** Problem Interface — `problems/base.py`: `Problem` ABC, `EvaluationResult`, `SearchSpace`; contract test
- [ ] **`[IMPL-002]`** Problem Repository — `problems/registry.py`: `@registry.register` decorator, `discover()`, fail-early validation
- [ ] **`[IMPL-003]`** SearchSpace types — `problems/search_space.py`: `ContinuousVariable`, `IntegerVariable`, `CategoricalVariable` with Pydantic v2
- [ ] **`[IMPL-004]`** Algorithm Interface — `algorithms/base.py`: `Algorithm` ABC (ask-tell: `suggest`, `observe`, `reset`), `AlgorithmInstanceRecord`, `RunContext`
- [ ] **`[IMPL-005]`** Algorithm Registry + RandomSearch — `algorithms/registry.py`, `algorithms/random_search.py`; `numpy.random.default_rng` seed handling
- [ ] **`[IMPL-006]`** Optuna TPE adapter — `algorithms/adapters/optuna_adapter.py` in ≤ 15 lines; tutorial `docs/06_tutorials/01_wrap_optuna_sampler.md` · *Fulfills: REF-TASK-0004*
- [ ] **`[IMPL-007]`** Experiment Runner — `runner/runner.py`: `deepcopy` isolation per run, determinism test, independence test · *Refs: MANIFESTO Principle 18*
- [ ] **`[IMPL-008]`** Seed Manager — `runner/seed_manager.py`: `generate_seeds()` via `numpy.random.SeedSequence.spawn()`
- [ ] **`[IMPL-009]`** Data entities — `storage/entities.py`: `RunRecord`, `PerformanceRecord`, `StudyRecord` (UUID IDs, JSON round-trip) · *Refs: data-format.md §2, ADR-001*
- [ ] **`[IMPL-010]`** Repository interface + LocalFileRepository — `storage/repository.py`: `Repository` ABC, `LocalFileRepository`, `RepositoryContractTest` · *Fulfills: REF-TASK-0023*
- [ ] **`[IMPL-011]`** Metric taxonomy — `analysis/metrics.py`: `@metric` registry; `QUALITY-BEST_VALUE_AT_BUDGET`, `TIME-EVALUATIONS_TO_TARGET`, `RELIABILITY-SUCCESS_RATE`; implementation refs added to `metric-taxonomy.md` · *Fulfills: REF-TASK-0015*
- [ ] **`[IMPL-012]`** Statistical analysis — `analysis/statistical.py`: three-level (exploratory summary, Wilcoxon/Kruskal-Wallis + Holm-Bonferroni, Cliff's delta); `ThreeLevelAnalysis.analyze()` requires all three levels · *Fulfills: REF-TASK-0020*
- [ ] **`[IMPL-013]`** Anytime performance — `analysis/anytime.py`: `compute_anytime_curve`, `compute_ecdf`, `compute_ecdf_area` (empirical normalization per ADR-007 *(planned)*; LOCF per ADR-003); basic IOHprofiler `.dat` export · *Fulfills: REF-TASK-0016*
- [ ] **`[IMPL-014]`** Reporting Engine — `reporting/reports.py`: `StudyReport` (required `scope_statement`, `limitations`); Jinja2 templates for researcher + practitioner reports; raises `ValueError` when scope absent · *Fulfills: REF-TASK-0019*
- [ ] **`[IMPL-015]`** Visualizations — `reporting/visualizations.py`: VIZ-L1-01 boxplot, VIZ-L1-02 convergence curves, VIZ-L1-03 ECDF (`plt.step(where='post')`), VIZ-L1-04 violin (n > 50); auto-generated for every report
- [ ] **`[IMPL-016]`** Study Orchestrator — `orchestrator.py`: `StudyConfig`, `StudyOrchestrator.run()`, diversity validation, `SeedSequence` seed generation, Facade over all modules · *Refs: REF-TASK-0021*
- [ ] **`[IMPL-017]`** Public API + CLI — `api.py`, `cli.py` (Click): `corvus run`, `corvus list-problems`, `corvus list-algorithms`; `CliRunner` tests · *Refs: REF-TASK-0004, NFR-MODULAR-01*

---

## IMPL Phase 2 — Repo Closure
> ADRs, bulk storage after spike, ecosystem bridges (IOHprofiler/COCO/Nevergrad), LLM tools.

- [ ] **`[IMPL-018]`** ADR-006: Technical constraints — `pyproject.toml` `requires-python = ">=3.10"`, MIT license, optional extras (`optuna`, `rag`, `all`), CI license check · *Fulfills: REF-TASK-0011*
- [ ] **`[IMPL-019]`** ADR-007 + ADR-008: ECDF_AREA normalization (empirical min/max, limitations documented) + Standard Reporting Set definition; update `metric-taxonomy.md §3` · *Fulfills: REF-TASK-0016, REF-TASK-0017*
- [ ] **`[IMPL-020]`** ADR-008 + statistical-methodology.md: diversity requirements (≥5 problems, ≥2 dimensionality ranges); Level 1 VIZ-L1-01..03 spec in §2; Wilcoxon/Kruskal decision tree in §3 · *Fulfills: REF-TASK-0019, REF-TASK-0020, REF-TASK-0021*
- [ ] **`[IMPL-021]`** Sensitivity documentation — `SensitivityReport(BaseModel)` in `storage/entities.py`, `data-format.md §2.2`, `contribution-guide.md §2` · *Fulfills: REF-TASK-0022*
- [ ] **`[IMPL-022]`** Bulk PerformanceRecord storage — **blocked on REF-TASK-0024 spike**; ADR-009 from benchmark evidence; `LocalFileRepository.save_bulk_records()`; round-trip test · *Fulfills: REF-TASK-0024*
- [ ] **`[IMPL-023]`** IOHprofiler bridge — `bridge/iohprofiler.py`: full `.dat` export + `.meta.json` sidecar (seed, run_id, wall_time); round-trip test; `data-format.md §3` mapping table · *Fulfills: REF-TASK-0007*
- [ ] **`[IMPL-024]`** COCO bridge — **blocked on REF-TASK-0005 spike**; `bridge/coco_exporter.py`; continuous-only warning; `data-format.md §3` mapping with documented data loss · *Fulfills: REF-TASK-0005*
- [ ] **`[IMPL-025]`** Nevergrad adapter — **blocked on REF-TASK-0006 spike**; `algorithms/adapters/nevergrad_adapter.py`; `ng.p.Dict` → `SearchSpace`; tutorial; `data-format.md §3` mapping · *Fulfills: REF-TASK-0006*
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
- [ ] **`[IMPL-047]`** Portfolio — `README.md` (V1/V2/V3 narrative), `docs/architecture.md` (C1 Mermaid + design philosophy), `demo/demo.py` + `demo/demo_autonomous.py`; demo scripts run in CI

---

## IMPL Phase 4 — Learner Actor
> Learner implementation: Algorithm Visualization Engine, Socratic Guide (LangGraph node), Algorithm Genealogy module.

- [ ] **`[IMPL-044]`** Algorithm Visualization Engine — `learner/visualization_engine.py`: convergence animation, parameter sensitivity heatmap, search trajectory, Pareto front, algorithm genealogy timeline · *Refs: REF-TASK-0027, UC-06*
- [ ] **`[IMPL-045]`** Socratic Guide — `v2_researcher/agents/socratic_guide.py`: LangGraph node activated by `state["interaction_mode"] == "socratic"`, generates bridging questions, never direct answers; CLI `--mode socratic` · *Fulfills: REF-TASK-0028, UC-08*
- [ ] **`[IMPL-046]`** Algorithm Genealogy — `learner/genealogy.py` + `learner/data/genealogy_data.json`: `AlgorithmNode`, `Genealogy` directed graph, lineage (MAB 1933 → BayesOpt 1998 → TPE 2011) and CMA-ES/NSGA-II history; tutorial `docs/06_tutorials/06_algorithm_genealogy_explorer.md` · *Refs: REF-TASK-0030, UC-09*

---

## Learner Actor — Education Platform
> New actor introduced after V1: Learner persona with Algorithm Visualization, Socratic guidance mode, algorithm history/evolution features. Requires C1, SRS, C2, GLOSSARY updates.

- [x] **[REF-TASK-0025] Add Learner actor to C1 context document** — role, goals, gives/gets, relationship to Researcher data flow, C1 diagram update ·
- [x] **[REF-TASK-0026] Add Learner use cases to SRS §3** — UC-06 (visualization), UC-07 (contextual help), UC-08 (Socratic), UC-09 (algorithm history), UC-10 (explore Researcher results) ·
- [x] **[REF-TASK-0027] Add Algorithm Visualization Engine container to C2** — matplotlib/plotly/manim; ADR for technology choice; diagram update ·
- [x] **[REF-TASK-0028] Add Socratic Guide component to C2/C3** — LangGraph `--mode socratic`; guides toward understanding rather than answering ·
- [ ] **[REF-TASK-0029] Add Learner terms to GLOSSARY.md** — Learner, Algorithm Visualization, Algorithm Genealogy, Socratic Mode ·
- [ ] **[REF-TASK-0030] Add Learner education tutorials** — visualization (`UC-06`), Socratic mode (`UC-08`), algorithm genealogy explorer (`UC-09`) ·

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
                           ├──► data-format.md update (REF-TASK-0022) — after IMPL-021
                           └──► interface-contracts.md (REF-TASK-0023) — after IMPL-010

REF-TASK-0005/0006/0007 spikes ──► IMPL-024/025/023 bridges ──► SRS §7 (REF-TASK-0012)
REF-TASK-0024 spike ──► IMPL-022 bulk storage (ADR-006)

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

## Open Tasks Index

### Documentation Tasks (REF-TASK)

| Task | Milestone | Status |
|---|---|---|
| REF-TASK-0001 — Extend GLOSSARY from interface-contracts and data-format | V1 Core | Blocked on contracts |
| REF-TASK-0002 — Verify Schema Version definition against data-format.md | V1 Core | Blocked on data-format.md §6 |
| REF-TASK-0004 — Define Algorithm Author onboarding tutorial (15-line wrapper) | V1 Interoperability | Blocked on interface-contracts.md §2 |
| REF-TASK-0005 — COCO format mapping in data-format.md §3 | V1 Interoperability | Open (spike first) |
| REF-TASK-0006 — Nevergrad adapter pattern and tutorial | V1 Interoperability | Open (spike first) |
| REF-TASK-0007 — IOHprofiler export format mapping — full spec + round-trip test | V1 Interoperability | Open |
| REF-TASK-0008 — Complete SRS §4, §5, §7, §8 after C2 architecture design | V1 Core | Unblocked |
| REF-TASK-0009 — Expand UC-01 and UC-02 into full use case descriptions | V1 Core | Open |
| REF-TASK-0010 — Add measurable criteria to all NFRs | V1 Core | Open |
| REF-TASK-0011 — Define technical constraints (Python version, OS, dependencies) | V1 Core | Open (fulfilled by IMPL-018) |
| REF-TASK-0012 — Fill SRS §7 Interface Requirements from interop mappings | V1 Core | Blocked on REF-TASK-0005/0006/0007 |
| REF-TASK-0013 — Fill SRS §8 Acceptance Test Strategy | V1 Core | Open |
| REF-TASK-0014 — Review and extend metric definitions after first studies | Post-V1 | Deferred |
| REF-TASK-0015 — Add implementation references to all metric definitions | V1 Methodology | Blocked on analysis module (IMPL-011) |
| REF-TASK-0016 — Formalize ANYTIME-ECDF_AREA computation procedure | V1 Methodology | Open |
| REF-TASK-0017 — Decide whether TIME-EVALUATIONS_TO_TARGET joins Standard Reporting Set | V1 Methodology | Open |
| REF-TASK-0018 — Add research question archetypes to Metric Selection Guide | Post-V1 | Deferred |
| REF-TASK-0019 — Specify required Level 1 visualizations in statistical-methodology.md | V1 Methodology | Blocked on reporting module |
| REF-TASK-0020 — Specify statistical test selection procedure and correction methods | V1 Methodology | Open |
| REF-TASK-0021 — Define minimum diversity requirements for Problem Instance selection | V1 Methodology | Open |
| REF-TASK-0022 — Define sensitivity documentation format in Algorithm Instance schema | V1 Methodology | Blocked on data-format.md §2.2 |
| REF-TASK-0023 — Design the Repository storage abstraction interface | V1 Core | Open (fulfilled by IMPL-010) |
| REF-TASK-0024 — Decide bulk PerformanceRecord storage format (Parquet vs HDF5) | V1 Infrastructure | Open (spike first) |
| REF-TASK-0025 — Add Learner actor to C1 context document | Learner Actor | Open |
| REF-TASK-0026 — Add Learner use cases to SRS §3 (UC-06..UC-10) | Learner Actor | Blocked on REF-TASK-0025 |
| REF-TASK-0027 — Add Algorithm Visualization container to C2 | Learner Actor | Blocked on REF-TASK-0025/0026 |
| REF-TASK-0028 — Add Socratic Guide component to C2/C3 (Pilot V2 extension) | Learner Actor | Blocked on REF-TASK-0025/0026/0027 |
| REF-TASK-0029 — Add Learner terms to GLOSSARY.md | Learner Actor | Blocked on REF-TASK-0025..0028 |
| REF-TASK-0030 — Add Learner education tutorials to docs/06_tutorials/ | Learner Actor | Blocked on REF-TASK-0025..0029 |
| REF-TASK-0032 — Reconcile anti-pattern numbering and add anti-patterns to MANIFESTO | V1 Core | Open (author decision on AP-2 required) |
| REF-TASK-0033 — Specify CLI experience — commands, arguments, terminal output | V1 Core | Blocked on IMPL-017 |
| REF-TASK-0034 — Specify report output format — sections, visualizations, audience language | V1 Core | Blocked on IMPL-014/015 |
| REF-TASK-0035 — Add competitive differentiation statement to SRS §2 | V1 Core | Open |
| REF-TASK-0036 — Document LocalFileRepository directory structure | V1 Core | Blocked on IMPL-010 |
| REF-TASK-0037 — Define public API facade contract (`cc.*` functions, response objects, exceptions) | V1 Core | Open; blocks IMPL-017 |

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
| IMPL-011 — Metric taxonomy | Phase 1 | `analysis/metrics.py`, metric-taxonomy.md refs |
| IMPL-012 — Statistical analysis | Phase 1 | `analysis/statistical.py`, ThreeLevelAnalysis |
| IMPL-013 — Anytime performance | Phase 1 | `analysis/anytime.py`, ECDF, basic .dat export |
| IMPL-014 — Reporting Engine | Phase 1 | `reporting/reports.py`, Jinja2 templates |
| IMPL-015 — Visualizations | Phase 1 | `reporting/visualizations.py`, VIZ-L1-01..04 |
| IMPL-016 — Study Orchestrator | Phase 1 | `orchestrator.py`, StudyConfig, Facade |
| IMPL-017 — Public API + CLI | Phase 1 | `api.py`, `cli.py`, corvus run/list commands · *Blocked on REF-TASK-0037* |
| IMPL-018 — ADR-006 technical constraints | Phase 2 | ADR-006, pyproject.toml finalized |
| IMPL-019 — ADR-007 + ADR-008 ECDF + SRS | Phase 2 | ADR-007/008, metric-taxonomy.md §3 |
| IMPL-020 — ADR-008 + statistical-methodology | Phase 2 | ADR-008, statistical-methodology.md §2/§3 |
| IMPL-021 — Sensitivity documentation | Phase 2 | SensitivityReport schema, data-format.md §2.2 |
| IMPL-022 — Bulk PerformanceRecord storage | Phase 2 | ADR-009, `save_bulk_records()` (spike first) |
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
| IMPL-047 — Portfolio | Phase 3b | README, docs/architecture.md, demo scripts |
