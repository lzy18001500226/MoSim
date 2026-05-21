from typing import Any
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:7b",
        "model_type": "chat",
    },
).set_settings("debug", True)

agent = Agently.create_agent()


@agent.action_func
async def add(a: int, b: int) -> int:
    """
    Return result of `a(int)` add `b(int)`
    """
    import asyncio

    await asyncio.sleep(1)
    print(a, "+", b, "=", a + b)
    return a + b


@agent.action_func
async def python_code_executor(
    python_code: str,
):
    """
    Execute Python code and get final result.
    Use print() to throw processing results.
    """
    import io
    import asyncio
    import contextlib

    result_io = io.StringIO()
    local_vars: dict[str, Any] = {}

    try:
        with contextlib.redirect_stdout(result_io):
            compiled = compile(python_code, "<string>", "exec")
            exec(compiled, {}, local_vars)

            final_result = None

            if "main" in local_vars and asyncio.iscoroutinefunction(local_vars["main"]):
                final_result = await local_vars["main"]()

            else:
                try:
                    compiled_eval = compile(python_code, "<string>", "eval")
                except SyntaxError:
                    pass
                else:
                    final_result = eval(compiled_eval, {}, local_vars)

    except Exception as e:
        return {"code": python_code[:1000], "stdout": result_io.getvalue(), "result": None, "error": repr(e)}

    return {"code": python_code[:1000], "stdout": result_io.getvalue(), "result": final_result, "error": None}


# Try provide two actions for agent
agent.use_actions([add, python_code_executor])
# Try just use code executor
# agent.use_actions(python_code_executor)
# Try use nothing
# pass


@agent.auto_func
def calculate(formula: str) -> int:
    """
    Return result of {formula}.
    MUST USE ACTIONS TO ENSURE THE ANSWER IS ACTUAL NO MATTER WHAT.
    """
    ...


result = calculate("3333+6666=?")
print(result)

# Expected output shape (content is variable — requires local Ollama):
# 3333 + 6666 = 9999        (printed by the add action during execution)
# 9999                      (final return value of calculate())
#
# How it works:
# @agent.action_func registers a Python function as an Agently action — here both
# add (an async integer adder with a 1-second sleep) and python_code_executor
# (a sandboxed Python eval loop).
# @agent.auto_func decorates a stub function whose docstring is used as the model
# instruction.  Calling calculate("3333+6666=?") triggers an agent request that
# uses the registered actions to compute the answer, then returns it as the
# function's return value — the stub body (...) is never executed.
