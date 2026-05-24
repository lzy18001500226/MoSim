from agently import Agently

import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "full_url": "http://localhost:11434/v1/chat/completions",
        # "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5-coder:14b",
        "request_options": {
            "temperature": 0.7,
        },
        "content_mapping": {
            # "delta": "result",
        },
        "stream": False,
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
# after provider credentials are configured, the full_url_instead_of_base_url.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# full_url= replaces base_url= when you want to point at a specific endpoint path rather
# than letting Agently append "/chat/completions".  stream=False disables streaming and
# requests the full response in one shot.  content_mapping= (commented out) lets you remap
# non-standard response fields to Agently's expected keys for custom API wrappers.
