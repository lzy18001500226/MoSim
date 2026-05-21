import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import asyncio

from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": os.environ["DEEPSEEK_BASE_URL"],
        "model": os.environ["DEEPSEEK_DEFAULT_MODEL"],
        "model_type": "chat",
        "auth": os.environ["DEEPSEEK_API_KEY"],
    },
)

agent = Agently.create_agent()


async def validate_handler(result, context):
    if "python" in result["joke"].lower():
        print("OK, it has 'python' in the joke.")
        return True
    else:
        print("No, I need 'python' in the joke! Let's try again!")
        return False


result = (
    agent.input("Tell me a joke about python the animal.")
    .output(
        {
            "joke": (str, None, True),
            "punch_line": (str, None, True),
        }
    )
    .validate(validate_handler)
    .start()
)

print("Final Result:\n", result)

# Expected output (content is variable — requires DeepSeek API key):
# If the first attempt lacks "python": "No, I need 'python' in the joke! Let's try again!"
# On a passing attempt:             "OK, it has 'python' in the joke."
# Final Result:
#  {'joke': '...python...', 'punch_line': '...'}
#
# How it works:
# .validate(async_handler) wraps the request in an auto-retry loop.
# The handler receives (result, context) after each generation attempt and
# returns True to accept the result or False to trigger another attempt.
# This lets you apply semantic validation (e.g. checking that a specific word
# appears in the output) that cannot be expressed in the .output() schema alone.
# Retries reuse the same prompt; the model sees its previous attempt in context.
