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

gen = agent.input("Give me a long speech").get_generator()

for delta in gen:
    print(delta, end="", flush=True)

print("")

# Expected output (content is variable — requires local Ollama):
# (instant() runs directly)
# <practice question 1><newline><reference answer 1>
# <practice question 2><newline><reference answer 2>
#
# How it works:
# Three streaming variants are demonstrated over the same complex nested schema:
# basic_delta (async):  get_async_generator(type="delta") — raw tokens, simplest.
# async_instant (async): get_async_generator(type="instant") — structured nodes
#   with .path, .wildcard_path, .delta; dispatches per field without index math.
# instant (sync):       get_generator(type="instant") — same nodes synchronously.
# The instant variants filter on wildcard_path == "practices[*].question" and
# "practices[*].answer" to print practice Q/A pairs as each list element streams,
# detecting field changes via change_path to emit newlines between question and answer.
