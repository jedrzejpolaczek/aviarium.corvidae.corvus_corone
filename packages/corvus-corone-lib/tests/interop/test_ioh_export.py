"""Interoperability tests for IOHExporter (REF-TASK-0007).

Acceptance criteria verified here
----------------------------------
AC-1  data-format.md §4.2 IOHprofiler mapping exists (documentation, not tested here).
AC-2  Performance Records export to .dat format that is parseable by IOHanalyzer.
AC-3  Sidecar .json stores fields not supported by .dat format (seed, run_id).
AC-4  Round-trip: exported evaluation_number and raw_y values match PerformanceRecord data.

These tests do NOT require IOHanalyzer or the ioh Python package. They verify the
format contract by parsing the produced files with Python stdlib only (json, re).

References
----------
Interface contract : docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md §4.2
Exporter           : corvus_corone/export/ioh_exporter.py
Stubs              : tests/e2e/_stubs.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.e2e._stubs import (
    ExperimentRecord,
    MinimalRunner,
    StubGreedyAlgorithm,
    StubNoisySphereProblem,
    StubRandomSearchAlgorithm,
    create_study,
)

from corvus_corone.export.ioh_exporter import AlgorithmMeta, IOHExporter, ProblemMeta

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def small_experiment() -> ExperimentRecord:
    """1 problem × 1 algorithm × 3 repetitions, budget=20."""
    study = create_study(
        study_id="study-ioh-test",
        name="IOH export test",
        research_question="Test fixture for IOH export.",
        problem_ids=["prob-001"],
        algorithm_ids=["alg-001"],
        repetitions=3,
        budget=20,
    )
    sphere = StubNoisySphereProblem("prob-001", dim=2, budget=20, noise_std=0.05)
    alg = StubRandomSearchAlgorithm("alg-001")
    runner = MinimalRunner(study)
    return runner.run_study(
        problems={"prob-001": sphere},
        algorithms={"alg-001": alg},
    )


@pytest.fixture
def two_alg_experiment() -> ExperimentRecord:
    """1 problem × 2 algorithms × 2 repetitions."""
    study = create_study(
        study_id="study-ioh-two-alg",
        name="Two-algorithm IOH export test",
        research_question="Test fixture for multi-algorithm IOH export.",
        problem_ids=["prob-001"],
        algorithm_ids=["alg-001", "alg-002"],
        repetitions=2,
        budget=20,
    )
    sphere = StubNoisySphereProblem("prob-001", dim=2, budget=20, noise_std=0.05)
    runner = MinimalRunner(study)
    return runner.run_study(
        problems={"prob-001": sphere},
        algorithms={
            "alg-001": StubRandomSearchAlgorithm("alg-001"),
            "alg-002": StubGreedyAlgorithm("alg-002"),
        },
    )


PROB_META = {
    "prob-001": ProblemMeta(func_id=1, func_name="NoisySphere2D", dimensions=2),
}
ALG_META = {
    "alg-001": AlgorithmMeta(name="RandomSearch", info="uniform random baseline"),
    "alg-002": AlgorithmMeta(name="GreedySearch", info="greedy perturbation"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_dat(dat_path: Path) -> list[list[tuple[int, float]]]:
    """Parse a .dat file into a list of runs.

    Returns a list of runs; each run is a list of (evaluations, raw_y) tuples.
    Run boundaries are the header lines (first token is non-numeric).

    Matches IOHanalyzer's run-boundary detection logic.
    """
    runs: list[list[tuple[int, float]]] = []
    current: list[tuple[int, float]] = []
    for line in dat_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        first_token = line.split()[0]
        try:
            int(first_token)
        except ValueError:
            # Non-numeric first token → header / run boundary
            if current:
                runs.append(current)
            current = []
            continue
        evals, raw_y = line.split()
        current.append((int(evals), float(raw_y)))
    if current:
        runs.append(current)
    return runs


# ---------------------------------------------------------------------------
# AC-2: .dat file format correctness
# ---------------------------------------------------------------------------


class TestDatFileFormat:
    def test_dat_file_exists(self, small_experiment: ExperimentRecord, tmp_path: Path) -> None:
        """AC-2: .dat file is created at the expected path."""
        IOHExporter().export(
            small_experiment,
            tmp_path,
            problem_meta=PROB_META,
            algorithm_meta=ALG_META,
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        assert dat.exists(), f".dat file not found at {dat}"

    def test_dat_starts_with_header(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-2: first line of .dat is the column header (IOH run-boundary marker)."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        first_line = dat.read_text(encoding="utf-8").splitlines()[0]
        assert first_line == "evaluations raw_y"

    def test_dat_data_rows_are_numeric(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-2: all non-header rows parse as (int, float) without error."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        for line in dat.read_text(encoding="utf-8").splitlines():
            tokens = line.split()
            if not tokens or tokens[0] == "evaluations":
                continue
            assert len(tokens) == 2, f"Expected 2 columns, got {len(tokens)}: {line!r}"
            int(tokens[0])  # must not raise
            float(tokens[1])  # must not raise

    def test_dat_contains_correct_run_count(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-2: .dat encodes exactly repetitions=3 runs (3 header-separated blocks)."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        runs = _parse_dat(dat)
        assert len(runs) == 3

    def test_dat_evaluation_numbers_are_positive_and_monotone(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-2: within each run, evaluation_number is strictly increasing."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        for run_rows in _parse_dat(dat):
            evals = [e for e, _ in run_rows]
            assert evals == sorted(evals), "evaluation_number not monotonically increasing"
            assert all(e > 0 for e in evals), "evaluation_number must be positive"

    def test_dat_raw_y_is_monotone_non_increasing_for_minimization(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-2: raw_y (best_so_far) is non-increasing within each minimization run."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        for run_rows in _parse_dat(dat):
            ys = [y for _, y in run_rows]
            for i in range(1, len(ys)):
                assert ys[i] <= ys[i - 1] + 1e-12, (
                    f"raw_y not non-increasing at index {i}: {ys[i - 1]} → {ys[i]}"
                )


# ---------------------------------------------------------------------------
# AC-3: .json sidecar correctness
# ---------------------------------------------------------------------------


class TestJsonSidecar:
    def test_sidecar_exists(self, small_experiment: ExperimentRecord, tmp_path: Path) -> None:
        """AC-3: .json sidecar is created at the expected path."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        sidecar = tmp_path / "alg-001" / "IOHprofiler_f1_NoisySphere2D.json"
        assert sidecar.exists()

    def test_sidecar_is_valid_json(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-3: .json sidecar parses without error."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        sidecar = tmp_path / "alg-001" / "IOHprofiler_f1_NoisySphere2D.json"
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_sidecar_required_fields(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-3: sidecar contains all IOHprofiler required top-level fields."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        data = json.loads((tmp_path / "alg-001" / "IOHprofiler_f1_NoisySphere2D.json").read_text())
        for field in (
            "version",
            "function_id",
            "function_name",
            "maximization",
            "algorithm",
            "attributes",
            "scenarios",
        ):
            assert field in data, f"Required field '{field}' missing from sidecar"

    def test_sidecar_stores_seed(self, small_experiment: ExperimentRecord, tmp_path: Path) -> None:
        """AC-3: seed is stored in sidecar (not expressible in .dat format)."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        data = json.loads((tmp_path / "alg-001" / "IOHprofiler_f1_NoisySphere2D.json").read_text())
        runs = data["scenarios"][0]["runs"]
        for run_entry in runs:
            assert "corvus_seed" in run_entry, "corvus_seed missing from sidecar run entry"
            assert isinstance(run_entry["corvus_seed"], int)

    def test_sidecar_stores_run_id(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-3: corvus_run_id is preserved in sidecar."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        data = json.loads((tmp_path / "alg-001" / "IOHprofiler_f1_NoisySphere2D.json").read_text())
        for run_entry in data["scenarios"][0]["runs"]:
            assert "corvus_run_id" in run_entry

    def test_sidecar_algorithm_name(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-3: algorithm.name in sidecar matches supplied AlgorithmMeta."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        data = json.loads((tmp_path / "alg-001" / "IOHprofiler_f1_NoisySphere2D.json").read_text())
        assert data["algorithm"]["name"] == "RandomSearch"

    def test_sidecar_run_count_matches_experiment(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-3: sidecar run count equals the number of completed runs."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        data = json.loads((tmp_path / "alg-001" / "IOHprofiler_f1_NoisySphere2D.json").read_text())
        completed = sum(1 for r in small_experiment.runs if r.status != "failed")
        assert len(data["scenarios"][0]["runs"]) == completed


# ---------------------------------------------------------------------------
# AC-4: Round-trip fidelity
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_evaluation_numbers_match_records(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-4: evaluation_numbers in .dat match PerformanceRecord.evaluation_number."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        exported_runs = _parse_dat(dat)

        source_runs = [r for r in small_experiment.runs if r.status != "failed"]
        assert len(exported_runs) == len(source_runs)

        for exported, source_run in zip(exported_runs, source_runs):
            exported_evals = [e for e, _ in exported]
            source_evals = [rec.evaluation_number for rec in source_run.records]
            assert exported_evals == source_evals, (
                f"evaluation_number mismatch for run {source_run.run_id}"
            )

    def test_raw_y_matches_best_so_far(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-4: raw_y in .dat matches PerformanceRecord.best_so_far (or objective_value)."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        exported_runs = _parse_dat(dat)

        source_runs = [r for r in small_experiment.runs if r.status != "failed"]

        for exported, source_run in zip(exported_runs, source_runs):
            for (_, raw_y), rec in zip(exported, source_run.records):
                expected = getattr(rec, "best_so_far", rec.objective_value)
                assert abs(raw_y - expected) < 1e-8, (
                    f"raw_y mismatch at eval {rec.evaluation_number}: "
                    f"exported={raw_y}, expected={expected}"
                )

    def test_best_y_in_sidecar_matches_dat(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """AC-4: best.y in sidecar matches the minimum raw_y in the .dat run."""
        IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        sidecar_data = json.loads(
            (tmp_path / "alg-001" / "IOHprofiler_f1_NoisySphere2D.json").read_text()
        )
        exported_runs = _parse_dat(dat)
        sidecar_runs = sidecar_data["scenarios"][0]["runs"]

        assert len(exported_runs) == len(sidecar_runs)
        for exported, sidecar_run in zip(exported_runs, sidecar_runs):
            ys = [y for _, y in exported]
            expected_best = min(ys)  # minimization
            assert abs(sidecar_run["best"]["y"] - expected_best) < 1e-8


# ---------------------------------------------------------------------------
# Multi-algorithm layout
# ---------------------------------------------------------------------------


class TestMultiAlgorithmLayout:
    def test_separate_folders_per_algorithm(
        self, two_alg_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """Each algorithm produces its own subfolder under output_dir."""
        IOHExporter().export(
            two_alg_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        assert (tmp_path / "alg-001").is_dir()
        assert (tmp_path / "alg-002").is_dir()

    def test_dat_files_independent_per_algorithm(
        self, two_alg_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """Each algorithm .dat file contains only that algorithm's runs."""
        IOHExporter().export(
            two_alg_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        dat1 = tmp_path / "alg-001" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"
        dat2 = tmp_path / "alg-002" / "data_f1_NoisySphere2D" / "IOHprofiler_f1_DIM2.dat"

        runs1 = _parse_dat(dat1)
        runs2 = _parse_dat(dat2)

        # 2 repetitions each
        assert len(runs1) == 2
        assert len(runs2) == 2
        # Files are distinct
        assert dat1.read_text() != dat2.read_text()


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


class TestManifest:
    def test_manifest_is_non_empty(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """NFR-INTEROP-01: manifest is never empty."""
        manifest = IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        assert len(manifest) > 0

    def test_manifest_entries_have_required_keys(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """Each manifest entry has key, severity, condition, description."""
        manifest = IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        for entry in manifest:
            for field in ("key", "severity", "condition", "description"):
                assert field in entry, f"Manifest entry missing '{field}': {entry}"

    def test_loss_ioh_03_always_present(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """LOSS-IOH-03 (elapsed_time not exported) is always in the manifest."""
        manifest = IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        keys = [e["key"] for e in manifest]
        assert "LOSS-IOH-03" in keys

    def test_loss_ioh_08_always_present(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """LOSS-IOH-08 (seed in sidecar only) is always in the manifest."""
        manifest = IOHExporter().export(
            small_experiment, tmp_path, problem_meta=PROB_META, algorithm_meta=ALG_META
        )
        keys = [e["key"] for e in manifest]
        assert "LOSS-IOH-08" in keys

    def test_missing_metadata_triggers_warning(
        self, small_experiment: ExperimentRecord, tmp_path: Path
    ) -> None:
        """LOSS-IOH-06 fires when problem_meta is not supplied."""
        manifest = IOHExporter().export(small_experiment, tmp_path)
        keys = [e["key"] for e in manifest]
        assert "LOSS-IOH-06" in keys
