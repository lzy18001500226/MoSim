import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-5",
        "auth": "<OpenAI-API-Key>",
        # Provide local proxy address if you need
        "proxy": "http://127.0.0.1:7890",
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
# after provider credentials are configured, the OpenAI.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# OpenAI uses the OpenAI-compatible endpoint at api.openai.com/v1.
# Set auth="<OpenAI-API-Key>" and model="gpt-5" (or any available model).
# proxy= accepts an HTTP/HTTPS proxy URL string for environments that require one;
# omit it when connecting directly.
