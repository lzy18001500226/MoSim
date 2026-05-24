from _shared import create_deepseek_agent, print_action_results, print_response


agent = create_deepseek_agent(
    "Use available actions whenever they can produce an exact answer. "
    "For arithmetic, call the action before you reply."
)


@agent.action_func
def add_invoice_amounts(first_amount: int, second_amount: int) -> int:
    """Add two invoice amounts and return the exact integer total."""
    return first_amount + second_amount


if __name__ == "__main__":
    agent.use_actions(add_invoice_amounts)
    agent.input(
        "Use the action to calculate 17850 + 42675, then answer with the total and one short sentence."
    )
    records = agent.get_action_result()
    print_action_results(records)
    response = agent.get_response()
    print_response(response)

# Expected key output after configuring DeepSeek:
# [ACTION_RECORDS] includes a successful add_invoice_amounts call with result 60525.
# [ACTION_RESULTS_INJECTED_TO_REPLY] contains {"Add two invoice amounts...": 60525}.
# [MODEL_REPLY] mentions the total 60525.

# How it works:
# @agent.action_func decorates a plain Python function and registers it as an action
# with an auto-generated id and schema derived from type annotations and the docstring.
# agent.use_actions() activates it for the current request.
# get_action_result() asks the model to plan calls, executes them with the default
# FunctionActionExecutor, and returns ActionResult records.
# get_response() re-sends those records so the model can reference the exact result
# in its final reply.
#
# Flow:
# agent.input("...17850 + 42675...")
#   |
#   v
# model plans: add_invoice_amounts(first_amount=17850, second_amount=42675)
#   |
#   v
# FunctionActionExecutor calls Python function -> 60525
#   |
#   v
# ActionResult(action_id="add_invoice_amounts", result=60525) injected
#   |
#   v
# model reply: "The total is 60525."
