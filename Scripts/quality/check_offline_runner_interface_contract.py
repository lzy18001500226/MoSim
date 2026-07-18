#!/usr/bin/env python3
"""Validate the static four-boundary offline Runner interface contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "Config/control_platform/offline_runner_interface_contract_v1.json"
EXPECTED_BOUNDARIES = {"ATTITUDE_THRUST", "BODY_RATE_THRUST", "WRENCH", "ROTOR_COMMAND"}
REQUIRED_RESULT_NAMES = {"position_ref", "position", "attitude", "rotor_command", "position_error_norm"}
REQUIRED_LIFECYCLE = {"dt", "reset", "enable", "run_id", "profile_hash", "parameter_version", "random_seed"}


def validate(contract: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != "mosim.offline_runner_interface_contract.v1":
        errors.append("invalid_schema")
    boundaries = contract.get("boundaries", {})
    if set(boundaries) != EXPECTED_BOUNDARIES:
        errors.append("four_explicit_boundaries_required")
    for boundary, declaration in boundaries.items():
        for key in ("interface_source", "runner_source"):
            value = declaration.get(key)
            path = root / value if isinstance(value, str) else None
            if path is None or not path.is_file():
                errors.append(f"missing_{key}:{boundary}")
        outputs = declaration.get("outputs")
        if not isinstance(outputs, list) or not outputs:
            errors.append(f"outputs_required:{boundary}")
            continue
        for output in outputs:
            semantics = output.get("unit_semantics", "")
            if not semantics or (
                output["name"] in {"collective_thrust_delta", "body_force", "body_torque", "rotor_command"}
                and not any(marker in semantics for marker in ("legacy", "not_verified"))
            ):
                errors.append(f"unverified_physical_unit_overclaim:{boundary}:{output.get('name')}")
        interface_text = (root / declaration["interface_source"]).read_text(encoding="utf-8")
        runner_text = (root / declaration["runner_source"]).read_text(encoding="utf-8")
        for output in outputs:
            if output["name"] not in interface_text:
                errors.append(f"interface_output_missing:{boundary}:{output['name']}")
        for name in REQUIRED_RESULT_NAMES:
            if name not in runner_text:
                errors.append(f"runner_result_missing:{boundary}:{name}")

    result_names = {item.get("name") for item in contract.get("runner_result_surface", [])}
    if result_names != REQUIRED_RESULT_NAMES:
        errors.append("runner_result_surface_mismatch")
    lifecycle = contract.get("lifecycle_contract", {})
    if set(lifecycle.get("required_future_fields", [])) != REQUIRED_LIFECYCLE:
        errors.append("lifecycle_fields_mismatch")
    if lifecycle.get("current_model_ports_implemented") is not False:
        errors.append("lifecycle_ports_must_remain_blocked_until_model_evidence")
    gaps = set(contract.get("known_gaps", []))
    for required_gap in (
        "coordinate_frame_contract_not_bound_to_model_ports",
        "physical_command_units_not_verified",
        "lifecycle_context_not_bound_to_model_ports",
    ):
        if required_gap not in gaps:
            errors.append(f"required_gap_missing:{required_gap}")
    return errors


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    errors = validate(contract)
    result = {"ok": not errors, "errors": errors, "boundary_count": len(contract.get("boundaries", {}))}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
