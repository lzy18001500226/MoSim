from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from src.orchestration.runtime_sidecar_contract import build_operator_runtime_status


ROOT = Path(__file__).resolve().parents[2]
QGC_CUSTOM = ROOT / "src" / "ground_station" / "qgc" / "mosim_extension" / "custom"


def _manifest() -> dict[str, object]:
    return {
        "run_id": "qgc-runtime-status-test",
        "experiment_profile_id": "official_pid_hover_v1",
        "experiment_profile_hash": "profile-hash-test",
        "controller_backend": "mworks_live",
        "controller_id": "official_pid",
    }


def _sidecar_module():
    path = ROOT / "Scripts/ui/runtime_sidecar.py"
    spec = importlib.util.spec_from_file_location("mosim_runtime_sidecar_status_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_status_contract_binds_identity_and_leaves_unreported_values_absent() -> None:
    payload = build_operator_runtime_status(
        manifest=_manifest(),
        state="running",
        reason_code="runtime_ready",
        updated_at_unix_s=123.0,
    )

    assert payload == {
        "schema": "mosim.operator_runtime_status.v1",
        "run_id": "qgc-runtime-status-test",
        "experiment_profile_id": "official_pid_hover_v1",
        "experiment_profile_hash": "profile-hash-test",
        "controller_backend": "mworks_live",
        "state": "running",
        "reason_code": "runtime_ready",
        "updated_at_unix_s": 123.0,
    }


def test_status_contract_rejects_legacy_manifest_without_frozen_backend() -> None:
    legacy_manifest = _manifest()
    legacy_manifest.pop("controller_backend")

    with pytest.raises(ValueError, match="operator_runtime_status_manifest_identity_invalid"):
        build_operator_runtime_status(
            manifest=legacy_manifest,
            state="running",
            reason_code="runtime_ready",
            updated_at_unix_s=123.0,
        )


def test_sidecar_reads_only_same_run_finite_rt1_metrics(tmp_path: Path) -> None:
    sidecar = _sidecar_module()
    metrics_path = tmp_path / "observability" / "RT1_STATUS.json"
    metrics_path.parent.mkdir()
    metrics_path.write_text(
        json.dumps(
            {
                "run_id": "other-run",
                "command_age_ms": 9.0,
                "transport": {"rtt_ms_p95": 1.0},
            }
        ),
        encoding="utf-8",
    )
    assert sidecar._load_rt1_observability(tmp_path, "qgc-runtime-status-test") == {}

    metrics_path.write_text(
        json.dumps(
            {
                "run_id": "qgc-runtime-status-test",
                "command_age_ms": 4.5,
                "transport": {
                    "rtt_ms_p95": 6.25,
                    "receive_interval_jitter_ms": 0.75,
                    "estimated_command_drop_rate": 0.02,
                },
            }
        ),
        encoding="utf-8",
    )
    assert sidecar._load_rt1_observability(tmp_path, "qgc-runtime-status-test") == {
        "rtt_ms": 6.25,
        "jitter_ms": 0.75,
        "command_age_ms": 4.5,
        "packet_loss_rate": 0.02,
    }


def test_qgc_status_surface_checks_identity_and_marks_missing_metrics_unmeasured() -> None:
    bridge = (QGC_CUSTOM / "src" / "MoSimOperatorBridge.cc").read_text(encoding="utf-8")
    layer = (QGC_CUSTOM / "src" / "FlyViewCustomLayer.qml").read_text(encoding="utf-8")

    assert "isReadableOperatorRuntimeStatus" in bridge
    assert "operator_runtime_status_identity_mismatch" in bridge
    assert "runtimeStatusIsBound" in layer
    assert 'state === "completed"' in layer
    assert "root.runtimeMetricText" in layer
    assert "未测量" in layer
    assert "运行端未上报告警" in layer
