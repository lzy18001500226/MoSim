# PDF Export Dry-Run Plan, 2026-06-10

Status: `dry_run_pdf_export_plan_not_final_output`

## Summary

- Source docs ready: `True`
- Pandoc available: `True`
- PDF engine available: `False`
- Selected PDF engine: ``
- Source edit approved for export: `False`
- Final artifacts ready: `False`
- Safe to run PDF export now: `False`
- Runs Pandoc now: `False`
- Generates final outputs: `False`

## Claim Boundary

- This is a dry-run export command plan only.
- It does not run Pandoc.
- It does not create Results/submission.
- It does not write PDF files.
- It does not record or render demo video.
- It does not write PMO final acceptance.

## Tooling

- Pandoc available: `True`
- Pandoc source: `D:\Dev\Anaconda3\Library\bin\pandoc.EXE`

| Engine | Available | Source |
|---|---|---|
| xelatex | False | `` |
| lualatex | False | `` |
| tectonic | False | `` |
| pdflatex | False | `` |
| wkhtmltopdf | False | `` |
| weasyprint | False | `` |

## Commands After Approval

| Export | Source | Output | Runs Now | Blocked By | Command |
|---|---|---|---|---|---|
| user_manual_pdf | `Docs/user_manual.md` | `Results/submission/user_manual.pdf` | `False` | final_artifacts_missing, pdf_engine_missing, report_source_edit_not_approved | `pandoc Docs/user_manual.md --from markdown --standalone --pdf-engine=<approved_pdf_engine> --output Results/submission/user_manual.pdf` |
| simulation_analysis_report_pdf | `Docs/simulation_report.md` | `Results/submission/simulation_analysis_report.pdf` | `False` | final_artifacts_missing, pdf_engine_missing, report_source_edit_not_approved | `pandoc Docs/simulation_report.md --from markdown --standalone --pdf-engine=<approved_pdf_engine> --output Results/submission/simulation_analysis_report.pdf` |

## Blockers

- `pdf_engine_missing`: no preferred Pandoc PDF engine is available on PATH Needed action: install or expose xelatex, lualatex, tectonic, wkhtmltopdf, or another approved engine
- `report_source_edit_not_approved`: source-output readiness does not permit final PDF export yet Needed action: obtain explicit human/PMO approval for report-source edits and final PDF export
- `final_artifacts_missing`: final artifact manifest still reports missing final outputs Needed action: after approved export and video creation, rerun final artifact manifest check

## Next Gates After Approval

- Create Results/submission only after explicit approval.
- Run the selected Pandoc commands after source edits and export are approved.
- Run check_final_submission_artifact_manifest.py without --allow-missing.
- Do not write PMO final acceptance until PDFs, demo video, and review evidence exist.
