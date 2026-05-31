"""Stage 1: Parallel Reasoning — generate K independent reasoning trajectories."""

import asyncio
import logging
from typing import List

from .agent.openai_compatible import OpenAICompatibleAgent
from .config import HeavySkillConfig
from .utils import is_repetitive

logger = logging.getLogger(__name__)


async def parallel_reason(
    query: str,
    config: HeavySkillConfig,
    agent: OpenAICompatibleAgent = None,
) -> List[str]:
    """
    Generate K parallel reasoning trajectories for the given query.

    Args:
        query: The user query / problem statement.
        config: HeavySkill configuration.
        agent: Optional pre-initialized agent. Created from config if None.

    Returns:
        List of K reasoning trajectory strings.
    """
    if agent is None:
        agent = OpenAICompatibleAgent(
            model_name=config.model_name,
            api_base=config.api_base,
            api_key=config.api_key,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    logger.info(
        "Starting parallel reasoning: K=%d, model=%s", config.reason_k, config.model_name
    )

    trajectories = await agent.generate(
        prompt=query,
        n=config.reason_k,
        temperature=config.reason_temperature,
        max_tokens=config.reason_max_tokens,
        top_p=config.reason_top_p,
    )

    # Filter out repetitive / degenerate responses
    valid = []
    for traj in trajectories:
        if is_repetitive(traj):
            logger.warning("Filtered repetitive trajectory (length=%d)", len(traj))
            continue
        valid.append(traj)

    if not valid:
        logger.warning("All trajectories were repetitive, keeping originals")
        valid = trajectories

    logger.info(
        "Parallel reasoning complete: %d/%d valid trajectories",
        len(valid),
        len(trajectories),
    )
    return valid
