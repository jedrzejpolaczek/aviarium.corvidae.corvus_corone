# Software Requirements Specification — Corvus Corone: HPO Algorithm Benchmarking Platform

<!--
STORY ROLE: The "contract of capabilities". Translates the WHY (MANIFESTO) into verifiable WHAT.
Every requirement here must be traceable to at least one MANIFESTO principle,
and every MANIFESTO principle should produce at least one requirement.

NARRATIVE POSITION:
  MANIFESTO (WHY) → SRS → (WHAT the system must do)
  C1 (actors) feeds §3 (stakeholders and use cases)
  C2 (containers) feeds §4 (functional requirement grouping)
  SRS §7 feeds → docs/03_technical_contracts/interface-contracts.md and docs/03_technical_contracts/data-format.md (how)
  SRS §8 feeds → tasks/tickets (what to test and verify)

CONNECTS TO:
  ← docs/01_manifesto/MANIFESTO.md                              : principles are the source of requirements
  ← docs/02_design/02_architecture/c1-context.md               : actors become stakeholders; external systems become interface requirements
  ← docs/02_design/02_architecture/c2-containers.md            : container grouping organizes §4 (TODO: REF-TASK-0008)
  → docs/03_technical_contracts/data-format.md                  : §7 data requirements are detailed there
  → docs/03_technical_contracts/interface-contracts.md          : §7 interface requirements are formalized there
  → docs/04_scientific_practice/methodology/statistical-methodology.md : §5 NFR-STAT operationalized there
  → docs/05_community/versioning-governance.md                  : §5 NFR-REPRO operationalized there
  → docs/02_design/02_architecture/adr/                         : when a requirement drives an architectural decision, link the ADR
  → docs/05_community/TASKS.md                                  : each requirement ID (FR-XX, NFR-XX) should be referenced in tasks
  → docs/GLOSSARY.md                                            : all terms used in requirement descriptions are defined there
-->

---

## 1. Introduction

### Purpose

This document specifies the software requirements for the Corvus Corone: HPO Algorithm Benchmarking Platform — a Python library that enables rigorous, reproducible benchmarking of hyperparameter optimization algorithms. It is intended for:

- **Library developers** implementing the system
- **Community contributors** designing new features or extending the platform
- **Researchers** evaluating the system's fitness for their scientific needs
- **External reviewers** assessing compliance with benchmarking best practices

### Scope

The system is a **Python library** that a user integrates by providing an algorithm Implementation; the library then handles Study execution, measurement, statistical analysis, and report generation automatically. The core value proposition is: *wrap your algorithm, get rigorous benchmarking*.

What is explicitly out of scope is defined in `docs/02_design/02_architecture/c1-context.md` — Explicit Scope Exclusions. The most important exclusion: this system does not produce algorithm rankings.

### Relationship to MANIFESTO

This document operationalizes `docs/01_manifesto/MANIFESTO.md`. Where the MANIFESTO states values ("we value X over Y"), this SRS states verifiable requirements. Every requirement in §4–§5 must trace to at least one MANIFESTO Principle; a requirement without a source is a candidate for removal. The traceability matrix in §9 makes this relationship explicit.

### Document Status

**Version:** 0.1 (initial — §4, §5, §7, §8 pending architectural decisions)

> **`TODO: REF-TASK-0008`** — Complete §4 Functional Requirements, §5 NFRs (measurable criteria),
> §7 Interface Requirements, and §8 Acceptance Test Strategy once C2 containers are designed.
> Owner: technical lead. Acceptance: all MANIFESTO principles map to at least one FR or NFR with
> measurable acceptance criteria; §9 traceability matrix is complete.

---

## 2. System Overview

The Corvus Corone: HPO Algorithm Benchmarking Platform is a Python library designed to serve the discovery of truth about hyperparameter optimization algorithm performance. A researcher wraps their algorithm in a thin adapter implementing the Algorithm Interface, specifies a Study (research question, problem selection, experimental design), and receives in return: automated execution of reproducible Runs, full Anytime Performance curves, three-level statistical analysis, and multi-audience reports — all without manual instrumentation.

The system prioritizes scientific validity over convenience: it enforces pre-registration of hypotheses, controls and records all sources of randomness, and scopes every conclusion to the Problem Instances actually tested. It does not tell the researcher which algorithm is "best"; it helps them answer the specific question they asked.

For context on who uses the system and what surrounds it, see `docs/02_design/02_architecture/c1-context.md`. For the values that shaped these design choices, see `docs/01_manifesto/MANIFESTO.md`.

---

## 3. Stakeholders and Use Cases

Stakeholders correspond directly to actors defined in `docs/02_design/02_architecture/c1-context.md`. Refer there for full actor descriptions; this section states their primary needs and the use cases they drive.

### Researcher

**Primary needs:** A framework that enforces good experimental practice without becoming an obstacle — pre-registration, seed management, independence of Runs, and scoped conclusions should happen automatically.

**Success criteria:** A researcher can go from research question to reproducible, statistically valid analysis report without writing boilerplate statistical code or manually managing seeds and logs.

### Practitioner

**Primary needs:** Clear, scoped summaries of algorithm performance on problem characteristics similar to their application. Explicit limitations — not universal recommendations.

**Success criteria:** A practitioner can identify which Algorithm Instances perform well on their problem class, with explicit scope statements, without needing to understand the full statistical methodology.

### Algorithm Author

**Primary needs:** Minimal friction to contribute a new algorithm. A fair, documented comparison process. Clear provenance for their Implementation.

**Success criteria:** An Algorithm Author wraps an existing optimizer (e.g., an Optuna sampler) in under 15 lines of code and submits it for evaluation. The contribution process is documented in `docs/05_community/contribution-guide.md`.

### Use Cases

| ID | Actor | Trigger | Goal |
|---|---|---|---|
| UC-01 | Researcher | Has a research question about HPO algorithm behavior | Design and execute a reproducible benchmarking Study; receive a statistically valid analysis report |
| UC-02 | Algorithm Author | Has a new HPO algorithm or wants to wrap an existing one | Contribute an Implementation; see it fairly evaluated against other Algorithm Instances |
| UC-03 | Practitioner | Needs to select an HPO algorithm for an ML project | Find performance summaries scoped to problem characteristics matching their application |
| UC-04 | Community Contributor | Discovers a missing Problem Instance type | Contribute a new Problem Instance to the benchmark set |
| UC-05 | Researcher | Wants to verify a published study | Reproduce an existing Experiment from its archived Artifacts |
| UC-06 | Researcher | Has completed a Study | Export results to IOHprofiler / COCO format for cross-platform comparison |

> **`TODO: REF-TASK-0009`** — Expand UC-01 and UC-02 into full use case descriptions (main flow,
> preconditions, postconditions, failure scenarios) once the library's API surface is defined in C2/C3.
> Owner: technical lead. Acceptance: each expanded use case has a corresponding tutorial in
> `docs/06_tutorials/` and a passing end-to-end test.

---

## 4. Functional Requirements

> **`TODO: REF-TASK-0008`** — This section requires C2 containers to be designed first. The
> subsection headers below are placeholders matching expected container names; fill each subsection
> with formal FR-XX requirements once the architecture is settled. See the traceability hints in §9.

### 4.1 Problem Repository
*Requirements for storing, retrieving, versioning, and validating benchmark Problem Instances. Derives from MANIFESTO Principles 4–7.*

### 4.2 Algorithm Registry
*Requirements for registering, configuring, and managing Algorithm Implementations. Must enforce the Algorithm / Algorithm Instance / Implementation distinction (Principle 8).*

### 4.3 Experiment Runner
*Requirements for executing Studies, managing seeds, enforcing Run independence. Derives from MANIFESTO Principles 16–18.*

### 4.4 Measurement & Analysis Engine
*Requirements for collecting Performance Records, computing metrics, running three-level statistical analysis. Derives from MANIFESTO Principles 12–15. Metrics defined in `docs/03_technical_contracts/metric-taxonomy.md`; methodology in `docs/04_scientific_practice/methodology/statistical-methodology.md`.*

### 4.5 Reproducibility Layer
*Requirements for versioning Artifacts, open data publication, and long-term storage. Derives from MANIFESTO Principles 19–22. Policy operationalized in `docs/05_community/versioning-governance.md`.*

### 4.6 Reporting & Visualization
*Requirements for multi-audience report generation, visualization, and explicit limitation communication. Derives from MANIFESTO Principles 23–25.*

### 4.7 Ecosystem Integration
*Requirements for COCO, Nevergrad, and IOHprofiler compatibility. Derives from MANIFESTO Principles 26–28. Format mappings in `docs/03_technical_contracts/data-format.md` §3.*

---

## 5. Non-Functional Requirements

> **`TODO: REF-TASK-0010`** — Add measurable criteria (numbers, thresholds, test conditions) to
> each NFR once architectural decisions establish the system's target scale and platform.
> Owner: technical lead. Acceptance: each NFR has at least one measurable criterion that can
> be evaluated by an automated test or benchmark.

### NFR-REPRO-01: Reproducibility

**Description:** Every Experiment can be exactly re-executed by a different team using the archived Artifacts (code, data, seeds, procedures) to produce identical results.

**Source:** MANIFESTO Principles 19–22.

**Measurable criterion:** `TODO: REF-TASK-0010` — define bit-for-bit vs. numerical tolerance; platform constraints.

**Operationalized in:** `docs/05_community/versioning-governance.md`.

---

### NFR-STAT-01: Statistical Validity

**Description:** All analysis outputs comply with the three-level analysis methodology — no study report is produced without exploratory, confirmatory, and practical significance analysis.

**Source:** MANIFESTO Principles 13, 15.

**Measurable criterion:** `TODO: REF-TASK-0010` — define automated checks for mandatory analysis steps.

**Operationalized in:** `docs/04_scientific_practice/methodology/statistical-methodology.md`.

---

### NFR-INTEROP-01: Ecosystem Interoperability

**Description:** Results can be exported to COCO, Nevergrad, and IOHprofiler formats without data loss beyond the documented field mappings in `docs/03_technical_contracts/data-format.md` §3.

**Source:** MANIFESTO Principle 26.

**Measurable criterion:** `TODO: REF-TASK-0010` — round-trip test criteria per platform.

---

### NFR-OPEN-01: Open Data and Code

**Description:** All experimental data, algorithm code, and analysis scripts are publicly available under open licenses in standardized, well-documented formats.

**Source:** MANIFESTO Principles 20, 22.

**Measurable criterion:** `TODO: REF-TASK-0010` — license type, format approval list.

**Operationalized in:** `docs/05_community/versioning-governance.md` §5.

---

### NFR-MODULAR-01: Extensibility

**Description:** Adding a new Problem Instance or Algorithm Implementation requires only implementing the defined interface — no modification of existing system code.

**Source:** MANIFESTO Value 6 (System adaptability), Principle 27 (community development).

**Measurable criterion:** `TODO: REF-TASK-0010` — plugin test: new algorithm contributes and runs without modifying core library files.

**Operationalized in:** `docs/03_technical_contracts/interface-contracts.md`.

---

### NFR-USABILITY-01: Minimal Onboarding Friction

**Description:** A researcher familiar with Python can wrap an existing HPO optimizer and run their first benchmarking Study in under 30 minutes from installation.

**Source:** MANIFESTO Principle 28 (education and support), user requirement (Python library, minimal boilerplate).

**Measurable criterion:** `TODO: REF-TASK-0010` — define the "first study" tutorial and measure completion time in user testing.

---

## 6. Constraints

### Scientific Constraints

These derive directly from MANIFESTO anti-patterns and are hard constraints — not design preferences.

| Constraint | MANIFESTO Anti-Pattern | Statement |
|---|---|---|
| CONST-SCI-01 | Anti-pattern 1 (Algorithm ranking) | The system MUST NOT produce or display global algorithm rankings or "best algorithm" declarations |
| CONST-SCI-02 | Anti-pattern 3 (Competition) | The system MUST NOT support competition-style scoring or leaderboard features |
| CONST-SCI-03 | Anti-pattern 7 (Substitute for thinking) | The system MUST NOT make algorithm selection decisions on behalf of the user; it produces evidence, not recommendations |
| CONST-SCI-04 | Anti-pattern 4 (Black box) | Every analysis step performed by the system MUST be inspectable, documented, and reproducible by the user independently |
| CONST-SCI-05 | Anti-pattern 6 (Marketing tool) | Every generated report MUST include an explicit limitations section stating the scope conditions of conclusions |
| CONST-SCI-06 | Principle 3 | Conclusions in any system-generated output MUST be scoped to the Problem Instances actually tested; extrapolations MUST be explicitly labeled |

### Community Constraints

| Constraint | Source | Statement |
|---|---|---|
| CONST-COM-01 | MANIFESTO Principle 20 | All source code MUST be released under an open source license |
| CONST-COM-02 | MANIFESTO Principle 20 | All experimental data and results produced by the system MUST be publishable under an open data license |
| CONST-COM-03 | MANIFESTO Principle 22 | All data formats used for archival MUST be open, well-documented, and readable without proprietary tools |

### Technical Constraints

> **`TODO: REF-TASK-0011`** — Define technical constraints (Python version minimum, OS support,
> dependency restrictions, platform targets) once the first architecture decisions are made.
> Owner: technical lead. Acceptance: constraints are recorded as ADRs in
> `docs/02_design/02_architecture/adr/`.

---

## 7. Interface Requirements

> **`TODO: REF-TASK-0012`** — Fill this section once `docs/03_technical_contracts/interface-contracts.md`
> is completed. For each external system in C1, state: what interface must be supported, direction,
> data format, and failure handling. Owner: ecosystem integration lead.

External systems that require interface specifications (from `docs/02_design/02_architecture/c1-context.md`):
- COCO export interface
- Nevergrad import/export interface
- IOHprofiler export interface
- HPC/Cloud job submission interface *(V1 scope TBD — `TODO: REF-TASK-0003`)*
- Artifact Repository publication interface

---

## 8. Acceptance Test Strategy

> **`TODO: REF-TASK-0013`** — Define test categories and connect requirement IDs to test files once
> C2/C3 architecture and interface contracts are designed. Owner: QA / technical lead.

Test categories planned:

| Category | Purpose | Derives from |
|---|---|---|
| Unit tests | Component behavior in isolation | C3 components (`TODO: REF-TASK-0008`) |
| Integration tests | Container interaction flows | C2 containers (`TODO: REF-TASK-0008`) |
| Reproducibility tests | Same Study → identical Experiment results | NFR-REPRO-01 |
| Statistical validity tests | Analysis outputs meet three-level methodology | NFR-STAT-01 |
| Interoperability tests | Export round-trips to COCO/IOHprofiler/Nevergrad | NFR-INTEROP-01 |
| Usability tests | First-study completion time | NFR-USABILITY-01 |

---

## 9. Requirements Traceability Matrix

Partial matrix — populated from MANIFESTO-derivable content. Container and test columns require `TODO: REF-TASK-0008`.

| Req ID | MANIFESTO Principle | Section | C2 Container | Status |
|---|---|---|---|---|
| CONST-SCI-01 | Anti-pattern 1 | §6 | N/A | Defined |
| CONST-SCI-02 | Anti-pattern 3 | §6 | N/A | Defined |
| CONST-SCI-03 | Anti-pattern 7 | §6 | N/A | Defined |
| CONST-SCI-04 | Anti-pattern 4 | §6 | N/A | Defined |
| CONST-SCI-05 | Anti-pattern 6 | §6 | N/A | Defined |
| CONST-SCI-06 | Principle 3 | §6 | N/A | Defined |
| CONST-COM-01 | Principle 20 | §6 | N/A | Defined |
| CONST-COM-02 | Principle 20 | §6 | N/A | Defined |
| CONST-COM-03 | Principle 22 | §6 | N/A | Defined |
| NFR-REPRO-01 | Principles 19–22 | §5 | Reproducibility Layer | Criteria pending |
| NFR-STAT-01 | Principles 13, 15 | §5 | Analysis Engine | Criteria pending |
| NFR-INTEROP-01 | Principle 26 | §5 | Ecosystem Integration | Criteria pending |
| NFR-OPEN-01 | Principles 20, 22 | §5 | All | Criteria pending |
| NFR-MODULAR-01 | Value 6, Principle 27 | §5 | All | Criteria pending |
| NFR-USABILITY-01 | Principle 28 | §5 | Library API | Criteria pending |
| UC-01 | Principles 1, 13, 16 | §3 | TBD | Pending C2 |
| UC-02 | Principles 8, 10, 31 | §3 | TBD | Pending C2 |
| UC-03 | Principles 2, 24, 25 | §3 | TBD | Pending C2 |
| UC-04 | Principles 4–7, 27 | §3 | TBD | Pending C2 |
| UC-05 | Principles 19–22 | §3 | TBD | Pending C2 |
| UC-06 | Principle 26 | §3 | TBD | Pending C2 |
