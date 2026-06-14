#!/usr/bin/env python3
"""Validate CoAgent capability_resolution blocks.

The capability index is a router, not an authority grant. This checker ensures
packets that select or create reusable tools/skills/scripts first resolve
existing indexed capabilities and explain any new asset creation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_TOP_FIELDS = [
    "required",
    "capability_index_consulted",
    "consulted_index_path",
    "matched_capability_ids",
    "matched_capabilities",
    "existing_assets_to_reuse",
    "searched_existing_assets",
    "create_new_assets",
    "do_not_recreate",
    "unresolved_capabilities",
]

REQUIRED_SEARCH_ASSETS = [
    "Docs/Index/capability_index.md",
    "CoAgent/skills/",
    "Docs/Skills/",
    "Scripts/",
]

CREATE_ASSET_KEYWORDS = [
    "skill",
    "workflow",
    "script",
    "checker",
    "mcp",
    "plugin",
    "capability",
    "hook",
]

AUTHORITY_GRANT_MARKERS = [
    "authorizes",
    "permission granted",
    "approval granted",
    "may click",
    "may login",
    "may save",
    "may restart",
    "may dispatch",
]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(non_empty_string(item) for item in value)


def extract_resolution(packet: dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(packet.get("capability_resolution"), dict):
        return packet["capability_resolution"]
    metadata = packet.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("capability_resolution"), dict):
        return metadata["capability_resolution"]
    if packet.get("template_type") == "capability_resolution":
        return packet
    return None


def creates_reusable_asset(create_new_assets: list[Any]) -> bool:
    joined = "\n".join(str(item).lower() for item in create_new_assets)
    return any(keyword in joined for keyword in CREATE_ASSET_KEYWORDS)


def validate_resolution(resolution: dict[str, Any], *, strict: bool = False) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    for field in REQUIRED_TOP_FIELDS:
        if field not in resolution:
            findings.append({
                "severity": "error",
                "field": f"capability_resolution.{field}",
                "reason": "missing_required_field",
                "message": f"capability_resolution.{field} is required.",
            })

    if resolution.get("required") is not True:
        findings.append({
            "severity": "error" if strict else "warning",
            "field": "capability_resolution.required",
            "reason": "capability_resolution_not_required",
            "message": "capability_resolution.required should be true for reusable capability/tool decisions.",
        })

    if resolution.get("capability_index_consulted") is not True:
        findings.append({
            "severity": "error",
            "field": "capability_resolution.capability_index_consulted",
            "reason": "capability_index_not_consulted",
            "message": "Capability index must be consulted before selecting or creating reusable assets.",
        })

    consulted_index = str(resolution.get("consulted_index_path", ""))
    if consulted_index != "Docs/Index/capability_index.md":
        findings.append({
            "severity": "error",
            "field": "capability_resolution.consulted_index_path",
            "reason": "wrong_capability_index",
            "message": "consulted_index_path must be Docs/Index/capability_index.md.",
        })

    searched_assets = [str(item) for item in as_list(resolution.get("searched_existing_assets"))]
    for required_asset in REQUIRED_SEARCH_ASSETS:
        if required_asset not in searched_assets:
            findings.append({
                "severity": "error",
                "field": "capability_resolution.searched_existing_assets",
                "reason": "missing_existing_asset_search",
                "message": f"searched_existing_assets must include {required_asset}.",
            })

    matched_ids = as_list(resolution.get("matched_capability_ids"))
    matched_names = as_list(resolution.get("matched_capabilities"))
    existing_assets = as_list(resolution.get("existing_assets_to_reuse"))
    unresolved = as_list(resolution.get("unresolved_capabilities"))
    create_new_assets = as_list(resolution.get("create_new_assets"))
    do_not_recreate = as_list(resolution.get("do_not_recreate"))

    if strict and not non_empty_string_list(matched_ids) and not non_empty_string_list(unresolved):
        findings.append({
            "severity": "error",
            "field": "capability_resolution.matched_capability_ids",
            "reason": "no_matched_or_unresolved_capability",
            "message": "Strict mode requires at least one matched capability id or explicit unresolved capability.",
        })

    if non_empty_string_list(matched_ids) and not non_empty_string_list(matched_names):
        findings.append({
            "severity": "error",
            "field": "capability_resolution.matched_capabilities",
            "reason": "matched_names_missing",
            "message": "matched_capabilities must name the matched ids for human review.",
        })

    if non_empty_string_list(matched_ids) and not non_empty_string_list(existing_assets):
        findings.append({
            "severity": "error",
            "field": "capability_resolution.existing_assets_to_reuse",
            "reason": "matched_capability_without_reuse_asset",
            "message": "Matched capabilities must list existing assets to reuse.",
        })

    if create_new_assets:
        reason = str(resolution.get("reason_existing_assets_insufficient", "")).strip()
        if not reason:
            findings.append({
                "severity": "error",
                "field": "capability_resolution.reason_existing_assets_insufficient",
                "reason": "new_asset_without_insufficiency_reason",
                "message": "Creating new assets requires a concrete reason existing assets are insufficient.",
            })
        if not non_empty_string_list(do_not_recreate):
            findings.append({
                "severity": "error",
                "field": "capability_resolution.do_not_recreate",
                "reason": "new_asset_without_do_not_recreate_list",
                "message": "Creating new assets must record what existing concepts must not be recreated.",
            })
        if creates_reusable_asset(create_new_assets) and not non_empty_string_list(existing_assets):
            findings.append({
                "severity": "error",
                "field": "capability_resolution.existing_assets_to_reuse",
                "reason": "new_reusable_asset_without_existing_asset_context",
                "message": "Reusable asset creation must name existing assets that were checked or reused.",
            })

    notes = str(resolution.get("notes", "")).lower()
    for marker in AUTHORITY_GRANT_MARKERS:
        if marker in notes:
            findings.append({
                "severity": "error",
                "field": "capability_resolution.notes",
                "reason": "capability_resolution_claims_authority",
                "message": f"Capability resolution is routing evidence, not permission: {marker}",
            })

    if unresolved and not str(resolution.get("reason_existing_assets_insufficient", "")).strip():
        findings.append({
            "severity": "warning",
            "field": "capability_resolution.unresolved_capabilities",
            "reason": "unresolved_without_reason",
            "message": "Unresolved capabilities should explain what remains unknown.",
        })

    return findings


def validate_packet(packet: dict[str, Any], *, strict: bool = False) -> dict[str, Any]:
    resolution = extract_resolution(packet)
    if resolution is None:
        finding = {
            "severity": "error" if strict else "warning",
            "field": "capability_resolution",
            "reason": "missing_capability_resolution",
            "message": "No capability_resolution block found.",
        }
        findings = [finding]
    else:
        findings = validate_resolution(resolution, strict=strict)

    errors = [finding for finding in findings if finding["severity"] == "error"]
    warnings = [finding for finding in findings if finding["severity"] == "warning"]
    return {
        "ok": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", help="JSON packet or capability_resolution template")
    parser.add_argument("--strict", action="store_true", help="Treat missing/weak optional routing evidence as errors")
    parser.add_argument("--output-json", help="Optional validation report path")
    args = parser.parse_args()

    packet_path = repo_path(args.packet)
    try:
        packet = read_json(packet_path)
        report = validate_packet(packet, strict=args.strict)
    except Exception as exc:
        report = {
            "ok": False,
            "error_count": 1,
            "warning_count": 0,
            "findings": [{
                "severity": "error",
                "field": str(packet_path),
                "reason": "read_or_parse_failed",
                "message": str(exc),
            }],
        }

    report["packet"] = rel(packet_path)
    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
