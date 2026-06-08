#!/usr/bin/env python3
"""Smoke tests for CoAgent preflight policy checks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.hooks import preflight


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
    completed = subprocess.run(
        [sys.executable, "CoAgent/hooks/codex_native_hook.py"],
        cwd=ROOT,
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
        check=False,
    )
    assert completed.returncode == 0, {
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }
    assert completed.stdout.strip(), completed
    return json.loads(completed.stdout)


def main() -> int:
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
                    "evidence": ["CoAgent/tests/test_preflight_policy.py"],
                    "next_recommended_action": "none",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        policy = preflight.collect(
            make_args(
                path=["CoAgent/hooks/preflight.py", "/tmp/outside-read"],
                write_path=["Results/tmp/preflight-ok", "/tmp/outside-write", "C:/Users/HP/.codex/auth.json"],
                command=["git add .", "rm -rf Results/tmp/bad", "python3 CoAgent/hooks/preflight.py"],
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
        assert "Results/coagent_status/probe.json" in policy["runtime_output_ignore"]["checked_paths"]
        benign_limit_policy = preflight.check_command_policy(
            [
                "python -m pytest CoAgent/tests/test_preflight_policy.py -k " + "token" + "_limit_test",
                "python CoAgent/hooks/preflight.py --command " + "token" + "_limit_test",
                "python script.py --" + "token" + "-limit 8192",
            ]
        )
        assert benign_limit_policy["ok"], benign_limit_policy

        sensitive_command_policy = preflight.check_command_policy(
            [
                "Get-Content " + "C:/Users/HP/.codex/" + "auth.json",
                "Get-Content " + "C:/Users/HP/." + "ssh/id_" + "ed25519",
            ]
        )
        assert not sensitive_command_policy["ok"], sensitive_command_policy
        assert any(item["reason"] == "secret_risk_path" for item in sensitive_command_policy["findings"])

        assert not preflight.check_secret_paths(["Results/tmp/session." + "token"])["ok"]
        assert not preflight.check_secret_paths(["Results/tmp/client_" + "secret.json"])["ok"]
        assert preflight.check_secret_paths(["CoAgent/tests/" + "token" + "_limit_test.py"])["ok"]

        packet_prefix = "Results/agent_packets/returns/COAGENTOPS-HOOK-"
        assert preflight.check_secret_paths(
            [packet_prefix + "SEC" + "RET" + "-FALSE-POSITIVE-FIX-20260608-001.json"]
        )["ok"]
        combo_ok_command = (
            "Get-Content "
            + packet_prefix
            + "SEC"
            + "RET"
            + "-FALSE-POSITIVE-FIX-20260608-001.json; Write-Output ok"
        )
        combo_ok_policy = preflight.check_command_policy([combo_ok_command])
        assert combo_ok_policy["ok"], combo_ok_policy
        blocker_prefix = "Results/agent_packets/blockers/PMO-HOOK-"
        assert preflight.check_secret_paths(
            [blocker_prefix + "creden" + "tial" + "-LABEL-20260608-001.json"]
        )["ok"]
        sensitive_dir = str(Path("Results") / "tmp")
        credentials_name = "creden" + "tial" + "s" + "." + "json"
        client_secret_name = "client_" + "sec" + "ret" + "." + "json"
        assert not preflight.check_secret_paths([str(Path(sensitive_dir) / credentials_name)])["ok"]
        assert not preflight.check_secret_paths([str(Path(sensitive_dir) / client_secret_name)])["ok"]

        token_env = "$env:API_" + "TO" + "KEN" + "_VALUE" + "=" + "x"
        secret_env = "$env:" + "SEC" + "RET" + "_PATH" + "=" + "x"
        auth_env = "AUTH_" + "TO" + "KEN" + "=" + "x"
        env_assignment_policy = preflight.check_command_policy([token_env, secret_env, auth_env])
        assert not env_assignment_policy["ok"], env_assignment_policy
        env_hints = {item["hint"] for item in env_assignment_policy["findings"]}
        assert {"token", "secret"}.issubset(env_hints), env_assignment_policy
        shell_read = "Get" + "-Content "
        combo_bad_path = shell_read + str(Path(sensitive_dir) / credentials_name) + "; Write-Output ok"
        combo_bad_path_policy = preflight.check_command_policy([combo_bad_path])
        assert not combo_bad_path_policy["ok"], combo_bad_path_policy
        combo_bad_env_policy = preflight.check_command_policy([token_env + "; Write-Output ok"])
        assert not combo_bad_env_policy["ok"], combo_bad_env_policy

        runtime_ignore = preflight.check_runtime_output_ignore()
        assert runtime_ignore["ok"], runtime_ignore
        assert runtime_ignore["missing"] == [], runtime_ignore
        assert "Results/coagent_knowledge/knowledge_index.json" in runtime_ignore["checked_paths"]
        assert "Results/coagent_learning/learning_index.json" in runtime_ignore["checked_paths"]

        custom_runtime_ignore = preflight.check_runtime_output_ignore((
            "CoAgent/hooks/preflight.py",
            "CoAgent/not_ignored_runtime_probe.json",
        ))
        assert not custom_runtime_ignore["ok"], custom_runtime_ignore
        assert "CoAgent/hooks/preflight.py" in custom_runtime_ignore["tracked_paths"]
        assert "CoAgent/not_ignored_runtime_probe.json" in custom_runtime_ignore["missing"]


        clean = preflight.collect(
            make_args(
                path=["CoAgent/hooks/preflight.py"],
                write_path=["Results/tmp/preflight-ok"],
                command=["python3 CoAgent/hooks/preflight.py"],
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
        assert clean["git_workspace_state"]["ok"], clean["git_workspace_state"]

        session_payload = {
            "cwd": str(ROOT),
            "hook_event_name": "SessionStart",
            "source": "resume",
        }
        session_smoke = run_adapter_payload(session_payload)
        session_output = session_smoke["hookSpecificOutput"]
        assert session_output["hookEventName"] == "SessionStart", session_smoke
        assert "additionalContext" in session_output, session_smoke
        assert "AGENTS.md" in session_output["additionalContext"], session_smoke
        assert "Docs/Workflows/new_conversation_context.md" in session_output["additionalContext"], session_smoke

        blocked_cmd = " ".join([("g" + "it"), ("res" + "et"), ("-" + "-hard")])
        pretool_payload = {
            "cwd": str(ROOT),
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": blocked_cmd},
        }
        pretool_smoke = run_adapter_payload(pretool_payload)
        pretool_output = pretool_smoke["hookSpecificOutput"]
        assert pretool_output["hookEventName"] == "PreToolUse", pretool_smoke
        assert pretool_output["permissionDecision"] == "deny", pretool_smoke
        assert "destructive_command" in pretool_output["permissionDecisionReason"], pretool_smoke

        git_policy = preflight.check_git_workspace_state(
            staged_limit=2,
            staged_override=[
                "Results/agent_runtime/tasks.sqlite3",
                "References/Agent/example/README.md",
                "CoAgent/runtime/mosim_agent_runtime.py",
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
                "CoAgent/hooks/preflight.py",
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
