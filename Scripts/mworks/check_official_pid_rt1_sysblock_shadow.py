#!/usr/bin/env python3
"""Check that the RT1 Official PID shadow path is owned by the graphical core."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Models/MoSimQuadrotorModel/Control/Adapters/OfficialPidSysblockAttitudeThrustAdapter.mo"
DEPLOYMENT = ROOT / "Models/MoSimQuadrotorModel/Deployment/RT1OfficialPidSysblockShadow50Hz.mo"
ADAPTER_ORDER = ROOT / "Models/MoSimQuadrotorModel/Control/Adapters/package.order"
DEPLOYMENT_ORDER = ROOT / "Models/MoSimQuadrotorModel/Deployment/package.order"
FORMAL_RUNNER = ROOT / "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/OfficialPidSysblockAttitudeThrustFormalRunner.mo"
FORMAL_RUNNER_ORDER = ROOT / "Models/MoSimQuadrotorModel/Experiment/Runners/Formal/package.order"


def require(text: str, token: str, failures: list[str], label: str) -> None:
    if token not in text:
        failures.append(f"missing {label}: {token}")


def reject(text: str, token: str, failures: list[str], label: str) -> None:
    if token in text:
        failures.append(f"unexpected {label}: {token}")


def run_checks() -> dict[str, Any]:
    failures: list[str] = []
    paths = [
        ADAPTER,
        DEPLOYMENT,
        ADAPTER_ORDER,
        DEPLOYMENT_ORDER,
        FORMAL_RUNNER,
        FORMAL_RUNNER_ORDER,
    ]
    missing_paths = [path.as_posix() for path in paths if not path.is_file()]
    if missing_paths:
        return {
            "schema": "mosim.official_pid_rt1_sysblock_shadow_check.v1",
            "status": "fail",
            "failures": [f"missing paths: {', '.join(missing_paths)}"],
        }

    adapter = ADAPTER.read_text(encoding="utf-8")
    deployment = DEPLOYMENT.read_text(encoding="utf-8")
    adapter_order = ADAPTER_ORDER.read_text(encoding="utf-8").splitlines()
    deployment_order = DEPLOYMENT_ORDER.read_text(encoding="utf-8").splitlines()
    formal_runner = FORMAL_RUNNER.read_text(encoding="utf-8")
    formal_runner_order = FORMAL_RUNNER_ORDER.read_text(encoding="utf-8").splitlines()

    require(
        adapter,
        "extends MoSimQuadrotorModel.Control.Interfaces.PartialAttitudeThrustController;",
        failures,
        "formal ATTITUDE_THRUST contract",
    )
    require(
        adapter,
        "MoSimQuadrotorModel.Control.PID.OfficialPidGraphicalCore",
        failures,
        "native graphical core binding",
    )
    for token in (
        "connect(controller_core.roll_ref_limit.y, attitude_ref[1])",
        "connect(controller_core.pitch_ref_limit.y, attitude_ref[2])",
        "native_collective_thrust_mapper",
        "connect(controller_core.thrust_command.y, native_collective_thrust_mapper.u)",
        "connect(native_collective_thrust_mapper.y, collective_thrust_delta)",
    ):
        require(adapter, token, failures, "direct graphical signal export")
    require(adapter, "attitude_ref[3] = yaw_reference_rad;", failures, "fixed graphical yaw boundary")

    require(
        deployment,
        "OfficialPidSysblockAttitudeThrustAdapter\n    controller",
        failures,
        "RT1 graphical adapter binding",
    )
    for token in (
        "mosim_mworks_live_rt1_receive(",
        "mosim_mworks_live_rt1_send(",
        "controller.position_ref = positionReference;",
        "controller.velocity_ref = {0, 0, 0};",
        "controller.acceleration_ref = {0, 0, 0};",
        "controller.position_mea = positionMeasurement;",
        "controller.velocity_mea = {0, 0, 0};",
        "controller.attitude_mea = attitudeMeasurement;",
        "thrustDeltaNewton = controller.collective_thrust_delta;",
        "when sample(samplePeriod / 2, samplePeriod)",
        "shadow-only",
    ):
        require(deployment, token, failures, "RT1 bridge contract")
    for token in (
        "mosim_mworks_live_rt1_exchange_official_pid",
        "exchangeOfficialPid",
        "desiredAcceleration",
        "parameter Real kp",
        "parameter Real kv",
    ):
        reject(deployment, token, failures, "embedded controller calculation")

    if "OfficialPidSysblockAttitudeThrustAdapter" not in adapter_order:
        failures.append("adapter package.order omits OfficialPidSysblockAttitudeThrustAdapter")
    if "RT1OfficialPidSysblockShadow50Hz" not in deployment_order:
        failures.append("deployment package.order omits RT1OfficialPidSysblockShadow50Hz")
    require(
        formal_runner,
        "MoSimQuadrotorModel.Experiment.Runners.Base.FormalAttitudeThrustRunnerBase",
        failures,
        "formal whole-aircraft runner base",
    )
    require(
        formal_runner,
        "MoSimQuadrotorModel.Control.Adapters.OfficialPidSysblockAttitudeThrustAdapter",
        failures,
        "formal graphical adapter binding",
    )
    if "OfficialPidSysblockAttitudeThrustFormalRunner" not in formal_runner_order:
        failures.append(
            "formal runner package.order omits OfficialPidSysblockAttitudeThrustFormalRunner"
        )

    return {
        "schema": "mosim.official_pid_rt1_sysblock_shadow_check.v1",
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "adapter": ADAPTER.relative_to(ROOT).as_posix(),
        "deployment": DEPLOYMENT.relative_to(ROOT).as_posix(),
        "claim_boundary": (
            "Static source/wiring contract only. This does not prove MWORKS CheckModel, "
            "RT0 realtime execution, controller takeover, Gazebo, or PX4 flight."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = run_checks()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
