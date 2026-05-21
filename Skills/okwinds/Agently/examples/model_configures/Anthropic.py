import asyncio
import os

from dotenv import find_dotenv, load_dotenv

from agently import Agently

load_dotenv(find_dotenv())

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("Missing ANTHROPIC_API_KEY. Put it in your environment or .env before running this example.")

Agently.set_settings("plugins.ModelRequester.activate", "AnthropicCompatible")
Agently.set_settings(
    "AnthropicCompatible",
    {
        "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"),
        "model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        "auth": {"api_key": api_key},
        "request_options": {
            "temperature": 0.7,
        },
    },
)

llm = Agently.create_agent()


async def main():
    instant_mode_response = (
        llm.input("Give me 5 computer-related words and 3 color-related phrases and 1 random sentence.")
        .output(
            {
                "words": [(str,)],
                "phrases": {
                    "<color-name>": (str, "phrase"),
                },
                "sentence": (str,),
            }
        )
        .get_async_generator(type="instant")
    )

    async for event in instant_mode_response:
        print(
            event.path,
            "[DONE]" if event.is_complete else "[>>>>]",
            event.value,
        )


asyncio.run(main())

# Stable expected key output from the declared run:
# after provider credentials are configured, the Anthropic.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# Anthropic's API requires the "AnthropicCompatible" plugin instead of "OpenAICompatible".
# Activate it with set_settings("plugins.ModelRequester.activate", "AnthropicCompatible"),
# then configure the "AnthropicCompatible" namespace with base_url, model, and auth.
# auth={"api_key": api_key} maps to the x-api-key header expected by the Anthropic API.
# The request and output API are identical to OpenAICompatible after activation.
