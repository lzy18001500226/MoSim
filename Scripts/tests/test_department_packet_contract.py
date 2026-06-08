#!/usr/bin/env python3
"""Tests for generic visible-department packet contract validation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_checker():
    path = ROOT / "Scripts" / "quality" / "check_department_packet_contract.py"
    spec = importlib.util.spec_from_file_location("check_department_packet_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def base_packet() -> dict:
    return {
        "status": "completed",
        "department_local_goal": "close the diagnostic gate",
        "critical_path_steps": ["read evidence", "write packet"],
        "parallelizable_slices": ["read-only log audit"],
        "subagent_plan": "available_but_not_useful",
        "subagent_plan_reason": "current task is small and evidence-local",
        "subagents_used": [],
        "verification_gates": ["json valid"],
        "manual_review_or_blocker_triggers": ["missing evidence"],
        "actual_engineering_outputs": ["ROS2 source-window topic evidence"],
        "claim_boundary": ["diagnostic only"],
        "semantic_boundary": {
            "decision_scope": "visible_thread",
            "state_class": "routable",
            "evidence_minimum": ["expected packet exists"],
            "allowed_actions": ["integrate return packet"],
            "forbidden_actions": ["claim runtime success"],
            "stop_triggers": ["missing evidence"],
            "next_owner": "PMO",
        },
    }


def test_valid_completed_packet_passes() -> None:
    checker = load_checker()
    assert checker.validate(base_packet(), strict_completed_outputs=True) == []


def test_missing_planning_fields_fail() -> None:
    checker = load_checker()
    packet = base_packet()
    packet.pop("subagent_plan")
    errors = checker.validate(packet, strict_completed_outputs=True)
    assert "missing required planning field: subagent_plan" in errors


def test_invalid_subagent_plan_fails() -> None:
    checker = load_checker()
    packet = base_packet()
    packet["subagent_plan"] = "mandatory"
    errors = checker.validate(packet, strict_completed_outputs=True)
    assert any("subagent_plan must be one of" in err for err in errors)


def test_non_string_subagent_plan_fails_cleanly() -> None:
    checker = load_checker()
    packet = base_packet()
    packet["subagent_plan"] = {"outcome": "available_but_not_useful"}
    errors = checker.validate(packet, strict_completed_outputs=True)
    assert "subagent_plan must be a string enum, not dict" in errors


def test_json_only_completed_packet_fails() -> None:
    checker = load_checker()
    packet = base_packet()
    packet["actual_engineering_outputs"] = [
        "JSON return packet",
        "PROGRESS.md ledger entry",
    ]
    errors = checker.validate(packet, strict_completed_outputs=True)
    assert "completed packet actual_engineering_outputs appears control-plane only" in errors


def test_rule_sync_packet_can_allow_control_plane_outputs() -> None:
    checker = load_checker()
    packet = base_packet()
    packet["task_class"] = "rule_sync_only"
    packet["actual_engineering_outputs"] = ["JSON return packet"]
    assert checker.validate(packet, strict_completed_outputs=True) == []


def test_completed_packet_requires_claim_boundary() -> None:
    checker = load_checker()
    packet = base_packet()
    packet.pop("claim_boundary")
    errors = checker.validate(packet, strict_completed_outputs=True)
    assert "completed packet missing claim_boundary" in errors


def test_missing_semantic_boundary_fails_for_current_packet() -> None:
    checker = load_checker()
    packet = base_packet()
    packet.pop("semantic_boundary")
    errors = checker.validate(packet, strict_completed_outputs=True)
    assert "missing required semantic_boundary" in errors


def test_semantic_boundary_rejects_free_text_state_class() -> None:
    checker = load_checker()
    packet = base_packet()
    packet["semantic_boundary"]["state_class"] = "healthy"
    errors = checker.validate(packet, strict_completed_outputs=True)
    assert "semantic_boundary.state_class is free-text-only: healthy" in errors


def test_semantic_boundary_rejects_unknown_mworks_state_class() -> None:
    checker = load_checker()
    packet = base_packet()
    packet["semantic_boundary"]["decision_scope"] = "mworks_window_patrol"
    packet["semantic_boundary"]["state_class"] = "window_ok"
    errors = checker.validate(packet, strict_completed_outputs=True)
    assert "semantic_boundary.state_class unknown for MWORKS: window_ok" in errors
