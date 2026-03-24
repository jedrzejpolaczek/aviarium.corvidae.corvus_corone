"""corvus_corone.algorithms.adapters — Thin adapters wrapping third-party optimizers.

Each adapter translates between the Corvus Corone Algorithm Interface (§2,
docs/03-technical-contracts/02-interface-contracts/03-algorithm-interface.md) and
the native API of a third-party library. Adapters are optional: the third-party
library must be installed separately and is never a hard dependency of the core.

Available adapters
------------------
NevergradAdapter  — wraps any optimizer registered in ng.optimizers.registry.
                    Requires: nevergrad (pip install nevergrad)
"""
