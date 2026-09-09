# Study Builder

> Container: [Study Orchestrator](../../07-study-orchestrator.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Validate user-provided study configuration, resolve algorithm and problem IDs against the registries, assemble a complete `Study`, generate the run plan in ADR-017 order (problems, then algorithms, then repetitions), and persist the Study entity to the Results Store.

---

## Interface

Called by the Public API when a Study is created and again when it is locked. It is not
called during execution: by then the Study is locked and its plan fixed (ADR-013).

```python
class StudyBuilder:
    def build(
        self,
        raw_config: dict,
        algorithm_registry: AlgorithmRepository,
        problem_repo: ProblemRepository,
    ) -> Study:
        """
        Validates raw_config, resolves entity IDs, returns a complete Study.
        Raises ValidationError with a list of all validation failures (not just the first).
        """

    def generate_run_plan(self, study_config: Study) -> list[Run]:
        """
        Returns the run plan in ADR-017 order: problems, then algorithms, then repetitions.
        """
```

---

## Dependencies

- **Algorithm Registry** — `get_algorithm(id)` for ID resolution and algorithm validation
- **Problem Repository** — `get_problem(id)` for ID resolution and problem validation
- **Results Store** — `StudyRepository.create_study()` and `lock_study()`, reached through
  the `RepositoryFactory` (ADR-001)

---

## Key Behaviors

1. **Schema validation** — validates all required fields of `raw_config` against the `Study` schema. Collects all validation errors (does not short-circuit on first error) and raises a single `ValidationError` with a complete error list.

2. **Entity ID resolution** — resolves each `algorithm_id` and `problem_id` in the config against the registries. Unresolvable IDs are included in the `ValidationError`.

3. **Run plan generation** — computes the Cartesian product in the order ADR-017 fixes:
   problem index, then algorithm index, then repetition index. The order is part of the
   contract rather than an implementation choice, because Run seeds are spawned from
   `SeedSequence(Study.root_seed)` in exactly this order; any other order produces
   different seeds for the same Study.

4. **Study entity creation** — creates the Study with `status = "draft"` (ADR-013) and
   persists it through `StudyRepository.create_study()`. The repository assigns the UUID;
   the caller does not supply one. No component constructs a path into the store (ADR-001).

5. **Lock-time validation** — `lock_study()` re-runs the checks above and adds the ones
   that only make sense on a complete plan: at least one pre-registered hypothesis
   (ADR-021) and the ADR-009 diversity floor unless the Study is exploratory. Every
   unresolved decision is reported at once, with its consequence (FR-27).

   There is no idempotency guard keyed on a caller-supplied identifier: identifiers are
   assigned by the repository, so a caller cannot name a Study into existence twice.

---

## State

No persistent in-memory state. All persistent data written to Results Store.

---

## Implementation Reference

`corvus_corone/study_orchestrator/study_builder.py`

---

## SRS Traceability

- UC-01 (create study): Study Builder is the implementation of the study creation step.
- FR-08 (study validation): all Study fields must be validated before execution begins.
