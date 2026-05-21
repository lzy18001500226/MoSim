import asyncio
from pprint import pprint

from agently import TriggerFlow, TriggerFlowRuntimeData


TICKET_TEXT = """
Customer report:
The invoice export failed after today's account migration. The customer can
still access the dashboard, but finance cannot close the monthly report.
"""

SUPPORT_CONTEXT = {
    "source": "support-chat",
    "customer_tier": "enterprise",
    "severity_hint": "urgent",
    "contract_sla_hours": 4,
}


def build_ticket_triage_flow() -> TriggerFlow:
    flow = TriggerFlow(name="step-22-ticket-triage-auto-intervention")

    async def normalize_ticket(data: TriggerFlowRuntimeData):
        await asyncio.sleep(0.05)
        await data.async_set_state("ticket_id", "ticket-2026-05-18-117", emit=False)
        return {
            "topic": "invoice-export",
            "impact": "monthly close is blocked",
            "default_priority": "p2",
        }

    async def classify_ticket(data: TriggerFlowRuntimeData):
        interventions = data.get_interventions(status="inserted", target="classify_ticket")
        supplements = [item["payload"] for item in interventions]
        enterprise_urgent = any(
            isinstance(item, dict)
            and item.get("customer_tier") == "enterprise"
            and item.get("severity_hint") == "urgent"
            for item in supplements
        )
        classification = {
            "topic": data.input["topic"],
            "priority": "p1" if enterprise_urgent else data.input["default_priority"],
            "supplement_count": len(supplements),
            "sla_hours": next(
                (
                    item.get("contract_sla_hours")
                    for item in supplements
                    if isinstance(item, dict) and item.get("contract_sla_hours")
                ),
                24,
            ),
        }
        for item in interventions:
            await data.async_mark_intervention_consumed(
                item["id"],
                status="applied",
                note="Included in priority and SLA classification.",
            )
        await data.async_set_state("classification", classification)
        return classification

    async def route_ticket(data: TriggerFlowRuntimeData):
        route = {
            "ticket_id": data.get_state("ticket_id"),
            "priority": data.input["priority"],
            "queue": (
                "enterprise-support"
                if data.input["priority"] == "p1"
                else "standard-support"
            ),
            "sla_hours": data.input["sla_hours"],
            "supplement_count": data.input["supplement_count"],
        }
        await data.async_set_state("route", route)

    flow.to(("normalize_ticket", normalize_ticket)).to(("classify_ticket", classify_ticket)).to(
        ("route_ticket", route_ticket)
    )
    return flow


async def main():
    flow = build_ticket_triage_flow()
    execution = flow.create_execution(auto_close=False, intervention_mode="auto")

    start_task = asyncio.create_task(execution.async_start(TICKET_TEXT))
    await asyncio.sleep(0.01)
    intervention = await execution.async_intervene(
        SUPPORT_CONTEXT,
        author="support-agent",
        target="classify_ticket",
        note="Support added contract context while ticket normalization was running.",
    )

    await start_task
    snapshot = await execution.async_close()
    inserted = execution.result.get_latest_intervention(
        status="inserted",
        target="classify_ticket",
    )
    assert intervention is not None
    assert inserted is not None

    print("[INTERVENTION]")
    pprint(
        {
            "id": intervention["id"],
            "status": inserted["status"],
            "target": inserted["target"],
            "consumer_status": inserted["consumers"]["classify_ticket"]["status"],
        }
    )
    print("[ROUTE]")
    pprint(snapshot["route"])

    assert inserted["id"] == intervention["id"]
    assert inserted["consumers"]["classify_ticket"]["status"] == "applied"
    assert snapshot["route"] == {
        "ticket_id": "ticket-2026-05-18-117",
        "priority": "p1",
        "queue": "enterprise-support",
        "sla_hours": 4,
        "supplement_count": 1,
    }


if __name__ == "__main__":
    asyncio.run(main())


# Stable expected key output from a local run:
# [INTERVENTION]
# {'consumer_status': 'applied',
#  'status': 'inserted',
#  'target': 'classify_ticket'}
# [ROUTE]
# {'priority': 'p1',
#  'queue': 'enterprise-support',
#  'sla_hours': 4,
#  'supplement_count': 1,
#  'ticket_id': 'ticket-2026-05-18-117'}
#
# How it works:
# - The execution uses intervention_mode="auto", so the flow does not declare
#   an explicit .intervention_point(...).
# - The pending intervention targets the chunk name "classify_ticket".
# - TriggerFlow inserts it immediately before dispatching that chunk, then the
#   chunk reads it with data.get_interventions(...) and records consumption; the
#   consumer defaults to the chunk name.
#
# ASCII flow:
# start
#   |
#   v
# normalize_ticket  -- async_intervene(..., target="classify_ticket") while running
#   |
#   v
# [auto boundary inserts pending context before target chunk]
#   |
#   v
# classify_ticket reads + marks intervention applied
#   |
#   v
# route_ticket -> close snapshot["route"]
