#!/usr/bin/env python3
"""Read-only temporary-index checks for split Git integration.

This helper does not modify the live Git index, worktree, commits, or refs.
It builds a temporary index from HEAD plus the current staged version of a
batch's paths and verifies that Git can write a tree for that isolated batch.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def run(command: list[str], *, env: dict[str, str] | None = None, input_text: str | None = None, timeout: int = 60) -> dict[str, Any]:
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


def staged_ls(paths: list[str]) -> dict[str, dict[str, str]]:
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


def check_batch(paths_file: Path, output: Path | None = None) -> dict[str, Any]:
    paths = read_paths(paths_file)
    staged = staged_ls(paths)
    status = status_for_paths(paths)
    missing_staged = sorted(path for path in paths if path not in staged)
    overlap = sorted(item["path"] for item in status if item["status"][0] not in {" ", "?"} and item["status"][1] not in {" "})
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        temp_index = Path(tmp) / "index"
        read_tree = run(["git", "read-tree", "HEAD"], env={"GIT_INDEX_FILE": str(temp_index)})
        if not read_tree["ok"]:
            raise SystemExit(f"git read-tree failed: {read_tree}")
        update_lines = [f"{entry['mode']} {entry['oid']}\t{path}" for path, entry in staged.items()]
        update_index = run(
            ["git", "update-index", "--index-info"],
            env={"GIT_INDEX_FILE": str(temp_index)},
            input_text="\n".join(update_lines) + ("\n" if update_lines else ""),
        )
        if not update_index["ok"]:
            raise SystemExit(f"git update-index failed: {update_index}")
        write_tree = run(["git", "write-tree"], env={"GIT_INDEX_FILE": str(temp_index)})
        tree_oid = write_tree["stdout"].strip() if write_tree["ok"] else ""
    result = {
        "ok": bool(write_tree["ok"] and not missing_staged),
        "paths_file": rel(project_path(paths_file)),
        "path_count": len(paths),
        "staged_entry_count": len(staged),
        "missing_staged": missing_staged,
        "overlap_count": len(overlap),
        "overlap": overlap,
        "tree_oid": tree_oid,
        "write_tree_ok": bool(write_tree["ok"]),
        "write_tree_stderr": write_tree.get("stderr", ""),
        "mode": "read_only_temporary_index",
    }
    if output:
        resolved_output = project_path(output)
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["output"] = rel(resolved_output)
    return result


def check_directory(batch_list_dir: Path, output: Path | None = None) -> dict[str, Any]:
    directory = project_path(batch_list_dir)
    batch_results: list[dict[str, Any]] = []
    for paths_file in sorted(directory.glob("*.staged.paths")):
        if paths_file.name == "overlap.staged.paths":
            continue
        result = check_batch(paths_file)
        result["batch"] = paths_file.name.removesuffix(".staged.paths")
        batch_results.append(result)
    summary = {
        "ok": all(item["ok"] for item in batch_results),
        "mode": "read_only_temporary_index_directory",
        "batch_list_dir": rel(directory),
        "batch_count": len(batch_results),
        "checked_path_count": sum(item["path_count"] for item in batch_results),
        "overlap_count": sum(item["overlap_count"] for item in batch_results),
        "failed_batches": [item["batch"] for item in batch_results if not item["ok"]],
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
    parser.add_argument("--paths-file", type=Path)
    parser.add_argument("--batch-list-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if bool(args.paths_file) == bool(args.batch_list_dir):
        raise SystemExit("provide exactly one of --paths-file or --batch-list-dir")
    result = check_directory(args.batch_list_dir, args.output) if args.batch_list_dir else check_batch(args.paths_file, args.output)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if result["mode"] == "read_only_temporary_index_directory":
            print(
                f"ok={result['ok']} batches={result['batch_count']} paths={result['checked_path_count']} "
                f"overlap={result['overlap_count']}"
            )
        else:
            print(
                f"ok={result['ok']} paths={result['path_count']} staged={result['staged_entry_count']} "
                f"overlap={result['overlap_count']} tree={result['tree_oid']}"
            )
        if result.get("output"):
            print(f"output={result['output']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
