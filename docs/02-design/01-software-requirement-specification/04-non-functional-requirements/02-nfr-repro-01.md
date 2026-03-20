# NFR-REPRO-01 — Reproducibility

*Every Experiment can be exactly re-executed by a different team using the archived Artifacts to produce identical results.*
*Source: MANIFESTO Principles 19–22.*
*Use Cases: UC-01, UC-05.*

---

## NFR-REPRO-01

**Every Experiment MUST be exactly re-executable by a different team using the archived Artifacts (code, data, seeds, procedures) to produce identical results.**

- **Source:** MANIFESTO Principles 19–22
- **Measurable criterion:** `TODO: REF-TASK-0010` — define bit-for-bit vs. numerical tolerance; platform constraints
- **Operationalized in:** `docs/05-community/02-versioning-governance.md`
- **Exercises:** UC-01 (postcondition: all Artifacts versioned and reproducible); UC-05 (verification run produces identical or documented-divergent results)
- **Tested by:** Reproducibility tests — re-execute the same Study from archived Artifacts on a clean environment and compare Result Aggregates
- **Enforced by:** FR-09 (system-assigned seeds), FR-10 (execution environment recording), FR-17 (UUID-based Artifact identity), FR-18 (complete Artifact archive)
