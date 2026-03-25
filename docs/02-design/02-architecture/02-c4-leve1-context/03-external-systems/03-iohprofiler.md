# External System: IOHprofiler

> C1 Context: [../01-c1-context.md](../01-c1-context.md)

**What it is:** An analysis and visualization platform for iterative optimization heuristics, providing ECDF-based anytime performance analysis and statistical comparison tools.

**Why we interact with it:** IOHprofiler's analysis methodology directly aligns with our Anytime Performance requirements (Principle 14). Exporting to IOHprofiler format makes our results accessible to its powerful visualization tools.

**Direction:** Outbound export — we produce IOHprofiler-compatible data files from our Run records.

**Risk:** IOHprofiler's data format is well-documented but specific. Export mapping must be maintained as both systems evolve.

> **`TODO: REF-TASK-0007`** — Define the IOHprofiler export format mapping in `data-format.md` §3.
> Owner: ecosystem integration lead. Acceptance: Performance Records export to IOHprofiler `.dat`
> format and load correctly in IOHanalyzer.
