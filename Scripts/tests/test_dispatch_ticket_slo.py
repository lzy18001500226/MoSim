#!/usr/bin/env python3
"""Tests for PMO visible-thread dispatch ticket SLO validation."""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_checker():
    path = ROOT / "Scripts" / "quality" / "check_dispatch_ticket_slo.py"
    spec = importlib.util.spec_from_file_location("check_dispatch_ticket_slo", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def base_ticket() -> dict:
    return {
        "ticket_version": 1,
        "request_id": "PMO-DISPATCH-SLO-SMOKE",
        "dispatch_nonce": "dispatch-slo-smoke-nonce",
        "task_type": "source_static",
        "owner": "PMO",
        "target_thread": "MoSim｜ROS2 Runtime 集成-R1",
        "target_thread_id": "019e9c72-ee74-79d1-b9fe-621d3c6fc99e",
        "task_packet_path": "Results/agent_packets/tasks/PMO-DISPATCH-SLO-SMOKE.json",
        "expected_return_path": "Results/agent_packets/returns/PMO-DISPATCH-SLO-SMOKE.json",
        "blocker_return_path": "Results/agent_packets/blockers/PMO-DISPATCH-SLO-SMOKE.json",
        "sent_at": "2026-06-09T10:00:00+08:00",
        "first_readback_due": "2026-06-09T10:00:30+08:00",
        "second_readback_due_if_no_visible_turn": "2026-06-09T10:02:00+08:00",
        "failure_suspected_due": "2026-06-09T10:05:00+08:00",
        "first_agent_output_due": "2026-06-09T10:05:00+08:00",
        "dispatcher_next_check_due": "2026-06-09T10:02:00+08:00",
        "dispatcher_owns_slo_closure": True,
        "expected_packet_due": "2026-06-09T10:15:00+08:00",
        "checkpoint_due": None,
        "durable_start_due": "2026-06-09T10:05:00+08:00",
        "durable_start_requirement": {
            "required": True,
            "exempt": False,
            "artifact_path_or_class": (
                "Results/runtime_leases/"
                "019e9c72-ee74-79d1-b9fe-621d3c6fc99e/"
                "PMO-DISPATCH-SLO-SMOKE.json"
            ),
            "artifact_type": "runtime_lease",
            "nonce": "dispatch-slo-smoke-nonce",
            "minimum_fields": [
                "request_id",
                "target_thread_id",
                "nonce",
                "started_at",
                "last_checkpoint_at",
                "current_phase",
                "next_checkpoint_due_at",
            ],
            "artifact_seen": False,
            "artifact_observed_at": None,
            "last_checkpoint_at": None,
            "next_checkpoint_due_at": None,
            "current_phase": None,
        },
        "last_observed_turn": "turn 019example inProgress",
        "observed_state": "visible_turn_in_progress",
        "breach_action": "wait_for_expected_packet",
    }


def at(value: str) -> datetime:
    return datetime.fromisoformat(value)


def test_source_static_dispatch_ticket_passes() -> None:
    checker = load_checker()
    errors = checker.validate(base_ticket(), now=at("2026-06-09T10:03:00+08:00"))
    assert errors == []


def test_visible_thread_dispatch_ticket_template_passes() -> None:
    checker = load_checker()
    template = ROOT / "CoAgent" / "protocol" / "templates" / "visible_thread_dispatch_ticket.json"
    ticket = checker._load_json(template)
    assert checker.validate(ticket, now=at("2026-06-09T10:06:00+08:00")) == []


def test_source_static_expected_packet_due_must_be_10_to_20_minutes() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["expected_packet_due"] = "2026-06-09T10:25:00+08:00"
    errors = checker.validate(ticket, now=at("2026-06-09T10:03:00+08:00"))
    assert any("expected_packet_due for source_static" in err for err in errors)


def test_missing_visible_turn_after_five_minutes_requires_suspected_failure() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["last_observed_turn"] = "none"
    ticket["observed_state"] = "no_visible_turn"
    ticket["breach_action"] = "recheck_within_2m"
    errors = checker.validate(ticket, now=at("2026-06-09T10:05:30+08:00"))
    assert (
        "after 5 minutes with no visible turn/agent output/packet, breach_action must be dispatch_surface_failure_suspected"
        in errors
    )


def test_no_visible_turn_second_readback_due_must_be_within_two_minutes() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["second_readback_due_if_no_visible_turn"] = "2026-06-09T10:03:00+08:00"
    errors = checker.validate(ticket, now=at("2026-06-09T10:01:00+08:00"))
    assert "second_readback_due_if_no_visible_turn must be within 2 minutes of sent_at" in errors


def test_runtime_lease_missing_nonce_fails() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["durable_start_requirement"]["nonce"] = ""
    errors = checker.validate(ticket, now=at("2026-06-09T10:03:00+08:00"))
    assert "runtime_lease durable_start_requirement.nonce is required" in errors


def test_ticket_version_2_requires_dispatch_nonce() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["ticket_version"] = 2
    ticket["dispatch_nonce"] = ""
    errors = checker.validate(ticket, now=at("2026-06-09T10:03:00+08:00"))
    assert "dispatch_nonce is required" in errors


def test_ticket_version_2_runtime_lease_nonce_must_match_dispatch_nonce() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["ticket_version"] = 2
    ticket["dispatch_nonce"] = "fresh-dispatch-nonce"
    ticket["durable_start_requirement"]["nonce"] = "stale-lease-nonce"
    errors = checker.validate(ticket, now=at("2026-06-09T10:03:00+08:00"))
    assert "runtime_lease durable_start_requirement.nonce must match dispatch_nonce" in errors


def test_ticket_version_2_runtime_lease_path_is_canonical() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["ticket_version"] = 2
    ticket["durable_start_requirement"]["artifact_path_or_class"] = (
        "Results/runtime_leases/wrong-thread/PMO-DISPATCH-SLO-SMOKE.json"
    )
    errors = checker.validate(ticket, now=at("2026-06-09T10:03:00+08:00"))
    assert any(
        "runtime_lease durable_start_requirement.artifact_path_or_class must be" in err
        for err in errors
    )


def test_runtime_lease_minimum_fields_must_include_required_fields() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["durable_start_requirement"]["minimum_fields"] = ["request_id", "target_thread_id"]
    errors = checker.validate(ticket, now=at("2026-06-09T10:03:00+08:00"))
    assert any(
        "runtime_lease durable_start_requirement.minimum_fields missing:" in err for err in errors
    )


def test_lease_missing_after_five_minutes_requires_suspected_failure() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["last_observed_turn"] = "turn visible but no lease artifact observed"
    ticket["observed_state"] = "lease_missing"
    ticket["breach_action"] = "wait_for_expected_packet"
    errors = checker.validate(ticket, now=at("2026-06-09T10:05:30+08:00"))
    assert (
        "lease_missing after failure_suspected_due must use breach_action dispatch_surface_failure_suspected"
        in errors
    )


def test_runtime_lease_seen_counts_as_progress_after_five_minutes() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["last_observed_turn"] = "turn visible and runtime lease observed"
    ticket["observed_state"] = "lease_seen"
    ticket["breach_action"] = "wait_for_expected_packet"
    ticket["durable_start_requirement"]["artifact_seen"] = True
    ticket["durable_start_requirement"]["artifact_observed_at"] = "2026-06-09T10:01:00+08:00"
    ticket["durable_start_requirement"]["last_checkpoint_at"] = "2026-06-09T10:01:00+08:00"
    ticket["durable_start_requirement"]["next_checkpoint_due_at"] = "2026-06-09T10:06:00+08:00"
    ticket["durable_start_requirement"]["current_phase"] = "started"
    errors = checker.validate(ticket, now=at("2026-06-09T10:05:30+08:00"))
    assert errors == []


def test_live_runtime_can_run_long_with_visible_turn_and_checkpoint() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["task_type"] = "live_runtime"
    ticket["expected_packet_due"] = "2026-06-09T12:00:00+08:00"
    ticket["checkpoint_due"] = "2026-06-09T10:10:00+08:00"
    ticket["observed_state"] = "agent_output_seen"
    ticket["last_observed_turn"] = "turn 019example inProgress with agent output"
    ticket["breach_action"] = "wait_for_checkpoint"
    errors = checker.validate(ticket, now=at("2026-06-09T10:06:00+08:00"))
    assert errors == []


def test_visible_turn_stuck_without_agent_output_after_five_minutes_escalates() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["last_observed_turn"] = "turn 019example inProgress, no agent output observed"
    ticket["observed_state"] = "visible_turn_in_progress"
    ticket["breach_action"] = "wait_for_expected_packet"
    errors = checker.validate(ticket, now=at("2026-06-09T10:05:30+08:00"))
    assert (
        "after 5 minutes with no visible turn/agent output/packet, breach_action must be dispatch_surface_failure_suspected"
        in errors
    )
    assert (
        "after first_agent_output_due with visible turn but no agent output/packet, breach_action must escalate"
        in errors
    )


def test_visible_turn_stuck_state_requires_escalating_action() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["last_observed_turn"] = "turn 019example inProgress, still thinking"
    ticket["observed_state"] = "visible_turn_stuck_no_agent_output"
    ticket["breach_action"] = "wait_for_expected_packet"
    errors = checker.validate(ticket, now=at("2026-06-09T10:05:30+08:00"))
    assert any("no visible turn/agent output/packet" in err for err in errors)


def test_view_refresh_required_after_five_minutes_escalates() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["last_observed_turn"] = "thread row selected but transcript still loading"
    ticket["observed_state"] = "view_refresh_required"
    ticket["breach_action"] = "dispatch_surface_failure_suspected"
    errors = checker.validate(ticket, now=at("2026-06-09T10:05:30+08:00"))
    assert errors == []


def test_view_refresh_required_after_five_minutes_must_not_wait_indefinitely() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["last_observed_turn"] = "thread row selected but transcript still loading"
    ticket["observed_state"] = "view_refresh_required"
    ticket["breach_action"] = "wait_for_expected_packet"
    errors = checker.validate(ticket, now=at("2026-06-09T10:05:30+08:00"))
    assert (
        "view_refresh_required after 5 minutes must escalate to dispatch_surface_failure_suspected; UI refresh is incident-scoped, not a dispatch-ticket breach action"
        in errors
    )


def test_dispatcher_owns_slo_closure_required() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["dispatcher_owns_slo_closure"] = False
    errors = checker.validate(ticket, now=at("2026-06-09T10:03:00+08:00"))
    assert "dispatcher_owns_slo_closure must be true" in errors


def test_live_runtime_requires_checkpoint_due() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["task_type"] = "live_runtime"
    ticket["expected_packet_due"] = "2026-06-09T12:00:00+08:00"
    ticket["checkpoint_due"] = None
    errors = checker.validate(ticket, now=at("2026-06-09T10:06:00+08:00"))
    assert "checkpoint_due is required for live_runtime" in errors


def test_completed_without_expected_packet_must_escalate() -> None:
    checker = load_checker()
    ticket = base_ticket()
    ticket["observed_state"] = "completed_without_expected_packet"
    ticket["last_observed_turn"] = "turn completed but expected packet absent"
    ticket["breach_action"] = "wait_for_expected_packet"
    errors = checker.validate(ticket, now=at("2026-06-09T10:06:00+08:00"))
    assert "completed_without_expected_packet must escalate through breach_action" in errors
