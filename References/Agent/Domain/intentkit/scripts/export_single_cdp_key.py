import argparse
import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intentkit.wallets.cdp import get_cdp_client

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main(address: str) -> None:
    logger.info("Initializing CDP client...")
    try:
        cdp_client = get_cdp_client()
    except Exception as e:
        logger.error(f"Failed to initialize CDP client: {e}")
        sys.exit(1)

    logger.info(f"Exporting private key for address: {address}")
    try:
        # The key is returned as a string
        # Note: The CDP SDK requires the address to be associated with the project
        private_key = await cdp_client.evm.export_account(address=address)

        # Output strictly the private key or a JSON for easy parsing?
        # The user just said "export single address script".
        # I'll print it clearly.
        print("-" * 64)
        print(f"Address: {address}")
        print(f"Private Key: {private_key}")
        print("-" * 64)

    except Exception as exc:
        logger.error(f"Failed to export key for {address}: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export the private key for a single CDP wallet address."
    )
    parser.add_argument(
        "address", help="The EVM wallet address to export the private key for."
    )
    args = parser.parse_args()

    asyncio.run(main(args.address))
