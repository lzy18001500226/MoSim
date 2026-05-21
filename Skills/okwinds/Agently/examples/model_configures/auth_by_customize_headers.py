import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://my-customize-server/v1",
        "model": "my-model",
        "auth": {
            "headers": {
                "Authorization": "Customize <My-Customize-Token>",
            }
        },
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
# after provider credentials are configured, the auth_by_customize_headers.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# When a provider requires authentication via custom HTTP headers (e.g., "Authorization: Customize ..."),
# pass auth={"headers": {"Authorization": "Customize <token>"}} instead of a plain string.
# Agently merges these into the outgoing HTTP headers before sending the request.
