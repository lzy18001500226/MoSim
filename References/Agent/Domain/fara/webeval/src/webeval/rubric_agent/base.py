"""Minimal Agent / VerifierAgent / AgentConfig base classes.

Only the config-plumbing surface needed by
:class:`.mm_rubric_agent.MMRubricAgent` in evaluation mode
(``_extract_input_from_datapoint`` + ``_generate_reply`` +
``_wrap_result``) is kept. No RunContext / Environment is instantiated.
"""

from __future__ import annotations

from abc import ABC
from typing import Any

from pydantic import BaseModel, ConfigDict


class AgentConfig(BaseModel):
    """Base configuration for agents."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    name: str = "agent"
    client: Any = None
    metadata: dict[str, Any] = {}


class Agent(ABC):
    """Trimmed Agent base — holds config, no run-context plumbing."""

    def __init__(
        self, config: AgentConfig | dict[str, Any] | None = None, **kwargs: Any
    ):
        if config is None:
            config = self._get_config_class().model_validate(kwargs)
        elif isinstance(config, dict):
            config = self._get_config_class().model_validate(config)
        self.config = config
        self._initialized = False

    @classmethod
    def _get_config_class(cls) -> type[AgentConfig]:
        return AgentConfig

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def client(self) -> Any:
        return self.config.client


class VerifierAgent(Agent):
    """Marker base for verification agents."""


class RunContext:  # noqa: D401 — stub for type-hint compatibility
    """Stub; the rubric agent's ``run`` method references this class but
    the evaluation path invokes ``_generate_reply`` directly and never
    constructs a real RunContext."""

    data_point: Any = None
    output_dir: Any = None
