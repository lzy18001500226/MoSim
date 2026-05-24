from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:7b",
        "model_type": "chat",
    },
)

yaml_prompt = """
$role: You're a cat language expert!
input: The cat said "${cat_words}"
output:
    cat_words:
        $type: str
        $desc: what did the cat said?
    reply:
        $type: str
        $desc: what would you reply?
""".strip()

cat_words = "This is delicious!"

agent = Agently.create_agent()
result = agent.load_yaml_prompt(yaml_prompt, mappings={"cat_words": cat_words}).start()
print(result)

# Expected output (content is variable — requires local Ollama):
# {'cat_words': 'This is delicious!', 'reply': '<cat-language expert reply>'}
#
# How it works:
# load_yaml_prompt() accepts an inline YAML string (not only a file path).
# The YAML DSL maps $role, input, and output sections onto Agently prompt slots.
# mappings={"cat_words": cat_words} substitutes ${cat_words} tokens in the YAML at
# load time, before the prompt is built.  .start() sends the assembled prompt to the
# local model and returns the structured dict.
