# §6 Cross-Cutting Contracts

> Index: [01-interface-contracts.md](01-interface-contracts.md)

Contracts that apply to **all** interface implementations in this system.
These are the system-wide rules that make the whole greater than the sum of its parts.
Violating any rule in this section is a contract breach regardless of which interface
the implementation targets.

**Design decisions recorded here:**
- **Structured log format: JSON.** All structured log events are emitted as JSON objects.
  This enables machine-readable audit trails, debugging, and integration with standard
  log aggregation tools without custom parsers.

---

### Randomness Isolation

No implementation may generate random numbers without receiving a seed from outside.
All randomness flows from seeds injected by the Runner (§3 — [04-runner-interface.md](04-runner-interface.md)).

**Rule:** The following calls are **forbidden** inside any Problem, Algorithm, or Analyzer
implementation unless a seed parameter has been received from the Runner:
- `random.random()`, `random.Random()` without seed
- `numpy.random.random()`, `numpy.random.rand()`, etc. (legacy API)
- `numpy.random.default_rng()` without seed

**Required pattern:**
```python
# Runner injects seed → implementation creates its own RNG from it
self._rng = random.Random(seed)          # stdlib
self._rng = numpy.random.default_rng(seed)  # numpy
```

**Rationale:** → MANIFESTO Principle 18; SRS NFR-REPRO

---

### Structured Logging

Every implementation of every interface MUST emit structured JSON log events at defined
points. Log events are written to the standard logging framework at `DEBUG` level unless
noted otherwise.

**Mandatory log events:**

| Event | Level | Fields |
|---|---|---|
| Method entry (public methods) | `DEBUG` | `method`, `component`, `run_id` (if applicable) |
| Method exit (public methods) | `DEBUG` | `method`, `component`, `duration_ms` |
| Exception raised | `WARNING` | `method`, `component`, `error_code`, `message` |
| Seed used | `INFO` | `component`, `seed`, `run_id` |
| Budget consumed | `INFO` | `run_id`, `eval_number`, `remaining_budget` |

**JSON log event format:**
```json
{
  "timestamp": "2026-03-23T14:00:00.000Z",
  "level": "INFO",
  "component": "Runner",
  "event": "seed_used",
  "run_id": "run-abc123",
  "seed": 42
}
```

All fields use `snake_case`. Timestamps are ISO 8601 UTC. No free-form string concatenation
in structured events — all variable data goes in named fields.

---

### Error Taxonomy

All exceptions raised by interface implementations MUST belong to this hierarchy.
Every exception MUST carry: `error_code` (string), `message` (human-readable), `context`
(dict of relevant field values at the time of the error).

```
CorvusError (base)
├── ValidationError       — input does not conform to contract
│   ├── InvalidSolutionError     (§1 Problem)
│   ├── StudyNotLockedError      (§3 Runner)
│   ├── StudyAlreadyLockedError  (§5 Repository)
│   ├── ImmutableFieldError      (§5 Repository)
│   └── UnknownMetricError       (§4 Analyzer)
├── BudgetError           — budget exhausted or invalid
│   └── BudgetExhaustedError     (§1 Problem)
├── ReproducibilityError  — seed not set, state not isolated
│   └── SeedCollisionError       (§3 Runner)
├── StorageError          — repository unavailable or corrupt
│   ├── EntityNotFoundError      (§5 Repository)
│   ├── VersionNotFoundError     (§5 Repository)
│   └── DuplicateEvaluationError (§5 Repository)
├── IntegrationError      — external system unavailable
│   └── CodeReferenceError       (§5 Repository — unreachable code_reference)
└── AnalysisError         — analysis precondition not met
    ├── ExperimentNotCompleteError  (§4 Analyzer)
    └── InsufficientRunsError       (§4 Analyzer)
```

All exceptions are importable from `corvus_corone.exceptions`.

---

### Version Declaration

Every implementation MUST expose a `declared_version() → str` method.
The returned string is a semantic version (`"X.Y.Z"`) matching the `version` field of the
corresponding entity record.

This version is recorded in the `AlgorithmInstance` / `ProblemInstance` record at
registration time and stored in every `Run` that uses the instance.
→ data-format.md §2.1 and §2.2 provenance fields

**Postconditions:**
- result matches the regex `^\d+\.\d+\.\d+$`
- result is stable — returns the same value for the lifetime of the instance

---

### Docstring Requirements

Every public method of every interface implementation MUST have docstrings with all of
the following sections:

| Section | Required content |
|---|---|
| **Summary** | One-line imperative description |
| **Parameters** | Name, type, and semantics for every parameter |
| **Returns** | Type and semantics of the return value |
| **Raises** | Every exception from §Error Taxonomy that this method raises, with the condition that triggers it |
| **Example** | At least one usage example |
| **References** | Links to relevant specs (e.g., `metric_name → metric-taxonomy.md §2.1`) |

→ C4 code documents specify additional per-component docstring requirements.
