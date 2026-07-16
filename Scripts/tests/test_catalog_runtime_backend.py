from __future__ import annotations

import json
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

    backend = CatalogRuntimeBackend(process_factory=factory)
    monkeypatch.setattr("src.orchestration.runtime_backend.DEFAULT_RUN_ROOT", tmp_path)
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


def test_stop_uses_fixed_helper_and_owned_process(tmp_path: Path, monkeypatch) -> None:
    process = FakeProcess()
    stop_calls = []

    def runner(command, **kwargs):
        stop_calls.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    backend = CatalogRuntimeBackend(process_factory=lambda *args, **kwargs: process, command_runner=runner)
    monkeypatch.setattr("src.orchestration.runtime_backend.DEFAULT_RUN_ROOT", tmp_path)
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
