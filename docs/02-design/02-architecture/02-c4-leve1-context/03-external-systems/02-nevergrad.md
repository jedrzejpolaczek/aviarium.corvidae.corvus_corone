# External System: Nevergrad

> C1 Context: [01-c1-context.md](../01-c4-l1-context/01-c1-context.md)

**What it is:** Facebook Research's gradient-free optimization platform providing a large portfolio of algorithms and benchmark functions, with Python-first design.

**Why we interact with it:** Nevergrad algorithm implementations are a primary source of Algorithm Instances for our library. Its benchmark functions may serve as Problem Instances.

**Direction:** Bidirectional — we import Nevergrad algorithms and export results back for cross-platform comparison.

**Risk:** Nevergrad is actively developed; API changes may break wrapped implementations. Algorithm Instances must pin exact Nevergrad versions.

