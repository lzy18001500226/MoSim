from agently import Agently

# These examples require a model that supports tool-calling (function-calling).
# qwen2.5:7b via Ollama includes tool-call support. Swap base_url/model for your provider.
Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)

agent = Agently.create_agent()
agent.set_action_loop(max_rounds=4)


## @agent.action_func — register a Python function as an action
#
# The decorator auto-generates the action schema from the function's
# type annotations and docstring, so the model knows what each action does
# and what arguments to pass.

@agent.action_func
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit, rounded to 2 decimal places."""
    return round(celsius * 9 / 5 + 32, 2)


@agent.action_func
def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert a temperature from Fahrenheit to Celsius, rounded to 2 decimal places."""
    return round((fahrenheit - 32) * 5 / 9, 2)


def demo_single_action():
    # Activate one action. The model must call it to produce the exact answer.
    agent.use_actions(celsius_to_fahrenheit)
    agent.input("Normal body temperature is 37°C. What is that in Fahrenheit? Use the action.")

    # Phase 1: model plans the call, Agently executes it, records are returned
    records = agent.get_action_result()
    print("[action records]", records)

    # Phase 2: model writes the final reply using the action result
    response = agent.get_response()
    print(response.result.get_text())


# demo_single_action()


def demo_two_actions():
    # With two actions available, the model selects the right direction automatically.
    agent.use_actions([celsius_to_fahrenheit, fahrenheit_to_celsius])
    agent.input(
        "The oven is set to 375°F and the room is 22°C. "
        "Convert each temperature to the other scale using the available actions."
    )
    records = agent.get_action_result()
    print("[action records]", records)
    response = agent.get_response()
    print(response.result.get_text())


# demo_two_actions()


# Expected output (demo_two_actions — exact values are deterministic, text varies):
# [action records] [ActionResult(action_id='fahrenheit_to_celsius', result=190.56, ...),
#                   ActionResult(action_id='celsius_to_fahrenheit', result=71.6, ...)]
# The oven is 375°F (190.56°C), and the room temperature is 22°C (71.6°F).
#
# How it works:
# @agent.action_func decorates a Python function and registers it with an auto-derived
# action_id (the function name) and schema from type annotations + docstring.
# agent.use_actions() activates the listed actions for the upcoming request.
# agent.get_action_result() asks the model to plan which actions to call, runs them
# through FunctionActionExecutor, and returns a list of ActionResult records.
# agent.get_response() feeds those records back so the model can cite exact values.
#
# Flow:
# agent.use_actions([celsius_to_fahrenheit, fahrenheit_to_celsius])
#   |
#   v
# agent.input("The oven is 375°F and the room is 22°C...")
#   |
#   v
# agent.get_action_result()
#   model plans: fahrenheit_to_celsius(fahrenheit=375.0) -> 190.56
#                celsius_to_fahrenheit(celsius=22.0)      -> 71.6
#   FunctionActionExecutor runs both calls
#   |
#   v
# agent.get_response()
#   model sees action results and writes:
#   "The oven is 375°F (190.56°C), and the room is 22°C (71.6°F)."
