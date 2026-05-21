import asyncio
from typing import cast

from agently import TriggerFlow, TriggerFlowRuntimeData


class SimpleLogger:
    def info(self, message: str):
        print(f"[logger] {message}")


def has_multiple_sections(data: TriggerFlowRuntimeData):
    if not isinstance(data.input, dict):
        return False
    sections = data.input.get("sections", [])
    return isinstance(sections, list) and len(sections) > 1


async def prepare_request(data: TriggerFlowRuntimeData):
    topic = str(data.input).strip()
    sections = ["summary"] if "brief" in topic.lower() else ["overview", "risks", "actions"]
    request_context = {"topic": topic, "sections": sections}
    await data.async_set_state("request_context", request_context)
    return request_context


async def use_multi_section_mode(data: TriggerFlowRuntimeData):
    logger = cast(SimpleLogger, data.require_resource("logger"))
    logger.info("multi-section mode")
    next_value = dict(data.input) if isinstance(data.input, dict) else {}
    next_value["mode"] = "multi"
    return next_value


async def use_single_section_mode(data: TriggerFlowRuntimeData):
    logger = cast(SimpleLogger, data.require_resource("logger"))
    logger.info("single-section mode")
    next_value = dict(data.input) if isinstance(data.input, dict) else {}
    next_value["mode"] = "single"
    return next_value


async def list_sections(data: TriggerFlowRuntimeData):
    if not isinstance(data.input, dict):
        return []
    return [
        {
            "topic": data.input.get("topic"),
            "mode": data.input.get("mode"),
            "section": section,
        }
        for section in data.input.get("sections", [])
    ]


async def draft_section(data: TriggerFlowRuntimeData):
    item = data.input if isinstance(data.input, dict) else {}
    section = str(item.get("section", data.input))
    mode = item.get("mode", "unknown")
    logger = cast(SimpleLogger, data.require_resource("logger"))
    logger.info(f"drafting {section}")
    await data.async_put_into_stream({"scope": "child", "section": section})
    return {
        "topic": item.get("topic"),
        "mode": mode,
        "section": section,
        "text": f"[{mode}] {section}: {item.get('topic')}",
    }


async def summarize_child_report(data: TriggerFlowRuntimeData):
    drafts = list(data.input) if isinstance(data.input, list) else [data.input]
    first = drafts[0] if drafts and isinstance(drafts[0], dict) else {}
    report = {
        "topic": first.get("topic"),
        "mode": first.get("mode"),
        "sections": [draft.get("section") for draft in drafts if isinstance(draft, dict)],
        "summary": "\n".join(
            str(draft.get("text", draft)) if isinstance(draft, dict) else str(draft)
            for draft in drafts
        ),
    }
    await data.async_set_state("report", report)
    return report


async def finalize_request(data: TriggerFlowRuntimeData):
    report = data.input if isinstance(data.input, dict) else {"summary": data.input}
    await data.async_put_into_stream({"scope": "parent", "summary": report.get("summary")})
    await data.async_set_state("child_report", report)
    await data.async_set_state(
        "final",
        {
            "summary": report.get("summary"),
            "child_report": report,
        },
    )


child_flow = TriggerFlow(name="child-review-flow")
(
    child_flow.if_condition(has_multiple_sections)
    .to(use_multi_section_mode)
    .else_condition()
    .to(use_single_section_mode)
    .end_condition()
    .to(list_sections)
    .for_each()
    .to(draft_section)
    .end_for_each()
    .to(summarize_child_report)
)

parent_flow = TriggerFlow(name="parent-review-flow")
parent_flow.update_runtime_resources(logger=SimpleLogger())
(
    parent_flow.to(prepare_request)
    .to_sub_flow(
        child_flow,
        capture={
            "input": "value",
            "resources": {
                "logger": "resources.logger",
            },
        },
        write_back={
            "value": "result.report",
        },
    )
    .to(finalize_request)
)


async def main():
    execution = parent_flow.create_execution(auto_close=False)
    await execution.async_start("AI infra weekly")

    close_task = asyncio.create_task(execution.async_close())
    stream_items = [item async for item in execution.get_async_runtime_stream(timeout=None)]
    state = await close_task

    print("\nStream:")
    for item in stream_items:
        print(item)
    print("\nState:")
    print(state)

    assert state["request_context"]["topic"] == "AI infra weekly"
    assert state["child_report"]["mode"] == "multi"
    assert "overview" in state["final"]["summary"]


if __name__ == "__main__":
    asyncio.run(main())

# Stable expected key output from the declared run:
# child_report.mode == "multi", final.summary includes "overview", and stream emits child sections.
#
# How it works:
# to_sub_flow(child, capture={...}, write_back={...}) bridges two flows:
#   capture: maps parent data.input -> child start value; copies parent "logger" resource
#   write_back: after child closes, copies child state["report"] -> parent data.input
# The child flow branches on section count (multi/single), fans out per section via
# for_each, and emits stream items per section.  Those child stream items bubble up
# to the parent execution's stream channel and are visible in get_async_runtime_stream().
#
# Flow:
# async_start("AI infra weekly")
#   |
#   v
# prepare_request  ->  sections=["overview","risks","actions"] (3 > 1)
#   |
# to_sub_flow(child_flow, capture={input:"value", resources:{logger}}, write_back={value:"result.report"})
#   |  [child receives request_context as input + logger resource]
#   |    v
#   |    if_condition (has_multiple_sections=True)  ->  use_multi_section_mode  (mode="multi")
#   |      |
#   |      v
#   |    list_sections  ->  [{"section":"overview",...}, {"section":"risks",...}, {"section":"actions",...}]
#   |      |
#   |      v
#   |    for_each  ->  draft_section x3  (each emits child scope stream item)
#   |      |
#   |      v
#   |    summarize_child_report  ->  child state["report"] = {mode:"multi", sections:[...], summary}
#   |  [child closes; write_back: parent data.input = child state["report"]]
#   |
#   v
# finalize_request  ->  emits parent scope stream item
#                        state["child_report"] + state["final"]
#   |
# async_close()
