import asyncio
from pathlib import Path

from agently import TriggerFlow

flow = TriggerFlow(name="execution-state-resume-demo")


async def prepare_request(data):
    await data.async_set_state(
        "request",
        {
            "topic": data.input,
            "status": "waiting_feedback",
        },
    )


async def resume_with_feedback(data):
    request = data.get_state("request", {}) or {}
    await data.async_set_state(
        "final",
        {
            "topic": request.get("topic"),
            "feedback": data.input,
            "status": "done",
        },
    )


flow.to(prepare_request)
flow.when("UserFeedback").to(resume_with_feedback)


async def main():
    state_file = Path(__file__).with_name("execution_state_checkpoint.json")
    execution = flow.create_execution(auto_close=False)
    await execution.async_start("refund order #A1001")
    execution.save(state_file)

    restored_execution = flow.create_execution(auto_close=False)
    restored_execution.load(state_file)
    await restored_execution.async_emit(
        "UserFeedback",
        {
            "approved": True,
            "note": "Customer uploaded a valid receipt.",
        },
    )
    state = await restored_execution.async_close()
    result = restored_execution.result
    assert state is not None
    state_file.unlink(missing_ok=True)
    assert result.get_state("final.status") == "done"
    print({"final": state["final"], "meta": result.get_meta()})


asyncio.run(main())

# Stable expected key output from the declared run:
# final.status == "done", final.topic == "refund order #A1001", and final.feedback.approved is True.
#
# How it works:
# execution.save(path) serializes state + event queues + interrupt positions to a JSON
# file.  restored_execution.load(path) reconstructs the snapshot on a fresh execution
# object.  Emitting "UserFeedback" on the restored execution drives the when() handler
# exactly as if it had been emitted on the original.
# state_file.unlink() cleans up the checkpoint file after the test.
#
# Flow:
# async_start("refund order #A1001")
#   |
#   v
# prepare_request  ->  state["request"] = {"topic":"refund order #A1001", "status":"waiting_feedback"}
#   |
# execution.save(state_file)       <- serialize to JSON on disk
# [--- restore from file ---]
# restored_execution.load(state_file)
# restored_execution.async_emit("UserFeedback", {approved:True, note:...})
#   |
#   v  [event: UserFeedback]
# resume_with_feedback  ->  state["final"] = {topic, feedback, status:"done"}
#   |
# async_close()  ->  prints state["final"] and result.get_meta()
# state_file.unlink()
