"""Notes tool for PentestAgent - persistent key findings storage."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from ..registry import ToolSchema, register_tool

# Notes storage - kept at loot root for easy access
_notes: Dict[str, Dict[str, Any]] = {}
# Optional override (tests can call set_notes_file)
_custom_notes_file: Path | None = None
# Lock for safe concurrent access from multiple agents (asyncio since agents are async tasks)
_notes_lock = asyncio.Lock()


def _notes_file_path() -> Path:
    from ...workspaces.utils import get_loot_file

    if _custom_notes_file:
        return _custom_notes_file
    return get_loot_file("notes.json")


def _load_notes_unlocked() -> None:
    """Load notes from file (caller must hold lock)."""
    global _notes
    nf = _notes_file_path()
    if nf.exists():
        try:
            loaded = json.loads(nf.read_text(encoding="utf-8"))
            # Migration: Convert legacy string values to dicts
            _notes = {}
            for k, v in loaded.items():
                if isinstance(v, str):
                    _notes[k] = {
                        "content": v,
                        "category": "info",
                        "confidence": "medium",
                    }
                else:
                    _notes[k] = v
        except (json.JSONDecodeError, IOError):
            _notes = {}


def _save_notes_unlocked() -> None:
    """Save notes to file (caller must hold lock)."""
    nf = _notes_file_path()
    nf.parent.mkdir(parents=True, exist_ok=True)
    nf.write_text(json.dumps(_notes, indent=2), encoding="utf-8")


async def get_all_notes() -> Dict[str, Dict[str, Any]]:
    """Get all notes (for TUI /notes command)."""
    async with _notes_lock:
        if not _notes:
            _load_notes_unlocked()
        return _notes.copy()


def get_all_notes_sync() -> Dict[str, Dict[str, Any]]:
    """Get all notes synchronously (read-only, best effort for prompts)."""
    # If notes are empty, try to load from disk (safe read)
    if not _notes and _notes_file_path().exists():
        try:
            loaded = json.loads(_notes_file_path().read_text(encoding="utf-8"))
            # Migration for sync read
            result = {}
            for k, v in loaded.items():
                if isinstance(v, str):
                    result[k] = {
                        "content": v,
                        "category": "info",
                        "confidence": "medium",
                    }
                else:
                    result[k] = v
            return result
        except (json.JSONDecodeError, IOError):
            pass
    return _notes.copy()


def set_notes_file(path: Path) -> None:
    """Set custom notes file path."""
    global _custom_notes_file
    _custom_notes_file = Path(path)
    # Can't use async here, so load without lock (called at init time)
    _load_notes_unlocked()


# Defer loading until first access to avoid caching active workspace path at import


# Validation schema - declarative rules for note structure
HOST_SPECIFIC_FIELDS = {"services", "endpoints", "technologies", "port"}

CATEGORY_REQUIREMENTS = {
    "credential": {
        "required": ["username", "target"],
        "one_of": [["password", "protocol"]],
    },
    "vulnerability": {
        "required": ["target"],
        "one_of": [["cve", "weaknesses"]],
    },
    "finding": {
        "required": ["target"],
        "one_of": [["services", "endpoints", "technologies", "port"]],
    },
}


def _validate_note_schema(category: str, metadata: Dict[str, Any]) -> str | None:
    """
    Validate note schema based on declarative rules.

    Returns:
        Error message if validation fails, None if valid
    """
    # Check if note has host-specific structured data
    has_host_data = bool(HOST_SPECIFIC_FIELDS & metadata.keys())

    # If note has host-specific data, require target
    if has_host_data and not metadata.get("target"):
        fields = ", ".join(f"'{f}'" for f in HOST_SPECIFIC_FIELDS if f in metadata)
        return f"Error: 'target' field is required when providing host-specific data ({fields})."

    # Apply category-specific validation rules
    if category in CATEGORY_REQUIREMENTS:
        rules = CATEGORY_REQUIREMENTS[category]

        # Check required fields
        for field in rules.get("required", []):
            if not metadata.get(field):
                return f"Error: '{field}' field is required for category '{category}'."

        # Check one_of constraints (at least one field from each group must be present)
        for field_group in rules.get("one_of", []):
            if not any(metadata.get(field) for field in field_group):
                field_list = "' or '".join(field_group)
                return f"Error: At least one of '{field_list}' is required for category '{category}'."

    return None


@register_tool(
    name="notes",
    description="Manage persistent notes for key findings. Actions: create, read, update, delete, list (2 options, all or the truncated text to 60 characters).",
    schema=ToolSchema(
        properties={
            "action": {
                "type": "string",
                "enum": [
                    "create",
                    "read",
                    "update",
                    "delete",
                    "list_all",
                    "list_truncated",
                ],
                "description": "The action to perform",
            },
            "key": {
                "type": "string",
                "description": "Note identifier (e.g., 'creds_ssh', 'open_ports', 'vuln_sqli')",
            },
            "value": {
                "type": "string",
                "description": "Note content (for create/update)",
            },
            "category": {
                "type": "string",
                "enum": [
                    "finding",
                    "credential",
                    "task",
                    "info",
                    "vulnerability",
                    "artifact",
                ],
                "description": "Category for organization (default: info)",
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "Confidence level (default: medium)",
            },
            "status": {
                "type": "string",
                "enum": ["open", "closed", "filtered", "confirmed", "potential"],
                "description": "Status of the finding (e.g., 'open' for ports, 'closed' for dead services). Default: confirmed/open.",
            },
            "source": {
                "type": "string",
                "description": "Source IP/Hostname where the finding originated (e.g., where creds were found)",
            },
            "target": {
                "type": "string",
                "description": "Target IP/Hostname the finding applies to (e.g., the host with the open port)",
            },
            "username": {
                "type": "string",
                "description": "Username for credentials",
            },
            "password": {
                "type": "string",
                "description": "Password or hash for credentials",
            },
            "port": {
                "type": "string",
                "description": "Port number (e.g., 80, 443)",
            },
            "cve": {
                "type": "string",
                "description": "CVE ID for vulnerabilities",
            },
            "url": {
                "type": "string",
                "description": "URL associated with the finding (e.g., for web apps)",
            },
            "evidence_path": {
                "type": "string",
                "description": "Path to a screenshot or downloaded file supporting this finding",
            },
            "services": {
                "type": "array",
                "description": "Array of service objects with port, product, version",
                "items": {
                    "type": "object",
                    "properties": {
                        "port": {"type": "integer"},
                        "product": {"type": "string"},
                        "version": {"type": "string"},
                    },
                },
            },
            "technologies": {
                "type": "array",
                "description": "Array of technology objects with name, version",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                    },
                },
            },
            "endpoints": {
                "type": "array",
                "description": "Array of endpoint objects with path, methods",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "methods": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "weaknesses": {
                "type": "array",
                "description": "Array of weakness objects for WG stage",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "description": {"type": "string"},
                    },
                },
            },
            "affected_versions": {
                "type": "object",
                "description": "Version range constraints for vulnerabilities (e.g., {'PHP': '5.0.0 - 5.2.17'})",
            },
        },
        required=["action"],
    ),
    category="utility",
)
async def notes(arguments: dict, runtime) -> str:
    """
    Manage persistent notes.

    Args:
        arguments: Dictionary with action, key, value, category, confidence
        runtime: The runtime environment (unused)

    Returns:
        Result message
    """
    action = arguments["action"]
    key = arguments.get("key", "").strip()
    value = arguments.get("value", "")

    # Soft validation for category
    category = arguments.get("category", "info")
    valid_categories = [
        "finding",
        "credential",
        "task",
        "info",
        "vulnerability",
        "artifact",
    ]
    if category not in valid_categories:
        category = "info"

    confidence = arguments.get("confidence", "medium")
    status = arguments.get("status", "confirmed")

    # Extract structured metadata (supports nested structures)
    metadata = {}
    for field in [
        "source",
        "target",
        "username",
        "password",
        "port",
        "cve",
        "url",
        "evidence_path",
        "services",  # Array of service dicts: [{"port": 80, "product": "Apache", "version": "2.2.8"}]
        "technologies",  # Array of tech dicts: [{"name": "PHP", "version": "5.2.4"}]
        "endpoints",  # Array of endpoint dicts: [{"path": "/admin", "methods": ["GET", "POST"]}]
        "weaknesses",  # Array of weakness dicts for WG stage
        "affected_versions",  # Dict for version ranges
    ]:
        if field in arguments:
            metadata[field] = arguments[field]

    async with _notes_lock:
        if action == "create":
            if not key:
                return "Error: key is required for create"
            if not value:
                return "Error: value is required for create"
            if key in _notes:
                return f"Error: note '{key}' already exists. Use 'update' to modify."

            # Validate schema based on category
            validation_error = _validate_note_schema(category, metadata)
            if validation_error:
                return validation_error

            _notes[key] = {
                "content": value,
                "category": category,
                "confidence": confidence,
                "status": status,
                "metadata": metadata,
            }
            _save_notes_unlocked()
            return f"Created note '{key}' ({category}, {status})"

        elif action == "read":
            if not key:
                return "Error: key is required for read"
            if key not in _notes:
                return f"Note '{key}' not found"

            note = _notes[key]
            meta_str = (
                f" {json.dumps(note.get('metadata', {}))}"
                if note.get("metadata")
                else ""
            )
            status_str = f", {note.get('status', 'confirmed')}"
            return f"[{key}] ({note['category']}, {note['confidence']}{status_str}) {note['content']}{meta_str}"

        elif action == "update":
            if not key:
                return "Error: key is required for update"
            if not value:
                return "Error: value is required for update"

            existed = key in _notes

            # Validate schema based on category
            validation_error = _validate_note_schema(category, metadata)
            if validation_error:
                return validation_error

            # Merge metadata if updating? For now, overwrite to keep it simple and consistent with content
            _notes[key] = {
                "content": value,
                "category": category,
                "confidence": confidence,
                "status": status,
                "metadata": metadata,
            }
            _save_notes_unlocked()
            return f"{'Updated' if existed else 'Created'} note '{key}'"

        elif action == "delete":
            if not key:
                return "Error: key is required for delete"
            if key not in _notes:
                return f"Note '{key}' not found"

            del _notes[key]
            _save_notes_unlocked()
            return f"Deleted note '{key}'"

        elif action == "list_all" or action == "list_truncated":
            if not _notes:
                return "No notes saved"

            lines = [f"Notes ({len(_notes)} entries):"]

            # Group by category for display
            by_category = {}
            for k, v in _notes.items():
                cat = v["category"]
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append((k, v))

            for cat in sorted(by_category.keys()):
                lines.append(f"\n## {cat.title()}")
                for k, v in by_category[cat]:
                    content = v["content"]

                    display_val = content
                    if action == "list_truncated":
                        display_val = (
                            content if len(content) <= 60 else content[:57] + "..."
                        )

                    conf = v.get("confidence", "medium")
                    lines.append(f"  [{k}] ({conf}) {display_val}")

            return "\n".join(lines)

        else:
            return f"Unknown action: {action}"
