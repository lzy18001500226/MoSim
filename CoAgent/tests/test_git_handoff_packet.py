#!/usr/bin/env python3
"""Smoke test the read-only CoAgent Git handoff packet."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.devops import git_handoff_packet


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        output = tmp_root / "git_handoff.json"
        markdown = tmp_root / "git_handoff.md"
        result = git_handoff_packet.run_packet(
            ns(
                task_id="coagent_git_handoff_smoke",
                output=output,
                markdown_output=markdown,
                staged_file_warning_threshold=1,
                include_packet=True,
                json=True,
            )
        )
        assert output.exists()
        assert markdown.exists()
        packet = json.loads(output.read_text(encoding="utf-8"))
        assert packet["schema_type"] == "coagent_git_handoff_packet"
        assert packet["mode"] == "read_only"
        assert "no commit" in packet["non_goals"]
        assert isinstance(packet["batches"], list)
        assert packet["totals"]["batch_count"] == len(packet["batches"])
        if packet["batches"]:
            first = packet["batches"][0]
            assert "commands" in first
            assert "inspect" in first["commands"]
            assert "verify" in first["commands"]
            assert "split_commit_safety" in first["commands"]
        markdown_text = markdown.read_text(encoding="utf-8")
        assert "CoAgent Git Handoff Packet" in markdown_text
        assert "Required Review Gates" in markdown_text
        assert "GitSafetyReview" in markdown_text
        assert result["outputs"]["json"].endswith("git_handoff.json")

    print("git_handoff_packet_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
