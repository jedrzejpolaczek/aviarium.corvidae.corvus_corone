# Contribution Guide

<!--
STORY ROLE: The "welcome letter and rulebook". Enables MANIFESTO Principle 27 (community development)
while maintaining the scientific quality that makes community contributions valuable.
A contributor reads this BEFORE making any changes.

NARRATIVE POSITION:
  MANIFESTO (community values) → Contribution Guide → (how to contribute correctly)
  This document is an entry point; it delegates technical detail to specs/ documents.

CONNECTS TO:
  ← MANIFESTO Principles 27, 28 : community development and education motivate this document
  ← SRS §5 NFR-OPEN, NFR-MODULAR : contribution process must align with these requirements
  → specs/interface-contracts.md : all code contributions must implement contracts there
  → specs/data-format.md         : all data contributions must conform to schemas there
  → specs/metric-taxonomy.md     : metric contributions follow the taxonomy format there
  → community/versioning-governance.md : accepted contributions enter the versioning pipeline
  → docs/GLOSSARY.md             : all contributions use precise glossary terms
  → architecture/adr/            : contributions requiring design decisions need an ADR
  → docs/tutorials/              : significant contributions should include or update a tutorial

PRINCIPLE: Every contribution type has a defined interface.
If you are not sure which interface to implement, read the relevant spec document first.
The specs define the "what"; this guide describes the "how and who".
-->

---

## Types of Contributions

<!--
  Overview table of contribution types and where to start for each.

  | Type                        | Start here                                      | Key contract                      |
  |-----------------------------|-------------------------------------------------|-----------------------------------|
  | New benchmark problem       | §1 below                                        | specs/interface-contracts.md §1   |
  | New algorithm implementation | §2 below                                       | specs/interface-contracts.md §2   |
  | New analysis tool / metric  | §3 below                                        | specs/metric-taxonomy.md          |
  | Documentation               | §4 below                                        | Style guide in §4                 |
  | Bug fix                     | §5 below                                        | (depends on area)                 |
  | Architecture change         | Must open an ADR first: architecture/adr/TEMPLATE.md | SRS + C2/C3 impact analysis  |
-->

---

## 1. Adding new task to project backlog
<!--
1. Link to project booard here + in README: https://github.com/users/jedrzejpolaczek/projects/12/views/1
2. Suggested template as:
## Why This Task
## Summary
## Acceptance Criteria
(Optional)
## Proposed Decision
## Source
## Reference
## Implementation notes
etc.
-->

---

## 2. Adding a Benchmark Problem

<!--
  When to contribute a new problem:
    - The problem class is not already represented in the Problem Repository
    - It addresses a real HPO challenge (not purely synthetic for its own sake)
    - You have access to complete metadata required by the Problem Instance schema

  Requirements — your contribution MUST:
    - Implement the Problem Interface: specs/interface-contracts.md §1
      (all methods, all contracts, all cross-cutting requirements in §6)
    - Provide a complete Problem Instance record: specs/data-format.md §2.1
      (all required fields, including landscape_characteristics if known)
    - Include a written justification of representativeness
      (which real HPO challenges does this problem reflect?)
    - Include tests that verify interface compliance
    - Include a docstring for every public method → C4 requirements for this component
    - Use exact GLOSSARY.md terms in all names, parameters, and descriptions

  Review criteria:
    - Interface compliance (automated check)
    - Metadata completeness (automated validation against data-format.md §2.1 schema)
    - Representativeness justification quality (human review)
    - Diversity: does this problem add characteristics not already covered?
      → reviewers check against the current problem set's characteristic coverage
    - Test coverage

  After acceptance:
    - Assigned a Problem Instance ID and version
    - Enters the versioning pipeline → community/versioning-governance.md §1
    - Listed in the Problem Repository with your name in provenance
-->

---

## 3. Adding an Algorithm Implementation

<!--
  When to contribute a new algorithm:
    - The algorithm family is not already represented, OR
    - You have a meaningfully different implementation or configuration of an existing algorithm

  Requirements — your contribution MUST:
    - Implement the Algorithm Interface: specs/interface-contracts.md §2
    - Provide a complete Algorithm Instance record: specs/data-format.md §2.2
      including: algorithm_family, configuration with justification, known_assumptions
    - Include a default configuration and document why it is "best reasonable" → Principle 10
    - Include a sensitivity report: how does performance change when key parameters vary?
      → Principle 11 (Sensitivity documentation)
    - Include tests (unit tests for interface compliance, integration test with a simple problem)
    - Reference the original paper or source for the algorithm concept

  Review criteria:
    - Interface compliance
    - Configuration justification quality
    - Declared assumptions are honest (algorithm that assumes continuous space must say so)
    - Sensitivity report included
    - Code quality and test coverage

  After acceptance:
    → versioning-governance.md §1 for versioning
-->

---

## 4. Adding Analysis Tools or Metrics

<!--
  When to contribute a new metric:
    - It captures an aspect of performance not covered by the Standard Reporting Set
    - It has a rigorous definition (can two independent implementations agree on the result?)
    - It has a clear use case: for which research questions is this metric appropriate?

  Requirements:
    - Add the metric to specs/metric-taxonomy.md using the template format there
    - Implement the metric in the analysis codebase, implementing the Analyzer interface
      → specs/interface-contracts.md §4
    - Update specs/metric-taxonomy.md §4 (Metric Selection Guide) with when to use this metric
    - If the metric should be added to the Standard Reporting Set, make the case in a discussion
      before submitting — this is a significant change requiring broader review

  For new visualization tools:
    - Follow the Reporting & Visualization component's interface (→ C3 document for that container)
    - Document what the visualization shows, for which audience, and how to interpret it
-->

---

## 5. Documentation Contributions

<!--
  Types of documentation contributions:
    - Filling in a template (replacing hints with real content)
    - Adding or updating a tutorial
    - Updating the glossary
    - Fixing errors or outdated information

  Style guide:
    - Use exact terms from GLOSSARY.md — never introduce synonyms
    - Every document must maintain its cross-reference links (CONNECTS TO sections)
    - When adding content that changes the scope of a document, update the STORY ROLE comment
    - Cross-references use the format: docs/[path/to/doc.md] §[section]
    - Tutorials follow the template: docs/tutorials/TEMPLATE.md

  When adding a tutorial:
    - It must be self-contained (reader should not need other docs to complete it)
    - It must reference the relevant protocol steps, specs, and methodology sections
    - It must have a clear audience, learning objective, and expected outcome
    → see docs/tutorials/TEMPLATE.md

  Updating templates (replacing hints with real content):
    - This is the most common documentation task as the system is built
    - Remove hint comments as you fill them in
    - Do not remove the STORY ROLE and CONNECTS TO header comments — these are permanent
-->

---

## 6. Bug Fixes

<!--
  For all bug fixes:
    - Reference the issue / task that describes the bug
    - Include a test that reproduces the bug (before the fix) and passes (after the fix)
    - If the bug reveals a gap in interface contract documentation, update specs/interface-contracts.md
    - If the bug was caused by an ambiguity in data-format.md, fix the spec alongside the code

  For reproducibility-affecting bugs:
    - This is a high-severity class — flag it explicitly
    - Any fix that changes the output of a Run for the same seed MUST be versioned as a breaking change
    - Affected previous results should be marked with the bug reference in their metadata
-->

---

## 7. Review Process

<!--
  Stages of contribution review:

  1. Draft / Discussion:
     Open an issue or discussion before writing code for:
     - New problem types (representativeness discussion)
     - New algorithm families (portfolio balance discussion)
     - Changes to Standard Reporting Set (methodology discussion)
     - Architecture changes (must go through ADR process first)

  2. Implementation:
     Submit a pull request with:
     - All requirements from the relevant section above met
     - Completed checklist (§7 below)
     - Reference to the motivating issue/discussion

  3. Automated checks:
     - Interface compliance tests
     - Schema validation
     - Test suite passes
     - Docstring completeness check

  4. Human review:
     - Scientific/methodological correctness (for problems, algorithms, metrics)
     - Code quality
     - Documentation quality
     - Cross-reference accuracy

  5. After acceptance:
     → community/versioning-governance.md for artifact versioning and publication
-->

---

## 8. Quality Checklist

<!--
  Every contribution must pass this checklist before requesting review.
  Copy this into your PR description and check each item.

  General:
    [ ] I have read the MANIFESTO and the relevant sections of this guide
    [ ] All terms I use appear in GLOSSARY.md with my intended meaning
    [ ] I have not introduced synonyms for existing glossary terms
    [ ] Cross-references in any documents I modified are still accurate

  For code contributions:
    [ ] I implement the relevant interface from specs/interface-contracts.md completely
    [ ] I have read and comply with the cross-cutting contracts (§6 of interface-contracts.md)
    [ ] My code contains no uncontrolled randomness (seeds are always injected)
    [ ] All public methods have docstrings meeting the requirements in C4 for this component
    [ ] I have written tests covering: normal usage, edge cases, and error conditions

  For problem contributions:
    [ ] Problem Instance record is complete (all required fields in data-format.md §2.1)
    [ ] Representativeness justification is written
    [ ] Diversity analysis completed (which characteristics does this problem add?)

  For algorithm contributions:
    [ ] Algorithm Instance record is complete (data-format.md §2.2)
    [ ] Default configuration is documented with justification
    [ ] known_assumptions are honest and complete
    [ ] Sensitivity report included

  For documentation contributions:
    [ ] STORY ROLE comment is accurate and updated
    [ ] CONNECTS TO links are verified as accurate
    [ ] Tutorials are self-contained and follow the template
-->
