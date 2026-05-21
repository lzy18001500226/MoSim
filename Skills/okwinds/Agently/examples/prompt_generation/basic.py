from agently import Agently

agent = Agently.create_agent()

user_input = "Hello"
welcome_words = {
    "Hello": "Welcome word in English",
    "你好": "Welcome word in Chinese",
    "こんにちは": "Welcome word in Japanese",
    "Bonjour": "Welcome word in French",
    "Hola": "Welcome word in Spanish",
}

(
    agent.input({"user_input": user_input})
    .info(welcome_words)
    .instruct(
        [
            "Judge user's region according {user_input}",
            "Use {info} to help",
        ]
    )
    .examples(
        [
            {"user_input": "Hello", "user_region": "UK / US"},
            {"user_input": "你好", "user_region": "China"},
        ]
    )
    .output(
        {
            "why": (str, "explanation"),
            "user_region": (str,),
        }
    )
)

print(agent.prompt.to_messages()[0]["content"])
print("==================")
print(agent.prompt.to_text())

# Expected output (deterministic — no model call):
# agent.prompt.to_messages()[0]["content"] — the full system message text with all sections
# ==================
# agent.prompt.to_text() — the same prompt in human-readable text form
#
# How it works:
# .input({"user_input": user_input}), .info(welcome_words), .instruct([...]),
# .examples([...]), and .output({...}) each populate a named prompt slot.
# {user_input}, {info} placeholders in instruct strings are resolved at render time.
# to_messages() serializes to an OpenAI-style messages list (one system message here).
# to_text() serializes to readable text for debugging.  No model call is made.
