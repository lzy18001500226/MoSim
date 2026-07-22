#!/usr/bin/env python3
"""Validate one evidence-backed G5 MWORKS graphical-structure review packet.

G5 records a visual/topological verdict for the actual internal control-law
model selected by the frozen queue.  A passing ``check_model`` is useful
context, but never substitutes for readable layout evidence or a simulation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = (
    ROOT
    / "Results"
    / "control_platform"
    / "g5_graphical_structure_review_20260722"
    / "G5_GRAPHICAL_REVIEW_QUEUE.json"
)
SCHEMA = "mosim.g5_graphical_review_packet.v1"
ALLOWED_VERDICTS = {
    "layout_passed",
    "needs_relayout",
    "wrapper_only",
    "missing_graphical_counterpart",
    "blocked",
}
REQUIRED_LAYOUT_OBSERVATIONS = (
    "is_internal_control_law",
    "signal_flow_readable",
    "functional_groups_readable",
    "wires_traceable",
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def as_repo_path(value: Any) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = ROOT / value
    try:
        path.resolve().relative_to(ROOT)
    except ValueError:
        return None
    return path


def queue_row(queue: dict[str, Any], scheme_id: str) -> dict[str, Any] | None:
    rows = queue.get("schemes")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("scheme_id") == scheme_id:
            return row
    return None


def validate_review_packet(packet: dict[str, Any], queue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("schema") != SCHEMA:
        errors.append(f"schema must equal {SCHEMA}")

    scheme_id = packet.get("scheme_id")
    if not isinstance(scheme_id, str) or not scheme_id:
        errors.append("scheme_id is required")
        return errors
    planned = queue_row(queue, scheme_id)
    if planned is None:
        errors.append(f"scheme_id is absent from frozen G5 queue: {scheme_id}")
        return errors

    target = packet.get("review_target")
    planned_target = planned.get("review_target")
    if not isinstance(target, dict) or not isinstance(planned_target, dict):
        errors.append("review_target must match a concrete G5 queue target")
    else:
        for key in ("model_file", "model_class", "model_sha256"):
            if target.get(key) != planned_target.get(key):
                errors.append(f"review_target.{key} differs from frozen G5 queue")
        target_path = as_repo_path(target.get("model_file"))
        if target_path is None or not target_path.is_file():
            errors.append("review_target.model_file must be an existing project file")
        elif target.get("model_sha256") != sha256_file(target_path):
            errors.append("review_target.model_sha256 no longer matches its model file")

    verdict = packet.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        errors.append(f"verdict must be one of {sorted(ALLOWED_VERDICTS)}")

    observations = packet.get("layout_observations")
    if not isinstance(observations, dict):
        errors.append("layout_observations must be an object")
    else:
        for key in REQUIRED_LAYOUT_OBSERVATIONS:
            if not isinstance(observations.get(key), bool):
                errors.append(f"layout_observations.{key} must be boolean")

    live = packet.get("live_mworks")
    if not isinstance(live, dict):
        errors.append("live_mworks must be an object")
    else:
        if live.get("live_mworks_touched") is not True:
            errors.append("live_mworks.live_mworks_touched must be true for a live G5 review")
        if live.get("will_not_click_activation_login") is not True:
            errors.append("live_mworks.will_not_click_activation_login must be true")
        model_check = live.get("model_check")
        if not isinstance(model_check, dict):
            errors.append("live_mworks.model_check must be an object")
        elif verdict in {"layout_passed", "needs_relayout"}:
            if model_check.get("status") != "passed":
                errors.append("layout verdict requires a passed MWORKS check_model result")
            if isinstance(target, dict) and model_check.get("model_name") != target.get("model_class"):
                errors.append("model_check.model_name must match review_target.model_class")

    evidence = packet.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be an object")
    else:
        screenshots = evidence.get("mworks_phase_screenshots")
        if not isinstance(screenshots, list) or not screenshots:
            errors.append("evidence.mworks_phase_screenshots must contain native window evidence")
        else:
            for item in screenshots:
                path = as_repo_path(item)
                if path is None or not path.is_file():
                    errors.append(f"missing screenshot evidence: {item}")
        manifest = as_repo_path(evidence.get("screenshot_manifest"))
        if manifest is None or not manifest.is_file():
            errors.append("evidence.screenshot_manifest must be an existing project file")

    claim_boundary = packet.get("claim_boundary")
    if not isinstance(claim_boundary, dict):
        errors.append("claim_boundary must be an object")
    else:
        if claim_boundary.get("simulation") != "not_run":
            errors.append("G5 packet may not claim a simulation result")
        if claim_boundary.get("controller_behavior") != "not_claimed":
            errors.append("G5 packet may not claim controller behavior")
        if claim_boundary.get("code_generation") != "not_run":
            errors.append("G5 packet may not claim code generation")

    if isinstance(observations, dict):
        readable = all(observations.get(key) is True for key in REQUIRED_LAYOUT_OBSERVATIONS)
        if verdict == "layout_passed" and not readable:
            errors.append("layout_passed requires every required layout observation to be true")
        if verdict == "needs_relayout":
            if observations.get("is_internal_control_law") is not True:
                errors.append("needs_relayout requires an actual internal control-law target")
            if readable:
                errors.append("needs_relayout requires at least one readability observation to be false")
    if verdict == "blocked":
        blocker = packet.get("blocker")
        if not isinstance(blocker, dict) or not blocker.get("code") or not blocker.get("reason"):
            errors.append("blocked verdict requires blocker.code and blocker.reason")
    if verdict in {"needs_relayout", "missing_graphical_counterpart", "wrapper_only"}:
        repair = packet.get("next_action")
        if not isinstance(repair, str) or not repair.strip():
            errors.append(f"{verdict} requires a concrete next_action")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--packet",
        type=Path,
        required=True,
        help="Current G5 packet below Results/control_platform/g5_graphical_structure_review_20260722/reviews/.",
    )
    parser.add_argument("--queue", type=Path, default=QUEUE_PATH)
    args = parser.parse_args(argv)

    packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
    queue_path = args.queue if args.queue.is_absolute() else ROOT / args.queue
    try:
        packet = read_json(packet_path)
        queue = read_json(queue_path)
        errors = validate_review_packet(packet, queue)
    except Exception as exc:
        errors = [str(exc)]
    print(json.dumps({"ok": not errors, "packet": str(packet_path), "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
