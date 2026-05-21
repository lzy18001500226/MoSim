from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:7b",
        "model_type": "chat",
    },
).set_settings("debug", True)

agent = Agently.create_agent()

ensured_data_object = (
    agent.input(
        # Change the integer from "Now 'control' is 2" to see what happen
        "How to develop an independent game? You MUST use the key name 'final.results' instead of the key name 'final.steps' IF value of the key 'control' > 1. Now 'control' is 1."
    )
    .output(
        {
            "control": (int,),
            "final": {
                "steps": [(str,)],
            },
            "resources": [
                {
                    "title": (str,),
                    "link": (str,),
                }
            ],
        }
    )
    .get_data_object(
        # Use ensure_keys for runtime-dependent paths or conditional checks.
        # Fixed required leaves should be marked with True in .output(...) instead.
        # Use ensure_all_keys=True when you want the whole structure strictly enforced.
        ensure_keys=["final.steps", "resources[*].title", "resources[*].link"],
        # You can switch key path style in 'dot' and 'slash'("final/steps")
        key_style="dot",  # default: "dot"
        # You can customize max retries
        max_retries=1,  # default: 3
        # You can control whether to raise exception if can not ensure
        # all keys in model generation or just ignore it and return the value
        # of the last try.
        raise_ensure_failure=False,  # default: True
    )
)
print(ensured_data_object)
print(ensured_data_object.final)  # type: ignore
print(ensured_data_object.final.steps)  # type: ignore
# use type: ignore since ensure_data_object is a runtime created data model

# Expected output shape (content is variable — requires local Ollama):
# <data_object with .control, .final.steps, .resources[*].title, .resources[*].link>
# The model output must contain final.steps and each resource must have title+link.
#
# How it works:
# get_data_object(ensure_keys=[...]) retries generation up to max_retries times
# if any of the listed key paths are absent or null in the response.
# Key paths use dot notation ("final.steps") or wildcard syntax ("resources[*].title").
# raise_ensure_failure=False returns the last attempt's value instead of raising
# if all retries fail.  Fixed required fields should use True in .output() schema
# rather than ensure_keys; ensure_keys targets runtime-conditional paths.
