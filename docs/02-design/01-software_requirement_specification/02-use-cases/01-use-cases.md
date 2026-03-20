# Use Cases — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: Describes HOW each stakeholder interacts with the system — the concrete scenarios
that the system must support. Each use case is a contract between a stakeholder and the system.

NARRATIVE POSITION:
  MANIFESTO (WHY) → SRS §1–§2 (WHAT) → Use Cases (HOW stakeholders interact)
  Use Cases → Functional Requirements (what the system must do to support each use case)
  Use Cases → C2 Containers (which containers serve which actors)
  Use Cases → Acceptance Test Strategy (each UC must have a passing end-to-end test)

CONNECTS TO:
  ← docs/01-manifesto/MANIFESTO.md                            : MANIFESTO principles motivate each UC
  ← docs/02-design/02-architecture/c1-context.md              : actors defined there become UC actors here
  → docs/02-design/01-software-requirement-specification/functional-requirements.md : each UC step drives FRs
  → docs/02-design/01-software-requirement-specification/constraints.md             : constraints guard UC boundaries
  → docs/02-design/01-software-requirement-specification/acceptance-test-strategy.md : each UC must be tested
  → docs/03-technical-contracts/data-format.md                : entity schemas referenced in UC flows
  → docs/03-technical-contracts/interface-contracts.md        : interfaces invoked in UC flows
  → docs/04_scientific_practice/methodology/benchmarking-protocol.md : UC-01 maps to the 8-step protocol
-->
Stakeholders correspond directly to actors defined in `docs/02-design/02-architecture/c1-context.md`. Refer there for full actor descriptions; this section states their primary needs and the use cases they drive.

### Researcher

**Primary needs:** A framework that enforces good experimental practice without becoming an obstacle — pre-registration, seed management, independence of Runs, and scoped conclusions should happen automatically.

**Success criteria:** A researcher can go from research question to reproducible, statistically valid analysis report without writing boilerplate statistical code or manually managing seeds and logs.

### Practitioner

**Primary needs:** Clear, scoped summaries of algorithm performance on problem characteristics similar to their application. Explicit limitations — not universal recommendations.

**Success criteria:** A practitioner can identify which Algorithm Instances perform well on their problem class, with explicit scope statements, without needing to understand the full statistical methodology.

### Algorithm Author

**Primary needs:** Minimal friction to contribute a new algorithm. A fair, documented comparison process. Clear provenance for their Implementation.

**Success criteria:** An Algorithm Author wraps an existing optimizer (e.g., an Optuna sampler) in under 15 lines of code and submits it for evaluation. The contribution process is documented in `docs/05_community/contribution-guide.md`.

### Learner

**Primary needs:** Minimal friction to explore algorithms visually, contextually, and historically; a system that challenges rather than replaces thinking.

**Success criteria:** A Learner can go from "I've heard of TPE" to understanding its mathematical basis, historical origin, and when to apply it — without the system doing their thinking for them.

---

## Use Case Summary

| ID | Actor | Trigger | Goal |
|---|---|---|---|
| UC-01 | Researcher | Has a research question about HPO algorithm behavior | Design and execute a reproducible benchmarking Study; receive a statistically valid analysis report |
| UC-02 | Algorithm Author | Has a new HPO algorithm or wants to wrap an existing one | Contribute an Implementation; see it fairly evaluated against other Algorithm Instances |
| UC-03 | Practitioner | Needs to select an HPO algorithm for an ML project | Find performance summaries scoped to problem characteristics matching their application |
| UC-04 | Community Contributor | Discovers a missing Problem Instance type | Contribute a new Problem Instance to the benchmark set |
| UC-05 | Researcher | Wants to verify a published study | Reproduce an existing Experiment from its archived Artifacts |
| UC-06 | Researcher | Has completed a Study | Export results to IOHprofiler / COCO format for cross-platform comparison |
| UC-07 | Learner | Wants to understand how an algorithm works | Receive both mathematical and visual/intuitive representations of the algorithm to minimise introduction cost |
| UC-08 | Learner | Wants to understand how/why/where an algorithm works | Receive contextual explanations with theoretical and practical examples so they can independently understand the algorithm |
| UC-09 | Learner | Wants to deepen understanding of an algorithm or experimental design | System challenges them with guided questions and leads them toward their own conclusions rather than providing direct answers |
| UC-10 | Learner | Wants to understand the historical development of an algorithm | Receive the algorithm's genealogy: predecessor algorithms, historical development, and design choice rationale |

---

## UC-01: Design and Execute a Reproducible Benchmarking Study

**Actor:** Researcher
**Trigger:** Has a research question about HPO algorithm behavior
**Goal:** Execute a reproducible benchmarking Study and receive a statistically valid analysis report

**Preconditions:**
- At least two Algorithm Instances are registered in the Algorithm Registry
- At least one Problem Instance is registered with all characteristics documented
- The Researcher has formulated a specific research question (not a generic ranking request)

**Main Flow:**
1. Researcher defines a research question and records it as the Study's `research_question` field (→ `docs/03-technical-contracts/data-format.md` §2.3 Study)
2. Researcher selects Problem Instances from the Problem Repository, verifying characteristic diversity across the intended test set (→ MANIFESTO Principles 4–5; `docs/02-design/02-architecture/c2-containers.md` Problem Repository)
3. Researcher selects Algorithm Instances to compare and reviews each `configuration_justification` for fairness (→ MANIFESTO Principle 10; `docs/03-technical-contracts/data-format.md` §2.2)
4. Researcher specifies experimental design: repetitions, budget allocation, stopping criteria (→ `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Steps 1–4)
5. Researcher pre-registers hypotheses in the Study record — the system locks the Study plan at this point; no modification to problem set, algorithm set, or hypotheses is permitted after this step (→ `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Step 5; MANIFESTO Principle 16)
6. System executes the Experiment: assigns seeds automatically per the Study's `seed_strategy`, runs each (problem, algorithm) pair independently, records a Performance Record sequence per Run (→ `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Step 6; `docs/03-technical-contracts/interface-contracts.md` Runner interface; `docs/03-technical-contracts/data-format.md` §2.4–§2.6)
7. System computes Standard Reporting Set metrics across all Runs and constructs Result Aggregates (→ `docs/03-technical-contracts/metric-taxonomy.md` Standard Reporting Set; `docs/03-technical-contracts/data-format.md` §2.7)
8. System runs three-level statistical analysis: exploratory (visualizations, summary statistics), confirmatory (pre-registered hypothesis tests, multiple-testing correction), practical significance (effect sizes) (→ `docs/04_scientific_practice/methodology/statistical-methodology.md`)
9. System generates Researcher Report and Practitioner Report, each with an explicit limitations section scoping conclusions to the tested Problem Instances (→ `docs/04_scientific_practice/methodology/benchmarking-protocol.md` Steps 7–8; MANIFESTO Principles 23–25)
10. Researcher receives the reports and a Raw Data export for independent analysis (→ NFR-OPEN-01)

**Postconditions:**
- A completed Experiment record exists with all Run data, seeds, and execution environment archived
- Result Aggregates exist for every (problem, algorithm) pair
- Researcher Report and Practitioner Report are produced
- Raw Data export is available in a machine-readable format
- All Artifacts are versioned and reproducible by a third party from archived materials

**Failure Scenarios:**
- *F1: Insufficient problem diversity* — System warns if the Problem Instance set does not meet minimum diversity requirements (`REF-TASK-0021`)
- *F2: Run failure* — Failed Runs record the failure reason; the Study continues; the analyst is warned if failure rate exceeds threshold (→ `docs/03-technical-contracts/data-format.md` §2.5 Run.status)
- *F3: Pre-registration gate violation* — If the Researcher attempts to modify hypotheses after Step 5, the system rejects the change and records the attempt with a timestamp
- *F4: Seed collision* — System detects and rejects duplicate seeds within an Experiment

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — Principles 1, 4–5, 10, 12–16, 18–22, 23–25
- `docs/02-design/02-architecture/c1-context.md` — Researcher actor definition
- `docs/03-technical-contracts/data-format.md` — §2.3 (Study), §2.4 (Experiment), §2.5 (Run), §2.6 (Performance Record), §2.7 (Result Aggregate)
- `docs/03-technical-contracts/interface-contracts.md` — Runner interface, Analyzer interface
- `docs/03-technical-contracts/metric-taxonomy.md` — Standard Reporting Set
- `docs/04_scientific_practice/methodology/benchmarking-protocol.md` — all 8 steps
- `docs/04_scientific_practice/methodology/statistical-methodology.md` — three-level analysis framework
- `functional-requirements.md`: FR-08, FR-09, FR-10, FR-11, FR-13, FR-14, FR-15, FR-17, FR-18, FR-20, FR-21, FR-22
- `non-functional-requirements.md`: NFR-REPRO-01, NFR-STAT-01, NFR-OPEN-01

---

## UC-02: Contribute an Algorithm Implementation

**Actor:** Algorithm Author
**Trigger:** Has a new HPO algorithm or wants to wrap an existing optimizer
**Goal:** Contribute a new Algorithm Instance that is registered with full provenance and available for fair evaluation

**Preconditions:**
- The Algorithm Author has an existing optimizer (e.g., an Optuna sampler, a scipy.optimize function)
- The optimizer can be wrapped to satisfy the Algorithm interface (→ `docs/03-technical-contracts/interface-contracts.md` Algorithm interface)

**Main Flow:**
1. Author reads the Algorithm interface contract to understand required method signatures (→ `docs/03-technical-contracts/interface-contracts.md` Algorithm interface)
2. Author implements a thin adapter satisfying the interface — common wrappers require ≤15 lines (NFR-USABILITY-01; `docs/05_community/contribution-guide.md`)
3. Author constructs the Algorithm Instance record: `id`, `name`, `algorithm_family`, `hyperparameters`, `configuration_justification`, `code_reference` (version-pinned), `language`, `framework`, `framework_version`, `known_assumptions` (→ `docs/03-technical-contracts/data-format.md` §2.2)
4. Author submits the Algorithm Instance to the Algorithm Registry (→ `docs/02-design/02-architecture/c2-containers.md` Algorithm Registry)
5. System validates: `code_reference` is resolvable and version-pinned; hyperparameter names match declared schema; `configuration_justification` is non-empty; interface is satisfied
6. (Optionally) Author triggers a test run against a known Problem Instance to verify the adapter operates correctly
7. Algorithm Instance is approved and available for inclusion in future Studies

**Postconditions:**
- Algorithm Instance record exists with full provenance (`contributed_by`, `created_at`, `code_reference`)
- The Implementation is version-pinned and independently reproducible
- The Instance appears in the Algorithm Registry for Study design

**Failure Scenarios:**
- *F1: Interface not satisfied* — System rejects registration with specific method signature errors identifying which methods are missing or incorrect
- *F2: Code reference unresolvable* — System rejects registration; `code_reference` must resolve to a pinned, retrievable artifact
- *F3: Missing configuration justification* — System rejects registration; `configuration_justification` cannot be empty (MANIFESTO Principle 10)
- *F4: Hyperparameter schema mismatch* — System rejects if declared hyperparameter names do not match the algorithm's known parameter schema

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — Principles 8, 10, 11, 19, 31
- `docs/02-design/02-architecture/c1-context.md` — Algorithm Author actor definition
- `docs/03-technical-contracts/data-format.md` — §2.2 (Algorithm Instance)
- `docs/03-technical-contracts/interface-contracts.md` — Algorithm interface contract
- `docs/05_community/contribution-guide.md` — contribution process and review
- `functional-requirements.md`: FR-05, FR-06, FR-07
- `non-functional-requirements.md`: NFR-MODULAR-01, NFR-USABILITY-01

---

## UC-03: Select an HPO Algorithm for an ML Project

**Actor:** Practitioner
**Trigger:** Needs to select an HPO algorithm for an ML project
**Goal:** Find performance summaries scoped to problem characteristics matching their application, with explicit scope statements

**Preconditions:**
- Published Study results exist covering problem characteristics similar to the Practitioner's application

**Main Flow:**
1. Practitioner identifies their problem characteristics: search space dimension, variable types, noise level, budget constraints
2. Practitioner browses available Study results filtered by problem characteristics matching their application
3. Practitioner reads the Practitioner Report for relevant Studies: performance of Algorithm Instances on matching Problem Instances, with explicit scope statements (→ MANIFESTO Principle 25; FR-20)
4. Practitioner reads the limitations section of each report to understand the scope boundary of every conclusion (→ MANIFESTO Principle 24; CONST-SCI-06)
5. Practitioner identifies Algorithm Instances that perform consistently on their matching problem class (→ MANIFESTO Principle 2)
6. Practitioner makes an informed selection — the system provides evidence, not a recommendation (CONST-SCI-03)

**Postconditions:**
- Practitioner has reviewed evidence scoped to their problem class
- Practitioner has read the explicit limitations of those conclusions

**Failure Scenarios:**
- *F1: No matching Problem Instances* — System indicates that no Studies cover the Practitioner's problem characteristics; the system does not extrapolate beyond tested instances (CONST-SCI-06)

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — Principles 2, 3, 24, 25
- `docs/02-design/02-architecture/c1-context.md` — Practitioner actor definition
- `functional-requirements.md`: FR-20, FR-21
- `constraints.md`: CONST-SCI-03, CONST-SCI-06

---

## UC-04: Contribute a New Problem Instance

**Actor:** Community Contributor
**Trigger:** Discovers a benchmark gap — a problem type not represented in the current set
**Goal:** Contribute a new Problem Instance that enriches the benchmark's characteristic diversity

**Preconditions:**
- The Problem Instance has fully documented characteristics (dimension, variable types, bounds, noise level, known optimum if available, landscape characteristics)
- The Problem Instance is not a near-duplicate of an existing registered instance

**Main Flow:**
1. Contributor reads the Problem Instance schema to understand required fields (→ `docs/03-technical-contracts/data-format.md` §2.1)
2. Contributor constructs the Problem Instance record: `id`, `name`, `version`, search space descriptors, objective specification, evaluation budget, `landscape_characteristics`, provenance fields (`created_by`, `source_reference`) (→ `docs/03-technical-contracts/data-format.md` §2.1)
3. Contributor submits the record to the Problem Repository (→ `docs/02-design/02-architecture/c2-containers.md` Problem Repository)
4. System validates completeness: all required fields present; `dimensions` equals `len(variables)`; variable bounds valid for each variable type (→ `docs/03-technical-contracts/data-format.md` §2.1 validation rules)
5. Governance review verifies the contribution adds diversity rather than duplication (→ `docs/05_community/versioning-governance.md`)
6. Problem Instance is published with a version number and added to the benchmark set

**Postconditions:**
- Problem Instance record exists with full provenance
- The Problem Instance is available for inclusion in new Studies

**Failure Scenarios:**
- *F1: Incomplete documentation* — System rejects submission if required fields are missing; rejection message lists the missing fields
- *F2: Duplicate detection* — System warns if the submitted characteristic profile is within tolerance of an existing instance; contributor must justify the addition

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — Principles 4, 5, 6, 7, 27
- `docs/02-design/02-architecture/c1-context.md` — Community Contributor actor definition
- `docs/03-technical-contracts/data-format.md` — §2.1 (Problem Instance)
- `docs/05_community/versioning-governance.md` — governance and review process
- `functional-requirements.md`: FR-01, FR-02, FR-03
- `non-functional-requirements.md`: NFR-MODULAR-01

---

## UC-05: Verify a Published Study

**Actor:** Researcher
**Trigger:** Wants to independently verify claims of a published benchmarking Study
**Goal:** Re-execute the Study from archived Artifacts and document agreement or measured divergence

**Preconditions:**
- The Study's Artifacts are published in an open repository (code, data, seeds, procedures)
- The Researcher has access to compatible execution environment specifications

**Main Flow:**
1. Researcher retrieves the archived Study record: Study plan, Algorithm Instance versions, Problem Instance versions, seed assignments (→ MANIFESTO Principle 19; `docs/03-technical-contracts/data-format.md` §2.3–§2.5)
2. Researcher reconstructs the execution environment matching the recorded `execution_environment` specification (→ `docs/03-technical-contracts/data-format.md` §2.4 Experiment)
3. Researcher re-runs the Experiment using the archived Study plan — seeds come from the archived Run records, not re-generated
4. System produces a new Experiment record linked to the same Study ID
5. Researcher compares Result Aggregates between the original and verification Experiments (→ `docs/03-technical-contracts/data-format.md` §2.7)
6. Researcher documents agreement or measured divergence with explanation — both outcomes are valid scientific results and should be published

**Postconditions:**
- A new Experiment record exists representing the verification run, linked to the original Study
- Agreement or divergence is documented with the verification Experiment

**Failure Scenarios:**
- *F1: Missing Artifacts* — If code or data is not publicly available, verification is impossible; the system records this as a limitation of the original Study
- *F2: Incompatible execution environment* — The Researcher documents the platform difference; the system does not silently substitute alternatives or adjust seeds

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — Principles 19, 20, 21, 22
- `docs/02-design/02-architecture/c1-context.md` — Researcher actor definition
- `docs/03-technical-contracts/data-format.md` — §2.3 (Study), §2.4 (Experiment), §2.5 (Run), §2.7 (Result Aggregate)
- `docs/05_community/versioning-governance.md` — Artifact versioning policy
- `functional-requirements.md`: FR-17, FR-18, FR-19
- `non-functional-requirements.md`: NFR-REPRO-01

---

## UC-06: Export Results to an External Platform

**Actor:** Researcher
**Trigger:** Has completed a Study and wants to compare results with data from COCO, IOHprofiler, or Nevergrad
**Goal:** Produce an export file in the target platform's format, with any information loss explicitly documented

**Preconditions:**
- A completed Experiment exists with Performance Records and Result Aggregates
- The target platform's format mapping is documented (→ `docs/03-technical-contracts/data-format.md` §4)

**Main Flow:**
1. Researcher selects a completed Experiment and a target export format (COCO, IOHprofiler `.dat`, Nevergrad)
2. System applies the format mapping for the selected target (→ `docs/03-technical-contracts/data-format.md` §4 Interoperability Mappings)
3. System reports all information loss: fields in the Corvus Corone schema that have no equivalent in the target format are listed explicitly before the export is produced
4. Researcher confirms and receives the export file ready for loading in the target platform
5. (Optionally) Researcher loads the file into the target platform for cross-platform visualization or comparison

**Postconditions:**
- Export file is produced in the target format
- An information-loss manifest is produced alongside the export, documenting every field that was dropped or approximated

**Failure Scenarios:**
- *F1: Unsupported format* — System lists supported export formats and refuses to produce a partial export for an unsupported target
- *F2: Mandatory target field missing* — If the target format requires a field not captured in the Run data, the system rejects the export with an explicit error identifying the missing field

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — Principle 26
- `docs/02-design/02-architecture/c1-context.md` — external systems: COCO, IOHprofiler, Nevergrad
- `docs/03-technical-contracts/data-format.md` — §4 (Interoperability Mappings)
- `docs/03-technical-contracts/interface-contracts.md` — Ecosystem Bridge interface
- `functional-requirements.md`: FR-23, FR-24, FR-25, FR-26
- `non-functional-requirements.md`: NFR-INTEROP-01

---

## UC-07: Algorithm Visualisation

**Actor:** Learner
**Trigger:** Wants to understand how an HPO algorithm works and needs both mathematical and visual/intuitive entry points
**Goal:** Receive a mathematical description and a visual/intuitive representation of the algorithm that minimises introduction cost for non-experts

**Preconditions:**
- The algorithm is registered in the Algorithm Registry
- Study results exist for the algorithm (required for data-driven visualisations such as convergence plots and search trajectories)

**Main Flow:**
1. Learner selects an algorithm by name (e.g., "TPE") from the available Algorithm Registry
2. System presents the mathematical specification of the algorithm: objective function structure, probability model, acquisition function or sampling rule
3. System generates intuitive visualisations derived from recorded study data: animated convergence, parameter sensitivity heatmap, search trajectory scatter, algorithm genealogy timeline
4. Learner can request a specific visualisation type (convergence, sensitivity, trajectory, genealogy) or receive all at once
5. Each visualisation is labelled with the concept it represents and linked to the corresponding mathematical element from Step 2
6. Learner can adjust the study or algorithm instance used as the data source for the visualisation

**Postconditions:**
- Learner has received both a mathematical description and at least one visual representation of the algorithm
- Each visual element is explicitly linked to its corresponding mathematical concept

**Failure Scenarios:**
- *F1: No study data for algorithm* — System presents the mathematical specification only and notes that data-driven visualisations require at least one completed Study
- *F2: Algorithm not registered* — System returns a not-found error listing available algorithms; it does not fabricate a visualisation

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — principles relevant to education and accessible understanding (note: Learner Actor section not yet present in MANIFESTO as of this writing)
- `docs/02-design/02-architecture/c1-context.md` — Learner actor definition (REF-TASK-0025)
- `functional-requirements.md`: no existing FR yet — Learner actor FRs to be added in a future task
- REF-TASK-0027
- IMPL-044

---

## UC-08: Contextual Algorithm Help

**Actor:** Learner
**Trigger:** Wants to understand how an algorithm works, why it works, and where it works best
**Goal:** Receive contextual explanations with theoretical depth and practical examples so the Learner can independently understand the algorithm without requiring researcher-level expertise

**Preconditions:**
- The algorithm is registered in the Algorithm Registry
- An LLM-powered explanation module is available

**Main Flow:**
1. Learner poses a contextual question about an algorithm: "How does TPE work?", "Why does CMA-ES use a covariance matrix?", or "Where does Bayesian optimisation perform best?"
2. System identifies the question type (how / why / where) and selects the appropriate explanation strategy
3. System generates a theoretical explanation: the mechanism of the algorithm, its mathematical basis, the problem it was designed to solve
4. System supplements the theoretical explanation with practical examples drawn from recorded study data where available: problem types where the algorithm excels, characteristic failure modes, comparisons against alternatives on similar problems
5. System explicitly marks the boundary between established algorithm mechanics (what this module explains) and open research conclusions (which are not provided here — see UC-09 for Socratic exploration of research questions)
6. Learner can ask follow-up questions; the system answers within the established mechanics scope, redirecting to Socratic mode (UC-09) when the question moves into experimental-design territory

**Postconditions:**
- Learner has received a how/why/where explanation grounded in established algorithm theory
- Practical examples have been provided alongside the theoretical account
- The boundary between established mechanics and open research conclusions is explicit

**Failure Scenarios:**
- *F1: Question outside algorithm mechanics scope* — System redirects to Socratic mode (UC-09) rather than fabricating a conclusion; it states explicitly that the question requires experimental reasoning rather than established fact
- *F2: Algorithm not registered* — System returns a not-found error; it does not generate an explanation for an unknown algorithm

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — principles relevant to education and accessible understanding (note: Learner Actor section not yet present in MANIFESTO as of this writing)
- `docs/02-design/02-architecture/c1-context.md` — Learner actor definition (REF-TASK-0025)
- `functional-requirements.md`: no existing FR yet — Learner actor FRs to be added in a future task
- REF-TASK-0026
- IMPL-048

---

## UC-09: Socratic Guided Deduction

**Actor:** Learner
**Trigger:** Wants to deepen understanding of an algorithm or experimental design question
**Goal:** System challenges the Learner with guided questions and leads them toward their own conclusions rather than providing direct answers; applies to both algorithm understanding and experimental design reasoning

**Preconditions:**
- The Learner has a question about algorithm behaviour or experimental design
- Socratic interaction mode is active (explicit opt-in or detected from question type)

**Main Flow:**
1. Learner poses a question that involves reasoning or experimental judgment: "Which algorithm should I use for my problem?", "Is TPE better than random search?", or "What budget should I assign to this study?"
2. System identifies that the question requires reasoning rather than factual recall, and activates Socratic mode
3. System identifies what the Learner already knows from prior conversation context
4. System identifies the gap between the Learner's current knowledge state and the conclusion they are seeking
5. System generates a bridging question that nudges the Learner one reasoning step forward without providing the answer
6. Learner responds; system evaluates whether the response closes the gap or reveals a new knowledge gap
7. Steps 5–6 repeat until the Learner has reasoned their way to a conclusion independently
8. System confirms the Learner's conclusion if correct, or identifies the specific point of error without providing the corrected answer directly

**Postconditions:**
- Learner has arrived at a conclusion through their own reasoning process
- The system has not provided the conclusion directly at any point in the interaction

**Failure Scenarios:**
- *F1: Learner requests direct answer* — System acknowledges the request, explains that Socratic mode requires independent reasoning, and offers to exit Socratic mode if the Learner chooses; it does not provide the direct answer while in Socratic mode
- *F2: Reasoning loop detected* — If the Learner repeats the same incorrect reasoning step three times, the system changes the bridging question strategy rather than continuing to ask the same question

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — principles relevant to education and accessible understanding (note: Learner Actor section not yet present in MANIFESTO as of this writing)
- `docs/02-design/02-architecture/c1-context.md` — Learner actor definition (REF-TASK-0025)
- `functional-requirements.md`: no existing FR yet — Learner actor FRs to be added in a future task
- REF-TASK-0028
- IMPL-045

---

## UC-10: Algorithm History and Evolution

**Actor:** Learner
**Trigger:** Wants to understand the historical development and intellectual genealogy of an HPO algorithm
**Goal:** Receive the algorithm's genealogy — predecessor algorithms, historical development timeline, and rationale behind key design choices — so the Learner builds comprehensive understanding of why the algorithm is designed the way it is

**Preconditions:**
- The algorithm is registered in the Algorithm Registry
- Genealogy data for the algorithm exists in the system's genealogy data store

**Main Flow:**
1. Learner selects an algorithm and requests its history (e.g., "Show me the history of TPE")
2. System retrieves the algorithm's genealogy record: year of origin, authors, the problem it was designed to solve, predecessor algorithms it built on, successor algorithms it inspired
3. System presents the lineage as a timeline: each predecessor is described with the specific problem it solved and the specific limitation that motivated the next step in the lineage
4. System highlights the design choices that distinguish the target algorithm from its predecessors, connecting each design choice to the problem it addressed
5. Learner can navigate the genealogy graph: selecting any ancestor or descendant algorithm to view its own history record
6. System links the historical account to the corresponding visualisation (UC-07) and contextual explanation (UC-08) for each algorithm in the lineage

**Postconditions:**
- Learner has received a genealogy record covering the algorithm's key predecessors and the design decisions that connect them
- Each design choice in the lineage is connected to the problem it was invented to solve

**Failure Scenarios:**
- *F1: No genealogy data for algorithm* — System notes that genealogy data is not yet available for the selected algorithm and lists algorithms for which genealogy data exists
- *F2: Algorithm not registered* — System returns a not-found error; it does not fabricate a historical account

**Connects to:**
- `docs/01-manifesto/MANIFESTO.md` — principles relevant to education and accessible understanding (note: Learner Actor section not yet present in MANIFESTO as of this writing)
- `docs/02-design/02-architecture/c1-context.md` — Learner actor definition (REF-TASK-0025)
- `functional-requirements.md`: no existing FR yet — Learner actor FRs to be added in a future task
- REF-TASK-0030
- IMPL-046
