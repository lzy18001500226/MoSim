from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://qianfan.baidubce.com/v2",
        "model": "ernie-4.5-turbo-vl",
        "auth": "<QianFan-API-Key>",
        "request_options": {
            "temperature": 0.7,
        },
    },
).set_settings("debug", True)

agent = Agently.create_agent()

result = agent.attachment(
    [
        {"type": "text", "text": "What's this？"},
        {
            "type": "image_url",
            "image_url": {"url": "https://cdn.deepseek.com/logo.png?x-image-process=image%2Fresize%2Cw_1920"},
        },
    ],
).start()

print(result)

# Runs on import — requires a valid QianFan API key in the auth field.
# Expected output: model description of the DeepSeek logo image (blue stylized "D" mark).
# Content is non-deterministic; the model should mention a logo or branding element.
#
# How it works:
# .attachment([...]) accepts an OpenAI-style multi-modal content list:
#   {"type": "text", "text": "..."}        — text part of the user message
#   {"type": "image_url", "image_url": {"url": "..."}}  — image by URL
# The list is assembled as the user-turn content and sent to the VLM endpoint.
# Any OpenAI-compatible VLM can be used here; swap base_url, model, and auth
# to use a different provider (Ollama, OpenAI, DeepSeek-VL, etc.).
# debug=True prints the raw request/response stream to console.
