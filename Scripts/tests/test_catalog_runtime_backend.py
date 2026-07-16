from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from types import SimpleNamespace

from src.orchestration.runtime_backend import CatalogRuntimeBackend


class FakeProcess:
    pid = 2468
    returncode = None

    def poll(self):
        return self.returncode

    def wait(self, timeout):
        self.returncode = 143
        return self.returncode


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
