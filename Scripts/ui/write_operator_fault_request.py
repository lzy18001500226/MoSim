#!/usr/bin/env python3
"""Write one auditable Factory fault command without starting a runtime.

QGC copies this command to the system clipboard. The operator explicitly runs
it in a visible terminal, after which a running ROS sidecar may consume the
request from ``injection_commands``. This tool never launches ROS, Gazebo,
PX4, QGC, or UE.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.runtime_sidecar_contract import atomic_write_json, load_contract, validate_command


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("fault_request_json_object_required")
    return value


def _command_id() -> str:
    return f"inj-{int(time.time() * 1000)}-{uuid.uuid4().hex[:12]}"


def _base_command(manifest: dict[str, Any], args: argparse.Namespace, *, target: str, value: float, rotor_index: int | None) -> dict[str, Any]:
    return {
        "schema": "mosim.factory_injection_command.v1",
        "command_id": _command_id(),
        "run_id": manifest.get("run_id", ""),
        "profile_hash": manifest.get("experiment_profile_hash", ""),
        "vehicle_id": args.vehicle_id,
        "target": target,
        "requested_at": time.time(),
        "apply_mode": args.apply_mode,
        "value": value,
        "ramp_s": args.ramp_s,
        "duration_s": args.duration_s,
        "restore_policy": args.restore_policy,
        "source": "qgc_visible_terminal",
        **({"rotor_index": rotor_index} if rotor_index is not None else {}),
    }


def build_commands(manifest: dict[str, Any], contract: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.restore_normal:
        candidates = [
            _base_command(manifest, args, target="wind_speed_mps", value=0.0, rotor_index=None),
            *[
                _base_command(manifest, args, target="motor_effectiveness", value=1.0, rotor_index=index)
                for index in range(1, 5)
            ],
        ]
        for command in candidates:
            command["apply_mode"] = "restore"
        return [validate_command(command, manifest=manifest, contract=contract) for command in candidates]

    if not args.target or args.value is None:
        raise ValueError("fault_request_target_and_value_required")
    command = _base_command(
        manifest,
        args,
        target=args.target,
        value=args.value,
        rotor_index=args.rotor_index,
    )
    return [validate_command(command, manifest=manifest, contract=contract)]


def write_commands(run_dir: Path, commands: list[dict[str, Any]]) -> list[Path]:
    output_dir = run_dir / "injection_commands"
    written: list[Path] = []
    for command in commands:
        path = output_dir / f"{command['command_id']}.json"
        atomic_write_json(path, command)
        written.append(path)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--vehicle-id", required=True, choices=tuple(f"uav{index}" for index in range(1, 10)))
    parser.add_argument("--target", choices=("wind_speed_mps", "wind_direction_deg", "motor_effectiveness"))
    parser.add_argument("--value", type=float)
    parser.add_argument("--rotor-index", type=int, choices=range(1, 5))
    parser.add_argument("--apply-mode", choices=("set", "restore"), default="set")
    parser.add_argument("--restore-policy", choices=("manual", "after_duration", "on_run_end"), default="manual")
    parser.add_argument("--ramp-s", type=float, default=0.0)
    parser.add_argument("--duration-s", type=float, default=0.0)
    parser.add_argument("--restore-normal", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = args.run_dir / "RUN_MANIFEST.json"
    if not manifest_path.is_file():
        raise SystemExit("fault_request_run_manifest_missing")
    try:
        manifest = _read_object(manifest_path)
        contract = load_contract(ROOT / "Config" / "control_platform" / "factory_injection_contract.json")
        commands = build_commands(manifest, contract, args)
        written = write_commands(args.run_dir, commands)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps({"schema": "mosim.operator_fault_request_result.v1", "written": [str(path) for path in written]}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
