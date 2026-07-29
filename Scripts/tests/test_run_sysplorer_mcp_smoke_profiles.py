#!/usr/bin/env python3
"""Regression checks for Sysplorer MCP smoke runner profiles."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "Scripts" / "mworks" / "run_sysplorer_mcp_smoke.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_sysplorer_mcp_smoke", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_diagnostics_smoke_metrics_do_not_require_tracking_columns() -> None:
    module = load_module()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        raw_csv = tmp_root / "raw.csv"
        metrics_json = tmp_root / "metrics.json"
        metrics_csv = tmp_root / "metrics.csv"
        raw_csv.write_text(
            "time,total_thrust_loss,roll_moment_imbalance\n"
            "0.00,0.0,0.0\n"
            "0.05,0.1,0.02\n"
            "0.10,0.2,0.04\n"
            "0.15,0.3,0.06\n"
            "0.20,0.4,0.08\n"
            "0.25,0.5,0.10\n"
            "0.30,0.6,0.12\n"
            "0.35,0.7,0.14\n"
            "0.40,0.8,0.16\n"
            "0.45,0.9,0.18\n"
            "0.50,1.0,0.20\n",
            encoding="utf-8",
            newline="\n",
        )
        module.write_metrics(
            raw_csv,
            metrics_json,
            metrics_csv,
            "mosimquad_formal_dynamics_rotor_effectiveness_smoke",
            "diagnostics_no_controller",
            "future_live_mworks_formal_dynamics_smoke_contract",
            "diagnostics_smoke",
        )
        metrics = json.loads(metrics_json.read_text(encoding="utf-8"))
        assert metrics["valid"] is True
        assert metrics["metrics_profile"] == "diagnostics_smoke"
        assert metrics["claim_role"] == "dynamics_smoke_only"
        assert metrics["diagnostics_column_count"] == 2
        assert "position_rmse_m" not in metrics
        assert metrics_csv.exists()


def test_diagnostics_profile_verifies_declared_variable_not_tracking_z() -> None:
    module = load_module()
    variables = {
        "time": "time",
        "dynamics_total_thrust": "dynamics.total_thrust",
        "dynamics_hover_thrust_error": "dynamics.hover_thrust_error",
    }
    assert module.choose_verify_result_var("diagnostics_declared", variables) == "dynamics.total_thrust"
    assert module.choose_verify_result_var("standard_tracking", {"time": "time", "z": "custom.z"}) == "custom.z"


def test_simulate_modelingpy_records_errors_before_partial_result_probes() -> None:
    module = load_module()

    class FakeClient:
        def call_tool(self, name, arguments, timeout_s):
            assert name == "call_code"
            source = arguments["payload"]["python_source"]
            assert '"GetLastErrors"' in source
            assert source.index("GetLastErrors") < source.index("GetResultVariableInfo")
            assert source.index("GetSimulationExitState") < source.index("GetResultVariableInfo")
            assert source.index("GetSimulationState") < source.index("GetResultVariableInfo")
            assert source.index("GetCurrentSimTime") < source.index("GetResultVariableInfo")
            assert source.index("MessageText") < source.index("GetResultVariableInfo")
            compile(source, "simulate_modelingpy.py", "exec")
            return {
                "ok": True,
                "run_script_result": {
                    "simulate": False,
                    "last_errors": ["solver failed at t=0"],
                    "post_simulation_diagnostics": {
                        "GetSimulationExitState": {"ok": True, "data": "failed"},
                        "GetCurrentSimTime": {"ok": True, "data": 0.0},
                    },
                    "has_readable_result": False,
                },
            }

    result = module.simulate_modelingpy(
        FakeClient(),
        model_name="Example.FailingRunner",
        target_time=[0.0, 0.2],
        native_result_dir=None,
        verify_result_var="position[3]",
    )

    assert result["simulate_api_reported_failure"] is True
    assert result["last_errors"] == ["solver failed at t=0"]
    assert result["post_simulation_diagnostics"]["GetSimulationExitState"]["data"] == "failed"


def test_simulate_modelingpy_supports_bounded_simulate_model_ex_diagnostics() -> None:
    module = load_module()

    class FakeClient:
        def call_tool(self, name, arguments, timeout_s):
            assert name == "call_code"
            source = arguments["payload"]["python_source"]
            assert "ModelingPy.SimulateModelEx" in source
            assert "'Algorithm': 'Euler'" in source
            assert "'IntegratorStep': 0.01" in source
            compile(source, "simulate_modelingpy_ex.py", "exec")
            return {
                "ok": True,
                "run_script_result": {
                    "simulate": True,
                    "last_errors": [],
                    "post_simulation_diagnostics": {},
                    "has_readable_result": True,
                    "result_probe_type": "Real",
                    "get_var_value_at": 0.2,
                },
            }

    result = module.simulate_modelingpy(
        FakeClient(),
        model_name="Example.EulerRunner",
        target_time=[0.0, 0.2],
        native_result_dir=None,
        verify_result_var="position[3]",
        simulation_api="simulate_model_ex",
        simulate_ex_options={"Algorithm": "Euler", "IntegratorStep": 0.01},
    )

    assert result["api"] == "ModelingPy.SimulateModelEx"
    assert result["simulation_options"] == {"Algorithm": "Euler", "IntegratorStep": 0.01}
    assert result["data"] is True


def test_simulate_modelingpy_supports_explicit_simulate_model_solver_profile() -> None:
    module = load_module()
    profile = {
        "algo": "Rkfix4",
        "integralStep": 0.002,
        "storeDouble": True,
        "storeEvent": False,
        "isPieceWiseStep": True,
        "pieceWiseStep": ((0.0, 0.002),),
    }

    class FakeClient:
        def call_tool(self, name, arguments, timeout_s):
            assert name == "call_code"
            source = arguments["payload"]["python_source"]
            assert "ModelingPy.SimulateModel(" in source
            assert "'algo': 'Rkfix4'" in source
            assert "'integralStep': 0.002" in source
            assert "'storeEvent': False" in source
            assert "'pieceWiseStep': ((0.0, 0.002),)" in source
            compile(source, "simulate_modelingpy_fixed_step.py", "exec")
            return {
                "ok": True,
                "run_script_result": {
                    "simulate": True,
                    "last_errors": [],
                    "post_simulation_diagnostics": {},
                    "has_readable_result": True,
                    "result_probe_type": "Real",
                    "get_var_value_at": 0.2,
                },
            }

    result = module.simulate_modelingpy(
        FakeClient(),
        model_name="Example.FixedStepRunner",
        target_time=[0.0, 0.2],
        native_result_dir=None,
        verify_result_var="position[3]",
        interval=0.01,
        simulate_model_options=profile,
    )

    assert result["api"] == "ModelingPy.SimulateModel"
    assert result["simulation_options"] == profile
    assert result["data"] is True


def test_simulate_modelingpy_rejects_simulate_model_result_binding_override() -> None:
    module = load_module()

    with pytest.raises(ValueError, match="must not override target-time or result-binding"):
        module.simulate_modelingpy(
            object(),
            model_name="Example.InvalidOverride",
            target_time=[0.0, 0.2],
            native_result_dir=None,
            verify_result_var="position[3]",
            simulate_model_options={"path": "C:/wrong"},
        )


def test_simulate_modelingpy_rejects_simulate_ex_time_override() -> None:
    module = load_module()

    with pytest.raises(ValueError, match="must not override target-time"):
        module.simulate_modelingpy(
            object(),
            model_name="Example.InvalidOverride",
            target_time=[0.0, 0.2],
            native_result_dir=None,
            verify_result_var="position[3]",
            simulation_api="simulate_model_ex",
            simulate_ex_options={"stopTime": 99.0},
        )


def test_mcp_client_uses_utf8_replacement_for_process_streams() -> None:
    module = load_module()
    captured: dict[str, object] = {}
    original_popen = module.subprocess.Popen

    class FakePipe:
        def write(self, _text: str) -> int:
            return 0

        def flush(self) -> None:
            return None

        def __iter__(self):
            return iter(())

    class FakeProcess:
        stdin = FakePipe()
        stdout = FakePipe()
        stderr = FakePipe()
        returncode = None

        def poll(self):
            return 0

        def terminate(self) -> None:
            return None

        def wait(self, timeout=None):
            return 0

        def kill(self) -> None:
            return None

    def fake_popen(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return FakeProcess()

    module.subprocess.Popen = fake_popen
    try:
        client = module.JsonlMcpClient(["fake-mcp"], Path("fake.jsonl"))
        client.close()
    finally:
        module.subprocess.Popen = original_popen

    kwargs = captured["kwargs"]
    assert kwargs["text"] is True
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["errors"] == "replace"
    assert kwargs["stdin"] is subprocess.PIPE
    assert kwargs["stdout"] is subprocess.PIPE
    assert kwargs["stderr"] is subprocess.PIPE


def main() -> int:
    test_diagnostics_smoke_metrics_do_not_require_tracking_columns()
    test_diagnostics_profile_verifies_declared_variable_not_tracking_z()
    test_simulate_modelingpy_records_errors_before_partial_result_probes()
    test_simulate_modelingpy_supports_bounded_simulate_model_ex_diagnostics()
    test_simulate_modelingpy_supports_explicit_simulate_model_solver_profile()
    test_simulate_modelingpy_rejects_simulate_model_result_binding_override()
    test_simulate_modelingpy_rejects_simulate_ex_time_override()
    test_mcp_client_uses_utf8_replacement_for_process_streams()
    print("[OK] run_sysplorer_mcp_smoke profile regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
