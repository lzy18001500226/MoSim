import asyncio
from pprint import pprint
from typing import Any, cast

from agently import Agently, TriggerFlow, TriggerFlowRuntimeData


async def main():
    flow = TriggerFlow(name="example-triggerflow-managed-python")

    async def calculate(data: TriggerFlowRuntimeData):
        sandbox = cast(Any, data.require_resource("managed_python"))
        result = sandbox.run(
            "input_value = " + repr(int(data.value)) + "\n"
            "result = base + input_value\n"
        )["result"]
        data.state.set("answer", result)

    flow.to(calculate)

    result = await flow.async_start(
        2,
        execution_environments=[
            {
                "kind": "python",
                "scope": "execution",
                "resource_key": "managed_python",
                "config": {"base_vars": {"base": 40}},
            }
        ],
    )

    print("[TRIGGERFLOW_RESULT]")
    pprint(result)
    assert result == {"answer": 42}

    execution_handles = Agently.execution_environment.list(scope="execution")
    print("[EXECUTION_HANDLES_AFTER_RELEASE]")
    pprint(execution_handles)
    assert execution_handles == []


if __name__ == "__main__":
    asyncio.run(main())

# Expected key output:
# [TRIGGERFLOW_RESULT] prints {"answer": 42}.
# [EXECUTION_HANDLES_AFTER_RELEASE] prints [] after the execution-scoped Python resource is released.

# How it works:
# execution_environments=[{kind:"python", scope:"execution", resource_key:"managed_python",
# config:{base_vars:{base:40}}}] declares a Python sandbox that persists across the entire
# TriggerFlow execution (scope="execution"), not just one action call.
# data.require_resource("managed_python") retrieves the sandbox handle inside a chunk.
# sandbox.run(code)["result"] executes code with base=40 in scope; input_value=2 → answer=42.
# After async_close(), execution-scoped handles are released automatically.
#
# Flow:
# async_start(2, execution_environments=[...])
#   | Python sandbox created with base_vars={base:40}, scope="execution"
#   v
# calculate: data.require_resource("managed_python")
#   sandbox.run("input_value=2\nresult=base+input_value") -> 42
#   data.state.set("answer", 42)
#   |
#   v
# async_close() -> {"answer": 42}
# handle released -> list(scope="execution") == []
