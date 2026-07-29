#!/usr/bin/env python3
"""Audit a ROS launch log for process crashes and planner semantic failures."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FATAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("roslaunch_process_died", re.compile(r"process has died \[pid .*?exit code\s+(-?\d+)", re.IGNORECASE)),
    ("assertion_failed", re.compile(r"\bAssertion [`'\"]", re.IGNORECASE)),
    ("eigen_assertion_failed", re.compile(r"Eigen::.*Assertion", re.IGNORECASE)),
    ("aborted", re.compile(r"\bAborted\b|SIGABRT|Signal sent by tkill", re.IGNORECASE)),
    ("segmentation_fault", re.compile(r"Segmentation fault|SIGSEGV", re.IGNORECASE)),
    ("uncaught_exception", re.compile(r"terminate called|std::exception|boost::exception", re.IGNORECASE)),
]

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
ROS_TIME_RE = re.compile(r"\[[0-9]+(?:\.[0-9]+)?,\s*([0-9]+(?:\.[0-9]+)?)\]")

SEMANTIC_PROFILES: dict[str, list[tuple[str, re.Pattern[str], bool]]] = {
    "none": [],
    "racer": [
        # RACER predicts a future inter-UAV conflict and immediately returns to
        # PLAN_TRAJ. The flight gate separately enforces actual separation and
        # trajectory freshness, so this event alone is diagnostic.
        ("racer_swarm_collision_prediction", re.compile(r"\bDrone\s+\d+\s+collide with drone\s+\d+\.", re.IGNORECASE), False),
        ("racer_acvrp_failed", re.compile(r"\bFail to solve ACVRP\.", re.IGNORECASE), True),
        # traj_server rejects stale/duplicate trajectory IDs. Treat this as a
        # blocker only through the independent trajectory-freshness gate.
        ("racer_out_of_order_bspline", re.compile(r"\bout of order bspline\.", re.IGNORECASE), False),
        ("racer_no_path_to_viewpoint", re.compile(r"\bNo path to next viewpoint\b", re.IGNORECASE), False),
        # RACER logs these two as ROS_ERROR inside a candidate pair-opt branch,
        # then immediately rejects that candidate and returns without changing
        # the active allocation. They are useful diagnostics, but not standalone
        # flight blockers unless a hard safety/trajectory gate also fails.
        ("racer_inconsistent_grid_path", re.compile(r"\bPath [12]\s+inconsistent\b", re.IGNORECASE), False),
        ("racer_larger_cost_after_reallocation", re.compile(r"\bLarger cost after reallocation\b", re.IGNORECASE), False),
        ("racer_collision_replan", re.compile(r"\bReplan:\s+collision detected\b", re.IGNORECASE), False),
    ],
    "swarm_formation": [
        # The upstream planner emits this while rejecting a candidate optimized
        # trajectory, then returns to REPLAN_TRAJ. Keep it as a diagnostic:
        # completed-target, clearance, separation, and emergency-stop gates
        # decide whether the recovered flight can be accepted.
        (
            "swarm_formation_optimized_trajectory_collision",
            re.compile(r"\boptimized trajectory collision\b", re.IGNORECASE),
            False,
        ),
        (
            "swarm_formation_emergency_stop",
            re.compile(r"\bEmergency stop!", re.IGNORECASE),
            True,
        ),
        (
            "swarm_formation_exec_traj_emergency_stop",
            re.compile(r"\[SAFETY\]:\s*from\s+EXEC_TRAJ\s+to\s+EMERGENCY_STOP\b", re.IGNORECASE),
            True,
        ),
    ],
}

RACER_PAIR_OPT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("attempt", re.compile(r":\s*Pair opt\s+\d+\s*&\s*\d+\s*$", re.IGNORECASE)),
    ("request_sent", re.compile(r"\bsend opt request to\b", re.IGNORECASE)),
    ("response_accepted", re.compile(r"\bget response 1\b", re.IGNORECASE)),
    ("response_rejected", re.compile(r"\bget response 2\b", re.IGNORECASE)),
    (
        "applied_receiver",
        re.compile(r"\bpair opt applied role=receiver\b", re.IGNORECASE),
    ),
    (
        "applied_initiator",
        re.compile(r"\bpair opt applied role=initiator\b", re.IGNORECASE),
    ),
    (
        "ownership_changed",
        re.compile(r"\bpair opt applied role=initiator\b.*\bchanged=true\b", re.IGNORECASE),
    ),
    ("rejected_empty", re.compile(r"\breject pair opt\b.*\bempty allocation\b", re.IGNORECASE)),
    (
        "rejected_inconsistent",
        re.compile(r"\breject pair opt\b.*\binconsistent grid path\b", re.IGNORECASE),
    ),
    ("rejected_larger_cost", re.compile(r"\bLarger cost after reallocation\b", re.IGNORECASE)),
    ("acvrp_failed", re.compile(r"\bFail to solve ACVRP\.", re.IGNORECASE)),
    (
        "lkh_process_failed",
        re.compile(r"\b(?:Failed to start LKH3 process|LKH3 process failed)\b", re.IGNORECASE),
    ),
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        return {"_invalid_json": str(exc)}


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def strip_ansi(line: str) -> str:
    return ANSI_RE.sub("", line)


def compact_line(line: str, limit: int) -> str:
    line = strip_ansi(line.rstrip("\n"))
    if len(line) <= limit:
        return line
    return line[: limit - 3] + "..."


def extract_ros_time(line: str) -> float | None:
    match = ROS_TIME_RE.search(strip_ansi(line))
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def collect_events(
    lines: list[str],
    patterns: list[tuple[str, re.Pattern[str]]],
    *,
    context: int,
    line_limit: int,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        clean_line = strip_ansi(line)
        matched = [kind for kind, pattern in patterns if pattern.search(clean_line)]
        if not matched:
            continue
        start = max(0, index - context)
        end = min(len(lines), index + context + 1)
        events.append(
            {
                "line": index + 1,
                "ros_time_s": extract_ros_time(line),
                "kinds": matched,
                "text": compact_line(line, line_limit),
                "context": [compact_line(item, line_limit) for item in lines[start:end]],
            }
        )
    return events


def count_kinds(events: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        for kind in event["kinds"]:
            counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def build_racer_pair_opt_evidence(lines: list[str]) -> dict[str, Any]:
    counts = {kind: 0 for kind, _pattern in RACER_PAIR_OPT_PATTERNS}
    examples: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        clean_line = strip_ansi(line)
        matched = [kind for kind, pattern in RACER_PAIR_OPT_PATTERNS if pattern.search(clean_line)]
        if not matched:
            continue
        for kind in matched:
            counts[kind] += 1
        if len(examples) < 50:
            examples.append(
                {
                    "line": index + 1,
                    "ros_time_s": extract_ros_time(line),
                    "kinds": matched,
                    "text": compact_line(line, 500),
                }
            )

    if counts["attempt"] == 0:
        status = "disabled_or_not_exercised"
    elif counts["response_accepted"] == 0:
        status = "exercised_no_applied_reallocation"
    elif counts["applied_initiator"] == 0:
        status = "accepted_response_observed_ownership_change_uninstrumented"
    elif counts["ownership_changed"] == 0:
        status = "applied_no_observed_ownership_change"
    else:
        status = "applied_with_ownership_change"

    return {
        "status": status,
        "counts": counts,
        "successful_transaction_count": counts["response_accepted"],
        "ownership_change_transaction_count": counts["ownership_changed"],
        "examples": examples,
    }


def event_is_within_semantic_blocker_time(
    event: dict[str, Any],
    semantic_blocker_max_ros_time: float | None,
) -> bool:
    if semantic_blocker_max_ros_time is None:
        return True
    ros_time = event.get("ros_time_s")
    if not isinstance(ros_time, (int, float)):
        # Missing log time cannot be safely classified as post-mission cleanup.
        return True
    return float(ros_time) <= semantic_blocker_max_ros_time


def audit_log(
    log_path: Path,
    *,
    context: int,
    line_limit: int,
    missing_is_blocker: bool,
    planner_semantic_profile: str,
    semantic_blocker_max_ros_time: float | None,
) -> dict[str, Any]:
    if not log_path.exists():
        blockers = ["planner_runtime_log_missing"] if missing_is_blocker else []
        return {
            "schema": "mosim.sunray_ros1.roslaunch_runtime_log_audit.v1",
            "status": "blocked" if blockers else "not_checked",
            "log_path": str(log_path),
            "log_exists": False,
            "fatal_event_count": 0,
            "fatal_event_kinds": [],
            "blockers": blockers,
            "events": [],
        }

    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    events = collect_events(lines, FATAL_PATTERNS, context=context, line_limit=line_limit)
    semantic_config = SEMANTIC_PROFILES.get(planner_semantic_profile, [])
    semantic_patterns = [(kind, pattern) for kind, pattern, _blocker in semantic_config]
    semantic_blocker_kinds = {kind for kind, _pattern, blocker in semantic_config if blocker}
    semantic_events = collect_events(lines, semantic_patterns, context=context, line_limit=line_limit)
    racer_pair_opt = (
        build_racer_pair_opt_evidence(lines)
        if planner_semantic_profile == "racer"
        else None
    )

    fatal_kinds = sorted({kind for event in events for kind in event["kinds"]})
    blockers = []
    if events:
        blockers.append("planner_process_crashed")
        if any("assertion_failed" in event["kinds"] or "eigen_assertion_failed" in event["kinds"] for event in events):
            blockers.append("planner_assertion_failed")
        if any("aborted" in event["kinds"] for event in events):
            blockers.append("planner_aborted")

    semantic_counts = count_kinds(semantic_events)
    active_semantic_events = [
        event
        for event in semantic_events
        if event_is_within_semantic_blocker_time(event, semantic_blocker_max_ros_time)
    ]
    ignored_semantic_blocker_events = [
        event
        for event in semantic_events
        if not event_is_within_semantic_blocker_time(event, semantic_blocker_max_ros_time)
        and any(kind in semantic_blocker_kinds for kind in event["kinds"])
    ]
    active_semantic_counts = count_kinds(active_semantic_events)
    ignored_semantic_blocker_counts = count_kinds(ignored_semantic_blocker_events)
    semantic_blockers = [
        f"planner_semantic_{kind}"
        for kind in sorted(active_semantic_counts)
        if kind in semantic_blocker_kinds
    ]
    blockers.extend(semantic_blockers)

    return {
        "schema": "mosim.sunray_ros1.roslaunch_runtime_log_audit.v1",
        "status": "blocked" if blockers else "passed",
        "log_path": str(log_path),
        "log_exists": True,
        "line_count": len(lines),
        "fatal_event_count": len(events),
        "fatal_event_kinds": fatal_kinds,
        "fatal_event_counts": count_kinds(events),
        "planner_semantic_profile": planner_semantic_profile,
        "semantic_blocker_time_policy": (
            "blocker events after semantic_blocker_max_ros_time_s are retained as diagnostics only"
            if semantic_blocker_max_ros_time is not None
            else "all semantic blocker events are active"
        ),
        "semantic_blocker_max_ros_time_s": semantic_blocker_max_ros_time,
        "semantic_event_count": len(semantic_events),
        "semantic_event_counts": semantic_counts,
        "semantic_event_kinds": sorted(semantic_counts),
        "active_semantic_event_count": len(active_semantic_events),
        "active_semantic_event_counts": active_semantic_counts,
        "ignored_semantic_blocker_count": len(ignored_semantic_blocker_events),
        "ignored_semantic_blocker_counts": ignored_semantic_blocker_counts,
        "semantic_blockers": semantic_blockers,
        "racer_pair_opt": racer_pair_opt,
        "blockers": blockers,
        "events": events[:50],
        "semantic_events": semantic_events[:50],
        "ignored_semantic_blocker_events": ignored_semantic_blocker_events[:50],
    }


def merge_metrics(metrics_path: Path, audit: dict[str, Any], blocker_prefix: str) -> None:
    metrics = load_json(metrics_path)
    if not metrics:
        return

    audit_blockers = [f"{blocker_prefix}_{item}" if blocker_prefix else item for item in audit.get("blockers", [])]
    previous_audit_blockers = set((metrics.get("runtime_log_audit") or {}).get("blockers") or [])
    blockers = [item for item in list(metrics.get("blockers") or []) if item not in previous_audit_blockers]
    for blocker in audit_blockers:
        if blocker not in blockers:
            blockers.append(blocker)

    metrics["runtime_log_audit"] = {
        "status": audit.get("status"),
        "path": audit.get("output_path"),
        "log_path": audit.get("log_path"),
        "fatal_event_count": audit.get("fatal_event_count", 0),
        "fatal_event_kinds": audit.get("fatal_event_kinds", []),
        "fatal_event_counts": audit.get("fatal_event_counts", {}),
        "planner_semantic_profile": audit.get("planner_semantic_profile"),
        "semantic_blocker_time_policy": audit.get("semantic_blocker_time_policy"),
        "semantic_blocker_max_ros_time_s": audit.get("semantic_blocker_max_ros_time_s"),
        "semantic_event_count": audit.get("semantic_event_count", 0),
        "semantic_event_counts": audit.get("semantic_event_counts", {}),
        "semantic_event_kinds": audit.get("semantic_event_kinds", []),
        "active_semantic_event_count": audit.get("active_semantic_event_count", 0),
        "active_semantic_event_counts": audit.get("active_semantic_event_counts", {}),
        "ignored_semantic_blocker_count": audit.get("ignored_semantic_blocker_count", 0),
        "ignored_semantic_blocker_counts": audit.get("ignored_semantic_blocker_counts", {}),
        "semantic_blockers": [
            f"{blocker_prefix}_{item}" if blocker_prefix else item
            for item in audit.get("semantic_blockers", [])
        ],
        "racer_pair_opt": audit.get("racer_pair_opt"),
        "blockers": audit_blockers,
    }
    metrics["status"] = "blocked" if blockers else "passed"
    metrics["blockers"] = blockers
    dump_json(metrics_path, metrics)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--metrics-json", type=Path)
    parser.add_argument("--blocker-prefix", default="")
    parser.add_argument("--context", type=int, default=3)
    parser.add_argument("--line-limit", type=int, default=500)
    parser.add_argument("--missing-is-blocker", action="store_true")
    parser.add_argument("--planner-semantic-profile", choices=sorted(SEMANTIC_PROFILES), default="none")
    parser.add_argument("--semantic-blocker-max-ros-time", type=float)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = audit_log(
        args.log,
        context=max(0, args.context),
        line_limit=max(120, args.line_limit),
        missing_is_blocker=args.missing_is_blocker,
        planner_semantic_profile=args.planner_semantic_profile,
        semantic_blocker_max_ros_time=args.semantic_blocker_max_ros_time,
    )
    audit["output_path"] = str(args.output)
    dump_json(args.output, audit)
    if args.metrics_json:
        merge_metrics(args.metrics_json, audit, args.blocker_prefix)
    return 1 if audit.get("status") == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
