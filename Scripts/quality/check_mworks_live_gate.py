#!/usr/bin/env python3
"""Validate MWORKS live-session gate fields in MoSim task/return packets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_TASK_FIELDS = {
    "live_mworks_touched",
    "mworks_window_policy",
    "required_return_fields",
    "blocker_on",
}

REQUIRED_PATROL_TASK_FIELDS = {
    "activation_patrol_owner",
    "recent_patrol_required",
    "max_patrol_age_minutes",
}

REQUIRED_RETURN_FIELDS = {
    "will_not_click_activation_login",
    "live_mworks_touched",
}

REQUIRED_PATROL_RETURN_FIELDS = {
    "mworks_activation_patrol_reference",
}

REQUIRED_LIVE_PHASE_RETURN_FIELDS = {
    "mworks_phase_screenshots",
    "mworks_phase_observations",
}

REQUIRED_LIVE_ACTIVATION_RETURN_FIELDS = {
    "license_api_before",
}

LEGACY_SENTINEL_RETURN_FIELD_NAMES = {
    "activation_sentinel_before",
    "activation_state_observation",
    "background_screenshot_before",
    "gui_sentinel_before",
    "license_state",
    "mworks_window_evidence_touched",
}

REQUIRED_PREFLIGHT_SNIPPETS = [
    "check_mworks_gui_sentinel.py",
    "capture_window_background.ps1",
]

REQUIRED_BLOCKER_SNIPPETS = [
    "demo",
    "unactivated",
    "login",
    "activation",
    "authorization",
    "error-report",
    "unknown",
]

LICENSE_STATE_SNIPPETS = [
    "education",
    "教育",
    "clean_preflight",
    "window_observed",
    "activation_unverified",
    "license_api_verified",
    "demo",
    "演示",
    "unactivated",
    "未激活",
    "login",
    "登录",
    "登陆",
    "activation",
    "激活",
    "authorization",
    "授权",
    "equation",
    "mixed",
    "gui_error",
    "error_report",
    "error-report",
    "sentinel_unavailable",
    "unavailable",
    "unknown",
    "blocked",
]

OBSERVATION_SOURCE_SNIPPETS = [
    "sentinel",
    "gui",
    "window",
    "title",
    "screenshot",
    "capture",
    "manifest",
    "observed",
    "status",
    "窗口",
    "标题",
    "截图",
    "捕获",
    "观察",
    "教育版",
    "演示版",
]

PHASE_OBSERVATION_SNIPPETS = [
    "screenshot",
    "capture",
    "window",
    "title",
    "load",
    "check",
    "simulate",
    "plot",
    "animation",
    "layout",
    "wire",
    "connection",
    "diagram",
    "截图",
    "捕获",
    "窗口",
    "标题",
    "加载",
    "检查",
    "仿真",
    "绘图",
    "动画",
    "布局",
    "走线",
    "连线",
    "图形",
]

BLOCKING_LICENSE_STATE_SNIPPETS = [
    "demo",
    "演示",
    "unactivated",
    "未激活",
    "login",
    "登录",
    "登陆",
    "activation_required",
    "activation_prompt",
    "激活",
    "authorization",
    "授权",
    "equation",
    "mixed",
    "gui_error",
    "error_report",
    "error-report",
    "sentinel_unavailable",
    "unavailable",
    "unknown",
    "blocked",
]

UNVERIFIED_LICENSE_STATE_SNIPPETS = [
    "activation_unverified",
    "window_observed",
]

DIAGNOSTIC_ENGINEERING_MODES = {
    "diagnostic_only",
    "rule_sync_only",
    "preflight_drill_only",
    "dispatch_surface_diagnostic",
    "static_inventory_only",
}

ENGINEERING_OUTPUT_SNIPPETS = [
    ".mo",
    "package.mo",
    "check_model",
    "check model",
    "SimulateModel",
    "simulate",
    "simulation",
    ".msr",
    "Result.msr",
    "native_result",
    "diagram",
    "layout",
    "wire",
    "connection",
    "screenshot",
    "mworks_phase_screenshots",
    "plot",
    "animation",
    "metrics",
    "GetVarTimes",
    "result variable",
    "model_manager",
    "Sysblock",
    "模型",
    "仿真",
    "连线",
    "走线",
    "图形",
    "截图",
    "曲线",
    "结果",
]

JSON_ONLY_SNIPPETS = [
    ".json",
    "result packet",
    "return packet",
    "blocker packet",
    "task packet",
    "ledger",
    "PROGRESS.md",
]


def _load_json(path: Path) -> dict[str, Any]:
    packet_path = path if path.is_absolute() else ROOT / path
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(packet, dict):
        raise SystemExit("packet root must be a JSON object")
    return packet


def _contains_snippet(values: Any, snippet: str) -> bool:
    if isinstance(values, str):
        return snippet.casefold() in values.casefold()
    if isinstance(values, list):
        return any(_contains_snippet(item, snippet) for item in values)
    if isinstance(values, dict):
        return any(_contains_snippet(item, snippet) for item in values.values())
    return False


def _contains_any_snippet(values: Any, snippets: list[str]) -> bool:
    return any(_contains_snippet(values, snippet) for snippet in snippets)


def _engineering_output_mode(packet: dict[str, Any], gate: dict[str, Any] | None = None) -> str:
    value = None
    if gate is not None:
        value = gate.get("engineering_output_mode")
    if value in (None, ""):
        value = packet.get("engineering_output_mode")
    return str(value or "").strip()


def _engineering_outputs(packet: dict[str, Any], gate: dict[str, Any] | None = None) -> Any:
    if gate is not None and "expected_engineering_outputs" in gate:
        return gate.get("expected_engineering_outputs")
    if "expected_engineering_outputs" in packet:
        return packet.get("expected_engineering_outputs")
    for key in (
        "actual_engineering_outputs",
        "engineering_outputs",
        "files_changed",
        "commands_run",
        "evidence",
        "evidence_artifacts",
        "evidence_paths",
    ):
        if key in packet:
            return packet.get(key)
    return None


def _is_diagnostic_engineering_mode(mode: str) -> bool:
    return mode.casefold() in DIAGNOSTIC_ENGINEERING_MODES


def _get_gate(packet: dict[str, Any]) -> dict[str, Any] | None:
    gate = packet.get("mworks_live_gate")
    return gate if isinstance(gate, dict) else None


def _is_false(value: Any) -> bool:
    return value is False or (isinstance(value, str) and value.casefold() == "false")


def _is_true(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.casefold() == "true")


def _has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _has_patrol_reference(packet: dict[str, Any]) -> bool:
    return _has_content(packet.get("mworks_activation_patrol_reference")) or _has_content(
        packet.get("activation_patrol_reference")
    )


def _gate_uses_patrol(gate: dict[str, Any]) -> bool:
    owner = str(gate.get("activation_patrol_owner", "")).casefold()
    return "legacy ops patrol" in owner or "ops patrol" in owner or gate.get("recent_patrol_required") is not None


def _add(findings: list[dict[str, str]], field: str, reason: str, message: str) -> None:
    findings.append({"field": field, "reason": reason, "message": message})


def _check_task(packet: dict[str, Any], *, expect: str) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    gate = _get_gate(packet)

    if gate is None:
        if expect == "static":
            _add(
                findings,
                "mworks_live_gate",
                "missing_static_gate",
                "Static MWORKS tasks must explicitly set mworks_live_gate.live_mworks_touched=false.",
            )
        else:
            _add(
                findings,
                "mworks_live_gate",
                "missing_mworks_live_gate",
                "Live MWORKS/Sysplorer/Syslab task packets must include mworks_live_gate before dispatch.",
            )
        return {"ok": False, "fail_count": len(findings), "findings": findings}

    window_evidence_touched = _is_true(gate.get("mworks_window_evidence_touched"))
    patrol_mode = _gate_uses_patrol(gate)
    requires_full_gate = expect in {"live", "department"} or window_evidence_touched or patrol_mode

    if expect == "static" and not window_evidence_touched:
        if not _is_false(gate.get("live_mworks_touched")):
            _add(
                findings,
                "mworks_live_gate.live_mworks_touched",
                "static_task_missing_false_flag",
                "Static-only MWORKS packets must state live_mworks_touched=false.",
            )
        return {"ok": not findings, "fail_count": len(findings), "findings": findings}

    if expect == "live" and _is_false(gate.get("live_mworks_touched")):
        _add(
            findings,
            "mworks_live_gate.live_mworks_touched",
            "live_task_marked_static",
            "Live MWORKS task packets must set live_mworks_touched=true. Use --expect static only for file-only work.",
        )
        return {"ok": False, "fail_count": len(findings), "findings": findings}

    if expect == "auto" and _is_false(gate.get("live_mworks_touched")) and not requires_full_gate:
        return {"ok": True, "fail_count": 0, "findings": findings}

    missing = sorted(field for field in REQUIRED_TASK_FIELDS if field not in gate)
    for field in missing:
        _add(findings, f"mworks_live_gate.{field}", "missing_required_gate_field", field)

    legacy_sentinel_mode = "activation_sentinel_required" in gate or "background_screenshot_required" in gate
    if patrol_mode:
        for field in sorted(REQUIRED_PATROL_TASK_FIELDS):
            if field not in gate:
                _add(findings, f"mworks_live_gate.{field}", "missing_required_patrol_gate_field", field)
        if not _contains_snippet(gate.get("activation_patrol_owner"), "legacy ops patrol"):
            _add(
                findings,
                "mworks_live_gate.activation_patrol_owner",
                "activation_patrol_owner_not_legacy_ops_patrol",
                "MWORKS activation patrol owner must be legacy ops patrol for department dispatches.",
            )
    elif legacy_sentinel_mode:
        for bool_field in ["activation_sentinel_required", "background_screenshot_required"]:
            if gate.get(bool_field) is not True:
                _add(
                    findings,
                    f"mworks_live_gate.{bool_field}",
                    "required_boolean_not_true",
                    f"{bool_field} must be true when using legacy current-turn sentinel mode.",
                )

        for snippet in REQUIRED_PREFLIGHT_SNIPPETS:
            if not _contains_snippet(gate.get("preflight_order"), snippet):
                _add(
                    findings,
                    "mworks_live_gate.preflight_order",
                    "missing_preflight_step",
                    f"preflight_order must mention {snippet} when using legacy current-turn sentinel mode.",
                )
    elif expect in {"live", "department"}:
        _add(
            findings,
            "mworks_live_gate.activation_patrol_owner",
            "missing_patrol_or_sentinel_gate",
            "MWORKS department tasks must either reference legacy ops patrol activation patrol or explicitly use current-turn sentinel mode.",
        )

    required_return_names = set(REQUIRED_RETURN_FIELDS)
    if patrol_mode:
        required_return_names |= REQUIRED_PATROL_RETURN_FIELDS
    if legacy_sentinel_mode:
        required_return_names |= LEGACY_SENTINEL_RETURN_FIELD_NAMES

    for field_name in sorted(required_return_names):
        if not _contains_snippet(gate.get("required_return_fields"), field_name):
            _add(
                findings,
                "mworks_live_gate.required_return_fields",
                "missing_required_return_field",
                field_name,
            )

    if _is_true(gate.get("live_mworks_touched")):
        live_required = set(REQUIRED_LIVE_PHASE_RETURN_FIELDS)
        if legacy_sentinel_mode and not patrol_mode:
            live_required |= REQUIRED_LIVE_ACTIVATION_RETURN_FIELDS
        for field_name in sorted(live_required):
            if not _contains_snippet(gate.get("required_return_fields"), field_name):
                _add(
                    findings,
                    "mworks_live_gate.required_return_fields",
                    "missing_live_phase_required_return_field",
                    field_name,
                )

    for snippet in REQUIRED_BLOCKER_SNIPPETS:
        if not _contains_snippet(gate.get("blocker_on"), snippet):
            _add(
                findings,
                "mworks_live_gate.blocker_on",
                "missing_blocker_condition",
                snippet,
            )

    if expect == "department":
        expected_outputs = _engineering_outputs(packet, gate)
        output_mode = _engineering_output_mode(packet, gate)
        if not _has_content(expected_outputs):
            _add(
                findings,
                "mworks_live_gate.expected_engineering_outputs",
                "missing_expected_engineering_outputs",
                "MWORKS department task packets must state the engineering deliverables expected beyond the JSON result packet.",
            )
        elif not _is_diagnostic_engineering_mode(output_mode) and not _contains_any_snippet(
            expected_outputs, ENGINEERING_OUTPUT_SNIPPETS
        ):
            _add(
                findings,
                "mworks_live_gate.expected_engineering_outputs",
                "expected_outputs_not_engineering_evidence",
                "For MWORKS model/simulation/layout work, expected_engineering_outputs must name concrete .mo, check_model, simulation, result, diagram, screenshot, metrics, or layout evidence. JSON packets alone are not engineering progress.",
            )
        if _contains_any_snippet(expected_outputs, JSON_ONLY_SNIPPETS) and not _is_diagnostic_engineering_mode(
            output_mode
        ) and not _contains_any_snippet(expected_outputs, ENGINEERING_OUTPUT_SNIPPETS):
            _add(
                findings,
                "mworks_live_gate.expected_engineering_outputs",
                "json_only_expected_outputs",
                "A MWORKS department task cannot define completion as only JSON packets, ledger entries, or status docs unless it is explicitly diagnostic_only/rule_sync_only/preflight_drill_only/static_inventory_only.",
            )

    return {"ok": not findings, "fail_count": len(findings), "findings": findings}


def _check_return(packet: dict[str, Any], *, expect: str) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    live_touched = packet.get("live_mworks_touched")
    evidence_touched = _is_true(packet.get("mworks_window_evidence_touched"))
    has_sentinel = "activation_sentinel_before" in packet or "gui_sentinel_before" in packet
    has_patrol_reference = _has_patrol_reference(packet)
    legacy_sentinel_mode = evidence_touched or has_sentinel or "background_screenshot_before" in packet

    if expect == "department" and not evidence_touched and not has_patrol_reference:
        _add(
            findings,
            "mworks_activation_patrol_reference",
            "department_return_missing_patrol_or_window_evidence",
            "MWORKS department return/blocker packets must reference the latest legacy ops patrol or include current-turn sentinel/window evidence.",
        )

    if expect == "static" and not evidence_touched and not has_sentinel:
        if not _is_false(live_touched):
            _add(
                findings,
                "live_mworks_touched",
                "static_return_missing_false_flag",
                "Static-only MWORKS return/blocker packets must state live_mworks_touched=false.",
            )
        return {"ok": not findings, "fail_count": len(findings), "findings": findings}

    if expect == "auto" and _is_false(live_touched) and not evidence_touched and not has_sentinel:
        return {"ok": True, "fail_count": 0, "findings": findings}

    if _is_false(live_touched) and legacy_sentinel_mode:
        if not evidence_touched:
            _add(
                findings,
                "mworks_window_evidence_touched",
                "missing_window_evidence_flag",
                "MWORKS activation/screenshot evidence packets must set mworks_window_evidence_touched=true when live_mworks_touched=false.",
            )

    for field in sorted(REQUIRED_RETURN_FIELDS):
        if field not in packet:
            _add(findings, field, "missing_required_mworks_return_field", field)

    if expect == "department" and has_patrol_reference:
        if "mworks_activation_patrol_age_minutes" in packet:
            age = packet.get("mworks_activation_patrol_age_minutes")
            try:
                if float(age) < 0:
                    _add(
                        findings,
                        "mworks_activation_patrol_age_minutes",
                        "invalid_patrol_age",
                        "mworks_activation_patrol_age_minutes must be non-negative when provided.",
                    )
            except (TypeError, ValueError):
                _add(
                    findings,
                    "mworks_activation_patrol_age_minutes",
                    "invalid_patrol_age",
                    "mworks_activation_patrol_age_minutes must be numeric when provided.",
                )

    if packet.get("will_not_click_activation_login") is not True:
        _add(
            findings,
            "will_not_click_activation_login",
            "no_click_pledge_not_true",
            "will_not_click_activation_login must be true.",
        )

    if legacy_sentinel_mode and "gui_sentinel_before" not in packet and "activation_sentinel_before" not in packet:
        _add(
            findings,
            "gui_sentinel_before",
            "missing_sentinel_reference",
            "Return/blocker must include gui_sentinel_before or activation_sentinel_before.",
        )
    for field in ["activation_sentinel_before", "gui_sentinel_before"]:
        if field in packet and not _has_content(packet.get(field)):
            _add(
                findings,
                field,
                "empty_sentinel_reference",
                f"{field} must contain the actual sentinel status/path/result or an explicit unavailable blocker, not an empty placeholder.",
            )

    screenshot = packet.get("background_screenshot_before")
    if legacy_sentinel_mode and not _has_content(screenshot):
        _add(
            findings,
            "background_screenshot_before",
            "missing_background_screenshot",
            "MWORKS department work must include a background screenshot reference/result or an explicit unavailable blocker.",
        )

    live_touched_bool = _is_true(live_touched)

    if live_touched_bool:
        if legacy_sentinel_mode and not has_patrol_reference:
            for field in sorted(REQUIRED_LIVE_ACTIVATION_RETURN_FIELDS):
                if not _has_content(packet.get(field)):
                    _add(
                        findings,
                        field,
                        "missing_live_activation_api_evidence",
                        "Live MWORKS work using current-turn activation evidence must include stronger license_api_before or task-local license-sufficiency evidence.",
                    )
        phase_screenshots = packet.get("mworks_phase_screenshots")
        phase_observations = packet.get("mworks_phase_observations")
        if not _has_content(phase_screenshots):
            _add(
                findings,
                "mworks_phase_screenshots",
                "missing_live_phase_screenshots",
                "Live MWORKS work must include during-work background screenshot evidence, not only the preflight screenshot.",
            )
        if not _has_content(phase_observations):
            _add(
                findings,
                "mworks_phase_observations",
                "missing_live_phase_observations",
                "Live MWORKS work must state what the phase screenshots showed after load/check/simulation/plot/animation/layout phases as applicable.",
            )
        elif not _contains_any_snippet(phase_observations, PHASE_OBSERVATION_SNIPPETS):
            _add(
                findings,
                "mworks_phase_observations",
                "live_phase_observations_missing_evidence_source",
                "mworks_phase_observations must reference the screenshot/capture/window evidence and the phase reviewed, such as check, simulation, plot, animation, layout, wire, or connection review.",
            )

    license_state = packet.get("license_state")
    if legacy_sentinel_mode or "license_state" in packet:
        if not isinstance(license_state, str) or not license_state.strip():
            _add(findings, "license_state", "missing_license_state", "license_state must be a non-empty string when current-turn window evidence is reported.")
        elif not any(snippet.casefold() in license_state.casefold() for snippet in LICENSE_STATE_SNIPPETS):
            _add(
                findings,
                "license_state",
                "unclassified_license_state",
                "license_state must classify the observed state, for example education_window_observed_activation_unverified, license_api_recorded_education_version_only, mixed_education_and_demo_blocked, demo_blocked, login_required, authorization_failed, gui_error_report_blocked, sentinel_unavailable_blocked, or unknown_blocked.",
            )
        elif any(snippet.casefold() in license_state.casefold() for snippet in BLOCKING_LICENSE_STATE_SNIPPETS):
            status_text = str(packet.get("status", "")).casefold()
            if "block" not in status_text:
                _add(
                    findings,
                    "status",
                    "blocking_license_state_not_returned_as_blocker",
                    "A demo/login/activation/authorization/mixed/visible-unknown/unavailable license_state must be returned as a blocker, not as a completed MWORKS task. Hidden helper-window risk counts alone should not be encoded as unknown_blocked.",
                )
        elif live_touched_bool and any(
            snippet.casefold() in license_state.casefold() for snippet in UNVERIFIED_LICENSE_STATE_SNIPPETS
        ):
            status_text = str(packet.get("status", "")).casefold()
            if "block" not in status_text:
                _add(
                    findings,
                    "status",
                    "unverified_activation_state_not_returned_as_blocker",
                    "For live MWORKS work, education-window-only evidence is activation_unverified and cannot be completed unless stronger task-local license-sufficiency evidence is also recorded.",
                )

    observation = packet.get("activation_state_observation")
    if not legacy_sentinel_mode and "activation_state_observation" not in packet:
        has_observation = True
    elif isinstance(observation, str):
        stripped_observation = observation.strip()
        has_observation = bool(stripped_observation)
        if has_observation and len(stripped_observation) < 24:
            _add(
                findings,
                "activation_state_observation",
                "vague_activation_state_observation",
                "activation_state_observation must describe what the sentinel, window title, or screenshot actually showed; a short ACK/status word is not enough.",
            )
    elif isinstance(observation, dict):
        has_observation = bool(observation)
    elif isinstance(observation, list):
        has_observation = bool(observation)
    else:
        has_observation = False
    if legacy_sentinel_mode and not has_observation:
        _add(
            findings,
            "activation_state_observation",
            "missing_activation_state_observation",
            "Return/blocker must state what the sentinel, window title, or screenshot actually showed about activation state.",
        )
    elif legacy_sentinel_mode and not _contains_any_snippet(observation, OBSERVATION_SOURCE_SNIPPETS):
        _add(
            findings,
            "activation_state_observation",
            "activation_state_observation_missing_evidence_source",
            "activation_state_observation must explicitly reference the sentinel, window title, screenshot, capture manifest, or equivalent observed evidence; a generic status sentence is not enough.",
        )

    if expect == "department":
        status_text = str(packet.get("status", "")).casefold()
        output_mode = _engineering_output_mode(packet)
        outputs = _engineering_outputs(packet)
        if "complete" in status_text or "done" in status_text:
            if _is_diagnostic_engineering_mode(output_mode):
                pass
            elif not _has_content(outputs):
                _add(
                    findings,
                    "engineering_outputs",
                    "missing_engineering_outputs",
                    "Completed MWORKS department returns must include actual_engineering_outputs/engineering_outputs or equivalent evidence beyond the JSON packet.",
                )
            elif not _contains_any_snippet(outputs, ENGINEERING_OUTPUT_SNIPPETS):
                _add(
                    findings,
                    "engineering_outputs",
                    "json_only_mworks_return",
                    "A completed MWORKS department return that only points to JSON packets, ledger entries, or status docs is control-plane metadata, not model/simulation/layout progress.",
                )

    return {"ok": not findings, "fail_count": len(findings), "findings": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="Path to a JSON task, return, or blocker packet.")
    parser.add_argument("--kind", choices=["task", "return"], required=True)
    parser.add_argument(
        "--expect",
        choices=["live", "static", "auto", "department"],
        default="auto",
        help="Use department for PMO->MWORKS department dispatches, live for live GUI/MCP packets, static only for non-department file-only work.",
    )
    args = parser.parse_args(argv)

    packet = _load_json(args.packet)
    if args.kind == "task":
        result = _check_task(packet, expect=args.expect)
    else:
        result = _check_return(packet, expect=args.expect)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
