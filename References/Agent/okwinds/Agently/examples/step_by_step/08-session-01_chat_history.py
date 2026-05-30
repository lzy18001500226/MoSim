from agently import Agently

agent = Agently.create_agent()

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## Chat History: basic multi-turn management
def chat_history_basic():
    # You can add messages to chat_history to keep multi-turn context.
    agent.set_chat_history(
        [
            {"role": "user", "content": "Hi, who are you?"},
            {"role": "assistant", "content": "I'm an Agently assistant."},
        ]
    )
    result = agent.input("What did I ask you before?").start()
    print(result)

    # You can append new turns, or reset the history.
    # Treat the last answer as a new user message to continue the thread.
    agent.add_chat_history({"role": "user", "content": result})
    follow_up = agent.input("Summarize my last message in one sentence.").start()
    print(follow_up)

    agent.reset_chat_history()


# chat_history_basic()

# chat_history_basic() is commented out — uncomment to run with a local Ollama model.
# Expected output shape (content is variable):
#   line 1: model answer that references "Hi, who are you?" (the seeded history)
#   line 2: one-sentence summary of the model's own previous answer
#
# How it works:
# set_chat_history([...]) replaces the current history with a list of {role, content} dicts.
# The history is an agent-level prompt, so it persists across requests until reset.
# add_chat_history({role, content}) appends one turn without clearing existing history —
# useful for feeding the model's last reply back as a user message to continue the thread.
# reset_chat_history() clears all history.
# Chat history is injected into the prompt as a standard OpenAI-style messages list,
# so model context and token limits apply in the normal way.
