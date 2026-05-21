import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://qianfan.baidubce.com/v2",
        "model": "ernie-4.5-turbo-128k",
        "auth": "QianFan API Key",
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
# after provider credentials are configured, the BaiduErnie.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# Baidu's QianFan platform exposes an OpenAI-compatible endpoint at qianfan.baidubce.com/v2.
# Set auth="<QianFan API Key>" and model="ernie-4.5-turbo-128k" (or any ERNIE model).
# Structured output, streaming, and tool use work the same as with OpenAI-compatible models.
