# Versioning and Data Governance Policy

<!--
STORY ROLE: The "rules of the archive". Without this, reproducibility is a promise, not a guarantee.
When a researcher runs the same study two years from now, this document is what ensures they can.

NARRATIVE POSITION:
  MANIFESTO Principles 19–22 → Versioning & Governance → (operational reproducibility rules)
  → This document is enforced by the Reproducibility Layer container (C2)

CONNECTS TO:
  ← MANIFESTO Principles 19–22 : directly operationalized here
  ← SRS NFR-REPRO, NFR-OPEN    : non-functional requirements this policy implements
  → docs/03-technical-contracts/01-data-format/13-schema-versioning.md     : schema versioning details delegate to this policy
  → docs/05-community/01-contribution-guide.md : contributions enter the versioning pipeline described here
  → architecture/adr/           : versioning scheme choices (e.g., semantic vs. date-based) need ADRs

GOVERNANCE PRINCIPLE: This policy applies equally to all artifact types.
No artifact is "too small" to version, and no version is deleted once published.
If something needs to change, deprecate and create a new version.
-->

---

## 1. Artifact Types and Versioning Schemes

> **Deferred.** This section has no content, and that is a decision rather than an oversight:
> the versioning schemes it would describe are settled elsewhere and by decisions that
> are already made — entity identity by ADR-020, the schema version by
> `01-data-format/13-schema-versioning.md` — so what is left here is the artifact taxonomy,
> which needs the community model of §6 before it can say who versions what.
> Tracked as REF-TASK-0048. **No requirement or contract may cite this section as though it
> stated a policy.** The outline below records what it will have to cover.

<!--
  An "artifact" is any versioned, stored product of the system.
  → see GLOSSARY.md: Artifact

  For each artifact type, define:
    - Versioning scheme: which scheme and why? → create an ADR for non-obvious choices
    - Version identifier format (string pattern, e.g., "v1.2.3", "2026-03-01", "commit-abc1234")
    - What constitutes a new version (when must the version number change?)
    - What constitutes a breaking change (when must the major version increment?)

  Artifact types to cover:

  ### Problem Instances
    Breaking change: any change that would cause a different evaluation result for the same solution
    Non-breaking change: adding optional metadata fields, fixing documentation
    Hint: how fine-grained should versioning be? Per-instance or per-collection?

  ### Algorithm Implementations
    Breaking change: any change that would cause suggest() to return a different solution
    for the same seed and observation sequence
    Non-breaking: documentation, logging improvements, performance optimization

  ### Data Schemas (docs/03-technical-contracts/01-data-format/01-index.md)
    Breaking change: removing a required field, renaming a field, changing a field type
    Non-breaking: adding optional fields, adding new entity types
    → Schema Version referenced in all stored artifacts → GLOSSARY: Schema Version

  ### Experiment Results (Run data, ResultAggregates)
    Results are IMMUTABLE once written.
    A result's version is determined by the artifact versions used to produce it:
    (problem_version, algorithm_version, schema_version, runner_version)
    → This version tuple is stored in the Experiment record: docs/03-technical-contracts/01-data-format/05-experiment.md

  ### Analysis Tools and Metrics
    Breaking change: any change to a metric's definition that would produce different values
    → deprecated metrics must remain in docs/03-technical-contracts/03-metric-taxonomy/01-index.md §5 permanently

  ### Documentation
    Documentation versions follow the system release version.
    Historical documentation is archived alongside historical software releases.
-->

---

## 2. Dependency Tracking and Reproducibility Provenance

> **Deferred.** This section has no content, and that is a decision rather than an oversight:
> the provenance chain it describes is enforced by the entity schemas and by cross-entity
> rules `CV-001` through `CV-024`, which are written. Restating them here would be a second
> copy to keep true. What genuinely belongs here — what the system does when a dependency
> has become unavailable — needs a decision nobody has made.
> Tracked as REF-TASK-0048. **No requirement or contract may cite this section as though it
> stated a policy.** The outline below records what it will have to cover.

<!--
  Goal: given any stored result, it must be possible to identify EXACTLY which versions
  of all artifacts were used to produce it. → MANIFESTO Principle 21.

  The reproducibility provenance chain:
    Result ← Run ← Experiment ← Study
    Each level records the versions of artifacts it depends on.

  Required provenance in each artifact:
    Problem Instance record:    own version, schema version
    Algorithm Instance record:  own version, dependency library versions, schema version
    Study record:               problem versions, algorithm versions, schema version
    Experiment record:          study version, runner version, platform/environment, schema version
    Run record:                 inherits from experiment + own seed

  Verification:
    The system must be able to, given an Experiment ID:
    1. List all artifact versions involved
    2. Check if all versions are still available (not deleted)
    3. Reproduce the Run with identical results (same seed, same code, same platform)
    → This is the reproducibility acceptance test: SRS §8

  Hint: what happens if a dependency is unavailable? (library deprecated, cloud service gone)
    The Experiment is marked "partially reproducible" with explanation.
    It is never silently unmarked as reproducible when dependencies are missing.
-->

---

## 3. Deprecation Policy

This is the one section of this document that is written, because ADR-020 rests the entire
identity model of the system on it: entities are immutable, a revision is a new entity, and
deprecation is the mechanism that connects the two. The repository contract enforces the
mechanics; this section is the policy those mechanics serve.

---

### 3.1 What deprecation is

Deprecation marks an entity as one that should not be used in new work, without removing it from
the record. It is the **only** permitted mutation of an otherwise immutable entity, and it changes
how the entity is listed rather than what it contains.

Concretely, and specified in
[`02-interface-contracts/06-repository-interface.md`](../03-technical-contracts/02-interface-contracts/06-repository-interface.md):

- `deprecated` becomes `true`, `deprecation_reason` records why, and `superseded_by` records the
  replacement where there is one;
- the entity stops appearing in `list_problems()` and `list_algorithms()`;
- `get_problem(id)` and `get_algorithm(id)` keep returning it, byte-identical apart from those
  three fields.

**Nothing is ever deleted.** An archived Run references entities by UUID, and a UUID that stops
resolving breaks UC-05 — the reproduction of a published study — for every study that used it.
Deletion is not a policy this project has; deprecation exists because deletion is unavailable.

---

### 3.2 When an entity may be deprecated

Any of the following is sufficient:

- **It has been superseded.** A corrected or improved registration exists, and `superseded_by`
  names it. This is the ordinary case.
- **It was wrong.** A Problem Instance whose bounds were mistyped, an Algorithm Instance whose
  `code_reference` points at an artifact that turned out not to be the one described. The reason
  says what was wrong; the entity stays, because studies that used it are still studies that used
  it.
- **It has been withdrawn.** A problem whose source dataset is no longer distributable, an
  algorithm whose implementation is no longer obtainable. There is no replacement, and
  `superseded_by` stays null — deprecation without a successor is legitimate.

**No notice period, and no requirement to notify.** V1 is a library with a local repository; there
is no shared registry from which an entity could disappear under someone, and no user list to
notify. A notice period is a policy for a hosted registry, and it belongs with the V2 Platform
Server rather than here. What replaces it is that nothing is removed: a study depending on a
deprecated entity keeps working, so there is nothing to give notice about.

---

### 3.3 What deprecation does not do

- **It does not invalidate past results.** An Experiment that used a since-deprecated Problem
  Instance is exactly as valid as it was. The deprecation says the instance should not be chosen
  for new work; it says nothing about work already done.
- **It does not stop reproduction.** `get_*(id)` still resolves, which is the point.
- **It does not forbid comparison across the boundary.** Comparing results obtained with a
  deprecated entity against results obtained with its replacement is legitimate and sometimes
  necessary — it is how the effect of the correction is measured. Such a comparison is scoped in
  the Report like any other, naming both entities and the fact that one supersedes the other.

---

### 3.4 The lineage

`superseded_by` forms a chain, not a graph. The repository contract rejects a link that names the
entity itself, one that names an entity of a different kind, and one that would close a cycle,
because "what replaced this?" has to have an answer.

Following the chain to its end gives the current entity. There is no field holding "the latest
version": that would be a mutable pointer on an immutable entity, which is the addressing model
ADR-020 removed.

---

### 3.5 What a Study does about it

`CV-018` rejects a Study at `lock_study()` whose referenced entities are deprecated. That is the
whole enforcement, and it sits at exactly one point: the moment pre-registration takes effect.

Afterwards the Study is a historical record and its entities must stay resolvable, so deprecating
an entity a locked Study references succeeds and changes nothing about that Study. A researcher
who deprecates a Problem Instance is not reaching back into experiments that already ran.

---

### 3.6 Deprecating a metric

Metric identifiers are not entities and are not deprecated through the repository. A metric whose
definition changes in a way that would produce different values is a **new metric identifier**;
the old one remains in
[`03-metric-taxonomy/10-deprecated-metrics.md`](../03-technical-contracts/03-metric-taxonomy/10-deprecated-metrics.md)
permanently, so that a Result Aggregate from an archived study can still be read.

The reason is the same one as for entities: a stored `ResultAggregate.metrics` key that stops
having a definition is a number nobody can interpret.

---
## 4. Long-Term Storage

> **Deferred.** This section has no content, and that is a decision rather than an oversight:
> every question in it depends on infrastructure that does not exist. Where the archive
> lives, how long availability is guaranteed and what happens if the project stops being
> maintained are answerable once there is a project with users, and inventing answers now
> would produce commitments nobody has agreed to.
> Tracked as REF-TASK-0048. **No requirement or contract may cite this section as though it
> stated a policy.** The outline below records what it will have to cover.

<!--
  Where artifacts are stored permanently:
    Primary repository: [to be decided — GitHub? institutional repo? Zenodo?] → ADR candidate
    Backup / archival: [secondary storage strategy]

  Retention commitment:
    How long will the system guarantee availability of stored artifacts?
    Minimum: [years] — must outlive the expected lifetime of published studies citing this system.
    Hint: published papers cite specific versions; those versions must remain accessible.

  Format requirements for archival:
    All archived data must use open, well-documented formats. → MANIFESTO Principle 22.
    Proprietary formats are forbidden for archival storage.
    Current approved archival formats: [list formats and their justification ADRs]

  What if the organization ceases to maintain the system?
    A continuity plan should describe how the community could take over.
    At minimum: all data is under an open license in a format any researcher can read.
-->

---

## 5. Licensing

> **Deferred.** This section has no content, and that is a decision rather than an oversight:
> the code licence is decided and recorded in ADR-022: AGPL-3.0-or-later, with the
> dependency rule that follows from it in CONST-TECH. What is undecided is the **data**
> licence for benchmark problems and experimental results, which is a different domain from
> the code licence and needs its own decision.
> Tracked as REF-TASK-0048. **No requirement or contract may cite this section as though it
> stated a policy.** The outline below records what it will have to cover.

<!--
  Code license:
    What open source license? → ADR for the choice.
    Why this license over alternatives?
    What are the obligations for users who redistribute code?

  Data license:
    What open data license for benchmark problem datasets and experimental results?
    Hint: code licenses and data licenses are different domains.
    Creative Commons licenses are common for scientific data.

  Contributor License Agreement (CLA):
    Is a CLA required for contributions?
    What rights does contributing grant to the project?
    → Reference: docs/05-community/01-contribution-guide.md §6 review process

  Third-party components:
    How are license obligations for dependencies tracked?
    What licenses are allowed in dependencies? (avoid viral licenses if the project is permissive)
-->

---

## 6. Governance Model

> **Deferred.** This section has no content, and that is a decision rather than an oversight:
> it cannot be written by one author. Who reviews a contribution, who may deprecate an
> artifact, what bar a change to the Standard Reporting Set has to clear and how maintainers
> are added are answers a community gives, and this project does not have one yet. Writing
> them alone would produce a governance model that governs nobody.
> Tracked as REF-TASK-0048. **No requirement or contract may cite this section as though it
> stated a policy.** The outline below records what it will have to cover.

<!--
  Who makes decisions about this system?

  Decision types and who makes them:
    - Adding a new problem/algorithm: reviewed by [role/group]
    - Changing the Standard Reporting Set: [higher bar — broader community input]
    - Deprecating an artifact: [who has authority]
    - Breaking schema changes: [highest bar — must have migration path and notice period]
    - Architecture decisions: [ADR process, reviewed by maintainers]

  How are decisions recorded?
    Architecture decisions: architecture/adr/
    Policy changes: as versioned changes to this document (with rationale in commit/PR)
    Community discussions: [platform: GitHub Discussions, mailing list, etc.]

  How can the community influence decisions?
    → MANIFESTO Principle 27: open development process, public discussions

  How are maintainers added or removed?
    [Process — to be defined with the community]
-->
