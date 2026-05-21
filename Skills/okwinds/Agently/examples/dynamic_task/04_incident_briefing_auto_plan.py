from __future__ import annotations

import asyncio

from _shared import configure_model
from agently import Agently


INCIDENT_REPORT = """
09:12 - Payment webhook latency rose from 200ms to 4.8s.
09:18 - Checkout retries increased by 32%.
09:24 - Customer success reported three enterprise customers asking whether
       payments were duplicated.
09:31 - Engineering mitigated by routing webhooks through the backup queue.
09:47 - Latency returned below 400ms. Duplicate payment checks are still running.
"""


class MockIncidentStatusSystem:
    def current_status(self) -> dict:
        return {
            "latency_status": "resolved",
            "duplicate_payment_check_status": "running",
            "next_update": "when duplicate payment verification completes",
            "source": "mock incident status system",
        }


FRONTSTAGE_BRIEF_SCHEMA = {
    "brief": (str, "concise customer-success briefing for account owners", True),
    "next_update": (str, "when the customer-success team should expect the next update", True),
}


# DynamicTask auto-planning business example.
# The app exposes IncidentBriefingService.brief(report). Unlike examples 02/03,
# this one does not submit a TaskDAG. The model planner creates the DAG first,
# then Dynamic Task validates and executes it.
# Expected key output from one DeepSeek run:
# provider=deepseek
# planned_task_count=3
# task_ids=summarize_facts,assess_customer_impact,write_customer_success_briefing
# semantic_role=customer_success_briefing
# semantic_final_task=write_customer_success_briefing
# frontstage_brief_non_empty=True
# frontstage_next_update=when duplicate payment verification completes
# [FRONTSTAGE_STATUS_BANNER] says latency is resolved and duplicate payment
# checks are running.
#
# How it works:
# The business API is one method: brief(report). A mock incident-status system
# supplies operational status because this example is not connected to a real
# incident platform. The model still owns DAG planning and briefing generation.


class IncidentBriefingService:
    def __init__(self, incident_status: MockIncidentStatusSystem | None = None):
        self.incident_status = incident_status or MockIncidentStatusSystem()

    async def brief(self, incident_report: str) -> dict:
        business_status = self.incident_status.current_status()
        task = Agently.create_dynamic_task(
            target=(
                "Create an incident briefing for a customer-success lead. "
                "Plan no more than three model tasks: summarize facts, assess customer impact, "
                "and write a concise customer-success briefing."
            ),
            max_tasks=3,
            output_schema=FRONTSTAGE_BRIEF_SCHEMA,
        )
        plan = await task.async_plan(max_retries=3)
        validation = task.validate(plan, strict_schema_version=True)
        snapshot = await task.async_run(
            plan,
            graph_input={
                "incident_report": incident_report,
                "business_system_feedback": business_status,
                "audience": "customer-success lead",
                "frontstage_goal": "brief account owners on what happened and what to say next",
            },
            timeout=120,
        )
        semantic_outputs = snapshot["semantic_outputs"]
        final_role = next(iter(semantic_outputs))
        structured_brief = semantic_outputs[final_role]["result"]
        frontstage_brief = structured_brief["brief"].strip()
        return {
            "frontstage_brief": frontstage_brief,
            "frontstage_status_banner": (
                f"Latency status: { business_status['latency_status'] }. "
                f"Duplicate payment checks: { business_status['duplicate_payment_check_status'] }."
            ),
            "backstage": {
                "plan": plan,
                "mock_incident_status": business_status,
                "raw_result": structured_brief,
                "task_ids": validation.topological_task_ids,
                "semantic_role": final_role,
                "semantic_final_task": semantic_outputs[final_role]["task_id"],
                "next_update": structured_brief["next_update"],
            },
        }


async def main():
    provider = configure_model(temperature=0.0)
    service = IncidentBriefingService()
    result = await service.brief(INCIDENT_REPORT)

    print(f"provider={provider}")
    print(f"planned_task_count={ len(result['backstage']['task_ids']) }")
    print(f"task_ids={ ','.join(result['backstage']['task_ids']) }")
    print(f"semantic_role={ result['backstage']['semantic_role'] }")
    print(f"semantic_final_task={ result['backstage']['semantic_final_task'] }")
    print(f"frontstage_brief_non_empty={ bool(str(result['frontstage_brief']).strip()) }")
    print(f"frontstage_next_update={ result['backstage']['next_update'] }")
    print("[MOCK_INCIDENT_STATUS_SYSTEM_FEEDBACK]")
    print(result["backstage"]["mock_incident_status"])
    print("[BACKSTAGE_MODEL_PLAN]")
    print(result["backstage"]["plan"])
    print("[BACKSTAGE_RAW_RESULT]")
    print(result["backstage"]["raw_result"])
    print("[FRONTSTAGE_STATUS_BANNER]")
    print(result["frontstage_status_banner"])
    print("[FRONTSTAGE_INCIDENT_BRIEF]")
    print(result["frontstage_brief"])

    assert result["backstage"]["task_ids"]
    assert len(result["backstage"]["task_ids"]) <= 3
    assert result["backstage"]["semantic_final_task"]
    assert str(result["frontstage_brief"]).strip()


if __name__ == "__main__":
    asyncio.run(main())
