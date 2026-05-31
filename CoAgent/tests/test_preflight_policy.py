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
            Namespace(
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

        clean = preflight.collect(
            Namespace(
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

        direct = subprocess.run(
            [
                sys.executable,
                "CoAgent/hooks/preflight.py",
                "--result-packet",
                str(complete_packet.relative_to(ROOT)),
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
