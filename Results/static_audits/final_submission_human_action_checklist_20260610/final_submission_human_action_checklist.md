# Final Submission Human Action Checklist, 2026-06-10

Status: `human_action_checklist_not_execution`

## Summary

- Source blockers: `16`
- Actions: `6`
- Automated execution allowed: `False`
- Generates final outputs: `False`
- Final acceptance: `False`

## Claim Boundary

- This checklist is a human-action planning artifact.
- It does not install tools.
- It does not approve report-source edits.
- It does not export PDFs or record video.
- It does not write PMO final acceptance.

## Actions

### A1-approve-or-reject-report-source-edits

- Priority: `1`
- Owner: `user_or_PMO`
- Action: Review the simulation-report source edit preview/readiness gate and approve, reject, or narrow final report-source edits.
- Success evidence: A reviewed decision is recorded and the source edit readiness gate can be regenerated with the decision reflected.
- Source blockers:
  - `source_output_readiness/report_source_edit_not_approved`: simulation report source edit readiness gate does not permit applying preview snippets
  - `source_output_readiness/report_source_edit_application_plan_not_ready`: simulation report source edit application plan is not approved for application
  - `source_output_readiness/report_source_edit_application_not_applied`: no evidence shows the approved report-source application plan has been applied to Docs/simulation_report.md
  - `pdf_export_plan/report_source_edit_not_approved`: source-output readiness does not permit final PDF export yet

### A2-provide-pdf-engine

- Priority: `2`
- Owner: `local_environment_owner`
- Action: Install or expose a Pandoc-compatible PDF engine such as xelatex, lualatex, tectonic, pdflatex, wkhtmltopdf, or weasyprint.
- Success evidence: The PDF export dry-run plan reports pdf_engine_available=true.
- Source blockers:
  - `pdf_export_plan/pdf_engine_missing`: no preferred Pandoc PDF engine is available on PATH

### A3-review-demo-storyboard

- Priority: `3`
- Owner: `user_or_PMO`
- Action: Review the demo-video storyboard, wording, evidence mapping, and forbidden claims before any recording.
- Success evidence: Storyboard review decision is recorded and safe_to_record_demo_video_now can become true in a follow-up gate.
- Source blockers:
  - `demo_video_storyboard/manual_storyboard_review_required`: storyboard content must be reviewed before recording
  - `final_acceptance_prereq/demo_video_recording_not_approved`: storyboard plan does not permit video recording yet

### A4-create-reviewed-final-artifacts

- Priority: `4`
- Owner: `packaging_or_manual_operator`
- Action: After approvals, create reviewed final PDFs and demo_video.mp4, then rerun the final artifact manifest without --allow-missing.
- Success evidence: Final artifact manifest reports final_submission_artifacts_ready=true.
- Source blockers:
  - `source_output_readiness/final_outputs_missing`: final PDFs, demo video, or PMO final acceptance packet are missing
  - `pdf_export_plan/final_artifacts_missing`: final artifact manifest still reports missing final outputs
  - `demo_video_storyboard/demo_video_not_recorded`: Results/submission/demo_video.mp4 is missing
  - `final_acceptance_prereq/final_artifacts_not_ready`: one or more final artifacts are missing or failing

### A5-rerun-readiness-gates

- Priority: `5`
- Owner: `operator`
- Action: Rerun PDF, video, artifact, source-output, acceptance-prereq, and dashboard gates after A1-A4 are complete.
- Success evidence: Dashboard blocking_gate_count decreases and final_submission_ready reflects current artifacts.
- Source blockers:
  - `final_acceptance_prereq/pdf_export_not_ready`: PDF export dry-run plan does not permit final PDF export yet
  - `final_acceptance_prereq/source_output_readiness_blocks_acceptance`: source-output readiness does not permit writing final acceptance

### A6-review-final-output-execution-decision

- Priority: `6`
- Owner: `user_or_PMO`
- Action: Review and approve or keep pending the final-output execution decision for PDF export, demo video, and final acceptance packet writing.
- Success evidence: The final output execution decision checker reports the relevant authorizes_* fields as true after upstream gates pass.
- Source blockers:
  - `final_output_execution_decision/authorizes_pdf_export`: PDF export execution is not authorized
  - `final_output_execution_decision/authorizes_demo_video_recording`: demo video recording/rendering is not authorized
  - `final_output_execution_decision/authorizes_final_acceptance_packet`: canonical final acceptance packet writing is not authorized
