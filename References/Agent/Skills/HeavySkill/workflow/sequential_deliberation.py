"""Stage 2: Sequential Deliberation — synthesize parallel trajectories into a final answer."""

import logging
from typing import List, Optional

from .agent.openai_compatible import OpenAICompatibleAgent
from .config import HeavySkillConfig
from .memory_cache import MemoryCache
from .prompts import build_summary_prompt
from .utils import clip_trajectories

logger = logging.getLogger(__name__)


async def deliberate(
    query: str,
    cache: MemoryCache,
    config: HeavySkillConfig,
    agent: Optional[OpenAICompatibleAgent] = None,
    trajectory_selection: str = "random",
) -> List[str]:
    """
    Perform sequential deliberation on cached reasoning trajectories.

    Args:
        query: Original user query.
        cache: MemoryCache containing parallel reasoning trajectories.
        config: HeavySkill configuration.
        agent: Optional pre-initialized agent for summary. Created from config if None.
        trajectory_selection: Strategy for selecting trajectories ("random", "max_answer_num", "max_diversity").

    Returns:
        List of summary_k deliberation outputs.
    """
    if agent is None:
        agent = OpenAICompatibleAgent(
            model_name=config.summary_model,
            api_base=config.summary_base,
            api_key=config.summary_key,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    # Select trajectories from cache
    selected = cache.select(k=config.reason_k, strategy=trajectory_selection)

    # Clip if exceeding token budget
    selected = clip_trajectories(selected, config.max_trajectory_tokens)

    # Build summary prompt
    prompt = build_summary_prompt(
        query=query,
        trajectories=selected,
        prompt_type=config.prompt_type,
        language=config.language,
    )

    logger.info(
        "Starting deliberation: %d trajectories, summary_k=%d, model=%s",
        len(selected),
        config.summary_k,
        config.summary_model,
    )

    # Generate summary_k deliberation outputs
    summaries = await agent.generate(
        prompt=prompt,
        n=config.summary_k,
        temperature=config.summary_temperature,
        max_tokens=config.summary_max_tokens,
        top_p=config.reason_top_p,
    )

    logger.info("Deliberation complete: %d outputs generated", len(summaries))
    return summaries
