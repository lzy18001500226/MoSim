#!/usr/bin/env python3
"""CoAgent dispatch helpers for department-thread routing and packet exchange."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.dispatch.conversation_registry import THREADS_JSON, get_thread_by_department, load_registry, save_registry
from CoAgent.result_router import result_router


MWORKS_DEPARTMENTS = {
    "MWorksDynamicsControlAgent",
    "MWorksGraphicalModelAuditAgent",
}
ROS2_DEPARTMENTS = {
    "ROS2RuntimeAgent",
}
UE_DEPARTMENTS = {
    "UEExperimentConsoleAgent",
}
ASSET_DEPARTMENTS = {
    "Sunray150AssetPBRAgent",
}


def _department_local_planning_contract_lines() -> list[str]:
    return [
        "",
        "[Department Local Planning And Subagent Decision Contract]",
        "Before any non-trivial business work, derive and record a department-local task graph. This is a planning requirement, not a requirement to use at least one sub-agent.",
        "- Return/blocker packets must include: department_local_goal, critical_path_steps, parallelizable_slices, subagent_plan, subagent_plan_reason, subagents_used, verification_gates, and manual_review_or_blocker_triggers.",
        "- subagent_plan must be one of: used, available_but_not_useful, unavailable, unsafe.",
        "- Use disposable sub-agents only for bounded independent research, review, file-level audit, or disjoint write slices when the current runtime exposes that capability and the resource scope is safe.",
        "- If no disposable sub-agent is used, set subagents_used=[] and give a concrete subagent_plan_reason such as no independent slice, resource conflict, unavailable tool surface, or unsafe shared GUI/runtime state.",
        "- Disposable sub-agents are not durable departments, hidden queues, visible-thread replacements, or a way to create/fork/rename/archive visible threads.",
    ]


def _department_execution_acceptance_contract_lines() -> list[str]:
    return [
        "",
        "[Department Execution And Acceptance Contract]",
        "Treat the department as an accountable owner, not a passive prompt sink. After the local plan is written, execute the critical path autonomously inside the declared scope until completion or a real blocker.",
        "- Run the task-specific infrastructure preflight before business work. Examples: MWORKS sentinel/screenshots for MWORKS work, ROS2 stale-process/topic/source-window checks for ROS2 work, UE/source-static/build-scope checks for UE work, Blender/source-asset availability checks for visual asset work.",
        "- If a preflight, GUI, license, runtime, build, tool-surface, source-data, or permission issue blocks the task, stop the domain work and return a blocker promptly. Do not spend turns producing unrelated JSON, tuning parameters, or retrying solver/runtime/model steps after the infrastructure gate failed.",
        "- Report phase checkpoints in the return/blocker packet for long or live work: what phase ran, what evidence was inspected, what changed, and what remains blocked.",
        "- The expected engineering output must match the task type. Model/simulation/layout work needs model edits, check/simulation/native result/metrics, diagram/layout screenshots, or wiring observations. ROS2 runtime work needs topic/process/source-window/log/evidence artifacts. UE work needs source/static/build/runtime evidence according to scope. Asset/PBR work needs Blender/UE asset files, rendered review images, material manifests, or visual-review artifacts.",
        "- JSON task/result/blocker packets, ledger rows, and progress notes are control-plane evidence. They do not count as engineering output unless the task is explicitly diagnostic_only, rule_sync_only, preflight_drill_only, dispatch_surface_diagnostic, or static_inventory_only.",
        "- If the task produces a user-review artifact such as an image, video, native result viewer, or model diagram, request PMO display/review rather than returning only a path.",
        "- A completed return must state which verification gates passed and which claims are still forbidden. PMO may reject completed packets that lack the declared engineering outputs, omit the local plan/subagent decision, or turn a real blocker into completed metadata.",
    ]


def _ros2_runtime_gate_contract_lines(department: str) -> list[str]:
    if department not in ROS2_DEPARTMENTS:
        return []
    return [
        "",
        "[ROS2 Runtime Gate Contract]",
        "This is a ROS2/RViz2/FAST-LIO/planner-runtime department. Treat each live graph as a scarce probe with explicit boundaries, not an open-ended retry loop.",
        "- Start with the task packet and current workflow evidence. If the task says existing-evidence-only or no-rerun, do not launch ROS2; close from existing evidence or return a blocker.",
        "- Before any live ROS2 graph, record a runtime preflight: ROS2 environment/source status, stale MoSim/FAST-LIO/planner processes, expected source-window availability, intended topics, forbidden topics, probe_count budget, and cleanup plan.",
        "- The task packet must declare expected_engineering_outputs. For ROS2 runtime work these are concrete source-window, topic, process, log, FAST-LIO/planner evidence, forbidden-topic absence, and cleanup artifacts as applicable.",
        "- A live ROS2 task must record actual runtime evidence such as source-window/topic stamps, topic rates/counts, FAST-LIO output counts, loop-back counts, logs, forbidden-topic absence, and cleanup. A packet alone is not runtime progress.",
        "- If source timestamps regress, FAST-LIO callback loop-back remains, required topics are absent, stale processes cannot be cleaned, or the task-specific one-probe budget is exhausted, stop and return a status=blocked packet. Do not rerun until PMO issues a new task.",
        "- Never advance from a diagnostic FAST-LIO/source gate into RViz2, planner/EGO, PositionCommand, 20 Hz adapter, TF/RViz readiness, or controller claims unless the task packet explicitly authorizes that phase and the previous gate passed.",
        "- Return fields for non-trivial ROS2 work must include ros2_preflight_before, probe_count, source_window_evidence, topic_evidence, fastlio_or_planner_evidence as applicable, forbidden_topic_absence, cleanup_summary, actual_engineering_outputs, expected_engineering_outputs, manual_review_or_blocker_triggers, and claim_boundary.",
        "- Keep the claim boundary explicit: nonzero topics or RViz visibility alone do not prove FAST-LIO success, localization quality, planner_ready, controller performance, mission success, or closed_loop.",
    ]


def _ue_runtime_gate_contract_lines(department: str) -> list[str]:
    if department not in UE_DEPARTMENTS:
        return []
    return [
        "",
        "[UE Runtime And Review Gate Contract]",
        "This is a UE experiment-console / scene-interaction department. UE is an operator/review/render surface, not the authority for controller or planner success.",
        "- Start by classifying the task scope as source-static, build, editor/runtime, or manual-review. Run only the matching preflight: source/schema checks for static work, build/log checks for build work, and bounded editor/runtime checks for live work.",
        "- The task packet must declare expected_engineering_outputs for the selected scope.",
        "- Completed UE work must produce scope-matched evidence: C++/Blueprint/schema edits with tests for source work, build/log evidence for build work, runtime echo/transport evidence for command work, or screenshots/review packets for visual review.",
        "- Do not treat a JSON packet, scene registry row, or command schema as runtime ack. Runtime ack requires the task-authorized UE/bridge/ROS2/MWORKS evidence path.",
        "- Do not use UE to teleport UAV pose, feed global truth to planners, label controller success, or replace MWORKS/ROS2 gates.",
        "- If a review artifact is produced, ask PMO to open/display it or send a concise review prompt; do not return only a file path.",
    ]


def _sunray_asset_gate_contract_lines(department: str) -> list[str]:
    if department not in ASSET_DEPARTMENTS:
        return []
    return [
        "",
        "[Sunray150 Asset And PBR Gate Contract]",
        "This is a Sunray150 visual-asset/PBR department. The accepted route is the DAE-derived Blender asset line; visual work must not change dynamics, geometry truth, extrinsics, or controller/planner state.",
        "- Read the Sunray PBR workflow before editing Blender, DAE/FBX/glTF, UE materials, or material scripts.",
        "- Start by checking source asset availability, component identity, material evidence, UV/material-slot limitations, and intended review outputs.",
        "- The task packet must declare expected_engineering_outputs for the asset/PBR pass.",
        "- Completed asset work must produce real visual artifacts: Blender/UE asset edits, material manifests, rendered close-ups/contact sheets, texture/PBR map evidence, or explicit failed-review images. Packets alone are not material progress.",
        "- Use component-first PBR evidence. Do not claim final material acceptance from whole-aircraft grey/color tuning or from a Base Color edit.",
        "- If a part identity, license, UV, geometry, export/import, or review-window issue blocks the task, stop and return a blocker instead of painting over unknowns.",
        "- Geometry assembly, rotor centers, mass/inertia/motor/thrust constants, FAST-LIO extrinsics, ROS2/MWORKS/UE runtime behavior, controller, and planner files are out of scope unless PMO issues a separate task.",
        "- If the output needs human review, request PMO display/open the image or Blender scene; do not only send a path.",
    ]


def _mworks_live_gate_contract_lines(department: str) -> list[str]:
    if department not in MWORKS_DEPARTMENTS:
        return []
    return [
        "",
        "[MWORKS Live Gate Contract]",
        "This is a MWORKS department. Every MWORKS department task must begin with a non-invasive existing-window activation/screenshot preflight, even when the business task is static file organization.",
        "- The task packet must include mworks_live_gate and set mworks_window_evidence_touched=true.",
        "- If any MWORKS/Sysplorer/Syslab MCP, model load/check/translate/simulate, plot, animation, or GUI review may occur after the preflight, set mworks_live_gate.live_mworks_touched=true.",
        "- If the business task is static file-only after the preflight, set mworks_live_gate.live_mworks_touched=false, but still run the activation/screenshot preflight and return mworks_window_evidence_touched=true.",
        "- First run: python Scripts\\agent\\check_mworks_gui_sentinel.py --output Results\\mworks_gui_incidents\\<task_id>\\gui_sentinel_before.json",
        "- Then run: powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\\tools\\capture_window_background.ps1 -TitleRegex 'Sysplorer|MWORKS|Quadrotor|AWFF' -OutDir Results\\mworks_background_capture\\<task_id> -RestoreMinimized",
        "- The background capture script parameter is -OutDir; do not use -OutputDir.",
        "- Treat the screenshot/sentinel as the first business gate. A static ACK or PMO-side screenshot does not satisfy this task; the target department must collect and classify its own evidence in this turn.",
        "- The sentinel is an all-window license gate. If any relevant MWORKS/Sysplorer/Syslab window is demo, login/activation, authorization-failed, GUI-error, mixed, or visible unknown, the whole MWORKS task is blocked even if another window looks clean or education-mode. Hidden Qt/browser-proxy/helper windows with no license/error text are risk evidence and must be counted, but they do not alone block a clean education preflight.",
        "- Important correction: a Sysplorer education-edition title only proves the visible edition/window marker; it does not prove the account is activated. If only the education window/title is observed, use license_state=education_window_observed_activation_unverified.",
        "- Live MWORKS work must include a current-turn license_api_before probe when available. Do not claim account activation unless the API/result explicitly exposes account activation status. Treat check_model/simulation with no authorization error as task-local license sufficiency evidence, not a permanent activation claim.",
        "- A clean-looking background screenshot is not sufficient if the title, sentinel, or license API still indicates demo/login/authorization risk; hidden login/license panes may require PMO-authorized foreground maximize/focus recovery on the existing window.",
        "- These checks belong to the target department, not PMO. If the department cannot run either check because the tool surface is unavailable, it must still write a blocker with status=unavailable, license_state=sentinel_unavailable_blocked, and no live MWORKS work.",
        "- Return activation_sentinel_before, gui_sentinel_before, background_screenshot_before, activation_state_observation, license_state, will_not_click_activation_login=true, live_mworks_touched, and mworks_window_evidence_touched. For live_mworks_touched=true, also return license_api_before when the API surface is available.",
        "- The task packet must declare expected_engineering_outputs. For model/simulation/layout work, expected outputs must include concrete .mo/package.mo edits, check_model/SimulateModel/native_result/metrics evidence, diagram/layout screenshots, or wiring observations as applicable.",
        "- JSON result/blocker/task packets, ledger updates, and PROGRESS notes are control-plane evidence only. They do not count as MWORKS engineering progress unless the task is explicitly diagnostic_only, rule_sync_only, preflight_drill_only, dispatch_surface_diagnostic, or static_inventory_only.",
        "- activation_state_observation must say what the sentinel, window title, or screenshot actually showed, for example one education-mode window, demo marker, login prompt, activation prompt, mixed state, visible unknown window, hidden helper-window risk count, or unknown/unavailable evidence.",
        "- Do not only return paths. Read the sentinel JSON/capture manifest or inspect the screenshot metadata enough to classify the observed activation state in this same turn.",
        "- license_state must be a concrete classification such as education_window_observed_activation_unverified, license_api_recorded_education_version_only, mixed_education_and_demo_blocked, demo_blocked, login_required, authorization_failed, gui_error_report_blocked, sentinel_unavailable_blocked, or unknown_blocked; vague values like ok/normal/looks_fine are not acceptable.",
        "- During live MWORKS work, continue taking and inspecting background screenshots at phase checkpoints, not only preflight. Return mworks_phase_screenshots and mworks_phase_observations when live_mworks_touched=true.",
        "- R1 simulation/control tasks should capture after load/check and after simulate/plot/animation phases when those phases run. R2 graphical/layout tasks should capture during or after graphical layout review and inspect missing wires, disconnected blocks, poor routing, or wrong window state.",
        "- If activation/license/login/authorization/GUI-error state appears at preflight or mid-task, classify it as a P0 MWORKS infrastructure incident: stop live work, return a blocker, and make PMO send both sparse WeChat and sparse email alert. Do not rely on WeChat alone.",
        "- Demo edition, unactivated/login/authorization state, GUI error-report dialog, mixed license state, visible unknown window, unknown sentinel state, or unavailable screenshot/sentinel tooling is a blocker and must be returned as status=blocked; do not click login/activation/error-report controls, open a fresh window, close/restart MWORKS, or tune solver/model code.",
        "- Departments do not perform foreground login/activation recovery. They preserve evidence and return the blocker; PMO owns any user-authorized recovery and must re-prove education/license state before redispatch.",
        "- PMO may reject the packet with Scripts/quality/check_mworks_live_gate.py --expect department if these fields are missing.",
    ]


def list_departments(args: argparse.Namespace) -> dict[str, Any]:
    return load_registry(args.registry)


def set_thread(args: argparse.Namespace) -> dict[str, Any]:
    data = load_registry(args.registry)
    found = False
    for item in data["threads"]:
        if item["department"] == args.department:
            item["thread_id"] = args.thread_id
            item["surface"] = args.surface
            item["status"] = args.status
            found = True
            break
    if not found:
        raise SystemExit(f"unknown department: {args.department}")
    save_registry(data, args.registry)
    return data


def build_dispatch_envelope(args: argparse.Namespace) -> dict[str, Any]:
    task = runtime.export_task_packet(args)
    task_text = runtime.format_task_packet_text(args)["text"]
    target = get_thread_by_department(args.department, args.registry)
    return {
        "target_department": args.department,
        "thread_name": target["thread_name"],
        "thread_id": target["thread_id"],
        "surface": target["surface"],
        "status": target["status"],
        "task_packet": task,
        "task_packet_text": task_text,
    }


def build_department_task_text(args: argparse.Namespace) -> dict[str, Any]:
    envelope = build_dispatch_envelope(args)
    lines = [
        "[MoSim Department Dispatch]",
        f"target_department: {envelope['target_department']}",
        f"thread_name: {envelope['thread_name']}",
        f"thread_id: {envelope['thread_id']}",
        f"surface: {envelope['surface']}",
        f"dispatch_status: {envelope['status']}",
        "",
        envelope["task_packet_text"],
        "",
        "[Execution Contract]",
        "1. Stay inside the declared read/write scope.",
        "2. Do not expand scope without returning a blocker.",
        "3. Write one MoSim Result Packet to the declared result_file path.",
        "4. If blocked, report blocker and next recommended action.",
        *_department_local_planning_contract_lines(),
        *_department_execution_acceptance_contract_lines(),
        *_ros2_runtime_gate_contract_lines(envelope["target_department"]),
        *_ue_runtime_gate_contract_lines(envelope["target_department"]),
        *_sunray_asset_gate_contract_lines(envelope["target_department"]),
        *_mworks_live_gate_contract_lines(envelope["target_department"]),
    ]
    return {
        "task_id": envelope["task_packet"]["task_id"],
        "department": envelope["target_department"],
        "text": "\n".join(lines),
    }


def import_result_packet(args: argparse.Namespace) -> dict[str, Any]:
    return result_router.import_packet(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            packet=Path(args.packet),
            claim_token=args.claim_token or "",
            archive=True,
            archive_invalid=True,
        )
    )


def import_result_text(args: argparse.Namespace) -> dict[str, Any]:
    return result_router.import_packet(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            packet=Path(args.packet),
            claim_token=args.claim_token or "",
            archive=True,
            archive_invalid=True,
        )
    )


def build_review_brief(args: argparse.Namespace) -> dict[str, Any]:
    packet = runtime.export_result_packet(args)
    lines = [
        "[MoSim Review Brief]",
        f"task_id: {packet['task_id']}",
        f"status: {packet['status']}",
        f"owner: {packet['owner']}",
        f"role: {packet['role']}",
        f"summary: {packet['summary']}",
        f"read_scope: {json.dumps(packet['read_scope'], ensure_ascii=False)}",
        f"write_scope: {json.dumps(packet['write_scope'], ensure_ascii=False)}",
        "review_checklist:",
        "- verify the task stayed inside scope",
        "- verify evidence is sufficient",
        "- verify next action or blocker is coherent",
        "- return approval or follow-up",
    ]
    return {"task_id": packet["task_id"], "text": "\n".join(lines)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    list_parser.set_defaults(func=list_departments)

    set_parser = subparsers.add_parser("set-thread")
    set_parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    set_parser.add_argument("--department", required=True)
    set_parser.add_argument("--thread-id", required=True)
    set_parser.add_argument("--surface", default="codex_app_or_vscode")
    set_parser.add_argument("--status", default="ready")
    set_parser.set_defaults(func=set_thread)

    dispatch_parser = subparsers.add_parser("dispatch-envelope")
    runtime.add_common(dispatch_parser)
    dispatch_parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    dispatch_parser.add_argument("--department", required=True)
    dispatch_parser.add_argument("--task-id", required=True)
    dispatch_parser.set_defaults(func=build_dispatch_envelope)

    dispatch_text_parser = subparsers.add_parser("department-task-text")
    runtime.add_common(dispatch_text_parser)
    dispatch_text_parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    dispatch_text_parser.add_argument("--department", required=True)
    dispatch_text_parser.add_argument("--task-id", required=True)
    dispatch_text_parser.set_defaults(func=build_department_task_text)

    import_parser = subparsers.add_parser("import-result")
    runtime.add_common(import_parser)
    import_parser.add_argument("--packet", required=True)
    import_parser.add_argument("--claim-token", default="")
    import_parser.set_defaults(func=import_result_packet)

    import_text_parser = subparsers.add_parser("import-result-text")
    runtime.add_common(import_text_parser)
    import_text_parser.add_argument("--packet", required=True)
    import_text_parser.add_argument("--claim-token", default="")
    import_text_parser.set_defaults(func=import_result_text)

    review_parser = subparsers.add_parser("review-brief")
    runtime.add_common(review_parser)
    review_parser.add_argument("--task-id", required=True)
    review_parser.set_defaults(func=build_review_brief)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    if args.command in {"department-task-text", "review-brief"}:
        print(result["text"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
