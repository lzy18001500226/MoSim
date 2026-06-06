"""WorkspaceManager: file-backed workspace and target management using YAML.

Design goals:
- Workspace metadata stored as YAML at workspaces/{name}/meta.yaml
- Active workspace marker stored at workspaces/.active
- No in-memory caching: all operations read/write files directly
- Lightweight hostname validation; accept IPs, CIDRs, hostnames
"""

import ipaddress
import logging
import re
import time
from pathlib import Path
from typing import List

import yaml


class WorkspaceError(Exception):
    pass


WORKSPACES_DIR_NAME = "workspaces"
NAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _safe_mkdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


class TargetManager:
    """Validate and normalize targets (IP, CIDR, hostname).

    Hostname validation is intentionally light: allow letters, digits, hyphens, dots.
    """

    HOST_RE = re.compile(r"^[A-Za-z0-9.-]{1,253}$")

    @staticmethod
    def normalize_target(value: str) -> str:
        v = value.strip()
        # try CIDR or IP
        try:
            if "/" in v:
                net = ipaddress.ip_network(v, strict=False)
                return str(net)
            else:
                ip = ipaddress.ip_address(v)
                return str(ip)
        except Exception:
            # fallback to hostname validation (light)
            if TargetManager.HOST_RE.match(v) and ".." not in v:
                return v.lower()
            raise WorkspaceError(f"Invalid target: {value}") from None

    @staticmethod
    def validate(value: str) -> bool:
        try:
            TargetManager.normalize_target(value)
            return True
        except WorkspaceError:
            return False


class WorkspaceManager:
    """File-backed workspace manager. No persistent in-memory state.

    Root defaults to current working directory.
    """

    def __init__(self, root: Path = Path(".")):
        self.root = Path(root)
        self.workspaces_dir = self.root / WORKSPACES_DIR_NAME
        _safe_mkdir(self.workspaces_dir)

    def validate_name(self, name: str):
        if not NAME_RE.match(name):
            raise WorkspaceError(
                "Invalid workspace name; allowed characters: A-Za-z0-9._- (1-64 chars)"
            )
        # prevent path traversal and slashes
        if "/" in name or ".." in name:
            raise WorkspaceError("Invalid workspace name; must not contain '/' or '..'")

    def workspace_path(self, name: str) -> Path:
        self.validate_name(name)
        return self.workspaces_dir / name

    def meta_path(self, name: str) -> Path:
        return self.workspace_path(name) / "meta.yaml"

    def active_marker(self) -> Path:
        return self.workspaces_dir / ".active"

    def create(self, name: str) -> dict:
        self.validate_name(name)
        p = self.workspace_path(name)
        # create required dirs
        for sub in (
            "loot",
            "knowledge/sources",
            "knowledge/embeddings",
            "notes",
            "memory",
        ):
            _safe_mkdir(p / sub)

        # initialize meta if missing
        if not self.meta_path(name).exists():
            meta = {
                "name": name,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "targets": [],
            }
            self._write_meta(name, meta)
            return meta
        return self._read_meta(name)

    def _read_meta(self, name: str) -> dict:
        mp = self.meta_path(name)
        if not mp.exists():
            return {"name": name, "targets": []}
        try:
            data = yaml.safe_load(mp.read_text(encoding="utf-8"))
            if data is None:
                return {"name": name, "targets": []}
            # ensure keys
            data.setdefault("name", name)
            data.setdefault("targets", [])
            return data
        except Exception as e:
            raise WorkspaceError(f"Failed to read meta for {name}: {e}") from e

    def _write_meta(self, name: str, meta: dict):
        mp = self.meta_path(name)
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")

    def set_active(self, name: str):
        # ensure workspace exists
        self.create(name)
        marker = self.active_marker()
        marker.write_text(name, encoding="utf-8")
        # update last_active_at in meta.yaml
        try:
            meta = self._read_meta(name)
            meta["last_active_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            # ensure operator_notes and tool_runs exist
            meta.setdefault("operator_notes", "")
            meta.setdefault("tool_runs", [])
            self._write_meta(name, meta)
        except Exception as e:
            # Non-fatal - don't block activation on meta write errors, but log for visibility
            logging.getLogger(__name__).exception(
                "Failed to update meta.yaml for workspace '%s': %s", name, e
            )
            try:
                # Emit operator-visible notification if UI present
                from ..interface.notifier import notify

                notify("warning", f"Failed to update workspace meta for '{name}': {e}")
            except Exception:
                # ignore notifier failures
                pass

    def set_operator_note(self, name: str, note: str) -> dict:
        """Append or set operator_notes for a workspace (plain text)."""
        meta = self._read_meta(name)
        prev = meta.get("operator_notes", "") or ""
        if prev:
            new = prev + "\n" + note
        else:
            new = note
        meta["operator_notes"] = new
        self._write_meta(name, meta)
        return meta

    def get_meta_field(self, name: str, field: str):
        meta = self._read_meta(name)
        return meta.get(field)

    def get_active(self) -> str:
        marker = self.active_marker()
        if not marker.exists():
            return ""
        return marker.read_text(encoding="utf-8").strip()

    def list_workspaces(self) -> List[str]:
        if not self.workspaces_dir.exists():
            return []
        return [p.name for p in self.workspaces_dir.iterdir() if p.is_dir()]

    def get_meta(self, name: str) -> dict:
        return self._read_meta(name)

    def add_targets(self, name: str, values: List[str]) -> List[str]:
        # read-modify-write for strict file-backed behavior
        meta = self._read_meta(name)
        existing = set(meta.get("targets", []))
        changed = False
        for v in values:
            norm = TargetManager.normalize_target(v)
            if norm not in existing:
                existing.add(norm)
                changed = True
        if changed:
            meta["targets"] = sorted(existing)
            self._write_meta(name, meta)
        return meta.get("targets", [])

    def set_last_target(self, name: str, value: str) -> str:
        """Set the workspace's last used target and ensure it's in the targets list."""
        norm = TargetManager.normalize_target(value)
        meta = self._read_meta(name)
        # ensure targets contains it
        existing = set(meta.get("targets", []))
        if norm not in existing:
            existing.add(norm)
            meta["targets"] = sorted(existing)
        meta["last_target"] = norm
        self._write_meta(name, meta)
        return norm

    def remove_target(self, name: str, value: str) -> List[str]:
        meta = self._read_meta(name)
        existing = set(meta.get("targets", []))
        norm = TargetManager.normalize_target(value)
        if norm in existing:
            existing.remove(norm)
            meta["targets"] = sorted(existing)
            self._write_meta(name, meta)
        return meta.get("targets", [])

    def list_targets(self, name: str) -> List[str]:
        meta = self._read_meta(name)
        return meta.get("targets", [])
