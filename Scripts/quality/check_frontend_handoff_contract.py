#!/usr/bin/env python3
"""Check that the pre-frontend handoff points to valid control authorities."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "Config" / "control_platform" / "frontend_handoff_contract.json"


def validate() -> list[str]:
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    errors: list[str] = []
    if handoff.get("schema") != "mosim.control_platform.frontend_handoff.v1":
        errors.append("invalid_schema")
    for name, value in handoff.get("authorities", {}).items():
        path = ROOT / value
        if not path.is_file():
            errors.append(f"missing_authority:{name}:{value}")
            continue
        json.loads(path.read_text(encoding="utf-8"))
    required_commands = {"validate_experiment_profile", "start_run", "stop_run", "apply_injection", "restore_injection"}
    if not required_commands.issubset(handoff.get("commands", [])):
        errors.append("missing_commands")
    required_states = {"idle", "ready", "running", "completed", "blocked", "failed"}
    if not required_states.issubset(handoff.get("lifecycle_states", [])):
        errors.append("missing_lifecycle_states")
    if "injection_state" not in handoff.get("telemetry_channels", []):
        errors.append("missing_injection_telemetry")
    return errors


def main() -> int:
    errors = validate()
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
