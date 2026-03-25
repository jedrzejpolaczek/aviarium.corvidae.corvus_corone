# Study Builder

> Container: [Study Orchestrator](../../03-c4-leve2-containers/07-study-orchestrator.md)
> C3 Index: [index.md](index.md)

---

## Responsibility

Validate user-provided study configuration, resolve algorithm and problem IDs against the registries, assemble a complete `StudyConfig`, generate the run plan (the Cartesian product of algorithms × problems × seeds), and persist the Study entity to the Results Store.

---

## Interface

Called by the Execution Coordinator (and indirectly by the Public API):

```python
class StudyBuilder:
    def build(
        self,
        raw_config: dict,
        algorithm_registry: AlgorithmRegistry,
        problem_repo: ProblemRepository,
    ) -> StudyConfig:
        """
        Validates raw_config, resolves entity IDs, returns a complete StudyConfig.
        Raises StudyValidationError with a list of all validation failures (not just the first).
        """

    def generate_run_plan(self, study_config: StudyConfig) -> list[RunConfig]:
        """
        Returns the Cartesian product: algorithms × problems × n_runs seeds.
        """
```

---

## Dependencies

- **Algorithm Registry** — `get_algorithm(id)` for ID resolution and algorithm validation
- **Problem Repository** — `get_problem(id)` for ID resolution and problem validation
- **Results Store — JSON Entity Store** — persists the Study entity after successful build

---

## Key Behaviors

1. **Schema validation** — validates all required fields of `raw_config` against the `StudyConfig` schema. Collects all validation errors (does not short-circuit on first error) and raises a single `StudyValidationError` with a complete error list.

2. **Entity ID resolution** — resolves each `algorithm_id` and `problem_id` in the config against the registries. Unresolvable IDs are included in the `StudyValidationError`.

3. **Run plan generation** — computes the Cartesian product of `algorithms × problems × range(n_runs)`. Each element is a `RunConfig` with a unique `run_id` (UUID) and a `base_seed` derived from the Study-level seed.

4. **Study entity creation** — creates a `Study` dataclass with `status=pending`, the run plan, and metadata. Persists it to the Results Store via the JSON Entity Store.

5. **Idempotency guard** — if a Study with the same `study_id` already exists in the Results Store, raises `StudyAlreadyExistsError`. The caller (Public API) is responsible for offering a resume path.

---

## State

No persistent in-memory state. All persistent data written to Results Store.

---

## Implementation Reference

`corvus_corone/study_orchestrator/study_builder.py`

---

## SRS Traceability

- UC-01 (create study): Study Builder is the implementation of the study creation step.
- FR-O-01 (study validation): all StudyConfig fields must be validated before execution begins.
