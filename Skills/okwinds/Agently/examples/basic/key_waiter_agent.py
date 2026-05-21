import asyncio

from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:7b",
        "model_type": "chat",
    },
).set_settings("debug", False)

agent = Agently.create_agent()

# Get specific key before all generation completed
(

    agent.input("34643523+52131231=?").output(
        {
            "thinking": (str,),
            "result": (float,),
            "reply": (str,),
        }
    )
)

reply = agent.get_key_result("thinking")
print(reply)

# Get specific keys from generator before generation completed
(
    agent.input("34643523+52131231=?").output(
        {
            "thinking": (str,),
            "result": (float,),
            "reply": (str,),
        }
    )
)

gen = agent.wait_keys(["thinking", "reply"])
for event, data in gen:
    print(event, data)

# Use handlers to handle different specific keys
(
    agent.input("34643523+52131231=?")
    .output(
        {
            "thinking": (str,),
            "result": (float,),
            "reply": (str,),
        }
    )
    .when_key("thinking", lambda result: print("🤔:", result))
    .when_key("result", lambda result: print("✅:", result))
    .when_key("reply", lambda result: print("⏩:", result))
    .start_waiter()
)

# Expected output shape (content is variable — requires local Ollama):
# <thinking text>                   (from get_key_result)
# thinking <thinking text>          (from wait_keys)
# reply <reply text>                (from wait_keys)
# 🤔: <thinking text>              (from when_key callbacks)
# ✅: 86774754.0                   (from when_key callbacks — 34643523+52131231)
# ⏩: <reply text>                  (from when_key callbacks)
#
# How it works:
# Three APIs for extracting specific structured output fields before or as they arrive:
# get_key_result("key") — blocks until the specified key is fully generated,
#   returns its value; remaining keys continue generating in the background.
# wait_keys(["key1","key2"]) — returns a generator that yields (key_name, value)
#   tuples as each named key finishes; other keys are discarded.
# when_key("key", callback) + start_waiter() — registers callbacks dispatched
#   automatically as each key completes; start_waiter() drives the generator.
