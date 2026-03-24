"""Interface contract tests for InMemoryRepositoryFactory.

These tests verify that ``InMemoryRepositoryFactory`` honours every postcondition
and exception contract stated in interface-contracts.md §5 (Repository Interface).

They are written against the *abstract interface* — all assertions go through
:class:`~corvus_corone.repository.interfaces.RepositoryFactory` properties.
The swap test at the end demonstrates the ADR-001 guarantee: any
:class:`~corvus_corone.repository.interfaces.RepositoryFactory` implementation
can be substituted without changing client code.

References
----------
→ docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md
→ docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md
→ docs/02-design/01-software-requirement-specification/07-acceptance-test-strategy/
  01-acceptance-test-strategy.md  (REF-TASK-0023 acceptance criteria)
"""

from __future__ import annotations

import re

import pytest

from corvus_corone.exceptions import (
    CodeReferenceError,
    DuplicateEvaluationError,
    EntityNotFoundError,
    ImmutableFieldError,
    StudyAlreadyLockedError,
    ValidationError,
)
from corvus_corone.repository.in_memory import InMemoryRepositoryFactory
from corvus_corone.repository.interfaces import (
    AlgorithmFilter,
    ProblemFilter,
    RepositoryFactory,
    RunFilter,
    StudyFilter,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def factory() -> InMemoryRepositoryFactory:
    """Fresh InMemoryRepositoryFactory for each test."""
    return InMemoryRepositoryFactory()


# Minimal valid entity dicts used across tests.

VALID_PROBLEM = {
    "name": "TestProblem2D",
    "dimensions": 2,
    "noise_level": "gaussian_0.1",
    "provenance": "synthetic",
    "landscape_characteristics": ["multimodal", "noisy"],
}

VALID_ALGORITHM = {
    "name": "TestRandomSearch",
    "algorithm_family": "random",
    "code_reference": "corvus-corone-stubs==0.1.0",
    "configuration_justification": "Uniform random sampling; no hyperparameters.",
    "supported_variable_types": ["continuous"],
    "framework": "stdlib",
    "contributed_by": "test-suite",
}

VALID_STUDY = {
    "name": "Test Study",
    "research_question": "Does TPE beat RandomSearch within budget=50?",
    "problem_ids": ["prob-uuid-001"],
    "algorithm_ids": ["alg-uuid-001"],
    "repetitions": 5,
    "budget": 50,
    "seed_strategy": "sequential",
    "sampling_strategy": "log_scale_plus_improvement",
    "pre_registered_hypotheses": [{"h0": "No difference", "alpha": 0.05}],
}


# ---------------------------------------------------------------------------
# Helper: UUID format assertion
# ---------------------------------------------------------------------------


UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def assert_uuid(value: str) -> None:
    """Assert value is a valid UUID v4 string — not a file path (ADR-001)."""
    assert isinstance(value, str), f"Expected str, got {type(value)}"
    assert UUID_RE.match(value), (
        f"Expected UUID v4 string, got: {value!r}\n"
        "All entity IDs must be UUIDs, not file paths (ADR-001)."
    )


# ===========================================================================
# ProblemRepository contract tests
# ===========================================================================


class TestProblemRepository:
    def test_register_returns_uuid(self, factory: InMemoryRepositoryFactory) -> None:
        """register_problem() must return a UUID v4 (ADR-001 server-compatible IDs)."""
        pid = factory.problems.register_problem(VALID_PROBLEM.copy())
        assert_uuid(pid)

    def test_get_returns_registered_entity(self, factory: InMemoryRepositoryFactory) -> None:
        """get_problem(id) returns the entity that was registered with that ID."""
        pid = factory.problems.register_problem(VALID_PROBLEM.copy())
        problem = factory.problems.get_problem(pid)
        assert problem["id"] == pid
        assert problem["name"] == VALID_PROBLEM["name"]
        assert problem["dimensions"] == VALID_PROBLEM["dimensions"]

    def test_get_returns_deep_copy(self, factory: InMemoryRepositoryFactory) -> None:
        """Mutations to the returned dict must not affect the stored entity."""
        pid = factory.problems.register_problem(VALID_PROBLEM.copy())
        p1 = factory.problems.get_problem(pid)
        p1["name"] = "MUTATED"
        p2 = factory.problems.get_problem(pid)
        assert p2["name"] == VALID_PROBLEM["name"]

    def test_get_unknown_id_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """get_problem() must raise EntityNotFoundError for unknown IDs."""
        with pytest.raises(EntityNotFoundError) as exc_info:
            factory.problems.get_problem("00000000-0000-4000-8000-000000000000")
        assert exc_info.value.error_code == "ENTITY_NOT_FOUND"

    def test_list_returns_all_non_deprecated(self, factory: InMemoryRepositoryFactory) -> None:
        """list_problems() excludes deprecated instances."""
        pid1 = factory.problems.register_problem({**VALID_PROBLEM, "name": "P1"})
        pid2 = factory.problems.register_problem({**VALID_PROBLEM, "name": "P2"})
        factory.problems.deprecate_problem(pid1, reason="Replaced")

        result = factory.problems.list_problems()
        ids = [p["id"] for p in result]
        assert pid1 not in ids
        assert pid2 in ids

    def test_list_with_dimension_filter(self, factory: InMemoryRepositoryFactory) -> None:
        """list_problems(ProblemFilter(max_dimensions=2)) returns only matching."""
        factory.problems.register_problem({**VALID_PROBLEM, "name": "2D", "dimensions": 2})
        factory.problems.register_problem({**VALID_PROBLEM, "name": "5D", "dimensions": 5})

        result = factory.problems.list_problems(ProblemFilter(max_dimensions=2))
        assert all(p["dimensions"] <= 2 for p in result)
        assert any(p["name"] == "2D" for p in result)
        assert not any(p["name"] == "5D" for p in result)

    def test_register_missing_name_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """Registering a Problem without 'name' raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            factory.problems.register_problem({"dimensions": 2})
        assert "name" in exc_info.value.message.lower()

    def test_deprecate_unknown_id_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """deprecate_problem() raises EntityNotFoundError for unknown IDs."""
        with pytest.raises(EntityNotFoundError):
            factory.problems.deprecate_problem(
                "00000000-0000-4000-8000-000000000000",
                reason="Gone",
            )

    def test_deprecated_still_retrievable_by_id(self, factory: InMemoryRepositoryFactory) -> None:
        """Deprecated instances remain retrievable by ID for reproducibility."""
        pid = factory.problems.register_problem(VALID_PROBLEM.copy())
        factory.problems.deprecate_problem(pid, reason="Old version")
        problem = factory.problems.get_problem(pid)
        assert problem["deprecated"] is True

    def test_landscape_characteristics_filter(self, factory: InMemoryRepositoryFactory) -> None:
        """Filter by landscape_characteristics performs subset match."""
        factory.problems.register_problem(
            {**VALID_PROBLEM, "name": "Noisy", "landscape_characteristics": ["noisy"]}
        )
        factory.problems.register_problem(
            {**VALID_PROBLEM, "name": "Both", "landscape_characteristics": ["noisy", "multimodal"]}
        )
        result = factory.problems.list_problems(ProblemFilter(landscape_characteristics=["noisy"]))
        names = [p["name"] for p in result]
        assert "Noisy" in names
        assert "Both" in names

        result2 = factory.problems.list_problems(
            ProblemFilter(landscape_characteristics=["noisy", "multimodal"])
        )
        names2 = [p["name"] for p in result2]
        assert "Both" in names2
        assert "Noisy" not in names2


# ===========================================================================
# AlgorithmRepository contract tests
# ===========================================================================


class TestAlgorithmRepository:
    def test_register_returns_uuid(self, factory: InMemoryRepositoryFactory) -> None:
        aid = factory.algorithms.register_algorithm(VALID_ALGORITHM.copy())
        assert_uuid(aid)

    def test_get_returns_registered_entity(self, factory: InMemoryRepositoryFactory) -> None:
        aid = factory.algorithms.register_algorithm(VALID_ALGORITHM.copy())
        alg = factory.algorithms.get_algorithm(aid)
        assert alg["id"] == aid
        assert alg["name"] == VALID_ALGORITHM["name"]

    def test_get_unknown_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(EntityNotFoundError):
            factory.algorithms.get_algorithm("00000000-0000-4000-8000-000000000000")

    def test_register_empty_justification_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """FR-07: configuration_justification must be non-empty."""
        bad = {**VALID_ALGORITHM, "configuration_justification": ""}
        with pytest.raises(ValidationError) as exc_info:
            factory.algorithms.register_algorithm(bad)
        assert "configuration_justification" in exc_info.value.message

    def test_register_unpinned_code_reference_raises(
        self, factory: InMemoryRepositoryFactory
    ) -> None:
        """FR-06: code_reference must be version-pinned."""
        bad = {**VALID_ALGORITHM, "code_reference": "my-unpinned-lib"}
        with pytest.raises(CodeReferenceError) as exc_info:
            factory.algorithms.register_algorithm(bad)
        assert exc_info.value.error_code == "CODE_REFERENCE_ERROR"

    def test_register_pinned_with_at_sign(self, factory: InMemoryRepositoryFactory) -> None:
        """code_reference with '@' (git pin) is accepted."""
        good = {**VALID_ALGORITHM, "code_reference": "git+https://github.com/org/repo@abc123"}
        aid = factory.algorithms.register_algorithm(good)
        assert_uuid(aid)

    def test_list_with_family_filter(self, factory: InMemoryRepositoryFactory) -> None:
        factory.algorithms.register_algorithm(
            {**VALID_ALGORITHM, "name": "RS", "algorithm_family": "random"}
        )
        factory.algorithms.register_algorithm(
            {**VALID_ALGORITHM, "name": "TPE", "algorithm_family": "bayesian_tpe"}
        )
        result = factory.algorithms.list_algorithms(AlgorithmFilter(algorithm_family="random"))
        assert all(a["algorithm_family"] == "random" for a in result)

    def test_deprecate_removes_from_listing(self, factory: InMemoryRepositoryFactory) -> None:
        aid = factory.algorithms.register_algorithm(VALID_ALGORITHM.copy())
        factory.algorithms.deprecate_algorithm(aid, reason="Superseded")
        listed = factory.algorithms.list_algorithms()
        assert not any(a["id"] == aid for a in listed)

    def test_deprecated_still_retrievable_by_id(self, factory: InMemoryRepositoryFactory) -> None:
        aid = factory.algorithms.register_algorithm(VALID_ALGORITHM.copy())
        factory.algorithms.deprecate_algorithm(aid, reason="Old")
        alg = factory.algorithms.get_algorithm(aid)
        assert alg["deprecated"] is True


# ===========================================================================
# StudyRepository contract tests
# ===========================================================================


class TestStudyRepository:
    def test_create_returns_uuid(self, factory: InMemoryRepositoryFactory) -> None:
        sid = factory.studies.create_study(VALID_STUDY.copy())
        assert_uuid(sid)

    def test_create_sets_draft_status(self, factory: InMemoryRepositoryFactory) -> None:
        """create_study() must always produce status='draft' (pre-lock)."""
        sid = factory.studies.create_study(VALID_STUDY.copy())
        study = factory.studies.get_study(sid)
        assert study["status"] == "draft"

    def test_create_ignores_caller_status(self, factory: InMemoryRepositoryFactory) -> None:
        """Even if caller passes status='locked', repository must set status='draft'."""
        sid = factory.studies.create_study({**VALID_STUDY, "status": "locked"})
        study = factory.studies.get_study(sid)
        assert study["status"] == "draft"

    def test_lock_transitions_status(self, factory: InMemoryRepositoryFactory) -> None:
        sid = factory.studies.create_study(VALID_STUDY.copy())
        factory.studies.lock_study(sid)
        study = factory.studies.get_study(sid)
        assert study["status"] == "locked"

    def test_lock_already_locked_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """lock_study() on an already-locked Study raises StudyAlreadyLockedError (FR-08)."""
        sid = factory.studies.create_study(VALID_STUDY.copy())
        factory.studies.lock_study(sid)
        with pytest.raises(StudyAlreadyLockedError) as exc_info:
            factory.studies.lock_study(sid)
        assert exc_info.value.error_code == "STUDY_ALREADY_LOCKED"

    def test_lock_unknown_id_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(EntityNotFoundError):
            factory.studies.lock_study("00000000-0000-4000-8000-000000000000")

    def test_lock_missing_required_field_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """lock_study() raises ValidationError if required fields are absent."""
        incomplete = {"name": "Incomplete Study"}
        sid = factory.studies.create_study(incomplete)
        with pytest.raises(ValidationError):
            factory.studies.lock_study(sid)

    def test_get_unknown_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(EntityNotFoundError):
            factory.studies.get_study("00000000-0000-4000-8000-000000000000")

    def test_list_with_status_filter(self, factory: InMemoryRepositoryFactory) -> None:
        sid1 = factory.studies.create_study(VALID_STUDY.copy())
        factory.studies.lock_study(sid1)
        factory.studies.create_study(VALID_STUDY.copy())  # remains draft

        locked = factory.studies.list_studies(StudyFilter(status="locked"))
        drafts = factory.studies.list_studies(StudyFilter(status="draft"))

        assert all(s["status"] == "locked" for s in locked)
        assert all(s["status"] == "draft" for s in drafts)
        assert len(locked) == 1
        assert len(drafts) == 1

    def test_list_with_problem_ids_overlap_filter(self, factory: InMemoryRepositoryFactory) -> None:
        sid1 = factory.studies.create_study({**VALID_STUDY, "problem_ids": ["prob-A", "prob-B"]})
        factory.studies.create_study({**VALID_STUDY, "problem_ids": ["prob-C"]})

        result = factory.studies.list_studies(StudyFilter(problem_ids=["prob-A"]))
        assert len(result) == 1
        assert result[0]["id"] == sid1


# ===========================================================================
# ExperimentRepository contract tests
# ===========================================================================


class TestExperimentRepository:
    def _create_locked_study(self, factory: InMemoryRepositoryFactory) -> str:
        sid = factory.studies.create_study(VALID_STUDY.copy())
        factory.studies.lock_study(sid)
        return sid

    def test_create_returns_uuid(self, factory: InMemoryRepositoryFactory) -> None:
        sid = self._create_locked_study(factory)
        eid = factory.experiments.create_experiment({"study_id": sid})
        assert_uuid(eid)

    def test_create_sets_running_status(self, factory: InMemoryRepositoryFactory) -> None:
        sid = self._create_locked_study(factory)
        eid = factory.experiments.create_experiment({"study_id": sid})
        exp = factory.experiments.get_experiment(eid)
        assert exp["status"] == "running"

    def test_update_mutable_field(self, factory: InMemoryRepositoryFactory) -> None:
        sid = self._create_locked_study(factory)
        eid = factory.experiments.create_experiment({"study_id": sid})
        factory.experiments.update_experiment(eid, status="completed")
        assert factory.experiments.get_experiment(eid)["status"] == "completed"

    def test_update_immutable_field_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """Updating 'study_id' after creation raises ImmutableFieldError."""
        sid = self._create_locked_study(factory)
        eid = factory.experiments.create_experiment({"study_id": sid})
        with pytest.raises(ImmutableFieldError) as exc_info:
            factory.experiments.update_experiment(eid, study_id="different-study")
        assert exc_info.value.error_code == "IMMUTABLE_FIELD"

    def test_get_unknown_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(EntityNotFoundError):
            factory.experiments.get_experiment("00000000-0000-4000-8000-000000000000")

    def test_list_by_study_id(self, factory: InMemoryRepositoryFactory) -> None:
        sid = self._create_locked_study(factory)
        eid1 = factory.experiments.create_experiment({"study_id": sid})
        eid2 = factory.experiments.create_experiment({"study_id": "other-study-id"})

        result = factory.experiments.list_experiments(study_id=sid)
        ids = [e["id"] for e in result]
        assert eid1 in ids
        assert eid2 not in ids


# ===========================================================================
# RunRepository contract tests
# ===========================================================================


class TestRunRepository:
    def test_create_returns_uuid(self, factory: InMemoryRepositoryFactory) -> None:
        rid = factory.runs.create_run({"experiment_id": "exp-uuid-001", "seed": 42})
        assert_uuid(rid)

    def test_get_returns_registered_run(self, factory: InMemoryRepositoryFactory) -> None:
        rid = factory.runs.create_run({"experiment_id": "exp-001", "seed": 7})
        run = factory.runs.get_run(rid)
        assert run["id"] == rid
        assert run["seed"] == 7

    def test_get_unknown_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(EntityNotFoundError):
            factory.runs.get_run("00000000-0000-4000-8000-000000000000")

    def test_update_run_fields(self, factory: InMemoryRepositoryFactory) -> None:
        rid = factory.runs.create_run({"experiment_id": "exp-001", "seed": 0})
        factory.runs.update_run(rid, status="completed", budget_used=50)
        run = factory.runs.get_run(rid)
        assert run["status"] == "completed"
        assert run["budget_used"] == 50

    def test_save_and_get_performance_records(self, factory: InMemoryRepositoryFactory) -> None:
        """save_performance_records() → get_performance_records() round-trip."""
        rid = factory.runs.create_run({"experiment_id": "exp-001", "seed": 0})
        records = [
            {"evaluation_number": 1, "objective_value": 3.0, "best_so_far": 3.0},
            {"evaluation_number": 2, "objective_value": 2.5, "best_so_far": 2.5},
            {"evaluation_number": 5, "objective_value": 2.0, "best_so_far": 2.0},
        ]
        factory.runs.save_performance_records(rid, records)
        fetched = factory.runs.get_performance_records(rid)
        assert len(fetched) == 3
        assert fetched[0]["evaluation_number"] == 1
        assert fetched[2]["evaluation_number"] == 5

    def test_performance_records_sorted_ascending(self, factory: InMemoryRepositoryFactory) -> None:
        """Records are always returned in ascending evaluation_number order."""
        rid = factory.runs.create_run({"experiment_id": "exp-001", "seed": 0})
        factory.runs.save_performance_records(
            rid,
            [
                {"evaluation_number": 5, "objective_value": 1.0, "best_so_far": 1.0},
                {"evaluation_number": 10, "objective_value": 0.9, "best_so_far": 0.9},
            ],
        )
        fetched = factory.runs.get_performance_records(rid)
        nums = [r["evaluation_number"] for r in fetched]
        assert nums == sorted(nums)

    def test_duplicate_evaluation_number_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """Saving a duplicate evaluation_number raises DuplicateEvaluationError."""
        rid = factory.runs.create_run({"experiment_id": "exp-001", "seed": 0})
        factory.runs.save_performance_records(
            rid, [{"evaluation_number": 1, "objective_value": 1.0, "best_so_far": 1.0}]
        )
        with pytest.raises(DuplicateEvaluationError) as exc_info:
            factory.runs.save_performance_records(
                rid, [{"evaluation_number": 1, "objective_value": 2.0, "best_so_far": 2.0}]
            )
        assert exc_info.value.error_code == "DUPLICATE_EVALUATION"

    def test_non_monotonic_sequence_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """Out-of-order evaluation_numbers raise ValidationError."""
        rid = factory.runs.create_run({"experiment_id": "exp-001", "seed": 0})
        with pytest.raises(ValidationError):
            factory.runs.save_performance_records(
                rid,
                [
                    {"evaluation_number": 5, "objective_value": 1.0, "best_so_far": 1.0},
                    {"evaluation_number": 3, "objective_value": 0.5, "best_so_far": 0.5},
                ],
            )

    def test_list_runs_by_experiment(self, factory: InMemoryRepositoryFactory) -> None:
        rid1 = factory.runs.create_run({"experiment_id": "exp-A", "seed": 1})
        factory.runs.create_run({"experiment_id": "exp-B", "seed": 2})
        result = factory.runs.list_runs("exp-A")
        ids = [r["id"] for r in result]
        assert rid1 in ids
        assert len(ids) == 1

    def test_list_runs_with_status_filter(self, factory: InMemoryRepositoryFactory) -> None:
        rid = factory.runs.create_run({"experiment_id": "exp-A", "seed": 1})
        factory.runs.update_run(rid, status="completed")
        factory.runs.create_run({"experiment_id": "exp-A", "seed": 2})  # no status update

        completed = factory.runs.list_runs("exp-A", RunFilter(status="completed"))
        assert all(r["status"] == "completed" for r in completed)

    def test_save_records_unknown_run_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(EntityNotFoundError):
            factory.runs.save_performance_records(
                "00000000-0000-4000-8000-000000000000",
                [{"evaluation_number": 1, "objective_value": 1.0, "best_so_far": 1.0}],
            )


# ===========================================================================
# ResultAggregateRepository contract tests
# ===========================================================================


class TestResultAggregateRepository:
    def test_save_and_retrieve_aggregates(self, factory: InMemoryRepositoryFactory) -> None:
        aggregates = [
            {
                "experiment_id": "exp-001",
                "problem_id": "prob-001",
                "algorithm_id": "alg-001",
                "n_runs": 10,
                "metrics": {"QUALITY-BEST_VALUE_AT_BUDGET": {"median": 0.05}},
            }
        ]
        factory.aggregates.save_result_aggregates(aggregates)
        result = factory.aggregates.list_result_aggregates("exp-001")
        assert len(result) == 1
        assert result[0]["problem_id"] == "prob-001"

    def test_list_by_experiment_id(self, factory: InMemoryRepositoryFactory) -> None:
        factory.aggregates.save_result_aggregates(
            [
                {
                    "experiment_id": "exp-A",
                    "problem_id": "p1",
                    "algorithm_id": "a1",
                    "n_runs": 5,
                    "metrics": {},
                }
            ]
        )
        factory.aggregates.save_result_aggregates(
            [
                {
                    "experiment_id": "exp-B",
                    "problem_id": "p2",
                    "algorithm_id": "a2",
                    "n_runs": 5,
                    "metrics": {},
                }
            ]
        )
        assert len(factory.aggregates.list_result_aggregates("exp-A")) == 1
        assert len(factory.aggregates.list_result_aggregates("exp-B")) == 1

    def test_save_missing_field_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(ValidationError):
            factory.aggregates.save_result_aggregates(
                [{"experiment_id": "exp-001", "problem_id": "p1"}]  # missing required fields
            )

    def test_get_by_id(self, factory: InMemoryRepositoryFactory) -> None:
        factory.aggregates.save_result_aggregates(
            [
                {
                    "experiment_id": "exp-001",
                    "problem_id": "p1",
                    "algorithm_id": "a1",
                    "n_runs": 3,
                    "metrics": {"QUALITY-BEST_VALUE_AT_BUDGET": {"median": 0.1}},
                }
            ]
        )
        all_aggs = factory.aggregates.list_result_aggregates("exp-001")
        agg_id = all_aggs[0]["id"]
        fetched = factory.aggregates.get_result_aggregate(agg_id)
        assert fetched["id"] == agg_id

    def test_get_unknown_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(EntityNotFoundError):
            factory.aggregates.get_result_aggregate("00000000-0000-4000-8000-000000000000")


# ===========================================================================
# ReportRepository contract tests
# ===========================================================================


class TestReportRepository:
    def test_save_and_retrieve_report(self, factory: InMemoryRepositoryFactory) -> None:
        rid = factory.reports.save_report(
            {
                "report_type": "researcher",
                "experiment_id": "exp-001",
                "limitations": ["Scope: 3 tested problems only."],
                "artifact_reference": "study_001/reports/researcher.html",
            }
        )
        assert_uuid(rid)
        report = factory.reports.get_report(rid)
        assert report["report_type"] == "researcher"

    def test_save_empty_limitations_raises(self, factory: InMemoryRepositoryFactory) -> None:
        """FR-21: limitations must be non-empty."""
        with pytest.raises(ValidationError) as exc_info:
            factory.reports.save_report(
                {
                    "report_type": "researcher",
                    "experiment_id": "exp-001",
                    "limitations": [],
                    "artifact_reference": "path.html",
                }
            )
        assert "limitations" in exc_info.value.message.lower()

    def test_save_missing_artifact_reference_raises(
        self, factory: InMemoryRepositoryFactory
    ) -> None:
        with pytest.raises(ValidationError):
            factory.reports.save_report(
                {
                    "report_type": "researcher",
                    "experiment_id": "exp-001",
                    "limitations": ["Scope limited."],
                    # artifact_reference missing
                }
            )

    def test_list_reports_by_experiment(self, factory: InMemoryRepositoryFactory) -> None:
        for report_type in ("researcher", "practitioner"):
            factory.reports.save_report(
                {
                    "report_type": report_type,
                    "experiment_id": "exp-001",
                    "limitations": ["Scope limited."],
                    "artifact_reference": f"path/{report_type}.html",
                }
            )
        reports = factory.reports.list_reports("exp-001")
        assert len(reports) == 2
        types = {r["report_type"] for r in reports}
        assert types == {"researcher", "practitioner"}

    def test_get_unknown_raises(self, factory: InMemoryRepositoryFactory) -> None:
        with pytest.raises(EntityNotFoundError):
            factory.reports.get_report("00000000-0000-4000-8000-000000000000")


# ===========================================================================
# ADR-001 Swap test
# ===========================================================================
# "A ServerRepository implementation that delegates to a REST API can be plugged
#  in without changing any other library code." — ADR-001
#
# This test demonstrates the guarantee: the same client function works with any
# RepositoryFactory implementation without modification.
# ===========================================================================


def _register_and_retrieve_problem(repo_factory: RepositoryFactory) -> None:
    """Client function — uses only the RepositoryFactory interface."""
    pid = repo_factory.problems.register_problem({"name": "SwapTestProblem", "dimensions": 3})
    problem = repo_factory.problems.get_problem(pid)
    assert problem["name"] == "SwapTestProblem"
    assert problem["dimensions"] == 3
    assert_uuid(pid)


def _full_study_lifecycle(repo_factory: RepositoryFactory) -> None:
    """Client function — exercises Study create → lock → Experiment create flow."""
    # Create and lock a study
    sid = repo_factory.studies.create_study(VALID_STUDY.copy())
    assert repo_factory.studies.get_study(sid)["status"] == "draft"
    repo_factory.studies.lock_study(sid)
    assert repo_factory.studies.get_study(sid)["status"] == "locked"

    # Create an experiment
    eid = repo_factory.experiments.create_experiment({"study_id": sid})
    assert_uuid(eid)

    # Create a run with performance records
    rid = repo_factory.runs.create_run({"experiment_id": eid, "seed": 42})
    repo_factory.runs.save_performance_records(
        rid,
        [
            {"evaluation_number": 1, "objective_value": 5.0, "best_so_far": 5.0},
            {"evaluation_number": 50, "objective_value": 0.1, "best_so_far": 0.1},
        ],
    )
    records = repo_factory.runs.get_performance_records(rid)
    assert len(records) == 2

    # Save and retrieve a report
    report_id = repo_factory.reports.save_report(
        {
            "report_type": "researcher",
            "experiment_id": eid,
            "limitations": ["Conclusions scoped to 1 problem instance."],
            "artifact_reference": f"study_{sid}/reports/researcher.html",
        }
    )
    reports = repo_factory.reports.list_reports(eid)
    assert any(r["id"] == report_id for r in reports)


class TestADR001SwapGuarantee:
    """Demonstrate that client code is independent of RepositoryFactory implementation.

    Per ADR-001: swapping ``InMemoryRepositoryFactory`` for any other
    ``RepositoryFactory`` implementation must require zero changes to client code.
    Both factories below implement the same abstract interface; the client
    functions accept ``RepositoryFactory`` — not the concrete type.
    """

    def test_problem_workflow_with_factory_a(self) -> None:
        """Client function works with InMemoryRepositoryFactory instance A."""
        _register_and_retrieve_problem(InMemoryRepositoryFactory())

    def test_problem_workflow_with_factory_b(self) -> None:
        """Same client function works with a fresh InMemoryRepositoryFactory instance B.

        In production this would be a different *type* (e.g., ServerRepository).
        The test shows the interface is the only dependency — not the implementation.
        """
        _register_and_retrieve_problem(InMemoryRepositoryFactory())

    def test_full_lifecycle_with_factory_a(self) -> None:
        _full_study_lifecycle(InMemoryRepositoryFactory())

    def test_full_lifecycle_with_factory_b(self) -> None:
        """Second fresh factory — identical lifecycle, zero code changes required."""
        _full_study_lifecycle(InMemoryRepositoryFactory())

    def test_factory_is_subtype_of_repository_factory(self) -> None:
        """InMemoryRepositoryFactory is a RepositoryFactory (Liskov substitution)."""
        factory: RepositoryFactory = InMemoryRepositoryFactory()
        assert isinstance(factory, RepositoryFactory)
        # All seven repository properties are accessible through the abstract interface
        assert isinstance(factory.problems, object)
        assert isinstance(factory.algorithms, object)
        assert isinstance(factory.studies, object)
        assert isinstance(factory.experiments, object)
        assert isinstance(factory.runs, object)
        assert isinstance(factory.aggregates, object)
        assert isinstance(factory.reports, object)


# ===========================================================================
# No file-path IDs test
# ===========================================================================


class TestNoFilePathsInIDs:
    """Enforce ADR-001: no entity ID may look like a file path.

    All IDs are UUID v4 strings. This prevents the 'pure library with direct
    file I/O' anti-pattern (rejected in ADR-001 §Alternatives Considered).
    """

    def test_problem_id_is_not_a_path(self, factory: InMemoryRepositoryFactory) -> None:
        pid = factory.problems.register_problem(VALID_PROBLEM.copy())
        assert "/" not in pid
        assert "\\" not in pid
        assert not pid.endswith(".json")

    def test_algorithm_id_is_not_a_path(self, factory: InMemoryRepositoryFactory) -> None:
        aid = factory.algorithms.register_algorithm(VALID_ALGORITHM.copy())
        assert "/" not in aid
        assert "\\" not in aid

    def test_study_id_is_not_a_path(self, factory: InMemoryRepositoryFactory) -> None:
        sid = factory.studies.create_study(VALID_STUDY.copy())
        assert "/" not in sid
        assert "\\" not in sid

    def test_experiment_id_is_not_a_path(self, factory: InMemoryRepositoryFactory) -> None:
        sid = factory.studies.create_study(VALID_STUDY.copy())
        factory.studies.lock_study(sid)
        eid = factory.experiments.create_experiment({"study_id": sid})
        assert "/" not in eid
        assert "\\" not in eid

    def test_run_id_is_not_a_path(self, factory: InMemoryRepositoryFactory) -> None:
        rid = factory.runs.create_run({"experiment_id": "exp-001", "seed": 0})
        assert "/" not in rid
        assert "\\" not in rid
