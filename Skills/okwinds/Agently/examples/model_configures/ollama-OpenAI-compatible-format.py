import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5-coder:14b",
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
# after provider credentials are configured, the ollama-OpenAI-compatible-format.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# Ollama exposes an OpenAI-compatible endpoint at localhost:11434/v1 with no auth required.
# Set model to any locally pulled Ollama model name (e.g., qwen2.5-coder:14b).
# No auth key is needed — just base_url and model.  This is the standard pattern for
# local LLM development and testing with any Ollama-served model.
