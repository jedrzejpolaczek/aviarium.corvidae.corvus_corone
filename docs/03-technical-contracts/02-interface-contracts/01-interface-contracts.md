# Interface Contracts

<!--
STORY ROLE: The "handshake specification". Defines the boundaries between components.
A module is only as modular as its interface contracts are precise.
This document enables Value 6 (System adaptability): anyone can implement an interface
and plug into the system without reading other implementations.

NARRATIVE POSITION:
  C3 (component boundaries) → Interface Contracts → (formal boundary definitions)
  → C4 (code): concrete classes implement these contracts
  → community/contribution-guide.md: contributors implement these contracts

CONNECTS TO:
  ← C3                          : each component boundary visible there is formalized here
  ← SRS §4, §7                  : requirements for interoperability and modularity
  → specs/data-format.md        : all input/output types reference entities defined there
  → specs/metric-taxonomy.md    : metric-related return types reference taxonomy names
  → community/contribution-guide.md : all contribution types must implement a contract here
  → C4                          : code-level abstractions implement these contracts
  → Docstrings                  : every public method must have docstrings that document
                                  the contracts stated here (pre/postconditions, exceptions)

GLOSSARY: All terms from docs/GLOSSARY.md apply. Use exact glossary terms.

CONTRACT FORMAT for each method (applies to all section files):
  - Signature: parameter names and types (reference data-format.md for complex types)
  - Semantics: what does this method DO? (not how — that is implementation detail)
  - Preconditions: what must be true BEFORE calling this method?
  - Postconditions: what is guaranteed to be true AFTER a successful call?
  - Exceptions: what error conditions does this method raise and when?
  - Thread/isolation safety: can this be called concurrently?
  - Docstring requirement: what sections are mandatory in the implementing class?
-->

---

## Contents

| Section | File | Status |
|---|---|---|
| §1 Problem Interface | [02-problem-interface.md](02-problem-interface.md) | ✅ Formal contract |
| §2 Algorithm Interface | [03-algorithm-interface.md](03-algorithm-interface.md) | ✅ Formal contract |
| §3 Runner Interface | [04-runner-interface.md](04-runner-interface.md) | ✅ Formal contract |
| §4 Analyzer Interface | [05-analyzer-interface.md](05-analyzer-interface.md) | ✅ Formal contract |
| §5 Repository Interface | [06-repository-interface.md](06-repository-interface.md) | ✅ Formal contract |
| §6 Cross-Cutting Contracts | [07-cross-cutting-contracts.md](07-cross-cutting-contracts.md) | ✅ Formal contract |
