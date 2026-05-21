from agently import Agently

## Settings
# Global Model Settings
Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)

# Create LLM Request Agent Instance
agent = Agently.create_agent()

# Keys' values in agent instance settings will cover global settings
# but not keys' values that not mention will inherit from global settings
agent.set_settings(
    "OpenAICompatible",
    {
        "model": "qwen3:latest",
    },
)

## Debug Toggle
# Set to False by default, turn on debug mode will display model request processing streaming logs in console.
agent.set_settings("debug", True)

agent_model_requester_settings = agent.settings.get("plugins.ModelRequester.OpenAICompatible", {})
assert isinstance(agent_model_requester_settings, dict)
print(agent_model_requester_settings.get("base_url"))  # "http://127.0.0.1:11434/v1"
print(agent_model_requester_settings.get("model"))  # qwen3:latest

## Note:
# Default Global Settings: agently/_default_settings.yaml
# Default Plugin Settings can be defined in attribution "DEFAULT_SETTINGS" in Plugin Class
# Core Plugins with Settings:
# Model Requester: agently/builtins/plugins/ModelRequester/OpenAICompatible.py

# Expected output (deterministic — no model call is made):
# http://127.0.0.1:11434/v1
# qwen3:latest
#
# How it works:
# Agently.set_settings() writes to the global settings store shared by all agents.
# agent.set_settings() writes to the agent instance's own store, which overlays the global one.
# When a key exists in both, the instance value wins (model = "qwen3:latest" overrides
# the global "qwen2.5:7b"); keys absent from the instance fall back to global
# (base_url = "http://127.0.0.1:11434/v1" is inherited).
# settings.get("plugins.ModelRequester.OpenAICompatible") reads the merged result —
# this assertion confirms the overlay logic without making a model call.
