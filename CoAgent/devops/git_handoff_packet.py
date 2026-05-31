#!/usr/bin/env python3
"""Build a read-only DevOps handoff packet for broad CoAgent Git work."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "coagent_status"
DEFAULT_TASK_ID = "COAGENT-IMPL-LONGRUN-20260531"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.devops import git_batch_plan
from CoAgent.hooks import preflight


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


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


def staged_unstaged_overlap(plan: dict[str, Any]) -> list[str]:
    return sorted(
        item["path"]
        for batch in plan.get("batches", [])
        for item in batch.get("files", [])
        if item.get("staged") == "yes" and item.get("worktree") == "yes"
    )


def batch_risks(batch: dict[str, Any]) -> list[str]:
    risks: list[str] = []
    if batch.get("file_count", 0) > 80:
        risks.append("large_batch_requires_review")
    if batch.get("worktree_count", 0):
        risks.append("has_unstaged_worktree_changes")
    if batch.get("staged_count", 0) and batch.get("worktree_count", 0):
        risks.append("mixed_staged_and_worktree_state")
    if batch.get("batch") in {"task_artifacts", "architecture_decisions_research"}:
        risks.append("documentation_volume_review")
    if batch.get("batch") == "guardrails_doctor_automation":
        risks.append("guardrail_runtime_behavior_review")
    if batch.get("batch") == "review_gateway_status":
        risks.append("human_review_notification_surface_review")
    return risks


def integration_commands_for(batch: dict[str, Any]) -> dict[str, list[str]]:
    files = [item["path"] for item in batch.get("files", [])]
    pathspec = " ".join(files[:40])
    overflow = len(files) - 40
    note = f" # plus {overflow} more pathspecs from packet JSON" if overflow > 0 else ""
    return {
        "inspect": [
            f"git diff --cached --stat -- {pathspec}{note}",
            f"git diff --check -- {pathspec}{note}",
        ],
        "verify": [
            "python3 CoAgent/doctor/coagent_doctor.py --mode full --json --output Results/coagent_doctor/latest_gateway_full.json",
            "python3 CoAgent/runtime/mosim_agent_runtime.py audit-events",
        ],
        "split_commit_safety": [
            "Do not run git commit -- <pathspec> in this live worktree when paths have staged/worktree overlap.",
            "Use a temporary-index split-commit builder or first reach a reviewed clean index/worktree boundary.",
        ],
    }


def preflight_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    data = preflight.collect(
        argparse.Namespace(
            path=[],
            write_path=[],
            command=[],
            result_packet=[],
            large_limit_mb=100,
            full_repo_large_scan=False,
            allow_destructive_command=False,
            allow_broad_git=False,
            staged_file_warning_threshold=args.staged_file_warning_threshold,
        )
    )
    git_state = data.get("git_workspace_state", {})
    return {
        "ok": bool(data.get("ok")),
        "git_workspace_state": {
            "ok": bool(git_state.get("ok")),
            "staged_count": git_state.get("staged_count"),
            "staged_limit": git_state.get("staged_limit"),
            "staged_runtime_count": git_state.get("staged_runtime_count"),
            "staged_external_count": git_state.get("staged_external_count"),
            "index_lock_present": git_state.get("index_lock_present"),
            "findings": git_state.get("findings", []),
        },
    }


def build_packet(args: argparse.Namespace) -> dict[str, Any]:
    plan = git_batch_plan.build_plan()
    preflight_data = preflight_snapshot(args)
    overlap = staged_unstaged_overlap(plan)
    raw_batches = plan.get("batches", [])
    batches = []
    for index, batch in enumerate(raw_batches, start=1):
        batches.append(
            {
                "sequence": index,
                "batch": batch["batch"],
                "description": batch.get("description", ""),
                "file_count": batch.get("file_count", 0),
                "staged_count": batch.get("staged_count", 0),
                "worktree_count": batch.get("worktree_count", 0),
                "risks": batch_risks(batch),
                "review_owner": "DevOpsReleaseAgent",
                "verification_owner": "VerificationAgent",
                "commands": integration_commands_for(batch),
                "files": batch.get("files", []),
            }
        )
    blockers: list[dict[str, Any]] = []
    git_state = preflight_data.get("git_workspace_state", {})
    if git_state.get("index_lock_present"):
        blockers.append(
            {
                "blocker": "git_index_lock_present",
                "action": "stop Git work; verify no active Git owner before removing stale lock",
            }
        )
    if git_state.get("staged_runtime_count", 0):
        blockers.append(
            {
                "blocker": "staged_runtime_outputs",
                "count": git_state.get("staged_runtime_count"),
                "action": "unstage runtime outputs before any commit",
            }
        )
    if git_state.get("staged_external_count", 0):
        blockers.append(
            {
                "blocker": "staged_external_reference_tree",
                "count": git_state.get("staged_external_count"),
                "action": "exclude or separately approve external reference-tree integration",
            }
        )
    return {
        "schema_type": "coagent_git_handoff_packet",
        "schema_version": 1,
        "task_id": args.task_id,
        "ok": not any(item.get("blocker") for item in blockers),
        "mode": "read_only",
        "purpose": "Split broad CoAgent Git work into reviewable DevOps-owned integration batches.",
        "non_goals": [
            "no staging changes",
            "no commit",
            "no push",
            "no worktree creation",
            "no destructive cleanup",
        ],
        "totals": {
            "total_file_count": plan.get("total_file_count", 0),
            "staged_file_count": plan.get("staged_file_count", 0),
            "worktree_file_count": plan.get("worktree_file_count", 0),
            "batch_count": len(batches),
            "staged_unstaged_overlap_count": len(overlap),
        },
        "preflight": preflight_data,
        "blockers": blockers,
        "global_risks": [
            "broad_staged_surface" if plan.get("staged_file_count", 0) > args.staged_file_warning_threshold else "",
            "mixed_index_and_worktree_state" if overlap else "",
            "live_pathspec_commit_can_capture_worktree_content" if overlap else "",
        ],
        "staged_unstaged_overlap": overlap[:100],
        "batches": batches,
        "recommended_sequence": [batch["batch"] for batch in batches],
        "required_review_gates": [
            "DevOpsReview: batch boundaries and staged/worktree state are acceptable",
            "VerificationReview: full doctor and targeted tests pass after each accepted batch",
            "SafetyReview: no secrets, runtime outputs, external reference trees, or destructive commands are staged",
            "GitSafetyReview: do not use live `git commit -- <pathspec>` when staged/worktree overlap exists; use temporary-index or clean-boundary integration",
        ],
        "next_action": "Use this packet to drive a split DevOps review and temporary-index or clean-boundary integration plan; do not run one broad commit or live pathspec commit.",
    }


def write_markdown(path: Path, packet: dict[str, Any]) -> str:
    totals = packet["totals"]
    lines = [
        "# CoAgent Git Handoff Packet",
        "",
        f"- task_id: `{packet['task_id']}`",
        f"- mode: `{packet['mode']}`",
        f"- ok: `{packet['ok']}`",
        f"- total_file_count: `{totals['total_file_count']}`",
        f"- staged_file_count: `{totals['staged_file_count']}`",
        f"- worktree_file_count: `{totals['worktree_file_count']}`",
        f"- batch_count: `{totals['batch_count']}`",
        f"- staged_unstaged_overlap_count: `{totals['staged_unstaged_overlap_count']}`",
        "",
        "## Non Goals",
        "",
    ]
    for item in packet["non_goals"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Blockers", ""])
    if packet["blockers"]:
        for item in packet["blockers"]:
            lines.append(f"- `{item.get('blocker')}`: {item.get('action')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Required Review Gates", ""])
    for item in packet["required_review_gates"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Batches", ""])
    for batch in packet["batches"]:
        lines.extend(
            [
                f"### {batch['sequence']}. {batch['batch']}",
                "",
                batch["description"],
                "",
                f"- file_count: `{batch['file_count']}`",
                f"- staged_count: `{batch['staged_count']}`",
                f"- worktree_count: `{batch['worktree_count']}`",
                f"- risks: `{', '.join(batch['risks']) if batch['risks'] else 'none'}`",
                "",
                "Review commands:",
            ]
        )
        for command in batch["commands"]["inspect"] + batch["commands"]["verify"]:
            lines.append(f"- `{command}`")
        lines.extend(["", "Files:"])
        for item in batch["files"][:50]:
            lines.append(f"- `{item['status']}` `{item['path']}`")
        if len(batch["files"]) > 50:
            lines.append(f"- ... {len(batch['files']) - 50} more")
        lines.append("")
    lines.extend(["## Next Action", "", packet["next_action"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return rel(path)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    packet = build_packet(args)
    outputs: dict[str, str] = {}
    if args.output:
        output = project_path(args.output)
    else:
        output = DEFAULT_OUTPUT_ROOT / f"{args.task_id}.git_handoff.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs["json"] = rel(output)
    if args.markdown_output:
        outputs["markdown"] = write_markdown(project_path(args.markdown_output), packet)
    return {"ok": packet["ok"], "outputs": outputs, "packet": packet if args.include_packet else {}}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--staged-file-warning-threshold", type=int, default=preflight.STAGED_BROAD_THRESHOLD)
    parser.add_argument("--include-packet", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_packet(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"git_handoff ok={result['ok']} json={result['outputs']['json']}")
        if "markdown" in result["outputs"]:
            print(f"markdown={result['outputs']['markdown']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
