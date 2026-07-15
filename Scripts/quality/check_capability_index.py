#!/usr/bin/env python3
"""Validate the machine-readable MoSim capability index.

The capability index is a router, not an authority grant. This checker keeps
the JSON companion aligned with the human Markdown index and makes sure each
capability has owner docs, stop actions, evidence gates, and health/checker
routes before agents rely on it.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = ROOT / "Config" / "capabilities" / "capability_index.json"
MARKDOWN_INDEX = ROOT / "Docs" / "Index" / "capability_index.md"

REQUIRED_TOP_FIELDS = [
    "schema_version",
    "status",
    "purpose",
    "authority_model",
    "consultation_order",
    "capabilities",
]

REQUIRED_CAPABILITY_FIELDS = [
    "id",
    "display_name",
    "family",
    "use_when",
    "owner_docs",
    "existing_assets",
    "stop_actions",
    "evidence_gates",
    "health_or_checker",
]

REQUIRED_IDS = {
    "codex.visible_thread.dispatch",
    "codex.thread_lifecycle",
    "automation.recurring_patrol",
    "hooks.preflight",
    "mworks.sysplorer_mcp",
    "mworks.window_review",
    "desktop.window.capture_evidence",
    "desktop.window.ui_action_control",
    "ue.runtime_or_source",
    "ros2.runtime_review",
    "git.devops",
    "github.issue_pr",
    "browser.web_research",
    "docs.secretary",
    "capability.cards",
    "review.evidence_gate",
}

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


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(non_empty_string(item) for item in value)


def markdown_stable_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    section_match = re.search(
        r"## 3\. Stable Capability IDs(?P<body>.*?)(?:\n## |\Z)",
        text,
        flags=re.DOTALL,
    )
    body = section_match.group("body") if section_match else text
    stable_ids: set[str] = set()
    for line in body.splitlines():
        match = re.match(r"\|\s*`([a-z0-9_]+(?:\.[a-z0-9_]+)+)`\s*\|", line)
        if match:
            stable_ids.add(match.group(1))
    return stable_ids


def contains_authority_grant(value: Any) -> str | None:
    if isinstance(value, dict):
        joined = "\n".join(str(item) for pair in value.items() for item in pair)
    elif isinstance(value, list):
        joined = "\n".join(str(item) for item in value)
    else:
        joined = str(value)
    lowered = joined.lower()
    for marker in AUTHORITY_GRANT_MARKERS:
        if marker in lowered:
            return marker
    return None


def validate_index(index: dict[str, Any], *, markdown_path: Path = MARKDOWN_INDEX) -> dict[str, Any]:
    findings: list[dict[str, str]] = []

    for field in REQUIRED_TOP_FIELDS:
        if field not in index:
            findings.append({
                "severity": "error",
                "field": field,
                "reason": "missing_required_field",
                "message": f"{field} is required.",
            })

    if index.get("authority_model") != "router_not_authority":
        findings.append({
            "severity": "error",
            "field": "authority_model",
            "reason": "wrong_authority_model",
            "message": "authority_model must be router_not_authority.",
        })

    purpose_marker = contains_authority_grant(index.get("purpose", ""))
    if purpose_marker:
        findings.append({
            "severity": "error",
            "field": "purpose",
            "reason": "purpose_claims_authority",
            "message": f"Capability index purpose must not imply authority: {purpose_marker}",
        })

    capabilities = as_list(index.get("capabilities"))
    if not capabilities:
        findings.append({
            "severity": "error",
            "field": "capabilities",
            "reason": "empty_capability_list",
            "message": "capabilities must contain at least one capability.",
        })

    seen_ids: set[str] = set()
    capability_ids: set[str] = set()

    for item_index, capability in enumerate(capabilities):
        field_prefix = f"capabilities[{item_index}]"
        if not isinstance(capability, dict):
            findings.append({
                "severity": "error",
                "field": field_prefix,
                "reason": "capability_not_object",
                "message": "Each capability must be an object.",
            })
            continue

        capability_id = str(capability.get("id", "")).strip()
        if not re.fullmatch(r"[a-z0-9_]+\.[a-z0-9_.]+", capability_id):
            findings.append({
                "severity": "error",
                "field": f"{field_prefix}.id",
                "reason": "invalid_capability_id",
                "message": "Capability id must use stable dotted lowercase form.",
            })
        elif capability_id in seen_ids:
            findings.append({
                "severity": "error",
                "field": f"{field_prefix}.id",
                "reason": "duplicate_capability_id",
                "message": f"Duplicate capability id: {capability_id}",
            })
        else:
            seen_ids.add(capability_id)
            capability_ids.add(capability_id)

        for field in REQUIRED_CAPABILITY_FIELDS:
            if field not in capability:
                findings.append({
                    "severity": "error",
                    "field": f"{field_prefix}.{field}",
                    "reason": "missing_required_field",
                    "message": f"{field} is required for each capability.",
                })

        for list_field in [
            "use_when",
            "owner_docs",
            "existing_assets",
            "stop_actions",
            "evidence_gates",
            "health_or_checker",
        ]:
            if not non_empty_string_list(capability.get(list_field)):
                findings.append({
                    "severity": "error",
                    "field": f"{field_prefix}.{list_field}",
                    "reason": "empty_required_list",
                    "message": f"{list_field} must include at least one non-empty string.",
                })

        marker = contains_authority_grant(capability)
        if marker:
            findings.append({
                "severity": "error",
                "field": field_prefix,
                "reason": "capability_claims_authority",
                "message": f"Capability entries route work but do not grant permission: {marker}",
            })

    missing_required = sorted(REQUIRED_IDS - capability_ids)
    if missing_required:
        findings.append({
            "severity": "error",
            "field": "capabilities",
            "reason": "missing_required_capability_ids",
            "message": "Missing required ids: " + ", ".join(missing_required),
        })

    md_ids = markdown_stable_ids(markdown_path)
    missing_from_markdown = sorted(capability_ids - md_ids)
    missing_from_json = sorted(md_ids - capability_ids)
    if missing_from_markdown:
        findings.append({
            "severity": "error",
            "field": "Docs/Index/capability_index.md",
            "reason": "json_ids_missing_from_markdown",
            "message": "JSON ids missing from Markdown stable-id table: " + ", ".join(missing_from_markdown),
        })
    if missing_from_json:
        findings.append({
            "severity": "error",
            "field": "Config/capabilities/capability_index.json",
            "reason": "markdown_ids_missing_from_json",
            "message": "Markdown ids missing from JSON index: " + ", ".join(missing_from_json),
        })

    errors = [finding for finding in findings if finding["severity"] == "error"]
    warnings = [finding for finding in findings if finding["severity"] == "warning"]
    return {
        "ok": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "capability_count": len(capability_ids),
        "markdown_stable_id_count": len(md_ids),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "capability_index",
        nargs="?",
        default=str(DEFAULT_INDEX.relative_to(ROOT)),
        help="Capability index JSON path",
    )
    parser.add_argument("--output-json", help="Optional validation report path")
    args = parser.parse_args()

    index_path = repo_path(args.capability_index)
    try:
        index = read_json(index_path)
        report = validate_index(index)
    except Exception as exc:
        report = {
            "ok": False,
            "error_count": 1,
            "warning_count": 0,
            "capability_count": 0,
            "markdown_stable_id_count": 0,
            "findings": [{
                "severity": "error",
                "field": rel(index_path),
                "reason": "read_or_parse_failed",
                "message": str(exc),
            }],
        }

    report["capability_index"] = rel(index_path)
    report["markdown_index"] = rel(MARKDOWN_INDEX)
    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
