# ADR-[NUMBER]: [Decision Title]

<!--
STORY ROLE: ADRs are the "how we got here" chapters. They explain WHY the system
looks the way it does. Without them, future contributors face a black box of
decisions that appear arbitrary, leading to well-intentioned but destructive changes.

NARRATIVE POSITION:
  ADRs are cross-cutting. Every other document may reference an ADR.
  They are written when a decision is made and referenced where the decision is visible.

CONNECTS TO:
  → The document where this decision is VISIBLE:
    (e.g., if a technology choice is made, link to the C2 container that uses it)
  → SRS requirements that motivated this decision
  → Other ADRs this supersedes (if applicable)
  → community/versioning-governance.md if this affects versioning or governance

NAMING CONVENTION: ADR-[zero-padded number]-[kebab-case-title].md
  Example: ADR-001-data-storage-format.md
           ADR-002-ask-tell-interface-pattern.md

ONE ADR PER DECISION. If you are making two independent decisions, write two ADRs.
An ADR is closed once accepted; it is never edited to change the decision.
To reverse a decision, write a new ADR that supersedes the old one.
-->

---

**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

**Date:** YYYY-MM-DD

**Deciders:**
<!--
  Who was involved in making this decision?
  List roles, not names (e.g., "core maintainers", "algorithm contributors", "community vote").
  This records the legitimacy and scope of the decision.
-->

---

## Context

<!--
  What is the situation that forces a decision?

  Describe:
    - The technical, scientific, or community pressure that requires a choice
    - What happens if we do nothing (the status quo problem)
    - The constraints that limit the solution space
    - Any relevant background that a future reader needs to understand the decision

  Reference:
    - The MANIFESTO principles that are relevant (which values are in tension?)
    - The SRS requirements that must be satisfied
    - Any prior discussions (GitHub issues, meeting notes)

  Keep this factual. Do not advocate for the chosen solution here.
-->

---

## Decision

<!--
  What did we decide?
  State it in one clear paragraph.
  Use active voice: "We will use X" / "We will not use Y".
  Reference the exact entity names from GLOSSARY.md if applicable.

  If this is a binary choice, state both options and which was chosen.
  If this is a design pattern selection, name the pattern precisely.
-->

---

## Rationale

<!--
  Why this option and not the alternatives?

  Structure:
    - What makes this option the best fit for the context?
    - Which MANIFESTO principles does this decision best support?
    - Which SRS requirements does this satisfy?
    - What trade-offs are accepted?

  Be honest about trade-offs. An ADR that claims a decision has no downsides
  is either incomplete or dishonest. Future readers need to know what was sacrificed.
-->

---

## Alternatives Considered

<!--
  For each alternative that was seriously considered:

  ### [Alternative Name]

  Description:
    What was this alternative?

  Why rejected:
    What made it worse than the chosen option for this context?
    Be specific — "too complex" is not informative. "Requires O(n²) storage per Run,
    which conflicts with NFR-PERF-01 at our target scale" is informative.

  Under what conditions would this be reconsidered:
    If the context changes (e.g., scale requirements drop, a new library becomes available),
    when should future contributors revisit this decision?
    This prevents ADRs from becoming permanent blockers to good ideas.
-->

---

## Consequences

<!--
  What does this decision change for the system?

  Positive:
    - What does this enable or simplify?
    - Which requirements are now easier to satisfy?

  Negative / Trade-offs:
    - What becomes harder or more expensive?
    - What new constraints does this introduce?
    - What must contributors now be aware of?

  Risks:
    - What could go wrong?
    - What assumptions does this decision rest on?
    - What is the mitigation if an assumption turns out to be wrong?
-->

---

## Related Documents

<!--
  List all documents that are affected by this decision and should be read alongside this ADR.

  | Document                                  | Relationship                                |
  |-------------------------------------------|---------------------------------------------|
  | docs/architecture/c2-containers.md        | Container [X] reflects this decision        |
  | docs/specs/data-format.md §[N]            | Entity [Y] format governed by this decision |
  | docs/specs/interface-contracts.md §[N]    | Interface [Z] shaped by this decision       |
  | ADR-[NUMBER]-[other-decision].md          | Supersedes / is related to                  |
-->
