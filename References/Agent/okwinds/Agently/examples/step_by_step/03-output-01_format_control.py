from agently import Agently

agent = Agently.create_agent()

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## Agently-Styled Output Data Format Control
def agently_output_format_control():
    result = (
        agent.input("Please explain recursion")
        # .output() declares the structured schema you want back.
        # Agently enforces this at the framework level — no dependency on
        # model-side "response_format" parameters or JSON mode.
        .output(
            {
                # Tuple[type, description, required?]
                # required=True: field is re-requested if missing (up to max_retries).
                "thinking": (str, "Think about how you would answer this question?", True),
                "explanation": (str, "Concept explanation", True),
                # Nested lists and dicts are fully supported.
                "example_codes": ([(str, "Example code")], "Provide at least 2 example codes"),
                "practices": (
                    [
                        {
                            "question": (str, "Practice question", True),
                            "answer": (str, "Reference answer", True),
                        }
                    ],
                    "Provide at least 2 practice questions, different from the example codes",
                ),
            }
        ).start(
            max_retries=1,           # default: 3
            raise_ensure_failure=False,  # default: True
        )
    )
    for item in result["practices"]:
        print("[Question]:\n", item["question"], "\n\n[Answer]:\n", item["answer"], "\n\n=======\n\n")


# agently_output_format_control()


## Output Field Ordering — drives CoT-style reasoning
#
# .output() preserves dict insertion order.  Fields generated earlier are visible
# to the model when it writes later fields — like a scratchpad that builds on itself.

def output_order_cot_control():
    result = (
        agent.input(
            "Where can I find the release dates for Dark Souls 3 and GTA6 and buy/pre-order them?"
        )
        .output(
            {
                # Step 1: enumerate known vs. uncertain facts
                "info_list": [
                    {
                        "topic": (str, "Which game/subject this info is about", True),
                        "key_fact": (str, "Key fact needed to answer the question", True),
                        "is_known": (bool, "Whether you are confident about this key fact", True),
                    }
                ],
                # Step 2: derive summaries from the list already generated above
                "sure_info": (str, "Only explain the key facts you are confident about"),
                "uncertain": (str, "List the key facts you are not confident about"),
            }
        )
        # If you swap the order (sure_info before info_list), the model answers
        # directly and skips the per-fact enumeration step.
        .start(max_retries=1, raise_ensure_failure=False)
    )
    print(result)


# output_order_cot_control()


## Self-Critique via Output Ordering
#
# action -> can_do -> can_do_explain -> fixed_action
# Each field references the previous one, creating an in-request critique loop.

def role_thinking_self_critique():
    result = (
        agent.input(
            {
                "target": "enter a cave blocked by a huge boulder",
                "items": ["spoon", "chopsticks"],
            }
        )
        .output(
            {
                "action": (str, "Propose the boldest way to complete {target} using {items}", True),
                "can_do": (bool, "Use common sense to judge if {action} is feasible", True),
                "can_do_explain": (str, "If {can_do} is false, explain why"),
                "fixed_action": (
                    str,
                    "If {can_do} is false, revise the plan using {items} and {can_do_explain}",
                    True,
                ),
            }
        )
        .start(max_retries=1, raise_ensure_failure=False)
    )
    print(result)


# role_thinking_self_critique()


# All functions are commented out — uncomment one to run with a local Ollama model.
# Model output is non-deterministic; the returned dict keys are stable.
#
# How it works:
# .output({...}) declares a typed schema enforced by Agently's parser, not the model.
# Each value is a Tuple[type, description] or Tuple[type, description, required].
# required=True fields are re-requested if absent (up to max_retries attempts).
# Nested lists ([...]) and nested dicts ({...}) are fully supported.
#
# Field ordering drives chain-of-thought:
# The model streams fields in declaration order.  A later field's description can
# reference earlier fields via {field_name} placeholders — the model has already
# written those fields by the time it reaches the current one, so it naturally
# builds on them rather than jumping to a conclusion.
#
# Self-critique pattern (role_thinking_self_critique):
# action -> can_do -> can_do_explain -> fixed_action
# The model proposes an action, judges feasibility, explains the flaw, then revises —
# all in one request, driven entirely by field order and description cross-references.
#
# Flow:
# agent.input({target, items})
#   |
#   v
# .output({action, can_do, can_do_explain, fixed_action})
#   model streams: action="Use spoon as lever" -> can_do=False
#     -> can_do_explain="A spoon cannot lever a boulder"
#     -> fixed_action="Create a wedge using stacked chopsticks..."
#   |
#   v
# .start() returns the parsed dict with all four fields
