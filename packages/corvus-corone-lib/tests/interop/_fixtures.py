"""Minimal data builders for the IOHprofiler export tests.

These construct ExperimentRecord-shaped objects directly. They deliberately do not
run an optimizer: the IOHprofiler exporter is a pure translation from
PerformanceRecords to `.dat` plus a JSON sidecar, so the export tests only need
records with the right shape and plausible values.

Field names follow the entity schemas in
`docs/03-technical-contracts/01-data-format/` (Run 2.5, PerformanceRecord 2.6) and
the identifiers are UUID-shaped strings per ADR-014.

This module replaces the interface stubs that previously lived in
`tests/e2e/_stubs.py`. Those stubs implemented Problem, Algorithm and Runner in
order to test whether the contracts were implementable; that question has been
answered and recorded in ADR-013, ADR-014, ADR-017, ADR-020 and ADR-021, and the
acceptance obligations they encoded are recorded in
`docs/02-design/01-software-requirement-specification/07-acceptance-test-strategy/`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PerformanceRecord:
    """data-format 2.6 — one record per trigger event in a Run."""

    evaluation_number: int
    objective_value: float
    best_so_far: float
    is_improvement: bool
    trigger_reason: str
    elapsed_time: float = 0.0
    current_solution: dict[str, Any] | None = None


@dataclass
class RunRecord:
    """data-format 2.5 — one execution of one algorithm on one problem."""

    id: str
    problem_id: str
    algorithm_id: str
    seed: int
    budget_used: int
    status: str = "completed"
    cap_reached_at_evaluation: int | None = None
    records: list[PerformanceRecord] = field(default_factory=list)


@dataclass
class ExperimentRecord:
    """data-format 2.4 — the executed instance of a Study."""

    id: str
    study_id: str
    status: str = "completed"
    runs: list[RunRecord] = field(default_factory=list)


def make_run(
    run_id: str,
    problem_id: str,
    algorithm_id: str,
    seed: int,
    budget: int = 20,
) -> RunRecord:
    """Build one Run with a monotonically improving best-so-far trace.

    The trace satisfies the invariants the exporter relies on: the first record is
    an improvement, `best_so_far` is non-increasing, `evaluation_number` is strictly
    increasing, and exactly one record carries an `end_of_run` trigger reason.
    """
    rng = random.Random(seed)
    records: list[PerformanceRecord] = []
    best = float("inf")
    scheduled = {1, 2, 5, 10, 20}

    for ev in range(1, budget + 1):
        value = rng.uniform(0.0, 10.0)
        improved = value < best
        if improved:
            best = value
        is_last = ev == budget
        if not (improved or ev in scheduled or is_last):
            continue

        reasons = []
        if ev in scheduled:
            reasons.append("scheduled")
        if improved:
            reasons.append("improvement")
        if is_last:
            reasons.append("end_of_run")
        trigger = _trigger_reason(reasons)

        records.append(
            PerformanceRecord(
                evaluation_number=ev,
                objective_value=value,
                best_so_far=best,
                is_improvement=improved,
                trigger_reason=trigger,
            )
        )

    return RunRecord(
        id=run_id,
        problem_id=problem_id,
        algorithm_id=algorithm_id,
        seed=seed,
        budget_used=budget,
        records=records,
    )


def _trigger_reason(reasons: list[str]) -> str:
    """Map the set of firing triggers onto the seven-value enum (ADR-002)."""
    s = set(reasons)
    if s == {"scheduled"}:
        return "scheduled"
    if s == {"improvement"}:
        return "improvement"
    if s == {"end_of_run"}:
        return "end_of_run"
    if s == {"scheduled", "improvement"}:
        return "both"
    if s == {"scheduled", "end_of_run"}:
        return "scheduled_end_of_run"
    if s == {"improvement", "end_of_run"}:
        return "improvement_end_of_run"
    return "all"


def make_experiment(
    experiment_id: str,
    study_id: str,
    problem_ids: list[str],
    algorithm_ids: list[str],
    repetitions: int,
    budget: int = 20,
) -> ExperimentRecord:
    """Build a complete Experiment: problems x algorithms x repetitions Runs."""
    runs: list[RunRecord] = []
    seed = 1000
    for problem_id in problem_ids:
        for algorithm_id in algorithm_ids:
            for rep in range(repetitions):
                seed += 1
                runs.append(
                    make_run(
                        run_id=f"run-{problem_id}-{algorithm_id}-{rep}",
                        problem_id=problem_id,
                        algorithm_id=algorithm_id,
                        seed=seed,
                        budget=budget,
                    )
                )
    return ExperimentRecord(id=experiment_id, study_id=study_id, runs=runs)
