"""Export Corvus Corone ExperimentRecords to IOHprofiler v0.3.3+ format.

Reference
---------
Format spec   : docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md §4.2
IOHprofiler   : https://iohprofiler.github.io/
IOHexperimenter: https://github.com/IOHprofiler/IOHexperimenter

Output layout
-------------
For each (algorithm_id, problem_id) combination the exporter writes:

    <output_dir>/
    └── <algorithm_id>/
        ├── IOHprofiler_f<func_id>_<func_name>.json      ← sidecar (all dimensions)
        └── data_f<func_id>_<func_name>/
            └── IOHprofiler_f<func_id>_DIM<dim>.dat      ← performance log

All runs for the same (algorithm, problem, dimension) are concatenated into
one .dat file, separated by a repeated header line (run boundary marker).

Format version
--------------
v0.3.3+ ("new" format): unquoted column headers, JSON sidecar.
IOHanalyzer auto-detects this format when the .json sidecar is present.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Public dataclass for caller-supplied metadata
# ---------------------------------------------------------------------------


@dataclass
class ProblemMeta:
    """Caller-supplied metadata for one problem.

    Parameters
    ----------
    func_id:
        Integer function ID used in filenames and the JSON sidecar.
        Must be unique across problems in the export.
    func_name:
        Human-readable function name; used in filenames (spaces replaced with _).
    dimensions:
        Number of search space dimensions.
    maximization:
        True if higher objective values are better; False for minimization.
    """

    func_id: int
    func_name: str
    dimensions: int
    maximization: bool = False


@dataclass
class AlgorithmMeta:
    """Caller-supplied metadata for one algorithm.

    Parameters
    ----------
    name:
        Algorithm name stored in the JSON sidecar ``algorithm.name`` field.
    info:
        Algorithm description stored in the JSON sidecar ``algorithm.info`` field.
    """

    name: str
    info: str = ""


# ---------------------------------------------------------------------------
# Exporter
# ---------------------------------------------------------------------------

_SAFE_NAME_RE = re.compile(r"[^\w\-]")


def _safe(name: str) -> str:
    """Replace characters unsafe for filenames with underscores."""
    return _SAFE_NAME_RE.sub("_", name)


class IOHExporter:
    """Export an ExperimentRecord to IOHprofiler v0.3.3+ .dat/.json format.

    Usage
    -----
    ::

        exporter = IOHExporter()
        manifest = exporter.export(
            experiment,
            output_dir="/tmp/ioh_results",
            problem_meta={
                "prob-001": ProblemMeta(func_id=1, func_name="NoisySphere2D", dimensions=2),
            },
            algorithm_meta={
                "alg-001": AlgorithmMeta(name="RandomSearch", info="uniform random"),
            },
        )

    Parameters not supplied in ``problem_meta`` / ``algorithm_meta`` are derived
    from the run IDs and flagged in the returned manifest.

    Returns
    -------
    list[dict]
        Information-loss manifest.  Each entry has keys:
        ``key`` (str), ``severity`` (str), ``condition`` (str), ``description`` (str).
        The list is never empty.
    """

    _DAT_HEADER = "evaluations raw_y"
    _IOHPROFILER_VERSION = "0.3.5"

    def export(
        self,
        experiment: Any,
        output_dir: Path | str,
        *,
        problem_meta: dict[str, ProblemMeta] | None = None,
        algorithm_meta: dict[str, AlgorithmMeta] | None = None,
    ) -> list[dict[str, str]]:
        """Write IOHprofiler files for all runs in ``experiment``.

        Parameters
        ----------
        experiment:
            An ExperimentRecord (or any object with ``.runs`` list of RunRecord).
        output_dir:
            Root directory.  Created if it does not exist.
        problem_meta:
            Mapping of problem_id → ProblemMeta.  Missing entries receive
            auto-generated defaults and produce LOSS-IOH-06 manifest items.
        algorithm_meta:
            Mapping of algorithm_id → AlgorithmMeta.  Missing entries receive
            auto-generated defaults and produce LOSS-IOH-07 manifest items.

        Returns
        -------
        list[dict[str, str]]
            Information-loss manifest.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        pm = problem_meta or {}
        am = algorithm_meta or {}

        # ── auto-generate missing metadata ──────────────────────────────────
        manifest: list[dict[str, str]] = []
        func_id_counter = [1]  # mutable counter for auto-assigned IDs

        def _get_problem_meta(pid: str) -> ProblemMeta:
            if pid not in pm:
                fid = func_id_counter[0]
                func_id_counter[0] += 1
                pm[pid] = ProblemMeta(
                    func_id=fid,
                    func_name=_safe(pid),
                    dimensions=0,  # unknown
                    maximization=False,
                )
                manifest.append(
                    {
                        "key": "LOSS-IOH-06",
                        "severity": "warning",
                        "condition": f"problem_id={pid!r} not in problem_meta",
                        "description": (
                            f"No ProblemMeta supplied for '{pid}'. "
                            "func_id auto-assigned; dimensions=0 (unknown). "
                            "Provide problem_meta to get correct DIM in filenames "
                            "and the JSON sidecar."
                        ),
                    }
                )
            return pm[pid]

        def _get_algorithm_meta(aid: str) -> AlgorithmMeta:
            if aid not in am:
                am[aid] = AlgorithmMeta(name=_safe(aid), info="")
                manifest.append(
                    {
                        "key": "LOSS-IOH-07",
                        "severity": "informational",
                        "condition": f"algorithm_id={aid!r} not in algorithm_meta",
                        "description": (
                            f"No AlgorithmMeta supplied for '{aid}'. "
                            "algorithm.name defaults to the algorithm_id string. "
                            "Provide algorithm_meta for a human-readable name."
                        ),
                    }
                )
            return am[aid]

        # ── group runs by (algorithm_id, problem_id) ────────────────────────
        # Nested dict: alg_id → prob_id → list[RunRecord]
        grouped: dict[str, dict[str, list[Any]]] = {}
        for run in experiment.runs:
            grouped.setdefault(run.algorithm_id, {}).setdefault(run.problem_id, []).append(run)

        # ── write files ─────────────────────────────────────────────────────
        has_maximization = False
        has_missing_solution = False
        has_failed_runs = False
        has_cap_reached = False

        for alg_id, prob_runs in grouped.items():
            alg_folder = output_dir / _safe(alg_id)
            alg_meta = _get_algorithm_meta(alg_id)

            # Collect JSON sidecar data across all problems for this algorithm
            sidecar: dict[str, Any] = {
                "version": self._IOHPROFILER_VERSION,
                "suite": "corvus_corone",
                "algorithm": {"name": alg_meta.name, "info": alg_meta.info},
                "attributes": ["evaluations", "raw_y"],
                "scenarios": [],
            }

            for prob_id, runs in prob_runs.items():
                pmeta = _get_problem_meta(prob_id)
                safe_name = _safe(pmeta.func_name)
                dim = pmeta.dimensions

                # JSON sidecar fields that vary per problem
                sidecar.setdefault("function_id", pmeta.func_id)
                sidecar.setdefault("function_name", pmeta.func_name)
                sidecar.setdefault("maximization", pmeta.maximization)
                if pmeta.maximization:
                    has_maximization = True

                # Directory and file paths
                data_subfolder = alg_folder / f"data_f{pmeta.func_id}_{safe_name}"
                data_subfolder.mkdir(parents=True, exist_ok=True)
                dat_path = data_subfolder / f"IOHprofiler_f{pmeta.func_id}_DIM{dim}.dat"

                # Collect per-run summaries for the JSON sidecar
                run_summaries: list[dict[str, Any]] = []

                with dat_path.open("w", encoding="utf-8") as fh:
                    for run in runs:
                        if run.status == "failed":
                            has_failed_runs = True
                            continue  # LOSS-IOH-05

                        # Write run-boundary header
                        fh.write(self._DAT_HEADER + "\n")

                        best_y = None
                        best_eval = None

                        for rec in run.records:
                            # Use best_so_far if available, fall back to objective_value
                            raw_y = getattr(rec, "best_so_far", rec.objective_value)

                            if (
                                best_y is None
                                or (pmeta.maximization and raw_y > best_y)
                                or (not pmeta.maximization and raw_y < best_y)
                            ):
                                best_y = raw_y
                                best_eval = rec.evaluation_number

                            fh.write(f"{rec.evaluation_number} {raw_y:.10f}\n")

                            if getattr(rec, "current_solution", None) is None:
                                has_missing_solution = True

                            if getattr(rec, "cap_reached_at_evaluation", None) is not None:
                                has_cap_reached = True

                        if run.cap_reached_at_evaluation is not None:
                            has_cap_reached = True

                        run_summaries.append(
                            {
                                "instance": 1,
                                "evals": run.budget_used,
                                "best": {
                                    "evals": best_eval,
                                    "y": best_y,
                                },
                                "corvus_seed": run.seed,
                                "corvus_run_id": run.id,
                            }
                        )

                sidecar["scenarios"].append(
                    {
                        "dimension": dim,
                        "path": str(dat_path.relative_to(alg_folder).as_posix()),
                        "runs": run_summaries,
                    }
                )

            # Write JSON sidecar for this algorithm (covers all its problems)
            # One sidecar per function; if there are multiple problems, each
            # gets its own sidecar.  Here we write once per (alg, prob) combo.
            for prob_id in prob_runs:
                pmeta = _get_problem_meta(prob_id)
                safe_name = _safe(pmeta.func_name)
                sidecar_path = alg_folder / f"IOHprofiler_f{pmeta.func_id}_{safe_name}.json"
                # Filter sidecar scenarios to this problem only
                prob_sidecar = {
                    **sidecar,
                    "function_id": pmeta.func_id,
                    "function_name": pmeta.func_name,
                    "maximization": pmeta.maximization,
                    "scenarios": [
                        s
                        for s in sidecar["scenarios"]
                        if s["path"].startswith(f"data_f{pmeta.func_id}_{safe_name}/")
                    ],
                }
                sidecar_path.write_text(json.dumps(prob_sidecar, indent=2), encoding="utf-8")

        # ── build manifest ───────────────────────────────────────────────────
        manifest.insert(
            0,
            {
                "key": "LOSS-IOH-03",
                "severity": "informational",
                "condition": "always",
                "description": (
                    "PerformanceRecord.elapsed_time has no IOHprofiler .dat equivalent "
                    "and is not exported. IOHanalyzer does not support wall-clock time."
                ),
            },
        )
        manifest.insert(
            1,
            {
                "key": "LOSS-IOH-04",
                "severity": "informational",
                "condition": "always",
                "description": (
                    "Corvus scheduled records (trigger_reason='scheduled') are included "
                    "in the .dat file alongside improvement records. IOHprofiler's default "
                    "OnImprovement trigger would write fewer rows. IOHanalyzer still "
                    "computes correct ERT from the exported data."
                ),
            },
        )
        manifest.insert(
            2,
            {
                "key": "LOSS-IOH-08",
                "severity": "informational",
                "condition": "always",
                "description": (
                    "Run.seed is stored in the JSON sidecar as 'corvus_seed' "
                    "(non-standard field). The .dat format has no seed column. "
                    "Reproducibility requires the Corvus ExperimentRecord."
                ),
            },
        )

        if has_maximization:
            manifest.append(
                {
                    "key": "LOSS-IOH-01",
                    "severity": "informational",
                    "condition": "ProblemMeta.maximization=True",
                    "description": (
                        "Raw objective values are stored as-is (not negated). "
                        "The 'maximization' flag in the JSON sidecar tells IOHanalyzer "
                        "to orient ECDF curves correctly. "
                        "Verify the sidecar maximization field before uploading."
                    ),
                }
            )

        if has_missing_solution:
            manifest.append(
                {
                    "key": "LOSS-IOH-02",
                    "severity": "informational",
                    "condition": "PerformanceRecord.current_solution absent",
                    "description": (
                        "Decision variable columns (x0, x1, …) not exported: "
                        "PerformanceRecord.current_solution is absent. "
                        "IOHanalyzer decision-space scatter plots are unavailable."
                    ),
                }
            )

        if has_failed_runs:
            manifest.append(
                {
                    "key": "LOSS-IOH-05",
                    "severity": "informational",
                    "condition": "Run.status='failed'",
                    "description": (
                        "Failed runs are excluded from the .dat export. "
                        "The JSON sidecar run count will be lower than "
                        "Study.experimental_design.repetitions."
                    ),
                }
            )

        if has_cap_reached:
            manifest.append(
                {
                    "key": "LOSS-IOH-09",
                    "severity": "warning",
                    "condition": "Run.cap_reached_at_evaluation is not None",
                    "description": (
                        "One or more runs hit max_records_per_run. Improvement records "
                        "stop at cap_reached_at_evaluation; the .dat trace is truncated "
                        "for those runs. ERT may be underestimated."
                    ),
                }
            )

        return manifest
