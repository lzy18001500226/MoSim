import asyncio
from typing import cast

import aiohttp
from web3 import AsyncWeb3
from web3.providers.rpc.utils import ExceptionRetryConfiguration

from intentkit.config.config import config
from intentkit.utils.chain import ChainProvider

_async_web3_client_cache: dict[str, AsyncWeb3] = {}


def get_async_web3_client(network_id: str) -> AsyncWeb3:
    """Get an Async Web3 client for the specified network with auto-retry.

    Args:
        network_id: The network ID to get the Web3 client for

    Returns:
        AsyncWeb3: An Async Web3 client instance for the specified network
    """
    if network_id in _async_web3_client_cache:
        return _async_web3_client_cache[network_id]

    chain_provider = cast(ChainProvider, config.chain_provider)
    chain = chain_provider.get_chain_config(network_id)

    # Configure provider with retry middleware
    retry_config = ExceptionRetryConfiguration(
        errors=(aiohttp.ClientError, asyncio.TimeoutError, TimeoutError),
        retries=5,
    )
    provider = AsyncWeb3.AsyncHTTPProvider(
        chain.rpc_url,
        exception_retry_configuration=retry_config,
    )
    web3_client = AsyncWeb3(provider)

    _async_web3_client_cache[network_id] = web3_client

    return web3_client


__all__ = ["get_async_web3_client"]
