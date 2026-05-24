import os

from dotenv import find_dotenv, load_dotenv

from agently import Agently

load_dotenv(find_dotenv())

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY. Put it in your environment or .env before running this example.")

Agently.set_settings("plugins.ModelRequester.activate", "OpenAIResponsesCompatible")
Agently.set_settings(
    "OpenAIResponsesCompatible",
    {
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "model": os.getenv("OPENAI_RESPONSES_MODEL", "gpt-5.5"),
        "auth": api_key,
        "request_options": {
            "text": {
                "verbosity": "low",
            },
            "max_output_tokens": 256,
        },
    },
)


def basic_streaming():
    print("Example 1: Basic streaming with OpenAI Responses\n\n-----\n\n")
    agent = Agently.create_agent()
    gen = (
        agent.input("Explain what the Responses API is in 3 short bullet points.")
        .options(
            {
                "instructions": "Reply in markdown bullet points. Keep it concise.",
            }
        )
        .get_generator(type="specific")
    )

    for event, content in gen:
        if event == "delta":
            print(content, end="", flush=True)

    print("\n")


def streaming_tool_calls():
    print("Example 2: Responses tool call chunks normalized to Agently standard events\n\n-----\n\n")
    agent = Agently.create_agent()
    gen = (
        agent.input("What is the weather like in Shanghai today? If you need fresh data, call get_weather.")
        .options(
            {
                "tools": [
                    {
                        "type": "function",
                        "name": "get_weather",
                        "description": "Get the current weather for a city.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string"},
                                "unit": {
                                    "type": "string",
                                    "enum": ["celsius", "fahrenheit"],
                                },
                            },
                            "required": ["city"],
                            "additionalProperties": False,
                        },
                        "strict": True,
                    }
                ],
                "tool_choice": "auto",
            }
        )
        .get_generator(type="specific")
    )

    for event, content in gen:
        if event == "delta":
            print(content, end="", flush=True)
        if event == "tool_calls":
            print("\n<tool_calls>\n", content, "\n</tool_calls>")

    print("")


if __name__ == "__main__":
    basic_streaming()
    streaming_tool_calls()

# Stable expected key output from the declared run:
# after provider credentials are configured, the OpenAIResponsesCompatible.py snippet sends a request through that provider and prints the model response.
#
# How it works:
# The OpenAI Responses API uses a different schema from the Chat Completions API.
# Activate it with set_settings("plugins.ModelRequester.activate", "OpenAIResponsesCompatible"),
# then configure the "OpenAIResponsesCompatible" namespace.
# Two examples are shown: basic streaming with options.instructions=, and streaming tool
# calls via .options({"tools":[...]}) using the same (event, data) pattern as the Chat plugin.
# The "tool_calls" event carries the normalized call payload when the model selects a tool.
