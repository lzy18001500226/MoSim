import asyncio
from typing import Any, cast
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
    await data.async_set_state("final", {"summary": report.get("summary"), "child_report": report})


def build_child_flow():
    child_flow = TriggerFlow(name="step-18-child-flow")
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
    return child_flow


def build_parent_flow():
    parent_flow = TriggerFlow(name="step-18-parent-flow")
    parent_flow.update_runtime_resources(logger=SimpleLogger())
    parent_flow.to(prepare_request).to_sub_flow(
        build_child_flow(),
        capture={
            "input": "value",
            "resources": {
                "logger": "resources.logger",
            },
        },
        write_back={
            "value": "result.report",
        },
    ).to(finalize_request)
    return parent_flow


async def triggerflow_sub_flow_capture_write_back_demo():
    flow = build_parent_flow()
    execution = flow.create_execution(auto_close=False)
    await execution.async_start("AI infra weekly")
    close_task = asyncio.create_task(execution.async_close())
    stream_items = [item async for item in execution.get_async_runtime_stream(timeout=None)]
    state = await close_task
    assert state["child_report"]["mode"] == "multi"
    assert cast(dict[str, Any], stream_items[-1])["scope"] == "parent"
    print({"stream": stream_items, "state": state})


if __name__ == "__main__":
    asyncio.run(triggerflow_sub_flow_capture_write_back_demo())

# Expected output (abridged; exact section text depends on topic):
# stream: [{"scope":"child","section":"overview"}, {"scope":"child","section":"risks"},
#          {"scope":"child","section":"actions"}, {"scope":"parent","summary":"..."}]
# state["child_report"]["mode"] == "multi"
#
# How it works:
# to_sub_flow() runs a child TriggerFlow as a nested execution and bridges data in both
# directions:
#   capture={"input": "value", "resources": {"logger": "resources.logger"}}
#     — maps parent data.input into the child's start value, and copies the parent's "logger"
#       resource into the child so child handlers can call data.require_resource("logger").
#   write_back={"value": "result.report"}
#     — after the child closes, copies child state["report"] into the parent's data.input,
#       which becomes the input to finalize_request.
# Stream items emitted inside the child (async_put_into_stream) bubble up to the parent
# execution's stream channel, interleaved with any parent-level stream items.
# The child flow itself branches (if_condition on section count) and fans out
# (for_each over sections), producing "multi" mode for multi-section topics.
#
# Flow:
# async_start("AI infra weekly")
#   |
#   v
# prepare_request  ->  sections=["overview","risks","actions"], state["request_context"]=...
#   |
#   v
# to_sub_flow(child_flow, capture={input, resources}, write_back={value: result.report})
#   |  [child starts with request_context as input]
#   |    v
#   |    if_condition(has_multiple_sections)  ->  True (3 sections)
#   |      |
#   |      v
#   |    use_multi_section_mode  ->  mode="multi"
#   |      |
#   |      v
#   |    list_sections  ->  [{"section":"overview",...}, {"section":"risks",...}, ...]
#   |      |
#   |      v
#   |    for_each -> draft_section (x3, each async_put_into_stream child scope item)
#   |      |
#   |      v
#   |    summarize_child_report  ->  child state["report"] = {mode, sections, summary}
#   |  [child closes; write_back copies report into parent data.input]
#   |
#   v
# finalize_request  ->  async_put_into_stream(parent scope summary)
#                        state["final"] = {summary, child_report}
#   |
# async_close()
