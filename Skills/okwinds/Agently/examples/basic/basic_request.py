import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from agently import Agently
from agently.utils import SettingsNamespace

request_settings = SettingsNamespace(
    Agently.settings,
    "plugins.ModelRequester.OpenAICompatible",
)
request_settings["base_url"] = os.environ["DEEPSEEK_BASE_URL"]
request_settings["model"] = os.environ["DEEPSEEK_DEFAULT_MODEL"]
request_settings["model_type"] = "chat"
request_settings["auth"] = os.environ["DEEPSEEK_API_KEY"]

request = Agently.create_request()
request.set_prompt("input", "Hello")
request.set_prompt(
    "output",
    {
        "thinking": ([(str,)], "Step by step"),
        "reply": (str, "Markdown Style", True),
    },
)

result = request.get_data_object()
Agently.print(result)

# Expected output shape (content is variable — requires DeepSeek API key):
# <Pydantic-like object with .thinking (list[str]) and .reply (str) attributes>
#
# How it works:
# Agently.create_request() creates a low-level request handle outside an agent.
# SettingsNamespace targets the OpenAICompatible model requester directly by its
# plugin settings path, bypassing the agent layer.
# request.set_prompt("output", {...}) defines the structured output schema.
# get_data_object() blocks, parses the response, and returns a Pydantic model
# instance with attribute access (result.thinking, result.reply).
