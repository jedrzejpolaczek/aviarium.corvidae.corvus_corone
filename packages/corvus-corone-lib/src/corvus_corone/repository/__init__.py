"""Repository storage abstraction layer.

Provides the abstract interfaces and the in-memory V1 implementation.

All persistent state access in corvus_corone flows through these interfaces.
No library code outside this package may call file I/O directly — all storage
operations must go through a :class:`RepositoryFactory` implementation.

References
----------
→ docs/03-technical-contracts/02-interface-contracts/06-repository-interface.md
→ docs/02-design/02-architecture/01-adr/adr-001-library-with-server-ready-data-layer.md
"""

from corvus_corone.repository.interfaces import (
    AlgorithmRepository,
    ExperimentRepository,
    ProblemRepository,
    RepositoryFactory,
    ReportRepository,
    ResultAggregateRepository,
    RunRepository,
    StudyRepository,
)
from corvus_corone.repository.in_memory import InMemoryRepositoryFactory

__all__ = [
    "ProblemRepository",
    "AlgorithmRepository",
    "StudyRepository",
    "ExperimentRepository",
    "RunRepository",
    "ResultAggregateRepository",
    "ReportRepository",
    "RepositoryFactory",
    "InMemoryRepositoryFactory",
]
