"""Exception hierarchy for corvus_corone.

All exceptions raised by interface implementations belong to this hierarchy.
Every exception carries: ``error_code`` (str), ``message`` (str), and ``context``
(dict of relevant field values at the time of the error).

Importable from ``corvus_corone.exceptions``.

References
----------
→ docs/03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md §Error Taxonomy
"""

from __future__ import annotations

from typing import Any


class CorvusError(Exception):
    """Base exception for all corvus_corone errors.

    Parameters
    ----------
    message:
        Human-readable description of the error.
    error_code:
        Machine-readable error code (e.g. ``"ENTITY_NOT_FOUND"``).
    context:
        Dict of relevant field values at the time of the error.
        Must not contain sensitive data.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "CORVUS_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context: dict[str, Any] = context or {}

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"error_code={self.error_code!r}, "
            f"message={self.message!r}, "
            f"context={self.context!r})"
        )


# ---------------------------------------------------------------------------
# ValidationError branch
# ---------------------------------------------------------------------------


class ValidationError(CorvusError):
    """Input does not conform to contract."""

    def __init__(
        self,
        message: str,
        error_code: str = "VALIDATION_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, error_code, context)


class InvalidSolutionError(ValidationError):
    """Solution vector does not conform to the Problem's search space.

    References
    ----------
    → interface-contracts.md §1 Problem Interface
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "INVALID_SOLUTION", context)


class StudyNotLockedError(ValidationError):
    """Experiment was started before the Study was locked.

    References
    ----------
    → interface-contracts.md §3 Runner Interface
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "STUDY_NOT_LOCKED", context)


class StudyAlreadyLockedError(ValidationError):
    """Modification was attempted on a locked Study.

    References
    ----------
    → interface-contracts.md §5 Repository Interface
    → FR-08, UC-01 F3
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "STUDY_ALREADY_LOCKED", context)


class ImmutableFieldError(ValidationError):
    """Caller attempted to update an immutable field after creation.

    References
    ----------
    → interface-contracts.md §5 Repository Interface — ExperimentRepository
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "IMMUTABLE_FIELD", context)


class UnknownMetricError(ValidationError):
    """Metric name is not registered in metric-taxonomy.md.

    References
    ----------
    → interface-contracts.md §4 Analyzer Interface
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "UNKNOWN_METRIC", context)


# ---------------------------------------------------------------------------
# BudgetError branch
# ---------------------------------------------------------------------------


class BudgetError(CorvusError):
    """Budget exhausted or invalid."""

    def __init__(
        self,
        message: str,
        error_code: str = "BUDGET_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, error_code, context)


class BudgetExhaustedError(BudgetError):
    """Problem.evaluate() called after budget was exhausted.

    References
    ----------
    → interface-contracts.md §1 Problem Interface
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "BUDGET_EXHAUSTED", context)


# ---------------------------------------------------------------------------
# ReproducibilityError branch
# ---------------------------------------------------------------------------


class ReproducibilityError(CorvusError):
    """Seed not set or run state not properly isolated."""

    def __init__(
        self,
        message: str,
        error_code: str = "REPRODUCIBILITY_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, error_code, context)


class SeedCollisionError(ReproducibilityError):
    """The same seed would be used twice within a single Experiment.

    References
    ----------
    → interface-contracts.md §3 Runner Interface — UC-01 F4
    → FR-09
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "SEED_COLLISION", context)


# ---------------------------------------------------------------------------
# StorageError branch
# ---------------------------------------------------------------------------


class StorageError(CorvusError):
    """Repository unavailable, entity missing, or data corrupt."""

    def __init__(
        self,
        message: str,
        error_code: str = "STORAGE_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, error_code, context)


class EntityNotFoundError(StorageError):
    """Entity with the given ID does not exist in the repository.

    References
    ----------
    → interface-contracts.md §5 Repository Interface
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "ENTITY_NOT_FOUND", context)


class VersionNotFoundError(StorageError):
    """Entity with the given ID exists but the requested version does not.

    References
    ----------
    → interface-contracts.md §5 Repository Interface — versioning semantics
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "VERSION_NOT_FOUND", context)


class DuplicateEvaluationError(StorageError):
    """A PerformanceRecord with the same evaluation_number already exists for this Run.

    References
    ----------
    → interface-contracts.md §5 Repository Interface — RunRepository.save_performance_records
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "DUPLICATE_EVALUATION", context)


# ---------------------------------------------------------------------------
# IntegrationError branch
# ---------------------------------------------------------------------------


class IntegrationError(CorvusError):
    """External system unavailable or returned an unexpected response."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTEGRATION_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, error_code, context)


class CodeReferenceError(IntegrationError):
    """Algorithm code_reference is not reachable or cannot be resolved.

    References
    ----------
    → interface-contracts.md §5 Repository Interface — AlgorithmRepository.register_algorithm
    → FR-06
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "CODE_REFERENCE_ERROR", context)


# ---------------------------------------------------------------------------
# AnalysisError branch
# ---------------------------------------------------------------------------


class AnalysisError(CorvusError):
    """Analysis precondition not met."""

    def __init__(
        self,
        message: str,
        error_code: str = "ANALYSIS_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, error_code, context)


class ExperimentNotCompleteError(AnalysisError):
    """Report generation attempted before all Runs completed.

    References
    ----------
    → interface-contracts.md §4 Analyzer Interface
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "EXPERIMENT_NOT_COMPLETE", context)


class InsufficientRunsError(AnalysisError):
    """Too few Runs for the requested statistical analysis.

    References
    ----------
    → interface-contracts.md §4 Analyzer Interface
    → statistical-methodology.md — minimum sample size requirements
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, "INSUFFICIENT_RUNS", context)
