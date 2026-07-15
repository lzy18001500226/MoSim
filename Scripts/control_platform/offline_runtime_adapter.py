#!/usr/bin/env python3
"""Offline lifecycle adapter for the pre-frontend control-platform contract.

This adapter validates profiles and reduces lifecycle/injection commands without
starting MWORKS, ROS, Gazebo, PX4, or MAVROS. It is an interface gate, not a
runtime acceptance harness.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.control_platform.factory_injection_replay import (
    InjectionState,
    apply_command,
    load_contract,
)
from Scripts.quality.check_experiment_profile import (
    DEFAULT_CATALOG,
    DEFAULT_CONTROL_MODULE_REGISTRY,
    DEFAULT_RUNTIME_LOG_EXPORTS,
    DEFAULT_TRACKING_SOURCES,
    canonical_hash,
    load_json,
    validate_experiment,
)


def now() -> float:
    return time.time()


@dataclass
class OfflineControlPlatform:
    """Small deterministic state machine matching the frontend handoff."""

    lifecycle_state: str = "idle"
    run_id: str = ""
    profile_hash: str = ""
    profile_id: str = ""
    profile_path: str = ""
    validation: dict[str, Any] | None = None
    injection_state: InjectionState = field(default_factory=InjectionState)
    events: list[dict[str, Any]] = field(default_factory=list)

    def _response(self, request_id: str, accepted: bool, reason_code: str) -> dict[str, Any]:
        return {
            "schema": "mosim.control_platform.command_response.v1",
            "request_id": request_id,
            "accepted": accepted,
            "reason_code": reason_code,
            "run_id": self.run_id,
            "profile_hash": self.profile_hash,
            "timestamp": now(),
            "lifecycle_state": self.lifecycle_state,
            "runtime_mode": "offline_contract_reducer",
            "runtime_started": False,
        }

    def validate_profile(self, profile_path: str, request_id: str = "") -> dict[str, Any]:
        path = (ROOT / profile_path).resolve() if not Path(profile_path).is_absolute() else Path(profile_path).resolve()
        request_id = request_id or f"req-{uuid.uuid4().hex}"
        try:
            result = validate_experiment(
                path,
                load_json(DEFAULT_CATALOG),
                load_json(DEFAULT_TRACKING_SOURCES),
                load_json(DEFAULT_RUNTIME_LOG_EXPORTS),
                load_json(DEFAULT_CONTROL_MODULE_REGISTRY),
            )
        except (OSError, ValueError) as exc:
            self.lifecycle_state = "blocked"
            self.validation = {"ok": False, "errors": [{"code": "PROFILE-IO-01", "message": str(exc)}]}
            response = self._response(request_id, False, "profile_validation_error")
            response["validation"] = self.validation
            return response
        self.validation = result
        if result.get("ok"):
            self.lifecycle_state = "ready"
            self.profile_id = str(result.get("experiment_id") or "")
            self.profile_hash = str(result.get("experiment_profile_hash") or "")
            self.profile_path = str(path)
            response = self._response(request_id, True, "profile_valid")
        else:
            self.lifecycle_state = "blocked"
            response = self._response(request_id, False, "profile_rejected")
        response["validation"] = result
        return response

    def start(self, request_id: str = "", run_id: str = "", profile_hash: str = "") -> dict[str, Any]:
        request_id = request_id or f"req-{uuid.uuid4().hex}"
        if not self.validation or not self.validation.get("ok"):
            return self._response(request_id, False, "profile_not_validated")
        if self.lifecycle_state == "running":
            return self._response(request_id, False, "run_already_active")
        if profile_hash and profile_hash != self.profile_hash:
            return self._response(request_id, False, "profile_hash_mismatch")
        self.run_id = run_id or f"offline-{uuid.uuid4().hex[:12]}"
        self.lifecycle_state = "running"
        return self._response(request_id, True, "run_started_offline")

    def stop(self, request_id: str = "") -> dict[str, Any]:
        request_id = request_id or f"req-{uuid.uuid4().hex}"
        if self.lifecycle_state != "running":
            return self._response(request_id, False, "run_not_active")
        self.lifecycle_state = "completed"
        return self._response(request_id, True, "run_stopped_offline")

    def apply_injection(self, command: dict[str, Any], restore: bool = False) -> dict[str, Any]:
        request_id = str(command.get("request_id") or command.get("command_id") or f"req-{uuid.uuid4().hex}")
        if self.lifecycle_state != "running":
            return self._response(request_id, False, "run_not_active")
        if command.get("run_id") != self.run_id:
            return self._response(request_id, False, "run_id_mismatch")
        if command.get("profile_hash") != self.profile_hash:
            return self._response(request_id, False, "profile_hash_mismatch")
        payload = dict(command)
        payload["apply_mode"] = "restore" if restore else payload.get("apply_mode", "set")
        events = apply_command(self.injection_state, payload, load_contract())
        self.events.extend(events)
        rejected = any(event["event_state"] == "rejected" for event in events)
        response = self._response(request_id, not rejected, "injection_rejected" if rejected else "injection_applied")
        response["events"] = events
        response["injection_state"] = {
            "wind_speed_mps": self.injection_state.wind_speed_mps,
            "wind_direction_deg": self.injection_state.wind_direction_deg,
            "motor_effectiveness": list(self.injection_state.motor_effectiveness),
        }
        return response

    def snapshot(self, request_id: str = "") -> dict[str, Any]:
        response = self._response(request_id or f"req-{uuid.uuid4().hex}", True, "snapshot_ready")
        response["active_run"] = {
            "run_id": self.run_id,
            "profile_id": self.profile_id,
            "profile_path": self.profile_path,
        }
        response["injection_state"] = {
            "wind_speed_mps": self.injection_state.wind_speed_mps,
            "wind_direction_deg": self.injection_state.wind_direction_deg,
            "motor_effectiveness": list(self.injection_state.motor_effectiveness),
        }
        response["event_count"] = len(self.events)
        response["claim_ceiling"] = (
            "offline lifecycle and injection contract only; no MWORKS, Gazebo, PX4, MAVROS, or controller-performance acceptance"
        )
        return response


def dispatch(platform: OfflineControlPlatform, command: dict[str, Any]) -> dict[str, Any]:
    kind = command.get("command")
    if kind == "validate_experiment_profile":
        return platform.validate_profile(str(command["profile_path"]), str(command.get("request_id") or ""))
    if kind == "start_run":
        return platform.start(str(command.get("request_id") or ""), str(command.get("run_id") or ""), str(command.get("profile_hash") or ""))
    if kind == "stop_run":
        return platform.stop(str(command.get("request_id") or ""))
    if kind == "apply_injection":
        return platform.apply_injection(command)
    if kind == "restore_injection":
        return platform.apply_injection(command, restore=True)
    if kind == "snapshot":
        return platform.snapshot(str(command.get("request_id") or ""))
    return platform._response(str(command.get("request_id") or f"req-{uuid.uuid4().hex}"), False, "unsupported_command")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("commands_jsonl", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    platform = OfflineControlPlatform()
    responses = [dispatch(platform, json.loads(line)) for line in args.commands_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in responses) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    offline_contract_ok = all(item.get("accepted") or item.get("reason_code") == "snapshot_ready" for item in responses)
    summary = {
        "schema": "mosim.control_platform.offline_adapter.v1",
        "status": "offline_contract_passed_runtime_not_accepted" if offline_contract_ok else "failed",
        "actual_end_to_end_runtime_accepted": False,
        "response_count": len(responses),
        "accepted_count": sum(bool(item.get("accepted")) for item in responses),
        "runtime_started": False,
        "shared_gazebo_px4_touched": False,
        "claim_ceiling": "offline lifecycle, profile binding, and injection event semantics only; no MWORKS, Gazebo, PX4, MAVROS, or controller-performance acceptance",
    }
    (args.output.parent / "G7_OFFLINE_ADAPTER_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if offline_contract_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
