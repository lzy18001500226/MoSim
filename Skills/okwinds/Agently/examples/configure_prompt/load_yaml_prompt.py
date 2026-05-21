import os
from agently import Agently

current_dir = os.path.dirname(os.path.abspath(__file__))
yaml_prompt_path = os.path.join(current_dir, "yaml_prompt.yaml")

agent = Agently.create_agent()
agent.load_yaml_prompt(
    yaml_prompt_path,
    mappings={
        "in_value_placeholder": "IN VALUE!",
        "key_name_placeholder": "KEY_NAME",
        "only_value_placeholder": [
            "THIS",
            "IS",
            "ONLY",
            "VALUE",
            "PLACEHOLDER",
        ],
    },
)
print("AGENT PROMPT:", agent.prompt.get())
print("REQUEST PROMPT:", agent.request.prompt.get(inherit=False))

# Expected output (deterministic — no model call):
# AGENT PROMPT: {...}   — all placeholder tokens replaced (IN VALUE!, KEY_NAME, list)
# REQUEST PROMPT: {}    — empty because no request-level overrides were set
#
# How it works:
# load_yaml_prompt() reads the YAML prompt file, fills in ${placeholder} tokens from
# mappings= with the provided values, and applies the result to the agent's prompt store.
# The YAML format mirrors the JSON format but is more readable for multi-field prompts.
# Agent-level vs request-level inheritance behaves identically to the JSON variant.
