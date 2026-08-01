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

    def test_initial_command_persists_a_read_only_conversation(self) -> None:
        prompt = server.build_prompt("当前证据是什么？", "任务：ClimbPath")
        self.assertIn("不得修改任何文件", prompt)
        command = server.build_command(Path("C:/MoSim/codex.exe"), prompt)
        self.assertIn("--sandbox", command)
        self.assertIn("read-only", command)
        self.assertNotIn("--ephemeral", command)
        self.assertIn("--ignore-user-config", command)
        self.assertIn("--config", command)
        self.assertIn('approval_policy="never"', command)
        self.assertNotIn("--ask-for-approval", command)

    def test_resume_command_reuses_the_persisted_thread(self) -> None:
        command = server.build_resume_command(
            Path("C:/MoSim/codex.exe"),
            "12345678-1234-1234-1234-123456789abc",
            "继续说明上一轮结论。",
        )
        self.assertEqual(command[1:3], ["exec", "resume"])
        self.assertIn("--json", command)
        self.assertIn("--ignore-user-config", command)
        self.assertIn("12345678-1234-1234-1234-123456789abc", command)
        self.assertNotIn("--ephemeral", command)

    def test_command_can_select_model_and_project_image(self) -> None:
        image = server.ROOT / "README.md"
        command = server.build_command(Path("C:/MoSim/codex.exe"), "问题", model="gpt-5.5", attachments=[image])
        self.assertIn("--model", command)
        self.assertIn("gpt-5.5", command)
        self.assertNotIn("--image", command)

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

    def test_jsonl_parser_exposes_safe_activity_labels(self) -> None:
        output = "\n".join(
            [
                json.dumps({"type": "turn.started"}),
                json.dumps({"type": "item.completed", "item": {"type": "command_execution"}}),
                json.dumps({"type": "turn.completed"}),
            ]
        )
        answer, error, activities = server.parse_event_stream_details(output)
        self.assertEqual(answer, "")
        self.assertEqual(error, "")
        self.assertEqual(activities, ["开始只读分析", "只读项目检索", "分析完成"])

    def test_missing_project_binary_returns_build_instruction(self) -> None:
        with patch.object(server, "resolve_codex_binary", return_value=None):
            result = server.query_agent("请解释当前任务")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "codex_not_built")
        self.assertIn("Codex CLI", result["answer"])

    def test_turn_payload_contains_only_public_progress(self) -> None:
        record = server.TurnRecord(request_id="abc12345")
        server._record_stream_event(record, {"type": "thread.started", "thread_id": "12345678-1234-1234-1234-123456789abc"})
        server._record_stream_event(record, {"type": "item.completed", "item": {"type": "command_execution", "command": "secret command"}})
        payload = server.turn_payload(record)
        self.assertEqual(payload["codex_thread_id"], "12345678-1234-1234-1234-123456789abc")
        self.assertIn("只读项目检索", payload["activities"])
        self.assertNotIn("secret command", json.dumps(payload, ensure_ascii=False))

    def test_studio_bridge_points_to_codex_cli_backend(self) -> None:
        bridge = (ROOT / "apps" / "model_studio" / "src" / "agent_integration.jl").read_text(encoding="utf-8")
        app_source = (ROOT / "apps" / "model_studio" / "src" / "app.jl").read_text(encoding="utf-8")
        self.assertIn("codex_cli_agent_server.py", bridge)
        self.assertIn("AbstractString", bridge)
        self.assertIn("start_mworks_turn", bridge)
        self.assertIn("poll_mworks_turn", bridge)
        self.assertIn("AssistantCodexThreadId", app_source)
        self.assertIn("Scrollable=false", app_source)
        self.assertNotIn("deleteat!(app.AssistantLines", app_source)
        self.assertIn("function trim_assistant_answer(app, answer, limit=700)", app_source)


if __name__ == "__main__":
    unittest.main()
