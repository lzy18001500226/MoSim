# Report Source Edit Decision Template, 2026-06-10

Status: `decision_template_pending_review_not_approval`

## Summary

- Available previews: `7`
- Approved previews: `0`
- Decision pending: `True`
- Safe to apply report source edits: `False`
- Edits report source: `False`
- Final acceptance: `False`

## Validation

- OK: `True`
- Decision: `pending_review`
- Issues: `0`
- Warnings: `1`

## Claim Boundary

- This artifact is a decision template only.
- It does not approve report-source edits.
- It does not edit Docs/simulation_report.md.
- It does not generate final PDFs/video or PMO final acceptance.

## Template

```json
{
  "decision_id": "report_source_edit_decision_20260610",
  "status": "decision_template_pending_review",
  "decision": "pending_review",
  "valid_decisions": [
    "pending_review",
    "approved",
    "rejected",
    "narrowed"
  ],
  "decision_owner": "<user_or_PMO>",
  "decided_at": "<ISO8601_after_review>",
  "applies_to": {
    "simulation_report": "Docs/simulation_report.md",
    "patch_preview": "Results/static_audits/simulation_report_patch_preview_20260610/simulation_report_patch_preview.json",
    "source_edit_readiness_gate": "Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.json"
  },
  "approved_preview_ids": [],
  "rejected_preview_ids": [],
  "narrowed_scope_notes": "",
  "review_notes": "",
  "required_boundaries": [
    "Do not claim final PMO acceptance.",
    "Do not claim final submission ready.",
    "Do not claim planner_ready or closed_loop.",
    "Do not claim UE build/runtime/editor success.",
    "Do not delete historical evidence without explicit approval."
  ],
  "available_preview_ids": [
    "preserve_final_acceptance_boundary_preview",
    "rewrite_formation_next_stage_boundary_preview",
    "insert_visual_trajectory_review_candidate_subsection_preview",
    "insert_fault_tolerance_candidate_subsection_preview",
    "insert_multi_uav_formation_candidate_subsection_preview",
    "condense_smoke_and_legacy_sections_preview",
    "renumber_l1_residual_subsection_preview"
  ],
  "safe_to_apply_report_source_edits": false
}
```
