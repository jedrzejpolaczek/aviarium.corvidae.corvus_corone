"""Abstract base classes for the Repository storage abstraction layer.

Every persistent entity type has its own domain repository interface.
A :class:`RepositoryFactory` groups all domain repositories and is the single
object passed to components that need cross-entity access.

Key design decisions (from interface-contracts.md §5):

- **Domain-specific repositories.** One interface per entity type. Independent
  versioning and testing per domain.
- **Versioning semantics.** ``get_*(id, version=None)`` returns the latest
  non-deprecated version. ``get_*(id, version="X.Y.Z")`` returns exactly that
  version — required for reproducibility (MANIFESTO Principle 19).
- **Server-compatible IDs.** All entity IDs are UUID strings. No file paths in
  any method signature (ADR-001).

References
----------
→ docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md
→ docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md
→ docs/03-technical-contracts/01-data-format/ (entity field definitions)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Filter types
# ---------------------------------------------------------------------------


@dataclass
class ProblemFilter:
    """Filter criteria for :meth:`ProblemRepository.list_problems`.

    All fields are optional; ``None`` means "no restriction on this field".

    Attributes
    ----------
    provenance:
        ``"synthetic"`` | ``"real_world"`` | ``None``
    real_or_synthetic:
        Alias for ``provenance``; either field accepted.
    min_dimensions:
        Inclusive lower bound on ``dimensions``.
    max_dimensions:
        Inclusive upper bound on ``dimensions``.
    landscape_characteristics:
        Subset match — returned instances must have *all* listed characteristics.
    """

    provenance: str | None = None
    real_or_synthetic: str | None = None
    min_dimensions: int | None = None
    max_dimensions: int | None = None
    landscape_characteristics: list[str] | None = None


@dataclass
class AlgorithmFilter:
    """Filter criteria for :meth:`AlgorithmRepository.list_algorithms`.

    Attributes
    ----------
    algorithm_family:
        Exact match (e.g. ``"random"``, ``"bayesian_tpe"``).
    supported_variable_types:
        Subset match — returned instances must support *all* listed types.
    framework:
        Exact match (e.g. ``"optuna"``, ``"stdlib"``).
    contributed_by:
        Exact match on contributor identifier.
    """

    algorithm_family: str | None = None
    supported_variable_types: list[str] | None = None
    framework: str | None = None
    contributed_by: str | None = None


@dataclass
class StudyFilter:
    """Filter criteria for :meth:`StudyRepository.list_studies`.

    Attributes
    ----------
    status:
        ``"draft"`` | ``"locked"`` | ``None``
    created_by:
        Exact match on creator identifier.
    problem_ids:
        Overlap match — returned Studies must include *at least one* of the given IDs.
    """

    status: str | None = None
    created_by: str | None = None
    problem_ids: list[str] | None = None


@dataclass
class RunFilter:
    """Filter criteria for :meth:`RunRepository.list_runs`.

    Attributes
    ----------
    status:
        ``"completed"`` | ``"failed"`` | ``None``
    problem_instance_id:
        Exact match on ``problem_id`` field.
    algorithm_instance_id:
        Exact match on ``algorithm_id`` field.
    """

    status: str | None = None
    problem_instance_id: str | None = None
    algorithm_instance_id: str | None = None


# ---------------------------------------------------------------------------
# Domain repository interfaces
# ---------------------------------------------------------------------------


class ProblemRepository(ABC):
    """Read/write access to Problem Instances.

    References
    ----------
    → interface-contracts.md §5 — ProblemRepository
    → data-format.md §2.1 — ProblemInstance schema
    """

    @abstractmethod
    def get_problem(
        self,
        id: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """Return the Problem Instance with the given ID.

        Parameters
        ----------
        id:
            UUID string of the Problem Instance.
        version:
            If ``None``, returns the latest non-deprecated version.
            If a semantic version string, returns exactly that version.

        Returns
        -------
        dict[str, Any]
            Complete Problem Instance record (data-format.md §2.1).

        Raises
        ------
        EntityNotFoundError
            If no Problem Instance with the given ID exists.
        VersionNotFoundError
            If ``version`` is specified and that version does not exist.

        Example
        -------
        >>> problem = repo.get_problem("prob-uuid-001")
        >>> problem["name"]
        'SyntheticNoisyRosenbrock2D'
        """

    @abstractmethod
    def list_problems(
        self,
        filters: ProblemFilter | None = None,
    ) -> list[dict[str, Any]]:
        """Return summaries of all non-deprecated Problem Instances.

        Parameters
        ----------
        filters:
            Optional filter criteria. ``None`` returns all non-deprecated instances.

        Returns
        -------
        list[dict[str, Any]]
            List of Problem Instance summary records. Never ``None``; may be empty.

        Example
        -------
        >>> summaries = repo.list_problems(ProblemFilter(max_dimensions=3))
        >>> [s["name"] for s in summaries]
        ['SyntheticNoisyRosenbrock2D', 'SyntheticNoisyBranin']
        """

    @abstractmethod
    def register_problem(self, problem: dict[str, Any]) -> str:
        """Validate and persist a new Problem Instance.

        Parameters
        ----------
        problem:
            Problem Instance record (data-format.md §2.1). Must not contain ``id``;
            the repository assigns a UUID.

        Returns
        -------
        str
            UUID string assigned to the new Problem Instance.

        Raises
        ------
        ValidationError
            If any data-format.md §2.1 validation rule fails (missing required field,
            invalid type, etc.).

        Example
        -------
        >>> pid = repo.register_problem({"name": "MyProblem", "dimensions": 2, ...})
        >>> isinstance(pid, str) and len(pid) == 36  # UUID format
        True
        """

    @abstractmethod
    def deprecate_problem(
        self,
        id: str,
        reason: str,
        superseded_by: str | None = None,
    ) -> None:
        """Mark a Problem Instance as deprecated.

        Deprecated instances are excluded from :meth:`list_problems` but remain
        retrievable by exact ID and version for reproducibility.

        Parameters
        ----------
        id:
            UUID of the Problem Instance to deprecate.
        reason:
            Human-readable reason for deprecation.
        superseded_by:
            UUID of the replacement Problem Instance, if any.

        Raises
        ------
        EntityNotFoundError
            If no Problem Instance with the given ID exists.

        Example
        -------
        >>> repo.deprecate_problem("old-prob-uuid", reason="Replaced by prob-002")
        """


class AlgorithmRepository(ABC):
    """Read/write access to Algorithm Instances.

    References
    ----------
    → interface-contracts.md §5 — AlgorithmRepository
    → data-format.md §2.2 — AlgorithmInstance schema
    """

    @abstractmethod
    def get_algorithm(
        self,
        id: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """Return the Algorithm Instance with the given ID.

        Parameters
        ----------
        id:
            UUID string of the Algorithm Instance.
        version:
            ``None`` → latest non-deprecated; version string → exact version.

        Returns
        -------
        dict[str, Any]
            Complete Algorithm Instance record (data-format.md §2.2).

        Raises
        ------
        EntityNotFoundError
            If no Algorithm Instance with the given ID exists.
        VersionNotFoundError
            If a specific version is requested and does not exist.

        Example
        -------
        >>> alg = repo.get_algorithm("alg-uuid-001")
        >>> alg["algorithm_family"]
        'random'
        """

    @abstractmethod
    def list_algorithms(
        self,
        filters: AlgorithmFilter | None = None,
    ) -> list[dict[str, Any]]:
        """Return summaries of all non-deprecated Algorithm Instances.

        Parameters
        ----------
        filters:
            Optional filter criteria. ``None`` returns all non-deprecated instances.

        Returns
        -------
        list[dict[str, Any]]
            List of Algorithm Instance summary records.

        Example
        -------
        >>> algs = repo.list_algorithms(AlgorithmFilter(algorithm_family="random"))
        >>> len(algs) >= 1
        True
        """

    @abstractmethod
    def register_algorithm(self, algorithm: dict[str, Any]) -> str:
        """Validate and persist a new Algorithm Instance.

        Parameters
        ----------
        algorithm:
            Algorithm Instance record (data-format.md §2.2). Must not contain ``id``.
            ``code_reference`` must be version-pinned (contains ``==`` or ``@``).
            ``configuration_justification`` must be non-empty (FR-07).

        Returns
        -------
        str
            UUID string assigned to the new Algorithm Instance.

        Raises
        ------
        ValidationError
            If any required field is missing or ``configuration_justification`` is empty.
        CodeReferenceError
            If ``code_reference`` is not version-pinned (FR-06).

        Example
        -------
        >>> aid = repo.register_algorithm({
        ...     "name": "MyTPE",
        ...     "algorithm_family": "bayesian_tpe",
        ...     "code_reference": "my-lib==1.0.0",
        ...     "configuration_justification": "Default settings.",
        ...     "supported_variable_types": ["continuous"],
        ... })
        >>> isinstance(aid, str)
        True
        """

    @abstractmethod
    def deprecate_algorithm(
        self,
        id: str,
        reason: str,
        superseded_by: str | None = None,
    ) -> None:
        """Mark an Algorithm Instance as deprecated.

        Parameters
        ----------
        id:
            UUID of the Algorithm Instance to deprecate.
        reason:
            Human-readable reason for deprecation.
        superseded_by:
            UUID of the replacement Algorithm Instance, if any.

        Raises
        ------
        EntityNotFoundError
            If no Algorithm Instance with the given ID exists.

        Example
        -------
        >>> repo.deprecate_algorithm("old-alg-uuid", reason="Superseded by alg-002")
        """


class StudyRepository(ABC):
    """Read/write access to Studies.

    References
    ----------
    → interface-contracts.md §5 — StudyRepository
    → data-format.md §2.3 — Study schema
    """

    @abstractmethod
    def get_study(
        self,
        id: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """Return the Study with the given ID.

        Parameters
        ----------
        id:
            UUID of the Study.
        version:
            ``None`` → latest version; version string → exact version.

        Returns
        -------
        dict[str, Any]
            Complete Study record (data-format.md §2.3).

        Raises
        ------
        EntityNotFoundError
            If no Study with the given ID exists.
        VersionNotFoundError
            If a specific version is requested and does not exist.

        Example
        -------
        >>> study = repo.get_study("study-uuid-001")
        >>> study["status"]
        'locked'
        """

    @abstractmethod
    def list_studies(
        self,
        filters: StudyFilter | None = None,
    ) -> list[dict[str, Any]]:
        """Return Study summary records matching the filter.

        Parameters
        ----------
        filters:
            Optional filter criteria. ``None`` returns all Studies.

        Returns
        -------
        list[dict[str, Any]]
            List of Study summary records.

        Example
        -------
        >>> locked = repo.list_studies(StudyFilter(status="locked"))
        >>> all(s["status"] == "locked" for s in locked)
        True
        """

    @abstractmethod
    def create_study(self, study: dict[str, Any]) -> str:
        """Persist a new Study in ``"draft"`` status.

        Parameters
        ----------
        study:
            Study record (data-format.md §2.3). Must not contain ``id``.
            ``status`` is ignored; the repository always sets it to ``"draft"``.

        Returns
        -------
        str
            UUID assigned to the new Study.

        Raises
        ------
        ValidationError
            If any required field is missing.

        Example
        -------
        >>> sid = repo.create_study({"name": "MyStudy", "research_question": "..."})
        >>> isinstance(sid, str)
        True
        """

    @abstractmethod
    def lock_study(self, id: str) -> None:
        """Transition a Study from ``"draft"`` to ``"locked"``.

        After locking, ``sampling_strategy``, ``log_scale_schedule``,
        ``improvement_epsilon``, and ``experimental_design`` fields are immutable.

        Parameters
        ----------
        id:
            UUID of the Study to lock.

        Raises
        ------
        EntityNotFoundError
            If no Study with the given ID exists.
        StudyAlreadyLockedError
            If the Study is already in ``"locked"`` status.
        ValidationError
            If required fields for locking are absent.

        Example
        -------
        >>> repo.lock_study("study-uuid-001")
        >>> repo.get_study("study-uuid-001")["status"]
        'locked'
        """


class ExperimentRepository(ABC):
    """Read/write access to Experiments.

    References
    ----------
    → interface-contracts.md §5 — ExperimentRepository
    → data-format.md §2.4 — Experiment schema
    """

    @abstractmethod
    def get_experiment(self, id: str) -> dict[str, Any]:
        """Return the Experiment with the given ID.

        Parameters
        ----------
        id:
            UUID of the Experiment.

        Returns
        -------
        dict[str, Any]
            Complete Experiment record (data-format.md §2.4).

        Raises
        ------
        EntityNotFoundError
            If no Experiment with the given ID exists.

        Example
        -------
        >>> exp = repo.get_experiment("exp-uuid-001")
        >>> exp["status"]
        'running'
        """

    @abstractmethod
    def list_experiments(
        self,
        study_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return Experiment summary records, optionally filtered by Study.

        Parameters
        ----------
        study_id:
            If given, return only Experiments for this Study UUID.

        Returns
        -------
        list[dict[str, Any]]
            List of Experiment summary records.

        Example
        -------
        >>> exps = repo.list_experiments(study_id="study-uuid-001")
        >>> all(e["study_id"] == "study-uuid-001" for e in exps)
        True
        """

    @abstractmethod
    def create_experiment(self, experiment: dict[str, Any]) -> str:
        """Persist a new Experiment in ``"running"`` status.

        Parameters
        ----------
        experiment:
            Experiment record (data-format.md §2.4). Must not contain ``id``.
            The referenced Study must exist and be in ``"locked"`` status.

        Returns
        -------
        str
            UUID assigned to the new Experiment.

        Raises
        ------
        ValidationError
            If the referenced Study does not exist or is not locked.

        Example
        -------
        >>> eid = repo.create_experiment({"study_id": "study-uuid-001", ...})
        >>> isinstance(eid, str)
        True
        """

    @abstractmethod
    def update_experiment(self, id: str, **fields: Any) -> None:
        """Update mutable fields of an Experiment.

        Mutable fields: ``status``, ``completed_at``.
        Immutable fields (``study_id``, ``execution_environment``) cannot be
        changed after creation.

        Parameters
        ----------
        id:
            UUID of the Experiment to update.
        **fields:
            Field names and new values.

        Raises
        ------
        EntityNotFoundError
            If no Experiment with the given ID exists.
        ImmutableFieldError
            If any key in ``fields`` is an immutable field.

        Example
        -------
        >>> repo.update_experiment("exp-uuid-001", status="completed")
        >>> repo.get_experiment("exp-uuid-001")["status"]
        'completed'
        """


class RunRepository(ABC):
    """Read/write access to Runs and their PerformanceRecords.

    References
    ----------
    → interface-contracts.md §5 — RunRepository
    → data-format.md §2.5 — Run schema
    → data-format.md §2.6 — PerformanceRecord schema
    """

    @abstractmethod
    def get_run(self, id: str) -> dict[str, Any]:
        """Return the Run with the given ID.

        Parameters
        ----------
        id:
            UUID of the Run.

        Returns
        -------
        dict[str, Any]
            Complete Run record (data-format.md §2.5).

        Raises
        ------
        EntityNotFoundError
            If no Run with the given ID exists.

        Example
        -------
        >>> run = repo.get_run("run-uuid-001")
        >>> run["status"]
        'completed'
        """

    @abstractmethod
    def list_runs(
        self,
        experiment_id: str,
        filters: RunFilter | None = None,
    ) -> list[dict[str, Any]]:
        """Return Run summary records for the given Experiment.

        Parameters
        ----------
        experiment_id:
            UUID of the Experiment whose Runs to list.
        filters:
            Optional filter criteria.

        Returns
        -------
        list[dict[str, Any]]
            List of Run summary records.

        Example
        -------
        >>> runs = repo.list_runs("exp-uuid-001")
        >>> len(runs)
        60
        """

    @abstractmethod
    def create_run(self, run: dict[str, Any]) -> str:
        """Persist a new Run record.

        Parameters
        ----------
        run:
            Run record (data-format.md §2.5). Must not contain ``id``.

        Returns
        -------
        str
            UUID assigned to the new Run.

        Raises
        ------
        ValidationError
            If required fields are missing.

        Example
        -------
        >>> rid = repo.create_run({"experiment_id": "exp-uuid-001", "seed": 42, ...})
        >>> isinstance(rid, str)
        True
        """

    @abstractmethod
    def update_run(self, id: str, **fields: Any) -> None:
        """Update mutable fields of a Run.

        Mutable fields: ``status``, ``budget_used``, ``completed_at``,
        ``failure_reason``, ``cap_reached_at_evaluation``.

        Parameters
        ----------
        id:
            UUID of the Run to update.
        **fields:
            Field names and new values.

        Raises
        ------
        EntityNotFoundError
            If no Run with the given ID exists.

        Example
        -------
        >>> repo.update_run("run-uuid-001", status="failed", failure_reason="OOM")
        """

    @abstractmethod
    def save_performance_records(
        self,
        run_id: str,
        records: list[dict[str, Any]],
    ) -> None:
        """Append PerformanceRecords for the given Run.

        Records must be supplied in ascending ``evaluation_number`` order and must
        not duplicate ``evaluation_number`` values already stored for this Run.

        Parameters
        ----------
        run_id:
            UUID of the Run these records belong to.
        records:
            List of PerformanceRecord dicts (data-format.md §2.6), each with
            ``evaluation_number``, ``objective_value``, ``best_so_far``.

        Raises
        ------
        EntityNotFoundError
            If no Run with the given ``run_id`` exists.
        ValidationError
            If ``evaluation_number`` sequence is not strictly monotonic.
        DuplicateEvaluationError
            If any ``evaluation_number`` already exists for this Run.

        Example
        -------
        >>> repo.save_performance_records("run-uuid-001", [
        ...     {"evaluation_number": 1, "objective_value": 3.14, "best_so_far": 3.14},
        ... ])
        """

    @abstractmethod
    def get_performance_records(
        self,
        run_id: str,
    ) -> list[dict[str, Any]]:
        """Return all PerformanceRecords for the given Run, sorted ascending.

        Parameters
        ----------
        run_id:
            UUID of the Run.

        Returns
        -------
        list[dict[str, Any]]
            PerformanceRecord dicts sorted by ``evaluation_number`` ascending.

        Raises
        ------
        EntityNotFoundError
            If no Run with the given ``run_id`` exists.

        Example
        -------
        >>> records = repo.get_performance_records("run-uuid-001")
        >>> records[0]["evaluation_number"]
        1
        """


class ResultAggregateRepository(ABC):
    """Read/write access to Result Aggregates.

    References
    ----------
    → interface-contracts.md §5 — ResultAggregateRepository
    → data-format.md §2.7 — ResultAggregate schema
    """

    @abstractmethod
    def get_result_aggregate(self, id: str) -> dict[str, Any]:
        """Return the Result Aggregate with the given ID.

        Parameters
        ----------
        id:
            UUID of the Result Aggregate.

        Returns
        -------
        dict[str, Any]
            Complete Result Aggregate record (data-format.md §2.7).

        Raises
        ------
        EntityNotFoundError
            If no Result Aggregate with the given ID exists.

        Example
        -------
        >>> agg = repo.get_result_aggregate("agg-uuid-001")
        >>> "QUALITY-BEST_VALUE_AT_BUDGET" in agg["metrics"]
        True
        """

    @abstractmethod
    def list_result_aggregates(
        self,
        experiment_id: str,
    ) -> list[dict[str, Any]]:
        """Return all Result Aggregates for the given Experiment.

        Parameters
        ----------
        experiment_id:
            UUID of the Experiment.

        Returns
        -------
        list[dict[str, Any]]
            List of Result Aggregate records.

        Example
        -------
        >>> aggs = repo.list_result_aggregates("exp-uuid-001")
        >>> len(aggs)  # 3 problems × 2 algorithms = 6
        6
        """

    @abstractmethod
    def save_result_aggregates(
        self,
        aggregates: list[dict[str, Any]],
    ) -> None:
        """Persist a batch of Result Aggregates.

        All aggregates must reference the same Experiment.

        Parameters
        ----------
        aggregates:
            List of Result Aggregate records (data-format.md §2.7).
            Each must have ``experiment_id``, ``problem_id``, ``algorithm_id``,
            ``n_runs``, and ``metrics``.

        Raises
        ------
        ValidationError
            If any required field is missing or metric names are not in
            metric-taxonomy.md.

        Example
        -------
        >>> repo.save_result_aggregates([{
        ...     "experiment_id": "exp-uuid-001",
        ...     "problem_id": "prob-uuid-001",
        ...     "algorithm_id": "alg-uuid-001",
        ...     "n_runs": 10,
        ...     "metrics": {"QUALITY-BEST_VALUE_AT_BUDGET": {"median": 0.05}},
        ... }])
        """


class ReportRepository(ABC):
    """Read/write access to Reports.

    References
    ----------
    → interface-contracts.md §5 — ReportRepository
    → data-format.md §2.8 — Report schema
    """

    @abstractmethod
    def get_report(self, id: str) -> dict[str, Any]:
        """Return the Report with the given ID.

        Parameters
        ----------
        id:
            UUID of the Report.

        Returns
        -------
        dict[str, Any]
            Complete Report record (data-format.md §2.8).

        Raises
        ------
        EntityNotFoundError
            If no Report with the given ID exists.

        Example
        -------
        >>> report = repo.get_report("report-uuid-001")
        >>> report["report_type"]
        'researcher'
        """

    @abstractmethod
    def list_reports(self, experiment_id: str) -> list[dict[str, Any]]:
        """Return all Reports for the given Experiment.

        Parameters
        ----------
        experiment_id:
            UUID of the Experiment.

        Returns
        -------
        list[dict[str, Any]]
            List of Report records. Exactly two expected per completed Experiment
            (one ``"researcher"``, one ``"practitioner"``).

        Example
        -------
        >>> reports = repo.list_reports("exp-uuid-001")
        >>> {r["report_type"] for r in reports}
        {'researcher', 'practitioner'}
        """

    @abstractmethod
    def save_report(self, report: dict[str, Any]) -> str:
        """Persist a Report.

        Parameters
        ----------
        report:
            Report record (data-format.md §2.8). Must not contain ``id``.
            ``limitations`` must be non-empty (FR-21).
            ``artifact_reference`` must be present.

        Returns
        -------
        str
            UUID assigned to the new Report.

        Raises
        ------
        ValidationError
            If ``limitations`` is empty or ``artifact_reference`` is missing.

        Example
        -------
        >>> rid = repo.save_report({
        ...     "report_type": "researcher",
        ...     "experiment_id": "exp-uuid-001",
        ...     "limitations": ["Scope: 3 tested problems only."],
        ...     "artifact_reference": "study_001/reports/researcher.html",
        ... })
        >>> isinstance(rid, str)
        True
        """


# ---------------------------------------------------------------------------
# RepositoryFactory
# ---------------------------------------------------------------------------


class RepositoryFactory(ABC):
    """Groups all domain repositories.

    Components that need cross-entity access receive a :class:`RepositoryFactory`
    instance rather than individual repositories. This keeps the component API
    stable when repository implementations are swapped.

    ``LocalFileRepository`` (V1) implements all seven domain interfaces and exposes
    itself as a :class:`RepositoryFactory`. Server-backed implementations (V2)
    replace individual interfaces independently without changing the factory contract.

    References
    ----------
    → interface-contracts.md §5 — RepositoryFactory
    → ADR-001 — the swap contract that makes V2 migration a plug-in, not a migration

    Example
    -------
    >>> factory = InMemoryRepositoryFactory()
    >>> factory.problems.register_problem({"name": "P1", "dimensions": 2})
    'some-uuid'
    """

    @property
    @abstractmethod
    def problems(self) -> ProblemRepository:
        """Problem Instance repository."""

    @property
    @abstractmethod
    def algorithms(self) -> AlgorithmRepository:
        """Algorithm Instance repository."""

    @property
    @abstractmethod
    def studies(self) -> StudyRepository:
        """Study repository."""

    @property
    @abstractmethod
    def experiments(self) -> ExperimentRepository:
        """Experiment repository."""

    @property
    @abstractmethod
    def runs(self) -> RunRepository:
        """Run and PerformanceRecord repository."""

    @property
    @abstractmethod
    def aggregates(self) -> ResultAggregateRepository:
        """Result Aggregate repository."""

    @property
    @abstractmethod
    def reports(self) -> ReportRepository:
        """Report repository."""
