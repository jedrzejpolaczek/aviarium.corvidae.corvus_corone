# C4: Code — [Component Name]

<!--
STORY ROLE: "What do the critical abstractions look like?"
NOT an exhaustive class diagram — only architecturally significant code structures.
The rule: if removing this abstraction would require changing multiple other components,
it belongs here. Everything else belongs in docstrings.

NARRATIVE POSITION:
  C3 (component structure) → C4 → (key code abstractions)
  → Docstrings (full method-level detail in the code itself)

CONNECTS TO:
  ← C3                          : the component zoomed into here must be named in C3
  → Docstrings                  : all method-level detail belongs in code, not here
  → specs/interface-contracts.md : concrete classes here implement contracts defined there
  → specs/metric-taxonomy.md    : metric-related enums/classes here must match taxonomy names
  → architecture/adr/           : design pattern choices made here belong in ADRs

INSTRUCTION: Create one C4 file per architecturally significant component.
Not every component needs a C4 file — only those where the code structure
itself is a design decision worth documenting.
-->

---

## Component: [Name] (from C3: [Container Name])

<!--
  One sentence: what architectural problem does this component solve?
  Why does its code structure matter beyond implementation convenience?
-->

---

## Key Abstractions

<!--
  For each architecturally significant class, interface, protocol, or dataclass:
  (Only list abstractions that define shape or behavior used by OTHER components.)

  ### [Abstraction Name]

  Type:
    abstract class / protocol / dataclass / enum / module-level interface
    Why this type? (e.g., "Protocol instead of ABC to allow structural subtyping")
    → If non-obvious: create an ADR

  Purpose:
    Why does this abstraction exist?
    What design pressure led to creating it?

  Key elements:
    List the most important methods or fields — names and one-line semantics only.
    DO NOT include full signatures here; those belong in docstrings.
    Hint: if you find yourself writing parameter types and return types, stop —
    that is docstring territory.

  Constraints / invariants:
    What must always be true about instances of this abstraction?
    (e.g., "seed must be set before any call to suggest()")
    → These become docstring postconditions and assert statements in code.

  Extension points:
    How is this abstraction intended to be extended or implemented?
    What is the expected variability?
    → This informs the Contribution Guide: specs/interface-contracts.md
-->

---

## Class / Module Diagram

<!--
  A UML or Mermaid class diagram showing relationships between key abstractions.

  Include:
    - Inheritance relationships (is-a)
    - Composition / aggregation (has-a)
    - Key dependencies (uses)

  Exclude:
    - Implementation classes that don't define architectural shape
    - Private helpers
    - Third-party library internals

  Hint: if the diagram has more than ~15 nodes, it is probably not a C4 diagram —
  it is an implementation diagram. Split or simplify.
-->

---

## Design Patterns Applied

<!--
  For each non-trivial design pattern used in this component:

  ### [Pattern Name]

  Where used:
    Which class(es) or module(s) implement this pattern?

  Why this pattern:
    What problem does it solve here?
    What alternatives were considered?
    → Record the decision in architecture/adr/ if it was a meaningful trade-off.

  Implications for contributors:
    What must a contributor understand about this pattern to extend the component correctly?
    → This becomes a section in the Contribution Guide.
-->

---

## Docstring Requirements for This Component

<!--
  What MUST be present in docstrings for all public classes and methods in this component?
  This section bridges C4 (architecture) with code-level documentation.

  Hint — common requirements for this system:
    - All public interfaces: full parameter descriptions, return type semantics,
      raised exceptions, and at least one usage example
    - Performance-sensitive methods: document computational complexity
    - Randomness-consuming methods: document seed dependency and reproducibility contract
    - Metric-computing methods: reference the metric definition in specs/metric-taxonomy.md

  → Contributors should read this section before implementing any part of this component.
  → Code reviewers use this as a checklist.
-->
