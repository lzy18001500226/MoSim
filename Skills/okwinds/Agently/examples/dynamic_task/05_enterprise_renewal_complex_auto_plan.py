from __future__ import annotations

import asyncio
from typing import Any

from _shared import configure_model
from agently import Agently


ACCOUNT_ESCALATION_BRIEF = """
Account: Northstar Retail Group
Renewal date: 2026-06-30
ARR at risk: USD 1.8M

Recent signals:
- CFO asked for a 20% concession before renewal.
- VP Operations says checkout latency during peak campaigns is hurting store
  rollout confidence.
- Support has two open P1 escalations about delayed inventory sync.
- Product usage is still high in store operations, but analytics adoption has
  fallen for three consecutive weeks.
- Legal asked whether the new data-processing addendum covers EU store data.
"""


RECOVERY_PACKAGE_SCHEMA = {
    "risk_level": (str, "renewal risk level with short rationale", True),
    "executive_summary": (str, "internal executive summary for the account team", True),
    "customer_message": (str, "customer-facing note for the account owner to send", True),
    "next_actions": ([str], "ordered next actions for sales, support, product, and legal", True),
}


class MockAccountSystems:
    def current_snapshot(self) -> dict[str, Any]:
        return {
            "source": "mock account systems",
            "crm": {
                "stage": "renewal negotiation",
                "economic_buyer": "CFO",
                "account_owner": "Maya Chen",
                "arr_at_risk": "USD 1.8M",
            },
            "product_usage": {
                "store_operations_weekly_active_users": "up 8%",
                "analytics_active_users": "down 27%",
                "checkout_latency_p95": "2.9s during campaign peaks",
            },
            "support": {
                "open_p1_cases": 2,
                "primary_theme": "delayed inventory sync",
                "oldest_p1_age": "46 hours",
            },
            "commercial": {
                "discount_request": "20%",
                "renewal_deadline": "2026-06-30",
                "procurement_status": "waiting on concession proposal",
            },
            "legal": {
                "pending_question": "EU store data-processing addendum coverage",
                "contract_blocker": True,
            },
        }


# DynamicTask complex auto-planning example.
# The app exposes EnterpriseRenewalService.prepare_recovery_package(brief).
# Unlike 02, the app does not submit a DAG. The model planner must produce a
# richer DAG with independent branches and at least one join before execution.
# Expected key output from one DeepSeek run:
# provider=deepseek
# planned_task_count=6
# root_task_count=3
# join_task_count=1
# task_ids=commercial_risk_analysis,product_adoption_risk_analysis,support_legal_risk_analysis,risk_synthesis,recovery_strategy_development,recovery_package_generation
# semantic_role=recovery_package
# semantic_final_task=recovery_package_generation
# next_actions_count=7
#
# How it works:
# Mock account systems provide CRM, product, support, commercial, and legal
# state because this example is not connected to real enterprise systems. The
# model owns DAG planning, branch analysis, synthesis, and frontstage message
# generation.


def _dag_shape(validation) -> dict[str, Any]:
    tasks = list(validation.graph.tasks)
    downstream_counts = {task.id: 0 for task in tasks}
    for task in tasks:
        for dep_id in task.depends_on:
            downstream_counts[dep_id] = downstream_counts.get(dep_id, 0) + 1
    return {
        "task_ids": list(validation.topological_task_ids),
        "root_task_ids": list(validation.root_task_ids),
        "join_task_ids": [task.id for task in tasks if len(task.depends_on) >= 2],
        "branch_task_ids": [
            task_id for task_id, downstream_count in downstream_counts.items() if downstream_count >= 2
        ],
    }


class EnterpriseRenewalService:
    def __init__(self, account_systems: MockAccountSystems | None = None):
        self.account_systems = account_systems or MockAccountSystems()

    async def prepare_recovery_package(self, escalation_brief: str) -> dict[str, Any]:
        system_snapshot = self.account_systems.current_snapshot()
        agent = Agently.create_agent("renewal-recovery-planner")
        task = agent.create_dynamic_task(
            target=(
                "Create an enterprise renewal recovery package. Generate a complex TaskDAG "
                "with five to seven model tasks. Use at least three independent root analysis "
                "branches for commercial risk, product adoption/performance risk, and support/legal "
                "risk. Join those branches into a synthesis task, then produce a final recovery "
                "package for the account team. Use semantic_outputs only for the final recovery_package."
            ),
            max_tasks=7,
            output_schema=RECOVERY_PACKAGE_SCHEMA,
        )
        plan = await task.async_plan(max_retries=3)
        validation = task.validate(plan, strict_schema_version=True)
        shape = _dag_shape(validation)
        snapshot = await task.async_run(
            plan,
            graph_input={
                "escalation_brief": escalation_brief,
                "business_system_feedback": system_snapshot,
                "frontstage_goal": "help the account owner send a credible recovery note",
                "backstage_goal": "coordinate sales, support, product, and legal before renewal",
            },
            timeout=180,
        )
        semantic_outputs = snapshot["semantic_outputs"]
        final_role = next(iter(semantic_outputs))
        recovery_package = semantic_outputs[final_role]["result"]
        return {
            "frontstage_message": recovery_package["customer_message"].strip(),
            "backstage": {
                "plan": plan,
                "mock_account_systems": system_snapshot,
                "raw_result": recovery_package,
                "shape": shape,
                "semantic_role": final_role,
                "semantic_final_task": semantic_outputs[final_role]["task_id"],
            },
        }


async def main():
    provider = configure_model(temperature=0.0)
    service = EnterpriseRenewalService()
    result = await service.prepare_recovery_package(ACCOUNT_ESCALATION_BRIEF)
    shape = result["backstage"]["shape"]
    raw_result = result["backstage"]["raw_result"]

    print(f"provider={provider}")
    print(f"planned_task_count={ len(shape['task_ids']) }")
    print(f"root_task_count={ len(shape['root_task_ids']) }")
    print(f"join_task_count={ len(shape['join_task_ids']) }")
    print(f"task_ids={ ','.join(shape['task_ids']) }")
    print(f"root_task_ids={ ','.join(shape['root_task_ids']) }")
    print(f"join_task_ids={ ','.join(shape['join_task_ids']) }")
    print(f"semantic_role={ result['backstage']['semantic_role'] }")
    print(f"semantic_final_task={ result['backstage']['semantic_final_task'] }")
    print(f"next_actions_count={ len(raw_result['next_actions']) }")
    print("[MOCK_ACCOUNT_SYSTEMS_FEEDBACK]")
    print(result["backstage"]["mock_account_systems"])
    print("[BACKSTAGE_MODEL_PLAN]")
    print(result["backstage"]["plan"])
    print("[BACKSTAGE_RAW_RESULT]")
    print(raw_result)
    print("[FRONTSTAGE_CUSTOMER_MESSAGE]")
    print(result["frontstage_message"])

    assert len(shape["task_ids"]) >= 5
    assert len(shape["root_task_ids"]) >= 3
    assert shape["join_task_ids"]
    assert result["backstage"]["semantic_final_task"]
    assert str(result["frontstage_message"]).strip()
    assert raw_result["next_actions"]


if __name__ == "__main__":
    asyncio.run(main())
