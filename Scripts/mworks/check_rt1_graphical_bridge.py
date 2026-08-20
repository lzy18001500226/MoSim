#!/usr/bin/env python3
"""Check the source-level RT1 boundary between UDP transport and Sysblock control."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "Models/MoSimQuadrotorModel/RealTime/Resources/Include/mosim_mworks_live_rt1_bridge.h"
EXCHANGE_HEADER = ROOT / "Models/MoSimQuadrotorModel/RealTime/Resources/Include/mosim_mworks_rt1_graphical_exchange.h"
MODEL = ROOT / "Models/MoSimQuadrotorModel/RealTime/MworksRt1Px4CtrlGraphicalShadow100Hz.mo"
ROOT_ORDER = ROOT / "Models/MoSimQuadrotorModel/package.order"
REALTIME_ORDER = ROOT / "Models/MoSimQuadrotorModel/RealTime/package.order"
OUTER_LOOP = ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlOuterLoopGraphicalSysblock.mo"
ADAPTER = ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlAttitudeThrustSysblockAdapter.mo"
PX4CTRL_PACKAGE = ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/package.mo"
PX4CTRL_ORDER = ROOT / "Models/MoSimQuadrotorModel/Control/Px4Ctrl/package.order"
CONTROL_ORDER = ROOT / "Models/MoSimQuadrotorModel/Control/package.order"
LOOPBACK_RUNNER = ROOT / "Scripts/mworks/run_rt1_graphical_loopback_mcp.py"


def inspect_graphical_outer_loop(text: str) -> tuple[dict[str, bool], dict[str, int]]:
    """Return the source-only review surface for the nested Sysblock core."""
    connect_count = len(re.findall(r"^\s*connect\s*\(", text, re.MULTILINE))
    line_count = len(re.findall(r"annotation\s*\(\s*Line\b", text))
    required_blocks = (
        "SysplorerEmbeddedCoder.Port.Inport",
        "SysplorerEmbeddedCoder.Port.Outport",
        "SysplorerEmbeddedCoder.MathOperation.Sum",
        "SysplorerEmbeddedCoder.MathOperation.Gain",
        "SysplorerEmbeddedCoder.Sources.Constant",
    )
    checks = {
        "native_model_workspace": "extends ModelWorkspace;" in text,
        "sysblock_metadata": all(
            marker in text
            for marker in (
                "__MWORKS",
                "modelType=Control",
                "BlockSystem(blockKind=BlockKind.userModel",
                'SysblockVersion="1.0"',
            )
        ),
        "visible_native_blocks": all(marker in text for marker in required_blocks),
        "visible_connections": connect_count > 0,
        "non_degenerate_line_annotations": (
            connect_count > 0
            and line_count == connect_count
            and "points={{0,0},{0,0}}" not in text.replace(" ", "")
        ),
        "not_equation_or_c_bridge": not any(
            marker in text for marker in ("CFunction", "EquationBridge", "external ")
        ),
    }
    return checks, {"connect_count": connect_count, "line_annotation_count": line_count}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "Results/mworks_live_gate/rt1_graphical_bridge/RT1_STATIC_CONTRACT.json",
    )
    args = parser.parse_args()

    header = HEADER.read_text(encoding="utf-8")
    exchange_header = EXCHANGE_HEADER.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    root_order = ROOT_ORDER.read_text(encoding="utf-8")
    realtime_order = REALTIME_ORDER.read_text(encoding="utf-8")
    outer_loop = OUTER_LOOP.read_text(encoding="utf-8")
    adapter = ADAPTER.read_text(encoding="utf-8")
    px4ctrl_package = PX4CTRL_PACKAGE.read_text(encoding="utf-8")
    px4ctrl_order = PX4CTRL_ORDER.read_text(encoding="utf-8")
    control_order = CONTROL_ORDER.read_text(encoding="utf-8")
    loopback_runner = LOOPBACK_RUNNER.read_text(encoding="utf-8")
    graphical_core_checks, graphical_core_counts = inspect_graphical_outer_loop(outer_loop)
    checks = {
        "fixed_state_frame": "double values[24]" in header,
        "bounded_receive_drain": "MOSIM_RT1_MAX_DRAIN 512" in header
        and "for (index = 0; index < MOSIM_RT1_MAX_DRAIN; ++index)" in header,
        "generic_receive": "mosim_mworks_live_rt1_receive" in header,
        "generic_send": "mosim_mworks_live_rt1_send" in header,
        "socket_diagnostics": "mosim_mworks_live_rt1_socket_status" in header,
        "no_c_controller": "mosim_rt1_compute_and_send_official_pid" not in header
        and "mosim_mworks_live_rt1_exchange_official_pid" not in header,
        "single_translation_unit_exchange": (
            '#include "mosim_mworks_live_rt1_bridge.h"' in exchange_header
            and "mosim_mworks_rt1_graphical_exchange" in exchange_header
            and "mosim_rt1_graphical_exchange_call_count" in exchange_header
            and "*exchange_call_count = mosim_rt1_graphical_exchange_call_count" in exchange_header
            and "received_datagrams" in exchange_header
            and "receive_error_code" in exchange_header
            and exchange_header.index("mosim_mworks_live_rt1_receive")
            < exchange_header.index("mosim_mworks_live_rt1_send")
        ),
        "realtime_transport_pacing": (
            'final parameter Integer transportPaceMs(min = 0) = 10' in model
            and "transportPaceMs" in model
            and "int transport_pace_ms" in exchange_header
            and "Sleep((DWORD)transport_pace_ms);" in exchange_header
        ),
        "graphical_core_adapter": "Px4CtrlAttitudeThrustSysblockAdapter" in model,
        "bridge_model_package_registered": (
            "RealTime" in root_order.splitlines()
            and "MworksRt1Px4CtrlGraphicalShadow100Hz" in realtime_order.splitlines()
        ),
        "adapter_selects_nested_graphical_core": all(
            marker in adapter
            for marker in (
                "Px4CtrlOuterLoopGraphicalSysblock outer_loop",
                "connect(position_ref[1], outer_loop.ref_p_x);",
                "connect(outer_loop.desired_acc_x, graphical_desired_acceleration[1]);",
                "connect(outer_loop.desired_acc_z, graphical_desired_acceleration[3]);",
            )
        ),
        "adapter_uses_graphical_output_only": all(
            marker in adapter
            for marker in (
                "desired_acceleration[1] = graphical_desired_acceleration[1];",
                "desired_acceleration[2] = graphical_desired_acceleration[2];",
                "desired_acceleration[3] = graphical_desired_acceleration[3];",
            )
        )
        and "if time < controller_sample_period_s" not in adapter
        and "EquationBridge law" not in adapter,
        "graphical_core_package_registered": (
            "package Px4Ctrl" in px4ctrl_package
            and "Px4CtrlOuterLoopGraphicalSysblock" in px4ctrl_order.splitlines()
            and "Px4CtrlAttitudeThrustSysblockAdapter" in px4ctrl_order.splitlines()
            and "Px4Ctrl" in control_order.splitlines()
        ),
        "graphical_outer_loop_review_surface": all(graphical_core_checks.values()),
        "adapter_wrapper_not_sec_instance": (
            "graphicalController(profile = profile);" in model
            and "graphicalController(profile = profile, controller_sample_period_s"
            not in model
        ),
        "causal_queued_command_pipeline": all(
            marker in model
            for marker in (
                "when sample(0, samplePeriod) then",
                "if pre(pendingCommand) then 1 else 0",
                "pre(queuedCommandQx)",
                "queuedCommandQx := commandQx;",
            )
        ),
        "graphical_core_startup_gate": all(
            marker in model
            for marker in (
                "discrete Integer graphicalStateTicks(start = 0, fixed = true);",
                "graphicalStateTicks := pre(graphicalStateTicks) + 1;",
                "pendingCommand := pre(graphicalStateTicks) >= 1;",
            )
        ),
        "discrete_transport_flags": all(
            marker in model
            for marker in (
                "discrete Integer saturationMask(start = 0, fixed = true);",
                "discrete Integer controllerStatus(start = 0, fixed = true);",
                "discrete Integer controllerOutputValid(start = 0, fixed = true);",
            )
        ),
        "receive_diagnostics": all(
            marker in model
            for marker in (
                "receivedDatagramsThisTick",
                "rejectedDatagramsThisTick",
                "lastReceivedByteCount",
                "receiveErrorCode",
            )
        )
        and "mosim_rt1_last_receive_datagrams" in header,
        "aggregate_receive_diagnostics": all(
            marker in model
            for marker in (
                "discrete Integer sampleTicks(start = 0, fixed = true);",
                "discrete Integer receivedDatagrams(start = 0, fixed = true);",
                "discrete Integer rejectedDatagrams(start = 0, fixed = true);",
                "sampleTicks := pre(sampleTicks) + 1;",
                "receivedDatagrams := pre(receivedDatagrams)",
                "rejectedDatagrams := pre(rejectedDatagrams)",
            )
        ),
        "exchange_call_diagnostic": all(
            marker in model
            for marker in (
                "output Integer exchangeCallCount;",
                "discrete Integer exchangeCallCount(start = 0, fixed = true);",
                "(processedThisTick, exchangeCallCount, sendStatus, socketReady, socketInitStatus,",
            )
        ),
        "single_exchange_binding": (
            "mosim_mworks_rt1_graphical_exchange" in model
            and "mosim_mworks_rt1_graphical_exchange.h" in model
            and "mosim_mworks_live_rt1_receive(" not in model
            and "mosim_mworks_live_rt1_send(" not in model
        ),
        "frame_mapping": all(f"stateValues[{index}]" in model for index in (1, 7, 10, 14, 17, 20)),
        "declared_100hz_boundary": "final parameter Real samplePeriod(unit = \"s\") = 0.01" in model,
        "fixture_precedes_single_batch_simulation": (
            "BATCH_SIM_MODE = 2" in loopback_runner
            and '"sim_mode": BATCH_SIM_MODE' in loopback_runner
            and '"startup_strategy": "fixture_precedes_single_batch_simulation"'
            in loopback_runner
            and "warmup_simulation = client.call_tool" not in loopback_runner
            and loopback_runner.index("fixture_process = subprocess.Popen")
            < loopback_runner.index("simulation = client.call_tool")
        ),
    }
    result = {
        "schema": "mosim.mworks_rt1_graphical_bridge_static.v1",
        "source": "static_source_check",
        "live_mworks_touched": False,
        "will_not_click_activation_login": True,
        "controller_execution_boundary": "Sysblock via Px4CtrlAttitudeThrustSysblockAdapter",
        "graphical_core_model": "MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlOuterLoopGraphicalSysblock",
        "graphical_core_source": str(OUTER_LOOP.relative_to(ROOT)),
        "graphical_core_checks": graphical_core_checks,
        "graphical_core_counts": graphical_core_counts,
        "transport_execution_boundary": "C UDP receive/send only",
        "checks": checks,
        "passed": all(checks.values()),
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
