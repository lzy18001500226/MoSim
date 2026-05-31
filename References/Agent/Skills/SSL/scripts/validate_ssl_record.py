"""Validate SSL records.

Usage:

    python scripts/validate_ssl_record.py path/to/example_ssl_record.json
    python scripts/validate_ssl_record.py path/to/annotated_skill_corpus.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


SCENE_TYPES = {"PREPARE", "ACQUIRE", "REASON", "ACT", "VERIFY", "RECOVER", "FINALIZE"}
ACT_TYPES = {
    "READ",
    "SELECT",
    "COMPARE",
    "VALIDATE",
    "INFER",
    "WRITE",
    "UPDATE_STATE",
    "CALL_TOOL",
    "REQUEST",
    "TRANSFER",
    "NOTIFY",
    "TERMINATE",
}
RESOURCE_SCOPES = {
    "MEMORY",
    "LOCAL_FS",
    "CODEBASE",
    "PROCESS",
    "USER_DATA",
    "CREDENTIALS",
    "NETWORK",
    "OTHER",
}
SCENE_TERMINALS = {"END_SUCCESS", "END_FAIL"}
STEP_TERMINALS = {"YIELD_SUCCESS", "YIELD_FAIL"}


def validate(record: dict) -> list[str]:
    errors: list[str] = []

    for field in ["skill", "scenes", "logic_steps"]:
        if field not in record:
            errors.append(f"missing top-level field: {field}")
    if errors:
        return errors

    skill = record["skill"]
    scenes = record["scenes"]
    steps = record["logic_steps"]

    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes must be a non-empty list")
    if not isinstance(steps, list) or not steps:
        errors.append("logic_steps must be a non-empty list")
    if errors:
        return errors

    scene_ids = [s.get("scene_id") for s in scenes]
    step_ids = [s.get("logic_step_id") for s in steps]
    scene_id_set = set(scene_ids)
    step_id_set = set(step_ids)

    if len(scene_ids) != len(scene_id_set):
        errors.append("duplicate scene_id")
    if len(step_ids) != len(step_id_set):
        errors.append("duplicate logic_step_id")

    entry_scene = skill.get("entry_scene_id")
    if entry_scene not in scene_id_set:
        errors.append(f"entry_scene_id not found: {entry_scene}")

    for sid in skill.get("subscenes", []):
        if sid not in scene_id_set:
            errors.append(f"subscene not found: {sid}")

    for scene in scenes:
        scene_id = scene.get("scene_id")
        if scene.get("scene_type") not in SCENE_TYPES:
            errors.append(f"{scene_id}: invalid scene_type {scene.get('scene_type')}")

        contained = set(scene.get("contained_logic_steps", []))
        entry_step = scene.get("entry_logic_step_id")
        if entry_step not in contained:
            errors.append(f"{scene_id}: entry_logic_step_id not in contained_logic_steps")
        for lid in contained:
            if lid not in step_id_set:
                errors.append(f"{scene_id}: contained logic step not found: {lid}")
        for rule in scene.get("next_scene_rules", []):
            target = rule.get("target")
            # Compatibility note: the preferred schema uses scene targets here.
            # Some released annotations point directly to an in-scope logic step,
            # so the release validator accepts either in-scope node type.
            if target not in scene_id_set and target not in step_id_set and target not in SCENE_TERMINALS:
                errors.append(f"{scene_id}: invalid next_scene target {target}")

    for step in steps:
        step_id = step.get("logic_step_id")
        if step.get("act_type") not in ACT_TYPES:
            errors.append(f"{step_id}: invalid act_type {step.get('act_type')}")
        if step.get("resource_scope") not in RESOURCE_SCOPES:
            errors.append(f"{step_id}: invalid resource_scope {step.get('resource_scope')}")
        for rule in step.get("next_step_rules", []):
            target = rule.get("target")
            if target not in step_id_set and target not in STEP_TERMINALS:
                errors.append(f"{step_id}: invalid next_step target {target}")

    return errors


def iter_records(path: Path) -> list[tuple[str, dict[str, Any]]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        records = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            record = row.get("ssl_record", row)
            records.append((f"{path}:{line_no}", record))
        return records

    obj = json.loads(text)
    if isinstance(obj, dict) and "ssl_record" in obj:
        obj = obj["ssl_record"]
    return [(str(path), obj)]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/validate_ssl_record.py <record.json|records.jsonl>")
    path = Path(sys.argv[1])
    failures: list[tuple[str, list[str]]] = []
    checked = 0
    for label, record in iter_records(path):
        checked += 1
        if not isinstance(record, dict):
            failures.append((label, ["record must be a JSON object"]))
            continue
        errors = validate(record)
        if errors:
            failures.append((label, errors))
    if failures:
        print(f"FAIL: {path}")
        for label, errors in failures[:20]:
            print(f"- {label}")
            for error in errors:
                print(f"  - {error}")
        if len(failures) > 20:
            print(f"- ... {len(failures) - 20} more failing records")
        raise SystemExit(1)
    print(f"OK: {path} ({checked} record(s))")


if __name__ == "__main__":
    main()
