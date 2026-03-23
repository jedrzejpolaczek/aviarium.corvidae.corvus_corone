"""
Pytest fixtures for UC-01 end-to-end tests.

All fixtures are function-scoped (default) — no shared mutable state between tests.
Stub implementations live in _stubs.py; this file only wires them into fixtures.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.e2e._stubs import (
    ExperimentRecord,
    MinimalRunner,
    ResultAggregate,
    StubGreedyAlgorithm,
    StubNoisySphereProblem,
    StubRandomSearchAlgorithm,
    StudyRecord,
    compute_result_aggregates,
    create_study,
    generate_reports,
)


# ---------------------------------------------------------------------------
# Problem fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sphere_2d() -> StubNoisySphereProblem:
    """2-D noisy sphere, budget=50, low noise."""
    return StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.05)


@pytest.fixture
def sphere_3d() -> StubNoisySphereProblem:
    """3-D noisy sphere, budget=50, moderate noise."""
    return StubNoisySphereProblem("prob-002", dim=3, budget=50, noise_std=0.1)


# ---------------------------------------------------------------------------
# Algorithm fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def random_search() -> StubRandomSearchAlgorithm:
    return StubRandomSearchAlgorithm("alg-001")


@pytest.fixture
def greedy_search() -> StubGreedyAlgorithm:
    return StubGreedyAlgorithm("alg-002")


# ---------------------------------------------------------------------------
# Study fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def locked_study() -> StudyRecord:
    """A fully locked StudyRecord for the canonical E2E scenario.

    2 problems × 2 algorithms × 5 repetitions = 20 runs total.
    Budget=50, sequential seeds, strict improvement (epsilon=None).
    """
    return create_study(
        name="Greedy vs RandomSearch on low-dim noisy sphere",
        research_question=(
            "Does greedy local search achieve lower QUALITY-BEST_VALUE_AT_BUDGET "
            "than random search within 50 evaluations on low-dimensional noisy sphere "
            "problems? Conclusions do not extend beyond the tested problem instances."
        ),
        problem_ids=["prob-001", "prob-002"],
        algorithm_ids=["alg-001", "alg-002"],
        repetitions=5,
        budget=50,
        seed_strategy="sequential",
        sampling_strategy="log_scale_plus_improvement",
        log_scale_schedule={"base_points": [1, 2, 5], "multiplier_base": 10},
        improvement_epsilon=None,
        pre_registered_hypotheses=[
            {
                "h0": (
                    "No significant difference in QUALITY-BEST_VALUE_AT_BUDGET "
                    "between StubGreedy and StubRandomSearch."
                ),
                "h1": "StubGreedy achieves lower QUALITY-BEST_VALUE_AT_BUDGET.",
                "test": "Wilcoxon signed-rank",
                "alpha": 0.05,
                "metrics": ["QUALITY-BEST_VALUE_AT_BUDGET"],
            }
        ],
    )


# ---------------------------------------------------------------------------
# Experiment fixture — runs the full study
# ---------------------------------------------------------------------------


@pytest.fixture
def completed_experiment(
    locked_study: StudyRecord,
    sphere_2d: StubNoisySphereProblem,
    sphere_3d: StubNoisySphereProblem,
    random_search: StubRandomSearchAlgorithm,
    greedy_search: StubGreedyAlgorithm,
) -> ExperimentRecord:
    """Run the locked study and return the completed ExperimentRecord."""
    runner = MinimalRunner(locked_study)
    return runner.run_study(
        problems={"prob-001": sphere_2d, "prob-002": sphere_3d},
        algorithms={"alg-001": random_search, "alg-002": greedy_search},
    )


@pytest.fixture
def result_aggregates(
    completed_experiment: ExperimentRecord,
) -> list[ResultAggregate]:
    """ResultAggregates computed from the completed experiment."""
    return compute_result_aggregates(completed_experiment)


# ---------------------------------------------------------------------------
# Helpers exposed to tests
# ---------------------------------------------------------------------------


def make_study_with_epsilon(epsilon: float) -> StudyRecord:
    """Return a locked study with a non-null improvement_epsilon (ADR-004)."""
    return create_study(
        study_id="study-epsilon",
        name="Epsilon test study",
        research_question="Testing epsilon filtering.",
        problem_ids=["prob-001"],
        algorithm_ids=["alg-001"],
        repetitions=1,
        budget=50,
        improvement_epsilon=epsilon,
    )


def make_study_with_cap(max_records: int) -> StudyRecord:
    """Return a locked study with max_records_per_run set (ADR-005)."""
    return create_study(
        study_id="study-cap",
        name="Storage cap test study",
        research_question="Testing storage cap.",
        problem_ids=["prob-001"],
        algorithm_ids=["alg-002"],
        repetitions=1,
        budget=50,
        max_records_per_run=max_records,
    )
