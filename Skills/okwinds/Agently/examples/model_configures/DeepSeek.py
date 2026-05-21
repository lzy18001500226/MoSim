import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "auth": "DEEPSEEK API Key",
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
# after provider credentials are configured, the DeepSeek.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# DeepSeek exposes an OpenAI-compatible endpoint at api.deepseek.com/v1.
# Set auth="<DeepSeek API Key>" and model="deepseek-chat" (or "deepseek-reasoner" for R1).
# For the reasoning model, use get_generator(type="specific") and handle "reasoning_delta"
# events to separate chain-of-thought tokens from the final answer.
