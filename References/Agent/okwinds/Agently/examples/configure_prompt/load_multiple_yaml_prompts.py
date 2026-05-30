from pathlib import Path
from agently import Agently

agent = Agently.create_agent()

agent.load_yaml_prompt(
    Path(__file__).parent / "multiple_yaml_prompts.yaml",
    prompt_key_path="prompt_1",
)
print(agent.get_prompt_text())

# Expected output (deterministic — no model call):
# The serialized prompt text for the "prompt_1" section of multiple_yaml_prompts.yaml.
#
# How it works:
# load_yaml_prompt() with prompt_key_path="prompt_1" selects a single named section
# from a multi-prompt YAML file, letting you keep several prompt variants in one file
# and load the right one at runtime without splitting into multiple files.
# The selected section is applied to the agent's prompt store and then serialized
# to text via get_prompt_text().
