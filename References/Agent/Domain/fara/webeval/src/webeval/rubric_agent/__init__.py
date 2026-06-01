"""Universal Verifier (MMRubricAgent).

Self-contained multimodal rubric verification pipeline used by the fara
``webeval`` package to score agent trajectories. Uses the
:class:`webeval.oai_clients.ChatCompletionClient` interface.
"""

from .mm_rubric_agent import MMRubricAgent, MMRubricAgentConfig
from .data_point import (
    Action,
    ComputerObservation,
    DataPoint,
    DataPointMetadata,
    MMRubricOutcomeResult,
    MMRubricResult,
    Outcome,
    SolverLog,
    SolverStatus,
    Task,
    UserMessage,
    UserMessageType,
    VerificationResult,
)

__all__ = [
    "MMRubricAgent",
    "MMRubricAgentConfig",
    "DataPoint",
    "DataPointMetadata",
    "Task",
    "SolverLog",
    "SolverStatus",
    "Outcome",
    "Action",
    "ComputerObservation",
    "UserMessage",
    "UserMessageType",
    "VerificationResult",
    "MMRubricResult",
    "MMRubricOutcomeResult",
]
