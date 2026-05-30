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
        {"type": "text", "text": "这是什么？"},
        {
            "type": "image_url",
            "image_url": {"url": "https://cdn.deepseek.com/logo.png?x-image-process=image%2Fresize%2Cw_1920"},
        },
    ],
).start()

print(result)

# Expected output (requires QianFan API key):
# <model description of the DeepSeek logo image in response to "这是什么？">
# (Content is non-deterministic; the model should mention a logo or brand element.)
#
# How it works:
# .attachment([{"type":"text","text":"这是什么？"},{"type":"image_url","image_url":{"url":"..."}}])
# assembles a multimodal user-turn message following the OpenAI Vision format.
# The list is sent as the content array of the user message to the VLM endpoint.
# Any OpenAI-compatible VLM provider works here; swap base_url, model, and auth
# to switch providers.  debug=True prints the raw request/response stream.
