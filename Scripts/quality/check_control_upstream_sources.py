"""Validate pinned and licensed upstream sources for MoSim control families."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES = ROOT / "Config" / "control_platform" / "upstream_sources.json"
APPROVED_LICENSES = {"MIT", "BSD-3-Clause", "Apache-2.0"}
ALLOWED_DECISIONS = {"selected", "dropped", "deferred_with_reason", "deferred_external_gate"}
REQUIRED_FAMILY_DECISIONS = {
    "nonlinear_ndi_feedback_linearization",
    "complete_adrc",
    "bounded_learning_augmentation",
    "formation_reference_generation",
    "basic_safety_filter",
    "px4_backend_control_allocation",
    "advanced_cbf_reference_governor",
    "fault_aware_allocation",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(data: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    def add(code: str, message: str) -> None:
        errors.append({"code": code, "message": message})

    if data.get("schema") != "mosim.control_upstream_sources.v1":
        add("CUS-SCHEMA-01", "unsupported upstream source schema")
    selected = data.get("selected")
    if not isinstance(selected, list) or not selected:
        add("CUS-SOURCE-01", "selected must be a non-empty list")
        return errors
    seen: set[str] = set()
    for index, item in enumerate(selected):
        if not isinstance(item, dict):
            add("CUS-SOURCE-02", f"selected[{index}] must be an object")
            continue
        source_id = str(item.get("id", ""))
        if not source_id or source_id in seen:
            add("CUS-SOURCE-03", f"missing or duplicate source id: {source_id}")
        seen.add(source_id)
        if item.get("license") not in APPROVED_LICENSES:
            add("CUS-LICENSE-01", f"{source_id} has unapproved license: {item.get('license')}")
        if not SHA40.fullmatch(str(item.get("commit", ""))):
            add("CUS-PIN-01", f"{source_id} must pin a 40-character commit SHA")
        url = str(item.get("url", ""))
        if not url.startswith("https://github.com/"):
            add("CUS-URL-01", f"{source_id} must use an explicit GitHub URL")
        if not str(item.get("family", "")) or not str(item.get("role", "")):
            add("CUS-ROLE-01", f"{source_id} must declare family and role")

    for index, item in enumerate(data.get("reference_only", [])):
        if not isinstance(item, dict):
            add("CUS-REF-01", f"reference_only[{index}] must be an object")
            continue
        if item.get("source_copy_allowed") is not False:
            add("CUS-REF-02", f"reference-only source {item.get('repo')} must forbid source copying")
        if not str(item.get("reason", "")):
            add("CUS-REF-03", f"reference-only source {item.get('repo')} must declare a reason")

    decisions = data.get("family_decisions")
    if not isinstance(decisions, list):
        add("CUS-DECISION-01", "family_decisions must be a list")
        return errors
    decision_ids: set[str] = set()
    for index, item in enumerate(decisions):
        if not isinstance(item, dict):
            add("CUS-DECISION-02", f"family_decisions[{index}] must be an object")
            continue
        family_id = str(item.get("family_id", ""))
        if not family_id or family_id in decision_ids:
            add("CUS-DECISION-03", f"missing or duplicate family decision: {family_id}")
        decision_ids.add(family_id)
        decision = item.get("decision")
        if decision not in ALLOWED_DECISIONS:
            add("CUS-DECISION-04", f"{family_id} has unsupported decision: {decision}")
        if decision == "selected" and not str(item.get("implementation", "")):
            add("CUS-DECISION-05", f"selected family {family_id} must name its implementation")
        if decision != "selected" and not str(item.get("reason", "")):
            add("CUS-DECISION-06", f"non-selected family {family_id} must declare a reason")
    missing = sorted(REQUIRED_FAMILY_DECISIONS - decision_ids)
    if missing:
        add("CUS-DECISION-07", f"missing required family decisions: {', '.join(missing)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", default=str(DEFAULT_SOURCES))
    args = parser.parse_args()
    path = Path(args.sources)
    try:
        errors = validate(load_json(path))
    except Exception as exc:
        errors = [{"code": "CUS-READ-01", "message": str(exc)}]
    report = {"ok": not errors, "sources": str(path), "error_count": len(errors), "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
