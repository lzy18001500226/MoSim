from __future__ import annotations

import asyncio
from typing import Any

from _shared import configure_model
from agently import Agently


CONTRACT_DRAFT = """
Clause 3. Acceptance:
Customer acceptance will be confirmed later by mutual agreement.

Clause 5. Payment:
Payment is due within 30 days after acceptance.

Clause 8. Termination:
Vendor may terminate immediately without prior notice if delivery conditions
change or required customer information is delayed.
"""


# DynamicTask business landing example.
# The app exposes a simple ContractRiskReviewService.review(contract) business
# API. Inside that service, local business handlers extract deterministic
# signals and a model node writes the final business-facing memo.
# Expected key output from one DeepSeek run:
# provider=deepseek
# task_ids=extract_payment_terms,extract_termination_terms,score_risk,write_risk_memo
# risk_level=high
# semantic_final_task=write_risk_memo
# frontstage_memo_non_empty=True
#
# How it works:
# This is the shape of a real internal module: deterministic local functions
# handle stable business rules, and the model is used where language synthesis
# is useful. Dynamic Task handles dependency injection and result aggregation,
# while the business layer exposes one review(contract) method.


async def payment_terms_handler(context) -> dict[str, Any]:
    text = context.graph_input["contract"]
    return {
        "acceptance_criteria_missing": "confirmed later" in text.lower(),
        "payment_due_days": 30 if "30 days" in text.lower() else None,
        "issue": "Acceptance criteria are not fixed before payment clock starts.",
    }


async def termination_terms_handler(context) -> dict[str, Any]:
    text = context.graph_input["contract"]
    return {
        "unilateral_immediate_termination": "terminate immediately without prior notice" in text.lower(),
        "issue": "Vendor termination right is immediate and unilateral.",
    }


async def risk_score_handler(context) -> dict[str, Any]:
    payment = context.dependency_results["extract_payment_terms"]
    termination = context.dependency_results["extract_termination_terms"]
    score = 0
    findings = []
    if payment["acceptance_criteria_missing"]:
        score += 40
        findings.append(payment["issue"])
    if termination["unilateral_immediate_termination"]:
        score += 60
        findings.append(termination["issue"])
    risk_level = "high" if score >= 70 else "medium" if score >= 40 else "low"
    return {
        "score": score,
        "risk_level": risk_level,
        "findings": findings,
    }


class ContractRiskReviewService:
    def __init__(self):
        self.graph = {
            "graph_id": "contract-risk-review",
            "task_schema_version": "task_dag/v1",
            "tasks": [
                {
                    "id": "extract_payment_terms",
                    "kind": "local",
                    "binding": "payment_terms_handler",
                    "title": "Extract payment risk signals",
                },
                {
                    "id": "extract_termination_terms",
                    "kind": "local",
                    "binding": "termination_terms_handler",
                    "title": "Extract termination risk signals",
                },
                {
                    "id": "score_risk",
                    "kind": "local",
                    "binding": "risk_score_handler",
                    "title": "Score contract risk",
                    "depends_on": ["extract_payment_terms", "extract_termination_terms"],
                },
                {
                    "id": "write_risk_memo",
                    "kind": "model",
                    "title": "Write risk memo",
                    "purpose": (
                        "Write a concise frontstage contract risk memo for an operations manager. "
                        "Use dependency_results.score_risk as the source of truth. "
                        "Include risk_level, findings, recommended next action, and one customer-facing "
                        "status sentence that can be shown in a review dashboard."
                    ),
                    "depends_on": ["score_risk"],
                },
            ],
            "semantic_outputs": {"frontstage_risk_memo": "write_risk_memo"},
        }

    async def review(self, contract: str) -> dict[str, Any]:
        task = Agently.create_dynamic_task(
            target="Review a service agreement draft and produce an operational risk memo.",
            plan=self.graph,
            handlers={
                "payment_terms_handler": payment_terms_handler,
                "termination_terms_handler": termination_terms_handler,
                "risk_score_handler": risk_score_handler,
            },
        )
        validation = task.validate(self.graph, strict_schema_version=True)
        snapshot = await task.async_run(graph_input={"contract": contract}, timeout=90)
        risk_score = snapshot["task_results"]["score_risk"]
        risk_memo = snapshot["semantic_outputs"]["frontstage_risk_memo"]["result"]
        return {
            "frontstage_memo": risk_memo,
            "backstage": {
                "task_ids": validation.topological_task_ids,
                "payment_terms": snapshot["task_results"]["extract_payment_terms"],
                "termination_terms": snapshot["task_results"]["extract_termination_terms"],
                "risk_score": risk_score,
                "semantic_final_task": snapshot["semantic_outputs"]["frontstage_risk_memo"]["task_id"],
            },
        }


async def main():
    provider = configure_model(temperature=0.0)
    service = ContractRiskReviewService()
    result = await service.review(CONTRACT_DRAFT)
    risk_level = result["backstage"]["risk_score"]["risk_level"]

    print(f"provider={provider}")
    print(f"task_ids={ ','.join(result['backstage']['task_ids']) }")
    print(f"risk_level={risk_level}")
    print(f"semantic_final_task={ result['backstage']['semantic_final_task'] }")
    print(f"frontstage_memo_non_empty={ bool(str(result['frontstage_memo']).strip()) }")
    print("[BACKSTAGE_RISK_SCORE]")
    print(result["backstage"]["risk_score"])
    print("[FRONTSTAGE_RISK_MEMO]")
    print(result["frontstage_memo"])

    assert result["backstage"]["task_ids"] == (
        "extract_payment_terms",
        "extract_termination_terms",
        "score_risk",
        "write_risk_memo",
    )
    assert risk_level == "high"
    assert result["backstage"]["semantic_final_task"] == "write_risk_memo"
    assert str(result["frontstage_memo"]).strip()


if __name__ == "__main__":
    asyncio.run(main())
