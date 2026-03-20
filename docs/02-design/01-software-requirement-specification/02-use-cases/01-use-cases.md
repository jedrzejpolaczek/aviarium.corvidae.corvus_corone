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
  → docs/04-scientific-practice/01-methodology/01-benchmarking-protocol.md : UC-01 maps to the 8-step protocol
-->

Stakeholders correspond directly to actors defined in `docs/02-design/02-architecture/02-c1-context.md`. Refer there for full actor descriptions; this section states their primary needs and the use cases they drive.

### Researcher

**Primary needs:** A framework that enforces good experimental practice without becoming an obstacle — pre-registration, seed management, independence of Runs, and scoped conclusions should happen automatically.

**Success criteria:** A researcher can go from research question to reproducible, statistically valid analysis report without writing boilerplate statistical code or manually managing seeds and logs.

### Practitioner

**Primary needs:** Clear, scoped summaries of algorithm performance on problem characteristics similar to their application. Explicit limitations — not universal recommendations.

**Success criteria:** A practitioner can identify which Algorithm Instances perform well on their problem class, with explicit scope statements, without needing to understand the full statistical methodology.

### Algorithm Author

**Primary needs:** Minimal friction to contribute a new algorithm. A fair, documented comparison process. Clear provenance for their Implementation.

**Success criteria:** An Algorithm Author wraps an existing optimizer (e.g., an Optuna sampler) in under 15 lines of code and submits it for evaluation. The contribution process is documented in `docs/05-community/01-contribution-guide.md`.

### Learner

**Primary needs:** Minimal friction to explore algorithms visually, contextually, and historically; a system that challenges rather than replaces thinking.

**Success criteria:** A Learner can go from "I've heard of TPE" to understanding its mathematical basis, historical origin, and when to apply it — without the system doing their thinking for them.

---

## Use Case Summary

| ID | Actor | Trigger | Goal | File |
|---|---|---|---|---|
| UC-01 | Researcher | Has a research question about HPO algorithm behavior | Design and execute a reproducible benchmarking Study; receive a statistically valid analysis report | [02-uc-01.md](02-uc-01.md) |
| UC-02 | Algorithm Author | Has a new HPO algorithm or wants to wrap an existing one | Contribute an Implementation; see it fairly evaluated against other Algorithm Instances | [03-uc-02.md](03-uc-02.md) |
| UC-03 | Practitioner | Needs to select an HPO algorithm for an ML project | Find performance summaries scoped to problem characteristics matching their application | [04-uc-03.md](04-uc-03.md) |
| UC-04 | Community Contributor | Discovers a missing Problem Instance type | Contribute a new Problem Instance to the benchmark set | [05-uc-04.md](05-uc-04.md) |
| UC-05 | Researcher | Wants to verify a published study | Reproduce an existing Experiment from its archived Artifacts | [06-uc-05.md](06-uc-05.md) |
| UC-06 | Researcher | Has completed a Study | Export results to IOHprofiler / COCO format for cross-platform comparison | [07-uc-06.md](07-uc-06.md) |
| UC-07 | Learner | Wants to understand how an algorithm works | Receive both mathematical and visual/intuitive representations of the algorithm to minimise introduction cost | [08-uc-07.md](08-uc-07.md) |
| UC-08 | Learner | Wants to understand how/why/where an algorithm works | Receive contextual explanations with theoretical and practical examples so they can independently understand the algorithm | [09-uc-08.md](09-uc-08.md) |
| UC-09 | Learner | Wants to deepen understanding of an algorithm or experimental design | System challenges them with guided questions and leads them toward their own conclusions rather than providing direct answers | [10-uc-09.md](10-uc-09.md) |
| UC-10 | Learner | Wants to understand the historical development of an algorithm | Receive the algorithm's genealogy: predecessor algorithms, historical development, and design choice rationale | [11-uc-10.md](11-uc-10.md) |
