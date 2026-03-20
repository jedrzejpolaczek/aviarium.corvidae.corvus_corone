# NFR-USABILITY-01 — Minimal Onboarding Friction

*A researcher familiar with Python can wrap an existing HPO optimizer and run their first benchmarking Study in under 30 minutes from installation.*
*Source: MANIFESTO Principle 28.*
*Use Cases: UC-01, UC-02.*

---

## NFR-USABILITY-01

**A researcher familiar with Python MUST be able to wrap an existing HPO optimizer and run their first benchmarking Study in under 30 minutes from installation.**

- **Source:** MANIFESTO Principle 28 (education and support)
- **Measurable criterion:** `TODO: REF-TASK-0010` — define the "first study" tutorial and measure completion time in user testing
- **Exercises:** UC-02 (algorithm wrapping ≤15 lines); UC-01 (Study definition and execution via the Python API)
- **Tested by:** Usability tests — timed completion of the "Algorithm Author" tutorial (target: ≤15 lines of adapter code) and the "First Study" tutorial (target: ≤30 minutes from installation to report)
- **Enforced by:** The Algorithm interface design (→ `docs/03-technical-contracts/02-interface-contracts.md`) must be minimal enough that common wrappers require ≤15 lines
