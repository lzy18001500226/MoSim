# Final Submission Human Decision Diff Template, 2026-06-10

Status: `human_decision_diff_template_not_execution`

## Summary

- Report-source fields: `8`
- Final-output actions: `3`
- Final-output fields: `15`
- Applies decisions now: `False`
- Edits decision templates now: `False`
- Generates final outputs: `False`
- Final acceptance: `False`

## Decision Groups

### A1-report-source-edit-decision

- Owner: `user_or_PMO`
- Source template: `Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision.template.json`
- Required checker after edit: `python Scripts/quality/check_report_source_edit_decision.py`

| Field | Current | Allowed | Notes |
|---|---|---|---|
| `decision` | `"pending_review"` | `["pending_review", "approved", "rejected", "narrowed"]` | Keep pending_review, or choose approved/rejected/narrowed after reviewing preview snippets. |
| `decision_owner` | `"<user_or_PMO>"` | `["<non-placeholder user_or_PMO identity>"]` | Required for approved or narrowed decisions. |
| `decided_at` | `"<ISO8601_after_review>"` | `["<ISO8601_after_review>"]` | Required for approved or narrowed decisions. |
| `approved_preview_ids` | `[]` | `["preserve_final_acceptance_boundary_preview", "rewrite_formation_next_stage_boundary_preview", "insert_visual_trajectory_review_candidate_subsection_preview", "insert_fault_tolerance_candidate_subsection_preview", "insert_multi_uav_formation_candidate_subsection_preview", "condense_smoke_and_legacy_sections_preview", "renumber_l1_residual_subsection_preview"]` | Must name approved preview ids when decision is approved or narrowed. |
| `rejected_preview_ids` | `[]` | `["preserve_final_acceptance_boundary_preview", "rewrite_formation_next_stage_boundary_preview", "insert_visual_trajectory_review_candidate_subsection_preview", "insert_fault_tolerance_candidate_subsection_preview", "insert_multi_uav_formation_candidate_subsection_preview", "condense_smoke_and_legacy_sections_preview", "renumber_l1_residual_subsection_preview"]` | May record rejected preview ids for rejected or narrowed decisions. |
| `narrowed_scope_notes` | `""` | `["<freeform reviewed scope note>"]` | Required in practice when decision is narrowed. |
| `review_notes` | `""` | `["<freeform review note>"]` | Recommended for approved or narrowed decisions. |
| `safe_to_apply_report_source_edits` | `false` | `[false, true]` | May become true only when decision is approved or narrowed and approved_preview_ids is non-empty. |

### A6-final-output-execution-decision

- Owner: `user_or_PMO`
- Source template: `Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision.template.json`
- Required checker after edit: `python Scripts/quality/check_final_output_execution_decision.py`

| Field | Current | Allowed | Notes |
|---|---|---|---|
| `actions.pdf_export.decision` | `"pending_review"` | `["pending_review", "approved", "rejected"]` | Approval still requires the upstream readiness gate to be true. |
| `actions.pdf_export.approved` | `false` | `[false, true]` | Must match decision==approved; true is invalid while upstream gate is false. |
| `actions.pdf_export.approved_by` | `"<user_or_PMO>"` | `["<non-placeholder user_or_PMO identity>"]` | Required when this action is approved. |
| `actions.pdf_export.approved_at` | `"<ISO8601_after_review>"` | `["<ISO8601_after_review>"]` | Required when this action is approved. |
| `actions.pdf_export.review_notes` | `""` | `["<freeform review note>"]` | Recommended when this action is approved. |
| `actions.demo_video_recording.decision` | `"pending_review"` | `["pending_review", "approved", "rejected"]` | Approval still requires the upstream readiness gate to be true. |
| `actions.demo_video_recording.approved` | `false` | `[false, true]` | Must match decision==approved; true is invalid while upstream gate is false. |
| `actions.demo_video_recording.approved_by` | `"<user_or_PMO>"` | `["<non-placeholder user_or_PMO identity>"]` | Required when this action is approved. |
| `actions.demo_video_recording.approved_at` | `"<ISO8601_after_review>"` | `["<ISO8601_after_review>"]` | Required when this action is approved. |
| `actions.demo_video_recording.review_notes` | `""` | `["<freeform review note>"]` | Recommended when this action is approved. |
| `actions.final_acceptance_packet.decision` | `"pending_review"` | `["pending_review", "approved", "rejected"]` | Approval still requires the upstream readiness gate to be true. |
| `actions.final_acceptance_packet.approved` | `false` | `[false, true]` | Must match decision==approved; true is invalid while upstream gate is false. |
| `actions.final_acceptance_packet.approved_by` | `"<user_or_PMO>"` | `["<non-placeholder user_or_PMO identity>"]` | Required when this action is approved. |
| `actions.final_acceptance_packet.approved_at` | `"<ISO8601_after_review>"` | `["<ISO8601_after_review>"]` | Required when this action is approved. |
| `actions.final_acceptance_packet.review_notes` | `""` | `["<freeform review note>"]` | Recommended when this action is approved. |

## Claim Boundary

- This is a non-applying diff template for human review.
- It does not edit report_source_edit_decision.template.json.
- It does not edit final_output_execution_decision.template.json.
- It does not approve pending decisions.
- It does not apply report-source edits.
- It does not export PDFs.
- It does not record or render demo video.
- It does not write PMO final acceptance.
