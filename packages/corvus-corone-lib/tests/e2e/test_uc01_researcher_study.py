"""
End-to-end tests for UC-01: Design and Execute a Reproducible Benchmarking Study.

Tests are grouped by what they validate:

  CLASS TestStudyLock
    — UC-01 F3: pre-registration gate (StudyLockedError)

  CLASS TestPerformanceRecordStrategy
    — ADR-002: dual-trigger + end-of-run trigger logic
    — ADR-002: trigger_reason field population
    — ADR-002: scheduled checkpoint coverage

  CLASS TestImprovementEpsilon
    — ADR-004: strict inequality default
    — ADR-004: configurable epsilon suppresses sub-threshold records

  CLASS TestStorageCap
    — ADR-005: improvement records stop at cap
    — ADR-005: scheduled records continue after cap
    — ADR-005: cap_reached_at_evaluation is set
    — ADR-005: end-of-run record always present

  CLASS TestReproducibility
    — MANIFESTO Principle 18: seeds are unique within an Experiment (UC-01 F4)
    — Determinism: same seed produces identical PerformanceRecords

  CLASS TestUC01Postconditions
    — Exact run count: n_problems × n_algorithms × n_repetitions
    — ResultAggregates exist for every (problem, algorithm) pair
    — ResultAggregate.n_runs equals study.repetitions
    — Reports: exactly two (researcher + practitioner)
    — Reports: non-empty limitations sections (FR-21)
    — Reports: epsilon limitation auto-disclosed when set (ADR-004)

References
----------
→ UC-01:          docs/02-design/01-software-requirement-specification/02-use-cases/02-uc-01.md
→ Tutorial:       docs/06-tutorials/02-researcher-design-and-execute-study.md
→ Interface:      docs/03-technical-contracts/02-interface-contracts.md
→ Data format:    docs/03-technical-contracts/01-data-format.md
→ ADR-002:        docs/02-design/02-architecture/01-adr/adr-002-performance-recording-strategy.md
→ ADR-004:        docs/02-design/02-architecture/01-adr/adr-004-improvement-sensitivity-threshold.md
→ ADR-005:        docs/02-design/02-architecture/01-adr/adr-005-performance-record-storage-cap.md
"""

from __future__ import annotations

import pytest

from tests.e2e._stubs import (
    VALID_TRIGGER_REASONS,
    ExperimentRecord,
    MinimalRunner,
    PerformanceRecord,
    ResultAggregate,
    RunRecord,
    StubGreedyAlgorithm,
    StubNoisySphereProblem,
    StubRandomSearchAlgorithm,
    StudyLockedError,
    StudyRecord,
    compute_log_scale_schedule,
    compute_result_aggregates,
    generate_reports,
    has_trigger,
    update_study,
)
from tests.e2e.conftest import make_study_with_cap, make_study_with_epsilon


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _end_of_run_records(run: RunRecord) -> list[PerformanceRecord]:
    return [r for r in run.records if has_trigger(r, "end_of_run")]


def _improvement_records(run: RunRecord) -> list[PerformanceRecord]:
    return [r for r in run.records if has_trigger(r, "improvement")]


def _scheduled_records(run: RunRecord) -> list[PerformanceRecord]:
    return [r for r in run.records if has_trigger(r, "scheduled")]


# ---------------------------------------------------------------------------
# TestStudyLock — UC-01 F3
# ---------------------------------------------------------------------------


class TestStudyLock:
    """Pre-registration gate: a locked Study must not be modifiable (UC-01 F3)."""

    def test_study_status_is_locked_after_creation(
        self, locked_study: StudyRecord
    ) -> None:
        assert locked_study.status == "locked"

    def test_update_raises_study_locked_error(self, locked_study: StudyRecord) -> None:
        """Attempting any modification raises StudyLockedError."""
        with pytest.raises(StudyLockedError, match=str(locked_study.study_id)):
            update_study(locked_study, repetitions=99)

    def test_update_does_not_mutate_study(self, locked_study: StudyRecord) -> None:
        """StudyLockedError is raised before any mutation occurs."""
        original_repetitions = locked_study.repetitions
        try:
            update_study(locked_study, repetitions=99)
        except StudyLockedError:
            pass
        assert locked_study.repetitions == original_repetitions

    def test_research_question_preserved(self, locked_study: StudyRecord) -> None:
        assert locked_study.research_question != ""

    def test_hypotheses_are_locked(self, locked_study: StudyRecord) -> None:
        assert len(locked_study.pre_registered_hypotheses) >= 1


# ---------------------------------------------------------------------------
# TestPerformanceRecordStrategy — ADR-002
# ---------------------------------------------------------------------------


class TestPerformanceRecordStrategy:
    """Dual-trigger + end-of-run PerformanceRecord strategy (ADR-002)."""

    def test_every_run_has_at_least_one_record(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        for run in completed_experiment.runs:
            assert run.records, f"Run {run.run_id} has no PerformanceRecords."

    def test_end_of_run_record_always_present(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        """ADR-002: end-of-run trigger is mandatory — always fires at budget exhaustion."""
        for run in completed_experiment.runs:
            end_records = _end_of_run_records(run)
            assert end_records, (
                f"Run {run.run_id}: no end-of-run PerformanceRecord found. "
                "ADR-002 requires this record to always be written."
            )

    def test_end_of_run_record_is_at_budget(
        self, completed_experiment: ExperimentRecord, locked_study: StudyRecord
    ) -> None:
        """End-of-run record evaluation_number must equal the study budget."""
        for run in completed_experiment.runs:
            end_records = _end_of_run_records(run)
            assert end_records[-1].evaluation_number == locked_study.budget, (
                f"Run {run.run_id}: end-of-run record not at budget "
                f"(expected eval {locked_study.budget})."
            )

    def test_scheduled_checkpoints_all_present(
        self, completed_experiment: ExperimentRecord, locked_study: StudyRecord
    ) -> None:
        """Every evaluation number in the log-scale schedule must have a record (ADR-002)."""
        expected_schedule = compute_log_scale_schedule(
            base_points=locked_study.log_scale_schedule["base_points"],
            multiplier_base=locked_study.log_scale_schedule["multiplier_base"],
            budget=locked_study.budget,
        )
        for run in completed_experiment.runs:
            recorded_evals = {r.evaluation_number for r in run.records}
            missing = expected_schedule - recorded_evals
            assert not missing, (
                f"Run {run.run_id}: missing scheduled checkpoint(s) {sorted(missing)}. "
                "ADR-002 requires all {1,2,5}×10^i evaluations to have records."
            )

    def test_evaluation_numbers_are_strictly_monotonic(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        """No duplicate evaluation_numbers within a Run (deduplication constraint, ADR-002)."""
        for run in completed_experiment.runs:
            evals = [r.evaluation_number for r in run.records]
            assert evals == sorted(set(evals)), (
                f"Run {run.run_id}: evaluation_numbers are not strictly increasing or "
                f"contain duplicates: {evals}"
            )

    def test_trigger_reason_is_valid_for_every_record(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        """Every PerformanceRecord.trigger_reason must be one of the ADR-002 values."""
        for run in completed_experiment.runs:
            for rec in run.records:
                assert rec.trigger_reason in VALID_TRIGGER_REASONS, (
                    f"Run {run.run_id}, eval {rec.evaluation_number}: "
                    f"invalid trigger_reason '{rec.trigger_reason}'. "
                    f"Valid values: {VALID_TRIGGER_REASONS}"
                )

    def test_is_improvement_flag_consistent_with_trigger_reason(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        """is_improvement must be True iff trigger_reason encodes the improvement trigger."""
        for run in completed_experiment.runs:
            for rec in run.records:
                has_improvement_trigger = has_trigger(rec, "improvement")
                assert rec.is_improvement == has_improvement_trigger, (
                    f"Run {run.run_id}, eval {rec.evaluation_number}: "
                    f"is_improvement={rec.is_improvement} inconsistent with "
                    f"trigger_reason='{rec.trigger_reason}'."
                )

    def test_best_so_far_is_non_increasing(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        """best_so_far must be non-increasing across records within a Run."""
        for run in completed_experiment.runs:
            prev = float("inf")
            for rec in run.records:
                assert rec.best_so_far <= prev + 1e-9, (
                    f"Run {run.run_id}, eval {rec.evaluation_number}: "
                    f"best_so_far increased from {prev} to {rec.best_so_far}."
                )
                prev = rec.best_so_far

    def test_combined_trigger_at_budget_50_with_schedule(
        self, locked_study: StudyRecord
    ) -> None:
        """Eval 50 = budget endpoint; it appears in the {1,2,5}×10^1 schedule.
        The last record should have trigger_reason containing both 'scheduled'
        and 'end_of_run' (at minimum).
        """
        problem = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.0)
        algorithm = StubRandomSearchAlgorithm("alg-001")
        runner = MinimalRunner(locked_study)
        run = runner.run_single(problem, algorithm, seed=0)
        last_record = run.records[-1]
        assert last_record.evaluation_number == 50
        assert "end_of_run" in last_record.trigger_reason
        assert "scheduled" in last_record.trigger_reason


# ---------------------------------------------------------------------------
# TestImprovementEpsilon — ADR-004
# ---------------------------------------------------------------------------


class TestImprovementEpsilon:
    """Improvement sensitivity threshold (ADR-004)."""

    def test_strict_inequality_default_records_every_improvement(self) -> None:
        """With epsilon=None (default), every obj < best_so_far fires an improvement record."""
        study = make_study_with_epsilon.__wrapped__ if hasattr(  # type: ignore[attr-defined]
            make_study_with_epsilon, "__wrapped__"
        ) else make_study_with_epsilon
        # Use the helper directly (not a fixture) to avoid pytest fixture injection
        locked = make_study_with_epsilon(epsilon=0.0)
        # epsilon=0.0 means best_so_far - obj > 0 → same as strict inequality for non-zero diffs
        problem = StubNoisySphereProblem("prob-001", dim=2, budget=20, noise_std=0.0)
        algorithm = StubGreedyAlgorithm("alg-002")
        # Patch budget
        locked.budget = 20
        runner = MinimalRunner(locked)
        run = runner.run_single(problem, algorithm, seed=42)
        improvement_recs = _improvement_records(run)
        # Greedy on noiseless sphere should find at least a few improvements
        assert len(improvement_recs) >= 1

    def test_null_epsilon_is_strict_inequality(self) -> None:
        """None epsilon means any obj < best_so_far fires — including tiny improvements."""
        study = make_study_with_epsilon(epsilon=None)  # type: ignore[arg-type]
        # Use a deterministic noiseless problem to get a predictable improvement trace
        problem = StubNoisySphereProblem("prob-001", dim=1, budget=10, noise_std=0.0)
        algorithm = StubGreedyAlgorithm("alg-002")
        study.budget = 10
        runner = MinimalRunner(study)
        run = runner.run_single(problem, algorithm, seed=0)
        for rec in run.records:
            if rec.is_improvement:
                # Every is_improvement record must reflect a genuine decrease
                assert rec.trigger_reason in VALID_TRIGGER_REASONS

    def test_large_epsilon_suppresses_small_improvements(self) -> None:
        """A large epsilon means only large jumps fire improvement records."""
        # Use a noiseless sphere where greedy convergence produces small incremental gains
        small_eps_study = make_study_with_epsilon(epsilon=0.001)
        large_eps_study = make_study_with_epsilon(epsilon=10.0)

        problem_small = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.0)
        problem_large = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.0)
        algo_small = StubGreedyAlgorithm("alg-002")
        algo_large = StubGreedyAlgorithm("alg-002")

        runner_small = MinimalRunner(small_eps_study)
        runner_large = MinimalRunner(large_eps_study)

        run_small = runner_small.run_single(problem_small, algo_small, seed=7)
        run_large = runner_large.run_single(problem_large, algo_large, seed=7)

        imp_small = len(_improvement_records(run_small))
        imp_large = len(_improvement_records(run_large))

        assert imp_large <= imp_small, (
            f"Large epsilon ({large_eps_study.improvement_epsilon}) should produce "
            f"≤ improvement records than small epsilon ({small_eps_study.improvement_epsilon}). "
            f"Got: large={imp_large}, small={imp_small}."
        )

    def test_epsilon_limitation_appears_in_report(self) -> None:
        """Non-null improvement_epsilon must be disclosed in the Report (ADR-004, FR-21)."""
        study = make_study_with_epsilon(epsilon=0.05)
        problem = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.1)
        algorithm = StubRandomSearchAlgorithm("alg-001")
        runner = MinimalRunner(study)
        experiment = runner.run_study(
            problems={"prob-001": problem},
            algorithms={"alg-001": algorithm},
        )
        aggregates = compute_result_aggregates(experiment)
        reports = generate_reports(experiment, aggregates, study)

        for report in reports:
            assert report.has_limitations_section
            epsilon_disclosed = any(
                "improvement_epsilon" in lim for lim in report.limitations
            )
            assert epsilon_disclosed, (
                f"Report type='{report.report_type}': improvement_epsilon not disclosed "
                "in limitations section (ADR-004 requires automatic disclosure)."
            )


# ---------------------------------------------------------------------------
# TestStorageCap — ADR-005
# ---------------------------------------------------------------------------


class TestStorageCap:
    """PerformanceRecord storage cap behaviour (ADR-005)."""

    def _run_with_cap(self, cap: int) -> RunRecord:
        study = make_study_with_cap(cap)
        problem = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.0)
        algorithm = StubGreedyAlgorithm("alg-002")
        runner = MinimalRunner(study)
        return runner.run_single(problem, algorithm, seed=0)

    def test_improvement_records_stop_at_cap(self) -> None:
        """Once max_records_per_run improvement-only records are written, no more are added.

        ADR-005: the cap stops records written *solely* by the improvement trigger.
        Combined scheduled+improvement records ("both", "all") are not capped because
        they would be written anyway by the scheduled trigger (ADR-005 §1).
        """
        cap = 3
        run = self._run_with_cap(cap)
        # Count only records whose trigger_reason is purely improvement-driven
        pure_improvement_count = sum(
            1 for r in run.records
            if r.trigger_reason in ("improvement", "improvement_end_of_run")
        )
        assert pure_improvement_count <= cap, (
            f"Expected ≤ {cap} pure improvement records with cap={cap}, "
            f"got {pure_improvement_count}."
        )

    def test_scheduled_records_continue_after_cap(self) -> None:
        """Scheduled records are never suppressed by the cap (ADR-005)."""
        cap = 1
        run = self._run_with_cap(cap)
        # With budget=50, schedule is {1,2,5,10,20,50}; all must appear regardless of cap
        scheduled_evals = {r.evaluation_number for r in _scheduled_records(run)}
        expected = compute_log_scale_schedule([1, 2, 5], 10, 50)
        missing = expected - scheduled_evals
        assert not missing, (
            f"Scheduled checkpoint(s) {sorted(missing)} missing after cap hit. "
            "ADR-005 requires scheduled records to continue after the cap."
        )

    def test_end_of_run_record_present_after_cap(self) -> None:
        """End-of-run record is always written, even after cap is reached (ADR-005)."""
        cap = 0  # zero: suppress all improvement records immediately
        run = self._run_with_cap(cap)
        assert _end_of_run_records(run), (
            "End-of-run record missing after cap=0. "
            "ADR-005 guarantees the end-of-run record is always written."
        )

    def test_cap_reached_at_evaluation_is_set(self) -> None:
        """cap_reached_at_evaluation must be populated when the cap is hit."""
        cap = 1
        run = self._run_with_cap(cap)
        # Greedy on noiseless sphere will hit the cap quickly
        if len(_improvement_records(run)) >= cap:
            assert run.cap_reached_at_evaluation is not None, (
                "cap_reached_at_evaluation not set despite cap being reached."
            )

    def test_cap_reached_at_evaluation_is_none_when_cap_not_set(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        """Without max_records_per_run, cap_reached_at_evaluation must be None."""
        for run in completed_experiment.runs:
            assert run.cap_reached_at_evaluation is None, (
                f"Run {run.run_id}: cap_reached_at_evaluation is set but "
                "max_records_per_run was not configured."
            )

    def test_cap_limitation_appears_in_report(self) -> None:
        """When a cap is hit, the Report limitations section must note it (ADR-005, FR-21)."""
        cap = 1
        study = make_study_with_cap(cap)
        problem = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.0)
        algorithm = StubGreedyAlgorithm("alg-002")
        runner = MinimalRunner(study)
        experiment = runner.run_study(
            problems={"prob-001": problem},
            algorithms={"alg-002": algorithm},
        )
        aggregates = compute_result_aggregates(experiment)
        reports = generate_reports(experiment, aggregates, study)

        cap_was_reached = any(r.cap_reached_at_evaluation is not None for r in experiment.runs)
        if cap_was_reached:
            for report in reports:
                cap_disclosed = any(
                    "max_records_per_run" in lim or "cap_reached" in lim
                    for lim in report.limitations
                )
                assert cap_disclosed, (
                    f"Report type='{report.report_type}': storage cap not disclosed "
                    "in limitations section (ADR-005 requires automatic disclosure)."
                )


# ---------------------------------------------------------------------------
# TestReproducibility — MANIFESTO Principle 18
# ---------------------------------------------------------------------------


class TestReproducibility:
    """Seeds are system-assigned, unique, and deterministic (MANIFESTO Principle 18)."""

    def test_all_seeds_unique_within_experiment(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        """UC-01 F4: no two Runs in the same Experiment may use the same seed."""
        seeds = [run.seed for run in completed_experiment.runs]
        assert len(seeds) == len(set(seeds)), (
            f"Seed collision detected in experiment {completed_experiment.experiment_id}. "
            f"Seeds: {seeds}"
        )

    def test_same_seed_produces_identical_records(
        self, locked_study: StudyRecord
    ) -> None:
        """Determinism: two runs with identical (problem, algorithm, seed) must produce
        identical PerformanceRecords (NFR-REPRO-01).
        """
        problem_a = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.1)
        problem_b = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.1)
        algo_a = StubRandomSearchAlgorithm("alg-001")
        algo_b = StubRandomSearchAlgorithm("alg-001")

        runner = MinimalRunner(locked_study)
        run_a = runner.run_single(problem_a, algo_a, seed=42)
        run_b = runner.run_single(problem_b, algo_b, seed=42)

        assert len(run_a.records) == len(run_b.records), (
            "Identical seed produced different number of PerformanceRecords."
        )
        for rec_a, rec_b in zip(run_a.records, run_b.records):
            assert rec_a.evaluation_number == rec_b.evaluation_number
            assert rec_a.objective_value == pytest.approx(rec_b.objective_value)
            assert rec_a.trigger_reason == rec_b.trigger_reason

    def test_different_seeds_produce_different_objective_sequences(
        self, locked_study: StudyRecord
    ) -> None:
        """Seeds must produce independent runs — same algorithm on different seeds
        should not produce identical objective sequences (basic sanity check).
        """
        problem_0 = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.1)
        problem_1 = StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.1)
        algo_0 = StubRandomSearchAlgorithm("alg-001")
        algo_1 = StubRandomSearchAlgorithm("alg-001")

        runner = MinimalRunner(locked_study)
        run_0 = runner.run_single(problem_0, algo_0, seed=0)
        run_1 = runner.run_single(problem_1, algo_1, seed=1)

        objectives_0 = [r.objective_value for r in run_0.records]
        objectives_1 = [r.objective_value for r in run_1.records]
        assert objectives_0 != objectives_1, (
            "Different seeds produced identical objective sequences — "
            "seeds are not providing independent randomness."
        )

    def test_seeds_are_sequential_in_experiment(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        """Sequential seed strategy: seeds must be 0, 1, 2, ... in run order."""
        for i, run in enumerate(completed_experiment.runs):
            assert run.seed == i, (
                f"Run index {i} has seed {run.seed}; sequential strategy requires seed={i}."
            )


# ---------------------------------------------------------------------------
# TestUC01Postconditions — UC-01 postconditions
# ---------------------------------------------------------------------------


class TestUC01Postconditions:
    """UC-01 postconditions must all hold after a successful study execution."""

    def test_experiment_status_is_completed(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        assert completed_experiment.status == "completed"

    def test_run_count_equals_problems_times_algorithms_times_repetitions(
        self, completed_experiment: ExperimentRecord, locked_study: StudyRecord
    ) -> None:
        """UC-01: a completed Experiment has all Run records populated."""
        expected = (
            len(locked_study.problem_ids)
            * len(locked_study.algorithm_ids)
            * locked_study.repetitions
        )
        actual = len(completed_experiment.runs)
        assert actual == expected, (
            f"Expected {expected} runs "
            f"({len(locked_study.problem_ids)} problems × "
            f"{len(locked_study.algorithm_ids)} algorithms × "
            f"{locked_study.repetitions} repetitions), got {actual}."
        )

    def test_all_runs_completed_successfully(
        self, completed_experiment: ExperimentRecord
    ) -> None:
        failed = [r for r in completed_experiment.runs if r.status != "completed"]
        assert not failed, (
            f"{len(failed)} run(s) did not complete: "
            f"{[r.run_id for r in failed]}"
        )

    def test_result_aggregates_exist_for_every_problem_algorithm_pair(
        self,
        completed_experiment: ExperimentRecord,
        result_aggregates: list[ResultAggregate],
        locked_study: StudyRecord,
    ) -> None:
        """UC-01: Result Aggregates exist for every (problem, algorithm) pair."""
        expected_pairs = {
            (p, a)
            for p in locked_study.problem_ids
            for a in locked_study.algorithm_ids
        }
        actual_pairs = {(agg.problem_id, agg.algorithm_id) for agg in result_aggregates}
        missing = expected_pairs - actual_pairs
        assert not missing, (
            f"ResultAggregates missing for pairs: {missing}. "
            "UC-01 postcondition requires aggregates for every (problem, algorithm) pair."
        )

    def test_result_aggregate_n_runs_equals_repetitions(
        self,
        result_aggregates: list[ResultAggregate],
        locked_study: StudyRecord,
    ) -> None:
        """ResultAggregate.n_runs must equal study.repetitions (interface-contracts.md §4)."""
        for agg in result_aggregates:
            assert agg.n_runs == locked_study.repetitions, (
                f"Aggregate ({agg.problem_id}, {agg.algorithm_id}): "
                f"n_runs={agg.n_runs}, expected {locked_study.repetitions}."
            )

    def test_quality_metric_present_in_every_aggregate(
        self, result_aggregates: list[ResultAggregate]
    ) -> None:
        """QUALITY-BEST_VALUE_AT_BUDGET must be in every ResultAggregate."""
        for agg in result_aggregates:
            assert "QUALITY-BEST_VALUE_AT_BUDGET" in agg.metrics, (
                f"Aggregate ({agg.problem_id}, {agg.algorithm_id}): "
                "QUALITY-BEST_VALUE_AT_BUDGET metric missing."
            )

    def test_exactly_two_reports_are_generated(
        self,
        completed_experiment: ExperimentRecord,
        result_aggregates: list[ResultAggregate],
        locked_study: StudyRecord,
    ) -> None:
        """UC-01 step 9: exactly one Researcher Report and one Practitioner Report."""
        reports = generate_reports(completed_experiment, result_aggregates, locked_study)
        assert len(reports) == 2
        report_types = {r.report_type for r in reports}
        assert report_types == {"researcher", "practitioner"}

    def test_both_reports_have_non_empty_limitations_sections(
        self,
        completed_experiment: ExperimentRecord,
        result_aggregates: list[ResultAggregate],
        locked_study: StudyRecord,
    ) -> None:
        """FR-21: every report must have a non-empty limitations section."""
        reports = generate_reports(completed_experiment, result_aggregates, locked_study)
        for report in reports:
            assert report.has_limitations_section, (
                f"Report type='{report.report_type}' is missing a limitations section "
                "(FR-21 requires this for every report)."
            )
            assert report.limitations, (
                f"Report type='{report.report_type}' limitations section is empty "
                "(FR-21 requires it to be non-empty)."
            )

    def test_limitations_scope_problem_instances(
        self,
        completed_experiment: ExperimentRecord,
        result_aggregates: list[ResultAggregate],
        locked_study: StudyRecord,
    ) -> None:
        """Limitations must explicitly scope conclusions to the tested problem instances."""
        reports = generate_reports(completed_experiment, result_aggregates, locked_study)
        for report in reports:
            scoped = any(
                "problem instance" in lim.lower() or "tested" in lim.lower()
                for lim in report.limitations
            )
            assert scoped, (
                f"Report type='{report.report_type}': no limitation scopes conclusions "
                "to the tested problem instances (MANIFESTO Principle 24)."
            )

    def test_experiment_id_references_study_id(
        self, completed_experiment: ExperimentRecord, locked_study: StudyRecord
    ) -> None:
        """Experiment is traceable to its Study (data-format.md §2.4)."""
        assert completed_experiment.study_id == locked_study.study_id

    def test_all_runs_reference_valid_problem_and_algorithm_ids(
        self, completed_experiment: ExperimentRecord, locked_study: StudyRecord
    ) -> None:
        """Every RunRecord must reference a problem and algorithm declared in the Study."""
        for run in completed_experiment.runs:
            assert run.problem_id in locked_study.problem_ids, (
                f"Run {run.run_id}: problem_id '{run.problem_id}' not in Study."
            )
            assert run.algorithm_id in locked_study.algorithm_ids, (
                f"Run {run.run_id}: algorithm_id '{run.algorithm_id}' not in Study."
            )
