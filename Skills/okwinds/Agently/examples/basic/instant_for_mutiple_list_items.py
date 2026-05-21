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

instant_generator = (
    agent.input("How to develop an independent game?")
    .output(
        {
            "steps": [(str,)],
        }
    )
    .get_generator(type="instant")
)

for data in instant_generator:
    if data.wildcard_path == "steps[*]":
        print(data.path, data.indexes, data.value, data.full_data)

# Expected output shape (content is variable — requires local Ollama):
# steps[0] [0] <complete step 1 text> {'steps': ['step 1', ...]}
# steps[1] [1] <complete step 2 text> {'steps': ['step 1', 'step 2', ...]}
# ...
#
# How it works:
# get_generator(type="instant") yields streaming_parse node objects as each
# list element completes.  Each node has:
#   .path         — exact key path ("steps[0]", "steps[1]", ...)
#   .wildcard_path — path with indices replaced by * ("steps[*]")
#   .indexes      — list of integer indices along the path ([0], [1], ...)
#   .value        — fully assembled value of the node so far
#   .full_data    — the complete parsed dict up to this point
# Filtering by wildcard_path == "steps[*]" fires once per completed list item.
