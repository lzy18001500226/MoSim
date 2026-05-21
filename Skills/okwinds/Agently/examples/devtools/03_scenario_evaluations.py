# pyright: reportMissingImports=false

from agently import TriggerFlow, TriggerFlowRuntimeData
from agently_devtools import EvaluationBinding, EvaluationBridge, EvaluationCase, EvaluationRunner


def build_flow():
    flow = TriggerFlow(name="support-triage-flow")

    @flow.chunk
    async def classify(data: TriggerFlowRuntimeData):
        text = str(data.input).lower()
        if "refund" in text:
            route = "billing"
        elif "shipment" in text:
            route = "logistics"
        else:
            route = "general"
        await data.async_set_state("route", route)

    flow.to(classify)
    return flow


async def run_flow(flow: TriggerFlow, value: str):
    execution = flow.create_execution(auto_close=True, auto_close_timeout=0.1)
    state = await execution.async_start(value)
    return state["route"]


def build_executor(active_flow: TriggerFlow):
    async def execute(case: EvaluationCase):
        return await run_flow(active_flow, case.input)

    return execute


bridge = EvaluationBridge(
    base_url="http://127.0.0.1:15596",
    app_id="agently-main-examples",
    group_id="devtools-evaluation-demo",
)
runner = EvaluationRunner(bridge=bridge)

binding = EvaluationBinding(
    bridge=bridge,
    suite_id="support-routing",
    target_type="triggerflow",
    target_name="support-triage-flow",
    executor=build_executor(build_flow()),
    target_factory=build_flow,
    target_executor_factory=build_executor,
)

report = runner.run(
    binding,
    cases=[
        EvaluationCase(case_id="refund", input="Need a refund for a duplicate payment."),
        EvaluationCase(case_id="shipping", input="Where is my shipment now?"),
        EvaluationCase(case_id="other", input="Just want general help."),
    ],
    rules=[
        lambda record: record.output in {"billing", "logistics", "general"},
        lambda record: record.error is None,
    ],
    rounds=2,
)

print(
    {
        "suite_id": report.suite_id,
        "passed_rounds": report.passed_rounds,
        "total_rounds": report.total_rounds,
    }
)

# Stable expected key output from the declared run:
# suite_id == "support-routing", passed_rounds == 6, and total_rounds == 6.
#
# How it works:
# EvaluationRunner.run() executes each EvaluationCase through the bound executor (the
# support-triage TriggerFlow) for the requested number of rounds, applies each rule
# function to the resulting EvaluationRecord, and accumulates pass/fail counts.
# The flow classifies input text into "billing", "logistics", or "general" by keyword.
# 3 cases × 2 rounds = 6 total, all passing because the routing is deterministic.
#
# Flow:
# runner.run(binding, cases=[refund, shipping, other], rules=[...], rounds=2)
#   |  3 cases × 2 rounds
#   v
# for each case: run_flow(input) -> route label (billing/logistics/general)
# rule_1: route in {"billing","logistics","general"}  -> True
# rule_2: error is None                               -> True
#   |
#   v
# report: suite_id="support-routing", passed_rounds=6, total_rounds=6
