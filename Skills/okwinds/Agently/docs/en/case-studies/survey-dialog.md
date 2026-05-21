---
title: Survey Dialog
description: Multi-turn survey with dynamic prompts, branching follow-ups, and stable session memory.
keywords: Agently, case study, survey, dialog, session, dynamic prompts
---

# Survey Dialog

> Languages: **English** · [中文](../../cn/case-studies/survey-dialog.md)

## The problem

Run a structured survey through a conversational interface. The model:

1. Asks the next question, given what's been answered so far.
2. Validates the answer (right type, in-range, on-topic).
3. Branches into follow-ups when the answer warrants it.
4. Knows when the survey is complete.
5. Produces a structured result at the end.

## The shape

A conversational agent with a session, plus a per-turn structured output that includes:

- the next question to ask
- the slot being filled
- whether the survey is complete

The application loop reads the model's structured output and decides whether to continue.

## Walkthrough

```python
from agently import Agently

agent = (
    Agently.create_agent()
    .role(
        "You are running a customer onboarding survey. "
        "Ask one question at a time. Branch into follow-ups when needed. "
        "End the survey when all required slots are filled.",
        always=True,
    )
    .info({
        "required_slots": ["company_size", "primary_use_case", "current_tools", "decision_timeline"],
        "format": "Reply only via the schema.",
    }, always=True)
)

agent.activate_session(session_id="survey-dialog")  # multi-turn

state = {"answers": {}}


def step(user_message: str):
    return (
        agent
        .info({"answers_so_far": state["answers"]}, always=False)
        .input(user_message)
        .output({
            "reply_to_user": (str, "What to show the user", True),
            "current_slot": (str, "Which slot is being filled", True),
            "captured": {
                "slot": (str, "Slot just captured (or empty)"),
                "value": "captured value (any type)",
            },
            "survey_complete": (bool, "True only when all required slots are captured", True),
        })
        .start()
    )


# Run
print("Hi! Let's get started. Ready?")
user_text = input("> ")
while True:
    result = step(user_text)
    print(result["reply_to_user"])

    captured = result.get("captured") or {}
    if captured.get("slot"):
        state["answers"][captured["slot"]] = captured.get("value")

    if result["survey_complete"]:
        break
    user_text = input("> ")

print("\nFinal answers:")
print(state["answers"])
```

## Why these choices

- **Per-turn structured output, not a free-form reply** — the application needs to know which slot was captured and whether the survey is done. Asking the model to format that in prose would be unreliable.
- **`info(answers_so_far, always=False)`** — the captured state changes every turn; passing it as request-only `info` means it's always current without polluting the agent's persistent prompt.
- **`info({"required_slots": [...]}, always=True)`** — the slot list doesn't change; pin it to the agent.
- **Session enabled** — the model needs to remember the conversation flow ("you said small/medium last turn, so I'll ask about pricing tier"). `activate_session()` handles that.
- **Branching driven by the model** — the model picks follow-up questions based on captured answers. The application doesn't need a hard-coded decision tree. Trade-off: less predictable than a hand-coded survey, but more natural conversation.
- **`survey_complete: bool`** — explicit termination. The application loop trusts this; the model is told only to set it when all required slots are filled.

## Variations

### Validate captured values before accepting

If a `value` should be one of an enum, use a custom `.validate(...)`:

```python
def value_check(result, ctx):
    captured = result.get("captured") or {}
    slot = captured.get("slot")
    value = captured.get("value")
    if slot == "decision_timeline" and value not in ("now", "this_quarter", "this_year", "exploring"):
        return {"ok": False, "reason": f"unknown timeline: {value}", "validator_name": "enum"}
    return True
```

See [Output Control](../requests/output-control.md).

### Custom summaries for very long surveys

For long surveys (20+ questions), register custom resize handlers that summarize older turns into `memo`:

```python
agent.set_settings("session.max_length", 12000)
agent.register_session_analysis_handler(analysis_handler)
agent.register_session_resize_handler("summarize_old_turns", resize_handler)
```

The default Session only trims the window; summarization logic comes from your handler. See [Session Memory](../requests/session-memory.md).

### Switch to TriggerFlow if branches are deep

If a single user answer triggers multi-step processing (lookup, validate, score), promote the per-turn handling to a TriggerFlow. The conversation layer stays in the agent loop; one flow runs per turn. See [TriggerFlow Orchestration Playbook](../playbooks/triggerflow-orchestration.md).

## Cross-links

- [Session Memory](../requests/session-memory.md) — multi-turn context, windowing, custom memo
- [Schema as Prompt](../requests/schema-as-prompt.md) — `survey_complete: bool` as an ensure'd field
- [Output Control](../requests/output-control.md) — `.validate(...)` for value checks
- [Context Engineering](../requests/context-engineering.md) — `info(always=True)` vs `always=False`
