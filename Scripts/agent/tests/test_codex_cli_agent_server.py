"""Offline contract tests for the Model Studio Codex CLI bridge."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = ROOT / "Scripts" / "agent"
sys.path.insert(0, str(AGENT_DIR))

import codex_cli_agent_server as server  # noqa: E402


class CodexCliAgentServerTests(unittest.TestCase):
    def test_config_declares_project_built_binary_and_read_only_policy(self) -> None:
        config = server.load_config()
        self.assertEqual(config.binary_env, "MOSIM_CODEX_BIN")
        self.assertIn("src/Agent/codex-main", config.windows_binary)
        self.assertEqual(config.sandbox, "read-only")
        self.assertEqual(config.approval_policy, "never")

    def test_health_payload_contains_no_credentials(self) -> None:
        with patch.object(server, "resolve_codex_binary", return_value=None):
            payload = server.health_payload()
        serialized = json.dumps(payload).lower()
        self.assertIn("codex_cli", serialized)
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("authorization", serialized)

    def test_prompt_and_command_keep_the_read_only_contract(self) -> None:
        prompt = server.build_prompt("当前证据是什么？", "任务：ClimbPath")
        self.assertIn("不得修改任何文件", prompt)
        command = server.build_command(Path("C:/MoSim/codex.exe"), prompt)
        self.assertIn("--sandbox", command)
        self.assertIn("read-only", command)
        self.assertIn("--ephemeral", command)
        self.assertIn("--config", command)
        self.assertIn('approval_policy="never"', command)
        self.assertNotIn("--ask-for-approval", command)

    def test_jsonl_parser_uses_only_agent_message_text(self) -> None:
        output = "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "test"}),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"id": "item_1", "type": "command_execution", "command": "rg", "aggregated_output": "", "exit_code": 0, "status": "completed"},
                    }
                ),
                json.dumps({"type": "item.completed", "item": {"id": "item_2", "type": "agent_message", "text": "这是证据结论。"}}),
            ]
        )
        answer, error = server.parse_event_stream(output)
        self.assertEqual(answer, "这是证据结论。")
        self.assertEqual(error, "")

    def test_missing_project_binary_returns_build_instruction(self) -> None:
        with patch.object(server, "resolve_codex_binary", return_value=None):
            result = server.query_agent("请解释当前任务")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "codex_not_built")
        self.assertIn("src/Agent", result["answer"])

    def test_studio_bridge_points_to_codex_cli_backend(self) -> None:
        bridge = (ROOT / "apps" / "model_studio" / "src" / "agent_integration.jl").read_text(encoding="utf-8")
        self.assertIn("codex_cli_agent_server.py", bridge)


if __name__ == "__main__":
    unittest.main()
