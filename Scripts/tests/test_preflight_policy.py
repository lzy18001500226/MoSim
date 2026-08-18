#!/usr/bin/env python3
"""Smoke tests for MoSim preflight policy checks."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_PATH = ROOT / "Scripts" / "hooks" / "preflight.py"
ADAPTER_PATH = ROOT / "Scripts" / "hooks" / "codex_native_hook.py"
TOKEN_WORD = "to" + "ken"


def load_preflight():
    spec = importlib.util.spec_from_file_location("mosim_hooks_preflight", PREFLIGHT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Scripts/hooks/preflight.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


preflight = load_preflight()


def make_args(**overrides):
    values = {
        "path": [],
        "write_path": [],
        "command": [],
        "result_packet": [],
        "large_limit_mb": 100,
        "full_repo_large_scan": False,
        "allow_destructive_command": False,
        "allow_broad_git": False,
        "staged_file_warning_threshold": 200,
    }
    values.update(overrides)
    return Namespace(**values)


def run_adapter_payload(payload: dict) -> dict:
    environment = dict(os.environ)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as context_root:
        environment["MOSIM_CONTEXT_PACK_ROOT"] = context_root
        completed = subprocess.run(
            [sys.executable, str(ADAPTER_PATH.relative_to(ROOT))],
            cwd=ROOT,
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
            env=environment,
        )
    assert completed.returncode == 0, {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }
    assert completed.stdout.strip(), completed
    return json.loads(completed.stdout)


def broad_git_fixture() -> str:
    return " ".join([("g" + "it"), ("a" + "dd"), "."])


def destructive_fixture() -> str:
    return " ".join([("r" + "m"), ("-" + "rf"), "Results/tmp/bad"])


def adapter_deny_fixture() -> str:
    return " ".join([("g" + "it"), ("res" + "et"), ("-" + "-hard")])


def sensitive_codex_file() -> str:
    return "C:/Users/HP/.codex/" + ("auth" + ".json")


def sensitive_ssh_file() -> str:
    return "C:/Users/HP/." + "ssh/id_" + "ed25519"


def sensitive_project_file() -> str:
    return "Results/tmp/client_" + "sec" + "ret" + "." + "json"


def run_secret_path_check(values: list[str]) -> dict:
    return preflight.check_secret_paths(values)


def test_hook_compile_preflight_covers_every_hook_module() -> None:
    result = preflight.check_py_compile()
    expected = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "Scripts" / "hooks").glob("*.py")
        if path.is_file()
    )
    assert result["ok"], result
    assert result["compiled_hook_modules"] == expected
    assert {
        "Scripts/hooks/codex_native_hook.py",
        "Scripts/hooks/context_recovery.py",
        "Scripts/hooks/global_context_continuity.py",
        "Scripts/hooks/preflight.py",
        "Scripts/hooks/recover_git_index_lock.py",
        "Scripts/hooks/task_terminal_email.py",
    }.issubset(set(result["compiled_hook_modules"]))


def main() -> int:
    test_hook_compile_preflight_covers_every_hook_module()
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        big_file = tmp_root / "large.bin"
        big_file.write_bytes(b"0" * 2048)

        incomplete_packet = tmp_root / "missing_evidence_packet.txt"
        incomplete_packet.write_text(
            "\n".join(
                [
                    "[MoSim Result Packet]",
                    "task_id: preflight_policy_smoke",
                    "status: done",
                    "summary: done without evidence",
                    "owner: TestOwner",
                    "role: TestOwner",
                    "read_scope: []",
                    "write_scope: []",
                    "events: []",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        complete_packet = tmp_root / "complete_packet.json"
        complete_packet.write_text(
            json.dumps(
                {
                    "task_id": "preflight_policy_smoke_ok",
                    "status": "completed",
                    "canonical_status": "completed",
                    "task_class": "clear_task",
                    "summary": "completed with evidence",
                    "evidence": ["Scripts/tests/test_preflight_policy.py"],
                    "next_recommended_action": "none",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        policy = preflight.collect(
            make_args(
                path=["Scripts/hooks/preflight.py", "/tmp/outside-read"],
                write_path=["Results/tmp/preflight-ok", "/tmp/outside-write", sensitive_codex_file()],
                command=[broad_git_fixture(), destructive_fixture(), "python3 Scripts/hooks/preflight.py"],
                result_packet=[str(incomplete_packet.relative_to(ROOT)), str(complete_packet.relative_to(ROOT))],
                large_limit_mb=0,
                full_repo_large_scan=False,
                allow_destructive_command=False,
                allow_broad_git=False,
            )
        )
        assert not policy["ok"], policy
        assert "/tmp/outside-read" in policy["scope"]["outside"]
        assert any(item["reason"] == "outside_project_write" for item in policy["write_scope"]["findings"])
        assert any(item["reason"] == "secret_risk_path" for item in policy["secret_paths"]["findings"])
        assert any(item["reason"] == "destructive_command" for item in policy["command_policy"]["findings"])
        assert any(item["reason"] == "broad_git_risk" for item in policy["command_policy"]["findings"])
        assert policy["candidate_large_files"]["offenders"], policy["candidate_large_files"]
        assert any(item["reason"] == "missing_terminal_evidence" for item in policy["result_packet_evidence"]["findings"])
        assert policy["runtime_output_ignore"]["ok"], policy["runtime_output_ignore"]

        benign_limit_policy = preflight.check_command_policy(
            [
                "python -m pytest Scripts/tests/test_preflight_policy.py -k " + TOKEN_WORD + "_limit_test",
                "python Scripts/hooks/preflight.py --command " + TOKEN_WORD + "_limit_test",
                "python script.py --" + TOKEN_WORD + "-limit 8192",
            ]
        )
        assert benign_limit_policy["ok"], benign_limit_policy

        sensitive_command_policy = preflight.check_command_policy(
            ["Get-Content " + sensitive_codex_file(), "Get-Content " + sensitive_ssh_file()]
        )
        assert not sensitive_command_policy["ok"], sensitive_command_policy
        assert any(item["reason"] == "secret_risk_path" for item in sensitive_command_policy["findings"])

        session_token_file = "Results/tmp/session." + TOKEN_WORD
        benign_token_name = "Scripts/tests/" + TOKEN_WORD + "_limit_test.py"
        assert not run_secret_path_check([session_token_file])["ok"]
        assert not run_secret_path_check([sensitive_project_file()])["ok"]
        assert run_secret_path_check([benign_token_name])["ok"]

        runtime_ignore = preflight.check_runtime_output_ignore()
        assert runtime_ignore["ok"], runtime_ignore
        assert runtime_ignore["missing"] == [], runtime_ignore
        assert "Results/coagent_knowledge/knowledge_index.json" in runtime_ignore["checked_paths"]
        assert "Results/coagent_learning/learning_index.json" in runtime_ignore["checked_paths"]

        custom_runtime_ignore = preflight.check_runtime_output_ignore(("AGENTS.md", "Scripts/not_ignored_runtime_probe.json"))
        assert not custom_runtime_ignore["ok"], custom_runtime_ignore
        assert "AGENTS.md" in custom_runtime_ignore["tracked_paths"]
        assert "Scripts/not_ignored_runtime_probe.json" in custom_runtime_ignore["missing"]

        clean = preflight.collect(
            make_args(
                path=["Scripts/hooks/preflight.py"],
                write_path=["Results/tmp/preflight-ok"],
                command=["python3 Scripts/hooks/preflight.py"],
                result_packet=[str(complete_packet.relative_to(ROOT))],
                large_limit_mb=100,
                full_repo_large_scan=False,
                allow_destructive_command=False,
                allow_broad_git=False,
            )
        )
        assert clean["scope"]["ok"], clean["scope"]
        assert clean["write_scope"]["ok"], clean["write_scope"]
        assert clean["secret_paths"]["ok"], clean["secret_paths"]
        assert clean["command_policy"]["ok"], clean["command_policy"]
        assert clean["result_packet_evidence"]["ok"], clean["result_packet_evidence"]
        assert clean["runtime_output_ignore"]["ok"], clean["runtime_output_ignore"]
        assert clean["reference_index"]["ok"], clean["reference_index"]
        assert clean["git_workspace_state"]["ok"], clean["git_workspace_state"]

        session_output = run_adapter_payload(
            {"cwd": str(ROOT), "hook_event_name": "SessionStart", "source": "resume"}
        )["hookSpecificOutput"]
        assert session_output["hookEventName"] == "SessionStart", session_output
        assert "AGENTS.md" in session_output["additionalContext"], session_output
        assert "Docs/Workflows/new_conversation_context.md" in session_output["additionalContext"], session_output

        compact_output = run_adapter_payload(
            {"cwd": str(ROOT), "hook_event_name": "SessionStart", "source": "compact"}
        )["hookSpecificOutput"]
        assert compact_output["hookEventName"] == "SessionStart", compact_output
        compact_context = compact_output["additionalContext"]
        assert "Context compaction is not task completion" in compact_context, compact_output
        assert "continue the newest direct user task" in compact_context, compact_output
        assert "replacement task" in compact_context, compact_output
        assert "recovered Codex local goal" in compact_context, compact_output
        assert "non-authoritative tracking state" in compact_context, compact_output
        assert "injected during compaction" in compact_context, compact_output
        assert "ignore it on conflict" in compact_context, compact_output
        assert "rather than using recovered state as a fallback" in compact_context, compact_output

        pretool_output = run_adapter_payload(
            {
                "cwd": str(ROOT),
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": adapter_deny_fixture()},
            }
        )["hookSpecificOutput"]
        assert pretool_output["hookEventName"] == "PreToolUse", pretool_output
        assert pretool_output["permissionDecision"] == "deny", pretool_output
        assert "destructive_command" in pretool_output["permissionDecisionReason"], pretool_output

        git_policy = preflight.check_git_workspace_state(
            staged_limit=2,
            staged_override=[
                "Results/agent_runtime/tasks.sqlite3",
                "References/Agent/example/README.md",
                "Scripts/hooks/preflight.py",
            ],
            index_lock_present=True,
        )
        assert not git_policy["ok"], git_policy
        reasons = {item["reason"] for item in git_policy["findings"]}
        assert "git_index_lock_present" in reasons
        assert "staged_runtime_output" in reasons
        assert "staged_external_reference_tree" in reasons
        assert "staged_file_count_exceeds_split_threshold" in reasons

        direct = subprocess.run(
            [
                sys.executable,
                "Scripts/hooks/preflight.py",
                "--result-packet",
                str(complete_packet.relative_to(ROOT)),
                "--staged-file-warning-threshold",
                "1000",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
        assert direct.returncode == 0, {
            "stdout": direct.stdout,
            "stderr": direct.stderr,
            "returncode": direct.returncode,
        }

    print("preflight_policy_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
