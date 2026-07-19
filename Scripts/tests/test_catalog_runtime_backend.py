from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from types import SimpleNamespace

from src.orchestration.runtime_backend import CatalogRuntimeBackend, _read_runtime_json


class FakeProcess:
    pid = 2468
    returncode = None

    def poll(self):
        return self.returncode

    def wait(self, timeout):
        self.returncode = 143
        return self.returncode

    def send_signal(self, _signal):
        self.returncode = 0

    def terminate(self):
        self.returncode = 0

    def kill(self):
        self.returncode = 1


def manifest(**overrides):
    value = {
        "run_id": "run-20260717-test",
        "experiment_profile_id": "px4ctrl_figure8_baseline_v1",
        "controller_id": "px4ctrl",
        "vehicle_count": 1,
    }
    value.update(overrides)
    return value


def test_catalog_backend_builds_only_fixed_project_launcher(tmp_path: Path, monkeypatch) -> None:
    process = FakeProcess()
    calls = []

    def factory(command, **kwargs):
        calls.append(command)
        return process

    backend = CatalogRuntimeBackend(process_factory=factory, run_root=tmp_path)
    result = backend.start(manifest())
    assert result["accepted"] is True
    assert result["lifecycle_state"] == "starting"
    assert calls[0][0:4] == ["wsl.exe", "-d", "Ubuntu-20.04", "--"]
    assert calls[0][-2:] == ["px4ctrl_figure8_single", "run-20260717-test"]
    assert "run_px4ctrl_basic_gate.sh" not in " ".join(calls[0])
    backend._close_logs("run-20260717-test")


def test_catalog_backend_rejects_unlisted_profile_and_invalid_run_id() -> None:
    backend = CatalogRuntimeBackend(process_factory=lambda *args, **kwargs: FakeProcess())
    unlisted = backend.start(manifest(experiment_profile_id="not-listed"))
    assert unlisted["reason_code"] == "runtime_profile_not_allowlisted"
    invalid = backend.start(manifest(run_id="run-bad;command"))
    assert invalid["reason_code"] == "invalid_run_id"


def test_catalog_backend_selects_generated_cascade_pid_operation(tmp_path: Path, monkeypatch) -> None:
    calls = []
    backend = CatalogRuntimeBackend(
        process_factory=lambda command, **kwargs: calls.append(command) or FakeProcess(), run_root=tmp_path
    )
    result = backend.start(
        manifest(
            experiment_profile_id="cascade_pid_figure8_generated_c_v1",
            controller_id="cascade_pid",
        )
    )
    assert result["accepted"] is True
    assert calls[0][-2:] == ["cascade_pid_figure8_single", "run-20260717-test"]
    backend._close_logs("run-20260717-test")


def test_catalog_backend_selects_only_rt0_accepted_mworks_live_profile(tmp_path: Path) -> None:
    calls = []
    backend = CatalogRuntimeBackend(
        process_factory=lambda command, **kwargs: calls.append(command) or FakeProcess(), run_root=tmp_path
    )
    accepted = backend.start(
        manifest(
            experiment_profile_id="mworks_live_official_pid_hover_50hz_v2",
            controller_id="official_pid",
        )
    )
    assert accepted["accepted"] is True
    assert calls[0][-2:] == ["mworks_live_official_pid_hover_50hz", "run-20260717-test"]
    backend._close_logs("run-20260717-test")

    accepted_200hz = backend.start(
        manifest(
            run_id="run-20260717-200hz",
            experiment_profile_id="mworks_live_official_pid_hover_200hz_v1",
            controller_id="official_pid",
        )
    )
    assert accepted_200hz["accepted"] is True
    assert calls[1][-2:] == ["mworks_live_official_pid_hover_200hz", "run-20260717-200hz"]
    backend._close_logs("run-20260717-200hz")

    blocked = backend.start(
        manifest(
            run_id="run-20260717-candidate",
            experiment_profile_id="mworks_live_official_pid_hover_candidate_v1",
            controller_id="official_pid",
        )
    )
    assert blocked["accepted"] is False
    assert blocked["reason_code"] == "runtime_profile_not_allowlisted"


def test_catalog_backend_selects_three_uav_swarm_formation_operation(tmp_path: Path) -> None:
    calls = []
    backend = CatalogRuntimeBackend(
        process_factory=lambda command, **kwargs: calls.append(command) or FakeProcess(), run_root=tmp_path
    )
    result = backend.start(
        manifest(
            experiment_profile_id="factory_l2_three_uav_swarm_formation_v1",
            controller_id="px4ctrl",
            vehicle_count=3,
        )
    )
    assert result["accepted"] is True
    assert calls[0][-2:] == ["factory_l2_three_uav_swarm_formation", "run-20260717-test"]
    backend._close_logs("run-20260717-test")


def test_model_operation_uses_only_fixed_project_worker(tmp_path: Path) -> None:
    calls = []
    backend = CatalogRuntimeBackend(
        process_factory=lambda command, **kwargs: calls.append(command) or FakeProcess(), run_root=tmp_path
    )
    model_manifest = manifest(
        experiment_profile_id="cascade_pid_figure8_generated_c_v1",
        controller_id="cascade_pid",
    )
    result = backend.start_model_operation(model_manifest, action="run_mil", operation_id="op-0123456789abcdef")
    assert result["accepted"] is True
    command = calls[0]
    assert command[-6:] == [
        "--action", "run_mil", "--run-id", "run-20260717-test", "--operation-id", "op-0123456789abcdef"
    ]
    assert command[1].endswith("Scripts\\ui\\run_model_studio_operation.py")
    backend._close_model_operation_logs("op-0123456789abcdef")


def test_model_operation_poll_accepts_persisted_status_after_restart(tmp_path: Path) -> None:
    backend = CatalogRuntimeBackend(run_root=tmp_path)
    model_manifest = manifest(
        experiment_profile_id="cascade_pid_figure8_generated_c_v1",
        controller_id="cascade_pid",
    )
    status_dir = tmp_path / model_manifest["run_id"] / "mworks" / "generate_code"
    status_dir.mkdir(parents=True)
    (status_dir / "OPERATION_STATUS.json").write_text(
        json.dumps({
            "status": "completed",
            "reason_code": "generate_code_completed",
            "operation_id": "op-fedcba9876543210",
            "result_gate": "mworks/generate_code/MWORKS_CODEGEN_RESULT.json",
        }),
        encoding="utf-8",
    )
    result = backend.poll_model_operation(
        model_manifest, action="generate_code", operation_id="op-fedcba9876543210"
    )
    assert result["state"] == "completed"
    assert result["result_gate"].endswith("MWORKS_CODEGEN_RESULT.json")


def test_model_operation_catalog_has_no_command_escape_hatch() -> None:
    catalog = json.loads(Path("Config/control_platform/model_operation_catalog.json").read_text(encoding="utf-8"))
    for entry in catalog["model_profiles"]:
        assert "command" not in entry and "arguments" not in entry
        assert set(entry) >= {"run_mil", "generate_code"}


def test_stop_uses_fixed_helper_and_owned_process(tmp_path: Path, monkeypatch) -> None:
    process = FakeProcess()
    stop_calls = []

    def runner(command, **kwargs):
        stop_calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    backend = CatalogRuntimeBackend(
        process_factory=lambda *args, **kwargs: process, command_runner=runner, run_root=tmp_path
    )
    assert backend.start(manifest())["accepted"] is True
    result = backend.stop(manifest())
    assert result["accepted"] is True
    assert stop_calls[0][-2].endswith("stop_orchestrated_runtime.sh")
    assert stop_calls[0][-1] == "run-20260717-test"


def test_runtime_catalog_contains_no_command_or_argument_escape_hatch() -> None:
    catalog = json.loads(
        Path("Config/control_platform/runtime_backend_catalog.json").read_text(encoding="utf-8")
    )
    for entry in catalog["runtime_profiles"]:
        assert "command" not in entry
        assert "arguments" not in entry
        assert entry["launcher"] == "wsl_project_script"


def test_runtime_catalog_and_runner_expose_fuel_fixed64_gate() -> None:
    catalog = json.loads(
        Path("Config/control_platform/runtime_backend_catalog.json").read_text(encoding="utf-8")
    )
    fuel = next(
        entry
        for entry in catalog["runtime_profiles"]
        if entry["operation_id"] == "factory_l2_fuel_fixed64_exploration"
    )
    assert fuel["experiment_profile_ids"] == ["factory_l2_fuel_fixed64_exploration_v1"]
    runner = Path("Scripts/ui/run_orchestrated_runtime.sh").read_text(encoding="utf-8")
    assert "run_fuel_fixed64_gate" in runner
    assert 'manifest.get("experiment_profile_id") != "factory_l2_fuel_fixed64_exploration_v1"' in runner
    assert '-FuelRandomSeed "${fuel_values[11]}"' in runner
    assert '-FuelBoxMinXOverride "${fuel_values[4]}"' in runner
    assert '-FuelPlannerMaxVelMps "${fuel_values[12]}"' in runner
    assert "FUEL RunManifest is incomplete; refusing to launch" in runner
    assert "-FuelCoverageExpansionGlobalSelector" in runner
    assert "-ReuseUnrealWindow" in runner


def test_poll_promotes_only_from_sidecar_readiness(tmp_path: Path) -> None:
    process = FakeProcess()
    backend = CatalogRuntimeBackend(process_factory=lambda *args, **kwargs: process, run_root=tmp_path)
    assert backend.start(manifest())["accepted"] is True
    assert backend.poll(manifest())["lifecycle_state"] == "starting"
    status = {
        "schema": "mosim.runtime_status.v1",
        "run_id": manifest()["run_id"],
        "status": "running",
        "reason_code": "runtime_ready",
        "updated_at": 1.0,
    }
    run_dir = tmp_path / manifest()["run_id"]
    (run_dir / "RUNTIME_STATUS.json").write_text(json.dumps(status), encoding="utf-8")
    result = backend.poll(manifest())
    assert result["lifecycle_state"] == "running"
    assert result["readiness"]["schema"] == "mosim.runtime_status.v1"
    backend._close_logs(manifest()["run_id"])


def test_runtime_json_reader_retries_transient_windows_share_error(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "status.json"
    path.write_text('{"status":"running"}', encoding="utf-8")
    original = Path.read_text
    calls = 0

    def flaky_read_text(candidate, *args, **kwargs):
        nonlocal calls
        if candidate == path and calls < 2:
            calls += 1
            raise PermissionError("temporary Windows share conflict")
        return original(candidate, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", flaky_read_text)
    assert _read_runtime_json(path, attempts=3, delay_s=0.0)["status"] == "running"
    assert calls == 2


def test_injection_uses_run_local_command_and_ack(tmp_path: Path) -> None:
    process = FakeProcess()
    run_id = manifest()["run_id"]
    full_manifest = manifest(experiment_profile_hash="profile-hash")
    backend = CatalogRuntimeBackend(
        process_factory=lambda *args, **kwargs: process,
        run_root=tmp_path,
        injection_ack_timeout_s=0.5,
    )
    assert backend.start(full_manifest)["accepted"] is True
    command = {
        "command_id": "inj-test-1",
        "run_id": run_id,
        "profile_hash": "profile-hash",
        "target": "motor_effectiveness",
        "requested_at": 1.0,
        "apply_mode": "set",
        "value": 0.65,
        "ramp_s": 0.0,
        "duration_s": 0.0,
        "restore_policy": "manual",
        "source": "test",
        "rotor_index": 1,
    }
    def acknowledge() -> None:
        command_path = tmp_path / run_id / "injection_commands" / "inj-test-1.json"
        deadline = time.monotonic() + 0.4
        while not command_path.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        ack_dir = tmp_path / run_id / "injection_acks"
        ack_dir.mkdir(parents=True)
        (ack_dir / "inj-test-1.json").write_text(
            json.dumps({"accepted": True, "reason_code": "motor_effectiveness_published", "applied_value": 0.65}),
            encoding="utf-8",
        )

    thread = threading.Thread(target=acknowledge)
    thread.start()
    result = backend.apply_injection(full_manifest, command)
    thread.join()
    assert result["accepted"] is True
    assert result["applied_value"] == 0.65
    queued = json.loads((tmp_path / run_id / "injection_commands" / "inj-test-1.json").read_text(encoding="utf-8"))
    assert queued["rotor_index"] == 1
    backend._close_logs(run_id)


def test_injection_rejects_profile_mismatch_before_queue(tmp_path: Path) -> None:
    process = FakeProcess()
    full_manifest = manifest(experiment_profile_hash="profile-hash")
    backend = CatalogRuntimeBackend(process_factory=lambda *args, **kwargs: process, run_root=tmp_path)
    assert backend.start(full_manifest)["accepted"] is True
    command = {
        "command_id": "inj-test-2", "run_id": full_manifest["run_id"], "profile_hash": "wrong",
        "target": "wind_speed_mps", "requested_at": 1.0, "apply_mode": "set", "value": 2.0,
        "ramp_s": 0.0, "duration_s": 0.0, "restore_policy": "manual", "source": "test",
    }
    result = backend.apply_injection(full_manifest, command)
    assert result["accepted"] is False
    assert result["reason_code"] == "injection_profile_hash_mismatch"
    backend._close_logs(full_manifest["run_id"])


def test_display_attach_uses_fixed_powershell_helper(tmp_path: Path) -> None:
    calls = []
    backend = CatalogRuntimeBackend(
        process_factory=lambda command, **kwargs: calls.append(command) or FakeProcess(), run_root=tmp_path
    )
    session = {
        "run_id": "run-20260717-test",
        "session_id": "display-1234567890",
        "displays": ["rviz_pointcloud", "unreal"],
    }
    result = backend.attach_display(session)
    assert result["accepted"] is True
    assert calls[0][0] == "powershell.exe"
    assert calls[0][5].endswith("attach_orchestrated_displays.ps1")
    assert calls[0][-2:] == ["-DisplayCsv", "rviz_pointcloud,unreal"]
    process, stdout, stderr = backend.display_processes.pop(session["session_id"])
    stdout.close()
    stderr.close()


def test_display_detach_accepts_persisted_detached_status_after_helper_error(tmp_path: Path) -> None:
    session = {
        "run_id": "run-20260717-test",
        "session_id": "display-1234567890",
        "displays": ["unreal"],
    }
    session_dir = tmp_path / session["run_id"] / "displays" / session["session_id"]
    session_dir.mkdir(parents=True)
    (session_dir / "DISPLAY_STATUS.json").write_text(
        json.dumps({"state": "detached", "session_id": session["session_id"]}),
        encoding="utf-8",
    )
    backend = CatalogRuntimeBackend(
        command_runner=lambda command, **kwargs: SimpleNamespace(
            returncode=4, stdout="", stderr="stale helper exit"
        ),
        run_root=tmp_path,
    )

    result = backend.detach_display(session)

    assert result["accepted"] is True
    assert result["reason_code"] == "display_already_detached"


def test_rviz_cleanup_targets_only_owned_display_sessions(tmp_path: Path) -> None:
    run_id = manifest()["run_id"]
    session_id = "display-1234567890"
    session_dir = tmp_path / run_id / "displays" / session_id
    session_dir.mkdir(parents=True)
    (session_dir / "DISPLAY_PROCESSES.json").write_text(
        json.dumps(
            [
                {"kind": "rviz_pointcloud", "pid": 100, "executable": "wsl.exe"},
                {"kind": "unreal", "pid": 200, "executable": "UnrealEditor.exe"},
            ]
        ),
        encoding="utf-8",
    )
    calls = []
    backend = CatalogRuntimeBackend(
        command_runner=lambda command, **kwargs: calls.append(command)
        or SimpleNamespace(returncode=0, stdout="", stderr=""),
        run_root=tmp_path,
    )
    result = backend.close_all_rviz(manifest(display_sessions=[session_id]))
    assert result["accepted"] is True
    assert result["session_count"] == 1
    assert calls[0][-1] == "-CloseRvizOnly"
    assert "UnrealEditor" not in " ".join(calls[0])


def test_ue_recording_uses_owned_unreal_window_and_requires_nonempty_output(tmp_path: Path) -> None:
    run_id = manifest()["run_id"]
    session_id = "display-1234567890"
    session_dir = tmp_path / run_id / "displays" / session_id
    session_dir.mkdir(parents=True)
    (session_dir / "DISPLAY_PROCESSES.json").write_text(
        json.dumps([{"kind": "unreal", "pid": 200, "executable": "UnrealEditor.exe"}]),
        encoding="utf-8",
    )
    gst = tmp_path / "gst-launch-1.0.exe"
    gst.write_bytes(b"test")
    calls = []
    process = FakeProcess()
    backend = CatalogRuntimeBackend(
        process_factory=lambda command, **kwargs: calls.append(command) or process,
        run_root=tmp_path,
        gstreamer_launch=gst,
        window_handle_resolver=lambda process_id: 9876 if process_id == 200 else None,
    )
    full_manifest = manifest(display_sessions=[session_id])
    started = backend.start_ue_recording(full_manifest)
    assert started["accepted"] is True
    assert "window-handle=9876" in calls[0]
    assert "bitrate=8000" in calls[0]
    output = backend.recording_paths[run_id]
    output.write_bytes(b"mp4")
    stopped = backend.stop_ue_recording(full_manifest)
    assert stopped["accepted"] is True
    assert stopped["size_bytes"] == 3
