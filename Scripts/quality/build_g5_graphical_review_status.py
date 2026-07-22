#!/usr/bin/env python3
"""Build the evidence-backed progress view for current G5 reviews only.

Packets captured before the 2026-07-22 graphical-model normalization are
preserved under the sibling historical archive. They are deliberately not
read here: their target hashes describe the pre-normalization files and must
not be promoted as current layout-review evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from check_g5_graphical_review_packet import ROOT, read_json, validate_review_packet


QUEUE_PATH = (
    ROOT
    / "Results"
    / "control_platform"
    / "g5_graphical_structure_review_20260722"
    / "G5_GRAPHICAL_REVIEW_QUEUE.json"
)
CURRENT_REVIEW_ROOT = QUEUE_PATH.parent / "reviews"
HISTORICAL_REVIEW_ROOT = QUEUE_PATH.parent / "historical_reviews_pre_normalization_20260722"
DEFAULT_OUTPUT = QUEUE_PATH.parent / "G5_GRAPHICAL_REVIEW_STATUS.json"


class StatusError(ValueError):
    """Raised when G5 packet state cannot be reconciled safely."""


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise StatusError(f"Path escapes project root: {path}") from exc


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def packet_paths() -> list[Path]:
    if not CURRENT_REVIEW_ROOT.is_dir():
        return []
    return sorted(CURRENT_REVIEW_ROOT.rglob("G5_REVIEW_PACKET.json"))


def build_status() -> dict[str, Any]:
    queue = read_json(QUEUE_PATH)
    if queue.get("schema") != "mosim.g5_graphical_review_queue.v1":
        raise StatusError("G5 review queue schema is invalid")
    rows = queue.get("schemes")
    if not isinstance(rows, list) or len(rows) != 49:
        raise StatusError("G5 review queue must contain exactly 49 schemes")
    planned_by_id = {
        str(row.get("scheme_id")): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("scheme_id"), str)
    }
    pending_ids = {
        scheme_id
        for scheme_id, row in planned_by_id.items()
        if row.get("review_disposition") == "pending_live_internal_graphical_review"
    }

    reviews: list[dict[str, Any]] = []
    seen: set[str] = set()
    errors: list[str] = []
    for path in packet_paths():
        packet = read_json(path)
        packet_errors = validate_review_packet(packet, queue)
        if packet_errors:
            errors.extend(f"{repo_path(path)}: {error}" for error in packet_errors)
            continue
        scheme_id = str(packet["scheme_id"])
        if scheme_id not in pending_ids:
            errors.append(f"{repo_path(path)}: packet targets non-pending scheme {scheme_id}")
            continue
        if scheme_id in seen:
            errors.append(f"duplicate G5 review packet for {scheme_id}")
            continue
        seen.add(scheme_id)
        reviews.append(
            {
                "scheme_id": scheme_id,
                "category": planned_by_id[scheme_id].get("category"),
                "verdict": packet.get("verdict"),
                "packet": repo_path(path),
                "next_action": packet.get("next_action"),
            }
        )
    if errors:
        raise StatusError("; ".join(errors))

    reviews.sort(key=lambda item: item["scheme_id"])
    reviewed_ids = {item["scheme_id"] for item in reviews}
    by_category: dict[str, dict[str, Any]] = {}
    category_rows: dict[str, list[str]] = defaultdict(list)
    for scheme_id in sorted(pending_ids):
        category_rows[str(planned_by_id[scheme_id].get("category"))].append(scheme_id)
    for category, scheme_ids in sorted(category_rows.items()):
        category_reviews = [item for item in reviews if item["category"] == category]
        by_category[category] = {
            "candidate_count": len(scheme_ids),
            "reviewed_count": len(category_reviews),
            "pending_scheme_ids": [scheme_id for scheme_id in scheme_ids if scheme_id not in reviewed_ids],
            "verdict_counts": dict(sorted(Counter(str(item["verdict"]) for item in category_reviews).items())),
        }

    non_live = [
        {
            "scheme_id": scheme_id,
            "review_disposition": row.get("review_disposition"),
            "blocker_code": row.get("blocker_code"),
        }
        for scheme_id, row in sorted(planned_by_id.items())
        if scheme_id not in pending_ids
    ]
    return {
        "schema": "mosim.g5_graphical_review_status.v1",
        "scope": "Evidence-backed current G5 layout-review status only. It excludes pre-normalization historical packets and does not promote any route to simulation, code generation, runtime, or report performance acceptance.",
        "queue": repo_path(QUEUE_PATH),
        "historical_packet_archive": {
            "path": repo_path(HISTORICAL_REVIEW_ROOT),
            "excluded_from_current_status": True,
            "reason": "Packets retain pre-normalization model hashes and are trace-back records only, not current G5 review evidence.",
        },
        "summary": {
            "top_level_scheme_count": 49,
            "live_review_candidate_count": len(pending_ids),
            "reviewed_count": len(reviews),
            "pending_count": len(pending_ids - reviewed_ids),
            "verdict_counts": dict(sorted(Counter(str(item["verdict"]) for item in reviews).items())),
        },
        "families": by_category,
        "reviewed": reviews,
        "non_live_routes": non_live,
    }


def validate_status(status: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if status.get("schema") != "mosim.g5_graphical_review_status.v1":
        errors.append("status schema is invalid")
        return errors
    archive = status.get("historical_packet_archive")
    if not isinstance(archive, dict) or archive.get("excluded_from_current_status") is not True:
        errors.append("historical packet archive must be explicitly excluded from current status")
    summary = status.get("summary")
    if not isinstance(summary, dict):
        errors.append("status summary is missing")
        return errors
    if summary.get("top_level_scheme_count") != 49:
        errors.append("status must retain the 49-scheme boundary")
    if summary.get("live_review_candidate_count") != 46:
        errors.append("status must retain 46 live review candidates")
    reviewed = status.get("reviewed")
    if not isinstance(reviewed, list):
        errors.append("reviewed list is missing")
        return errors
    reviewed_ids = [str(item.get("scheme_id")) for item in reviewed if isinstance(item, dict)]
    if len(reviewed_ids) != len(set(reviewed_ids)):
        errors.append("reviewed scheme IDs must be unique")
    if summary.get("reviewed_count") != len(reviewed_ids):
        errors.append("summary.reviewed_count does not match reviewed rows")
    if summary.get("pending_count") != 46 - len(reviewed_ids):
        errors.append("summary.pending_count does not match reviewed rows")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="fail if the status file differs from current G5 packets")
    args = parser.parse_args(argv)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    try:
        expected = build_status()
        errors = validate_status(expected)
        if args.check:
            if not output.is_file():
                errors.append(f"status file is missing: {output}")
            elif read_json(output) != expected:
                errors.append("on-disk status differs from G5 packets and queue")
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(canonical_json(expected), encoding="utf-8", newline="\n")
    except Exception as exc:
        errors = [str(exc)]
    print(json.dumps({"ok": not errors, "status": str(output), "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
