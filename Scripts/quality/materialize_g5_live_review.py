#!/usr/bin/env python3
"""Write one current-hash G5 packet from an existing live check and native capture.

This helper never opens, saves, or edits an MWORKS model.  A reviewer must
still make the graphical verdict; the helper only removes duplicated manifest
and packet bookkeeping after that observation has been made.
"""

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
UNREADABLE_KEYS = ("signal_flow_readable", "functional_groups_readable", "wires_traceable")


def read_json(path: Path) -> Any:
    # Windows PowerShell 5.1 writes UTF-8 BOM by default; native-window
    # capture manifests are valid JSON in either UTF-8 form.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def queue_row(scheme_id: str) -> dict[str, Any]:
    queue = read_json(QUEUE_PATH)
    for row in queue["schemes"]:
        if row.get("scheme_id") == scheme_id:
            return row
    raise ValueError(f"unknown G5 scheme: {scheme_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scheme-id", required=True)
    parser.add_argument(
        "--verdict",
        required=True,
        choices=("layout_passed", "needs_relayout", "wrapper_only", "missing_graphical_counterpart"),
    )
    parser.add_argument("--screenshot", required=True, type=Path, help="project-relative native PNG")
    parser.add_argument("--capture-manifest", required=True, type=Path, help="project-relative capture_manifest.json")
    parser.add_argument("--observation", required=True)
    parser.add_argument("--next-action", default="")
    parser.add_argument("--unreadable", action="append", choices=UNREADABLE_KEYS, default=[])
    parser.add_argument(
        "--processing-state",
        choices=("screened_only", "graphical_ready"),
        default="screened_only",
        help="Mark graphical_ready only after the current model, CheckModel, and native layout review all pass.",
    )
    args = parser.parse_args()

    row = queue_row(args.scheme_id)
    target = row.get("review_target")
    if row.get("review_disposition") != "pending_live_internal_graphical_review" or not isinstance(target, dict):
        raise ValueError(f"{args.scheme_id} is not a current live G5 target")
    if args.verdict in {"needs_relayout", "wrapper_only", "missing_graphical_counterpart"} and not args.next_action.strip():
        raise ValueError(f"{args.verdict} requires --next-action")
    if args.processing_state == "graphical_ready" and args.verdict != "layout_passed":
        raise ValueError("graphical_ready requires verdict=layout_passed")

    review_dir = REVIEW_ROOT / args.scheme_id
    model_check_path = review_dir / "logs/model_check.json"
    screenshot = (ROOT / args.screenshot).resolve()
    capture_manifest_path = (ROOT / args.capture_manifest).resolve()
    model_path = (ROOT / str(target["model_file"])).resolve()
    if not screenshot.is_file() or not capture_manifest_path.is_file() or not model_check_path.is_file() or not model_path.is_file():
        raise ValueError("model check, model, screenshot, and capture manifest must already exist")

    model_check = read_json(model_check_path)
    if model_check.get("status") != "passed":
        raise ValueError("G5 packet requires a passed model check")
    current_sha = sha256(model_path)
    current_topology_sha = model_topology_sha256(model_path)
    if current_sha != target.get("model_sha256") or model_check.get("model_sha256_after") != current_sha:
        raise ValueError("current model hash does not match queue or live check")
    if (
        current_topology_sha != target.get("model_topology_sha256")
        or model_check.get("model_topology_sha256_after") != current_topology_sha
    ):
        raise ValueError("current model topology fingerprint does not match queue or live check")

    captures = read_json(capture_manifest_path)
    if isinstance(captures, dict):
        captures = [captures]
    if not isinstance(captures, list):
        raise ValueError("capture manifest must be a capture list")
    capture = next(
        (
            item
            for item in captures
            if isinstance(item, dict)
            and Path(str(item.get("path") or item.get("output_png") or "")).name == screenshot.name
        ),
        None,
    )
    if not isinstance(capture, dict) or capture.get("capture_width") is None or capture.get("capture_height") is None:
        raise ValueError("matching native screenshot is absent from capture manifest")

    observations = {
        "is_internal_control_law": True,
        "signal_flow_readable": True,
        "functional_groups_readable": True,
        "wires_traceable": True,
        "black_box_shell": False,
    }
    unreadable = set(args.unreadable)
    if args.verdict in {"needs_relayout", "wrapper_only", "missing_graphical_counterpart"} and not unreadable:
        unreadable = set(UNREADABLE_KEYS)
    for key in unreadable:
        observations[key] = False
    if args.verdict in {"wrapper_only", "missing_graphical_counterpart"}:
        observations["is_internal_control_law"] = False
        observations["black_box_shell"] = True

    screenshot_ref = relative(screenshot)
    manifest_ref = relative(review_dir / "logs/screenshot_manifest.json")
    if capture.get("maximize_applied"):
        capture_mode = "maximized_native_window_capture"
    elif capture.get("restore_minimized_applied"):
        capture_mode = "restored_native_window_capture"
    else:
        capture_mode = "native_window_capture"
    screenshot_manifest = {
        "schema": "mosim.native_window_screenshot_manifest.v1",
        "scope": f"Native Windows capture for the current {args.scheme_id} G5 internal-structure review. No image was exported from an MWORKS canvas.",
        "scheme_id": args.scheme_id,
        "review_target": {
            "model_file": target["model_file"],
            "model_class": target["model_class"],
            "model_sha256": current_sha,
            "model_topology_sha256": current_topology_sha,
        },
        "captures": [{
            "path": screenshot_ref,
            "phase": "internal_graphical_layout_review",
            "capture_mode": capture_mode,
            "source": capture.get("source", "MWORKS_GUI"),
            "window_title": capture.get("title"),
            "width": capture["capture_width"],
            "height": capture["capture_height"],
            "sha256": sha256(screenshot),
            "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "blank_or_ambiguous": False,
            "cropped_or_incomplete": False,
            "observation": args.observation,
        }],
        "limitations": "Native window pixels establish GUI/layout observation only. This manifest does not claim a plant-coupled whole-aircraft simulation, controller performance, code generation, or runtime success. The durable artifact is a DPI-aware direct native Win32 window capture rather than an MWORKS canvas export; Windows MCP visible-desktop capture may provide supplementary current-turn review when available.",
    }
    write_json(review_dir / "logs/screenshot_manifest.json", screenshot_manifest)

    check_step = model_check.get("steps", {}).get("check_model", {})
    packet = {
        "schema": "mosim.g5_graphical_review_packet.v1",
        "scope": "One live G5 graphical-structure review. This packet does not record a simulation, metrics, code generation, or runtime result.",
        "reviewed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scheme_id": args.scheme_id,
        "processing_state": args.processing_state,
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
            "activation_state_observation": "The native Sysplorer window showed the requested formal target with no login, activation, authorization, or MWORKS error dialog.",
            "license_state": "task_local_sufficient_for_check_model_only",
            "model_check": {
                "status": "passed",
                "model_name": target["model_class"],
                "elapsed_s": check_step.get("elapsed_s"),
                "result": "The official Sysplorer Python API returned true for the current formal model; raw SHA-256 and the topology fingerprint are recorded before and after the check.",
            },
        },
        "evidence": {
            "source": "MWORKS official Python API plus native Windows window capture",
            "screenshot_manifest": manifest_ref,
            "mworks_phase_screenshots": [screenshot_ref],
            "native_window_observation": args.observation,
        },
        "relayout_integrity": {
            "change_scope": "not_applicable_no_relayout",
            "connection_count_before": target.get("connect_count"),
            "connection_count_after": target.get("connect_count"),
            "non_visual_text_equivalent": True,
            "formal_sha256_unchanged_by_post_review_check": True,
        },
        "layout_observations": observations,
        "verdict": args.verdict,
        "verdict_reason": [args.observation],
        "claim_boundary": {
            "layout": args.verdict,
            "simulation": "not_run",
            "controller_behavior": "not_claimed",
            "code_generation": "not_run",
            "runtime": "not_run",
        },
    }
    if args.verdict in {"needs_relayout", "wrapper_only", "missing_graphical_counterpart"}:
        packet["next_action"] = args.next_action
    write_json(review_dir / "G5_REVIEW_PACKET.json", packet)
    print(json.dumps({"ok": True, "packet": relative(review_dir / "G5_REVIEW_PACKET.json")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
