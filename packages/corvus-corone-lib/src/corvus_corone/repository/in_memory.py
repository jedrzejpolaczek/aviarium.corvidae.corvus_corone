"""In-memory implementation of all domain repositories.

:class:`InMemoryRepositoryFactory` is the V1 implementation used in tests
and local development. It stores all entities in Python dicts — no file I/O.
A :class:`LocalFileRepository` that writes JSON to disk is the production V1
target (future work); it will implement the same interfaces defined in
:mod:`corvus_corone.repository.interfaces`.

Design notes
------------
- All entity IDs are UUID v4 strings assigned by the repository on creation.
  Callers must not include ``id`` in the entity dict passed to create/register
  methods — the repository always assigns the ID.
- No file paths appear in any method signature or stored entity (ADR-001).
- Thread safety: not guaranteed. These implementations are single-threaded.

References
----------
→ docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md
→ docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md
"""

from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any

from corvus_corone.exceptions import (
    CodeReferenceError,
    DuplicateEvaluationError,
    EntityNotFoundError,
    ImmutableFieldError,
    StudyAlreadyLockedError,
    ValidationError,
)
from corvus_corone.repository.interfaces import (
    AlgorithmFilter,
    AlgorithmRepository,
    ExperimentRepository,
    ProblemFilter,
    ProblemRepository,
    ReportRepository,
    RepositoryFactory,
    ResultAggregateRepository,
    RunFilter,
    RunRepository,
    StudyFilter,
    StudyRepository,
)


def _new_id() -> str:
    """Return a new UUID v4 string."""
    return str(uuid.uuid4())


def _require(entity: dict[str, Any], *fields: str, entity_type: str) -> None:
    """Raise ValidationError if any of the given fields are missing or empty."""
    for field in fields:
        if field not in entity or entity[field] is None or entity[field] == "":
            raise ValidationError(
                f"{entity_type}: required field '{field}' is missing or empty.",
                context={"entity_type": entity_type, "field": field},
            )


# ---------------------------------------------------------------------------
# InMemoryProblemRepository
# ---------------------------------------------------------------------------


class _InMemoryProblemRepository(ProblemRepository):
    """In-memory ProblemRepository.

    Stores problem records in a dict keyed by UUID. Deprecated records are
    retained for reproducibility but excluded from list_problems().
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get_problem(
        self,
        id: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        if id not in self._store:
            raise EntityNotFoundError(
                f"ProblemInstance with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(self._store[id])

    def list_problems(
        self,
        filters: ProblemFilter | None = None,
    ) -> list[dict[str, Any]]:
        results = [deepcopy(p) for p in self._store.values() if not p.get("deprecated", False)]
        if filters is None:
            return results
        if filters.min_dimensions is not None:
            results = [p for p in results if p.get("dimensions", 0) >= filters.min_dimensions]
        if filters.max_dimensions is not None:
            results = [p for p in results if p.get("dimensions", 0) <= filters.max_dimensions]
        provenance = filters.provenance or filters.real_or_synthetic
        if provenance is not None:
            results = [p for p in results if p.get("provenance") == provenance]
        if filters.landscape_characteristics:
            required = set(filters.landscape_characteristics)
            results = [
                p for p in results if required.issubset(set(p.get("landscape_characteristics", [])))
            ]
        return results

    def register_problem(self, problem: dict[str, Any]) -> str:
        _require(problem, "name", entity_type="ProblemInstance")
        record = deepcopy(problem)
        record["id"] = _new_id()
        record.setdefault("deprecated", False)
        self._store[record["id"]] = record
        return record["id"]

    def deprecate_problem(
        self,
        id: str,
        reason: str,
        superseded_by: str | None = None,
    ) -> None:
        if id not in self._store:
            raise EntityNotFoundError(
                f"ProblemInstance with id='{id}' not found.",
                context={"id": id},
            )
        self._store[id]["deprecated"] = True
        self._store[id]["deprecation_reason"] = reason
        if superseded_by is not None:
            self._store[id]["superseded_by"] = superseded_by


# ---------------------------------------------------------------------------
# InMemoryAlgorithmRepository
# ---------------------------------------------------------------------------

# Code references must contain a version pin indicator
_VERSION_PIN_INDICATORS = ("==", "@", "git+")


def _is_version_pinned(code_reference: str) -> bool:
    return any(ind in code_reference for ind in _VERSION_PIN_INDICATORS)


class _InMemoryAlgorithmRepository(AlgorithmRepository):
    """In-memory AlgorithmRepository."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get_algorithm(
        self,
        id: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        if id not in self._store:
            raise EntityNotFoundError(
                f"AlgorithmInstance with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(self._store[id])

    def list_algorithms(
        self,
        filters: AlgorithmFilter | None = None,
    ) -> list[dict[str, Any]]:
        results = [deepcopy(a) for a in self._store.values() if not a.get("deprecated", False)]
        if filters is None:
            return results
        if filters.algorithm_family is not None:
            results = [a for a in results if a.get("algorithm_family") == filters.algorithm_family]
        if filters.framework is not None:
            results = [a for a in results if a.get("framework") == filters.framework]
        if filters.contributed_by is not None:
            results = [a for a in results if a.get("contributed_by") == filters.contributed_by]
        if filters.supported_variable_types:
            required = set(filters.supported_variable_types)
            results = [
                a for a in results if required.issubset(set(a.get("supported_variable_types", [])))
            ]
        return results

    def register_algorithm(self, algorithm: dict[str, Any]) -> str:
        _require(algorithm, "name", entity_type="AlgorithmInstance")
        # FR-07: configuration_justification must be non-empty
        justification = algorithm.get("configuration_justification", "")
        if not justification or not str(justification).strip():
            raise ValidationError(
                "AlgorithmInstance: 'configuration_justification' must be non-empty (FR-07).",
                context={"field": "configuration_justification"},
            )
        # FR-06: code_reference must be version-pinned
        code_ref = algorithm.get("code_reference", "")
        if not code_ref:
            raise ValidationError(
                "AlgorithmInstance: 'code_reference' is required.",
                context={"field": "code_reference"},
            )
        if not _is_version_pinned(str(code_ref)):
            raise CodeReferenceError(
                f"AlgorithmInstance: 'code_reference' must be version-pinned "
                f"(contains '==', '@', or 'git+'). Got: {code_ref!r} (FR-06).",
                context={"code_reference": code_ref},
            )
        record = deepcopy(algorithm)
        record["id"] = _new_id()
        record.setdefault("deprecated", False)
        self._store[record["id"]] = record
        return record["id"]

    def deprecate_algorithm(
        self,
        id: str,
        reason: str,
        superseded_by: str | None = None,
    ) -> None:
        if id not in self._store:
            raise EntityNotFoundError(
                f"AlgorithmInstance with id='{id}' not found.",
                context={"id": id},
            )
        self._store[id]["deprecated"] = True
        self._store[id]["deprecation_reason"] = reason
        if superseded_by is not None:
            self._store[id]["superseded_by"] = superseded_by


# ---------------------------------------------------------------------------
# InMemoryStudyRepository
# ---------------------------------------------------------------------------

_STUDY_LOCK_REQUIRED_FIELDS = (
    "name",
    "research_question",
    "problem_ids",
    "algorithm_ids",
    "repetitions",
    "budget",
    "seed_strategy",
    "sampling_strategy",
    "pre_registered_hypotheses",
)

_STUDY_IMMUTABLE_AFTER_LOCK = frozenset(
    {
        "sampling_strategy",
        "log_scale_schedule",
        "improvement_epsilon",
        "experimental_design",
        "problem_ids",
        "algorithm_ids",
        "repetitions",
        "budget",
        "pre_registered_hypotheses",
    }
)


class _InMemoryStudyRepository(StudyRepository):
    """In-memory StudyRepository."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get_study(
        self,
        id: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        if id not in self._store:
            raise EntityNotFoundError(
                f"Study with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(self._store[id])

    def list_studies(
        self,
        filters: StudyFilter | None = None,
    ) -> list[dict[str, Any]]:
        results = [deepcopy(s) for s in self._store.values()]
        if filters is None:
            return results
        if filters.status is not None:
            results = [s for s in results if s.get("status") == filters.status]
        if filters.created_by is not None:
            results = [s for s in results if s.get("created_by") == filters.created_by]
        if filters.problem_ids:
            overlap = set(filters.problem_ids)
            results = [s for s in results if overlap.intersection(set(s.get("problem_ids", [])))]
        return results

    def create_study(self, study: dict[str, Any]) -> str:
        _require(study, "name", entity_type="Study")
        record = deepcopy(study)
        record["id"] = _new_id()
        record["status"] = "draft"  # always starts as draft
        self._store[record["id"]] = record
        return record["id"]

    def lock_study(self, id: str) -> None:
        if id not in self._store:
            raise EntityNotFoundError(
                f"Study with id='{id}' not found.",
                context={"id": id},
            )
        study = self._store[id]
        if study["status"] == "locked":
            raise StudyAlreadyLockedError(
                f"Study '{id}' is already locked. Modification attempt recorded.",
                context={"id": id},
            )
        # Validate required fields are present before locking
        for field in _STUDY_LOCK_REQUIRED_FIELDS:
            val = study.get(field)
            if val is None or val == "" or val == []:
                raise ValidationError(
                    f"Study cannot be locked: required field '{field}' is missing or empty.",
                    context={"id": id, "field": field},
                )
        study["status"] = "locked"


# ---------------------------------------------------------------------------
# InMemoryExperimentRepository
# ---------------------------------------------------------------------------

_EXPERIMENT_IMMUTABLE_FIELDS = frozenset({"study_id", "execution_environment"})


class _InMemoryExperimentRepository(ExperimentRepository):
    """In-memory ExperimentRepository."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get_experiment(self, id: str) -> dict[str, Any]:
        if id not in self._store:
            raise EntityNotFoundError(
                f"Experiment with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(self._store[id])

    def list_experiments(
        self,
        study_id: str | None = None,
    ) -> list[dict[str, Any]]:
        results = [deepcopy(e) for e in self._store.values()]
        if study_id is not None:
            results = [e for e in results if e.get("study_id") == study_id]
        return results

    def create_experiment(self, experiment: dict[str, Any]) -> str:
        _require(experiment, "study_id", entity_type="Experiment")
        record = deepcopy(experiment)
        record["id"] = _new_id()
        record.setdefault("status", "running")
        self._store[record["id"]] = record
        return record["id"]

    def update_experiment(self, id: str, **fields: Any) -> None:
        if id not in self._store:
            raise EntityNotFoundError(
                f"Experiment with id='{id}' not found.",
                context={"id": id},
            )
        for key in fields:
            if key in _EXPERIMENT_IMMUTABLE_FIELDS:
                raise ImmutableFieldError(
                    f"Experiment field '{key}' is immutable after creation.",
                    context={"id": id, "field": key},
                )
        self._store[id].update(fields)


# ---------------------------------------------------------------------------
# InMemoryRunRepository
# ---------------------------------------------------------------------------


class _InMemoryRunRepository(RunRepository):
    """In-memory RunRepository."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        # run_id → list of PerformanceRecord dicts
        self._records: dict[str, list[dict[str, Any]]] = {}

    def get_run(self, id: str) -> dict[str, Any]:
        if id not in self._store:
            raise EntityNotFoundError(
                f"Run with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(self._store[id])

    def list_runs(
        self,
        experiment_id: str,
        filters: RunFilter | None = None,
    ) -> list[dict[str, Any]]:
        results = [
            deepcopy(r) for r in self._store.values() if r.get("experiment_id") == experiment_id
        ]
        if filters is None:
            return results
        if filters.status is not None:
            results = [r for r in results if r.get("status") == filters.status]
        if filters.problem_instance_id is not None:
            results = [r for r in results if r.get("problem_id") == filters.problem_instance_id]
        if filters.algorithm_instance_id is not None:
            results = [r for r in results if r.get("algorithm_id") == filters.algorithm_instance_id]
        return results

    def create_run(self, run: dict[str, Any]) -> str:
        _require(run, "experiment_id", entity_type="Run")
        record = deepcopy(run)
        record["id"] = _new_id()
        self._store[record["id"]] = record
        self._records[record["id"]] = []
        return record["id"]

    def update_run(self, id: str, **fields: Any) -> None:
        if id not in self._store:
            raise EntityNotFoundError(
                f"Run with id='{id}' not found.",
                context={"id": id},
            )
        self._store[id].update(fields)

    def save_performance_records(
        self,
        run_id: str,
        records: list[dict[str, Any]],
    ) -> None:
        if run_id not in self._store:
            raise EntityNotFoundError(
                f"Run with id='{run_id}' not found.",
                context={"run_id": run_id},
            )
        existing = self._records.get(run_id, [])
        existing_evals = {r["evaluation_number"] for r in existing}

        prev_eval = existing[-1]["evaluation_number"] if existing else 0

        for rec in records:
            eval_num = rec["evaluation_number"]
            if eval_num in existing_evals:
                raise DuplicateEvaluationError(
                    f"Run '{run_id}': evaluation_number={eval_num} already exists.",
                    context={"run_id": run_id, "evaluation_number": eval_num},
                )
            if eval_num <= prev_eval:
                raise ValidationError(
                    f"Run '{run_id}': evaluation_number={eval_num} is not strictly "
                    f"greater than previous={prev_eval}.",
                    context={
                        "run_id": run_id,
                        "evaluation_number": eval_num,
                        "previous": prev_eval,
                    },
                )
            existing_evals.add(eval_num)
            prev_eval = eval_num

        self._records[run_id].extend(deepcopy(records))

    def get_performance_records(self, run_id: str) -> list[dict[str, Any]]:
        if run_id not in self._store:
            raise EntityNotFoundError(
                f"Run with id='{run_id}' not found.",
                context={"run_id": run_id},
            )
        return sorted(
            deepcopy(self._records.get(run_id, [])),
            key=lambda r: r["evaluation_number"],
        )


# ---------------------------------------------------------------------------
# InMemoryResultAggregateRepository
# ---------------------------------------------------------------------------


class _InMemoryResultAggregateRepository(ResultAggregateRepository):
    """In-memory ResultAggregateRepository."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get_result_aggregate(self, id: str) -> dict[str, Any]:
        if id not in self._store:
            raise EntityNotFoundError(
                f"ResultAggregate with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(self._store[id])

    def list_result_aggregates(
        self,
        experiment_id: str,
    ) -> list[dict[str, Any]]:
        return [
            deepcopy(a) for a in self._store.values() if a.get("experiment_id") == experiment_id
        ]

    def save_result_aggregates(
        self,
        aggregates: list[dict[str, Any]],
    ) -> None:
        for agg in aggregates:
            _require(
                agg,
                "experiment_id",
                "problem_id",
                "algorithm_id",
                "n_runs",
                "metrics",
                entity_type="ResultAggregate",
            )
            record = deepcopy(agg)
            record["id"] = _new_id()
            self._store[record["id"]] = record


# ---------------------------------------------------------------------------
# InMemoryReportRepository
# ---------------------------------------------------------------------------


class _InMemoryReportRepository(ReportRepository):
    """In-memory ReportRepository."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get_report(self, id: str) -> dict[str, Any]:
        if id not in self._store:
            raise EntityNotFoundError(
                f"Report with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(self._store[id])

    def list_reports(self, experiment_id: str) -> list[dict[str, Any]]:
        return [
            deepcopy(r) for r in self._store.values() if r.get("experiment_id") == experiment_id
        ]

    def save_report(self, report: dict[str, Any]) -> str:
        # FR-21: limitations must be non-empty
        limitations = report.get("limitations", [])
        if not limitations:
            raise ValidationError(
                "Report: 'limitations' must be a non-empty list (FR-21).",
                context={"field": "limitations"},
            )
        _require(report, "artifact_reference", entity_type="Report")
        record = deepcopy(report)
        record["id"] = _new_id()
        self._store[record["id"]] = record
        return record["id"]


# ---------------------------------------------------------------------------
# InMemoryRepositoryFactory
# ---------------------------------------------------------------------------


class InMemoryRepositoryFactory(RepositoryFactory):
    """RepositoryFactory backed entirely by in-memory Python dicts.

    This is the V1 test/development implementation. No file I/O is performed.
    The same client code that works with this factory will work with any other
    :class:`~corvus_corone.repository.interfaces.RepositoryFactory` implementation
    (e.g., a future ``LocalFileRepository`` or ``ServerRepository``) without
    modification — that is the ADR-001 swap guarantee.

    Usage
    -----
    >>> factory = InMemoryRepositoryFactory()
    >>> pid = factory.problems.register_problem({"name": "P1", "dimensions": 2})
    >>> factory.problems.get_problem(pid)["name"]
    'P1'

    References
    ----------
    → ADR-001 — swap contract (V1→V2 is a plug-in, not a migration)
    → interface-contracts.md §5 — RepositoryFactory contract
    """

    def __init__(self) -> None:
        self._problems = _InMemoryProblemRepository()
        self._algorithms = _InMemoryAlgorithmRepository()
        self._studies = _InMemoryStudyRepository()
        self._experiments = _InMemoryExperimentRepository()
        self._runs = _InMemoryRunRepository()
        self._aggregates = _InMemoryResultAggregateRepository()
        self._reports = _InMemoryReportRepository()

    @property
    def problems(self) -> ProblemRepository:
        return self._problems

    @property
    def algorithms(self) -> AlgorithmRepository:
        return self._algorithms

    @property
    def studies(self) -> StudyRepository:
        return self._studies

    @property
    def experiments(self) -> ExperimentRepository:
        return self._experiments

    @property
    def runs(self) -> RunRepository:
        return self._runs

    @property
    def aggregates(self) -> ResultAggregateRepository:
        return self._aggregates

    @property
    def reports(self) -> ReportRepository:
        return self._reports
