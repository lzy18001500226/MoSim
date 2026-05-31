from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HeavySkillConfig:
    # Model
    model_name: str = "default"
    api_base: str = "http://localhost:8080"
    api_key: str = "EMPTY"

    # Stage 1: Parallel Reasoning
    reason_k: int = 8
    reason_temperature: float = 1.0
    reason_max_tokens: int = 32768
    reason_top_p: float = 0.95

    # Stage 2: Sequential Deliberation
    summary_k: int = 4
    summary_temperature: float = 0.7
    summary_max_tokens: int = 32768
    summary_model_name: Optional[str] = None
    summary_api_base: Optional[str] = None
    summary_api_key: Optional[str] = None

    # Prompt
    prompt_type: str = "general"
    language: str = "en"

    # Pipeline
    iterations: int = 1
    max_trajectory_tokens: int = 80000

    # Trajectory selection
    trajectory_component: str = "answer_clipped"
    think_start_tag: str = "<think>"
    think_end_tag: str = "</think>"

    # Network
    timeout: float = 600.0
    max_retries: int = 3

    @property
    def summary_model(self) -> str:
        return self.summary_model_name or self.model_name

    @property
    def summary_base(self) -> str:
        return self.summary_api_base or self.api_base

    @property
    def summary_key(self) -> str:
        return self.summary_api_key or self.api_key
