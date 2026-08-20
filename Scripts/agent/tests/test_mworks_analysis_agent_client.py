"""Offline contract tests for the persistent loopback HTTP client."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = ROOT / "Scripts" / "agent"
sys.path.insert(0, str(AGENT_DIR))

import mworks_analysis_agent_client as client  # noqa: E402


class PersistentClientTests(unittest.TestCase):
    def test_turn_protocol_contains_public_telemetry_fields(self) -> None:
        output = io.StringIO()
        response = {
            "ok": True,
            "status": "running",
            "answer": "",
            "partial_answer": "片段",
            "activities": ["只读工具调用"],
            "request_id": "abc12345",
            "error_code": "",
            "codex_thread_id": "thread1234",
            "error": "",
            "public_phase": "tool_call",
            "elapsed_time_s": 1.25,
            "updated_at": "2026-08-18T00:00:00Z",
            "poll_count": 3,
        }
        with patch("sys.stdout", output):
            client.emit_turn(response)
        fields = output.getvalue().strip().split("\t")
        self.assertEqual(fields[0], "turn")
        self.assertEqual(len(fields), 14)
        self.assertEqual(client.decode_argument(fields[10]), "tool_call")
        self.assertEqual(client.decode_argument(fields[13]), "3")

    def test_stdio_loop_reuses_one_client_for_sequential_http_requests(self) -> None:
        responses = [
            {"status": "ok", "configured": True},
            {
                "ok": True,
                "status": "running",
                "answer": "",
                "partial_answer": "片段",
                "activities": ["只读工具调用"],
                "request_id": "abc12345",
                "error_code": "",
                "codex_thread_id": "thread1234",
                "error": "",
                "public_phase": "tool_call",
                "elapsed_time_s": 0.5,
                "updated_at": "2026-08-18T00:00:00Z",
                "poll_count": 1,
            },
        ]
        stdin = io.StringIO("health\nturn-status\tYWJjMTIzNDU=\n")
        stdout = io.StringIO()
        with patch.object(client, "request_json", side_effect=responses) as request, patch("sys.stdin", stdin), patch("sys.stdout", stdout):
            self.assertEqual(client.stdio_loop("127.0.0.1", 8765, 15), 0)
        self.assertEqual(request.call_count, 2)
        lines = stdout.getvalue().splitlines()
        self.assertEqual(lines[0].split("\t")[0], "health")
        self.assertEqual(lines[1].split("\t")[0], "turn")
        self.assertEqual(client.decode_argument(lines[1].split("\t")[10]), "tool_call")


if __name__ == "__main__":
    unittest.main()
