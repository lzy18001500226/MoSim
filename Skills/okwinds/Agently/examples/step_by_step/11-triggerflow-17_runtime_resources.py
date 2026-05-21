import asyncio
from typing import Any, Callable, cast

from agently import TriggerFlow, TriggerFlowRuntimeData


class SimpleLogger:
    def info(self, message: str):
        print(f"[logger] {message}")


def search_tool(query: str):
    return [
        {"title": f"{query} - result 1"},
        {"title": f"{query} - result 2"},
    ]


async def triggerflow_runtime_resources_demo():
    flow = TriggerFlow(name="step-17-runtime-resources")
    flow.update_runtime_resources(logger=SimpleLogger())

    async def prepare(data: TriggerFlowRuntimeData):
        query = str(data.input).strip()
        await data.async_set_state("request", {"query": query})
        cast(SimpleLogger, data.require_resource("logger")).info(f"prepared: {query}")
        return await data.async_pause_for(
            type="human_input",
            payload={"question": f"search news for '{query}'?"},
            resume_to="next",
        )

    async def finalize(data: TriggerFlowRuntimeData):
        request = data.get_state("request") or {}
        logger = cast(SimpleLogger, data.require_resource("logger"))
        search = cast(Callable[[str], list[dict[str, Any]]], data.require_resource("search_tool"))
        results = search(str(request.get("query") or ""))
        logger.info(f"searched {len(results)} items")
        await data.async_set_state(
            "final",
            {
                "request": request,
                "feedback": data.input,
                "results": results,
            },
        )

    flow.to(prepare).to(finalize)

    execution = flow.create_execution(auto_close=False)
    await execution.async_start("AI chips")
    saved_state = execution.save()

    restored = flow.create_execution(
        auto_close=False,
        runtime_resources={"search_tool": search_tool},
    )
    restored.load(saved_state)

    interrupt_id = next(iter(restored.get_pending_interrupts()))
    await restored.async_continue_with(interrupt_id, {"approved": True})
    state = await restored.async_close()
    assert len(state["final"]["results"]) == 2
    print(state["final"])


if __name__ == "__main__":
    asyncio.run(triggerflow_runtime_resources_demo())

# Expected output:
# [logger] prepared: AI chips
# [logger] searched 2 items
# {'request': {'query': 'AI chips'}, 'feedback': {'approved': True},
#  'results': [{'title': 'AI chips - result 1'}, {'title': 'AI chips - result 2'}]}
#
# How it works:
# Two scopes for injectable dependencies:
#   flow.update_runtime_resources(name=obj)          — available to all executions of this flow
#   flow.create_execution(runtime_resources={…})     — available only to that one execution
# data.require_resource("name") retrieves by name and raises KeyError if absent (safe to cast).
#
# This example also shows a cross-session resource pattern: the original execution only has
# "logger" (flow-level); after save() and restore, "search_tool" is injected at the restored
# execution level.  Handlers on the restored execution see both resources.
#
# Flow:
# flow.update_runtime_resources(logger=SimpleLogger())   <- flow-level
#   |
# async_start("AI chips")
#   |
#   v
# prepare  ->  state["request"] = {"query": "AI chips"}
#              logger.info("prepared: AI chips")
#              async_pause_for(type="human_input", resume_to="next")   [PAUSED]
#   |
# execution.save()  ->  saved_state
#   |
# [--- restore with extra resource ---]
# restored = flow.create_execution(runtime_resources={"search_tool": search_tool})
# restored.load(saved_state)
# async_continue_with(interrupt_id, {"approved": True})
#   |
#   v  (resumes at finalize because resume_to="next")
# finalize  ->  logger.info("searched 2 items")
#               results = search_tool("AI chips")  -> 2 items
#               state["final"] = {request, feedback, results}
#   |
# async_close()  ->  prints state["final"]
