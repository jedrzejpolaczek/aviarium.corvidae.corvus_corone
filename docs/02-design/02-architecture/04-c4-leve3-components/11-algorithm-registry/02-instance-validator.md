# Instance Validator

> Container: [Algorithm Registry](../../03-c4-leve2-containers/10-algorithm-registry.md)
> C3 Index: [index.md](01-index.md)

---

## Responsibility

Validate an AlgorithmInstance against the required schema before it is accepted by the Version Manager for registration.

---

## Interface

```python
class AlgorithmInstanceValidator:
    def validate(self, instance: AlgorithmInstance) -> None:
        """
        Raises AlgorithmValidationError with all violations if invalid.
        Does nothing if valid.
        """
```

---

## Dependencies

- `dataclasses` stdlib (field inspection)
- No external libraries

---

## Key Behaviors

1. **Required fields check** — validates that all required fields are non-null: `id`, `name`, `algorithm_family`, `version`, `hyperparameters`, `known_assumptions`, `ask_callable`, `tell_callable`.

2. **ID format validation** — validates `id` matches the pattern `^[a-z0-9-]+$` (lowercase alphanumeric with hyphens). Rejects uppercase, spaces, and special characters.

3. **Hyperparameter schema** — validates each entry in `hyperparameters` has `name`, `type` (one of `continuous`, `integer`, `categorical`), and `range` or `choices` as appropriate.

4. **Callable check** — validates `ask_callable` and `tell_callable` are Python callables with the expected signatures (checked via `inspect.signature`).

5. **Error accumulation** — collects all violations before raising. `AlgorithmValidationError` lists every failed check, not just the first.

---

## State

Stateless.

---

## Implementation Reference

`corvus_corone/algorithm_registry/instance_validator.py`

---

## SRS Traceability

- FR-R-03 (algorithm validation): instances must be validated before registration.
