from __future__ import annotations

import asyncio
from typing import Any

from _shared import configure_model
from agently import Agently


CUSTOMER_TICKET = """
Customer: ACME Logistics
Plan: Pro
Message:
We were charged twice after upgrading our seats yesterday. The invoice numbers
are INV-2081 and INV-2082. Please explain what happened and give us a refund
timeline. We are blocked from closing our monthly finance report.
"""


class MockBillingSystem:
    def lookup_case(self, ticket: str) -> dict:
        return {
            "case_id": "BILL-8842",
            "duplicate_invoice_ids": ["INV-2081", "INV-2082"],
            "case_priority": "high",
            "refund_timeline": "3-5 business days after billing review approval",
            "current_status": "billing review opened; refund not yet issued",
            "source": "mock billing system",
            "ticket_excerpt": ticket.strip(),
        }


class MockCustomerPlanSystem:
    def lookup_plan(self, customer_name: str) -> dict:
        return {
            "customer_name": customer_name,
            "plan": "Pro",
            "support_tier": "priority",
            "account_owner": "support-owner@example.com",
            "refund_policy": "billing review approval required before refund issuance",
            "source": "mock customer plan system",
        }


# DynamicTask intelligent module example.
# The app exposes a simple SupportResponseModule.respond(ticket) business API.
# Inside that module, Dynamic Task runs a submitted fan-out / join DAG.
# Expected key output from one DeepSeek run:
# provider=deepseek
# task_ids=classify_ticket,lookup_billing,lookup_customer_plan,policy_check,draft_response,quality_check
# semantic_final_task=quality_check
# frontstage_response_non_empty=True
# [MOCK_BILLING_SYSTEM_FEEDBACK] shows case_id BILL-8842 and refund_timeline
# 3-5 business days after billing review approval.
#
# How it works:
# The product-facing API is just respond(ticket). Mock billing and customer-plan
# systems supply external status because this example is not connected to real
# backends. Model-owned classification, policy check, response drafting, and QA
# all use Agently output schemas instead of free-form marker parsing.


class SupportResponseModule:
    def __init__(
        self,
        billing_system: MockBillingSystem | None = None,
        customer_plan_system: MockCustomerPlanSystem | None = None,
    ):
        self.billing_system = billing_system or MockBillingSystem()
        self.customer_plan_system = customer_plan_system or MockCustomerPlanSystem()
        self.graph = {
            "graph_id": "support-response-module",
            "task_schema_version": "task_dag/v1",
            "tasks": [
                {
                    "id": "classify_ticket",
                    "kind": "model",
                    "binding": "classify_ticket_handler",
                    "title": "Classify support ticket",
                    "purpose": "Classify urgency, customer impact, and requested outcome.",
                    "produces": [{"role": "ticket_classification", "type": "json"}],
                },
                {
                    "id": "lookup_billing",
                    "kind": "local",
                    "binding": "billing_lookup_handler",
                    "title": "Lookup billing case",
                    "purpose": "Read duplicate billing case status from the billing system.",
                    "depends_on": ["classify_ticket"],
                    "produces": [{"role": "billing_case", "type": "json"}],
                },
                {
                    "id": "lookup_customer_plan",
                    "kind": "local",
                    "binding": "customer_plan_lookup_handler",
                    "title": "Lookup customer plan",
                    "purpose": "Read customer support plan and refund policy.",
                    "depends_on": ["classify_ticket"],
                    "produces": [{"role": "customer_plan", "type": "json"}],
                },
                {
                    "id": "policy_check",
                    "kind": "model",
                    "binding": "policy_check_handler",
                    "title": "Check response policy",
                    "purpose": "Identify safe commitments and escalation requirements for the response.",
                    "depends_on": ["classify_ticket"],
                    "produces": [{"role": "response_policy", "type": "json"}],
                },
                {
                    "id": "draft_response",
                    "kind": "model",
                    "binding": "draft_response_handler",
                    "title": "Draft customer response",
                    "purpose": "Draft a customer-facing response from classification, system lookups, and policy check.",
                    "depends_on": [
                        "classify_ticket",
                        "lookup_billing",
                        "lookup_customer_plan",
                        "policy_check",
                    ],
                    "produces": [{"role": "draft_response", "type": "json"}],
                },
                {
                    "id": "quality_check",
                    "kind": "model",
                    "binding": "quality_check_handler",
                    "title": "Quality check final answer",
                    "purpose": "Review and revise the draft for empathy, specificity, and operational safety.",
                    "depends_on": [
                        "classify_ticket",
                        "lookup_billing",
                        "lookup_customer_plan",
                        "policy_check",
                        "draft_response",
                    ],
                    "produces": [{"role": "frontstage_customer_response", "type": "json"}],
                },
            ],
            "semantic_outputs": {"frontstage_customer_response": "quality_check"},
        }

    async def classify_ticket_handler(self, context) -> dict[str, Any]:
        return await (
            Agently.create_agent()
            .input(
                {
                    "ticket": context.graph_input["ticket"],
                    "target": "Classify the customer support ticket.",
                }
            )
            .output(
                {
                    "urgency": (str, "low, medium, or high urgency", True),
                    "customer_impact": (str, "business impact described by the customer", True),
                    "requested_outcome": (str, "what the customer asks us to provide", True),
                    "evidence": ([str], "short evidence snippets from the ticket", True),
                }
            )
            .async_start(
                ensure_keys=["urgency", "customer_impact", "requested_outcome", "evidence"],
                max_retries=2,
            )
        )

    async def billing_lookup_handler(self, context) -> dict[str, Any]:
        return self.billing_system.lookup_case(context.graph_input["ticket"])

    async def customer_plan_lookup_handler(self, context) -> dict[str, Any]:
        return self.customer_plan_system.lookup_plan("ACME Logistics")

    async def policy_check_handler(self, context) -> dict[str, Any]:
        return await (
            Agently.create_agent()
            .input(
                {
                    "classification": context.dependency_results["classify_ticket"],
                    "ticket": context.graph_input["ticket"],
                    "task": "Identify response policy constraints for a duplicate billing support reply.",
                }
            )
            .output(
                {
                    "allowed_commitments": ([str], "commitments the response may safely make", True),
                    "restricted_claims": ([str], "claims the response should avoid or qualify", True),
                    "escalation_required": (bool, "whether the case should be escalated to billing/account owner", True),
                    "reason": (str, "short explanation of the policy decision", True),
                }
            )
            .async_start(
                ensure_keys=[
                    "allowed_commitments",
                    "restricted_claims",
                    "escalation_required",
                    "reason",
                ],
                max_retries=2,
            )
        )

    async def draft_response_handler(self, context) -> dict[str, Any]:
        return await (
            Agently.create_agent()
            .input(
                {
                    "ticket": context.graph_input["ticket"],
                    "classification": context.dependency_results["classify_ticket"],
                    "billing_case": context.dependency_results["lookup_billing"],
                    "customer_plan": context.dependency_results["lookup_customer_plan"],
                    "policy_check": context.dependency_results["policy_check"],
                }
            )
            .output(
                {
                    "subject": (str, "email subject line", True),
                    "customer_response": (str, "customer-facing response body", True),
                    "internal_notes": ([str], "internal notes for support team", True),
                }
            )
            .async_start(
                ensure_keys=["subject", "customer_response", "internal_notes"],
                max_retries=2,
            )
        )

    async def quality_check_handler(self, context) -> dict[str, Any]:
        return await (
            Agently.create_agent()
            .input(
                {
                    "draft": context.dependency_results["draft_response"],
                    "classification": context.dependency_results["classify_ticket"],
                    "billing_case": context.dependency_results["lookup_billing"],
                    "customer_plan": context.dependency_results["lookup_customer_plan"],
                    "policy_check": context.dependency_results["policy_check"],
                }
            )
            .output(
                {
                    "approved": (bool, "whether the response is ready to send", True),
                    "customer_response": (str, "final customer-facing response body", True),
                    "qa_checklist": ([str], "completed QA checks", True),
                    "safety_notes": ([str], "operational safety notes for the support team", True),
                }
            )
            .async_start(
                ensure_keys=["approved", "customer_response", "qa_checklist", "safety_notes"],
                max_retries=2,
            )
        )

    async def respond(self, ticket: str) -> dict:
        task = Agently.create_dynamic_task(
            target="Resolve a duplicate billing support ticket.",
            plan=self.graph,
            handlers={
                "classify_ticket_handler": self.classify_ticket_handler,
                "billing_lookup_handler": self.billing_lookup_handler,
                "customer_plan_lookup_handler": self.customer_plan_lookup_handler,
                "policy_check_handler": self.policy_check_handler,
                "draft_response_handler": self.draft_response_handler,
                "quality_check_handler": self.quality_check_handler,
            },
        )
        validation = task.validate(self.graph, strict_schema_version=True)
        snapshot = await task.async_run(
            graph_input={
                "ticket": ticket,
            },
            timeout=90,
        )
        final_result = snapshot["semantic_outputs"]["frontstage_customer_response"]["result"]
        return {
            "frontstage_response": final_result["customer_response"],
            "backstage": {
                "task_ids": validation.topological_task_ids,
                "mock_billing_case": snapshot["task_results"]["lookup_billing"],
                "mock_customer_plan": snapshot["task_results"]["lookup_customer_plan"],
                "classification": snapshot["task_results"]["classify_ticket"],
                "policy_check": snapshot["task_results"]["policy_check"],
                "draft": snapshot["task_results"]["draft_response"],
                "quality_check": final_result,
                "qa_checklist": final_result["qa_checklist"],
                "semantic_final_task": snapshot["semantic_outputs"]["frontstage_customer_response"]["task_id"],
            },
        }


async def main():
    provider = configure_model(temperature=0.0)
    module = SupportResponseModule()
    result = await module.respond(CUSTOMER_TICKET)

    print(f"provider={provider}")
    print(f"task_ids={ ','.join(result['backstage']['task_ids']) }")
    print(f"semantic_final_task={ result['backstage']['semantic_final_task'] }")
    print(f"frontstage_response_non_empty={ bool(str(result['frontstage_response']).strip()) }")
    print("[MOCK_BILLING_SYSTEM_FEEDBACK]")
    print(result["backstage"]["mock_billing_case"])
    print("[MOCK_CUSTOMER_PLAN_SYSTEM_FEEDBACK]")
    print(result["backstage"]["mock_customer_plan"])
    print("[BACKSTAGE_CLASSIFICATION]")
    print(result["backstage"]["classification"])
    print("[BACKSTAGE_POLICY_CHECK]")
    print(result["backstage"]["policy_check"])
    print("[BACKSTAGE_QA_CHECKLIST]")
    print(result["backstage"]["qa_checklist"])
    print("[FRONTSTAGE_CUSTOMER_RESPONSE]")
    print(result["frontstage_response"])

    assert result["backstage"]["task_ids"] == (
        "classify_ticket",
        "lookup_billing",
        "lookup_customer_plan",
        "policy_check",
        "draft_response",
        "quality_check",
    )
    assert result["backstage"]["semantic_final_task"] == "quality_check"
    assert str(result["frontstage_response"]).strip()


if __name__ == "__main__":
    asyncio.run(main())
