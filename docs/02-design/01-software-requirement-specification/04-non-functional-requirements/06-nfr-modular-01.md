# NFR-MODULAR-01 — Extensibility

*Adding a new Problem Instance or Algorithm Implementation requires only implementing the defined interface — no modification of existing system code.*
*Source: MANIFESTO Value 6, Principle 27.*
*Use Cases: UC-02, UC-04.*

---

## NFR-MODULAR-01

**Adding a new Problem Instance or Algorithm Implementation MUST require only implementing the defined interface — no modification of existing system code.**

- **Source:** MANIFESTO Value 6 (System adaptability), Principle 27 (community development)
- **Measurable criterion:** (1) A new Algorithm Instance contributed by creating one Python class in a separate file — implementing only the 5-method Algorithm interface — can be registered and used in a Study without modifying any file under `packages/corvus-corone-lib/src/`. (2) A new Problem Instance contributed by constructing a `ProblemInstance` record satisfying the schema can be registered and included in a Study without modifying any core library file. (3) The plugin test passes if and only if no file under `src/` has a later `git mtime` than the test start time after the plugin exercise.
- **Operationalized in:** `docs/03-technical-contracts/02-interface-contracts.md`
- **Exercises:** UC-02 (contribute algorithm via interface); UC-04 (contribute Problem Instance via schema)
- **Tested by:** Plugin tests — contribute a new Algorithm Instance and a new Problem Instance in an isolated test environment; verify no core files are modified; verify the new entries participate correctly in a Study
- **Enforced by:** FR-01, FR-02 (Problem Instance validation without code change), FR-05, FR-06, FR-07 (Algorithm Instance validation without code change)
