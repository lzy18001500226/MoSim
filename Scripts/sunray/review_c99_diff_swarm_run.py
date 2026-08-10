#!/usr/bin/env python3
"""Create a bounded audit packet for a staged C99/Diff-Swarm run."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, f"missing: {path.name}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, f"unreadable {path.name}: {error}"
    if not isinstance(data, dict):
        return None, f"invalid object: {path.name}"
    return data, None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_contract_float(path: Path, key: str) -> tuple[float | None, str | None]:
    if not path.is_file():
        return None, f"missing: {path.name}"
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.partition("=")
            if separator and name == key:
                parsed = float(value)
                if math.isfinite(parsed):
                    return parsed, None
                return None, f"non-finite {key}: {value!r}"
    except (OSError, ValueError) as error:
        return None, f"unreadable {path.name}: {error}"
    return None, f"missing {key} in {path.name}"


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "status": "passed" if passed else "failed", "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-dir", required=True, type=Path)
    parser.add_argument("--audit-exit-code", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result_dir = args.result_dir.resolve()
    output = args.output or result_dir / "C99_DIFF_SWARM_STAGE_REVIEW.json"
    components_path = result_dir / "C99_DIFF_SWARM_COMPONENTS_READY.json"
    metrics_path = result_dir / "EGO_SWARM_METRICS.json"
    audit_path = result_dir / "planner_runtime_log_audit.json"
    prepare_path = result_dir / "C99_DIFF_PREPARE_STATUS.json"
    target_contract_path = result_dir / "c99_diff_target_coordinate_contract.json"
    component_contract_path = result_dir / "c99_diff_swarm_component_contract.env"

    checks: list[dict[str, Any]] = []
    prepare, prepare_error = read_json(prepare_path)
    add_check(
        checks,
        "prepare",
        prepare is not None and prepare.get("status") == "passed",
        prepare_error or f"status={prepare.get('status')!r}",
    )
    components, components_error = read_json(components_path)
    components_passed = components is not None and components.get("status") == "passed"
    add_check(
        checks,
        "components",
        components_passed,
        components_error or f"status={components.get('status')!r}",
    )
    target_contract, target_contract_error = read_json(target_contract_path)
    add_check(
        checks,
        "coordinate_contract",
        target_contract is not None,
        target_contract_error or "present",
    )

    metrics, metrics_error = read_json(metrics_path)
    metrics_passed = metrics is not None and metrics.get("status") == "passed"
    add_check(
        checks,
        "mission_metrics",
        metrics_passed,
        metrics_error or f"status={metrics.get('status')!r}",
    )

    expected_uav_num = int(components.get("uav_num", 0)) if components else 0
    per_uav = metrics.get("per_uav", {}) if metrics else {}
    target_holds_ok = metrics_passed and isinstance(per_uav, dict) and len(per_uav) == expected_uav_num
    if target_holds_ok:
        target_holds_ok = all(
            isinstance(vehicle, dict)
            and isinstance(vehicle.get("target_hold"), dict)
            and vehicle["target_hold"].get("reached") is True
            for vehicle in per_uav.values()
        )
    add_check(
        checks,
        "per_uav_target_hold",
        target_holds_ok,
        f"expected_uav_num={expected_uav_num}, observed_uav_num={len(per_uav) if isinstance(per_uav, dict) else 0}",
    )

    required_separation_m, separation_contract_error = read_contract_float(
        component_contract_path, "EGO_GATE_MIN_INTER_UAV_DISTANCE"
    )
    observed_separation_m = metrics.get("min_inter_uav_distance_m") if metrics else None
    emergency_hold = metrics.get("inter_uav_emergency_hold") if metrics else None
    emergency_events = emergency_hold.get("events") if isinstance(emergency_hold, dict) else None
    separation_ok = (
        metrics_passed
        and isinstance(observed_separation_m, (int, float))
        and math.isfinite(observed_separation_m)
        and required_separation_m is not None
        and observed_separation_m >= required_separation_m
        and isinstance(emergency_events, list)
        and not emergency_events
    )
    separation_detail = separation_contract_error or (
        f"observed_m={observed_separation_m!r}, required_m={required_separation_m!r}, "
        f"emergency_events={len(emergency_events) if isinstance(emergency_events, list) else None}"
    )
    add_check(checks, "inter_uav_separation", separation_ok, separation_detail)

    landing = metrics.get("landing", {}) if metrics else {}
    landing_ok = metrics_passed and isinstance(landing, dict) and landing.get("completed") is True
    add_check(
        checks,
        "landing",
        landing_ok,
        f"completed={landing.get('completed') if isinstance(landing, dict) else None!r}",
    )

    audit, audit_error = read_json(audit_path)
    audit_ok = args.audit_exit_code == 0 and audit is not None and audit.get("status") == "passed"
    add_check(
        checks,
        "planner_runtime_log_audit",
        audit_ok,
        audit_error or f"exit_code={args.audit_exit_code}, status={audit.get('status')!r}",
    )

    artifacts: dict[str, dict[str, str]] = {}
    for path in (
        prepare_path,
        components_path,
        component_contract_path,
        target_contract_path,
        metrics_path,
        audit_path,
    ):
        if path.is_file():
            artifacts[path.name] = {"sha256": sha256(path), "path": str(path)}

    passed = all(check["status"] == "passed" for check in checks)
    packet = {
        "schema": "mosim.sunray_ros1.c99_diff_swarm_stage_review.v1",
        "status": "passed" if passed else "failed",
        "result_dir": str(result_dir),
        "checks": checks,
        "artifacts": artifacts,
        "claim_boundary": "This packet proves the staged C99/Diff-Swarm fixed-target runtime only when every recorded check passes. It does not prove RViz review, autonomous exploration, generalized swarm safety, UE integration, or MWORKS formal acceptance.",
    }
    output.write_text(json.dumps(packet, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
