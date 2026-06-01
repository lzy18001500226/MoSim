"""CDP wallet interaction skills.

This module provides wallet skills that require a CDP wallet provider.
"""

from typing import TypedDict

from intentkit.skills.base import SkillConfig, SkillState
from intentkit.skills.cdp.base import CDPBaseTool
from intentkit.skills.cdp.get_balance import CDPGetBalance
from intentkit.skills.cdp.get_wallet_details import CDPGetWalletDetails
from intentkit.skills.cdp.native_transfer import CDPNativeTransfer


class SkillStates(TypedDict):
    cdp_get_balance: SkillState
    cdp_get_wallet_details: SkillState
    cdp_native_transfer: SkillState


class Config(SkillConfig):
    """Configuration for CDP skills."""

    states: SkillStates


# Cache for skill instances
_cache: dict[str, CDPBaseTool] = {
    "cdp_get_balance": CDPGetBalance(),
    "cdp_get_wallet_details": CDPGetWalletDetails(),
    "cdp_native_transfer": CDPNativeTransfer(),
}


async def get_skills(
    config: Config,
    is_private: bool,
    **_,
) -> list[CDPBaseTool]:
    """Get all enabled CDP skills.

    Args:
        config: The configuration for CDP skills.
        is_private: Whether to include private skills.

    Returns:
        A list of enabled CDP skills.
    """
    tools: list[CDPBaseTool] = []

    for skill_name, state in config["states"].items():
        if state == "disabled":
            continue
        if state == "public" or (state == "private" and is_private):
            # Check cache first
            if skill_name in _cache:
                tools.append(_cache[skill_name])

    return tools


def available() -> bool:
    """Check if this skill category is available based on system config.

    CDP wallet skills are globally available but require the agent's
    wallet provider to be configured as 'cdp'.
    """
    return True
