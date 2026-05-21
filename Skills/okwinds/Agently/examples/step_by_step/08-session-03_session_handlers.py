from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)

agent = Agently.create_agent()


## Session Handler Injection — custom analysis and resize strategies
#
# A session maintains two data structures:
#   full_context   — every message ever recorded in this session (never trimmed)
#   context_window — the slice sent to the model each request (can be trimmed)
#
# When the context grows too large, Agently calls a two-phase pipeline:
#
#   ANALYSIS PHASE: decide whether the window needs to be resized.
#     analysis_handler(full_context, context_window, memo, settings) -> str | None
#     • Return a strategy name (str) to trigger that resize strategy.
#     • Return None to leave the window as-is.
#
#   RESIZE PHASE: shrink the window using the chosen strategy.
#     resize_handler(full_context, context_window, memo, settings)
#       -> (new_full_context | None, new_context_window | None, new_memo | None)
#     • new_full_context: pass None to leave full_context unchanged.
#     • new_context_window: the trimmed window that will be sent to the model.
#     • new_memo: arbitrary data to carry forward (e.g., a summary of dropped turns).
#
# API:
#   session.register_analysis_handler(fn)         — sets the analysis handler
#   session.register_resize_handler(name, fn)     — registers a named resize strategy
#   agent.activate_session(session_id=...)        — attach a session to the agent
#   agent.activated_session                       — the current session object


## Part 1 — Simple keep-last-N resize handler
#
# Strategy: once the window exceeds MAX_TURNS turns, keep only the last N turns.
# The analysis handler triggers the strategy; the resize handler implements it.

MAX_TURNS = 4      # trigger resize when window exceeds this
KEEP_TURNS = 2     # keep this many recent turns after resize


def demo_keep_last_n():
    agent.activate_session(session_id="demo-keep-last-n")
    session = agent.activated_session
    assert session is not None

    def analysis_handler(full_context, context_window, memo, session_settings):
        """Trigger 'keep_last_n' when context_window exceeds MAX_TURNS messages."""
        if len(context_window) > MAX_TURNS:
            print(f"  [Analysis] Window is {len(context_window)} turns → triggering 'keep_last_n'")
            return "keep_last_n"
        return None

    def keep_last_n_handler(full_context, context_window, memo, session_settings):
        """Keep only the most recent KEEP_TURNS messages from the window."""
        kept = list(context_window[-KEEP_TURNS:])
        new_memo = {"dropped": len(context_window) - len(kept), "kept": len(kept)}
        print(f"  [Resize] Dropped {new_memo['dropped']} turns, kept {new_memo['kept']}")
        return None, kept, new_memo

    session.register_analysis_handler(analysis_handler)
    session.register_resize_handler("keep_last_n", keep_last_n_handler)

    print("Seeding conversation history...")
    for i in range(1, 6):
        agent.add_chat_history({"role": "user",      "content": f"User message {i}"})
        agent.add_chat_history({"role": "assistant", "content": f"Assistant reply {i}"})

    print(f"full_context:   {len(session.full_context)} messages")
    print(f"context_window: {len(session.context_window)} messages")
    print(f"memo:           {session.memo}")


# demo_keep_last_n()


## Part 2 — Async AI-summarization resize handler
#
# Strategy: when the window grows beyond MAX_TURNS, keep the last KEEP_TURNS messages
# and use an LLM call to summarize the dropped portion into a `memo`.
# On subsequent requests, the memo is injected as context so the model retains key facts.
# agent.create_temp_request() creates a lightweight one-off request that shares the
# agent's model settings but does not affect the session or its chat history.


def demo_ai_summarization():
    agent.activate_session(session_id="demo-ai-summary")
    session = agent.activated_session
    assert session is not None

    def analysis_handler(full_context, context_window, memo, session_settings):
        """Trigger 'summarize_old' when the window exceeds MAX_TURNS messages."""
        if len(context_window) > MAX_TURNS:
            print(f"  [Analysis] Window has {len(context_window)} turns → triggering 'summarize_old'")
            return "summarize_old"
        return None

    async def summarize_old_handler(full_context, context_window, memo, session_settings):
        """Drop old turns and summarize them with an LLM into memo."""
        to_drop = list(context_window[:-KEEP_TURNS])
        kept = list(context_window[-KEEP_TURNS:])

        print(f"  [Resize] Summarizing {len(to_drop)} dropped turns via LLM...")

        # agent.create_temp_request() creates an isolated request that:
        #   • inherits the agent's model settings
        #   • does NOT record into any session
        #   • is safe to call from inside an async resize handler
        memo_request = agent.create_temp_request()
        (
            memo_request
            .input({
                "dropped_messages": [{"role": m.role, "content": m.content} for m in to_drop],
                "existing_memo":    memo,
            })
            .instruct([
                "Summarize the dropped conversation turns into concise key points.",
                "Merge with existing_memo if any prior key points are provided.",
            ])
            .output({
                "key_points": {
                    "<topic>": (str, "Key fact or decision from the dropped turns"),
                    "...": "...",
                }
            })
        )
        new_memo = await memo_request.async_start(ensure_keys=["key_points"])
        print(f"  [Resize] Summary memo: {new_memo.get('key_points', {})}")

        return None, kept, new_memo.get("key_points", {})

    session.register_analysis_handler(analysis_handler)
    session.register_resize_handler("summarize_old", summarize_old_handler)

    print("[Turn 1]")
    agent.input("My project is called Aurora and it's a real-time data pipeline.").streaming_print()

    print("[Turn 2]")
    agent.input("The main language is Python and we use Kafka for messaging.").streaming_print()

    print("[Turn 3]")
    agent.input("Our SLA requires < 500 ms end-to-end latency.").streaming_print()

    print("[Session state after turn 3]")
    print(f"  full_context:   {len(session.full_context)} messages")
    print(f"  context_window: {len(session.context_window)} messages")
    print(f"  memo:           {session.memo}")

    print("[Turn 4 — tests that memo is available to the model]")
    agent.input("Based on our conversation, what is the project name and language?").streaming_print()


# demo_ai_summarization()


# Expected output (demo_ai_summarization — content varies, structure is stable):
# [Turn 1] ... reply acknowledging Aurora ...
# [Turn 2] ... reply acknowledging Python + Kafka ...
# [Turn 3]
#   [Analysis] Window has 6 turns → triggering 'summarize_old'
#   [Resize] Summarizing 4 dropped turns via LLM...
#   [Resize] Summary memo: {'project': 'Aurora — real-time data pipeline', 'language': 'Python', 'messaging': 'Kafka'}
#   ... reply acknowledging latency SLA ...
#
# [Session state after turn 3]
#   full_context:   6 messages
#   context_window: 2 messages  (keep_last 2 after resize)
#   memo:           {'project': 'Aurora...', 'language': 'Python', ...}
#
# [Turn 4 — tests that memo is available to the model]
#   The project is Aurora (real-time data pipeline) and the language is Python.
#   (model recalls facts from memo even though those turns are no longer in the window)
#
# How it works:
# After every add_chat_history() or model reply, Agently calls analysis_handler().
# If analysis_handler returns a strategy name, the matching resize_handler runs.
# The resize handler returns (new_full_context, new_window, new_memo):
#   new_full_context=None: full history is preserved unchanged (audit trail).
#   new_window=kept:       only recent turns are sent to the model.
#   new_memo:              carries facts forward; Agently injects it into the next
#                          request automatically so the model can reference it.
# The async variant can call await agent.create_temp_request().async_start()
# to summarize dropped turns with the LLM before discarding them.
#
# Flow (demo_ai_summarization):
# turn 1, 2: window <= MAX_TURNS → analysis returns None → no resize
# turn 3: window > MAX_TURNS → analysis returns 'summarize_old'
#   summarize_old_handler:
#     drops turns 1...(n - KEEP_TURNS)
#     LLM call via create_temp_request() → key_points memo
#     returns (None, kept_turns, key_points_dict)
#   context_window = kept_turns; memo = key_points_dict
# turn 4: model receives memo in prompt → answers correctly despite short window
