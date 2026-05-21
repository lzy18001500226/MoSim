import os
from agently import Agently

current_dir = os.path.dirname(os.path.abspath(__file__))
json_prompt_path = os.path.join(current_dir, "json_prompt.json")

agent = Agently.create_agent()
agent.load_json_prompt(
    json_prompt_path,
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
# load_json_prompt() reads the JSON prompt file, fills in ${placeholder} tokens from
# mappings= with the provided values, and applies the result to the agent's prompt store.
# The agent-level prompt is inherited by every request from this agent.
# The request-level prompt is a per-call overlay; inspecting it separately shows it is
# empty here because all configuration was at the agent level.
