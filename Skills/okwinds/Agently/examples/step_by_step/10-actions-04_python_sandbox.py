from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)

agent = Agently.create_agent()
agent.set_action_loop(max_rounds=4)


## Python sandbox action — let the model write and execute Python code
#
# Instead of registering a fixed function, a sandbox action lets the model
# generate arbitrary Python code that Agently runs in an isolated interpreter.
# The model must store its final answer in a variable named `result`.
# This is useful for one-off computations, data transformations, or any task
# where the exact code needed depends on the input.

agent.action.register_python_sandbox_action(
    action_id="run_python",
    desc=(
        "Execute a Python code snippet inside an isolated sandbox environment. "
        "Always assign the final answer to the variable `result` before the code ends."
    ),
    expose_to_model=True,
)


def demo_python_sandbox():
    agent.use_actions("run_python")
    agent.input(
        "I have five product prices: 29.99, 14.50, 89.00, 5.25, 49.75. "
        "Use the Python sandbox to compute: the total, the average, and the price range "
        "(max minus min). Return all three values."
    )
    records = agent.get_action_result()
    print("[action records]", records)
    response = agent.get_response()
    print(response.result.get_text())


# demo_python_sandbox()


def demo_python_sandbox_sorting():
    agent.use_actions("run_python")
    agent.input(
        "Sort these words alphabetically and count unique first letters: "
        "['mango', 'apple', 'banana', 'avocado', 'blueberry', 'melon', 'cherry']. "
        "Use the Python sandbox."
    )
    records = agent.get_action_result()
    print("[action records]", records)
    response = agent.get_response()
    print(response.result.get_text())


# demo_python_sandbox_sorting()


# Expected output (demo_python_sandbox — values are deterministic, text varies):
# [action records] [ActionResult(action_id='run_python', model_digest=..., artifact_refs=[...])]
# Total: 188.49
# Average: 37.70
# Price range (max - min): 83.75
#
# How it works:
# register_python_sandbox_action() creates a special action that accepts a Python code
# string from the model. The code is executed inside an isolated Python interpreter
# with no network or filesystem access. The value of the `result` variable at the end
# of execution becomes the action's return value.
# The model writes computation as Python code instead of calling a fixed function —
# useful when the exact logic depends on the specific question asked.
# The ActionResult contains model_digest (a summary the model can read) and
# artifact_refs (pointers to the stored code and stdout for audit purposes).
#
# Flow:
# agent.use_actions("run_python")
# agent.input("Compute total, average, range for [29.99, 14.50, ...]")
# agent.get_action_result()
#   model plans: run_python(code="""
#       prices = [29.99, 14.50, 89.00, 5.25, 49.75]
#       result = {'total': sum(prices), 'average': sum(prices)/len(prices),
#                 'range': max(prices) - min(prices)}
#   """)
#   PythonSandboxExecutor runs the code
#   result = {'total': 188.49, 'average': 37.698, 'range': 83.75}
#   |
#   v
# agent.get_response()
#   model reads model_digest and replies with all three computed values
