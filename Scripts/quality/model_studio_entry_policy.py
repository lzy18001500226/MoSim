"""Load and validate the Model Studio semantic-entry promotion policy."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ENTRY_POLICY_PATH = ROOT / "Config" / "control_platform" / "model_studio_entry_policy_v1.toml"
REQUIRED_SEMANTIC_FIELDS = (
    "scheme_id",
    "display_name_zh",
    "display_name_en",
    "category",
    "entry_type",
    "role",
    "implementation_status",
    "selection_eligibility",
    "execution_kind",
)
# The current-model map is a route/mapping source, not the catalog's display
# source. It intentionally reuses the semantic fields except for the English
# label, which is owned by control_scheme_catalog.json.
MODEL_MAP_REQUIRED_FIELDS = tuple(field for field in REQUIRED_SEMANTIC_FIELDS if field != "display_name_en")
GRAPHICAL_BATCH_MODE = "current_graphical_runner_batch"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"semantic policy source must be a JSON object: {path}")
    return value


def _repo_file(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is missing")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"{label} must be repository-relative: {value}")
    path = (root / relative).resolve()
    if not path.is_file():
        raise ValueError(f"{label} does not exist: {value}")
    return path


def _scheme_rows(
    document: dict[str, Any],
    label: str,
    expected_count: int,
    *,
    required_fields: tuple[str, ...] = REQUIRED_SEMANTIC_FIELDS,
) -> dict[str, dict[str, Any]]:
    rows = document.get("schemes")
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise ValueError(f"{label} must contain exactly {expected_count} scheme rows")
    indexed: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        for field in required_fields:
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label}[{index}] is missing semantic field {field}")
        scheme_id = str(row["scheme_id"])
        if scheme_id in indexed:
            raise ValueError(f"{label} contains duplicate scheme_id: {scheme_id}")
        indexed[scheme_id] = row
    return indexed


def load_entry_policy(root: Path = ROOT) -> dict[str, Any]:
    """Return the validated policy plus its semantic source documents."""

    root = root.resolve()
    policy_path = root / ENTRY_POLICY_PATH.relative_to(ROOT)
    try:
        policy = tomllib.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"cannot read Model Studio entry policy: {policy_path}") from exc
    if policy.get("schema") != "mosim.model_studio_entry_policy.v1" or policy.get("version") != 1:
        raise ValueError("invalid_model_studio_entry_policy_schema")
    if policy.get("active_entry_mode") not in {
        "legacy_baseline_until_semantic_complete",
        GRAPHICAL_BATCH_MODE,
    }:
        raise ValueError("unsupported_model_studio_entry_mode")

    count = policy.get("new_semantic_entry_count")
    if count != 48:
        raise ValueError("model_studio_semantic_entry_count_must_be_48")
    semantic_source = _repo_file(root, policy.get("new_semantic_source"), "new_semantic_source")
    semantic_catalog = _read_json(semantic_source)
    semantic_rows = _scheme_rows(semantic_catalog, "new_semantic_source.schemes", count)

    model_source = _repo_file(root, policy.get("new_model_source"), "new_model_source")
    model_map = _read_json(model_source)
    model_rows = _scheme_rows(
        model_map,
        "new_model_source.schemes",
        count,
        required_fields=MODEL_MAP_REQUIRED_FIELDS,
    )
    if set(model_rows) != set(semantic_rows):
        raise ValueError("semantic catalog and current model map scheme ids differ")
    for scheme_id, row in model_rows.items():
        row["display_name_en"] = semantic_rows[scheme_id]["display_name_en"]

    legacy_ids = policy.get("legacy_controller_ids")
    if not isinstance(legacy_ids, list) or not legacy_ids or not all(isinstance(item, str) for item in legacy_ids):
        raise ValueError("model_studio_legacy_controller_ids_missing")
    legacy_id_set = set(legacy_ids)
    legacy_entries = policy.get("legacy_entry")
    if not isinstance(legacy_entries, list) or {item.get("controller_id") for item in legacy_entries if isinstance(item, dict)} != legacy_id_set:
        raise ValueError("model_studio_legacy_entries_do_not_match_ids")
    legacy_by_id: dict[str, dict[str, Any]] = {}
    for entry in legacy_entries:
        if not isinstance(entry, dict):
            raise ValueError("model_studio_legacy_entry_must_be_an_object")
        controller_id = entry.get("controller_id")
        if controller_id in legacy_by_id:
            raise ValueError(f"duplicate legacy controller id: {controller_id}")
        for field in ("task_runner_file", "codegen_model_file", "task_runner_class", "codegen_model_class", "boundary"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise ValueError(f"legacy entry {controller_id} is missing {field}")
        _repo_file(root, entry["task_runner_file"], f"legacy entry {controller_id} task_runner_file")
        _repo_file(root, entry["codegen_model_file"], f"legacy entry {controller_id} codegen_model_file")
        legacy_by_id[str(controller_id)] = entry

    complete = policy.get("new_semantic_entries_complete")
    if not isinstance(complete, bool):
        raise ValueError("new_semantic_entries_complete must be boolean")
    completed_ids = policy.get("completed_active_controller_ids", [])
    if not isinstance(completed_ids, list) or not all(isinstance(item, str) for item in completed_ids):
        raise ValueError("completed_active_controller_ids must be a string list")
    graphical_ids = policy.get("current_graphical_active_controller_ids", [])
    if policy.get("active_entry_mode") == GRAPHICAL_BATCH_MODE:
        graphical_count = policy.get("current_graphical_entry_count")
        if not isinstance(graphical_count, int) or graphical_count <= 0:
            raise ValueError("current_graphical_entry_count must be a positive integer")
        if not isinstance(graphical_ids, list) or len(graphical_ids) != graphical_count:
            raise ValueError(
                "current_graphical_active_controller_ids must contain "
                f"{graphical_count} entries"
            )
        if len(set(graphical_ids)) != len(graphical_ids):
            raise ValueError("current_graphical_active_controller_ids must be unique")
        if not set(graphical_ids).issubset(set(semantic_rows) - legacy_id_set):
            raise ValueError("current graphical batch contains a non-candidate controller")
    if complete:
        manifest_path = _repo_file(root, policy.get("semantic_completion_manifest"), "semantic_completion_manifest")
        manifest = _read_json(manifest_path)
        if manifest.get("status") != "complete" or manifest.get("completed_count") != count:
            raise ValueError("semantic completion manifest does not prove all 48 entries")
        manifest_ids = manifest.get("scheme_ids")
        if not isinstance(manifest_ids, list) or set(manifest_ids) != set(semantic_rows):
            raise ValueError("semantic completion manifest scheme ids do not match the catalog")
        if set(completed_ids) != set(semantic_rows):
            raise ValueError("completed_active_controller_ids must contain all 48 semantic ids")

    policy["_semantic_catalog"] = semantic_catalog
    policy["_model_entry_map"] = model_map
    policy["_semantic_rows"] = semantic_rows
    policy["_model_rows"] = model_rows
    policy["_legacy_by_id"] = legacy_by_id
    return policy


def active_controller_ids(policy: dict[str, Any]) -> frozenset[str]:
    """Return controller ids allowed to enter the active Model Studio path."""

    if not policy["new_semantic_entries_complete"]:
        if policy.get("active_entry_mode") == GRAPHICAL_BATCH_MODE:
            return frozenset(
                str(item)
                for item in (
                    list(policy["legacy_controller_ids"])
                    + list(policy["current_graphical_active_controller_ids"])
                )
            )
        return frozenset(str(item) for item in policy["legacy_controller_ids"])
    return frozenset(str(item) for item in policy["completed_active_controller_ids"])


def controller_is_active(policy: dict[str, Any], controller_id: str) -> bool:
    return controller_id in active_controller_ids(policy)


def legacy_entry(policy: dict[str, Any], controller_id: str) -> dict[str, Any] | None:
    entry = policy.get("_legacy_by_id", {}).get(controller_id)
    return dict(entry) if isinstance(entry, dict) else None
