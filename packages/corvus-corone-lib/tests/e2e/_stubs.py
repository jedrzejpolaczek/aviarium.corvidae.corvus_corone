"""
Stub implementations of the Problem, Algorithm, and Runner interfaces.

These stubs implement the interface contracts faithfully using minimal
deterministic logic. They are NOT mocks — they perform real computation
using only stdlib. They exist to make the UC-01 E2E test runnable before
the production library is implemented.

When corvus_corone ships, replace usage of these stubs with the real API:
    import corvus_corone as cc

Interface contracts:
    → docs/03-technical-contracts/02-interface-contracts.md §1 (Problem)
    → docs/03-technical-contracts/02-interface-contracts.md §2 (Algorithm)
    → docs/03-technical-contracts/02-interface-contracts.md §3 (Runner)

Data format:
    → docs/03-technical-contracts/01-data-format.md §2.3–§2.7

Architectural decisions implemented here:
    → ADR-002: dual-trigger PerformanceRecord strategy
    → ADR-004: improvement sensitivity threshold (improvement_epsilon)
    → ADR-005: PerformanceRecord storage cap
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Data containers  (minimal implementation of data-format.md §2.x entities)
# ---------------------------------------------------------------------------


@dataclass
class SearchSpace:
    """Minimal SearchSpace — data-format.md §2.1 variables field."""

    dimensions: int
    lower: float
    upper: float


@dataclass
class EvaluationResult:
    """data-format.md §2.6 output of Problem.evaluate()."""

    objective_value: float
    metadata: dict[str, Any]
    evaluation_number: int


@dataclass
class PerformanceRecord:
    """data-format.md §2.6 — one record per trigger event in a Run.

    trigger_reason values (ADR-002):
        scheduled | improvement | end_of_run |
        both | scheduled_end_of_run | improvement_end_of_run | all
    """

    evaluation_number: int
    objective_value: float
    best_so_far: float
    trigger_reason: str
    is_improvement: bool
    elapsed_time: float = 0.0


@dataclass
class RunRecord:
    """data-format.md §2.5 — one Run (single problem × algorithm × seed)."""

    run_id: str
    problem_id: str
    algorithm_id: str
    seed: int
    budget_used: int
    status: str  # "completed" | "failed"
    records: list[PerformanceRecord] = field(default_factory=list)
    cap_reached_at_evaluation: int | None = None
    failure_reason: str | None = None


@dataclass
class StudyRecord:
    """data-format.md §2.3 — locked before Experiment begins (MANIFESTO Principle 16)."""

    study_id: str
    name: str
    research_question: str
    problem_ids: list[str]
    algorithm_ids: list[str]
    repetitions: int
    budget: int
    seed_strategy: str
    sampling_strategy: str
    log_scale_schedule: dict[str, Any]
    improvement_epsilon: float | None
    pre_registered_hypotheses: list[dict[str, Any]]
    status: str = "locked"
    max_records_per_run: int | None = None


@dataclass
class ExperimentRecord:
    """data-format.md §2.4 — produced by the Runner."""

    experiment_id: str
    study_id: str
    runs: list[RunRecord] = field(default_factory=list)
    status: str = "completed"


@dataclass
class ResultAggregate:
    """data-format.md §2.7 — metrics aggregated over runs per (problem, algorithm)."""

    problem_id: str
    algorithm_id: str
    n_runs: int
    metrics: dict[str, Any]  # metric_name → {"mean", "median", "stdev"}


@dataclass
class Report:
    """Minimal report entity — FR-20/FR-21."""

    report_type: str  # "researcher" | "practitioner"
    experiment_id: str
    has_limitations_section: bool
    limitations: list[str]
    confirmatory_results: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Exception hierarchy  (interface-contracts.md §6 Error Taxonomy)
# ---------------------------------------------------------------------------


class StudyLockedError(Exception):
    """Raised when modification is attempted on a locked Study (UC-01 F3)."""


class SeedCollisionError(Exception):
    """Raised when the Runner detects a duplicate seed within an Experiment (UC-01 F4)."""


class BudgetExhaustedError(Exception):
    """Raised by Problem.evaluate() when budget is exhausted (interface-contracts.md §1)."""


# ---------------------------------------------------------------------------
# Schedule computation  (ADR-002 §COCO {1,2,5}×10^i schedule)
# ---------------------------------------------------------------------------


def compute_log_scale_schedule(
    base_points: list[int],
    multiplier_base: int,
    budget: int,
) -> set[int]:
    """Compute evaluation numbers that should receive a scheduled PerformanceRecord.

    Implements the COCO/IOH {1,2,5}×10^i preferred-number series (ADR-002).

    Parameters
    ----------
    base_points:
        The base values; canonical value is [1, 2, 5].
    multiplier_base:
        The multiplier base; canonical value is 10.
    budget:
        Maximum evaluation number (inclusive upper bound).

    Returns
    -------
    set[int]
        1-indexed evaluation numbers ≤ budget at which a scheduled record is due.

    Examples
    --------
    >>> compute_log_scale_schedule([1, 2, 5], 10, 50)
    {1, 2, 5, 10, 20, 50}
    """
    schedule: set[int] = set()
    i = 0
    while True:
        power = multiplier_base**i
        found_any = False
        for base in base_points:
            val = base * power
            if val <= budget:
                schedule.add(val)
                found_any = True
        if not found_any:
            break
        i += 1
    return schedule


# ---------------------------------------------------------------------------
# Stub Problem  (interface-contracts.md §1)
# ---------------------------------------------------------------------------

VALID_TRIGGER_REASONS = frozenset(
    {
        "scheduled",
        "improvement",
        "end_of_run",
        "both",
        "scheduled_end_of_run",
        "improvement_end_of_run",
        "all",
    }
)

# Maps each combined trigger_reason name to the set of individual triggers it encodes.
# Use has_trigger() rather than substring matching to query trigger membership.
_TRIGGER_FLAGS: dict[str, frozenset[str]] = {
    "scheduled": frozenset({"scheduled"}),
    "improvement": frozenset({"improvement"}),
    "end_of_run": frozenset({"end_of_run"}),
    "both": frozenset({"scheduled", "improvement"}),
    "scheduled_end_of_run": frozenset({"scheduled", "end_of_run"}),
    "improvement_end_of_run": frozenset({"improvement", "end_of_run"}),
    "all": frozenset({"scheduled", "improvement", "end_of_run"}),
}


def has_trigger(record: PerformanceRecord, trigger: str) -> bool:
    """Return True if the record was written because of the given trigger.

    Parameters
    ----------
    record:
        A PerformanceRecord with a trigger_reason from VALID_TRIGGER_REASONS.
    trigger:
        One of "scheduled", "improvement", "end_of_run".

    Examples
    --------
    >>> # trigger_reason="both" encodes scheduled + improvement
    >>> has_trigger(rec, "improvement")  # True even though "improvement" not in "both"
    >>> has_trigger(rec, "end_of_run")   # False
    """
    return trigger in _TRIGGER_FLAGS[record.trigger_reason]


class StubNoisySphereProblem:
    """Noisy sphere: f(x) = ||x||² + N(0, noise_std²).

    Implements the Problem Interface (interface-contracts.md §1):
    - evaluate() is deterministic given the same seed and solution
    - budget is enforced (BudgetExhaustedError after exhaustion)
    - state is fully reset by reset(seed), enabling Run isolation
    - no randomness is generated without a seed (cross-cutting contract §6)

    Parameters
    ----------
    problem_id:
        Unique identifier for this problem instance.
    dim:
        Number of search dimensions.
    budget:
        Maximum number of allowed evaluate() calls per Run.
    noise_std:
        Standard deviation of Gaussian noise added to each evaluation.
    """

    def __init__(
        self,
        problem_id: str,
        dim: int,
        budget: int,
        noise_std: float = 0.1,
    ) -> None:
        self._id = problem_id
        self._dim = dim
        self._budget = budget
        self._noise_std = noise_std
        self._eval_count = 0
        self._rng: random.Random | None = None

    def get_search_space(self) -> SearchSpace:
        """Return the search space — hypercube [-5, 5]^dim.

        Returns
        -------
        SearchSpace
            Immutable; not affected by evaluate() calls (postcondition §1).
        """
        return SearchSpace(dimensions=self._dim, lower=-5.0, upper=5.0)

    def get_metadata(self) -> dict[str, Any]:
        """Return the ProblemInstance metadata record (data-format.md §2.1).

        Returns
        -------
        dict[str, Any]
            Complete and valid problem metadata.
        """
        return {
            "id": self._id,
            "name": f"StubNoisySphere{self._dim}D",
            "dimensions": self._dim,
            "noise_level": f"gaussian_{self._noise_std}",
            "budget": self._budget,
        }

    def get_remaining_budget(self) -> int:
        """Return remaining evaluations. 0 means budget exhausted (postcondition §1).

        Returns
        -------
        int
            Non-negative remaining evaluation count.
        """
        return self._budget - self._eval_count

    def evaluate(self, solution: list[float]) -> EvaluationResult:
        """Evaluate the noisy sphere at solution.

        Parameters
        ----------
        solution:
            A point in [-5, 5]^dim.

        Returns
        -------
        EvaluationResult
            objective_value = ||solution||² + noise; evaluation_number increments by 1.

        Raises
        ------
        BudgetExhaustedError
            If get_remaining_budget() == 0.
        ValueError
            If len(solution) != dim.
        RuntimeError
            If reset() has not been called before the first evaluate().
        """
        if self.get_remaining_budget() <= 0:
            raise BudgetExhaustedError(
                f"Problem {self._id}: budget of {self._budget} evaluations exhausted."
            )
        if len(solution) != self._dim:
            raise ValueError(
                f"Problem {self._id}: expected {self._dim}-d solution, got {len(solution)}-d."
            )
        if self._rng is None:
            raise RuntimeError(
                f"Problem {self._id}: reset() must be called before evaluate()."
            )

        self._eval_count += 1
        raw_f = sum(x**2 for x in solution)
        noise = self._rng.gauss(0.0, self._noise_std)
        return EvaluationResult(
            objective_value=raw_f + noise,
            metadata={"raw_f": raw_f},
            evaluation_number=self._eval_count,
        )

    def reset(self, seed: int) -> None:
        """Reset internal state for a new Run with the given seed.

        Postcondition: subsequent evaluate() calls start from evaluation_number=1.
        The seed is the mechanism by which the Runner injects reproducible randomness
        (interface-contracts.md §1, cross-cutting contract §6).

        Parameters
        ----------
        seed:
            Run-specific seed injected by the Runner.
        """
        self._eval_count = 0
        self._rng = random.Random(seed)


# ---------------------------------------------------------------------------
# Stub Algorithms  (interface-contracts.md §2)
# ---------------------------------------------------------------------------


class StubRandomSearchAlgorithm:
    """Uniform random search over the search space.

    Implements the Algorithm Interface (interface-contracts.md §2).
    All randomness flows from the seed injected by initialize(); no unseeded
    random calls are ever made (cross-cutting contract §6).

    Parameters
    ----------
    algorithm_id:
        Unique identifier for this algorithm instance.
    """

    def __init__(self, algorithm_id: str) -> None:
        self._id = algorithm_id
        self._search_space: SearchSpace | None = None
        self._rng: random.Random | None = None

    def initialize(self, search_space: SearchSpace, seed: int) -> None:
        """Prepare for a new Run. Must be called before suggest().

        Postcondition: all subsequent suggest() calls are deterministic given seed.

        Parameters
        ----------
        search_space:
            The Problem's search space for this Run.
        seed:
            Run-specific seed injected by the Runner.
        """
        self._search_space = search_space
        self._rng = random.Random(seed)

    def suggest(self, context: dict[str, Any]) -> list[float]:
        """Propose the next solution — a uniformly random point in the search space.

        Parameters
        ----------
        context:
            RunContext with remaining_budget and elapsed_evaluations.

        Returns
        -------
        list[float]
            A point within search_space bounds (postcondition §2).
        """
        assert self._search_space is not None and self._rng is not None
        lo, hi = self._search_space.lower, self._search_space.upper
        return [
            self._rng.uniform(lo, hi) for _ in range(self._search_space.dimensions)
        ]

    def observe(self, solution: list[float], result: EvaluationResult) -> None:
        """Update internal model — random search ignores observations.

        Parameters
        ----------
        solution:
            The solution that was evaluated (returned by the most recent suggest()).
        result:
            The EvaluationResult from Problem.evaluate().
        """

    def get_metadata(self) -> dict[str, Any]:
        """Return AlgorithmInstance metadata (data-format.md §2.2).

        Returns
        -------
        dict[str, Any]
            Complete algorithm metadata record.
        """
        return {
            "id": self._id,
            "name": "StubRandomSearch",
            "algorithm_family": "random",
            "configuration_justification": "Uniform random sampling; no configuration.",
        }


class StubGreedyAlgorithm:
    """Greedy perturbation: exploits the current best solution with shrinking steps.

    Used as a proxy for "a better-than-random algorithm" in tests. On smooth
    low-noise objectives it consistently outperforms random search within
    moderate budgets.

    Implements the Algorithm Interface (interface-contracts.md §2).

    Parameters
    ----------
    algorithm_id:
        Unique identifier for this algorithm instance.
    """

    def __init__(self, algorithm_id: str) -> None:
        self._id = algorithm_id
        self._search_space: SearchSpace | None = None
        self._rng: random.Random | None = None
        self._best_solution: list[float] | None = None
        self._best_value: float = float("inf")

    def initialize(self, search_space: SearchSpace, seed: int) -> None:
        """Prepare for a new Run. Clears all state from prior Runs.

        Parameters
        ----------
        search_space:
            The Problem's search space for this Run.
        seed:
            Run-specific seed injected by the Runner.
        """
        self._search_space = search_space
        self._rng = random.Random(seed)
        self._best_solution = None
        self._best_value = float("inf")

    def suggest(self, context: dict[str, Any]) -> list[float]:
        """Propose the next solution.

        On the first call: uniform random. Subsequently: perturbs the current
        best solution with a step size that shrinks as elapsed evaluations grow.

        Parameters
        ----------
        context:
            RunContext with elapsed_evaluations used to decay the perturbation step.

        Returns
        -------
        list[float]
            A point within search_space bounds.
        """
        assert self._search_space is not None and self._rng is not None
        lo, hi = self._search_space.lower, self._search_space.upper
        if self._best_solution is None:
            return [
                self._rng.uniform(lo, hi) for _ in range(self._search_space.dimensions)
            ]
        elapsed = context.get("elapsed_evaluations", 1)
        step = 0.5 * (hi - lo) / (1.0 + elapsed)
        return [
            max(lo, min(hi, x + self._rng.gauss(0.0, step)))
            for x in self._best_solution
        ]

    def observe(self, solution: list[float], result: EvaluationResult) -> None:
        """Update best solution if result improves the current best.

        Parameters
        ----------
        solution:
            The solution returned by the most recent suggest().
        result:
            The EvaluationResult from Problem.evaluate().
        """
        if result.objective_value < self._best_value:
            self._best_value = result.objective_value
            self._best_solution = list(solution)

    def get_metadata(self) -> dict[str, Any]:
        """Return AlgorithmInstance metadata (data-format.md §2.2).

        Returns
        -------
        dict[str, Any]
            Complete algorithm metadata record.
        """
        return {
            "id": self._id,
            "name": "StubGreedy",
            "algorithm_family": "local_search",
            "configuration_justification": "Greedy perturbation with decaying step size.",
        }


# ---------------------------------------------------------------------------
# Minimal Runner  (interface-contracts.md §3)
# ---------------------------------------------------------------------------

Algorithm = StubRandomSearchAlgorithm | StubGreedyAlgorithm


class MinimalRunner:
    """Orchestrates Problems and Algorithms to produce an ExperimentRecord.

    Implements:
    - on_evaluation(): ADR-002 dual-trigger + end-of-run trigger
    - ADR-004: improvement_epsilon semantics
    - ADR-005: max_records_per_run cap (improvement records only)
    - UC-01 F4: seed collision detection (SeedCollisionError)
    - Isolation contract: each Run gets its own problem.reset() + algorithm.initialize()

    Parameters
    ----------
    study:
        The locked StudyRecord governing this Experiment.
    """

    def __init__(self, study: StudyRecord) -> None:
        self._study = study
        self._schedule = compute_log_scale_schedule(
            base_points=study.log_scale_schedule["base_points"],
            multiplier_base=study.log_scale_schedule["multiplier_base"],
            budget=study.budget,
        )

    def run_single(
        self,
        problem: StubNoisySphereProblem,
        algorithm: Algorithm,
        seed: int,
    ) -> RunRecord:
        """Execute one Run: one (problem, algorithm, seed) triple.

        Isolation contract: problem.reset(seed) and algorithm.initialize(..., seed)
        are called at the start; no state leaks between Runs.

        Parameters
        ----------
        problem:
            Problem instance; will be reset before the Run begins.
        algorithm:
            Algorithm instance; will be initialized before the Run begins.
        seed:
            Run-specific seed injected by the Runner (never generated inside Problem
            or Algorithm — cross-cutting contract §6).

        Returns
        -------
        RunRecord
            Completed Run with PerformanceRecords per ADR-002 trigger logic.
        """
        budget = self._study.budget
        epsilon = self._study.improvement_epsilon
        max_records = self._study.max_records_per_run

        problem.reset(seed)
        algorithm.initialize(problem.get_search_space(), seed)

        records: list[PerformanceRecord] = []
        best_so_far = float("inf")
        improvement_record_count = 0
        cap_reached_at: int | None = None

        for eval_num in range(1, budget + 1):
            context = {
                "remaining_budget": budget - eval_num + 1,
                "elapsed_evaluations": eval_num - 1,
            }
            solution = algorithm.suggest(context)
            result = problem.evaluate(solution)
            algorithm.observe(solution, result)

            obj = result.objective_value
            is_last = eval_num == budget

            # ADR-004: improvement criterion
            if epsilon is None:
                is_improvement = obj < best_so_far
            else:
                is_improvement = (best_so_far - obj) > epsilon

            if is_improvement:
                best_so_far = obj

            is_scheduled = eval_num in self._schedule

            # ADR-005: suppress improvement records once cap is reached.
            # Only non-scheduled, non-end-of-run improvement records count toward the cap
            # and are subject to suppression. Scheduled records that happen to also be
            # improvements continue to fire — they are written by the scheduled trigger,
            # not solely by the improvement trigger, so suppressing them would violate
            # ADR-005 §1 ("Scheduled records continue to be written").
            # cap_reached_at tracks the *first* evaluation where suppression began.
            if (
                max_records is not None
                and is_improvement
                and not is_scheduled
                and not is_last
                and improvement_record_count >= max_records
            ):
                if cap_reached_at is None:
                    cap_reached_at = eval_num
                is_improvement = False

            # Determine active triggers
            triggers: set[str] = set()
            if is_scheduled:
                triggers.add("scheduled")
            if is_improvement:
                triggers.add("improvement")
            if is_last:
                triggers.add("end_of_run")

            if not triggers:
                continue  # no trigger fired — skip this evaluation

            # ADR-002 combined trigger_reason encoding
            if triggers == {"scheduled", "improvement", "end_of_run"}:
                trigger_reason = "all"
            elif triggers == {"scheduled", "improvement"}:
                trigger_reason = "both"
            elif triggers == {"scheduled", "end_of_run"}:
                trigger_reason = "scheduled_end_of_run"
            elif triggers == {"improvement", "end_of_run"}:
                trigger_reason = "improvement_end_of_run"
            else:
                (trigger_reason,) = triggers  # single trigger

            # Count only non-scheduled improvement records toward the cap
            # (scheduled records are O(log budget) and do not drive unbounded growth)
            if is_improvement and not is_scheduled:
                improvement_record_count += 1

            records.append(
                PerformanceRecord(
                    evaluation_number=eval_num,
                    objective_value=obj,
                    best_so_far=best_so_far,
                    trigger_reason=trigger_reason,
                    is_improvement=is_improvement,
                )
            )

        meta = problem.get_metadata()
        alg_meta = algorithm.get_metadata()
        return RunRecord(
            run_id=f"run-{meta['id']}-{alg_meta['id']}-seed{seed}",
            problem_id=str(meta["id"]),
            algorithm_id=str(alg_meta["id"]),
            seed=seed,
            budget_used=budget,
            status="completed",
            records=records,
            cap_reached_at_evaluation=cap_reached_at,
        )

    def run_study(
        self,
        problems: dict[str, StubNoisySphereProblem],
        algorithms: dict[str, Algorithm],
    ) -> ExperimentRecord:
        """Execute all Runs defined by the Study plan.

        Seeds are assigned sequentially (sequential seed_strategy).
        Raises SeedCollisionError if any seed would be used twice (UC-01 F4).

        Parameters
        ----------
        problems:
            Mapping of problem_id → Problem instance.
        algorithms:
            Mapping of algorithm_id → Algorithm instance.

        Returns
        -------
        ExperimentRecord
            Completed Experiment with all Run records populated.
        """
        runs: list[RunRecord] = []
        used_seeds: set[int] = set()
        seed_counter = 0

        for prob_id in self._study.problem_ids:
            for alg_id in self._study.algorithm_ids:
                for _ in range(self._study.repetitions):
                    seed = seed_counter
                    seed_counter += 1
                    if seed in used_seeds:
                        raise SeedCollisionError(
                            f"Seed {seed} already used in this Experiment (UC-01 F4)."
                        )
                    used_seeds.add(seed)
                    run = self.run_single(problems[prob_id], algorithms[alg_id], seed)
                    runs.append(run)

        return ExperimentRecord(
            experiment_id=f"exp-{self._study.study_id}",
            study_id=self._study.study_id,
            runs=runs,
            status="completed",
        )


# ---------------------------------------------------------------------------
# Pre-registration gate  (FR-12 / MANIFESTO Principle 16)
# ---------------------------------------------------------------------------


def create_study(
    *,
    study_id: str = "study-e2e-001",
    name: str,
    research_question: str,
    problem_ids: list[str],
    algorithm_ids: list[str],
    repetitions: int,
    budget: int,
    seed_strategy: str = "sequential",
    sampling_strategy: str = "log_scale_plus_improvement",
    log_scale_schedule: dict[str, Any] | None = None,
    improvement_epsilon: float | None = None,
    pre_registered_hypotheses: list[dict[str, Any]] | None = None,
    max_records_per_run: int | None = None,
) -> StudyRecord:
    """Create and immediately lock a StudyRecord.

    The lock is permanent — no field can be changed after this call (UC-01 F3).

    Parameters
    ----------
    study_id:
        Unique identifier for the study.
    name:
        Human-readable study name.
    research_question:
        The scoped research question (MANIFESTO Principle 1).
    problem_ids:
        IDs of ProblemInstances selected for this study.
    algorithm_ids:
        IDs of AlgorithmInstances selected for this study.
    repetitions:
        Number of independent runs per (problem, algorithm) pair.
    budget:
        Evaluation budget per Run.
    seed_strategy:
        How seeds are assigned; "sequential" is the only stub-supported value.
    sampling_strategy:
        PerformanceRecord sampling strategy name (ADR-002).
    log_scale_schedule:
        base_points and multiplier_base for the COCO schedule (ADR-002).
    improvement_epsilon:
        Optional minimum improvement threshold (ADR-004). None = strict inequality.
    pre_registered_hypotheses:
        Hypotheses locked before execution (MANIFESTO Principle 16).
    max_records_per_run:
        Optional hard cap on improvement records per Run (ADR-005).

    Returns
    -------
    StudyRecord
        A locked study record (status == "locked").
    """
    return StudyRecord(
        study_id=study_id,
        name=name,
        research_question=research_question,
        problem_ids=problem_ids,
        algorithm_ids=algorithm_ids,
        repetitions=repetitions,
        budget=budget,
        seed_strategy=seed_strategy,
        sampling_strategy=sampling_strategy,
        log_scale_schedule=log_scale_schedule or {"base_points": [1, 2, 5], "multiplier_base": 10},
        improvement_epsilon=improvement_epsilon,
        pre_registered_hypotheses=pre_registered_hypotheses or [],
        status="locked",
        max_records_per_run=max_records_per_run,
    )


def update_study(study: StudyRecord, **kwargs: Any) -> None:
    """Attempt to update a Study field — raises StudyLockedError if locked (UC-01 F3).

    Parameters
    ----------
    study:
        The StudyRecord to modify.
    **kwargs:
        Fields to update.

    Raises
    ------
    StudyLockedError
        Always, because create_study() always returns a locked study.
    """
    if study.status == "locked":
        raise StudyLockedError(
            f"Study {study.study_id} is locked. Modification attempt recorded."
        )
    for k, v in kwargs.items():
        setattr(study, k, v)


# ---------------------------------------------------------------------------
# Minimal Analysis Engine  (interface-contracts.md §4)
# ---------------------------------------------------------------------------


def compute_result_aggregates(experiment: ExperimentRecord) -> list[ResultAggregate]:
    """Compute QUALITY-BEST_VALUE_AT_BUDGET for every (problem, algorithm) pair.

    Implements interface-contracts.md §4 compute_metrics() for the single metric
    QUALITY-BEST_VALUE_AT_BUDGET = best_so_far at the end-of-run PerformanceRecord.

    Parameters
    ----------
    experiment:
        The completed ExperimentRecord.

    Returns
    -------
    list[ResultAggregate]
        One ResultAggregate per (problem_id, algorithm_id) pair found in runs.
        n_runs equals the number of runs contributing to each aggregate.

    Postcondition
    -------------
    Every (problem_id, algorithm_id) combination present in experiment.runs
    appears exactly once in the output (interface-contracts.md §4).
    """
    groups: dict[tuple[str, str], list[float]] = {}
    for run in experiment.runs:
        end_records = [r for r in run.records if has_trigger(r, "end_of_run")]
        if not end_records:
            continue
        key = (run.problem_id, run.algorithm_id)
        groups.setdefault(key, []).append(end_records[-1].best_so_far)

    return [
        ResultAggregate(
            problem_id=prob_id,
            algorithm_id=alg_id,
            n_runs=len(values),
            metrics={
                "QUALITY-BEST_VALUE_AT_BUDGET": {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
                }
            },
        )
        for (prob_id, alg_id), values in groups.items()
    ]


def generate_reports(
    experiment: ExperimentRecord,
    aggregates: list[ResultAggregate],
    study: StudyRecord,
) -> list[Report]:
    """Generate Researcher and Practitioner Reports (FR-20, FR-21).

    Both reports always include a non-empty limitations section (FR-21).
    Non-null improvement_epsilon is automatically disclosed (ADR-004).

    Parameters
    ----------
    experiment:
        The completed ExperimentRecord.
    aggregates:
        ResultAggregates computed by compute_result_aggregates().
    study:
        The locked StudyRecord (provides scope context for limitations).

    Returns
    -------
    list[Report]
        Exactly two Reports: one "researcher" and one "practitioner".
    """
    limitations: list[str] = [
        (
            f"Conclusions are scoped to the {len(study.problem_ids)} tested "
            "problem instances only. Generalization beyond the tested problem "
            "characteristics is not supported."
        ),
        (
            f"Budget={study.budget} evaluations. Conclusions do not extend "
            "to other budget levels."
        ),
    ]
    if study.improvement_epsilon is not None:
        limitations.append(
            f"improvement_epsilon={study.improvement_epsilon} was pre-registered. "
            "Sub-epsilon improvements are not captured in improvement records "
            "(ADR-004). TIME-EVALUATIONS_TO_TARGET may be affected for targets "
            "first crossed by sub-epsilon improvements."
        )
    if any(r.cap_reached_at_evaluation is not None for r in experiment.runs):
        limitations.append(
            "max_records_per_run cap was reached in one or more Runs. "
            "Improvement records are absent beyond cap_reached_at_evaluation "
            "for those Runs (ADR-005)."
        )

    return [
        Report(
            report_type=report_type,
            experiment_id=experiment.experiment_id,
            has_limitations_section=True,
            limitations=limitations,
            confirmatory_results=[],
        )
        for report_type in ("researcher", "practitioner")
    ]
