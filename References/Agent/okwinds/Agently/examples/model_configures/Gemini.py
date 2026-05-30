import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash",
        "auth": "<Google-AIStudio-API-Key>",
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
# after provider credentials are configured, the Gemini.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# Google AI Studio exposes an OpenAI-compatible endpoint at generativelanguage.googleapis.com.
# Set auth="<Google-AIStudio-API-Key>" and model="gemini-2.5-flash" (or another Gemini model).
# The /openai/ suffix in the base_url is required for the OpenAI-compatible route.
