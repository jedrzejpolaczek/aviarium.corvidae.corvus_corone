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
  → community/contribution-guide.md : contributions enter the versioning pipeline described here
  → architecture/adr/           : versioning scheme choices (e.g., semantic vs. date-based) need ADRs

GOVERNANCE PRINCIPLE: This policy applies equally to all artifact types.
No artifact is "too small" to version, and no version is deleted once published.
If something needs to change, deprecate and create a new version.
-->

---

## 1. Artifact Types and Versioning Schemes

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

<!--
  When can an artifact be deprecated?
    - A newer version supersedes it AND
    - At least [N] months notice has been given to users AND
    - All studies using the deprecated version have been identified and notified

  What deprecation means:
    - The artifact is marked deprecated in the repository with:
      reason, deprecation date, superseded_by (version or "no replacement")
    - The artifact is NOT deleted
    - The artifact is NOT used in new Studies (system enforces this)
    - Existing Experiments referencing this artifact are still valid and reproducible

  What deprecation does NOT mean:
    - The data is not gone
    - Past results are not invalidated
    - Comparisons with deprecated-version results are discouraged but not forbidden
      (must be clearly labeled as comparing across deprecated/current)

  Breaking change policy:
    A new version that introduces a breaking change in behavior triggers:
    1. A deprecation notice for the previous version
    2. A migration guide (if applicable)
    3. An ADR documenting the reason for the breaking change
-->

---

## 4. Long-Term Storage

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
    → Reference: community/contribution-guide.md §6 review process

  Third-party components:
    How are license obligations for dependencies tracked?
    What licenses are allowed in dependencies? (avoid viral licenses if the project is permissive)
-->

---

## 6. Governance Model

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
