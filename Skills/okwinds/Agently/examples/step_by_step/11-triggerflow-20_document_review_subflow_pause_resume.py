import asyncio
from pprint import pprint

from agently import TriggerFlow, TriggerFlowRuntimeData


REVIEW_PACKAGE = {
    "doc_id": "contract-2026-08",
    "title": "Service Agreement Draft",
    "findings": [
        {
            "section": "Payment",
            "severity": "medium",
            "issue": "Acceptance criteria are not defined.",
        },
        {
            "section": "Termination",
            "severity": "high",
            "issue": "The vendor can terminate immediately without prior notice.",
        },
    ],
}


def build_prearranged_legal_approval_subflow() -> TriggerFlow:
    child_flow = TriggerFlow(name="step-20-prearranged-legal-approval-subflow")

    async def pause_for_legal_approval(data: TriggerFlowRuntimeData):
        review_package = data.input if isinstance(data.input, dict) else {}
        await data.async_set_state("review_package", review_package, emit=False)
        return await data.async_pause_for(
            type="scheduled_legal_approval",
            payload={
                "doc_id": review_package.get("doc_id"),
                "title": review_package.get("title"),
                "findings": review_package.get("findings", []),
            },
            interrupt_id="scheduled-legal-approval",
            resume_to={"event": "LegalApprovalSubmitted"},
        )

    async def apply_legal_approval(data: TriggerFlowRuntimeData):
        approval = data.input if isinstance(data.input, dict) else {}
        review_package = data.get_state("review_package") or {}
        summary = {
            "doc_id": review_package.get("doc_id"),
            "status": "approved" if approval.get("approved") else "rejected",
            "reviewer": approval.get("reviewer"),
            "finding_count": len(review_package.get("findings", [])),
        }
        await data.async_set_state("approval_summary", summary)
        return summary

    child_flow.to(pause_for_legal_approval)
    child_flow.when("LegalApprovalSubmitted").to(apply_legal_approval)
    return child_flow


def build_document_review_flow() -> TriggerFlow:
    parent_flow = TriggerFlow(name="step-20-document-review-prearranged-wait")

    async def package_review(data: TriggerFlowRuntimeData):
        review_package = data.input if isinstance(data.input, dict) else {}
        await data.async_set_state("doc_id", review_package.get("doc_id"), emit=False)
        await data.async_set_state("finding_count", len(review_package.get("findings", [])), emit=False)
        return review_package

    async def draft_final_report(data: TriggerFlowRuntimeData):
        approval_summary = data.get_state("approval_summary") or {}
        final_report = {
            "doc_id": data.get_state("doc_id"),
            "approval_status": approval_summary.get("status"),
            "reviewer": approval_summary.get("reviewer"),
            "finding_count": data.get_state("finding_count"),
        }
        await data.async_set_state("final_report", final_report)

    (
        parent_flow.to(package_review)
        .to_sub_flow(
            build_prearranged_legal_approval_subflow(),
            capture={"input": "value"},
            write_back={
                "runtime_data": {
                    "approval_summary": "result.approval_summary",
                }
            },
        )
        .to(draft_final_report)
    )
    return parent_flow


async def main():
    flow = build_document_review_flow()
    execution = flow.create_execution(auto_close=False)

    await execution.async_start(REVIEW_PACKAGE)
    pending = execution.get_pending_interrupts()
    root_interrupt_id, root_interrupt = next(iter(pending.items()))

    print("[ROOT_INTERRUPT]")
    print(root_interrupt_id)
    print("[PROJECTED_CHILD_INTERRUPT]")
    pprint(
        {
            "local_interrupt_id": root_interrupt["local_interrupt_id"],
            "resume_to": root_interrupt["resume_to"],
            "sub_flow_frame_id": root_interrupt["sub_flow_frame_id"],
        }
    )

    saved_state = execution.save()

    restored = flow.create_execution(auto_close=False)
    restored.load(saved_state)
    await restored.async_continue_with(
        root_interrupt_id,
        {
            "approved": True,
            "reviewer": "legal-director",
            "comment": "The prearranged legal approval gate has been completed.",
        },
    )

    state = await restored.async_close()
    print("[FINAL_REPORT]")
    pprint(state["final_report"])

    assert root_interrupt["local_interrupt_id"] == "scheduled-legal-approval"
    assert root_interrupt["resume_to"] == {"event": "LegalApprovalSubmitted"}
    assert state["final_report"]["approval_status"] == "approved"


if __name__ == "__main__":
    asyncio.run(main())


# Expected key output:
# [PROJECTED_CHILD_INTERRUPT] shows local_interrupt_id: scheduled-legal-approval
# and resume_to: {'event': 'LegalApprovalSubmitted'}.
# [FINAL_REPORT] shows approval_status: approved.

# How it works:
# The child sub-flow contains a pause: pause_for_legal_approval calls async_pause_for with
# resume_to={"event": "LegalApprovalSubmitted"}, which means the child waits for that event
# to be fired before continuing to apply_legal_approval.
# to_sub_flow() projects this child-level interrupt up to the parent execution namespace.
# The root interrupt dict (from execution.get_pending_interrupts()) contains three extra fields
# that describe the child context:
#   local_interrupt_id   — the interrupt_id declared inside the child flow
#   resume_to            — the resume target declared inside the child ("LegalApprovalSubmitted")
#   sub_flow_frame_id    — internal ID of the child execution frame
# Calling async_continue_with(root_interrupt_id, approval) on the parent routes the payload
# into the correct child frame and fires "LegalApprovalSubmitted" there, unblocking the child.
# write_back copies child state["approval_summary"] back to the parent, where draft_final_report
# uses it to build the final report.
#
# Flow:
# async_start(REVIEW_PACKAGE)
#   |
#   v
# package_review (parent)  ->  state["doc_id"], state["finding_count"]
#   |
#   v
# to_sub_flow(child_flow, capture={input:"value"}, write_back={runtime_data:{…}})
#   |  [child starts]
#   |    v
#   |    pause_for_legal_approval  ->  async_pause_for(interrupt_id="scheduled-legal-approval",
#   |                                                  resume_to={"event":"LegalApprovalSubmitted"})
#   |    [PAUSED — interrupt surfaced as root-level interrupt in parent]
#   |
# execution.save() -> saved_state
# [--- cross-session boundary ---]
# restored.load(saved_state)
# restored.async_continue_with(root_interrupt_id, {approved:True, reviewer:…})
#   |
#   v  (child fires LegalApprovalSubmitted)
#   |    v
#   |    apply_legal_approval  ->  child state["approval_summary"] = {status:"approved", …}
#   |  [child closes; write_back copies approval_summary to parent state]
#   |
#   v
# draft_final_report (parent)  ->  state["final_report"] = {approval_status:"approved", …}
#   |
# async_close()
