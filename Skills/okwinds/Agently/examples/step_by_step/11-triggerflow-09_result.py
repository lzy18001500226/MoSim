import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def triggerflow_close_result_demo():
    flow = TriggerFlow(name="step-09-execution-result")

    async def worker(data: TriggerFlowRuntimeData):
        await data.async_set_state("output", f"work({data.input})")

    flow.to(worker)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start("task-1")
    snapshot = await execution.async_close()
    result = execution.result
    assert snapshot is not None
    assert snapshot["output"] == "work(task-1)"
    assert result.get_state("output") == "work(task-1)"
    assert result.get_meta()["flow_name"] == "step-09-execution-result"
    print({"snapshot": snapshot, "meta": result.get_meta()})


async def triggerflow_set_result_compat_demo():
    flow = TriggerFlow(name="step-09-set-result-compat")

    async def worker(data: TriggerFlowRuntimeData):
        await data.async_set_state("output", f"work({data.input})")
        data.set_result({"compat_result": "explicit result still overrides close snapshot"})

    flow.to(worker)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start("task-2")
    snapshot = await execution.async_close()
    result = execution.result
    assert snapshot is not None
    final_result = await result.async_get_final_result()
    assert snapshot["output"] == "work(task-2)"
    assert snapshot["$final_result"] == {
        "compat_result": "explicit result still overrides close snapshot",
    }
    assert final_result == {"compat_result": "explicit result still overrides close snapshot"}
    print({"snapshot": snapshot, "final_result": final_result})


async def main():
    await triggerflow_close_result_demo()
    await triggerflow_set_result_compat_demo()


if __name__ == "__main__":
    asyncio.run(main())

# Expected output:
# Demo 1 (close snapshot + result object):
#   {'snapshot': {'output': 'work(task-1)'},
#    'meta': {'flow_name': 'step-09-execution-result', 'execution_id': ..., ...}}
#
# Demo 2 (set_result compat override):
#   {'snapshot': {'output': 'work(task-2)',
#                 '$final_result': {'compat_result': 'explicit result still overrides close snapshot'}},
#    'final_result': {'compat_result': 'explicit result still overrides close snapshot'}}
#
# How it works:
# Two result-access paths exist side by side:
#
# 1. Close snapshot  — async_close() returns the raw state dict (all async_set_state() writes).
#    execution.result is an ExecutionResult object giving typed access to the same data:
#    result.get_state("key") and result.get_meta() (flow_name, execution_id, lifecycle_state, …).
#
# 2. set_result() compat API  — data.set_result(obj) writes obj under the special key
#    "$final_result" in the snapshot.  result.async_get_final_result() extracts it.
#    Regular state keys are preserved alongside "$final_result" in the snapshot.
#    This API exists for compatibility with older consumers that expect a single top-level result
#    rather than the full state dict.
