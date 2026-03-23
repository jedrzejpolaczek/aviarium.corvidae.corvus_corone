# NFR-USABILITY-01 — Minimal Onboarding Friction

*A researcher familiar with Python can wrap an existing HPO optimizer and run their first benchmarking Study in under 30 minutes from installation.*
*Source: MANIFESTO Principle 28.*
*Use Cases: UC-01, UC-02.*

---

## NFR-USABILITY-01

**A researcher familiar with Python MUST be able to wrap an existing HPO optimizer and run their first benchmarking Study in under 30 minutes from installation.**

- **Source:** MANIFESTO Principle 28 (education and support)
- **Measurable criterion:** (1) The algorithm adapter in the UC-02 tutorial (`docs/06_tutorials/uc-02-contribute-algorithm.md`) minimal example contains ≤15 lines of algorithm-specific logic, measured by counting non-blank, non-comment lines in `initialize()`, `suggest()`, and `observe()` combined. The reference `RandomSearchAlgorithm` currently measures 7 lines. (2) A developer unfamiliar with the codebase who follows the UC-02 tutorial from `pip install corvus-corone` to a passing `run_single()` smoke run completes the task in ≤30 minutes in timed user testing. Both criteria are verifiable: (1) automatically by a line-count test; (2) by periodic user testing against the tutorial document.
- **Exercises:** UC-02 (algorithm wrapping ≤15 lines); UC-01 (Study definition and execution via the Python API)
- **Tested by:** Usability tests — timed completion of the "Algorithm Author" tutorial (target: ≤15 lines of adapter code) and the "First Study" tutorial (target: ≤30 minutes from installation to report)
- **Enforced by:** The Algorithm interface design (→ `docs/03-technical-contracts/02-interface-contracts.md`) must be minimal enough that common wrappers require ≤15 lines
