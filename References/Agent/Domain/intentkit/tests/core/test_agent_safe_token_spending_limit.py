import json
from datetime import datetime
from typing import Literal
from unittest.mock import AsyncMock, MagicMock

import pytest

from intentkit.core.agent import set_agent_safe_token_spending_limit
from intentkit.models.agent import Agent, AgentVisibility
from intentkit.models.agent_data import AgentData
from intentkit.utils.error import IntentKitAPIError


def _build_agent(wallet_provider: Literal["safe", "cdp"] = "safe") -> Agent:
    now = datetime.now()
    return Agent(
        id="agent-123",
        name="Test Agent",
        description="A test agent",
        model="gpt-4o",
        deployed_at=now,
        updated_at=now,
        created_at=now,
        owner="did:privy:user_1",
        skills={},
        prompt="You are a helper.",
        temperature=0.7,
        visibility=AgentVisibility.PRIVATE,
        public_info_updated_at=now,
        wallet_provider=wallet_provider,
        weekly_spending_limit=200.0,
        network_id="base-mainnet",
    )


@pytest.mark.asyncio
async def test_set_agent_safe_token_spending_limit_success(monkeypatch):
    agent = _build_agent("safe")
    now = datetime.now()
    agent_data = AgentData(
        id=agent.id,
        evm_wallet_address="0xsafe",
        privy_wallet_data=json.dumps(
            {
                "privy_wallet_id": "privy-wallet-1",
                "privy_wallet_address": "0x0000000000000000000000000000000000000001",
                "smart_wallet_address": "0x0000000000000000000000000000000000000002",
                "network_id": "base-mainnet",
                "rpc_url": "http://rpc.url",
            }
        ),
        created_at=now,
        updated_at=now,
    )

    monkeypatch.setattr(
        "intentkit.core.agent.queries.get_agent",
        AsyncMock(return_value=agent),
    )
    monkeypatch.setattr(AgentData, "get", AsyncMock(return_value=agent_data))
    monkeypatch.setattr("intentkit.wallets.privy.PrivyClient", MagicMock())

    set_limit_mock = AsyncMock(return_value={"next_nonce": 1})
    monkeypatch.setattr(
        "intentkit.wallets.privy.set_safe_token_spending_limit",
        set_limit_mock,
    )

    result = await set_agent_safe_token_spending_limit(
        agent_id=agent.id,
        token_address="0x1111111111111111111111111111111111111111",
        spending_limit=123.45,
    )

    set_limit_mock.assert_awaited_once()
    assert set_limit_mock.await_args is not None
    kwargs = set_limit_mock.await_args.kwargs
    assert kwargs["privy_wallet_id"] == "privy-wallet-1"
    assert kwargs["safe_address"] == "0x0000000000000000000000000000000000000002"
    assert kwargs["token_address"] == "0x1111111111111111111111111111111111111111"
    assert kwargs["spending_limit"] == 123.45
    assert kwargs["network_id"] == "base-mainnet"
    assert kwargs["rpc_url"] == "http://rpc.url"
    assert "token_decimals" not in kwargs
    assert result == {"next_nonce": 1}


@pytest.mark.asyncio
async def test_set_agent_safe_token_spending_limit_requires_safe_wallet(monkeypatch):
    agent = _build_agent("cdp")
    monkeypatch.setattr(
        "intentkit.core.agent.queries.get_agent",
        AsyncMock(return_value=agent),
    )

    with pytest.raises(IntentKitAPIError) as exc_info:
        await set_agent_safe_token_spending_limit(
            agent_id=agent.id,
            token_address="0x1111111111111111111111111111111111111111",
            spending_limit=10.0,
        )

    assert exc_info.value.key == "SafeWalletRequired"
