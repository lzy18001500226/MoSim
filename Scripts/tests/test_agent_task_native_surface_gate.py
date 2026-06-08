#!/usr/bin/env python3
"""Regression checks for the native Codex surface gate task-packet checker."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_agent_task_native_surface_gate.py"


def semantic_boundary(state_class: str = "routable") -> dict:
    return {
        "decision_scope": "visible_thread",
        "state_class": state_class,
        "evidence_minimum": ["target thread is active_visible"],
        "allowed_actions": ["send bounded task packet"],
        "forbidden_actions": ["change visible-thread lifecycle"],
        "stop_triggers": ["approval or provider surface appears"],
        "next_owner": "UE",
    }


def run_checker(packet_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(packet_path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_native_surface_gate_accepts_visible_thread_packet(tmp_path: Path) -> None:
    packet = {
        "task_id": "NATIVE-SURFACE-GATE-SMOKE",
        "target_thread": "MoSim｜UE实验控制台与场景交互部",
        "target_thread_id": "019e9b24-50aa-7cd3-9e7c-4c43b224d993",
        "expected_return_path": "Results/agent_packets/returns/NATIVE-SURFACE-GATE-SMOKE.json",
        "blocker_return_path": "Results/agent_packets/blockers/NATIVE-SURFACE-GATE-SMOKE.json",
        "semantic_boundary": semantic_boundary(),
        "native_surface_gate": {
            "selected_native_surface": ["visible_thread", "coagent_packet_glue"],
            "surface_selection_reason": "Durable UE department context is needed; packet files are the return channel.",
            "worktree_required": False,
            "worktree_decision": "Read-only planning task; no code or asset writes are allowed.",
            "rejected_surfaces": {
                "subagent": "Disposable context is insufficient for recurring UE console ownership.",
                "codex_exec": "Formal hidden dispatch is not accepted until visible delivery is verified.",
            },
        },
    }
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["fail_count"] == 0
    assert report["selected_native_surfaces"] == ["coagent_packet_glue", "visible_thread"]


def test_native_surface_gate_rejects_missing_gate(tmp_path: Path) -> None:
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(
        json.dumps(
            {
                "task_id": "MISSING-GATE",
                "expected_return_path": "Results/agent_packets/returns/MISSING-GATE.json",
                "blocker_return_path": "Results/agent_packets/blockers/MISSING-GATE.json",
            }
        ),
        encoding="utf-8",
    )

    completed = run_checker(packet_path)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    assert report["findings"][0]["reason"] == "missing_native_surface_gate"


def test_native_surface_gate_rejects_mworks_department_packet_without_mworks_gate(tmp_path: Path) -> None:
    packet = {
        "task_id": "MWORKS-MISSING-LIVE-GATE",
        "target_department": "MWorksDynamicsControlAgent",
        "target_thread": "MoSim｜MWORKS动力学与控制验证部-R1",
        "target_thread_id": "019e9be5-334b-76b1-93f9-8b02caebf376",
        "expected_return_path": "Results/agent_packets/returns/MWORKS-MISSING-LIVE-GATE.json",
        "blocker_return_path": "Results/agent_packets/blockers/MWORKS-MISSING-LIVE-GATE.json",
        "semantic_boundary": {
            "decision_scope": "mworks_live_task",
            "state_class": "live_attach_blocked",
            "evidence_minimum": ["MWORKS live gate is required before live work"],
            "allowed_actions": ["write blocker"],
            "forbidden_actions": ["open a new MWORKS window"],
            "stop_triggers": ["missing mworks_live_gate"],
            "next_owner": "PMO",
        },
        "native_surface_gate": {
            "selected_native_surface": ["visible_thread", "coagent_packet_glue"],
            "surface_selection_reason": "Durable MWORKS department context is needed.",
            "worktree_required": False,
            "worktree_decision": "No source writes are expected.",
        },
    }
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "mworks_department_gate_missing_mworks_live_gate" in reasons


def test_native_surface_gate_accepts_mworks_department_packet_with_mworks_gate(tmp_path: Path) -> None:
    packet = {
        "task_id": "MWORKS-WITH-LIVE-GATE",
        "target_department": "MWorksGraphicalModelAuditAgent",
        "target_thread": "MoSim｜MWORKS动力学与控制验证部-R2",
        "target_thread_id": "019e9999-b0d3-7682-bccd-faef08fcf1df",
        "expected_return_path": "Results/agent_packets/returns/MWORKS-WITH-LIVE-GATE.json",
        "blocker_return_path": "Results/agent_packets/blockers/MWORKS-WITH-LIVE-GATE.json",
        "semantic_boundary": {
            "decision_scope": "mworks_live_task",
            "state_class": "live_attach_blocked",
            "evidence_minimum": ["static-only task declares no live MWORKS touch"],
            "allowed_actions": ["perform static source audit"],
            "forbidden_actions": ["run live check_model or SimulateModel"],
            "stop_triggers": ["task attempts live GUI work"],
            "next_owner": "MWORKS_R2",
        },
        "native_surface_gate": {
            "selected_native_surface": ["visible_thread", "coagent_packet_glue"],
            "surface_selection_reason": "Durable MWORKS department context is needed.",
            "worktree_required": False,
            "worktree_decision": "No source writes are expected.",
        },
        "mworks_live_gate": {
            "live_mworks_touched": False,
            "mworks_window_evidence_touched": True,
            "mworks_window_policy": "reuse_existing_session_default_no_new_window",
            "expected_engineering_outputs": [
                "static package inventory evidence",
                "old-to-new model mapping",
                "graphical layout review plan",
            ],
            "activation_sentinel_required": True,
            "background_screenshot_required": True,
            "preflight_order": [
                "run Scripts/agent/check_mworks_gui_sentinel.py before first business step",
                "capture existing windows with Scripts/tools/capture_window_background.ps1",
            ],
            "required_return_fields": [
                "activation_sentinel_before",
                "activation_state_observation",
                "background_screenshot_before",
                "license_state",
                "gui_sentinel_before",
                "will_not_click_activation_login=true",
                "live_mworks_touched",
                "mworks_window_evidence_touched",
            ],
            "blocker_on": [
                "demo edition",
                "unactivated software",
                "login prompt",
                "activation prompt",
                "authorization failure",
                "GUI error-report dialog",
                "unknown sentinel state",
            ],
        },
    }
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True


def test_native_surface_gate_rejects_missing_semantic_boundary(tmp_path: Path) -> None:
    packet = {
        "task_id": "MISSING-SEMANTIC-BOUNDARY",
        "target_thread": "MoSim｜UE实验控制台与场景交互部",
        "target_thread_id": "019e9b24-50aa-7cd3-9e7c-4c43b224d993",
        "expected_return_path": "Results/agent_packets/returns/MISSING-SEMANTIC-BOUNDARY.json",
        "blocker_return_path": "Results/agent_packets/blockers/MISSING-SEMANTIC-BOUNDARY.json",
        "native_surface_gate": {
            "selected_native_surface": ["visible_thread", "coagent_packet_glue"],
            "surface_selection_reason": "Durable UE department context is needed.",
            "worktree_required": False,
            "worktree_decision": "No worktree needed.",
        },
    }
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "missing_semantic_boundary" in reasons


def test_native_surface_gate_rejects_free_text_state_class(tmp_path: Path) -> None:
    packet = {
        "task_id": "BAD-STATE-CLASS",
        "target_thread": "MoSim｜UE实验控制台与场景交互部",
        "target_thread_id": "019e9b24-50aa-7cd3-9e7c-4c43b224d993",
        "expected_return_path": "Results/agent_packets/returns/BAD-STATE-CLASS.json",
        "blocker_return_path": "Results/agent_packets/blockers/BAD-STATE-CLASS.json",
        "semantic_boundary": semantic_boundary("healthy"),
        "native_surface_gate": {
            "selected_native_surface": ["visible_thread", "coagent_packet_glue"],
            "surface_selection_reason": "Durable UE department context is needed.",
            "worktree_required": False,
            "worktree_decision": "No worktree needed.",
        },
    }
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")

    completed = run_checker(packet_path)
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    reasons = {finding["reason"] for finding in report["findings"]}
    assert "free_text_only_state_class" in reasons
