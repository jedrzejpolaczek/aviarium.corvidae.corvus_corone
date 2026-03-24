"""LocalFileRepository — V1 production storage backend.

Stores all entities as JSON files on the local filesystem. Each entity type
lives in its own subdirectory; files are named by UUID with no path-based
entity references inside the JSON content.

Directory layout produced under ``root_dir``::

    <root_dir>/
    ├── problems/
    │   └── <uuid>.json            ProblemInstance   (§2.1)
    ├── algorithms/
    │   └── <uuid>.json            AlgorithmInstance (§2.2)
    ├── studies/
    │   └── <uuid>.json            Study             (§2.3)
    ├── experiments/
    │   └── <uuid>.json            Experiment        (§2.4)
    ├── runs/
    │   └── <uuid>/
    │       ├── run.json           Run               (§2.5)
    │       └── performance_records.jsonl  PerformanceRecords (§2.6)
    ├── aggregates/
    │   └── <uuid>.json            ResultAggregate   (§2.7)
    └── reports/
        └── <uuid>.json            Report            (§2.8)

**Important design note (ADR-001):** This directory layout is an
*implementation detail of* ``LocalFileRepository``. It is **not** part of the
public ``RepositoryFactory`` interface. A ``ServerRepository`` (V2) or any
other future backend can fulfil the same interface without this layout.
Consumer code must never assume or traverse this tree directly — all access
goes through the ``RepositoryFactory`` properties.

References
----------
→ docs/03-technical-contracts/01-data-format/10-file-formats.md §3.2
→ docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md
→ docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md
"""

from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from pathlib import Path
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

# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------


def _new_id() -> str:
    """Return a new UUID v4 string."""
    return str(uuid.uuid4())


def _read_json(path: Path) -> dict[str, Any]:
    """Read and parse a JSON file. Caller is responsible for existence check."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)  # type: ignore[no-any-return]


def _write_json(path: Path, data: dict[str, Any]) -> None:
    """Write data to a JSON file, creating parent directories as needed.

    Uses a write-then-rename pattern to avoid partially written files on
    crash (best-effort; Windows rename is not atomic but is safe for V1).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    tmp_path.replace(path)


def _append_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    """Append records to a JSON Lines file, one JSON object per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSON Lines file. Returns empty list if file does not exist."""
    if not path.exists():
        return []
    result: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                result.append(json.loads(line))
    return result


# ---------------------------------------------------------------------------
# Validation helpers (shared with in_memory.py logic)
# ---------------------------------------------------------------------------


def _require(entity: dict[str, Any], *fields: str, entity_type: str) -> None:
    """Raise ValidationError if any of the given fields are missing or empty."""
    for field in fields:
        if field not in entity or entity[field] is None or entity[field] == "":
            raise ValidationError(
                f"{entity_type}: required field '{field}' is missing or empty.",
                context={"entity_type": entity_type, "field": field},
            )


_VERSION_PIN_INDICATORS = ("==", "@", "git+")


def _is_version_pinned(code_reference: str) -> bool:
    return any(ind in code_reference for ind in _VERSION_PIN_INDICATORS)


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

_EXPERIMENT_IMMUTABLE_FIELDS = frozenset({"study_id", "execution_environment"})


# ---------------------------------------------------------------------------
# Domain repositories — file-backed implementations
# ---------------------------------------------------------------------------


class _FileProblemRepository(ProblemRepository):
    """File-backed ProblemRepository. Each instance stored as <uuid>.json."""

    def __init__(self, base: Path) -> None:
        self._base = base
        base.mkdir(parents=True, exist_ok=True)

    def _path(self, entity_id: str) -> Path:
        return self._base / f"{entity_id}.json"

    def get_problem(self, id: str, version: str | None = None) -> dict[str, Any]:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"ProblemInstance with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(_read_json(p))

    def list_problems(self, filters: ProblemFilter | None = None) -> list[dict[str, Any]]:
        results = [
            deepcopy(_read_json(p))
            for p in self._base.glob("*.json")
            if not _read_json(p).get("deprecated", False)
        ]
        if filters is None:
            return results
        if filters.min_dimensions is not None:
            results = [r for r in results if r.get("dimensions", 0) >= filters.min_dimensions]
        if filters.max_dimensions is not None:
            results = [r for r in results if r.get("dimensions", 0) <= filters.max_dimensions]
        provenance = filters.provenance or filters.real_or_synthetic
        if provenance is not None:
            results = [r for r in results if r.get("provenance") == provenance]
        if filters.landscape_characteristics:
            required = set(filters.landscape_characteristics)
            results = [
                r for r in results if required.issubset(set(r.get("landscape_characteristics", [])))
            ]
        return results

    def register_problem(self, problem: dict[str, Any]) -> str:
        _require(problem, "name", entity_type="ProblemInstance")
        record = deepcopy(problem)
        new_id = _new_id()
        record["id"] = new_id
        record.setdefault("deprecated", False)
        _write_json(self._path(new_id), record)
        return new_id

    def deprecate_problem(
        self,
        id: str,
        reason: str,
        superseded_by: str | None = None,
    ) -> None:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"ProblemInstance with id='{id}' not found.",
                context={"id": id},
            )
        record = _read_json(p)
        record["deprecated"] = True
        record["deprecation_reason"] = reason
        if superseded_by is not None:
            record["superseded_by"] = superseded_by
        _write_json(p, record)


class _FileAlgorithmRepository(AlgorithmRepository):
    """File-backed AlgorithmRepository. Each instance stored as <uuid>.json."""

    def __init__(self, base: Path) -> None:
        self._base = base
        base.mkdir(parents=True, exist_ok=True)

    def _path(self, entity_id: str) -> Path:
        return self._base / f"{entity_id}.json"

    def get_algorithm(self, id: str, version: str | None = None) -> dict[str, Any]:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"AlgorithmInstance with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(_read_json(p))

    def list_algorithms(self, filters: AlgorithmFilter | None = None) -> list[dict[str, Any]]:
        results = [
            deepcopy(_read_json(p))
            for p in self._base.glob("*.json")
            if not _read_json(p).get("deprecated", False)
        ]
        if filters is None:
            return results
        if filters.algorithm_family is not None:
            results = [r for r in results if r.get("algorithm_family") == filters.algorithm_family]
        if filters.framework is not None:
            results = [r for r in results if r.get("framework") == filters.framework]
        if filters.contributed_by is not None:
            results = [r for r in results if r.get("contributed_by") == filters.contributed_by]
        if filters.supported_variable_types:
            required = set(filters.supported_variable_types)
            results = [
                r for r in results if required.issubset(set(r.get("supported_variable_types", [])))
            ]
        return results

    def register_algorithm(self, algorithm: dict[str, Any]) -> str:
        _require(algorithm, "name", entity_type="AlgorithmInstance")
        justification = algorithm.get("configuration_justification", "")
        if not justification or not str(justification).strip():
            raise ValidationError(
                "AlgorithmInstance: 'configuration_justification' must be non-empty (FR-07).",
                context={"field": "configuration_justification"},
            )
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
        new_id = _new_id()
        record["id"] = new_id
        record.setdefault("deprecated", False)
        _write_json(self._path(new_id), record)
        return new_id

    def deprecate_algorithm(
        self,
        id: str,
        reason: str,
        superseded_by: str | None = None,
    ) -> None:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"AlgorithmInstance with id='{id}' not found.",
                context={"id": id},
            )
        record = _read_json(p)
        record["deprecated"] = True
        record["deprecation_reason"] = reason
        if superseded_by is not None:
            record["superseded_by"] = superseded_by
        _write_json(p, record)


class _FileStudyRepository(StudyRepository):
    """File-backed StudyRepository. Each Study stored as <uuid>.json."""

    def __init__(self, base: Path) -> None:
        self._base = base
        base.mkdir(parents=True, exist_ok=True)

    def _path(self, entity_id: str) -> Path:
        return self._base / f"{entity_id}.json"

    def get_study(self, id: str, version: str | None = None) -> dict[str, Any]:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"Study with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(_read_json(p))

    def list_studies(self, filters: StudyFilter | None = None) -> list[dict[str, Any]]:
        results = [deepcopy(_read_json(p)) for p in self._base.glob("*.json")]
        if filters is None:
            return results
        if filters.status is not None:
            results = [r for r in results if r.get("status") == filters.status]
        if filters.created_by is not None:
            results = [r for r in results if r.get("created_by") == filters.created_by]
        if filters.problem_ids:
            overlap = set(filters.problem_ids)
            results = [r for r in results if overlap.intersection(set(r.get("problem_ids", [])))]
        return results

    def create_study(self, study: dict[str, Any]) -> str:
        _require(study, "name", entity_type="Study")
        record = deepcopy(study)
        new_id = _new_id()
        record["id"] = new_id
        record["status"] = "draft"
        _write_json(self._path(new_id), record)
        return new_id

    def lock_study(self, id: str) -> None:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"Study with id='{id}' not found.",
                context={"id": id},
            )
        record = _read_json(p)
        if record["status"] == "locked":
            raise StudyAlreadyLockedError(
                f"Study '{id}' is already locked. Modification attempt recorded.",
                context={"id": id},
            )
        for field in _STUDY_LOCK_REQUIRED_FIELDS:
            val = record.get(field)
            if val is None or val == "" or val == []:
                raise ValidationError(
                    f"Study cannot be locked: required field '{field}' is missing or empty.",
                    context={"id": id, "field": field},
                )
        record["status"] = "locked"
        _write_json(p, record)


class _FileExperimentRepository(ExperimentRepository):
    """File-backed ExperimentRepository. Each Experiment stored as <uuid>.json."""

    def __init__(self, base: Path) -> None:
        self._base = base
        base.mkdir(parents=True, exist_ok=True)

    def _path(self, entity_id: str) -> Path:
        return self._base / f"{entity_id}.json"

    def get_experiment(self, id: str) -> dict[str, Any]:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"Experiment with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(_read_json(p))

    def list_experiments(self, study_id: str | None = None) -> list[dict[str, Any]]:
        results = [deepcopy(_read_json(p)) for p in self._base.glob("*.json")]
        if study_id is not None:
            results = [r for r in results if r.get("study_id") == study_id]
        return results

    def create_experiment(self, experiment: dict[str, Any]) -> str:
        _require(experiment, "study_id", entity_type="Experiment")
        record = deepcopy(experiment)
        new_id = _new_id()
        record["id"] = new_id
        record.setdefault("status", "running")
        _write_json(self._path(new_id), record)
        return new_id

    def update_experiment(self, id: str, **fields: Any) -> None:
        p = self._path(id)
        if not p.exists():
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
        record = _read_json(p)
        record.update(fields)
        _write_json(p, record)


class _FileRunRepository(RunRepository):
    """File-backed RunRepository.

    Each Run is stored in its own subdirectory::

        runs/<uuid>/
        ├── run.json                 Run metadata (§2.5)
        └── performance_records.jsonl  One record per line (§2.6)
    """

    def __init__(self, base: Path) -> None:
        self._base = base
        base.mkdir(parents=True, exist_ok=True)

    def _run_dir(self, run_id: str) -> Path:
        return self._base / run_id

    def _run_path(self, run_id: str) -> Path:
        return self._run_dir(run_id) / "run.json"

    def _records_path(self, run_id: str) -> Path:
        return self._run_dir(run_id) / "performance_records.jsonl"

    def get_run(self, id: str) -> dict[str, Any]:
        p = self._run_path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"Run with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(_read_json(p))

    def list_runs(
        self,
        experiment_id: str,
        filters: RunFilter | None = None,
    ) -> list[dict[str, Any]]:
        results = []
        for run_dir in self._base.iterdir():
            if not run_dir.is_dir():
                continue
            run_file = run_dir / "run.json"
            if not run_file.exists():
                continue
            record = _read_json(run_file)
            if record.get("experiment_id") == experiment_id:
                results.append(deepcopy(record))
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
        new_id = _new_id()
        record["id"] = new_id
        _write_json(self._run_path(new_id), record)
        # Touch the JSONL file so the directory structure is complete on creation
        self._records_path(new_id).touch()
        return new_id

    def update_run(self, id: str, **fields: Any) -> None:
        p = self._run_path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"Run with id='{id}' not found.",
                context={"id": id},
            )
        record = _read_json(p)
        record.update(fields)
        _write_json(p, record)

    def save_performance_records(
        self,
        run_id: str,
        records: list[dict[str, Any]],
    ) -> None:
        if not self._run_path(run_id).exists():
            raise EntityNotFoundError(
                f"Run with id='{run_id}' not found.",
                context={"run_id": run_id},
            )
        existing = _read_jsonl(self._records_path(run_id))
        existing_evals = {r["evaluation_number"] for r in existing}
        prev_eval = existing[-1]["evaluation_number"] if existing else 0

        validated: list[dict[str, Any]] = []
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
            validated.append(rec)

        _append_jsonl(self._records_path(run_id), validated)

    def get_performance_records(self, run_id: str) -> list[dict[str, Any]]:
        if not self._run_path(run_id).exists():
            raise EntityNotFoundError(
                f"Run with id='{run_id}' not found.",
                context={"run_id": run_id},
            )
        records = _read_jsonl(self._records_path(run_id))
        return sorted(deepcopy(records), key=lambda r: r["evaluation_number"])


class _FileResultAggregateRepository(ResultAggregateRepository):
    """File-backed ResultAggregateRepository. Each aggregate stored as <uuid>.json."""

    def __init__(self, base: Path) -> None:
        self._base = base
        base.mkdir(parents=True, exist_ok=True)

    def _path(self, entity_id: str) -> Path:
        return self._base / f"{entity_id}.json"

    def get_result_aggregate(self, id: str) -> dict[str, Any]:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"ResultAggregate with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(_read_json(p))

    def list_result_aggregates(self, experiment_id: str) -> list[dict[str, Any]]:
        return [
            deepcopy(_read_json(p))
            for p in self._base.glob("*.json")
            if _read_json(p).get("experiment_id") == experiment_id
        ]

    def save_result_aggregates(self, aggregates: list[dict[str, Any]]) -> None:
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
            new_id = _new_id()
            record["id"] = new_id
            _write_json(self._path(new_id), record)


class _FileReportRepository(ReportRepository):
    """File-backed ReportRepository. Each Report stored as <uuid>.json."""

    def __init__(self, base: Path) -> None:
        self._base = base
        base.mkdir(parents=True, exist_ok=True)

    def _path(self, entity_id: str) -> Path:
        return self._base / f"{entity_id}.json"

    def get_report(self, id: str) -> dict[str, Any]:
        p = self._path(id)
        if not p.exists():
            raise EntityNotFoundError(
                f"Report with id='{id}' not found.",
                context={"id": id},
            )
        return deepcopy(_read_json(p))

    def list_reports(self, experiment_id: str) -> list[dict[str, Any]]:
        return [
            deepcopy(_read_json(p))
            for p in self._base.glob("*.json")
            if _read_json(p).get("experiment_id") == experiment_id
        ]

    def save_report(self, report: dict[str, Any]) -> str:
        limitations = report.get("limitations", [])
        if not limitations:
            raise ValidationError(
                "Report: 'limitations' must be a non-empty list (FR-21).",
                context={"field": "limitations"},
            )
        _require(report, "artifact_reference", entity_type="Report")
        record = deepcopy(report)
        new_id = _new_id()
        record["id"] = new_id
        _write_json(self._path(new_id), record)
        return new_id


# ---------------------------------------------------------------------------
# LocalFileRepository — the public factory
# ---------------------------------------------------------------------------


class LocalFileRepository(RepositoryFactory):
    """RepositoryFactory backed by JSON files on the local filesystem (V1).

    This is the production storage backend for V1. It satisfies ADR-001's
    swap guarantee: the same client code that works with
    :class:`~corvus_corone.repository.in_memory.InMemoryRepositoryFactory`
    will work without modification when passed a ``LocalFileRepository``.

    **Directory layout:** all entities are stored under ``root_dir`` in
    a structure keyed exclusively by UUID. The exact layout is documented in
    ``data-format.md §3.2`` and is an *implementation detail* — consumer code
    must not traverse or depend on it directly (ADR-001).

    Parameters
    ----------
    root_dir:
        Filesystem path where all entity files will be stored. Created on
        first use if it does not exist. Accepts ``str`` or ``os.PathLike``.

    Usage
    -----
    >>> import tempfile, os
    >>> with tempfile.TemporaryDirectory() as tmp:
    ...     factory = LocalFileRepository(tmp)
    ...     pid = factory.problems.register_problem({"name": "P1", "dimensions": 2})
    ...     factory.problems.get_problem(pid)["name"]
    'P1'

    References
    ----------
    → docs/03-technical-contracts/01-data-format/10-file-formats.md §3.2
    → docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md
    """

    _SUBDIRS = ("problems", "algorithms", "studies", "experiments", "runs", "aggregates", "reports")

    def __init__(self, root_dir: str | os.PathLike[str]) -> None:
        self._root = Path(root_dir)
        for subdir in self._SUBDIRS:
            (self._root / subdir).mkdir(parents=True, exist_ok=True)

        self._problems_repo = _FileProblemRepository(self._root / "problems")
        self._algorithms_repo = _FileAlgorithmRepository(self._root / "algorithms")
        self._studies_repo = _FileStudyRepository(self._root / "studies")
        self._experiments_repo = _FileExperimentRepository(self._root / "experiments")
        self._runs_repo = _FileRunRepository(self._root / "runs")
        self._aggregates_repo = _FileResultAggregateRepository(self._root / "aggregates")
        self._reports_repo = _FileReportRepository(self._root / "reports")

    @property
    def root_dir(self) -> Path:
        """The filesystem root directory for this repository."""
        return self._root

    @property
    def problems(self) -> ProblemRepository:
        return self._problems_repo

    @property
    def algorithms(self) -> AlgorithmRepository:
        return self._algorithms_repo

    @property
    def studies(self) -> StudyRepository:
        return self._studies_repo

    @property
    def experiments(self) -> ExperimentRepository:
        return self._experiments_repo

    @property
    def runs(self) -> RunRepository:
        return self._runs_repo

    @property
    def aggregates(self) -> ResultAggregateRepository:
        return self._aggregates_repo

    @property
    def reports(self) -> ReportRepository:
        return self._reports_repo
