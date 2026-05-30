import asyncio
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen3-coder-flash",
        "auth": "Aliyun API Key",
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
# after provider credentials are configured, the AliQwen.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# Aliyun DashScope uses the OpenAI-compatible endpoint at dashscope.aliyuncs.com.
# Set auth="<Aliyun API Key>" and model="qwen3-coder-flash" (or any DashScope model).
# get_async_generator(type="instant") streams structured output as it generates;
# event.path shows the current field, event.is_complete shows if the field is done.
