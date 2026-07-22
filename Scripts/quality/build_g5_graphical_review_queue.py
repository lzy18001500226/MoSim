#!/usr/bin/env python3
"""Build and validate the static G5 graphical-review queue.

G4 maps 49 top-level schemes to a current model, explicit implementation
blocker, or the ROS/PX4 runtime baseline.  G5 must not turn that mapping into
a claim that a whole-aircraft wrapper is a readable controller diagram.  This
generator names the actual review target, records wrapper risks, and produces
small family batches for authorized MWORKS review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from current_model_entry_map_lib import ROOT, model_declaration


MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
CONTROLLER_BLOCKS_ROOT = ROOT / "Models" / "QuadrotorControllerBlocks"
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "control_platform"
    / "g5_graphical_structure_review_20260722"
    / "G5_GRAPHICAL_REVIEW_QUEUE.json"
)

FAMILY_ORDER = [
    "pid_family",
    "classic_robust",
    "sliding_mode",
    "optimization",
    "geometric_flatness",
    "learning",
    "fixed_integrated",
]
FAMILY_LABELS = {
    "pid_family": "PID",
    "classic_robust": "经典鲁棒",
    "sliding_mode": "滑模",
    "optimization": "优化",
    "geometric_flatness": "几何平坦",
    "learning": "学习",
    "fixed_integrated": "固定集成链",
}


class QueueError(ValueError):
    """Raised when the frozen G4 mapping cannot safely form a G5 queue."""


def write_utf8_lf(path: Path, text: str) -> None:
    """Write generated artifacts with LF regardless of the host platform."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise QueueError(f"JSON object required: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise QueueError(f"Path escapes project root: {path}") from exc


def static_indicators(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise QueueError(f"Review target is missing: {path}")
    text = path.read_text(encoding="utf-8")
    within, name = model_declaration(text)
    model_class = f"{within}.{name}" if within else name
    return {
        "source_kind": "static_source_preflight_only",
        "model_file": repo_path(path),
        "model_class": model_class,
        "model_sha256": sha256_file(path),
        "placement_count": len(re.findall(r"\bPlacement\s*\(", text)),
        "connect_count": len(re.findall(r"\bconnect\s*\(", text)),
        "line_annotation_count": len(re.findall(r"\bLine\s*\(", text)),
        "mworks_marker_count": text.count("__MWORKS"),
        "inport_count": len(re.findall(r"\.Port\.Inport\b", text)),
        "outport_count": len(re.findall(r"\.Port\.Outport\b", text)),
        "claim_boundary": "Static indicators select a review target only; they do not prove readable GUI layout, check_model, simulation, or controller behavior.",
    }


def fixed_internal_target(source_wrapper_path: Path) -> dict[str, Any]:
    text = source_wrapper_path.read_text(encoding="utf-8")
    match = re.search(r"^\s*([A-Za-z_]\w*)\s+controller3_2\b", text, re.MULTILINE)
    if not match:
        raise QueueError(f"Cannot locate controller3_2 inside fixed source wrapper: {source_wrapper_path}")
    controller_name = match.group(1)
    controller_path = CONTROLLER_BLOCKS_ROOT / f"{controller_name}.mo"
    indicators = static_indicators(controller_path)
    if indicators["model_class"] != controller_name:
        raise QueueError(
            f"Fixed source wrapper {source_wrapper_path} references {controller_name}, but target declares {indicators['model_class']}"
        )
    return {
        "review_target_kind": "internal_controller_referenced_by_whole_aircraft_wrapper",
        "review_target": indicators,
        "wrapper_risk": "The mapped entry is a formal alias of a whole-aircraft closed-loop wrapper. Review the source wrapper's referenced controller3_2 model first; alias and wrapper are integration context only and cannot substitute for an internal controller-layout verdict.",
        "review_note_zh": "当前入口是固定整机链的正式别名；先审查源整机包装器中 controller3_2 指向的内部控制器，别名和整机包装器只用于核对接入关系。",
    }


def pending_graphical_row(row: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / str(row["current_model_file"])
    target = static_indicators(path)
    if target["model_class"] != row["current_model_class"]:
        raise QueueError(
            f"{row['scheme_id']}: current-map class drift: {target['model_class']} != {row['current_model_class']}"
        )
    if target["model_sha256"] != row["current_model_sha256"]:
        raise QueueError(f"{row['scheme_id']}: current-map hash drift")
    return {
        "scheme_id": row["scheme_id"],
        "display_name_zh": row.get("display_name_zh"),
        "category": row["category"],
        "entry_type": row["entry_type"],
        "mapping_state": row["mapping_state"],
        "review_disposition": "pending_live_internal_graphical_review",
        "live_review_status": "not_started",
        "review_target_kind": "current_graphical_controller_core",
        "review_target": target,
        "wrapper_risk": None,
        "review_note_zh": "必须在 MWORKS 中核对可见块、端口、走线和功能组；静态计数不能记为通过。",
        "required_layout_observations": [
            "is_internal_control_law",
            "signal_flow_readable",
            "functional_groups_readable",
            "wires_traceable",
        ],
    }


def fixed_source_wrapper(row: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    provenance = row.get("source_provenance")
    if not isinstance(provenance, dict):
        raise QueueError(f"{row.get('scheme_id')}: fixed-chain source provenance is missing")
    source_file = provenance.get("source_file")
    if not isinstance(source_file, str) or not source_file:
        raise QueueError(f"{row.get('scheme_id')}: fixed-chain source file is missing")
    path = (ROOT / source_file).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise QueueError(f"{row.get('scheme_id')}: fixed-chain source escapes the project root") from exc
    indicators = static_indicators(path)
    if indicators["model_sha256"] != provenance.get("source_sha256"):
        raise QueueError(f"{row.get('scheme_id')}: fixed-chain source-wrapper hash drift")
    if indicators["model_class"] != provenance.get("source_model_class"):
        raise QueueError(f"{row.get('scheme_id')}: fixed-chain source-wrapper class drift")
    return path, indicators


def pending_fixed_row(row: dict[str, Any]) -> dict[str, Any]:
    wrapper_path = ROOT / str(row["current_model_file"])
    wrapper = static_indicators(wrapper_path)
    if wrapper["model_class"] != row["current_model_class"]:
        raise QueueError(
            f"{row['scheme_id']}: wrapper class drift: {wrapper['model_class']} != {row['current_model_class']}"
        )
    if wrapper["model_sha256"] != row["current_model_sha256"]:
        raise QueueError(f"{row['scheme_id']}: current-map wrapper hash drift")
    source_wrapper_path, source_wrapper = fixed_source_wrapper(row)
    internal = fixed_internal_target(source_wrapper_path)
    return {
        "scheme_id": row["scheme_id"],
        "display_name_zh": row.get("display_name_zh"),
        "category": row["category"],
        "entry_type": row["entry_type"],
        "mapping_state": row["mapping_state"],
        "review_disposition": "pending_live_internal_graphical_review",
        "live_review_status": "not_started",
        "wrapper_static_indicators": wrapper,
        "source_wrapper_static_indicators": source_wrapper,
        **internal,
        "required_layout_observations": [
            "is_internal_control_law",
            "signal_flow_readable",
            "functional_groups_readable",
            "wires_traceable",
        ],
    }


def blocked_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheme_id": row["scheme_id"],
        "display_name_zh": row.get("display_name_zh"),
        "category": row["category"],
        "entry_type": row["entry_type"],
        "mapping_state": row["mapping_state"],
        "review_disposition": "blocked_before_live_review",
        "live_review_status": "not_started",
        "blocker_code": row.get("blocker_code"),
        "blocker_reason": row.get("blocker_reason"),
        "source_candidates_inspected": row.get("source_candidates_inspected", []),
        "review_note_zh": "缺少当前实现工件，不能以邻近控制器、历史截图或静态公式替代。",
    }


def not_applicable_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "scheme_id": row["scheme_id"],
        "display_name_zh": row.get("display_name_zh"),
        "category": row["category"],
        "entry_type": row["entry_type"],
        "mapping_state": row["mapping_state"],
        "review_disposition": "not_applicable_runtime_baseline",
        "live_review_status": "not_started",
        "blocker_code": row.get("blocker_code"),
        "review_note_zh": "px4ctrl 是 ROS1/PX4 工程基线，不伪造 MWORKS 图形模型；其验证留给 G7 后的运行时路线。",
    }


def make_batches(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["review_disposition"] == "pending_live_internal_graphical_review":
            by_category[str(row["category"])].append(row)

    batches: list[dict[str, Any]] = []
    sequence = 1
    for category in FAMILY_ORDER:
        candidates = by_category.get(category, [])
        for offset in range(0, len(candidates), 5):
            items = candidates[offset : offset + 5]
            batches.append(
                {
                    "batch_id": f"G5-{sequence:02d}-{category}",
                    "category": category,
                    "category_label_zh": FAMILY_LABELS[category],
                    "scheme_ids": [item["scheme_id"] for item in items],
                    "count": len(items),
                    "batch_note_zh": "按同族分批审查。少于四条的尾批保留为同族尾批，不与异构控制器混合。",
                }
            )
            sequence += 1
    return batches


def build_queue() -> dict[str, Any]:
    current_map = read_json(MAP_PATH)
    if current_map.get("schema") != "mosim.current_model_entry_map.v1":
        raise QueueError("G5 requires mosim.current_model_entry_map.v1")
    map_rows = current_map.get("schemes")
    if not isinstance(map_rows, list) or len(map_rows) != 49:
        raise QueueError("G5 requires exactly 49 frozen top-level schemes")

    rows: list[dict[str, Any]] = []
    for map_row in map_rows:
        if not isinstance(map_row, dict):
            raise QueueError("Current model map contains a non-object row")
        state = map_row.get("mapping_state")
        role = map_row.get("current_model_role")
        if state == "blocked_missing_current_model":
            rows.append(blocked_row(map_row))
        elif state == "not_applicable_runtime_baseline":
            rows.append(not_applicable_row(map_row))
        elif state == "resolved_current_model" and role == "graphical_controller_core":
            rows.append(pending_graphical_row(map_row))
        elif state == "resolved_current_model" and role == "fixed_integrated_whole_aircraft_closed_loop":
            rows.append(pending_fixed_row(map_row))
        else:
            raise QueueError(
                f"{map_row.get('scheme_id')}: unsupported G5 mapping state/role: {state}/{role}"
            )

    counts = Counter(str(row["review_disposition"]) for row in rows)
    family_counts = Counter(
        str(row["category"])
        for row in rows
        if row["review_disposition"] == "pending_live_internal_graphical_review"
    )
    return {
        "schema": "mosim.g5_graphical_review_queue.v1",
        "scope": "Static G5 review plan only. No row is a MWORKS check, simulation, layout-pass, code-generation, or runtime-success claim.",
        "source_map": repo_path(MAP_PATH),
        "source_map_sha256": sha256_file(MAP_PATH),
        "summary": {
            "top_level_scheme_count": len(rows),
            "current_mworks_review_scope_count": counts["pending_live_internal_graphical_review"],
            "pending_live_internal_review_count": counts["pending_live_internal_graphical_review"],
            "blocked_before_live_review_count": counts["blocked_before_live_review"],
            "not_applicable_runtime_baseline_count": counts["not_applicable_runtime_baseline"],
            "pending_family_counts": dict(sorted(family_counts.items())),
        },
        "first_live_batch": "G5-01-pid_family",
        "batches": make_batches(rows),
        "schemes": rows,
    }


def validate_queue(queue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if queue.get("schema") != "mosim.g5_graphical_review_queue.v1":
        errors.append("schema is invalid")
    rows = queue.get("schemes")
    if not isinstance(rows, list) or len(rows) != 49:
        errors.append("queue must contain exactly 49 schemes")
        return errors
    identifiers = [str(row.get("scheme_id")) for row in rows if isinstance(row, dict)]
    if len(identifiers) != 49 or len(set(identifiers)) != 49:
        errors.append("scheme IDs must be complete and unique")
    by_id = {str(row.get("scheme_id")): row for row in rows if isinstance(row, dict)}
    if by_id.get("px4ctrl", {}).get("review_disposition") != "not_applicable_runtime_baseline":
        errors.append("px4ctrl must remain not_applicable_runtime_baseline")
    for scheme_id in ("mu_synthesis", "neural_smc"):
        if by_id.get(scheme_id, {}).get("review_disposition") != "blocked_before_live_review":
            errors.append(f"{scheme_id} must remain blocked_before_live_review")
    pending = [
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("review_disposition") == "pending_live_internal_graphical_review"
    ]
    if len(pending) != 46:
        errors.append("expected exactly 46 pending live internal review candidates")
    for row in pending:
        target = row.get("review_target")
        if not isinstance(target, dict) or not target.get("model_file"):
            errors.append(f"{row.get('scheme_id')}: live review target is missing")
        elif not (ROOT / str(target["model_file"])).is_file():
            errors.append(f"{row.get('scheme_id')}: review target file is missing")
    for row in pending:
        if row.get("category") == "fixed_integrated" and "wrapper_static_indicators" not in row:
            errors.append(f"{row.get('scheme_id')}: fixed chain must declare wrapper risk")
    batches = queue.get("batches")
    if not isinstance(batches, list) or not batches:
        errors.append("queue must contain live review batches")
    else:
        batch_ids = [scheme_id for batch in batches for scheme_id in batch.get("scheme_ids", [])]
        pending_ids = [row["scheme_id"] for row in pending]
        if sorted(batch_ids) != sorted(pending_ids):
            errors.append("batches must cover each pending live review candidate exactly once")
        for batch in batches:
            if batch.get("count") != len(batch.get("scheme_ids", [])):
                errors.append(f"{batch.get('batch_id')}: count does not match scheme_ids")
            if int(batch.get("count", 0)) > 5:
                errors.append(f"{batch.get('batch_id')}: batch exceeds five models")
    expected_summary = {
        "top_level_scheme_count": 49,
        "current_mworks_review_scope_count": 46,
        "pending_live_internal_review_count": 46,
        "blocked_before_live_review_count": 2,
        "not_applicable_runtime_baseline_count": 1,
    }
    summary = queue.get("summary")
    if not isinstance(summary, dict):
        errors.append("summary is missing")
    else:
        for key, value in expected_summary.items():
            if summary.get(key) != value:
                errors.append(f"summary.{key} must equal {value}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="fail if the on-disk queue differs from the deterministic build")
    args = parser.parse_args(argv)

    try:
        expected = build_queue()
        errors = validate_queue(expected)
        output = args.output if args.output.is_absolute() else ROOT / args.output
        if args.check:
            if not output.is_file():
                errors.append(f"queue is missing: {output}")
            else:
                current = read_json(output)
                if current != expected:
                    errors.append("on-disk queue differs from deterministic G5 source mapping")
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            write_utf8_lf(output, canonical_json(expected))
    except Exception as exc:  # A fail-closed queue is more useful than a traceback-only result.
        errors = [str(exc)]
        output = args.output if args.output.is_absolute() else ROOT / args.output

    report = {
        "schema": "mosim.g5_graphical_review_queue_check.v1",
        "ok": not errors,
        "queue": repo_path(output) if output.is_absolute() else str(output),
        "errors": errors,
    }
    print(canonical_json(report).rstrip())
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
