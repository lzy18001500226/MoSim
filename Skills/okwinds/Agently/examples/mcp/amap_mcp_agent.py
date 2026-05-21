from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import os
import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:7b",
        "model_type": "chat",
    },
).set_settings("debug", True)

agent = Agently.create_agent()


async def main():
    result = (
        # MCP tools join the agent's Action runtime after registration.
        await agent.use_mcp(f"https://mcp.amap.com/mcp?key={ os.environ.get('AMAP_API_KEY') }")
        .input("What's the weather like in Shanghai today?")
        .async_start()
    )
    print(result)


asyncio.run(main())

# Expected output (requires AMAP_API_KEY and local Ollama):
# <model reply about Shanghai's current weather, referencing AMap tool output>
#
# How it works:
# await agent.use_mcp("https://mcp.amap.com/mcp?key=...") connects to the remote AMap
# MCP server and registers its tools (weather, geocode, directions, etc.) into the
# agent's Action runtime via the Model Context Protocol over HTTPS.
# The registered tools are exposed to the model in the same way as native actions.
# .input("...").async_start() sends the question; the model calls the weather tool,
# receives the result, and incorporates it into the final reply.
