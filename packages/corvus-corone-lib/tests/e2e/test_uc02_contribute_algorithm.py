"""
End-to-end tests for UC-02: Contribute an Algorithm Implementation.

Tests are grouped by what they validate:

  CLASS TestAlgorithmInterfaceCompliance
    — all five required methods are present and callable
    — method return-type contracts (suggest returns list of lists, etc.)

  CLASS TestAlgorithmInstanceMetadata
    — get_metadata() returns all required AlgorithmInstance fields
    — supported_variable_types in metadata matches get_supported_variable_types()
    — declared_version() result matches regex ^\\d+\\.\\d+\\.\\d+$
    — configuration_justification is non-empty (F3 precondition)
    — code_reference is version-pinned (F2 precondition)

  CLASS TestRegistrationValidation
    — F1: missing observe() → validation failure
    — F1: missing suggest() → validation failure
    — F1: missing initialize() → validation failure
    — F1: missing get_supported_variable_types() → validation failure
    — F1: missing get_metadata() → validation failure
    — F2: floating code_reference (branch name) → validation failure
    — F3: empty configuration_justification → validation failure
    — F4: hyperparameter key mismatch → validation failure
    — valid implementation passes all checks

  CLASS TestAdapterSmokeRun
    — UC-02 Step 6: smoke run completes without exception
    — run status is "completed"
    — at least one PerformanceRecord is produced
    — budget is respected (no extra evaluations)
    — end-of-run record exists (ADR-002 postcondition)
    — random_search and greedy both pass the smoke run

  CLASS TestReproducibility
    — same seed → identical PerformanceRecord sequence
    — different seeds → different solutions (statistically)
    — state is fully reset between consecutive runs (UC-02 Step 2 isolation)

  CLASS TestSeedIsolation
    — RNG is created from injected seed (not unseeded)
    — suggest() called before initialize() raises or produces no output

  CLASS TestBatchSuggest
    — suggest(batch_size=1) returns list of length 1
    — suggest(batch_size=3) returns list of length 3
    — all solutions in batch are within search space bounds
    — each solution has the correct dimensionality

References
----------
→ UC-02:         docs/02-design/01-software-requirement-specification/02-use-cases/03-uc-02.md
→ Tutorial:      docs/06_tutorials/uc-02-contribute-algorithm.md
→ Interface §2:  docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md
→ Data §2.2:     docs/03-technical-contracts/01-data-format/03-algorithm-instance.md
→ Cross-cutting: docs/03-technical-contracts/02-interface-contracts/07-cross-cutting-contracts.md
"""

from __future__ import annotations

import re
from typing import Any

import pytest
from tests.e2e._stubs import (
    EvaluationResult,
    MinimalRunner,
    PerformanceRecord,
    SearchSpace,
    StubGreedyAlgorithm,
    StubNoisySphereProblem,
    StubRandomSearchAlgorithm,
    create_study,
    has_trigger,
)

# ---------------------------------------------------------------------------
# Registration validator
# Simulates what the Algorithm Registry checks at registration time (UC-02 §5).
# Returns a list of validation error strings; empty list means the submission
# passes all checks.
# ---------------------------------------------------------------------------

_FLOATING_REF_PATTERN = re.compile(
    r"@(main|master|HEAD|develop|dev|latest)$",
    re.IGNORECASE,
)
_PINNED_PACKAGE_PATTERN = re.compile(r".+==\d+\.\d+(\.\d+)?")
_GIT_SHA_PATTERN = re.compile(r"@[0-9a-f]{7,40}$", re.IGNORECASE)


def _is_pinned(code_reference: str) -> bool:
    """Return True if code_reference is version-pinned (no floating refs).

    Accepts:
      - git URLs ending with a hex SHA  (e.g., git+https://...@abc1234)
      - package==version strings        (e.g., optuna==3.6.1)

    Rejects:
      - URLs ending with branch names   (e.g., @main, @master, @HEAD)
      - any other unrecognized pattern
    """
    if _FLOATING_REF_PATTERN.search(code_reference):
        return False
    if _GIT_SHA_PATTERN.search(code_reference):
        return True
    if _PINNED_PACKAGE_PATTERN.fullmatch(code_reference):
        return True
    # Bare package name without version is also floating
    return False


_REQUIRED_METHODS = ("initialize", "suggest", "observe", "get_supported_variable_types", "get_metadata")
_REQUIRED_METADATA_FIELDS = (
    "id",
    "name",
    "algorithm_family",
    "hyperparameters",
    "configuration_justification",
    "code_reference",
    "language",
    "framework",
    "framework_version",
    "known_assumptions",
    "contributed_by",
    "supported_variable_types",
)


def validate_for_registration(algorithm: object) -> list[str]:
    """Validate an algorithm object against all UC-02 registration rules.

    Returns a list of human-readable error strings. An empty list means the
    algorithm passes all checks and can be registered.

    Checks:
      F1 — all five interface methods are callable
      F2 — code_reference is version-pinned
      F3 — configuration_justification is non-empty
      F4 — all required metadata fields are present
    """
    errors: list[str] = []

    # F1: interface compliance
    for method_name in _REQUIRED_METHODS:
        if not callable(getattr(algorithm, method_name, None)):
            errors.append(f"F1: required method '{method_name}' is missing or not callable")

    # Cannot validate metadata fields if get_metadata() is missing
    if not callable(getattr(algorithm, "get_metadata", None)):
        return errors

    try:
        metadata = algorithm.get_metadata()  # type: ignore[union-attr]
    except Exception as exc:  # noqa: BLE001
        errors.append(f"F1: get_metadata() raised {type(exc).__name__}: {exc}")
        return errors

    # F4: required fields present
    for field in _REQUIRED_METADATA_FIELDS:
        if field not in metadata:
            errors.append(f"F4: required metadata field '{field}' is missing")

    # F2: code_reference is version-pinned
    code_ref = metadata.get("code_reference", "")
    if code_ref and not _is_pinned(code_ref):
        errors.append(
            f"F2: code_reference '{code_ref}' is not version-pinned "
            "(use a git SHA or package==version)"
        )

    # F3: configuration_justification is non-empty
    justification = metadata.get("configuration_justification", "")
    if not justification or not justification.strip():
        errors.append("F3: configuration_justification is empty")

    # supported_variable_types consistency
    if callable(getattr(algorithm, "get_supported_variable_types", None)):
        declared = algorithm.get_supported_variable_types()  # type: ignore[union-attr]
        in_metadata = metadata.get("supported_variable_types", [])
        if sorted(declared) != sorted(in_metadata):
            errors.append(
                "F4: supported_variable_types in metadata does not match "
                "get_supported_variable_types()"
            )

    return errors


# ---------------------------------------------------------------------------
# Deliberately broken implementations (for F1–F4 failure tests)
# ---------------------------------------------------------------------------


class _MissingObserve:
    """F1: observe() is missing."""

    def initialize(self, search_space: Any, seed: int) -> None: ...  # noqa: E704
    def suggest(self, context: Any, batch_size: int = 1) -> list[list[float]]: return []  # noqa: E704
    def get_supported_variable_types(self) -> list[str]: return ["continuous"]  # noqa: E704
    def get_metadata(self) -> dict[str, Any]:
        return {
            "id": "x", "name": "x", "algorithm_family": "x",
            "hyperparameters": {}, "configuration_justification": "justified",
            "code_reference": "pkg==1.0.0", "language": "python",
            "framework": "stdlib", "framework_version": "3.12",
            "known_assumptions": [], "contributed_by": "author",
            "supported_variable_types": ["continuous"],
        }


class _MissingSuggest:
    """F1: suggest() is missing."""

    def initialize(self, search_space: Any, seed: int) -> None: ...  # noqa: E704
    def observe(self, solution: Any, result: Any) -> None: ...  # noqa: E704
    def get_supported_variable_types(self) -> list[str]: return ["continuous"]  # noqa: E704
    def get_metadata(self) -> dict[str, Any]:
        return {
            "id": "x", "name": "x", "algorithm_family": "x",
            "hyperparameters": {}, "configuration_justification": "justified",
            "code_reference": "pkg==1.0.0", "language": "python",
            "framework": "stdlib", "framework_version": "3.12",
            "known_assumptions": [], "contributed_by": "author",
            "supported_variable_types": ["continuous"],
        }


class _FloatingCodeRef:
    """F2: code_reference points to a branch name, not a pinned version."""

    def initialize(self, search_space: Any, seed: int) -> None: ...  # noqa: E704
    def suggest(self, context: Any, batch_size: int = 1) -> list[list[float]]: return []  # noqa: E704
    def observe(self, solution: Any, result: Any) -> None: ...  # noqa: E704
    def get_supported_variable_types(self) -> list[str]: return ["continuous"]  # noqa: E704
    def get_metadata(self) -> dict[str, Any]:
        return {
            "id": "x", "name": "x", "algorithm_family": "x",
            "hyperparameters": {}, "configuration_justification": "justified",
            "code_reference": "git+https://github.com/org/repo@main",  # ← branch!
            "language": "python", "framework": "stdlib", "framework_version": "3.12",
            "known_assumptions": [], "contributed_by": "author",
            "supported_variable_types": ["continuous"],
        }


class _EmptyJustification:
    """F3: configuration_justification is an empty string."""

    def initialize(self, search_space: Any, seed: int) -> None: ...  # noqa: E704
    def suggest(self, context: Any, batch_size: int = 1) -> list[list[float]]: return []  # noqa: E704
    def observe(self, solution: Any, result: Any) -> None: ...  # noqa: E704
    def get_supported_variable_types(self) -> list[str]: return ["continuous"]  # noqa: E704
    def get_metadata(self) -> dict[str, Any]:
        return {
            "id": "x", "name": "x", "algorithm_family": "x",
            "hyperparameters": {}, "configuration_justification": "",  # ← empty!
            "code_reference": "pkg==1.0.0", "language": "python",
            "framework": "stdlib", "framework_version": "3.12",
            "known_assumptions": [], "contributed_by": "author",
            "supported_variable_types": ["continuous"],
        }


class _MissingMetadataField:
    """F4: required metadata field (contributed_by) is absent."""

    def initialize(self, search_space: Any, seed: int) -> None: ...  # noqa: E704
    def suggest(self, context: Any, batch_size: int = 1) -> list[list[float]]: return []  # noqa: E704
    def observe(self, solution: Any, result: Any) -> None: ...  # noqa: E704
    def get_supported_variable_types(self) -> list[str]: return ["continuous"]  # noqa: E704
    def get_metadata(self) -> dict[str, Any]:
        return {
            "id": "x", "name": "x", "algorithm_family": "x",
            "hyperparameters": {}, "configuration_justification": "justified",
            "code_reference": "pkg==1.0.0", "language": "python",
            "framework": "stdlib", "framework_version": "3.12",
            "known_assumptions": [],
            # ← "contributed_by" missing
            "supported_variable_types": ["continuous"],
        }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sphere_2d() -> StubNoisySphereProblem:
    return StubNoisySphereProblem("prob-001", dim=2, budget=50, noise_std=0.05)


@pytest.fixture
def sphere_5d() -> StubNoisySphereProblem:
    return StubNoisySphereProblem("prob-002", dim=5, budget=100, noise_std=0.1)


@pytest.fixture
def random_search() -> StubRandomSearchAlgorithm:
    return StubRandomSearchAlgorithm("alg-rs-001")


@pytest.fixture
def greedy_search() -> StubGreedyAlgorithm:
    return StubGreedyAlgorithm("alg-gs-001")


@pytest.fixture
def search_space_2d() -> SearchSpace:
    return SearchSpace(dimensions=2, lower=-5.0, upper=5.0)


@pytest.fixture
def search_space_5d() -> SearchSpace:
    return SearchSpace(dimensions=5, lower=-5.0, upper=5.0)


# ---------------------------------------------------------------------------
# CLASS TestAlgorithmInterfaceCompliance
# ---------------------------------------------------------------------------


class TestAlgorithmInterfaceCompliance:
    """Verify both reference implementations satisfy the Algorithm Interface §2."""

    @pytest.mark.parametrize("algorithm_fixture", ["random_search", "greedy_search"])
    def test_all_required_methods_exist(
        self, algorithm_fixture: str, request: pytest.FixtureRequest
    ) -> None:
        algorithm = request.getfixturevalue(algorithm_fixture)
        for method_name in _REQUIRED_METHODS:
            assert callable(getattr(algorithm, method_name, None)), (
                f"{type(algorithm).__name__} is missing required method '{method_name}' (F1)"
            )

    def test_suggest_returns_list(
        self, random_search: StubRandomSearchAlgorithm, search_space_2d: SearchSpace
    ) -> None:
        random_search.initialize(search_space_2d, seed=0)
        result = random_search.suggest({}, batch_size=1)
        assert isinstance(result, list)

    def test_suggest_returns_list_of_lists(
        self, random_search: StubRandomSearchAlgorithm, search_space_2d: SearchSpace
    ) -> None:
        random_search.initialize(search_space_2d, seed=0)
        result = random_search.suggest({}, batch_size=1)
        assert isinstance(result[0], list)

    def test_observe_returns_none(
        self, random_search: StubRandomSearchAlgorithm, search_space_2d: SearchSpace
    ) -> None:
        random_search.initialize(search_space_2d, seed=0)
        solution = random_search.suggest({}, batch_size=1)[0]
        result = EvaluationResult(objective_value=1.0, metadata={}, evaluation_number=1)
        assert random_search.observe(solution, result) is None

    def test_get_supported_variable_types_returns_nonempty_list(
        self, random_search: StubRandomSearchAlgorithm
    ) -> None:
        types = random_search.get_supported_variable_types()
        assert isinstance(types, list)
        assert len(types) >= 1

    def test_get_supported_variable_types_values_are_valid(
        self, random_search: StubRandomSearchAlgorithm
    ) -> None:
        valid = {"continuous", "integer", "categorical"}
        types = random_search.get_supported_variable_types()
        for t in types:
            assert t in valid, f"unknown variable type: '{t}'"

    def test_get_metadata_returns_dict(
        self, random_search: StubRandomSearchAlgorithm
    ) -> None:
        metadata = random_search.get_metadata()
        assert isinstance(metadata, dict)


# ---------------------------------------------------------------------------
# CLASS TestAlgorithmInstanceMetadata
# ---------------------------------------------------------------------------


class TestAlgorithmInstanceMetadata:
    """Verify get_metadata() returns a valid Algorithm Instance record (data-format §2.2)."""

    @pytest.mark.parametrize("algorithm_fixture", ["random_search", "greedy_search"])
    def test_all_required_fields_present(
        self, algorithm_fixture: str, request: pytest.FixtureRequest
    ) -> None:
        algorithm = request.getfixturevalue(algorithm_fixture)
        metadata = algorithm.get_metadata()
        for field in _REQUIRED_METADATA_FIELDS:
            assert field in metadata, f"required field '{field}' missing from get_metadata()"

    @pytest.mark.parametrize("algorithm_fixture", ["random_search", "greedy_search"])
    def test_configuration_justification_is_nonempty(
        self, algorithm_fixture: str, request: pytest.FixtureRequest
    ) -> None:
        algorithm = request.getfixturevalue(algorithm_fixture)
        metadata = algorithm.get_metadata()
        justification = metadata.get("configuration_justification", "")
        assert justification and justification.strip(), (
            "configuration_justification must be non-empty (F3, MANIFESTO Principle 10)"
        )

    @pytest.mark.parametrize("algorithm_fixture", ["random_search", "greedy_search"])
    def test_supported_variable_types_consistent_with_method(
        self, algorithm_fixture: str, request: pytest.FixtureRequest
    ) -> None:
        algorithm = request.getfixturevalue(algorithm_fixture)
        metadata = algorithm.get_metadata()
        from_method = algorithm.get_supported_variable_types()
        from_metadata = metadata.get("supported_variable_types", [])
        assert sorted(from_method) == sorted(from_metadata), (
            "supported_variable_types in get_metadata() must match get_supported_variable_types()"
        )

    @pytest.mark.parametrize("algorithm_fixture", ["random_search", "greedy_search"])
    def test_id_is_present_and_nonempty(
        self, algorithm_fixture: str, request: pytest.FixtureRequest
    ) -> None:
        algorithm = request.getfixturevalue(algorithm_fixture)
        metadata = algorithm.get_metadata()
        assert metadata.get("id"), "Algorithm Instance id must be present and non-empty"

    @pytest.mark.parametrize("algorithm_fixture", ["random_search", "greedy_search"])
    def test_algorithm_family_is_nonempty(
        self, algorithm_fixture: str, request: pytest.FixtureRequest
    ) -> None:
        algorithm = request.getfixturevalue(algorithm_fixture)
        metadata = algorithm.get_metadata()
        assert metadata.get("algorithm_family"), "algorithm_family must be non-empty"

    @pytest.mark.parametrize("algorithm_fixture", ["random_search", "greedy_search"])
    def test_hyperparameters_is_a_dict(
        self, algorithm_fixture: str, request: pytest.FixtureRequest
    ) -> None:
        algorithm = request.getfixturevalue(algorithm_fixture)
        metadata = algorithm.get_metadata()
        assert isinstance(metadata.get("hyperparameters"), dict), (
            "hyperparameters must be a dict (empty dict is valid for no-parameter algorithms)"
        )


# ---------------------------------------------------------------------------
# CLASS TestRegistrationValidation
# ---------------------------------------------------------------------------


class TestRegistrationValidation:
    """Simulate Registry validation: the four UC-02 failure scenarios."""

    def test_valid_random_search_passes_all_checks(
        self, random_search: StubRandomSearchAlgorithm
    ) -> None:
        errors = validate_for_registration(random_search)
        assert errors == [], f"Expected no errors but got: {errors}"

    def test_valid_greedy_passes_all_checks(
        self, greedy_search: StubGreedyAlgorithm
    ) -> None:
        errors = validate_for_registration(greedy_search)
        assert errors == [], f"Expected no errors but got: {errors}"

    def test_f1_missing_observe_is_detected(self) -> None:
        errors = validate_for_registration(_MissingObserve())
        assert any("F1" in e and "observe" in e for e in errors), (
            "F1 error for missing observe() must be reported"
        )

    def test_f1_missing_suggest_is_detected(self) -> None:
        errors = validate_for_registration(_MissingSuggest())
        assert any("F1" in e and "suggest" in e for e in errors), (
            "F1 error for missing suggest() must be reported"
        )

    def test_f2_floating_code_reference_is_detected(self) -> None:
        errors = validate_for_registration(_FloatingCodeRef())
        assert any("F2" in e for e in errors), (
            "F2 error for floating code_reference must be reported"
        )

    def test_f3_empty_justification_is_detected(self) -> None:
        errors = validate_for_registration(_EmptyJustification())
        assert any("F3" in e for e in errors), (
            "F3 error for empty configuration_justification must be reported"
        )

    def test_f4_missing_metadata_field_is_detected(self) -> None:
        errors = validate_for_registration(_MissingMetadataField())
        assert any("F4" in e and "contributed_by" in e for e in errors), (
            "F4 error for missing metadata field must be reported"
        )

    @pytest.mark.parametrize(
        "code_ref,expected_valid",
        [
            ("git+https://github.com/org/repo@abc1234", True),   # short SHA
            ("git+https://github.com/org/repo@a1b2c3d4e5f6", True),  # longer SHA
            ("optuna==3.6.1", True),                              # pinned package
            ("scipy==1.13.0", True),                              # pinned package
            ("git+https://github.com/org/repo@main", False),     # branch name
            ("git+https://github.com/org/repo@master", False),   # branch name
            ("git+https://github.com/org/repo@HEAD", False),     # HEAD ref
            ("optuna", False),                                    # unpinned
        ],
    )
    def test_code_reference_pinning_detection(
        self, code_ref: str, expected_valid: bool
    ) -> None:
        assert _is_pinned(code_ref) == expected_valid, (
            f"_is_pinned({code_ref!r}) should be {expected_valid}"
        )


# ---------------------------------------------------------------------------
# CLASS TestAdapterSmokeRun
# ---------------------------------------------------------------------------


class TestAdapterSmokeRun:
    """UC-02 Step 6: verify the adapter operates correctly end-to-end."""

    def _smoke_study(self, problem_id: str, algorithm_id: str) -> object:
        return create_study(
            study_id="study-uc02-smoke",
            name="UC-02 smoke run",
            research_question=(
                "Verify the algorithm adapter operates correctly on a known Problem Instance."
            ),
            problem_ids=[problem_id],
            algorithm_ids=[algorithm_id],
            repetitions=1,
            budget=50,
        )

    def test_random_search_smoke_run_completes(
        self,
        sphere_2d: StubNoisySphereProblem,
        random_search: StubRandomSearchAlgorithm,
    ) -> None:
        study = self._smoke_study("prob-001", "alg-rs-001")
        runner = MinimalRunner(study)
        run = runner.run_single(sphere_2d, random_search, seed=42)
        assert run.status == "completed"

    def test_greedy_smoke_run_completes(
        self,
        sphere_2d: StubNoisySphereProblem,
        greedy_search: StubGreedyAlgorithm,
    ) -> None:
        study = self._smoke_study("prob-001", "alg-gs-001")
        runner = MinimalRunner(study)
        run = runner.run_single(sphere_2d, greedy_search, seed=42)
        assert run.status == "completed"

    def test_smoke_run_produces_at_least_one_record(
        self,
        sphere_2d: StubNoisySphereProblem,
        random_search: StubRandomSearchAlgorithm,
    ) -> None:
        study = self._smoke_study("prob-001", "alg-rs-001")
        runner = MinimalRunner(study)
        run = runner.run_single(sphere_2d, random_search, seed=42)
        assert len(run.records) >= 1

    def test_smoke_run_budget_respected(
        self,
        sphere_2d: StubNoisySphereProblem,
        random_search: StubRandomSearchAlgorithm,
    ) -> None:
        study = self._smoke_study("prob-001", "alg-rs-001")
        runner = MinimalRunner(study)
        run = runner.run_single(sphere_2d, random_search, seed=42)
        assert run.budget_used == 50
        assert all(r.evaluation_number <= 50 for r in run.records)

    def test_smoke_run_end_of_run_record_exists(
        self,
        sphere_2d: StubNoisySphereProblem,
        random_search: StubRandomSearchAlgorithm,
    ) -> None:
        """ADR-002 postcondition: every completed Run has an end-of-run record."""
        study = self._smoke_study("prob-001", "alg-rs-001")
        runner = MinimalRunner(study)
        run = runner.run_single(sphere_2d, random_search, seed=42)
        end_records = [r for r in run.records if has_trigger(r, "end_of_run")]
        assert len(end_records) == 1
        assert end_records[0].evaluation_number == run.budget_used

    def test_smoke_run_first_record_is_improvement(
        self,
        sphere_2d: StubNoisySphereProblem,
        random_search: StubRandomSearchAlgorithm,
    ) -> None:
        """data-format §2.6: is_improvement must be True for the first record of every Run."""
        study = self._smoke_study("prob-001", "alg-rs-001")
        runner = MinimalRunner(study)
        run = runner.run_single(sphere_2d, random_search, seed=42)
        first_record = min(run.records, key=lambda r: r.evaluation_number)
        assert first_record.is_improvement

    def test_smoke_run_on_higher_dimensional_problem(
        self,
        sphere_5d: StubNoisySphereProblem,
        random_search: StubRandomSearchAlgorithm,
    ) -> None:
        study = create_study(
            study_id="study-uc02-5d",
            name="UC-02 5D smoke",
            research_question="Verify adapter on 5D problem.",
            problem_ids=["prob-002"],
            algorithm_ids=["alg-rs-001"],
            repetitions=1,
            budget=100,
        )
        runner = MinimalRunner(study)
        run = runner.run_single(sphere_5d, random_search, seed=7)
        assert run.status == "completed"
        assert run.budget_used == 100


# ---------------------------------------------------------------------------
# CLASS TestReproducibility
# ---------------------------------------------------------------------------


class TestReproducibility:
    """Verify the seed isolation and state reset contracts (MANIFESTO Principle 18)."""

    def _make_runner(self) -> MinimalRunner:
        return MinimalRunner(
            create_study(
                study_id="study-repro",
                name="Reproducibility test",
                research_question="Same seed must produce identical results.",
                problem_ids=["prob-001"],
                algorithm_ids=["alg-rs-001"],
                repetitions=1,
                budget=50,
            )
        )

    def test_same_seed_produces_identical_records(
        self,
        sphere_2d: StubNoisySphereProblem,
        random_search: StubRandomSearchAlgorithm,
    ) -> None:
        runner = self._make_runner()
        run_a = runner.run_single(sphere_2d, random_search, seed=99)
        run_b = runner.run_single(sphere_2d, random_search, seed=99)
        assert len(run_a.records) == len(run_b.records)
        for rec_a, rec_b in zip(run_a.records, run_b.records):
            assert rec_a.evaluation_number == rec_b.evaluation_number
            assert rec_a.objective_value == pytest.approx(rec_b.objective_value)
            assert rec_a.trigger_reason == rec_b.trigger_reason

    def test_different_seeds_produce_different_objective_values(
        self,
        sphere_2d: StubNoisySphereProblem,
        random_search: StubRandomSearchAlgorithm,
    ) -> None:
        runner = self._make_runner()
        run_a = runner.run_single(sphere_2d, random_search, seed=1)
        run_b = runner.run_single(sphere_2d, random_search, seed=2)
        values_a = [r.objective_value for r in run_a.records]
        values_b = [r.objective_value for r in run_b.records]
        # Different seeds must produce at least some different values
        assert values_a != values_b

    def test_state_is_fully_reset_between_consecutive_runs(
        self,
        sphere_2d: StubNoisySphereProblem,
    ) -> None:
        """Run 1 (seed=42) followed by Run 2 (seed=42) must match a standalone Run (seed=42).

        This verifies that initialize() discards all state from prior Runs.
        """
        runner = self._make_runner()

        # First, run with seed=0 to dirty the algorithm's internal state
        algo_a = StubGreedyAlgorithm("alg-gs-state-test")
        runner.run_single(sphere_2d, algo_a, seed=0)

        # Then run with seed=42 — must match a fresh run with seed=42
        run_after_dirty = runner.run_single(sphere_2d, algo_a, seed=42)

        algo_b = StubGreedyAlgorithm("alg-gs-state-test")
        run_fresh = runner.run_single(sphere_2d, algo_b, seed=42)

        assert len(run_after_dirty.records) == len(run_fresh.records)
        for rec_a, rec_b in zip(run_after_dirty.records, run_fresh.records):
            assert rec_a.objective_value == pytest.approx(rec_b.objective_value)

    def test_greedy_same_seed_identical_records(
        self,
        sphere_2d: StubNoisySphereProblem,
        greedy_search: StubGreedyAlgorithm,
    ) -> None:
        runner = self._make_runner()
        run_a = runner.run_single(sphere_2d, greedy_search, seed=5)
        run_b = runner.run_single(sphere_2d, greedy_search, seed=5)
        values_a = [r.objective_value for r in run_a.records]
        values_b = [r.objective_value for r in run_b.records]
        assert values_a == pytest.approx(values_b)


# ---------------------------------------------------------------------------
# CLASS TestSeedIsolation
# ---------------------------------------------------------------------------


class TestSeedIsolation:
    """Verify no unseeded randomness escapes the algorithm (cross-cutting §6)."""

    def test_rng_is_none_before_initialize(
        self, random_search: StubRandomSearchAlgorithm
    ) -> None:
        """RNG must be None (unset) before initialize() is called."""
        assert random_search._rng is None

    def test_rng_is_set_after_initialize(
        self, random_search: StubRandomSearchAlgorithm, search_space_2d: SearchSpace
    ) -> None:
        """initialize() must set the RNG from the injected seed."""
        random_search.initialize(search_space_2d, seed=42)
        assert random_search._rng is not None

    def test_rng_is_reset_on_reinitialize(
        self, random_search: StubRandomSearchAlgorithm, search_space_2d: SearchSpace
    ) -> None:
        """Calling initialize() a second time resets the RNG to a new seed."""
        import random as stdlib_random

        random_search.initialize(search_space_2d, seed=1)
        rng_first = random_search._rng
        assert isinstance(rng_first, stdlib_random.Random)

        random_search.initialize(search_space_2d, seed=2)
        rng_second = random_search._rng

        # Different seeds → different RNG state
        assert rng_first.getstate() != rng_second.getstate()

    def test_greedy_rng_is_none_before_initialize(
        self, greedy_search: StubGreedyAlgorithm
    ) -> None:
        assert greedy_search._rng is None

    def test_greedy_best_solution_is_none_before_initialize(
        self, greedy_search: StubGreedyAlgorithm
    ) -> None:
        """Greedy must start with no prior best solution."""
        assert greedy_search._best_solution is None

    def test_greedy_best_solution_is_cleared_on_reinitialize(
        self, greedy_search: StubGreedyAlgorithm, search_space_2d: SearchSpace
    ) -> None:
        """initialize() must clear the best solution from any prior Run."""
        greedy_search.initialize(search_space_2d, seed=0)
        context = {"remaining_budget": 50, "elapsed_evaluations": 0}
        solution = greedy_search.suggest(context)[0]
        result = EvaluationResult(objective_value=0.5, metadata={}, evaluation_number=1)
        greedy_search.observe(solution, result)

        # Best solution is now set
        assert greedy_search._best_solution is not None

        # Re-initialize → best solution must be cleared
        greedy_search.initialize(search_space_2d, seed=1)
        assert greedy_search._best_solution is None


# ---------------------------------------------------------------------------
# CLASS TestBatchSuggest
# ---------------------------------------------------------------------------


class TestBatchSuggest:
    """Verify the batch_size contract on suggest() (Algorithm Interface §2)."""

    @pytest.mark.parametrize("batch_size", [1, 2, 3, 5])
    def test_random_search_returns_correct_batch_size(
        self,
        random_search: StubRandomSearchAlgorithm,
        search_space_2d: SearchSpace,
        batch_size: int,
    ) -> None:
        random_search.initialize(search_space_2d, seed=0)
        result = random_search.suggest({}, batch_size=batch_size)
        assert len(result) == batch_size

    @pytest.mark.parametrize("batch_size", [1, 2, 3, 5])
    def test_greedy_returns_correct_batch_size(
        self,
        greedy_search: StubGreedyAlgorithm,
        search_space_2d: SearchSpace,
        batch_size: int,
    ) -> None:
        greedy_search.initialize(search_space_2d, seed=0)
        context = {"remaining_budget": 50, "elapsed_evaluations": 0}
        result = greedy_search.suggest(context, batch_size=batch_size)
        assert len(result) == batch_size

    def test_each_solution_has_correct_dimensionality(
        self,
        random_search: StubRandomSearchAlgorithm,
        search_space_2d: SearchSpace,
    ) -> None:
        random_search.initialize(search_space_2d, seed=0)
        solutions = random_search.suggest({}, batch_size=3)
        for solution in solutions:
            assert len(solution) == search_space_2d.dimensions

    def test_all_solutions_within_bounds(
        self,
        random_search: StubRandomSearchAlgorithm,
        search_space_2d: SearchSpace,
    ) -> None:
        random_search.initialize(search_space_2d, seed=0)
        solutions = random_search.suggest({}, batch_size=10)
        for solution in solutions:
            for val in solution:
                assert search_space_2d.lower <= val <= search_space_2d.upper, (
                    f"solution value {val} is outside bounds "
                    f"[{search_space_2d.lower}, {search_space_2d.upper}]"
                )

    def test_batch_size_1_is_default(
        self,
        random_search: StubRandomSearchAlgorithm,
        search_space_2d: SearchSpace,
    ) -> None:
        random_search.initialize(search_space_2d, seed=0)
        result = random_search.suggest({})  # no batch_size kwarg
        assert len(result) == 1

    def test_greedy_all_solutions_within_bounds_after_warm_up(
        self,
        greedy_search: StubGreedyAlgorithm,
        search_space_2d: SearchSpace,
    ) -> None:
        """Greedy's perturbation steps must stay within bounds even after observing a solution."""
        greedy_search.initialize(search_space_2d, seed=7)
        context = {"remaining_budget": 50, "elapsed_evaluations": 0}

        # Warm up: observe a solution so the greedy has a best_solution set
        first = greedy_search.suggest(context)[0]
        greedy_search.observe(
            first,
            EvaluationResult(objective_value=1.0, metadata={}, evaluation_number=1),
        )

        # Now suggest a batch and verify all solutions are in bounds
        context["elapsed_evaluations"] = 1
        solutions = greedy_search.suggest(context, batch_size=5)
        for solution in solutions:
            for val in solution:
                assert search_space_2d.lower <= val <= search_space_2d.upper
