# Non-Frontend Reproducibility and Demo Delivery Manifest

Status: `delivery_manifest_not_final_submission_acceptance`

## Scope

- Frontend excluded: `True`
- Runtime authority: `ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl`
- Controller counts: `{'accepted': 27, 'executed_blocked': 25, 'not_run': 15}`
- Final A/B counts: `{'accepted': 1, 'executed_blocked': 11, 'not_run': 2}`

## Reproduction Commands

1. `python -m pytest Scripts/tests/test_non_frontend_requirement_evidence_matrix.py Scripts/tests/test_non_frontend_report_source.py Scripts/tests/test_non_frontend_report_figures.py Scripts/tests/test_non_frontend_delivery_manifest.py Scripts/tests/test_non_frontend_submission_package_manifest.py Scripts/tests/test_non_frontend_final_qa_audit.py Scripts/tests/test_final_controller_ab_matrix.py -q`
2. `python Scripts/quality/build_non_frontend_requirement_evidence_matrix.py`
3. `python Scripts/quality/build_non_frontend_report_source.py`
4. `python Scripts/quality/build_non_frontend_report_figures.py`
5. `python Scripts/quality/build_non_frontend_delivery_manifest.py`
6. `python Scripts/quality/build_non_frontend_submission_package_manifest.py`
7. `python Scripts/quality/build_non_frontend_final_qa_audit.py`

## Demo Storyboard

| # | Scene | Evidence | Allowed claim |
|---:|---|---|---|
| 1 | Scope and evidence boundary | requirement_matrix, report_source | Show the project boundary and distinguish accepted, blocked, and not-run evidence. |
| 2 | Accepted controller and baseline evidence | controller_matrix, figure_manifest | Show accepted controller rows and saved metrics/figures without general superiority claims. |
| 3 | Safety and FTC | safety, ftc | Show the declared safety modes and bounded rotor-effectiveness FTC recovery. |
| 4 | Three-UAV formation | formation | Show bounded formation evidence; do not claim autonomous exploration. |
| 5 | Learning-control experiment | learning | Show Neural Residual and RL experimental routes as selectable=false report evidence. |
| 6 | Known limits and closeout | motor_fault_blocker, final_ab | Show unresolved runtime limits and the exact claim ceiling. |

## Required Human Outputs

| Path | Status |
|---|---|
| `Results/submission/user_manual.pdf` | `pending_human_export_and_review` |
| `Results/submission/simulation_analysis_report.pdf` | `pending_human_export_and_review` |
| `Results/submission/demo_video.mp4` | `pending_reviewed_recording` |
| `Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json` | `pending_final_review` |

## Claim Boundary

- This manifest proves reproducibility inputs and delivery structure, not final submission acceptance.
- It does not run Gazebo or MWORKS, export PDFs, record video, or write a final acceptance packet.
- A blocked or not-run row cannot be presented as a successful controller result.

## Forbidden Claims

- `final_submission_ready`
- `all_controller_gazebo_acceptance`
- `gain_scheduled_pid_general_superiority`
- `neural_or_rl_performance_accepted`
- `complete_motor_outage_recovery`
- `frontend_closed_loop_authority`
