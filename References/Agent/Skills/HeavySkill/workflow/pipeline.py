"""HeavySkill Pipeline — orchestrates parallel reasoning + sequential deliberation."""

import logging
from dataclasses import dataclass
from typing import List, Optional

from .agent.openai_compatible import OpenAICompatibleAgent
from .config import HeavySkillConfig
from .memory_cache import MemoryCache
from .parallel_reasoning import parallel_reason
from .sequential_deliberation import deliberate

logger = logging.getLogger(__name__)


@dataclass
class HeavySkillResult:
    query: str
    trajectories: List[str]
    summaries: List[str]
    iterations_done: int
    final_answer: str = ""

    def __post_init__(self):
        if self.summaries and not self.final_answer:
            self.final_answer = self.summaries[0]


async def run_heavyskill(
    query: str,
    config: HeavySkillConfig,
    reasoning_agent: Optional[OpenAICompatibleAgent] = None,
    summary_agent: Optional[OpenAICompatibleAgent] = None,
) -> HeavySkillResult:
    """
    Run the full HeavySkill pipeline: parallel reasoning -> sequential deliberation.

    Args:
        query: The input query / problem.
        config: HeavySkill configuration.
        reasoning_agent: Optional agent for Stage 1. Created from config if None.
        summary_agent: Optional agent for Stage 2. Created from config if None.

    Returns:
        HeavySkillResult containing trajectories, summaries, and final answer.
    """
    # Initialize agents
    if reasoning_agent is None:
        reasoning_agent = OpenAICompatibleAgent(
            model_name=config.model_name,
            api_base=config.api_base,
            api_key=config.api_key,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    if summary_agent is None:
        summary_agent = OpenAICompatibleAgent(
            model_name=config.summary_model,
            api_base=config.summary_base,
            api_key=config.summary_key,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    # Stage 1: Parallel Reasoning
    logger.info("=" * 50)
    logger.info("Stage 1: Parallel Reasoning (K=%d)", config.reason_k)
    logger.info("=" * 50)

    trajectories = await parallel_reason(query, config, agent=reasoning_agent)

    # Memory Cache
    cache = MemoryCache(trajectories)
    logger.info("Memory cache initialized: %d trajectories", len(cache))

    # Stage 2: Sequential Deliberation (with optional iterations)
    summaries = []
    for iteration in range(config.iterations):
        logger.info("=" * 50)
        logger.info(
            "Stage 2: Sequential Deliberation (iteration %d/%d)",
            iteration + 1,
            config.iterations,
        )
        logger.info("=" * 50)

        iter_summaries = await deliberate(
            query=query,
            cache=cache,
            config=config,
            agent=summary_agent,
        )
        summaries = iter_summaries

        # For iterative mode, feed summaries back into cache
        if config.iterations > 1 and iteration < config.iterations - 1:
            for s in iter_summaries:
                cache.add_deliberation(s)

    return HeavySkillResult(
        query=query,
        trajectories=trajectories,
        summaries=summaries,
        iterations_done=config.iterations,
    )
