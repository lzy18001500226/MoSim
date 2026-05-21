import asyncio

from agently import TriggerFlow, TriggerFlowRuntimeData


async def triggerflow_save_and_resume_state_demo():
    flow = TriggerFlow(name="step-14-execution-state-resume")

    async def prepare(data: TriggerFlowRuntimeData):
        await data.async_set_state("ticket", {"id": "T-001", "topic": data.input})

    async def finalize(data: TriggerFlowRuntimeData):
        await data.async_set_state(
            "final",
            {
                "ticket": data.get_state("ticket"),
                "feedback": data.input,
            },
        )

    flow.to(prepare)
    flow.when("UserFeedback").to(finalize)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start("refund request")
    saved_state = execution.save()

    restored_execution = flow.create_execution(auto_close=False)
    restored_execution.load(saved_state)
    await restored_execution.async_emit("UserFeedback", {"approved": True})
    state = await restored_execution.async_close()
    assert state["final"]["feedback"]["approved"] is True
    print(state["final"])


if __name__ == "__main__":
    asyncio.run(triggerflow_save_and_resume_state_demo())

# Expected output:
# {'ticket': {'id': 'T-001', 'topic': 'refund request'}, 'feedback': {'approved': True}}
#
# How it works:
# execution.save() serializes the current execution state, pending event queues, and
# interrupt positions to a plain Python dict (JSON-serializable).
# restored_execution.load(saved_state) reconstructs the same snapshot on a fresh execution
# object bound to the same flow definition.  From there, emitting "UserFeedback" on the
# restored execution continues exactly where the original left off.
# This is the foundation for cross-process handoff: serialize after async_start(), store
# the dict in a DB or queue, deserialize in a different process, resume with the human's
# response.
#
# Flow:
# async_start("refund request")
#   |
#   v
# prepare  ->  state["ticket"] = {"id": "T-001", "topic": "refund request"}
#              (flow.when("UserFeedback") is registered but not yet triggered)
#   |
# execution.save()  ->  saved_state dict  (serialized mid-execution snapshot)
#   |
# [--- cross-session boundary ---]
#   |
# restored_execution.load(saved_state)
# restored_execution.async_emit("UserFeedback", {"approved": True})
#   |
#   v  [event: UserFeedback]
# finalize  ->  state["final"] = {ticket: ..., feedback: {"approved": True}}
#   |
# async_close()  ->  prints state["final"]
