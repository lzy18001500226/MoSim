#!/usr/bin/env python3
"""Apply reviewed split Git commits from staged batches.

Default mode is read-only. Use `--apply` only after the split-index and
sequential dry-run evidence is current and reviewed.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

from CoAgent.devops import git_split_commit_dry_run


DEFAULT_MESSAGES = {
    "policy_status_docs": "CoAgent: add policy and status docs",
    "architecture_decisions_research": "CoAgent: add architecture and learning records",
    "runtime_protocol_bootstrap": "CoAgent: add runtime and protocol bootstrap",
    "dispatch_transport_context_memory": "CoAgent: add dispatch transport and context memory",
    "review_gateway_status": "CoAgent: add review gateway and status surfaces",
    "guardrails_doctor_automation": "CoAgent: add guardrails doctor and automation checks",
    "knowledge_devops": "CoAgent: add knowledge and DevOps helpers",
    "tests": "CoAgent: add runtime and Git smoke tests",
    "task_artifacts": "CoAgent: add architecture task artifacts",
    "other": "CoAgent: add remaining project-local changes",
}


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def run(command: list[str], *, timeout: int = 60, env: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env={**os.environ, **(env or {})},
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


def git_stdout(command: list[str]) -> str:
    result = run(command)
    if not result["ok"]:
        raise SystemExit(f"git command failed: {result}")
    return result["stdout"].strip()


def current_branch_ref() -> str:
    result = run(["git", "symbolic-ref", "-q", "HEAD"])
    if not result["ok"] or not result["stdout"].strip():
        raise SystemExit("HEAD is detached; refusing to update refs")
    return result["stdout"].strip()


def ensure_no_index_lock() -> None:
    index_lock = ROOT / ".git" / "index.lock"
    if index_lock.exists():
        raise SystemExit(f"git index lock exists: {rel(index_lock)}")


def ensure_cached_diff_clean() -> None:
    result = run(["git", "diff", "--cached", "--check"])
    if not result["ok"]:
        raise SystemExit(f"git diff --cached --check failed: {result}")


def create_commit(tree_oid: str, parent: str, message: str) -> str:
    result = run(["git", "commit-tree", tree_oid, "-p", parent, "-m", message])
    if not result["ok"]:
        raise SystemExit(f"git commit-tree failed: {result}")
    return result["stdout"].strip()


def build_commit_plan(batch_list_dir: Path, *, output: Path | None = None) -> dict[str, Any]:
    ensure_no_index_lock()
    ensure_cached_diff_clean()
    branch_ref = current_branch_ref()
    head_before = git_stdout(["git", "rev-parse", "HEAD"])
    live_index_tree = git_stdout(["git", "write-tree"])
    dry_run_result = git_split_commit_dry_run.dry_run(batch_list_dir)
    final_tree = dry_run_result["final_tree_oid"]
    live_index_matches = live_index_tree == final_tree
    commits: list[dict[str, Any]] = []
    parent = head_before
    for item in dry_run_result["batches"]:
        if item["tree_oid"] == item["previous_tree_oid"] or item["changed_file_count"] == 0:
            continue
        batch = item["batch"]
        commits.append(
            {
                "sequence": len(commits) + 1,
                "batch": batch,
                "message": DEFAULT_MESSAGES.get(batch, f"CoAgent: add {batch}"),
                "tree_oid": item["tree_oid"],
                "parent": parent,
                "changed_file_count": item["changed_file_count"],
                "path_count": item["path_count"],
                "overlap_count": item["overlap_count"],
            }
        )
        parent = f"<commit:{batch}>"
    result = {
        "ok": bool(dry_run_result["ok"] and live_index_matches and commits),
        "mode": "split_commit_apply_plan",
        "apply": False,
        "branch_ref": branch_ref,
        "head_before": head_before,
        "live_index_tree": live_index_tree,
        "dry_run_final_tree": final_tree,
        "live_index_matches_dry_run_final_tree": live_index_matches,
        "batch_list_dir": rel(project_path(batch_list_dir)),
        "commit_count": len(commits),
        "commits": commits,
        "dry_run_summary": {
            "batch_count": dry_run_result["batch_count"],
            "checked_path_count": dry_run_result["checked_path_count"],
            "overlap_count": dry_run_result["overlap_count"],
            "live_state_unchanged": dry_run_result["live_state_unchanged"],
        },
    }
    if output:
        resolved_output = project_path(output)
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["output"] = rel(resolved_output)
    return result


def apply_commits(batch_list_dir: Path, *, output: Path | None = None) -> dict[str, Any]:
    ensure_no_index_lock()
    ensure_cached_diff_clean()
    branch_ref = current_branch_ref()
    head_before = git_stdout(["git", "rev-parse", "HEAD"])
    live_index_tree_before = git_stdout(["git", "write-tree"])
    dry_run_result = git_split_commit_dry_run.dry_run(batch_list_dir)
    if not dry_run_result["ok"]:
        raise SystemExit(f"split commit dry-run failed: {dry_run_result}")
    if live_index_tree_before != dry_run_result["final_tree_oid"]:
        raise SystemExit(
            "live index tree no longer matches split dry-run final tree; regenerate plan before applying"
        )
    parent = head_before
    commits: list[dict[str, Any]] = []
    for item in dry_run_result["batches"]:
        if item["tree_oid"] == item["previous_tree_oid"] or item["changed_file_count"] == 0:
            continue
        batch = item["batch"]
        message = DEFAULT_MESSAGES.get(batch, f"CoAgent: add {batch}")
        commit_oid = create_commit(item["tree_oid"], parent, message)
        commits.append(
            {
                "sequence": len(commits) + 1,
                "batch": batch,
                "message": message,
                "commit_oid": commit_oid,
                "tree_oid": item["tree_oid"],
                "parent": parent,
                "changed_file_count": item["changed_file_count"],
                "path_count": item["path_count"],
                "overlap_count": item["overlap_count"],
            }
        )
        parent = commit_oid
    if not commits:
        raise SystemExit("no non-empty batches to commit")
    head_before_update = git_stdout(["git", "rev-parse", "HEAD"])
    live_index_tree_before_update = git_stdout(["git", "write-tree"])
    if head_before_update != head_before:
        raise SystemExit("HEAD changed during split commit creation; refusing update-ref")
    if live_index_tree_before_update != live_index_tree_before:
        raise SystemExit("live index changed during split commit creation; refusing update-ref")
    update_ref = run(
        [
            "git",
            "update-ref",
            "-m",
            "CoAgent split commit apply",
            branch_ref,
            commits[-1]["commit_oid"],
            head_before,
        ]
    )
    if not update_ref["ok"]:
        raise SystemExit(f"git update-ref failed: {update_ref}")
    head_after = git_stdout(["git", "rev-parse", "HEAD"])
    live_index_tree_after = git_stdout(["git", "write-tree"])
    result = {
        "ok": bool(head_after == commits[-1]["commit_oid"] and live_index_tree_after == dry_run_result["final_tree_oid"]),
        "mode": "split_commit_apply",
        "apply": True,
        "branch_ref": branch_ref,
        "head_before": head_before,
        "head_after": head_after,
        "live_index_tree_before": live_index_tree_before,
        "live_index_tree_after": live_index_tree_after,
        "dry_run_final_tree": dry_run_result["final_tree_oid"],
        "commit_count": len(commits),
        "commits": commits,
        "writes_refs": True,
        "writes_live_index": False,
        "writes_worktree": False,
        "batch_list_dir": rel(project_path(batch_list_dir)),
    }
    if output:
        resolved_output = project_path(output)
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["output"] = rel(resolved_output)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-list-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--apply", action="store_true", help="create split commits and update the current branch ref")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = (
        apply_commits(args.batch_list_dir, output=args.output)
        if args.apply
        else build_commit_plan(args.batch_list_dir, output=args.output)
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            f"ok={result['ok']} mode={result['mode']} commits={result['commit_count']} "
            f"branch={result['branch_ref']}"
        )
        if result.get("output"):
            print(f"output={result['output']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
