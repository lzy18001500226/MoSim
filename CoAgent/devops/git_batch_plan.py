#!/usr/bin/env python3
"""Build a read-only split-commit plan for CoAgent changes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MARKDOWN = ROOT / "Results" / "coagent_status" / "git_batch_plan.md"
DEFAULT_BATCH_LIST_DIR = ROOT / "Results" / "coagent_status" / "git_batches"


BATCH_RULES: list[tuple[str, tuple[str, ...], str]] = [
    ("policy_status_docs", ("CoAgent/README.md", "CoAgent/STATUS.md", ".gitignore"), "Top-level CoAgent policy/status and ignore rules."),
    ("architecture_decisions_research", ("CoAgent/docs/", "CoAgent/learning/"), "Architecture, decisions, research, and learning records."),
    ("runtime_protocol_bootstrap", ("CoAgent/runtime/", "CoAgent/protocol/", "CoAgent/bootstrap/"), "Runtime queue, protocol schemas/templates, and task bootstrap."),
    ("dispatch_transport_context_memory", ("CoAgent/dispatch/", "CoAgent/transport/", "CoAgent/context/", "CoAgent/memory/"), "Conversation dispatch, transport boundary, context packs, and memory recall."),
    ("review_gateway_status", ("CoAgent/result_router/", "CoAgent/review_queue/", "CoAgent/gateway/", "CoAgent/status_export/"), "Result intake, review queue, human notification, and status export."),
    ("guardrails_doctor_automation", ("CoAgent/hooks/", "CoAgent/doctor/", "CoAgent/automation/", "CoAgent/validators/"), "Preflight, doctor, automation guardrails, and validators."),
    ("knowledge_devops", ("CoAgent/knowledge/", "CoAgent/devops/"), "Knowledge indexer and DevOps helper tools."),
    ("tests", ("CoAgent/tests/",), "CoAgent smoke and regression tests."),
    ("task_artifacts", ("CoAgent/tasks/",), "Task-specific design and recovery artifacts."),
]


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def run(command: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
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


def git_status() -> list[dict[str, str]]:
    result = run(["git", "status", "--porcelain=v1", "--", ".gitignore", "CoAgent"], timeout=60)
    if not result.get("ok"):
        raise SystemExit(f"git status failed: {result}")
    items: list[dict[str, str]] = []
    for line in result["stdout"].splitlines():
        if not line:
            continue
        status = line[:2]
        raw_path = line[3:]
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        items.append(
            {
                "status": status,
                "path": raw_path,
                "staged": "yes" if status[0] not in {" ", "?"} else "no",
                "worktree": "yes" if status[1] not in {" "} or status[0] == "?" else "no",
            }
        )
    return items


def classify(path: str) -> str:
    for name, prefixes, _description in BATCH_RULES:
        if any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in prefixes):
            return name
    return "other"


def build_plan() -> dict[str, Any]:
    items = git_status()
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in items:
        groups[classify(item["path"])].append(item)
    batches = []
    descriptions = {name: description for name, _prefixes, description in BATCH_RULES}
    order = [name for name, _prefixes, _description in BATCH_RULES] + ["other"]
    for name in order:
        files = sorted(groups.get(name, []), key=lambda item: item["path"])
        if not files:
            continue
        batches.append(
            {
                "batch": name,
                "description": descriptions.get(name, "Unclassified project-local files."),
                "file_count": len(files),
                "staged_count": sum(1 for item in files if item["staged"] == "yes"),
                "worktree_count": sum(1 for item in files if item["worktree"] == "yes"),
                "files": files,
            }
        )
    return {
        "ok": True,
        "total_file_count": len(items),
        "staged_file_count": sum(1 for item in items if item["staged"] == "yes"),
        "worktree_file_count": sum(1 for item in items if item["worktree"] == "yes"),
        "batches": batches,
    }


def write_markdown(path: Path, plan: dict[str, Any]) -> str:
    lines = [
        "# CoAgent Git Batch Plan",
        "",
        "Read-only split plan for the current CoAgent Git state.",
        "",
        f"- total_file_count: `{plan['total_file_count']}`",
        f"- staged_file_count: `{plan['staged_file_count']}`",
        f"- worktree_file_count: `{plan['worktree_file_count']}`",
        "",
    ]
    for batch in plan["batches"]:
        lines.extend(
            [
                f"## {batch['batch']}",
                "",
                batch["description"],
                "",
                f"- file_count: `{batch['file_count']}`",
                f"- staged_count: `{batch['staged_count']}`",
                f"- worktree_count: `{batch['worktree_count']}`",
                "",
            ]
        )
        for item in batch["files"][:80]:
            lines.append(f"- `{item['status']}` `{item['path']}`")
        if len(batch["files"]) > 80:
            lines.append(f"- ... {len(batch['files']) - 80} more")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return rel(path)


def safe_batch_name(name: str) -> str:
    return "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in name)


def write_path_list(path: Path, values: list[str]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(values) + ("\n" if values else ""), encoding="utf-8")
    return rel(path)


def write_batch_lists(directory: Path, plan: dict[str, Any]) -> dict[str, Any]:
    directory = project_path(directory)
    outputs: dict[str, Any] = {"directory": rel(directory), "batches": {}, "overlap": ""}
    overlap: list[str] = []
    for batch in plan.get("batches", []):
        name = str(batch.get("batch", "unknown"))
        safe_name = safe_batch_name(name)
        files = [str(item["path"]) for item in batch.get("files", [])]
        staged = [str(item["path"]) for item in batch.get("files", []) if item.get("staged") == "yes"]
        worktree = [str(item["path"]) for item in batch.get("files", []) if item.get("worktree") == "yes"]
        overlap.extend(str(item["path"]) for item in batch.get("files", []) if item.get("staged") == "yes" and item.get("worktree") == "yes")
        outputs["batches"][name] = {
            "all": write_path_list(directory / f"{safe_name}.paths", files),
            "staged": write_path_list(directory / f"{safe_name}.staged.paths", staged),
            "worktree": write_path_list(directory / f"{safe_name}.worktree.paths", worktree),
        }
    outputs["overlap"] = write_path_list(directory / "overlap.paths", sorted(dict.fromkeys(overlap)))
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--batch-list-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    plan = build_plan()
    if args.markdown_output:
        plan["markdown_output"] = write_markdown(project_path(args.markdown_output), plan)
    if args.batch_list_dir:
        plan["batch_lists"] = write_batch_lists(project_path(args.batch_list_dir), plan)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"total={plan['total_file_count']} staged={plan['staged_file_count']} worktree={plan['worktree_file_count']}")
        for batch in plan["batches"]:
            print(f"{batch['batch']}: files={batch['file_count']} staged={batch['staged_count']} worktree={batch['worktree_count']}")
        if args.markdown_output:
            print(f"markdown={plan['markdown_output']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
