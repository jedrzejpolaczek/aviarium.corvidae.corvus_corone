# C3: Components — Experiment Runner

> C2 Container: [08-experiment-runner.md](../../08-experiment-runner.md)
> C3 Index: [C3 overview](../01-c4-l3-components/01-c4-l3-components.md)

> **Descriptive page. It defines nothing.** Under ADR-012 this layer explains how a container is
> decomposed and why the boundaries fall where they do. Every type, field name, enumeration
> value, exception class and signature it mentions is defined in the contracts listed under
> *Where the vocabulary comes from*; a statement here that those contracts do not support is a
> defect in this page, never in them. ADR-028 removed the per-component files this page used to
> link to, for the reason recorded there.

The Experiment Runner executes one Run at a time: it derives the Run's seed, hands it to the
Problem and the Algorithm, drives the evaluation loop within the Budget, and writes a Performance
Record whenever a recording trigger fires.

Execution is local and sequential (SRS §1.4, boundary B-01). A Run that fails is recorded with
`status = "failed"` and a `failure_reason`, and the next Run starts; there is no failure policy to
configure (ADR-027).

---

## Components

| Component | Responsibility | Implements |
|---|---|---|
| Seed Manager | Derives each Run's seed from the Study's `root_seed` and detects collisions before execution | ADR-017; [`04-runner-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/04-runner-interface.md) |
| Run Isolator | Gives each Run a fresh execution context, so that state left behind by one Run cannot reach the next (FR-11) | [`04-runner-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/04-runner-interface.md) |
| Evaluation Loop | Drives the `suggest` / `observe` cycle against the Budget and reports each raw evaluation result | [`02-problem-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/02-problem-interface.md), [`03-algorithm-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/03-algorithm-interface.md) |
| Performance Recorder | Decides which evaluations become records, maintains the running best, and writes them through the repository | ADR-002, ADR-004, ADR-005, ADR-023 |

---

## Where the vocabulary comes from

| Subject | Contract |
|---|---|
| Runner behaviour, `on_evaluation`, seed handover | [`02-interface-contracts/04-runner-interface.md`](../../../../../03-technical-contracts/02-interface-contracts/04-runner-interface.md) |
| Performance Record fields, including `objective_value` and `best_so_far` | [`01-data-format/07-performance-record.md`](../../../../../03-technical-contracts/01-data-format/07-performance-record.md) |
| Run fields and the `status` enumeration | [`01-data-format/06-run.md`](../../../../../03-technical-contracts/01-data-format/06-run.md) |
| Randomness isolation, error taxonomy, logging | [`02-interface-contracts/07-cross-cutting-contracts.md`](../../../../../03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md) |

**Recording triggers** are ADR-002: the log-scale schedule, the improvement trigger governed by
`Study.improvement_epsilon` (ADR-004), and the mandatory end-of-run record. ADR-005 governs what
happens when a Run produces an unusual number of them.


---

## What this container does not have

`Study.on_failure`, `Study.max_workers`, `Run.timeout_s`, `Run.memory_limit_mb`, the Run statuses
`skipped` and `aborted`, and the Experiment statuses `partial` and `aborted` were described here
for a long time and exist in no schema. ADR-027 settles it: they are not coming, and FR-12 is the
whole of the failure behaviour. Recorded so that the next reader does not reintroduce them.

`max_workers` in particular is a V2 name reserved by SRS §1.4 B-01 and must not reappear in a V1
component.
