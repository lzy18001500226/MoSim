#!/usr/bin/env python3
"""Validate the formal Dynamics live-preflight blocker and next-load strategy.

This checker is static/read-only. It does not call MWORKS, Sysplorer, MCP,
check_model, SimulateModel, or window tools.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_mosimquad_formal_dynamics_live_preflight"
)
SCENARIO_DIR = ROOT / "Config" / "scenarios" / "diagnostics"
OUTPUT_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260722_mosimquad_model_root_consolidation"
    / "live_preflight_blocker"
)

SCENARIOS = [
    "mosimquad_dynamics_hover_smoke.yaml",
    "mosimquad_dynamics_physical_wrench_hover_smoke.yaml",
    "mosimquad_dynamics_physical_wrench_yaw_step_smoke.yaml",
    "mosimquad_dynamics_rotor_effectiveness_smoke.yaml",
    "mosimquad_dynamics_wrapper_hover_smoke.yaml",
    "mosimquad_dynamics_wrapper_yaw_step_smoke.yaml",
    "mosimquad_dynamics_yaw_step_smoke.yaml",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML is required for this checker")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def latest(paths: list[Path]) -> Path | None:
    existing = [path for path in paths if path.exists()]
    if not existing:
        return None
    return max(existing, key=lambda path: path.stat().st_mtime)


def newest_glob(pattern: str, *, exclude_prefixes: tuple[str, ...] = ()) -> Path | None:
    paths = [
        path
        for path in PREFLIGHT_DIR.glob(pattern)
        if not any(path.name.startswith(prefix) for prefix in exclude_prefixes)
    ]
    return latest(paths)


def add_finding(findings: list[dict[str, Any]], code: str, message: str, *, target: str | None = None) -> None:
    item: dict[str, Any] = {"code": code, "message": message}
    if target:
        item["target"] = target
    findings.append(item)


def build_summary() -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    initial_sentinel = newest_glob("sentinel_*.json", exclude_prefixes=("sentinel_after_",))
    timeout_sentinel = newest_glob("sentinel_after_load_timeout_*.json")
    current_classifier_sentinel = newest_glob("current_gui_sentinel_after_upgrade_classifier_*.json")
    main_capture_manifest = newest_glob("window_capture_*/capture_manifest.json")
    upgrade_capture_manifest = newest_glob("upgrade_window_capture_*/capture_manifest.json")

    initial_data = json.loads(initial_sentinel.read_text(encoding="utf-8")) if initial_sentinel else {}
    timeout_data = json.loads(timeout_sentinel.read_text(encoding="utf-8")) if timeout_sentinel else {}
    current_classifier_data = (
        json.loads(current_classifier_sentinel.read_text(encoding="utf-8")) if current_classifier_sentinel else {}
    )

    if not initial_sentinel:
        add_finding(findings, "missing_initial_sentinel", "initial live preflight sentinel is missing")
    elif initial_data.get("status") != "clean":
        add_finding(findings, "initial_sentinel_not_clean", "initial sentinel was not clean")

    if not timeout_sentinel:
        add_finding(findings, "missing_timeout_sentinel", "post-load-timeout sentinel is missing")
    else:
        if timeout_data.get("error_kind") not in {"license_or_login", "gui_blocked"}:
            add_finding(findings, "unexpected_timeout_error_kind", "timeout sentinel did not preserve the blocking classification")
        unknown_titles = [item.get("title") for item in timeout_data.get("visible_unknown_mworks_windows", [])]
        if "升级模型" not in unknown_titles:
            add_finding(findings, "missing_upgrade_model_window", "post-timeout sentinel did not record the upgrade-model window")

    if not current_classifier_sentinel:
        add_finding(
            findings,
            "missing_current_upgrade_classifier_sentinel",
            "current upgrade-model classifier sentinel is missing",
        )
    else:
        if current_classifier_data.get("status") != "incident_detected":
            add_finding(
                findings,
                "current_classifier_not_blocking",
                "current upgrade-model classifier sentinel did not block live retry",
            )
        if current_classifier_data.get("error_kind") != "gui_blocked":
            add_finding(
                findings,
                "current_classifier_wrong_error_kind",
                "current upgrade-model classifier sentinel did not use gui_blocked",
            )
        if current_classifier_data.get("license_state_hint") != "upgrade_model_surface_blocked":
            add_finding(
                findings,
                "current_classifier_wrong_license_hint",
                "current upgrade-model classifier sentinel did not use upgrade_model_surface_blocked",
            )
        if int(current_classifier_data.get("upgrade_model_window_count") or 0) < 1:
            add_finding(
                findings,
                "current_classifier_missing_upgrade_window",
                "current upgrade-model classifier sentinel did not count the upgrade-model window",
            )

    if not main_capture_manifest:
        add_finding(findings, "missing_main_capture_manifest", "main Sysplorer screenshot manifest is missing")
    if not upgrade_capture_manifest:
        add_finding(findings, "missing_upgrade_capture_manifest", "upgrade-model screenshot manifest is missing")

    scenario_summaries: list[dict[str, Any]] = []
    for name in SCENARIOS:
        path = SCENARIO_DIR / name
        if not path.exists():
            add_finding(findings, "missing_scenario", "diagnostic scenario file is missing", target=rel(path))
            continue
        config = read_yaml(path)
        model = config.get("model", {})
        if not isinstance(model, dict):
            add_finding(findings, "model_field_not_mapping", "scenario model field is not a mapping", target=rel(path))
            continue
        strategy = model.get("live_load_strategy")
        base_model = model.get("base_model_path_hint")
        if strategy != "minimal_dynamics_only":
            add_finding(
                findings,
                "missing_minimal_dynamics_strategy",
                "formal Dynamics smoke scenarios must explicitly request the minimal Dynamics load strategy",
                target=rel(path),
            )
        if base_model != "Models/MoSimQuadrotorModel/package.mo":
            add_finding(
                findings,
                "unexpected_base_model_path",
                "scenario base model path drifted from the official baseline package",
                target=rel(path),
            )
        scenario_summaries.append(
            {
                "scenario": rel(path),
                "model_name": model.get("model_name"),
                "live_load_strategy": strategy,
                "base_model_path_hint": base_model,
            }
        )

    status = "blocked_by_upgrade_model_surface" if not findings else "failed_static"
    return {
        "schema": "mosim.mworks.formal_dynamics_live_preflight_blocker.v1",
        "status": status,
        "static_only": True,
        "live_mworks_touched_in_source_attempt": True,
        "mworks_window_evidence_touched_in_source_attempt": True,
        "current_live_gate_result": "blocked",
        "blocking_surface": "upgrade_model_modal_or_progress_window",
        "blocked_operation": "model_manager.load_file Models/MoSimQuadrotorModel/package.mo",
        "blocker_reason": (
            "Top-level MoSimQuadrotorModel load entered a broad package/dependency load and exposed an "
            "unknown MWORKS '升级模型' window; MCP session probe then timed out. No click/confirm/close/restart was performed."
        ),
        "initial_sentinel": rel(initial_sentinel) if initial_sentinel else None,
        "post_timeout_sentinel": rel(timeout_sentinel) if timeout_sentinel else None,
        "current_upgrade_classifier_sentinel": rel(current_classifier_sentinel) if current_classifier_sentinel else None,
        "current_upgrade_classifier": {
            "status": current_classifier_data.get("status"),
            "error_kind": current_classifier_data.get("error_kind"),
            "license_state_hint": current_classifier_data.get("license_state_hint"),
            "upgrade_model_window_count": current_classifier_data.get("upgrade_model_window_count"),
            "all_window_license_gate": current_classifier_data.get("all_window_license_gate"),
        },
        "main_window_capture_manifest": rel(main_capture_manifest) if main_capture_manifest else None,
        "upgrade_window_capture_manifest": rel(upgrade_capture_manifest) if upgrade_capture_manifest else None,
        "next_load_strategy": {
            "name": "minimal_dynamics_only",
            "purpose": "avoid re-entering full MoSimQuadrotorModel controller/System/Planning package load before Dynamics smoke gates",
            "scenario_field": "model.live_load_strategy",
            "required_before_next_live_attempt": True,
        },
        "scenario_count": len(scenario_summaries),
        "scenarios": scenario_summaries,
        "claim_boundary": [
            "This records a live-preflight blocker and a future load strategy only.",
            "It does not claim check_model, SimulateModel, result variables, controller performance, mission success, or closed_loop.",
            "Do not click the upgrade-model window automatically; require a narrower load strategy or explicit user/PMO UI decision.",
        ],
        "findings": findings,
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Formal Dynamics Live Preflight Blocker",
        "",
        f"Status: `{summary['status']}`",
        "",
        "The first live attempt reached Sysplorer but did not reach `check_model`.",
        "",
        "## Blocker",
        "",
        f"- blocked operation: `{summary['blocked_operation']}`",
        f"- surface: `{summary['blocking_surface']}`",
        f"- reason: {summary['blocker_reason']}",
        "",
        "## Evidence",
        "",
        f"- initial sentinel: `{summary['initial_sentinel']}`",
        f"- post-timeout sentinel: `{summary['post_timeout_sentinel']}`",
        f"- current upgrade classifier sentinel: `{summary['current_upgrade_classifier_sentinel']}`",
        f"- current classifier: `{summary['current_upgrade_classifier']}`",
        f"- main-window capture manifest: `{summary['main_window_capture_manifest']}`",
        f"- upgrade-window capture manifest: `{summary['upgrade_window_capture_manifest']}`",
        "",
        "## Next Strategy",
        "",
        "- Use `model.live_load_strategy: minimal_dynamics_only` for formal Dynamics diagnostic smoke scenarios.",
        "- Do not auto-click or close the upgrade-model window.",
        "- Do not claim runtime success until a future live task reaches `check_model`, `SimulateModel`, and result-variable probes.",
        "",
        "## Scenarios",
        "",
    ]
    for item in summary["scenarios"]:
        lines.append(f"- `{item['scenario']}` -> `{item['model_name']}` strategy=`{item['live_load_strategy']}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    summary = build_summary()
    write_json(output_dir / "live_preflight_blocker_summary.json", summary)
    write_markdown(output_dir / "live_preflight_blocker_summary.md", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "blocked_by_upgrade_model_surface" else 1


if __name__ == "__main__":
    raise SystemExit(main())
