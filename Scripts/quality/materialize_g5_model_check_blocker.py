#!/usr/bin/env python3
"""Materialize one terminal G5 model-check blocker from an existing live log."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from current_model_entry_map_lib import model_topology_sha256

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "Results/control_platform/g5_graphical_structure_review_20260722/G5_GRAPHICAL_REVIEW_QUEUE.json"
REVIEW_ROOT = QUEUE_PATH.parent / "reviews"
OBSERVATION_KEYS = (
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def queue_row(queue: dict[str, Any], scheme_id: str) -> dict[str, Any]:
    for row in queue.get("schemes", []):
        if isinstance(row, dict) and row.get("scheme_id") == scheme_id:
            return row
    raise ValueError(f"unknown G5 scheme: {scheme_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scheme-id", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--shared-blocker-id")
    parser.add_argument(
        "--screenshot",
        type=Path,
        required=True,
        help="Project-relative native MWORKS window PNG for the failed check.",
    )
    parser.add_argument(
        "--capture-manifest",
        type=Path,
        required=True,
        help="Capture manifest paired with --screenshot.",
    )
    parser.add_argument(
        "--screenshot-observation",
        default="",
        help="Short reviewer observation for the failed native window capture.",
    )
    args = parser.parse_args()

    queue = read_json(QUEUE_PATH)
    row = queue_row(queue, args.scheme_id)
    target = row.get("review_target")
    if row.get("review_disposition") != "pending_live_internal_graphical_review" or not isinstance(target, dict):
        raise ValueError(f"{args.scheme_id} is not a current live G5 target")

    review_dir = REVIEW_ROOT / args.scheme_id
    model_check_path = review_dir / "logs/model_check.json"
    model_check = read_json(model_check_path)
    model_file = ROOT / target["model_file"]
    current_sha = sha256(model_file)
    current_topology_sha = model_topology_sha256(model_file)
    if model_check.get("status") != "failed":
        raise ValueError("terminal model_check blocker requires status=failed")
    if model_check.get("model_class") != target.get("model_class"):
        raise ValueError("model-check class does not match frozen G5 target")
    if current_sha != target.get("model_sha256") or model_check.get("model_sha256_after") != current_sha:
        raise ValueError("model-check log or queue does not match the current model source")
    if (
        current_topology_sha != target.get("model_topology_sha256")
        or model_check.get("model_topology_sha256_after") != current_topology_sha
    ):
        raise ValueError("model-check log or queue does not match the current model topology")

    screenshot_refs: list[str] = []
    capture_manifest_ref = ""
    screenshot_observation = args.screenshot_observation.strip()
    screenshot = (ROOT / args.screenshot).resolve()
    capture_manifest = (ROOT / args.capture_manifest).resolve()
    if not screenshot.is_file() or not capture_manifest.is_file():
        raise ValueError("failed-check screenshot and capture manifest must exist")
    captures_raw = json.loads(capture_manifest.read_text(encoding="utf-8-sig"))
    captures = captures_raw if isinstance(captures_raw, list) else [captures_raw]
    matching_capture = next(
        (
            item
            for item in captures
            if isinstance(item, dict)
            and Path(str(item.get("path") or item.get("output_png") or "")).name == screenshot.name
            and item.get("capture_width") is not None
            and item.get("capture_height") is not None
        ),
        None,
    )
    if not isinstance(matching_capture, dict):
        raise ValueError("failed-check screenshot is absent from a valid capture manifest row")
    screenshot_refs = [relative(screenshot)]
    capture_manifest_ref = relative(capture_manifest)

    last_errors = model_check.get("last_errors")
    packet: dict[str, Any] = {
        "schema": "mosim.g5_graphical_review_packet.v1",
        "scope": "Terminal G5 model-check blocker. No readable graphical-layout, simulation, code-generation, runtime, or closed-loop claim is made.",
        "reviewed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scheme_id": args.scheme_id,
        "review_target": {
            "model_file": target["model_file"],
            "model_class": target["model_class"],
            "model_sha256": current_sha,
            "model_topology_sha256": current_topology_sha,
        },
        "evidence_capture_target": {
            "model_file": target["model_file"],
            "model_class": target["model_class"],
            "model_sha256": current_sha,
            "model_topology_sha256": current_topology_sha,
        },
        "live_mworks": {
            "live_mworks_touched": True,
            "will_not_click_activation_login": True,
            "model_check": {
                "status": "failed",
                "model_name": target["model_class"],
                "log": relative(model_check_path),
                "last_errors": last_errors if isinstance(last_errors, list) else [],
            },
        },
        "evidence": {
            "model_check_log": relative(model_check_path),
            "mworks_phase_screenshots": screenshot_refs,
        },
        "layout_observations": {key: False for key in OBSERVATION_KEYS},
        "verdict": "blocked",
        "terminal_status": "model_check_failed",
        "blocker": {
            "code": "model_check_failed",
            "reason": args.reason,
        },
        "claim_boundary": {
            "layout": "model_check_failed",
            "simulation": "not_run",
            "controller_behavior": "not_claimed",
            "code_generation": "not_run",
            "runtime": "not_run",
        },
    }
    if args.shared_blocker_id:
        packet["blocker"]["shared_blocker_id"] = args.shared_blocker_id
    packet["evidence"]["screenshot_manifest"] = capture_manifest_ref
    packet["evidence"]["native_window_observation"] = screenshot_observation or (
        "Native MWORKS window captured the failed formal target and its check-model output."
    )

    output = review_dir / "G5_REVIEW_PACKET.json"
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "packet": relative(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
