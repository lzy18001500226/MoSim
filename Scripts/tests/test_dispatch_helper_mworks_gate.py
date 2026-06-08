#!/usr/bin/env python3
"""Regression checks for MWORKS department dispatch text."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_dispatch_helper():
    path = ROOT / "CoAgent" / "dispatch" / "dispatch_helper.py"
    spec = importlib.util.spec_from_file_location("dispatch_helper", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load dispatch_helper.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mworks_department_dispatch_text_includes_self_evidence_gate() -> None:
    module = load_dispatch_helper()
    args = argparse.Namespace(
        db=ROOT / ".tmp" / "unused_tasks.sqlite3",
        events=ROOT / ".tmp" / "unused_events.jsonl",
        registry=ROOT / "CoAgent" / "dispatch" / "department_threads.json",
        department="MWorksDynamicsControlAgent",
        task_id="MWORKS-DISPATCH-TEXT-SMOKE",
    )

    lines = module._mworks_live_gate_contract_lines(args.department)
    text = "\n".join(lines)

    assert "Routine activation/window-health patrol is owned by CoAgentOps every 10 minutes" in text
    assert "activation_patrol_owner=CoAgentOps" in text
    assert "mworks_activation_patrol_reference" in text
    assert "run at most one bounded current-turn sentinel/API check" in text
    assert "Do not loop on activation checks" in text
    assert "education-edition title only proves the visible edition/window marker" in text
    assert "it also is not by itself a blocker" in text
    assert "semantic_boundary" in text
    assert "state_class" in text
    assert "live_attach_blocked" in text
    assert "vague state words" in text
    assert "maximized target-window evidence" in text
    assert "not Codex, another app, helper/proxy windows" in text
    assert "official login action does not return" in text
    assert "status=blocked" in text
    assert "expected_engineering_outputs" in text
    assert "JSON result/blocker/task packets" in text
    assert "current-turn sentinel/capture evidence" in text
    assert "sentinel_unavailable_blocked" in text
    assert "mworks_phase_screenshots" in text
    assert "mworks_phase_observations" in text
    assert "R1 simulation/control tasks" in text
    assert "R2 graphical/layout tasks" in text
    assert "both sparse WeChat and sparse email alert" not in text
    assert "must not click login, activation" in text
    assert "PMO owns any user-authorized recovery" in text


def test_department_dispatch_text_includes_subagent_planning_decision_contract() -> None:
    module = load_dispatch_helper()

    text = "\n".join(module._department_local_planning_contract_lines())

    assert "Department Local Planning And Subagent Decision Contract" in text
    assert "not a requirement to use at least one sub-agent" in text
    assert "subagent_plan" in text
    assert "subagent_plan_reason" in text
    assert "subagents_used=[]" in text
    assert "used, available_but_not_useful, unavailable, unsafe" in text
    assert "Disposable sub-agents are not durable departments" in text


def test_department_dispatch_text_includes_generic_execution_acceptance_contract() -> None:
    module = load_dispatch_helper()

    text = "\n".join(module._department_execution_acceptance_contract_lines())

    assert "Department Execution And Acceptance Contract" in text
    assert "accountable owner" in text
    assert "task-specific infrastructure preflight" in text
    assert "return a blocker promptly" in text
    assert "phase checkpoints" in text
    assert "expected engineering output" in text
    assert "ROS2 runtime work" in text
    assert "Asset/PBR work" in text
    assert "control-plane evidence" in text
    assert "diagnostic_only" in text
    assert "PMO may reject completed packets" in text


def test_non_mworks_department_dispatch_text_has_no_mworks_gate() -> None:
    module = load_dispatch_helper()
    assert module._mworks_live_gate_contract_lines("ROS2RuntimeAgent") == []


def test_non_mworks_department_dispatch_text_still_has_generic_contract(monkeypatch) -> None:
    module = load_dispatch_helper()

    def fake_build_dispatch_envelope(args: argparse.Namespace) -> dict:
        return {
            "target_department": "ROS2RuntimeAgent",
            "thread_name": "MoSim｜ROS2感知定位与规划运行部-R1",
            "thread_id": "thread-ros2",
            "surface": "codex_app_native",
            "status": "active_visible",
            "task_packet": {"task_id": "ROS2-DISPATCH-TEXT-SMOKE"},
            "task_packet_text": "task_packet_body",
        }

    monkeypatch.setattr(module, "build_dispatch_envelope", fake_build_dispatch_envelope)

    result = module.build_department_task_text(argparse.Namespace())
    text = result["text"]

    assert "Department Local Planning And Subagent Decision Contract" in text
    assert "Department Execution And Acceptance Contract" in text
    assert "ROS2 Runtime Gate Contract" in text
    assert "MWORKS Live Gate Contract" not in text


def test_ros2_department_dispatch_text_includes_runtime_gate() -> None:
    module = load_dispatch_helper()

    text = "\n".join(module._ros2_runtime_gate_contract_lines("ROS2RuntimeAgent"))

    assert "ROS2 Runtime Gate Contract" in text
    assert "no-rerun" in text
    assert "stale MoSim/FAST-LIO/planner processes" in text
    assert "probe_count" in text
    assert "forbidden topics" in text
    assert "cleanup_summary" in text
    assert "planner_ready" in text
    assert "closed_loop" in text


def test_ue_department_dispatch_text_includes_runtime_review_gate() -> None:
    module = load_dispatch_helper()

    text = "\n".join(module._ue_runtime_gate_contract_lines("UEExperimentConsoleAgent"))

    assert "UE Runtime And Review Gate Contract" in text
    assert "source-static, build, editor/runtime, or manual-review" in text
    assert "Runtime ack requires" in text
    assert "teleport UAV pose" in text
    assert "open/display" in text


def test_sunray_department_dispatch_text_includes_asset_gate() -> None:
    module = load_dispatch_helper()

    text = "\n".join(module._sunray_asset_gate_contract_lines("Sunray150AssetPBRAgent"))

    assert "Sunray150 Asset And PBR Gate Contract" in text
    assert "DAE-derived Blender asset line" in text
    assert "real visual artifacts" in text
    assert "Base Color edit" in text
    assert "mass/inertia/motor/thrust" in text
    assert "human review" in text
