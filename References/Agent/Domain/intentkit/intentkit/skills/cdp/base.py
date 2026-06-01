"""CDP wallet skills base class."""

from langchain_core.tools.base import ToolException

from intentkit.skills.onchain import IntentKitOnChainSkill


class CDPBaseTool(IntentKitOnChainSkill):
    """Base class for CDP wallet skills.

    CDP skills provide basic wallet operations like getting balances,
    wallet details, and transferring native tokens.

    These skills explicitly require a CDP wallet provider.
    """

    category: str = "cdp"

    def ensure_cdp_provider(self) -> None:
        """Ensure the agent's wallet provider is CDP."""
        if self.get_agent_wallet_provider_type() != "cdp":
            raise ToolException(
                "This skill is only available when the wallet provider is 'cdp'."
            )
