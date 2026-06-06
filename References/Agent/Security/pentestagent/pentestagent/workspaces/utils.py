"""Utilities to route loot/output into the active workspace or global loot.

All functions are file-backed and do not cache the active workspace selection.
This module will emit a single warning per run if no active workspace is set.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional

from .manager import WorkspaceManager

_WARNED = False
_WARNED_CONV = False


def get_conversations_base(root: Optional[Path] = None) -> Path:
    """Return the conversations directory: workspaces/{active}/memory/conversations or top-level conversations/.

    Emits a single warning if no workspace is active.
    """
    global _WARNED_CONV
    root = Path(root or "./")
    wm = WorkspaceManager(root=root)
    active = wm.get_active()
    if active:
        base = root / "workspaces" / active / "memory" / "conversations"
    else:
        if not _WARNED_CONV:
            logging.warning(
                "No active workspace — writing conversations to global conversations/ directory."
            )
            _WARNED_CONV = True
        base = root / "conversations"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_loot_base(root: Optional[Path] = None) -> Path:
    """Return the base loot directory: workspaces/{active}/loot or top-level `loot/`.

    Emits a single warning if no workspace is active.
    """
    global _WARNED
    root = Path(root or "./")
    wm = WorkspaceManager(root=root)
    active = wm.get_active()
    if active:
        base = root / "workspaces" / active / "loot"
    else:
        if not _WARNED:
            logging.warning(
                "No active workspace — writing loot to global loot/ directory."
            )
            _WARNED = True
        base = root / "loot"
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_loot_file(relpath: str, root: Optional[Path] = None) -> Path:
    """Return a Path for a file under the loot base, creating parent dirs.

    Example: get_loot_file('artifacts/example.log')
    """
    base = get_loot_base(root=root)
    p = base / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def resolve_knowledge_paths(root: Optional[Path] = None) -> dict:
    """Resolve knowledge-related paths, preferring active workspace if present.

    Returns a dict with keys: base, sources, embeddings, graph, index, using_workspace
    """
    root = Path(root or "./")
    wm = WorkspaceManager(root=root)
    active = wm.get_active()

    global_base = root / "knowledge"
    workspace_base = root / "workspaces" / active / "knowledge" if active else None

    use_workspace = False
    if workspace_base and workspace_base.exists():
        # prefer workspace if it has any content (explicit opt-in)
        try:
            # Use a non-recursive check to avoid walking the entire directory tree
            if any(workspace_base.iterdir()):
                use_workspace = True
            # Also allow an explicit opt-in marker file .use_workspace
            elif (workspace_base / ".use_workspace").exists():
                use_workspace = True
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Error while checking workspace knowledge directory: %s", e
            )
            use_workspace = False

    if use_workspace:
        base = workspace_base
    else:
        base = global_base

    paths = {
        "base": base,
        "sources": base / "sources",
        "embeddings": base / "embeddings",
        "graph": base / "graph",
        "index": base / "index",
        "using_workspace": use_workspace,
    }

    return paths


def get_session_file(root: Optional[Path] = None) -> Path:
    """Return the path to session.json for the active workspace.

    Stores at workspaces/{active}/memory/session.json or conversations/session.json
    (global fallback), alongside the conversations directory.
    """
    root = Path(root or "./")
    wm = WorkspaceManager(root=root)
    active = wm.get_active()
    if active:
        base = root / "workspaces" / active / "memory"
    else:
        base = root / "conversations"
    base.mkdir(parents=True, exist_ok=True)
    return base / "session.json"


def get_preferences_file(root: Optional[Path] = None) -> Path:
    """Return the path to prefs.json for the active workspace.

    Stores at workspaces/{active}/memory/prefs.json or conversations/prefs.json
    (global fallback), alongside session.json.
    """
    root = Path(root or "./")
    wm = WorkspaceManager(root=root)
    active = wm.get_active()
    if active:
        base = root / "workspaces" / active / "memory"
    else:
        base = root / "conversations"
    base.mkdir(parents=True, exist_ok=True)
    return base / "prefs.json"


def export_workspace(
    name: str, output: Optional[Path] = None, root: Optional[Path] = None
) -> Path:
    """Create a deterministic tar.gz archive of workspaces/{name}/ and return the archive path.

    Excludes __pycache__ and *.pyc. Does not mutate workspace.
    """
    import tarfile

    root = Path(root or "./")
    ws_dir = root / "workspaces" / name
    if not ws_dir.exists() or not ws_dir.is_dir():
        raise FileNotFoundError(f"Workspace not found: {name}")

    out_path = Path(output) if output else Path(f"{name}-workspace.tar.gz")

    # Use deterministic ordering
    entries = []
    for p in ws_dir.rglob("*"):
        # skip __pycache__ and .pyc
        if "__pycache__" in p.parts:
            continue
        if p.suffix == ".pyc":
            continue
        rel = p.relative_to(root)
        entries.append(rel)

    entries = sorted(entries, key=str)

    # Create tar.gz
    with tarfile.open(out_path, "w:gz") as tf:
        for rel in entries:
            full = root / rel
            # store with relative path (preserve workspaces/<name>/...)
            tf.add(str(full), arcname=str(rel))

    return out_path


def import_workspace(archive: Path, root: Optional[Path] = None) -> str:
    """Import a workspace tar.gz into workspaces/. Returns workspace name.

    Fails if workspace already exists. Requires meta.yaml present in archive.
    """
    import tarfile
    import tempfile

    root = Path(root or "./")
    archive = Path(archive)
    if not archive.exists():
        raise FileNotFoundError(f"Archive not found: {archive}")

    with tempfile.TemporaryDirectory() as td:
        tdpath = Path(td)
        with tarfile.open(archive, "r:gz") as tf:
            tf.extractall(path=tdpath)

        # Look for workspaces/<name>/meta.yaml or meta.yaml at root
        candidates = list(tdpath.rglob("meta.yaml"))
        if not candidates:
            raise ValueError("No meta.yaml found in archive")
        meta_file = candidates[0]
        # read name
        import yaml

        meta = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
        if not meta or not meta.get("name"):
            raise ValueError("meta.yaml missing 'name' field")
        name = meta["name"]

        dest = root / "workspaces" / name
        if dest.exists():
            raise FileExistsError(f"Workspace already exists: {name}")

        # Move extracted tree into place
        # Find root folder under tdpath that contains the workspace files
        # If archive stored paths with workspaces/<name>/..., move that subtree
        candidate_root = None
        for p in tdpath.iterdir():
            if p.is_dir() and p.name == "workspaces":
                candidate_root = p / name
                break
        if candidate_root and candidate_root.exists():
            # move candidate_root to dest (use shutil.move to support cross-filesystem)
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(candidate_root), str(dest))
            except Exception as e:
                raise RuntimeError(
                    f"Failed to move workspace subtree into place: {e}"
                ) from e
        else:
            # Otherwise, assume contents are directly the workspace folder
            # move the parent of meta_file (or its containing dir)
            src = meta_file.parent
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dest))
            except Exception as e:
                raise RuntimeError(
                    f"Failed to move extracted workspace into place: {e}"
                ) from e

    return name
