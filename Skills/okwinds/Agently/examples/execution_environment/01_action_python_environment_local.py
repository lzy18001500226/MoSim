from pprint import pprint
from typing import Any, cast

from agently import Agently


ACTION_ID = "calculate_stats"


def build_agent():
    agent = Agently.create_agent()
    agent.enable_python(action_id=ACTION_ID, expose_to_model=False)
    return agent


def main():
    agent = build_agent()
    result = agent.action.execute_action(
        ACTION_ID,
        {
            "python_code": [
                "numbers = [15, 23, 42, 8, 12]",
                "result = {",
                "    'average': sum(numbers) / len(numbers),",
                "    'count': len(numbers),",
                "    'max_minus_min_gap': max(numbers) - min(numbers),",
                "}",
            ]
        },
    )

    print("[ACTION_RESULT]")
    pprint(result)

    result_data = cast(dict[str, Any], result.get("data"))
    assert result.get("status") == "success"
    assert result_data["result"] == {
        "average": 20.0,
        "count": 5,
        "max_minus_min_gap": 34,
    }

    action_call_handles = Agently.execution_environment.list(scope="action_call")
    print("[ACTION_CALL_HANDLES_AFTER_RELEASE]")
    pprint(action_call_handles)
    assert action_call_handles == []


if __name__ == "__main__":
    main()

# Expected key output:
# [ACTION_RESULT] has status="success" and data["result"] equals
# {"average": 20.0, "count": 5, "max_minus_min_gap": 34}.
# [ACTION_CALL_HANDLES_AFTER_RELEASE] prints [].

# How it works:
# agent.enable_python(action_id=ACTION_ID, expose_to_model=False) registers a managed
# Python sandbox action without exposing it to the model (direct execution only).
# execute_action() calls the action directly with python_code as a list of code lines.
# The sandbox runs the code, reads the `result` variable, and returns it.
# After the call, Agently.execution_environment.list(scope="action_call") returns []
# because action-call-scoped handles are released automatically when the call ends.
#
# Flow:
# agent.enable_python(action_id=ACTION_ID, expose_to_model=False)
#   |
#   v
# agent.action.execute_action(ACTION_ID, {"python_code": [...]})
#   | (no model call)
#   v
# ManagedPythonEnvironment runs code -> result = {"average":20.0,"count":5,"max_minus_min_gap":34}
#   |
#   v
# handle released (scope="action_call") -> list(scope="action_call") == []
