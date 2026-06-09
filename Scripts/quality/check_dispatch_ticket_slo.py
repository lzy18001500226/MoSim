#!/usr/bin/env python3
"""Validate PMO visible-thread dispatch ticket SLO state."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

BOARD_FIELDS = [
    "sent_at",
    "first_readback_due",
    "expected_packet_due",
    "last_observed_turn",
    "breach_action",
    "owner",
]

REQUIRED_FIELDS = [
    "ticket_version",
    "request_id",
    "task_type",
    "owner",
    "target_thread",
    "target_thread_id",
    "task_packet_path",
    "expected_return_path",
    "blocker_return_path",
    "sent_at",
    "first_readback_due",
    "second_readback_due_if_no_visible_turn",
    "failure_suspected_due",
    "first_agent_output_due",
    "dispatcher_next_check_due",
    "dispatcher_owns_slo_closure",
    "expected_packet_due",
    "last_observed_turn",
    "observed_state",
    "breach_action",
]

TASK_TYPE_PROFILES = {
    "source_static": {
        "expected_min_minutes": 10,
        "expected_max_minutes": 20,
        "checkpoint_required": False,
    },
    "control_plane": {
        "expected_min_minutes": 10,
        "expected_max_minutes": 20,
        "checkpoint_required": False,
    },
    "packet_contract_fix": {
        "expected_min_minutes": 10,
        "expected_max_minutes": 20,
        "checkpoint_required": False,
    },
    "dispatch_surface_diagnostic": {
        "expected_min_minutes": 2,
        "expected_max_minutes": 10,
        "checkpoint_required": False,
    },
    "recovery_validation": {
        "expected_min_minutes": 2,
        "expected_max_minutes": 10,
        "checkpoint_required": False,
    },
    "live_runtime": {
        "expected_min_minutes": 20,
        "expected_max_minutes": 180,
        "checkpoint_required": True,
        "checkpoint_max_minutes": 10,
    },
    "mworks_gui": {
        "expected_min_minutes": 20,
        "expected_max_minutes": 180,
        "checkpoint_required": True,
        "checkpoint_max_minutes": 10,
    },
    "manual_review": {
        "expected_min_minutes": 20,
        "expected_max_minutes": 240,
        "checkpoint_required": True,
        "checkpoint_max_minutes": 15,
    },
    "other": {
        "expected_min_minutes": 5,
        "expected_max_minutes": 60,
        "checkpoint_required": False,
    },
}

OBSERVED_STATES = {
    "no_readback_yet",
    "no_visible_turn",
    "visible_turn_in_progress",
    "visible_turn_stuck_no_agent_output",
    "view_refresh_required",
    "agent_output_seen",
    "checkpoint_packet_seen",
    "expected_return_packet_seen",
    "blocker_packet_seen",
    "completed_without_expected_packet",
    "approval_or_provider_surface",
    "context_compression_surface",
}

NO_VISIBLE_PROGRESS_STATES = {"no_readback_yet", "no_visible_turn"}
NO_AGENT_OUTPUT_STATES = {
    "no_readback_yet",
    "no_visible_turn",
    "visible_turn_in_progress",
    "visible_turn_stuck_no_agent_output",
}
PACKET_STATES = {"expected_return_packet_seen", "blocker_packet_seen"}
CHECKPOINT_OR_PROGRESS_STATES = {
    "agent_output_seen",
    "checkpoint_packet_seen",
    "expected_return_packet_seen",
    "blocker_packet_seen",
    "approval_or_provider_surface",
    "context_compression_surface",
}

BREACH_ACTIONS = {
    "none",
    "immediate_readback_pending",
    "recheck_within_2m",
    "run_view_refresh_sweep",
    "wait_for_expected_packet",
    "wait_for_checkpoint",
    "dispatch_surface_failure_suspected",
    "agent_output_missing_or_stuck_in_progress",
    "route_to_coagentops",
    "return_initial_blocker",
    "checkpoint_overdue",
    "expected_packet_overdue",
    "integrate_expected_packet",
    "manual_review_needed",
}

ESCALATION_ACTIONS = {
    "dispatch_surface_failure_suspected",
    "agent_output_missing_or_stuck_in_progress",
    "route_to_coagentops",
    "return_initial_blocker",
    "checkpoint_overdue",
    "expected_packet_overdue",
    "manual_review_needed",
}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - argparse display path.
        raise SystemExit(f"failed to parse JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("ticket root must be a JSON object")
    return payload


def _parse_dt(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty ISO timestamp")
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field} is not ISO-8601: {value}")
        return None


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _project_relative(path_text: str) -> bool:
    path = Path(path_text)
    if path.is_absolute():
        try:
            resolved = path.resolve()
            root = ROOT.resolve()
        except OSError:
            return False
        return resolved == root or root in resolved.parents
    return not any(part == ".." for part in path.parts)


def _check_required_fields(ticket: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not _present(ticket.get(field)):
            errors.append(f"missing required field: {field}")
    for field in BOARD_FIELDS:
        if not _present(ticket.get(field)):
            errors.append(f"missing PMO board field: {field}")
    return errors


def validate(ticket: dict[str, Any], *, now: datetime | None = None) -> list[str]:
    errors = _check_required_fields(ticket)

    task_type = ticket.get("task_type")
    if not isinstance(task_type, str) or task_type not in TASK_TYPE_PROFILES:
        errors.append(
            "task_type must be one of "
            + ", ".join(sorted(TASK_TYPE_PROFILES))
            + f"; got {task_type!r}"
        )
        profile = TASK_TYPE_PROFILES["other"]
    else:
        profile = TASK_TYPE_PROFILES[task_type]

    observed_state = ticket.get("observed_state")
    if observed_state not in OBSERVED_STATES:
        errors.append(
            "observed_state must be one of "
            + ", ".join(sorted(OBSERVED_STATES))
            + f"; got {observed_state!r}"
        )

    breach_action = ticket.get("breach_action")
    if breach_action not in BREACH_ACTIONS:
        errors.append(
            "breach_action must be one of "
            + ", ".join(sorted(BREACH_ACTIONS))
            + f"; got {breach_action!r}"
        )

    for field in ["task_packet_path", "expected_return_path", "blocker_return_path"]:
        value = ticket.get(field)
        if isinstance(value, str) and value.strip() and not _project_relative(value):
            errors.append(f"{field} must stay inside the project: {value}")

    sent_at = _parse_dt(ticket.get("sent_at"), "sent_at", errors)
    first_due = _parse_dt(ticket.get("first_readback_due"), "first_readback_due", errors)
    second_due = _parse_dt(
        ticket.get("second_readback_due_if_no_visible_turn"),
        "second_readback_due_if_no_visible_turn",
        errors,
    )
    failure_due = _parse_dt(ticket.get("failure_suspected_due"), "failure_suspected_due", errors)
    first_agent_output_due = _parse_dt(
        ticket.get("first_agent_output_due"), "first_agent_output_due", errors
    )
    dispatcher_next_check_due = _parse_dt(
        ticket.get("dispatcher_next_check_due"), "dispatcher_next_check_due", errors
    )
    expected_due = _parse_dt(ticket.get("expected_packet_due"), "expected_packet_due", errors)

    checkpoint_due = None
    if ticket.get("checkpoint_due") is not None:
        checkpoint_due = _parse_dt(ticket.get("checkpoint_due"), "checkpoint_due", errors)

    if sent_at and first_due:
        if first_due < sent_at:
            errors.append("first_readback_due must not be before sent_at")
        if first_due - sent_at > timedelta(seconds=60):
            errors.append("first_readback_due must be within 60 seconds of sent_at")

    if sent_at and second_due:
        if second_due < sent_at:
            errors.append("second_readback_due_if_no_visible_turn must not be before sent_at")
        if second_due - sent_at > timedelta(minutes=2):
            errors.append("second_readback_due_if_no_visible_turn must be within 2 minutes of sent_at")

    if sent_at and failure_due:
        if failure_due < sent_at:
            errors.append("failure_suspected_due must not be before sent_at")
        if failure_due - sent_at > timedelta(minutes=5):
            errors.append("failure_suspected_due must be within 5 minutes of sent_at")

    if sent_at and first_agent_output_due:
        if first_agent_output_due < sent_at:
            errors.append("first_agent_output_due must not be before sent_at")
        if first_agent_output_due - sent_at > timedelta(minutes=5):
            errors.append("first_agent_output_due must be within 5 minutes of sent_at")
        if failure_due and first_agent_output_due > failure_due:
            errors.append("first_agent_output_due must not be after failure_suspected_due")

    if sent_at and dispatcher_next_check_due:
        if dispatcher_next_check_due < sent_at:
            errors.append("dispatcher_next_check_due must not be before sent_at")

    if sent_at and expected_due:
        expected_delta = expected_due - sent_at
        min_delta = timedelta(minutes=profile["expected_min_minutes"])
        max_delta = timedelta(minutes=profile["expected_max_minutes"])
        if expected_delta < min_delta or expected_delta > max_delta:
            errors.append(
                f"expected_packet_due for {task_type} must be between "
                f"{profile['expected_min_minutes']} and {profile['expected_max_minutes']} minutes after sent_at"
            )

    if profile.get("checkpoint_required"):
        if checkpoint_due is None:
            errors.append(f"checkpoint_due is required for {task_type}")
        elif sent_at:
            checkpoint_delta = checkpoint_due - sent_at
            if checkpoint_delta < timedelta(0):
                errors.append("checkpoint_due must not be before sent_at")
            if checkpoint_delta > timedelta(minutes=profile["checkpoint_max_minutes"]):
                errors.append(
                    f"checkpoint_due for {task_type} must be within "
                    f"{profile['checkpoint_max_minutes']} minutes of sent_at"
                )
            if expected_due and checkpoint_due > expected_due:
                errors.append("checkpoint_due must not be after expected_packet_due")

    is_template = ticket.get("template_type") == "visible_thread_dispatch_ticket"
    if ticket.get("dispatcher_owns_slo_closure") is not True:
        errors.append("dispatcher_owns_slo_closure must be true")

    if not is_template:
        check_now = now or datetime.now(tz=sent_at.tzinfo if sent_at and sent_at.tzinfo else None)
        if (
            failure_due
            and check_now >= failure_due
            and observed_state in NO_AGENT_OUTPUT_STATES
            and breach_action != "dispatch_surface_failure_suspected"
        ):
            errors.append(
                "after 5 minutes with no visible turn/agent output/packet, breach_action must be dispatch_surface_failure_suspected"
            )
        if (
            failure_due
            and check_now >= failure_due
            and observed_state == "view_refresh_required"
            and breach_action not in {"run_view_refresh_sweep", "dispatch_surface_failure_suspected"}
        ):
            errors.append(
                "view_refresh_required after 5 minutes must run a bounded refresh sweep or escalate to dispatch_surface_failure_suspected"
            )
        if (
            first_agent_output_due
            and check_now >= first_agent_output_due
            and observed_state in {"visible_turn_in_progress", "visible_turn_stuck_no_agent_output"}
            and breach_action not in ESCALATION_ACTIONS
        ):
            errors.append(
                "after first_agent_output_due with visible turn but no agent output/packet, breach_action must escalate"
            )
        if (
            expected_due
            and check_now >= expected_due
            and observed_state not in PACKET_STATES
            and breach_action not in ESCALATION_ACTIONS
        ):
            errors.append("after expected_packet_due without packet, breach_action must escalate")
        if (
            checkpoint_due
            and check_now >= checkpoint_due
            and observed_state not in CHECKPOINT_OR_PROGRESS_STATES
            and breach_action not in ESCALATION_ACTIONS
        ):
            errors.append("after checkpoint_due without turn/output/checkpoint/packet, breach_action must escalate")

    if observed_state == "completed_without_expected_packet" and breach_action not in {
        "expected_packet_overdue",
        "return_initial_blocker",
        "route_to_coagentops",
    }:
        errors.append("completed_without_expected_packet must escalate through breach_action")

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticket", type=Path)
    parser.add_argument(
        "--now",
        help="ISO timestamp used for SLO breach evaluation in tests or patrol replay.",
    )
    parser.add_argument("--json-output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ticket_path = args.ticket if args.ticket.is_absolute() else ROOT / args.ticket
    ticket = _load_json(ticket_path)
    now = None
    if args.now:
        now = datetime.fromisoformat(args.now.replace("Z", "+00:00"))
    errors = validate(ticket, now=now)
    result = {
        "ok": not errors,
        "ticket": str(args.ticket),
        "errors": errors,
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
