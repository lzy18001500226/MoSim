import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import asyncio

from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": os.environ["QIANFAN_BASE_URL"],
        "model": "ernie-lite-8k",
        "model_type": "chat",
        "auth": os.environ["QIANFAN_API_KEY"],
    },
)

user_input = "How are you today?"
role = "A teacher for kids that 3 years old."


async def main():
    agent = Agently.create_agent()
    result = (
        agent.input(
            "Acting as ${role} to response: ${user_input}",
            # Placeholder substitutions always use explicit mappings=...
            mappings={
                "user_input": user_input,
                "role": role,
            },
        )
        .output({"reply": (str, "role reply only", True)})
        .start()
    )
    print(result["reply"])


asyncio.run(main())

# Expected output shape (content is variable — requires QianFan API key):
# <reply in the style of a teacher addressing a 3-year-old about "How are you today?">
#
# How it works:
# .input("Acting as ${role} to response: ${user_input}", mappings={...}) uses
# ${placeholder} tokens in the input string and substitutes them at request time
# from the explicit mappings dict.  This separates the prompt template from the
# runtime values without string formatting in user code.  Only keys in mappings
# are substituted; unmatched tokens are left as-is.
