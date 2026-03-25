# C3: Components

## Contents

| Container | C3 file |
|---|---|
| Corvus Pilot V2 | [02-corvus-pilot.md](02-corvus-pilot.md) |

---

# C3: Components — [Container Name]

<!--
STORY ROLE: "What is inside each container?"
This is where architectural thinking meets code structure.
Each container from C2 gets its own C3 view (either as separate files or sections here).

NARRATIVE POSITION:
  C2 (containers and flows) → C3 → (internal structure of each container)
  → C4 (code-level abstractions for critical components)

CONNECTS TO:
  ← C2                          : the container decomposed here must match C2 exactly
  → C4                          : critical components here are zoomed into at code level there
  → specs/interface-contracts.md : component boundaries are formally defined as interfaces there
  → SRS §4                      : each component traces to one or more functional requirements
  → architecture/adr/           : design decisions inside a container belong in ADRs

INSTRUCTION: Create one section per container from C2, or split into separate files
(e.g., c3-problem-repository.md, c3-experiment-runner.md).
The file name convention should mirror C2 container names.
-->

---

## [Container Name] — Component Breakdown

<!--
  Brief reminder: what is this container responsible for? (one sentence, from C2)
  Which actors interact with this container? (from C1)
-->

### Component Diagram

<!--
  Draw a C4 Component diagram for this container.
  Show:
    - Each component as a labeled box with a one-line responsibility
    - Internal component-to-component relationships (arrows with reason/data)
    - External relationships: which other containers from C2 does this container
      interact with, and through which component?
    - Which external systems from C1 are touched by components in this container?
-->

---

### [Component Name]

<!--
  Repeat this block for each component in this container.

  Responsibility:
    One sentence. What is this component's single concern within the container?

  Interface:
    What does this component expose to other components inside this container?
    What does it expose to other containers (from C2)?
    → Formal contracts: specs/interface-contracts.md

  Dependencies:
    What does this component depend on?
    (other components, external libraries, storage, infrastructure services)

  Key behaviors:
    What are the 2–5 most important operations this component performs?
    Hint: name operations in domain terms, not implementation terms.
    (e.g., "validates problem metadata", not "calls validate_schema()")

  State:
    Does this component hold state? If yes:
    - What state? (in-memory, persisted, cached)
    - What are the lifecycle boundaries of that state?

  Implementation reference:
    Which module, package, or file implements this component?
    → Docstrings in that code provide the next level of detail.

  SRS traceability:
    Which functional requirements (FR-XX) does this component satisfy?
-->

---

## Cross-Cutting Concerns Within This Container

<!--
  Things that affect multiple components inside this container but aren't
  a single component's responsibility.

  Address each of the following:

  Logging & observability:
    What do components log, and in what format?
    → Standard: to be defined in specs/interface-contracts.md §6

  Error handling:
    What is the error taxonomy for this container?
    How do errors propagate between components?
    What gets surfaced to the caller vs. handled internally?

  Randomness / seed management:
    Which components consume random state?
    How is the seed injected and isolated between runs?
    → Critical for reproducibility: MANIFESTO Principle 18

  Configuration:
    How is configuration injected into components?
    What is configurable at runtime vs. compile time vs. deployment time?

  Testing strategy:
    How are components in this container tested in isolation?
    What are the integration test boundaries?
    → Test tasks in the issue tracker should reference component names from here.
-->
