"""Offline tests for the Model Studio Agent safety and configuration contract."""

from __future__ import annotations

import dataclasses
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = ROOT / "Scripts" / "agent"
sys.path.insert(0, str(AGENT_DIR))

import model_studio_agent_tools as tools  # noqa: E402
import mworks_analysis_agent_server as server  # noqa: E402


class ModelStudioAgentTests(unittest.TestCase):
    def test_config_uses_openai_and_non_secret_environment_variable(self) -> None:
        config = server.load_config()
        self.assertEqual(config.model_provider, "OpenAI")
        self.assertEqual(config.api_key_env, "MOSIM_OPENAI_API_KEY")
        self.assertTrue(config.disable_response_storage)
        self.assertGreater(config.max_tool_rounds, 0)

    def test_health_payload_never_contains_a_key(self) -> None:
        payload = server.health_payload()
        self.assertIn("status", payload)
        self.assertNotIn("api_key", payload)
        self.assertNotIn("authorization", payload)

    def test_registered_routes_are_readable(self) -> None:
        result = tools.list_formal_runner_routes()
        self.assertIn("climb_path_50s", result["formal_task_ids"])
        self.assertGreater(result["route_count"], 0)
        self.assertTrue(all(row["available"] for row in result["routes"]))

    def test_tool_catalog_has_thirty_read_only_entries(self) -> None:
        self.assertEqual(len(tools.TOOLS), 30)
        for name in (
            "compute_controller_metrics",
            "validate_gate_status",
            "generate_comparison_chart",
            "read_mworks_doc_section",
            "validate_sysblock_connections",
        ):
            self.assertIn(name, tools.TOOLS)
        capabilities = tools.get_agent_capabilities()
        self.assertTrue(capabilities["read_only"])

    def test_secret_and_external_paths_are_rejected(self) -> None:
        for path in (".env", "../outside.txt", "C:/Users/HP/.codex/config.toml"):
            with self.assertRaises(tools.ToolError):
                tools.read_project_document(path)

    def test_project_document_and_capability_queries_are_read_only(self) -> None:
        document = tools.read_project_document("Docs/Workflows/run_simulation.md", 1, 10)
        self.assertEqual(document["line_start"], 1)
        capabilities = tools.get_agent_capabilities()
        self.assertTrue(capabilities["read_only"])
        self.assertIn("启动 CheckModel 或仿真", capabilities["blocked_actions"])

    def test_frozen_gate_and_run_record_tools_use_existing_evidence(self) -> None:
        gate = tools.validate_gate_status()
        self.assertEqual(gate["effective_passed_count"], 28)
        self.assertEqual(gate["effective_failed_count"], 20)
        controller_gate = tools.validate_gate_status("adaptive_backstepping")
        self.assertEqual(controller_gate["status"], "pass")
        records = tools.locate_run_record("adaptive_backstepping", "climb_path_50s")
        self.assertGreaterEqual(records["record_count"], 1)
        comparison = tools.compare_controllers(["adaptive_backstepping"])
        self.assertEqual(comparison["controller_count"], 1)
        self.assertEqual(comparison["rows"][0]["controller_id"], "adaptive_backstepping")

    def test_csv_metrics_and_plot_handoff_are_no_write(self) -> None:
        path = "Results/control_platform/hinf_hover_wrench_repair_20260730/raw/hinf_hover_wrench_formal.csv"
        metrics = tools.compute_controller_metrics(path, error_column="position_error_norm", time_column="time")
        self.assertGreater(metrics["sample_count"], 0)
        self.assertGreaterEqual(metrics["rmse"], 0.0)
        plot = tools.generate_trajectory_plot(path, "x", "y", "z")
        self.assertIn("未生成文件", plot["execution"])
        figure = tools.export_report_figure(
            "Results/control_platform/phase2_full_48_climbpath/g3_repair/G3_STATUS.json",
            "g3_gate_summary",
        )
        self.assertIn("没有写入", figure["execution"])

    def test_model_and_skill_tools_remain_static(self) -> None:
        model = "MoSimQuadrotorModel.Experiment.Runners.Formal.Px4CtrlFormalRunner"
        dependencies = tools.get_model_dependencies(model)
        self.assertTrue(dependencies["path"].endswith("Px4CtrlFormalRunner.mo"))
        connections = tools.validate_sysblock_connections(model)
        self.assertGreater(connections["static_connect_count"], 0)
        self.assertTrue(connections["manual_check_required"])
        skills = tools.list_available_skills()
        self.assertGreaterEqual(skills["skill_count"], 8)
        documents = tools.list_mworks_documents()
        self.assertGreater(documents["document_count"], 0)
        section = tools.read_mworks_doc_section(documents["documents"][0]["path"], 1, 5)
        self.assertLessEqual(section["line_end"], 5)

    def test_missing_key_does_not_call_network(self) -> None:
        config = dataclasses.replace(
            server.CONFIG,
            api_key_env="MOSIM_AGENT_TEST_MISSING_KEY",
            fallback_api_key_env="MOSIM_AGENT_TEST_MISSING_FALLBACK",
        )
        result = server.query_agent("请解释当前控制链", config=config)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "model_not_configured")

    def test_responses_tool_loop_uses_only_registered_read_only_tool(self) -> None:
        config = dataclasses.replace(
            server.CONFIG,
            api_key_env="MOSIM_AGENT_TEST_KEY",
            fallback_api_key_env="MOSIM_AGENT_TEST_FALLBACK",
        )
        responses = [
            {
                "id": "response-1",
                "output": [
                    {
                        "type": "function_call",
                        "call_id": "call-1",
                        "name": "get_agent_capabilities",
                        "arguments": "{}",
                    }
                ],
            },
            {
                "id": "response-2",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "这是只读分析结果。"}],
                    }
                ],
            },
        ]
        with patch.dict(os.environ, {"MOSIM_AGENT_TEST_KEY": "test-only"}, clear=False):
            with patch.object(server, "_response_request", side_effect=responses) as request:
                result = server.query_agent("能力边界是什么？", "当前配置", config=config)
        self.assertTrue(result["ok"])
        self.assertEqual(result["tools_used"], ["get_agent_capabilities"])
        self.assertIn("只读", result["answer"])
        self.assertEqual(request.call_count, 2)
        follow_up = request.call_args_list[1].args[1]
        self.assertEqual(follow_up["input"][0]["type"], "function_call_output")

    def test_server_health_cli_is_key_free(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(AGENT_DIR / "mworks_analysis_agent_server.py"), "--health"],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["read_only"])

    def test_studio_source_uses_the_agent_bridge(self) -> None:
        source = (ROOT / "apps" / "model_studio" / "src" / "app.jl").read_text(encoding="utf-8")
        bridge = (ROOT / "apps" / "model_studio" / "src" / "agent_integration.jl").read_text(encoding="utf-8")
        self.assertIn('include(joinpath(@__DIR__, "agent_integration.jl"))', source)
        self.assertIn("AgentIntegration.start_mworks_turn", source)
        self.assertIn("AgentIntegration.poll_mworks_turn", source)
        self.assertIn("Only loopback binding is allowed", (AGENT_DIR / "mworks_analysis_agent_server.py").read_text(encoding="utf-8"))
        self.assertIn("MOSIM_OPENAI_API_KEY", (ROOT / "Config" / "control_platform" / "model_studio_agent_v1.toml").read_text(encoding="utf-8"))
        self.assertIn("query_mworks_agent", bridge)


if __name__ == "__main__":
    unittest.main()
