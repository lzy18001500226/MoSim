import asyncio
from pathlib import Path
from typing import cast

from agently import TriggerFlow, TriggerFlowRuntimeData


ASSET_DIR = Path(__file__).with_name("exported_sub_flow_assets")


class SimpleLogger:
    def info(self, message: str):
        print(f"[logger] {message}")


def has_multiple_sections(data: TriggerFlowRuntimeData):
    if not isinstance(data.input, dict):
        return False
    sections = data.input.get("sections", [])
    return isinstance(sections, list) and len(sections) > 1


async def collect_request(data: TriggerFlowRuntimeData):
    topic = str(data.input).strip()
    sections = ["summary"] if "brief" in topic.lower() else ["overview", "risks", "actions"]
    return {"topic": topic, "sections": sections}


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
    await data.async_set_state("final", report)


def register_handlers(flow: TriggerFlow):
    flow.register_condition_handler(has_multiple_sections)
    flow.register_chunk_handler(collect_request)
    flow.register_chunk_handler(use_multi_section_mode)
    flow.register_chunk_handler(use_single_section_mode)
    flow.register_chunk_handler(list_sections)
    flow.register_chunk_handler(draft_section)
    flow.register_chunk_handler(summarize_child_report)
    flow.register_chunk_handler(finalize_request)
    return flow


def build_child_flow() -> TriggerFlow:
    flow = TriggerFlow(name="child-review-flow")
    register_handlers(flow)
    (
        flow.if_condition(has_multiple_sections)
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
    return flow


def build_flow() -> TriggerFlow:
    flow = TriggerFlow(name="sub-flow-review-demo")
    register_handlers(flow)
    flow.update_runtime_resources(logger=SimpleLogger())
    child_flow = build_child_flow()

    (
        flow.to(collect_request)
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
    return flow


def export_assets(flow: TriggerFlow):
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    simplified_mermaid_path = ASSET_DIR / "sub_flow_review_simplified.mmd"
    detailed_mermaid_path = ASSET_DIR / "sub_flow_review_detailed.mmd"
    json_path = ASSET_DIR / "sub_flow_review_flow.json"
    yaml_path = ASSET_DIR / "sub_flow_review_flow.yaml"

    simplified_mermaid_path.write_text(flow.to_mermaid(mode="simplified"), encoding="utf-8")
    detailed_mermaid_path.write_text(flow.to_mermaid(mode="detailed"), encoding="utf-8")
    flow.get_json_flow(json_path)
    flow.get_yaml_flow(yaml_path)

    print("Exported files:")
    print(" -", simplified_mermaid_path)
    print(" -", detailed_mermaid_path)
    print(" -", json_path)
    print(" -", yaml_path)


async def run_flow(flow: TriggerFlow, value: str):
    execution = flow.create_execution()
    await execution.async_start(value)
    return await execution.async_close()


async def main():
    flow = build_flow()
    export_assets(flow)

    source_state = await run_flow(flow, "AI infra weekly")
    print("\nSource flow state:")
    print(source_state)

    json_flow = TriggerFlow()
    register_handlers(json_flow)
    json_flow.update_runtime_resources(logger=SimpleLogger())
    json_flow.load_json_flow(ASSET_DIR / "sub_flow_review_flow.json")
    json_state = await run_flow(json_flow, "Brief release note")
    print("\nJSON loaded flow state:")
    print(json_state)

    assert source_state["final"]["mode"] == "multi"
    assert json_state["final"]["mode"] == "single"


if __name__ == "__main__":
    asyncio.run(main())

# Stable expected key output from the declared run:
# source_state["final"]["mode"] == "multi" and json_state["final"]["mode"] == "single"; flow assets are exported under exported_sub_flow_assets/.
#
# How it works:
# flow.to_mermaid(mode="simplified") and mode="detailed" produce Mermaid diagram strings;
# get_json_flow(path) and get_yaml_flow(path) write the routing topology to files.
# Handlers must be re-registered before loading (register_handlers(json_flow)) because
# the config files store only graph structure, not function bodies.
# The same flow is then run with two different inputs:
#   "AI infra weekly" -> 3 sections -> mode="multi"
#   "Brief release note" -> "brief" triggers single section -> mode="single"
#
# Flow:
# build_flow()  ->  exports 4 asset files under exported_sub_flow_assets/
#   |
# run_flow(flow, "AI infra weekly")
#   -> collect_request -> to_sub_flow(child) -> finalize -> state["final"]["mode"]=="multi"
#   |
# json_flow.load_json_flow(json_path)
# run_flow(json_flow, "Brief release note")
#   -> collect_request -> to_sub_flow(child) -> finalize -> state["final"]["mode"]=="single"
