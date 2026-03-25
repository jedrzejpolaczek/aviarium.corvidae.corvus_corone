# C4: Code — Results Store

> C4 Top-level Index: [../01-index.md](../01-index.md)
> C3 Container Index: [../../04-c4-leve3-components/05-results-store/01-index.md](../../04-c4-leve3-components/05-results-store/01-index.md)

---

## Documented Abstractions

| File | Abstraction | Why C4 |
|---|---|---|
| [02-repository-protocol.md](02-repository-protocol.md) | `Repository` (Protocol) | V1→V2 swap point — every component that reads or writes study artifacts depends on this abstraction; `LocalFileRepository` (V1) and a future `ServerRepository` (V2) both implement it without modifying any caller |

---

## Shared Abstractions Used by This Container

The following cross-container abstractions from [02-shared/](../02-shared/) are consumed here:

| Abstraction | Role in Results Store |
|---|---|
| [`PerformanceRecord`](../02-shared/03-performance-record.md) | `JsonlPerformanceWriter` serialises records to JSONL; `ParquetPerformanceWriter` converts them post-run; `PerformanceRecordReader` deserialises them for the Analysis Engine |
