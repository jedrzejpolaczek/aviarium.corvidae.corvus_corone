# External System: HPC / Cloud Compute

> C1 Context: [01-c1-context.md](../01-c4-l1-context/01-c1-context.md)

**What it is:** Distributed computing infrastructure (SLURM clusters, cloud VMs, etc.) used to execute parallel Runs when local compute is insufficient.

**Why we interact with it:** Runs are independent by design (Principle 18), making them trivially parallelizable. Large studies with many (algorithm, problem, repetition) combinations require distributed execution.

**Direction:** Outbound — the system submits jobs and collects results.

**V1 scope:** Deferred. V1 supports local execution only (sequential or Python multiprocessing). The `Runner` interface is designed as an abstraction so a SLURM or cloud backend can be plugged in for V2 without changing the data format or library API. See `ADR-001`.
