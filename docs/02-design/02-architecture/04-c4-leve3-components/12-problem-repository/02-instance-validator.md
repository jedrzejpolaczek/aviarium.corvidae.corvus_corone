# Instance Validator

> Container: [Problem Repository](../../03-c4-leve2-containers/11-problem-repository.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Validate a ProblemInstance against the required schema before it is accepted by the Version Manager for registration.

---

## Interface

```python
class ProblemInstanceValidator:
    def validate(self, instance: ProblemInstance) -> None:
        """
        Raises ProblemValidationError with all violations if invalid.
        Does nothing if valid.
        """
```

---

## Dependencies

- `dataclasses` stdlib
- No external libraries

---

## Key Behaviors

1. **Required fields check** — validates all required fields: `id`, `name`, `dimension`, `search_space`, `objective_type` (single/multi), `evaluate_callable`, `max_budget`.

2. **ID format validation** — same pattern as Algorithm Registry: `^[a-z0-9-]+$`.

3. **Search space validation** — validates that `search_space` has at least one dimension and that each dimension has `type` (continuous/integer/categorical) and appropriate bounds or choices.

4. **Callable check** — validates `evaluate_callable` is a Python callable with the expected signature: `(x: list[float]) -> float` for single-objective, `(x: list[float]) -> list[float]` for multi-objective.

5. **Error accumulation** — same pattern as Algorithm Registry: collects all violations before raising.

---

## State

Stateless.

---

## Implementation Reference

`corvus_corone/problem_repository/instance_validator.py`

---

## SRS Traceability

- FR-R-06 (problem validation): problem instances must be validated before registration.
