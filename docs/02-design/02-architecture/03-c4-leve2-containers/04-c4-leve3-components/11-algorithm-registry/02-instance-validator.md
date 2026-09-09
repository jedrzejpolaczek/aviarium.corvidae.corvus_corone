# Instance Validator

> Container: [Algorithm Registry](../../10-algorithm-registry.md)
> C3 Index: [01-index.md](01-index.md)

---

## Responsibility

Validate an AlgorithmInstance against the required schema before it is accepted by the Version Manager for registration.

---

## Interface

```python
class AlgorithmInstanceValidator:
    def validate(self, instance: AlgorithmInstance) -> None:
        """
        Raises ValidationError with all violations if invalid.
        Does nothing if valid.
        """
```

---

## Dependencies

- `dataclasses` stdlib (field inspection)
- No external libraries

---

## Key Behaviors

1. **Required fields check** — validates that every field [`03-algorithm-instance.md`](../../../../../03-technical-contracts/01-data-format/03-algorithm-instance.md) marks required is present and non-null. The optimizer entry point is `code_reference`; the methods it must expose are `suggest` and `observe`, named in `03-algorithm-interface.md`.

2. **ID format validation** — validates `id` matches the pattern `^[a-z0-9-]+$` (lowercase alphanumeric with hyphens). Rejects uppercase, spaces, and special characters.

3. **Hyperparameter schema** — validates each entry in `hyperparameters` has `name`, `type` (one of `continuous`, `integer`, `categorical`), and `range` or `choices` as appropriate.

4. **Code reference check** — validates that `code_reference` resolves and is version-pinned, and that the object it names implements the Algorithm Interface. An unpinned reference is rejected with `CodeReferenceError` (FR-06).

5. **Error accumulation** — collects all violations before raising. `ValidationError` lists every failed check, not just the first.

---

## State

Stateless.

---

## Implementation Reference

`corvus_corone/algorithm_registry/instance_validator.py`

---

## SRS Traceability

- FR-06 (resolvable, pinned code reference): an unpinned or unresolvable `code_reference` is rejected at registration.
- FR-07 (configuration justification): a registration with an empty `configuration_justification` is rejected.
