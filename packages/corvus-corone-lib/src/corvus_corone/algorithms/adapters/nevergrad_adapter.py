"""Generic adapter wrapping any Nevergrad optimizer behind the Corvus Corone
Algorithm Interface (§2).

Reference
---------
Interface contract : docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md
Data format        : docs/03-technical-contracts/01-data-format/03-algorithm-instance.md
Interop mapping    : docs/03-technical-contracts/01-data-format/11-interoperability-mappings.md §4.3
Tutorial           : docs/06-tutorials/03-nevergrad-adapter.md

Requires
--------
    pip install nevergrad

Nevergrad is an optional dependency. The import is deferred to initialize() so
that importing this module does not fail when nevergrad is not installed.
"""

from __future__ import annotations

from collections import deque
from typing import Any


class NevergradAdapter:
    """Wraps any Nevergrad optimizer behind the Corvus Corone Algorithm Interface.

    One instance of this class corresponds to one Algorithm Instance in the
    Algorithm Registry. The underlying Nevergrad optimizer is created fresh in
    ``initialize()`` for every Run so that no state leaks between Runs
    (§2 isolation requirement).

    Parameters
    ----------
    algorithm_id:
        Opaque string used as the Algorithm Instance ID in the registry.
    optimizer_name:
        Name of the Nevergrad optimizer as registered in ``ng.optimizers.registry``
        (e.g. ``"NGOpt"``, ``"TwoPointsDE"``, ``"CMA"``). Call
        ``sorted(ng.optimizers.registry.keys())`` to list all available names.
    budget:
        Total evaluation budget passed to the Nevergrad constructor. Must match
        the Study's budget allocation so that budget-adaptive optimizers (e.g.
        NGOpt) can tune their strategy correctly.
    hyperparameters:
        Optional dict of additional keyword arguments forwarded to the Nevergrad
        optimizer constructor (optimizer-specific). Stored verbatim in the
        Algorithm Instance metadata.
    configuration_justification:
        Mandatory non-empty string explaining why this optimizer and
        hyperparameter combination was chosen. Required for registration (UC-02 F3).
    objective:
        ``"minimize"`` (default) or ``"maximize"``. Nevergrad always minimizes
        internally; for maximization problems the loss passed to ``tell()`` is
        negated automatically.
    """

    def __init__(
        self,
        algorithm_id: str,
        optimizer_name: str,
        budget: int,
        hyperparameters: dict[str, Any] | None = None,
        configuration_justification: str = "",
        objective: str = "minimize",
    ) -> None:
        self._id = algorithm_id
        self._optimizer_name = optimizer_name
        self._budget = budget
        self._hyperparameters: dict[str, Any] = hyperparameters or {}
        self._configuration_justification = configuration_justification
        self._objective = objective

        # Initialised in initialize(); None between Runs.
        self._optimizer: Any | None = None
        self._variable_order: list[str] = []
        self._pending: deque[Any] = deque()

    # ── Required: called once by Runner before every Run ─────────────────────

    def initialize(self, search_space: Any, seed: int) -> None:
        """Build a fresh Nevergrad optimizer from a Corvus SearchSpace.

        Translates each variable in ``search_space.variables`` to the
        corresponding ``ng.p.*`` class:

        ============  ============================================
        Corvus type   Nevergrad class
        ============  ============================================
        continuous    ``ng.p.Scalar(lower=lo, upper=hi)``
        integer       ``ng.p.Scalar(lower=lo, upper=hi).set_integer_casting()``
        categorical   ``ng.p.Choice(choices)``
        ============  ============================================

        Seed isolation is achieved via ``parametrization.random_state.seed(seed)``
        before the optimizer is constructed, satisfying the §6 randomness contract.
        """
        try:
            import nevergrad as ng
        except ImportError as exc:
            raise ImportError(
                "nevergrad is required for NevergradAdapter. Install it with: pip install nevergrad"
            ) from exc

        params: dict[str, Any] = {}
        for var in search_space.variables:
            vtype = var["type"]
            name = var["name"]
            if vtype == "continuous":
                lo, hi = var["bounds"]
                params[name] = ng.p.Scalar(lower=float(lo), upper=float(hi))
            elif vtype == "integer":
                lo, hi = var["bounds"]
                params[name] = ng.p.Scalar(lower=float(lo), upper=float(hi)).set_integer_casting()
            elif vtype == "categorical":
                params[name] = ng.p.Choice(var["choices"])
            else:
                raise ValueError(
                    f"Variable '{name}' has unsupported type '{vtype}'. "
                    f"NevergradAdapter supports: {self.get_supported_variable_types()}"
                )

        parametrization = ng.p.Dict(**params)
        parametrization.random_state.seed(seed)  # §6 seed isolation

        self._optimizer = ng.optimizers.registry[self._optimizer_name](
            parametrization=parametrization,
            budget=self._budget,
            **self._hyperparameters,
        )
        self._variable_order = [v["name"] for v in search_space.variables]
        self._pending = deque()

    # ── Required: ask step ────────────────────────────────────────────────────

    def suggest(self, context: Any, batch_size: int = 1) -> list[list[Any]]:
        """Ask Nevergrad for ``batch_size`` candidate solutions.

        Each Nevergrad candidate is queued in ``_pending`` for FIFO pairing with
        the subsequent ``observe()`` call. The candidate's ``kwargs`` dict (keyed
        by variable name) is converted to an ordered list matching
        ``search_space.variables`` order.
        """
        solutions: list[list[Any]] = []
        for _ in range(batch_size):
            candidate = self._optimizer.ask()
            self._pending.append(candidate)
            solutions.append([candidate.kwargs[name] for name in self._variable_order])
        return solutions

    # ── Required: tell step ───────────────────────────────────────────────────

    def observe(self, solution: Any, result: Any) -> None:
        """Tell Nevergrad the outcome of the oldest pending candidate.

        Candidates are matched FIFO: the candidate dequeued here is the one
        produced by the earliest ``suggest()`` call that has not yet been
        observed. The Runner guarantees this ordering for ``batch_size=1``;
        users running parallel evaluations must preserve ordering themselves.

        For maximization problems (``objective="maximize"``) the loss is negated
        before the ``tell()`` call because Nevergrad always minimizes internally.
        """
        candidate = self._pending.popleft()
        loss = result.objective_value if self._objective == "minimize" else -result.objective_value
        self._optimizer.tell(candidate, float(loss))

    # ── Required: variable type declaration ──────────────────────────────────

    def get_supported_variable_types(self) -> list[str]:
        """All three Corvus variable types are supported via ng.p parametrization."""
        return ["continuous", "integer", "categorical"]

    # ── Required: provenance record ───────────────────────────────────────────

    def get_metadata(self) -> dict[str, Any]:
        """Return the Algorithm Instance record for registry storage."""
        try:
            import nevergrad

            ng_version = nevergrad.__version__
        except ImportError:
            ng_version = "unknown"

        assumptions = ["objective is real-valued scalar", "no gradient available"]
        if self._objective == "maximize":
            assumptions.append("loss negated internally for maximization (Nevergrad minimizes)")

        return {
            "id": self._id,
            "name": f"Nevergrad-{self._optimizer_name}",
            "version": "1.0.0",
            "algorithm_family": self._optimizer_name,
            "hyperparameters": {
                "optimizer_name": self._optimizer_name,
                "budget": self._budget,
                **self._hyperparameters,
            },
            "configuration_justification": self._configuration_justification,
            "code_reference": f"nevergrad=={ng_version}",
            "language": "python",
            "framework": "nevergrad",
            "framework_version": ng_version,
            "known_assumptions": assumptions,
            "contributed_by": "corvus-corone",
            "supported_variable_types": self.get_supported_variable_types(),
        }
