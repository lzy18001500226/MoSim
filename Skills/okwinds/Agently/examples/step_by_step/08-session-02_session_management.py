from agently import Agently
from agently.core import Session

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)

agent = Agently.create_agent()


## Session — persistent, named conversation contexts
#
# A session is a named context that automatically records every request/reply turn
# and replays the history in each subsequent request.
# Unlike set_chat_history() (which is a one-shot injection), a session accumulates
# turns automatically and persists until explicitly deactivated.
#
# Key difference from chat_history:
#   set_chat_history()      — you manually manage the message list
#   activate_session()      — Agently records and replays turns automatically


## 1. Session on/off
def session_on_off():
    agent.activate_session(session_id="demo-on-off")

    print("[Session ON] Asking model to remember something...")
    agent.input("Remember this: my favourite colour is indigo.").streaming_print()

    print("[Session ON] The model has full conversation history:")
    agent.input("What colour did I ask you to remember?").streaming_print()

    agent.deactivate_session()

    print("[Session OFF] Same question without session — model has no memory:")
    agent.input("What colour did I ask you to remember?").streaming_print()


# session_on_off()


## 2. Session isolation by ID
#
# Different session_ids maintain completely independent histories.
# Switching IDs is instant — no data is lost from either session.

def session_isolation():
    agent.activate_session(session_id="project-alpha")
    agent.input("This project is called Alpha and uses Go.").streaming_print()

    agent.activate_session(session_id="project-beta")
    agent.input("This project is called Beta and uses Rust.").streaming_print()

    print("[project-beta context]")
    agent.input("What is the project name and language?").streaming_print()

    agent.activate_session(session_id="project-alpha")
    print("[project-alpha context]")
    agent.input("What is the project name and language?").streaming_print()


# session_isolation()


## 3. Selective recording with input_keys and reply_keys
#
# By default a session records the entire user input and the entire model reply.
# Use input_keys / reply_keys to record only specific fields — useful when the
# full prompt contains transient data (timestamps, request IDs) that should not
# pollute the session history.

def selective_recording():
    agent.activate_session(session_id="demo-selective")
    # Record only specific prompt fields and output keys.
    agent.set_settings("session.input_keys", ["info.topic", "input.question"])
    agent.set_settings("session.reply_keys", ["summary", "keywords"])

    result = (
        agent.info({"topic": "distributed systems", "request_id": "req-001-ephemeral"})
        .input({"question": "What is eventual consistency?", "timestamp": "2025-01-01T00:00:00Z"})
        .output({
            "summary": (str, "Concise explanation"),
            "keywords": [(str, "Key term")],
            "internal_trace": (str, "Internal processing note — not recorded"),
        })
        .get_data()
    )
    print("[result]", result)

    assert agent.activated_session is not None
    print("[recorded turns in session]")
    for i, msg in enumerate(agent.activated_session.full_context):
        print(f"  {i + 1}. {msg.role}: {msg.content[:120]}")

    # Reset to default (record everything) for the next demo.
    agent.set_settings("session.input_keys", None)
    agent.set_settings("session.reply_keys", None)


# selective_recording()


## 4. Export and restore a session
#
# get_json_session() serialises the full conversation history to a JSON string.
# load_json_session() restores it into a new Session object.
# This enables persistence across process restarts or transfer between services.

def export_and_restore():
    agent.activate_session(session_id="demo-export")
    agent.input("My project name is Orion and the deadline is end of Q3.").streaming_print()

    assert agent.activated_session is not None
    snapshot = agent.activated_session.get_json_session()
    print(f"\n[Exported {len(snapshot)} bytes of session JSON]")

    # Restore into a new Session object with a different ID.
    restored = Session(settings=agent.settings)
    restored.load_json_session(snapshot)
    restored.id = "demo-export-restored"
    agent.sessions["demo-export-restored"] = restored
    agent.activate_session(session_id="demo-export-restored")

    print("[Restored session — recall test]")
    agent.input("What is my project name and deadline?").streaming_print()


# export_and_restore()


# All functions are commented out — uncomment one to run with a local Ollama model.
#
# Expected outputs (content is variable, structure is stable):
#
# session_on_off():
#   [Session ON]  → model recalls "indigo" correctly
#   [Session OFF] → model says it has no previous context
#
# session_isolation():
#   [project-beta]  → "Beta, Rust"
#   [project-alpha] → "Alpha, Go"
#
# selective_recording():
#   full_context has 2 entries: user recorded {topic, question} only;
#   assistant recorded {summary, keywords} only; request_id and timestamp absent.
#
# export_and_restore():
#   Restored session recalls "Orion" and "end of Q3" correctly.
#
# How it works:
# activate_session(session_id) attaches a named Session to the agent.  After each
# request the agent appends the user turn and model reply to session.full_context.
# deactivate_session() detaches the session but keeps it in agent.sessions for later.
# session_id isolation: each ID owns a separate Session object; switching IDs atomically
# switches context without mixing histories.
# input_keys / reply_keys filter which parts of the prompt and response are recorded,
# so ephemeral fields (timestamps, trace IDs) never appear in the history.
# get_json_session() / load_json_session() round-trip the full_context to/from JSON,
# enabling persistence in a database or file system between process restarts.
