from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks" / "run_g6_controller_execution.py"


def load_module():
    spec = importlib.util.spec_from_file_location("g6_controller_execution", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def route(destination: str = "Docs/report/official_pid.png") -> dict[str, object]:
    return {
        "scheme_id": "official_pid",
        "result_root": "Results/g6/runs/official_pid",
        "target": {"model_sha256": "target-hash"},
        "required_artifacts": {"report_result_screenshot": destination},
    }


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_refreshes_only_a_hash_bound_same_route_archived_report_asset(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    row = route()
    destination = tmp_path / "Docs/report/official_pid.png"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"previous native result window")
    old_hash = module.sha256(destination)

    archive = tmp_path / "Results/g6/runs/official_pid/superseded/20260724_204050"
    archived_capture = archive / "screenshots/02_result_window.png"
    archived_capture.parent.mkdir(parents=True)
    archived_capture.write_bytes(b"previous native result window")
    write_json(
        archive / "RUN_RECORD.json",
        {
            "status": "passed",
            "scheme_id": "official_pid",
            "matrix": {"target": {"model_sha256": "target-hash"}},
            "report_result_screenshot": {
                "destination": "Docs/report/official_pid.png",
                "sha256": old_hash,
            },
        },
    )
    source = tmp_path / "new_capture.png"
    source.write_bytes(b"fresh native result window")

    result = module.materialize_report_result(row, source)

    assert destination.read_bytes() == b"fresh native result window"
    assert result["sha256"] == module.sha256(source)
    assert result["refresh_authority"]["scheme_id"] == "official_pid"
    assert result["refresh_authority"]["archived_capture"].endswith("screenshots/02_result_window.png")


def test_refreshes_hash_bound_same_route_asset_after_a_target_transition(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    row = route()
    destination = tmp_path / "Docs/report/official_pid.png"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"previous native result window")
    old_hash = module.sha256(destination)

    archive = tmp_path / "Results/g6/runs/official_pid/superseded/20260724_204050"
    archived_capture = archive / "screenshots/02_result_window.png"
    archived_capture.parent.mkdir(parents=True)
    archived_capture.write_bytes(b"previous native result window")
    write_json(
        archive / "RUN_RECORD.json",
        {
            "status": "passed",
            "scheme_id": "official_pid",
            "matrix": {"target": {"model_sha256": "previous-target-hash"}},
            "report_result_screenshot": {
                "destination": "Docs/report/official_pid.png",
                "sha256": old_hash,
            },
        },
    )
    source = tmp_path / "new_capture.png"
    source.write_bytes(b"fresh native result window")

    result = module.materialize_report_result(row, source)

    assert destination.read_bytes() == b"fresh native result window"
    assert result["refresh_authority"]["archived_model_sha256"] == "previous-target-hash"
    assert result["refresh_authority"]["current_model_sha256"] == "target-hash"
    assert result["refresh_authority"]["target_transition"] is True


def test_refuses_an_unproven_or_manually_replaced_report_asset(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    row = route()
    destination = tmp_path / "Docs/report/official_pid.png"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"manual asset")
    source = tmp_path / "new_capture.png"
    source.write_bytes(b"fresh native result window")

    with pytest.raises(RuntimeError, match="Refusing to replace"):
        module.materialize_report_result(row, source)


def test_classify_error_prioritizes_check_model_over_nested_results_payload() -> None:
    module = load_module()

    error = "CheckModel failed: {'results': [{'error': 'component type missing'}]}"

    assert module.classify_error(error) == "model_check_failed"


def test_classify_error_keeps_result_binding_for_actual_result_read_failures() -> None:
    module = load_module()

    assert module.classify_error("Declared result variable is unreadable") == "result_binding_failed"


def test_waits_for_fresh_native_result_and_complete_time_series(tmp_path: Path) -> None:
    module = load_module()
    native_result = tmp_path / "native" / "Runner" / "Result.msr"
    native_result.parent.mkdir(parents=True)
    native_result.write_bytes(b"current run")

    class FakeClient:
        def __init__(self) -> None:
            self.time_reads = 0

        def call_tool(self, name: str, arguments: dict[str, object], timeout_s: int) -> dict[str, object]:
            if name == "call_code":
                return {"ok": True, "run_script_result": {"open_result": True}}
            assert name == "result_manager"
            variable = arguments["var_names"][0]
            if variable == "time":
                self.time_reads += 1
                values = [] if self.time_reads == 1 else [float(value) for value in range(0, 51, 5)]
            else:
                values = [float(value) for value in range(11)]
            return {"ok": True, "data": [values]}

    result = module.wait_for_fresh_result_artifacts(
        FakeClient(),
        model_name="Example.Runner",
        variables={"time": "time", "x": "position[1]"},
        native_dir=tmp_path / "native",
        expected_native=native_result,
        expected_stop_time=50.0,
        not_before_unix=native_result.stat().st_mtime,
        timeout_s=1.0,
        poll_interval_s=0.0,
    )

    assert result["native_result"] == native_result
    assert result["series"]["time"][-1] == 50.0
    assert result["readiness"]["attempt_count"] >= 2


def test_preloads_canonical_base_packages_in_order(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    expected = [
        tmp_path / "Models/MoSimQuadrotorModel/package.mo",
    ]
    for path in expected:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"within {path.parent.name};", encoding="utf-8")

    class FakeClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, dict[str, object], int]] = []

        def call_tool(self, name: str, arguments: dict[str, object], timeout_s: int) -> dict[str, object]:
            self.calls.append((name, arguments, timeout_s))
            return {"ok": True}

    client = FakeClient()
    records = module.preload_base_packages(client)

    assert [record["path"] for record in records] == [
        "Models/MoSimQuadrotorModel/package.mo",
    ]
    assert [call[1]["file_path"] for call in client.calls] == [str(path) for path in expected]
    assert all(call[1]["force_reload"] is False for call in client.calls)
    assert all(call[1]["auto_load_deps"] is True for call in client.calls)


def test_loads_hash_bound_route_prerequisite_before_target(tmp_path: Path) -> None:
    module = load_module()
    module.ROOT = tmp_path
    prerequisite = tmp_path / "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/Example.mo"
    prerequisite.parent.mkdir(parents=True, exist_ok=True)
    prerequisite.write_text("within MoSimQuadrotorModel.Control.Implementations.Sysblocks;", encoding="utf-8")
    row = {
        "model_load_prerequisites": [
            {
                "role": "embedded_sysblock_definition",
                "source_component": "controller3_2",
                "source_declared_type": "MoSimQuadrotorModel.Control.Implementations.Sysblocks.Example",
                "model_file": "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/Example.mo",
                "model_class": "MoSimQuadrotorModel.Control.Implementations.Sysblocks.Example",
                "model_sha256": module.sha256(prerequisite),
            }
        ]
    }

    class FakeClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, dict[str, object], int]] = []

        def call_tool(self, name: str, arguments: dict[str, object], timeout_s: int) -> dict[str, object]:
            self.calls.append((name, arguments, timeout_s))
            return {"ok": True}

    client = FakeClient()
    records: list[dict[str, object]] = []
    module.load_route_model_prerequisites(client, row, records)

    assert [call[1]["file_path"] for call in client.calls] == [str(prerequisite)]
    assert records == [
        {
            "role": "embedded_sysblock_definition",
            "source_component": "controller3_2",
            "source_declared_type": "MoSimQuadrotorModel.Control.Implementations.Sysblocks.Example",
            "path": "Models/MoSimQuadrotorModel/Control/Implementations/Sysblocks/Example.mo",
            "model_class": "MoSimQuadrotorModel.Control.Implementations.Sysblocks.Example",
            "sha256": module.sha256(prerequisite),
            "force_reload": False,
            "auto_load_deps": True,
            "ok": True,
        }
    ]


def write_png(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 18), color=color).save(path)


def reconciliable_report_binding_fixture(tmp_path: Path):
    module = load_module()
    module.ROOT = tmp_path
    scheme_id = "official_pid"
    run_dir = tmp_path / "Results/g6/runs/official_pid"
    controller = tmp_path / "Models/MoSimQuadrotorModel/Control/Baselines/OfficialPid.mo"
    controller.parent.mkdir(parents=True, exist_ok=True)
    controller.write_text("within MoSimQuadrotorModel.Control.Baselines;", encoding="utf-8")
    controller_hash = module.sha256(controller)
    source_capture = run_dir / "screenshots/02_result_window.png"
    report_destination = tmp_path / "Docs/report/official_pid.png"
    write_png(source_capture, (20, 120, 220))
    write_png(report_destination, (220, 80, 20))
    native_result = run_dir / "raw/native/OfficialPid/Result.msr"
    native_result.parent.mkdir(parents=True, exist_ok=True)
    native_result.write_bytes(b"fresh native result")
    metrics = run_dir / "metrics/metrics.json"
    metrics.parent.mkdir(parents=True, exist_ok=True)
    metrics.write_text("{}", encoding="utf-8")

    row = {
        "scheme_id": scheme_id,
        "result_root": "Results/g6/runs/official_pid",
        "target": {
            "model_file": "Models/MoSimQuadrotorModel/Control/Baselines/OfficialPid.mo",
            "model_sha256": controller_hash,
        },
        "required_artifacts": {"report_result_screenshot": "Docs/report/official_pid.png"},
    }
    capture = {
        "phase": "result_window",
        "destination": module.relative(source_capture),
        "destination_sha256": module.sha256(source_capture),
    }
    error_message = f"Refusing to replace a different report result screenshot: {module.relative(report_destination)}"
    record = {
        "schema": "mosim.g6_controller_execution_run.v1",
        "scheme_id": scheme_id,
        "status": "result_binding_failed",
        "matrix": {"target": row["target"]},
        "error": {"message": error_message},
        "session_cleanup": {"verified_closed": True},
        "post_session_source_validation": {
            "state": "passed",
            "protected_source_sha256": {module.relative(controller): controller_hash},
        },
        "result_readiness": {
            "state": "ready",
            "attempts": [{"time_reaches_expected_stop": True, "full_series_ready": True}],
        },
        "native_result_locator": module.relative(native_result),
        "mworks_phase_screenshots": [capture],
        "artifact_refs": [],
    }
    write_json(run_dir / "RUN_RECORD.json", record)
    write_json(run_dir / "logs/screenshot_manifest.json", {"captures": [capture]})
    return module, row, run_dir, source_capture, report_destination


def test_reconciles_explicit_legacy_report_slot_after_completed_native_run(tmp_path: Path) -> None:
    module, row, run_dir, source_capture, report_destination = reconciliable_report_binding_fixture(tmp_path)
    old_hash = module.sha256(report_destination)

    outcome = module.reconcile_report_result_binding(row)

    assert module.sha256(report_destination) == module.sha256(source_capture)
    archived = tmp_path / outcome["archived_report_asset"]
    assert archived.is_file()
    assert module.sha256(archived) == old_hash
    assert (tmp_path / outcome["archive_manifest"]).is_file()
    record = json.loads((run_dir / "RUN_RECORD.json").read_text(encoding="utf-8"))
    assert record["status"] == "passed"
    assert "error" not in record
    assert record["report_result_screenshot"]["sha256"] == module.sha256(source_capture)
    assert record["report_result_binding_reconciliation"]["report_asset_before"]["sha256"] == old_hash


def test_reconciliation_refuses_to_overwrite_when_post_session_integrity_is_not_passed(tmp_path: Path) -> None:
    module, row, run_dir, source_capture, report_destination = reconciliable_report_binding_fixture(tmp_path)
    old_hash = module.sha256(report_destination)
    record_path = run_dir / "RUN_RECORD.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["post_session_source_validation"]["state"] = "failed"
    write_json(record_path, record)

    with pytest.raises(RuntimeError, match="post-session source validation"):
        module.reconcile_report_result_binding(row)

    assert module.sha256(report_destination) == old_hash
    assert module.sha256(source_capture) != old_hash
