import asyncio
from pprint import pprint

from agently import TriggerFlow, TriggerFlowRuntimeData


DOCUMENT_DRAFT = """
Service Agreement Draft

Clause 4. Payment:
The customer shall pay after acceptance. The acceptance date and acceptance
criteria will be confirmed later by both parties.

Clause 7. Termination:
The vendor may terminate the agreement immediately if it believes delivery
conditions have changed.
"""

SUPPLEMENTAL_CONTEXT = {
    "attachment": "latest-price-table",
    "acceptance_deadline": "2026-06-30",
    "termination_notice_days": 15,
}


def build_document_review_flow() -> TriggerFlow:
    flow = TriggerFlow(name="step-21-document-review-runtime-intervention")

    async def extract_terms(data: TriggerFlowRuntimeData):
        await asyncio.sleep(0.05)
        await data.async_set_state("doc_id", "contract-2026-09", emit=False)
        return {
            "payment_clause": "Acceptance criteria are not final.",
            "termination_clause": "Immediate termination is allowed.",
        }

    async def assess_risk(data: TriggerFlowRuntimeData):
        interventions = data.get_interventions(status="inserted", target="risk-review")
        supplements = [item["payload"] for item in interventions]
        notice_days = max(
            [
                int(supplement.get("termination_notice_days", 0))
                for supplement in supplements
                if isinstance(supplement, dict)
            ]
            or [0]
        )
        risk_level = "medium" if notice_days >= 15 else "high"
        assessment = {
            "risk_level": risk_level,
            "supplement_count": len(supplements),
            "payment_deadline": next(
                (
                    supplement.get("acceptance_deadline")
                    for supplement in supplements
                    if isinstance(supplement, dict) and supplement.get("acceptance_deadline")
                ),
                None,
            ),
            "remaining_issue": "termination notice is still short",
        }
        for item in interventions:
            await data.async_mark_intervention_consumed(
                item["id"],
                status="applied",
                note="Included in the risk assessment inputs.",
            )
        await data.async_set_state("risk_assessment", assessment)
        return assessment

    async def finalize(data: TriggerFlowRuntimeData):
        assessment = data.input if isinstance(data.input, dict) else {}
        final_report = {
            "doc_id": data.get_state("doc_id"),
            "risk_level": assessment.get("risk_level"),
            "supplement_count": assessment.get("supplement_count"),
            "payment_deadline": assessment.get("payment_deadline"),
        }
        await data.async_set_state("final_report", final_report)

    (
        flow.to(extract_terms)
        .intervention_point(name="before_risk_assessment", target="risk-review")
        .to(assess_risk)
        .to(finalize)
    )
    return flow


async def main():
    flow = build_document_review_flow()
    execution = flow.create_execution(auto_close=False)

    start_task = asyncio.create_task(execution.async_start(DOCUMENT_DRAFT))
    await asyncio.sleep(0.01)
    intervention = await execution.async_intervene(
        SUPPLEMENTAL_CONTEXT,
        author="legal-reviewer",
        target="risk-review",
        note="Reviewer uploaded Attachment A while extraction was still running.",
    )

    await start_task
    snapshot = await execution.async_close()
    inserted = execution.result.get_latest_intervention(status="inserted", target="risk-review")
    assert intervention is not None
    assert inserted is not None

    print("[INTERVENTION]")
    pprint(
        {
            "id": intervention["id"],
            "status": inserted["status"],
            "target": inserted["target"],
            "consumer_status": inserted["consumers"]["assess_risk"]["status"],
        }
    )
    print("[FINAL_REPORT]")
    pprint(snapshot["final_report"])

    assert inserted["id"] == intervention["id"]
    assert inserted["consumers"]["assess_risk"]["status"] == "applied"
    assert snapshot["final_report"] == {
        "doc_id": "contract-2026-09",
        "risk_level": "medium",
        "supplement_count": 1,
        "payment_deadline": "2026-06-30",
    }


if __name__ == "__main__":
    asyncio.run(main())


# Stable expected key output from a local run:
# [INTERVENTION]
# {'consumer_status': 'applied',
#  'status': 'inserted',
#  'target': 'risk-review'}
# [FINAL_REPORT]
# {'doc_id': 'contract-2026-09',
#  'payment_deadline': '2026-06-30',
#  'risk_level': 'medium',
#  'supplement_count': 1}
#
# How it works:
# - The flow declares .intervention_point(name="before_risk_assessment", ...),
#   so execution creation infers planned intervention mode.
# - The reviewer adds context while extract_terms is still running.
# - assess_risk reads the inserted context with data.get_interventions(...) and
#   records an applied audit entry; the consumer defaults to the chunk name.
#
# ASCII flow:
# start
#   |
#   v
# extract_terms  -- async_intervene(..., target="risk-review") while running
#   |
#   v
# intervention_point("before_risk_assessment") inserts matching context
#   |
#   v
# assess_risk reads + marks intervention applied
#   |
#   v
# finalize -> close snapshot["final_report"]
