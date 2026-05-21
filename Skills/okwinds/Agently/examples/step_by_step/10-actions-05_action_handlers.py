import asyncio
import time

from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)


## Action Handler Injection — intercept planning and execution phases
#
# The action pipeline has two injectable phases:
#
#   PLANNING PHASE:  the model (or your handler) decides which actions to call next.
#   EXECUTION PHASE: Agently (or your handler) runs those calls and returns results.
#
# Injecting a handler at either phase lets you:
#   • Audit or log planned calls before execution
#   • Override model decisions with deterministic Python logic
#   • Add pre/post hooks around execution (timing, validation, retries)
#
# API:
#   agent.register_action_planning_handler(fn)   — replaces the model-driven planner
#   agent.register_action_execution_handler(fn)  — wraps action execution


# --- Mock action functions ---

def lookup_price(item: str) -> dict:
    """Look up the current price of a product by name."""
    catalog = {"laptop": 1299.99, "monitor": 649.99, "keyboard": 89.99, "mouse": 29.99}
    price = catalog.get(item.lower())
    return {"item": item, "price": price} if price else {"error": f"Not found: {item}"}


def apply_discount(price: float, discount_pct: float) -> dict:
    """Apply a percentage discount to a price and return the discounted amount."""
    discounted = round(price * (1 - discount_pct / 100), 2)
    saved = round(price - discounted, 2)
    return {"original": price, "discount_pct": discount_pct, "discounted": discounted, "saved": saved}


agent = Agently.create_agent()
agent.set_action_loop(max_rounds=4)

agent.action.register_action(
    action_id="lookup_price",
    desc="Look up the current price of a product in the catalog.",
    kwargs={"item": (str, "Product name, e.g. 'laptop', 'monitor'")},
    func=lookup_price,
    expose_to_model=True,
)
agent.action.register_action(
    action_id="apply_discount",
    desc="Apply a percentage discount to a price and return the final amount.",
    kwargs={
        "price": (float, "Original price"),
        "discount_pct": (float, "Discount percentage, e.g. 15 for 15%"),
    },
    func=apply_discount,
    expose_to_model=True,
)


## Style A — Augmented planning handler
#
# Delegates to the model's default planner but intercepts the decision
# to log, audit, or filter the planned action calls.

async def auditing_planning_handler(context, request):
    """Log each planning round and delegate the actual decision to the model."""
    round_index = context.get("round_index", 0)
    done = context.get("done_plans", [])
    print(f"[Planning] Round {round_index}, actions completed so far: {len(done)}")

    # Delegate to the built-in model-based planning handler
    runtime = context["runtime"]
    decision = await runtime._default_planning_handler(context, request)

    next_action = decision.get("next_action", "response")
    calls = decision.get("action_calls", decision.get("execution_commands", []))
    if isinstance(calls, list) and calls:
        for call in calls:
            print(f"[Planning] Approved: {call.get('action_id')}({call.get('action_input', {})})")
    else:
        print(f"[Planning] Decision: {next_action} (no further actions)")

    return decision


def demo_augmented_planning():
    agent.register_action_planning_handler(auditing_planning_handler)
    agent.use_actions(["lookup_price", "apply_discount"])
    agent.input(
        "What is the price of a laptop after a 20% discount? Use the actions."
    )
    records = agent.get_action_result()
    response = agent.get_response()
    print(response.result.get_text())
    agent.register_action_planning_handler(None)  # reset to default


# demo_augmented_planning()


## Style B — Scripted planning handler
#
# Replaces the model entirely for planning: a Python function deterministically
# sequences actions based on round_index and what's been completed.
# Useful for fixed multi-step workflows where model planning is unnecessary.

def scripted_planning_handler(context, request):
    """Scripted two-step plan: first lookup, then apply discount. No model involved."""
    done = context.get("done_plans", [])

    if len(done) == 0:
        return {
            "next_action": "execute",
            "action_calls": [{
                "purpose": "Look up the laptop price",
                "action_id": "lookup_price",
                "action_input": {"item": "laptop"},
                "todo_suggestion": "Apply a 15% discount to the retrieved price next",
            }],
        }

    if len(done) == 1:
        price = done[0].get("result", {}).get("price", 0)
        return {
            "next_action": "execute",
            "action_calls": [{
                "purpose": "Apply 15% discount to the laptop price",
                "action_id": "apply_discount",
                "action_input": {"price": price, "discount_pct": 15},
                "todo_suggestion": "Return the discounted price to the user",
            }],
        }

    return {"next_action": "response", "action_calls": []}


def demo_scripted_planning():
    agent.register_action_planning_handler(scripted_planning_handler)
    agent.use_actions(["lookup_price", "apply_discount"])
    agent.input(
        "What is the discounted price of a laptop? Use the scripted plan."
    )
    records = agent.get_action_result()
    print("[action records]", records)
    response = agent.get_response()
    print(response.result.get_text())
    agent.register_action_planning_handler(None)


# demo_scripted_planning()


## Execution handler — wrap action execution with timing and logging
#
# The execution handler receives the list of action_calls the planner decided on
# and is responsible for running them and returning ActionResult records.
# Use it to add pre/post hooks: timing, logging, validation, or retry logic.

async def timed_execution_handler(context, request):
    """Run each action call with elapsed-time logging."""
    action = context["action"]
    settings = context["settings"]
    action_calls = request.get("action_calls", [])

    async def run_timed(call):
        action_id = call.get("action_id", "")
        action_input = call.get("action_input", {})
        print(f"[Execution] Starting: {action_id}({action_input})")
        t0 = time.perf_counter()
        result = await action.async_execute_action(
            action_id,
            action_input,
            settings=settings,
            purpose=call.get("purpose", f"Execute {action_id}"),
            todo_suggestion=call.get("todo_suggestion", ""),
        )
        elapsed = time.perf_counter() - t0
        print(f"[Execution] Done:     {action_id} in {elapsed:.4f}s — result: {result.get('result')}")
        return result

    return await asyncio.gather(*[run_timed(c) for c in action_calls])


def demo_execution_handler():
    agent.register_action_planning_handler(scripted_planning_handler)
    agent.register_action_execution_handler(timed_execution_handler)
    agent.use_actions(["lookup_price", "apply_discount"])
    agent.input("What is the 15% discounted price of a laptop? Use actions.")
    records = agent.get_action_result()
    response = agent.get_response()
    print(response.result.get_text())
    agent.register_action_planning_handler(None)
    agent.register_action_execution_handler(None)


# demo_execution_handler()


# Expected output (demo_execution_handler):
# [Planning] Round 0, actions completed so far: 0
# [Execution] Starting: lookup_price({'item': 'laptop'})
# [Execution] Done:     lookup_price in 0.0002s — result: {'item': 'laptop', 'price': 1299.99}
#
# [Planning] Round 1, actions completed so far: 1
# [Execution] Starting: apply_discount({'price': 1299.99, 'discount_pct': 15})
# [Execution] Done:     apply_discount in 0.0001s — result: {'original': 1299.99, ..., 'discounted': 1104.99}
#
# [Planning] Round 2 → next_action: response
# A laptop costs $1299.99; after a 15% discount you pay $1104.99 (saving $195.00).
#
# How it works:
# Planning handler (Augmented):
#   receives context={round_index, done_plans, ...} + request={action_list}
#   delegates to runtime._default_planning_handler() for model-based decisions
#   logs/filters the resulting action_calls before returning them
#
# Planning handler (Scripted):
#   inspects done_plans to determine what step we're on
#   returns hard-coded action_calls without any model call
#   returns next_action='response' when all steps are done
#
# Execution handler:
#   receives context={action, settings, ...} + request={action_calls, concurrency}
#   runs each action call via action.async_execute_action() with timing wraparound
#   returns list[ActionResult] — same format expected by get_response()
#
# Flow (demo_execution_handler with scripted planning):
# agent.get_action_result()
#   Round 0: scripted_planning_handler -> lookup_price(laptop)
#            timed_execution_handler  -> result: {price: 1299.99}
#   Round 1: scripted_planning_handler -> apply_discount(1299.99, 15)
#            timed_execution_handler  -> result: {discounted: 1104.99}
#   Round 2: scripted_planning_handler -> next_action='response'
# agent.get_response()
#   model reads action records -> final reply
