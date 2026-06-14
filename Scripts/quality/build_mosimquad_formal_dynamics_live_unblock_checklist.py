#!/usr/bin/env python3
"""Build the operator checklist for unblocking formal Dynamics live smoke.

This script is static/read-only. It does not call MWORKS, Sysplorer, MCP,
check_model, SimulateModel, or any GUI/window action.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_BLOCKER = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_live_preflight"
    / "live_preflight_blocker_summary.json"
)
SMOKE_READINESS = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_live_smoke_readiness"
    / "live_smoke_readiness.json"
)
RESULT_ACCEPTANCE = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_smoke_result_acceptance"
    / "result_acceptance.json"
)
OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_live_unblock_checklist"
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def add_finding(findings: list[dict[str, Any]], code: str, message: str, target: str) -> None:
    findings.append({"code": code, "message": message, "target": target})


def classify_unblock_state(preflight: dict[str, Any]) -> tuple[str, str]:
    classifier = preflight.get("current_upgrade_classifier", {})
    if not isinstance(classifier, dict):
        return "unknown", "current_upgrade_classifier is not a mapping"
    if classifier.get("license_state_hint") == "upgrade_model_surface_blocked":
        return "blocked_needs_user_or_pmo_ui_decision", "current MWORKS surface still reports upgrade_model_surface_blocked"
    if classifier.get("error_kind") in {None, "", "none"} and classifier.get("status") in {"clean", "ok"}:
        return "preflight_surface_clean", "current classifier is clean"
    return "unknown", "current classifier is neither clean nor the known upgrade-model blocker"


def build_checklist(preflight_path: Path, readiness_path: Path, acceptance_path: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    preflight = read_json(preflight_path)
    readiness = read_json(readiness_path)
    acceptance = read_json(acceptance_path)

    unblock_state, unblock_reason = classify_unblock_state(preflight)

    if preflight.get("status") != "blocked_by_upgrade_model_surface":
        add_finding(
            findings,
            "preflight_status_drift",
            "live preflight summary no longer records the expected upgrade-model blocker",
            rel(preflight_path),
        )

    if readiness.get("status") != "ready_but_blocked_by_gui":
        add_finding(
            findings,
            "readiness_status_drift",
            "live smoke readiness must remain ready_but_blocked_by_gui until a fresh clean preflight is recorded",
            rel(readiness_path),
        )

    if acceptance.get("status") not in {"pending_live_results", "partial_results_pending", "passed"}:
        add_finding(
            findings,
            "acceptance_status_invalid",
            "result acceptance checker is not in an allowed pre/post-live state",
            rel(acceptance_path),
        )

    if int(readiness.get("scenario_count") or 0) != 7:
        add_finding(findings, "wrong_scenario_count", "formal Dynamics smoke readiness must include seven scenarios", rel(readiness_path))

    future_command = readiness.get("future_live_batch_command", [])
    if not isinstance(future_command, list) or not future_command:
        add_finding(findings, "missing_future_live_command", "readiness output does not contain a future live batch command", rel(readiness_path))

    status = "blocked_needs_user_or_pmo_ui_decision"
    if findings:
        status = "failed_static_contract"
    elif unblock_state == "preflight_surface_clean":
        status = "ready_for_bounded_live_smoke_preflight"

    return {
        "schema": "mosim.mworks.formal_dynamics_live_unblock_checklist.v1",
        "status": status,
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_action_touched": False,
        "preflight_blocker": rel(preflight_path),
        "smoke_readiness": rel(readiness_path),
        "result_acceptance": rel(acceptance_path),
        "unblock_state": unblock_state,
        "unblock_reason": unblock_reason,
        "required_user_or_pmo_decision": unblock_state != "preflight_surface_clean",
        "allowed_next_action_when_clean": {
            "action": "bounded_formal_dynamics_live_smoke_preflight",
            "command": future_command,
            "must_run_before_command": [
                "fresh MWORKS/Sysplorer/Syslab sentinel or foreground/maximized evidence reports clean, non-login, non-license, non-upgrade, non-error state",
                "no unknown blocking MWORKS windows are visible",
                "no GUI click, close, restart, save, authorization, or upgrade confirmation is performed by an engineering task",
            ],
            "stop_before_command_on": [
                "升级模型 or any model-upgrade/progress modal remains visible",
                "login, activation, authorization, license, demo, mixed-license, GUI error-report, crash, save, restart, or unknown window",
                "classifier output is missing, stale, or not explicitly clean",
            ],
        },
        "operator_checklist": [
            "If the upgrade-model surface is still present, stop live smoke and ask PMO/user for a UI decision.",
            "After the surface is cleared by an authorized owner, collect a fresh sentinel or foreground/maximized target-main-window evidence.",
            "Run the static readiness guard again before any live smoke command.",
            "Run the future live command only with no GUI result viewer and no GUI open flags.",
            "After live output exists, run the result-acceptance checker before using any result in a report or controller claim.",
        ],
        "claim_boundary": [
            "This checklist is an executable gate for future live work only.",
            "It does not prove live load, check_model, SimulateModel, result variables, controller performance, mission success, or closed_loop.",
            "It does not authorize automatic GUI clicking, closing, restart, login, save, or model-upgrade confirmation.",
        ],
        "findings": findings,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, checklist: dict[str, Any]) -> None:
    lines = [
        "# Formal Dynamics Live Unblock Checklist",
        "",
        f"Status: `{checklist['status']}`",
        f"Unblock state: `{checklist['unblock_state']}`",
        f"Reason: {checklist['unblock_reason']}",
        "",
        "This is a static/read-only checklist. It does not call MWORKS, Sysplorer, MCP, `check_model`, `SimulateModel`, or any GUI/window action.",
        "",
        "## Operator Checklist",
        "",
    ]
    lines.extend(f"- {item}" for item in checklist["operator_checklist"])
    lines.extend(["", "## Stop Conditions", ""])
    lines.extend(f"- {item}" for item in checklist["allowed_next_action_when_clean"]["stop_before_command_on"])
    lines.extend(["", "## Allowed Command After Fresh Clean Evidence", "", "```powershell"])
    lines.append(" ".join(str(item) for item in checklist["allowed_next_action_when_clean"]["command"]))
    lines.extend(["```", "", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in checklist["claim_boundary"])
    lines.extend(["", "## Findings", ""])
    if checklist["findings"]:
        lines.extend(f"- `{item['code']}` at `{item['target']}`: {item['message']}" for item in checklist["findings"])
    else:
        lines.append("- none")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-blocker", type=Path, default=PREFLIGHT_BLOCKER)
    parser.add_argument("--smoke-readiness", type=Path, default=SMOKE_READINESS)
    parser.add_argument("--result-acceptance", type=Path, default=RESULT_ACCEPTANCE)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    preflight = args.preflight_blocker if args.preflight_blocker.is_absolute() else ROOT / args.preflight_blocker
    readiness = args.smoke_readiness if args.smoke_readiness.is_absolute() else ROOT / args.smoke_readiness
    acceptance = args.result_acceptance if args.result_acceptance.is_absolute() else ROOT / args.result_acceptance
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    checklist = build_checklist(preflight, readiness, acceptance)
    write_json(output_dir / "live_unblock_checklist.json", checklist)
    write_markdown(output_dir / "live_unblock_checklist.md", checklist)
    print(json.dumps(checklist, ensure_ascii=False, indent=2))
    return 0 if checklist["status"] in {"blocked_needs_user_or_pmo_ui_decision", "ready_for_bounded_live_smoke_preflight"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
