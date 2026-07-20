#!/usr/bin/env python3
"""Validate route-bound MWORKS graphical-controller review packets.

The report asset audit classifies possible controller sources statically. This
checker validates the *next* evidence layer: a route may be marked accepted
only after an authorized MWORKS review binds its actual internal model, model
check, simulation, layout decision, result title, and local artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT = (
    ROOT
    / "Results"
    / "control_platform"
    / "report_closeout_20260721"
    / "static_audit"
    / "控制器证据审计.json"
)
DEFAULT_REVIEWS_DIR = (
    ROOT
    / "Results"
    / "control_platform"
    / "report_closeout_20260721"
    / "route_reviews"
)
REQUIRED_SCHEMA = "mosim.controller_graphical_review.v1"
REQUIRED_ARTIFACT_KEYS = {
    "overview",
    "check_model_log",
    "simulation_manifest",
    "result_screenshot",
    "screenshot_manifest",
}
REQUIRED_LAYOUT_KEYS = {
    "is_internal_control_law",
    "signal_flow_readable",
    "functional_groups_readable",
    "wires_traceable",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def resolve_ref(value: Any, packet_path: Path) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    project_path = ROOT / candidate
    if project_path.exists():
        return project_path
    return packet_path.parent / candidate


def add_error(errors: list[dict[str, str]], field: str, message: str) -> None:
    errors.append({"field": field, "message": message})


def expected_model_names(row: dict[str, Any]) -> set[str]:
    return {
        str(record["model_name"])
        for record in row.get("source_records", [])
        if isinstance(record, dict) and isinstance(record.get("model_name"), str)
    }


def validate_artifact(
    value: Any,
    packet_path: Path,
    errors: list[dict[str, str]],
    field: str,
) -> None:
    path = resolve_ref(value, packet_path)
    if path is None:
        add_error(errors, field, "missing artifact reference")
    elif not path.is_file() or path.stat().st_size <= 0:
        add_error(errors, field, f"artifact is missing or empty: {path}")


def validate_accepted_packet(
    packet: dict[str, Any], row: dict[str, Any], packet_path: Path
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for field in ("source", "license_state", "internal_model_path", "internal_model_sha256"):
        if not packet.get(field):
            add_error(errors, field, "required for an accepted review")

    if str(packet.get("source")) not in {"MWORKS_MCP", "MWORKS_GUI"}:
        add_error(errors, "source", "must be MWORKS_MCP or MWORKS_GUI")
    if "demo" in str(packet.get("license_state", "")).casefold() or "licensed" not in str(
        packet.get("license_state", "")
    ).casefold():
        add_error(errors, "license_state", "must record an authorized non-demo session")

    expected_source = str(row.get("selected_internal_source") or "")
    actual_source = str(packet.get("internal_model_path") or "").replace("\\", "/")
    if actual_source != expected_source:
        add_error(errors, "internal_model_path", "does not match the audit-selected internal model")
    source_path = resolve_ref(packet.get("internal_model_path"), packet_path)
    if source_path is None or not source_path.is_file():
        add_error(errors, "internal_model_path", "source model is missing")
    elif str(packet.get("internal_model_sha256", "")).upper() != sha256(source_path):
        add_error(errors, "internal_model_sha256", "does not match the reviewed source model")

    if packet.get("check_model_status") != "passed":
        add_error(errors, "check_model_status", "must be passed before accepting a simulation")
    if packet.get("simulation_status") != "passed":
        add_error(errors, "simulation_status", "must be passed for accepted review")
    if packet.get("result_binding_status") != "passed":
        add_error(errors, "result_binding_status", "must be passed for accepted review")

    title = str(packet.get("result_window_title") or "")
    names = expected_model_names(row)
    if not title:
        add_error(errors, "result_window_title", "missing current Result Viewer title")
    elif names and not any(name.casefold() in title.casefold() for name in names):
        add_error(errors, "result_window_title", "does not contain a model name for this route")

    layout = packet.get("layout_review")
    if not isinstance(layout, dict):
        add_error(errors, "layout_review", "must be an object")
    else:
        for key in sorted(REQUIRED_LAYOUT_KEYS):
            if layout.get(key) is not True:
                add_error(errors, f"layout_review.{key}", "must be true for an accepted internal diagram")

    artifacts = packet.get("artifacts")
    if not isinstance(artifacts, dict):
        add_error(errors, "artifacts", "must be an object")
    else:
        for key in sorted(REQUIRED_ARTIFACT_KEYS):
            validate_artifact(artifacts.get(key), packet_path, errors, f"artifacts.{key}")
        panels = artifacts.get("detail_panels", [])
        if not isinstance(panels, list):
            add_error(errors, "artifacts.detail_panels", "must be a list when present")
        else:
            for index, value in enumerate(panels):
                validate_artifact(value, packet_path, errors, f"artifacts.detail_panels[{index}]")
    return errors


def validate_blocked_packet(packet: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if not packet.get("failure_kind"):
        add_error(errors, "failure_kind", "blocked review requires a concrete failure kind")
    not_performed = packet.get("not_performed")
    if not isinstance(not_performed, list) or not not_performed:
        add_error(errors, "not_performed", "blocked review must declare unfinished live steps")
    return errors


def validate_packet(packet: dict[str, Any], row: dict[str, Any], packet_path: Path) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if packet.get("schema") != REQUIRED_SCHEMA:
        add_error(errors, "schema", f"must equal {REQUIRED_SCHEMA}")
    if packet.get("controller") != row.get("controller"):
        add_error(errors, "controller", "does not match the review route")
    if row.get("source_classification") != "native_graphical_candidate":
        add_error(errors, "source_classification", "only native graphical candidates may use this review packet")
        return errors
    status = packet.get("status")
    if status == "accepted":
        errors.extend(validate_accepted_packet(packet, row, packet_path))
    elif status == "blocked":
        errors.extend(validate_blocked_packet(packet))
    else:
        add_error(errors, "status", "must be accepted or blocked")
    return errors


def audit_reviews(audit_path: Path, reviews_dir: Path) -> dict[str, Any]:
    audit = read_json(audit_path)
    rows = audit.get("rows")
    if not isinstance(rows, list):
        raise ValueError("audit rows must be a list")
    expected = {
        str(row["controller"]): row
        for row in rows
        if isinstance(row, dict)
        and row.get("source_classification") == "native_graphical_candidate"
    }
    packets: dict[str, tuple[Path, dict[str, Any]]] = {}
    parse_errors: list[dict[str, str]] = []
    if reviews_dir.is_dir():
        for path in sorted(reviews_dir.glob("*.json")):
            try:
                packet = read_json(path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                parse_errors.append({"packet": str(path), "field": "json", "message": str(exc)})
                continue
            route = str(packet.get("controller") or "")
            if not route:
                parse_errors.append({"packet": str(path), "field": "controller", "message": "missing controller"})
            elif route in packets:
                parse_errors.append({"packet": str(path), "field": "controller", "message": f"duplicate packet for {route}"})
            else:
                packets[route] = (path, packet)

    route_reports: list[dict[str, Any]] = []
    invalid = list(parse_errors)
    accepted = 0
    blocked = 0
    for route, row in sorted(expected.items()):
        entry = packets.pop(route, None)
        if entry is None:
            route_reports.append({"controller": route, "status": "missing_review_packet", "errors": []})
            continue
        path, packet = entry
        errors = validate_packet(packet, row, path)
        status = str(packet.get("status"))
        route_reports.append({"controller": route, "status": status, "packet": str(path), "errors": errors})
        if errors:
            invalid.extend({"packet": str(path), **error} for error in errors)
        elif status == "accepted":
            accepted += 1
        else:
            blocked += 1
    for route, (path, _) in sorted(packets.items()):
        invalid.append({"packet": str(path), "field": "controller", "message": f"route is not an expected native graphical candidate: {route}"})

    missing = sum(item["status"] == "missing_review_packet" for item in route_reports)
    return {
        "schema": "mosim.controller_graphical_review_audit.v1",
        "audit_path": str(audit_path),
        "reviews_dir": str(reviews_dir),
        "expected_native_graphical_routes": len(expected),
        "accepted": accepted,
        "blocked": blocked,
        "missing": missing,
        "invalid": len(invalid),
        "route_reports": route_reports,
        "invalid_packets": invalid,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--reviews-dir", type=Path, default=DEFAULT_REVIEWS_DIR)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args(argv)
    report = audit_reviews(args.audit, args.reviews_dir)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    complete = report["missing"] == 0 and report["blocked"] == 0 and report["invalid"] == 0
    return 0 if complete or (args.allow_incomplete and report["invalid"] == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
