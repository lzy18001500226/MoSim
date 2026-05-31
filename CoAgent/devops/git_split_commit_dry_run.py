#!/usr/bin/env python3
"""Dry-run sequential split integration using a temporary Git index.

This helper is intentionally conservative:

- it never updates refs;
- it never touches the live Git index;
- it never touches the worktree;
- it does not create commits.

It does write temporary tree objects via `git write-tree`, matching the
existing split-index checker. Those objects are unreachable unless a later,
explicit, reviewed integration step uses them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

BATCH_ORDER = [
    "policy_status_docs",
    "architecture_decisions_research",
    "runtime_protocol_bootstrap",
    "dispatch_transport_context_memory",
    "review_gateway_status",
    "guardrails_doctor_automation",
    "knowledge_devops",
    "tests",
    "task_artifacts",
    "other",
]


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def run(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env={**os.environ, **(env or {})},
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "timeout": True,
            "command": command,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "command": command,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def read_paths(path: Path) -> list[str]:
    resolved = project_path(path)
    values: list[str] = []
    for line in resolved.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        project_path(Path(stripped))
        values.append(stripped)
    return sorted(dict.fromkeys(values))


def index_fingerprint() -> dict[str, Any]:
    git_dir = run(["git", "rev-parse", "--git-dir"])
    if not git_dir["ok"]:
        raise SystemExit(f"git rev-parse --git-dir failed: {git_dir}")
    index_path = project_path(Path(git_dir["stdout"].strip()) / "index")
    data = index_path.read_bytes() if index_path.exists() else b""
    return {
        "path": rel(index_path),
        "exists": index_path.exists(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def git_oid(command: list[str]) -> str:
    result = run(command)
    if not result["ok"]:
        raise SystemExit(f"git command failed: {result}")
    return result["stdout"].strip()


def status_for_paths(paths: list[str]) -> list[dict[str, str]]:
    if not paths:
        return []
    result = run(["git", "status", "--porcelain=v1", "--"] + paths)
    if not result["ok"]:
        raise SystemExit(f"git status failed: {result}")
    items: list[dict[str, str]] = []
    for line in result["stdout"].splitlines():
        if not line:
            continue
        raw_path = line[3:]
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        items.append({"status": line[:2], "path": raw_path})
    return items


def staged_entries(paths: list[str]) -> dict[str, dict[str, str]]:
    if not paths:
        return {}
    result = run(["git", "ls-files", "-s", "--"] + paths)
    if not result["ok"]:
        raise SystemExit(f"git ls-files failed: {result}")
    entries: dict[str, dict[str, str]] = {}
    for line in result["stdout"].splitlines():
        parts = line.split(None, 3)
        if len(parts) != 4:
            continue
        mode, oid, stage, path = parts
        if stage != "0":
            raise SystemExit(f"unsupported non-zero index stage for {path}: {stage}")
        entries[path] = {"mode": mode, "oid": oid, "stage": stage}
    return entries


def staged_removals(paths: list[str], entries: dict[str, dict[str, str]], status: list[dict[str, str]]) -> list[str]:
    status_by_path = {item["path"]: item["status"] for item in status}
    removals: list[str] = []
    for path in paths:
        if path in entries:
            continue
        if status_by_path.get(path, "  ")[0] == "D":
            removals.append(path)
    return sorted(removals)


def discover_batch_files(batch_list_dir: Path) -> list[tuple[str, Path]]:
    directory = project_path(batch_list_dir)
    by_name = {
        path.name.removesuffix(".staged.paths"): path
        for path in directory.glob("*.staged.paths")
        if path.name != "overlap.staged.paths"
    }
    ordered: list[tuple[str, Path]] = []
    for name in BATCH_ORDER:
        path = by_name.pop(name, None)
        if path:
            ordered.append((name, path))
    for name in sorted(by_name):
        ordered.append((name, by_name[name]))
    return ordered


def apply_batch_to_temp_index(paths: list[str], temp_index: Path) -> dict[str, Any]:
    status = status_for_paths(paths)
    entries = staged_entries(paths)
    removals = staged_removals(paths, entries, status)
    missing_staged = sorted(path for path in paths if path not in entries and path not in removals)
    if entries:
        update_lines = [f"{entry['mode']} {entry['oid']}\t{path}" for path, entry in sorted(entries.items())]
        update_index = run(
            ["git", "update-index", "--index-info"],
            env={"GIT_INDEX_FILE": str(temp_index)},
            input_text="\n".join(update_lines) + "\n",
        )
        if not update_index["ok"]:
            raise SystemExit(f"git update-index failed: {update_index}")
    if removals:
        remove_result = run(
            ["git", "update-index", "--force-remove", "--"] + removals,
            env={"GIT_INDEX_FILE": str(temp_index)},
        )
        if not remove_result["ok"]:
            raise SystemExit(f"git update-index --force-remove failed: {remove_result}")
    overlap = sorted(
        item["path"]
        for item in status
        if item["status"][0] not in {" ", "?"} and item["status"][1] not in {" "}
    )
    return {
        "staged_entry_count": len(entries),
        "staged_removal_count": len(removals),
        "missing_staged": missing_staged,
        "overlap": overlap,
        "overlap_count": len(overlap),
    }


def diff_summary(previous_tree: str, next_tree: str) -> dict[str, Any]:
    stat = run(["git", "diff-tree", "--stat", "--summary", previous_tree, next_tree])
    names = run(["git", "diff-tree", "--name-status", "-r", previous_tree, next_tree])
    if not stat["ok"]:
        raise SystemExit(f"git diff-tree --stat failed: {stat}")
    if not names["ok"]:
        raise SystemExit(f"git diff-tree --name-status failed: {names}")
    changed_files = [line for line in names["stdout"].splitlines() if line.strip()]
    return {
        "changed_file_count": len(changed_files),
        "name_status": changed_files[:200],
        "stat": stat["stdout"].strip(),
    }


def dry_run(batch_list_dir: Path, output: Path | None = None) -> dict[str, Any]:
    batches = discover_batch_files(batch_list_dir)
    head_before = git_oid(["git", "rev-parse", "HEAD"])
    head_tree = git_oid(["git", "rev-parse", "HEAD^{tree}"])
    live_index_tree_before = git_oid(["git", "write-tree"])
    index_before = index_fingerprint()
    batch_results: list[dict[str, Any]] = []
    previous_tree = head_tree
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        temp_index = Path(tmp) / "index"
        read_tree = run(["git", "read-tree", "HEAD"], env={"GIT_INDEX_FILE": str(temp_index)})
        if not read_tree["ok"]:
            raise SystemExit(f"git read-tree failed: {read_tree}")
        for sequence, (name, paths_file) in enumerate(batches, start=1):
            paths = read_paths(paths_file)
            apply_result = apply_batch_to_temp_index(paths, temp_index)
            write_tree = run(["git", "write-tree"], env={"GIT_INDEX_FILE": str(temp_index)})
            if not write_tree["ok"]:
                raise SystemExit(f"git write-tree failed: {write_tree}")
            tree_oid = write_tree["stdout"].strip()
            diff = diff_summary(previous_tree, tree_oid)
            batch_results.append(
                {
                    "sequence": sequence,
                    "batch": name,
                    "paths_file": rel(project_path(paths_file)),
                    "path_count": len(paths),
                    "tree_oid": tree_oid,
                    "previous_tree_oid": previous_tree,
                    "changed_file_count": diff["changed_file_count"],
                    "diff_stat": diff["stat"],
                    "name_status": diff["name_status"],
                    **apply_result,
                    "ok": not apply_result["missing_staged"],
                }
            )
            previous_tree = tree_oid
    head_after = git_oid(["git", "rev-parse", "HEAD"])
    live_index_tree_after = git_oid(["git", "write-tree"])
    index_after = index_fingerprint()
    live_index_tree_unchanged = live_index_tree_before == live_index_tree_after
    live_index_fingerprint_unchanged = index_before == index_after
    live_state_unchanged = head_before == head_after and live_index_tree_unchanged
    summary = {
        "ok": all(item["ok"] for item in batch_results) and live_state_unchanged,
        "mode": "sequential_temporary_index_dry_run",
        "batch_list_dir": rel(project_path(batch_list_dir)),
        "batch_count": len(batch_results),
        "checked_path_count": sum(item["path_count"] for item in batch_results),
        "changed_file_count": sum(item["changed_file_count"] for item in batch_results),
        "overlap_count": sum(item["overlap_count"] for item in batch_results),
        "failed_batches": [item["batch"] for item in batch_results if not item["ok"]],
        "head_before": head_before,
        "head_after": head_after,
        "head_unchanged": head_before == head_after,
        "live_index_tree_before": live_index_tree_before,
        "live_index_tree_after": live_index_tree_after,
        "live_index_tree_unchanged": live_index_tree_unchanged,
        "index_before": index_before,
        "index_after": index_after,
        "live_index_fingerprint_unchanged": live_index_fingerprint_unchanged,
        "live_index_unchanged": live_index_tree_unchanged,
        "live_state_unchanged": live_state_unchanged,
        "final_tree_oid": previous_tree,
        "writes_refs": False,
        "writes_live_index": False,
        "writes_worktree": False,
        "creates_commits": False,
        "creates_unreachable_tree_objects": True,
        "batches": batch_results,
    }
    if output:
        resolved_output = project_path(output)
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary["output"] = rel(resolved_output)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-list-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = dry_run(args.batch_list_dir, args.output)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            f"ok={result['ok']} batches={result['batch_count']} paths={result['checked_path_count']} "
            f"changed={result['changed_file_count']} overlap={result['overlap_count']} "
            f"live_state_unchanged={result['live_state_unchanged']}"
        )
        if result.get("output"):
            print(f"output={result['output']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
