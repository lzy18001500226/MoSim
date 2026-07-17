from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTROL_DIR = ROOT / "Scripts/control_platform"
sys.path.insert(0, str(CONTROL_DIR))
SCRIPT = CONTROL_DIR / "summarize_classic_controller_closeout.py"
SPEC = importlib.util.spec_from_file_location("classic_summary", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_appends_every_missing_canonical_row_without_replacing_base(tmp_path: Path) -> None:
    base = {"rows": [{"controller": "lqg", "status": "accepted"}]}
    registry = {
        "modules": [
            {
                "module_id": "lqr_baseline",
                "status": "implemented",
                "claim_ceiling": "sil_only",
                "latest_offline_evidence": "Results/example.json",
            }
        ]
    }
    payload = MODULE.build_payload(base, registry, wave_a_root=tmp_path)
    ids = [row["controller"] for row in payload["rows"]]
    assert ids[0] == "lqg"
    assert len(ids) == len(MODULE.CANONICAL_CONTROLLERS)
    assert len(ids) == len(set(ids))
    lqr = next(row for row in payload["rows"] if row["controller"] == "lqr_baseline")
    assert lqr["mworks_codegen_state"] == "passed"
    assert lqr["status"] == "not_run"


def test_blocked_algorithm_identity_stays_blocked() -> None:
    base = {"rows": []}
    registry = {"modules": [{"module_id": "mu_synthesis", "status": "blocked"}]}
    payload = MODULE.build_payload(base, registry)
    mu = next(row for row in payload["rows"] if row["controller"] == "mu_synthesis")
    assert mu["implementation_state"] == "blocked"
    assert mu["status"] == "not_run"
    assert "musyn" in mu["first_blocker"]


def test_wave_a_runtime_evidence_replaces_not_run_without_promoting_failure(
    tmp_path: Path,
) -> None:
    runtime = tmp_path / "lqr_baseline/takeoff_hover_land_retry3_px4_startup"
    write_json(
        runtime / "PX4CTRL_BASIC_MISSION_METRICS.json",
        {
            "status": "blocked",
            "reason": "hover_z_rmse_above_max:0.9",
            "pre_takeoff_state_gate": {"status": "passed"},
            "takeoff_reached_altitude": False,
            "landing_disarm": {"success": True},
            "steady_hover": {"xy_rmse_m": 0.08, "z_abs_rmse_m": 0.9},
        },
    )
    write_json(
        runtime / "WAVE_A_GENERATED_RUNTIME_PROVENANCE.json",
        {"status": "passed", "errors": []},
    )
    registry = {"modules": [{"module_id": "lqr_baseline", "status": "implemented"}]}
    payload = MODULE.build_payload(
        {"rows": []}, registry, wave_a_root=tmp_path
    )
    lqr = next(row for row in payload["rows"] if row["controller"] == "lqr_baseline")
    assert lqr["status"] == "executed_blocked"
    assert lqr["mission_status"] == "blocked"
    assert lqr["provenance_status"] == "passed"
    assert lqr["px4_startup_backend"] == "file_backend"
    assert lqr["hover_z_rmse_m"] == 0.9
    assert lqr["trajectory_status"] == "not_run"
    assert lqr["selectable"] is False
    assert "hover_z_rmse_above_max" in lqr["first_blocker"]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_classic_addition_uses_runtime_and_trajectory_evidence(tmp_path: Path) -> None:
    for relative in (
        MODULE.SOURCE_GATE,
        MODULE.MWORKS_MIL,
        MODULE.MWORKS_CODEGEN,
        MODULE.GENERATED_SIL,
    ):
        write_json(tmp_path / relative, {"status": "passed"})
    hover = {
        "status": "passed",
        "reason": None,
        "pre_takeoff_state_gate": {"status": "passed"},
        "takeoff_reached_altitude": True,
        "landing_disarm": {"success": True},
        "steady_hover": {"xy_rmse_m": 0.01, "z_abs_rmse_m": 0.015},
    }
    write_json(tmp_path / "gazebo/mrac/PX4CTRL_BASIC_MISSION_METRICS.json", hover)
    write_json(
        tmp_path / "gazebo/mrac/CLASSIC_CONTROLLER_RUNTIME_PROVENANCE.json",
        {"status": "passed"},
    )
    write_json(
        tmp_path / "gazebo/mrac_figure8/PX4CTRL_BASIC_MISSION_METRICS.json",
        {"status": "blocked", "reason": "trajectory_xyz_rmse_above_max:0.06"},
    )
    write_json(
        tmp_path / "gazebo/mrac_figure8/CLASSIC_CONTROLLER_RUNTIME_PROVENANCE.json",
        {"status": "passed"},
    )
    registry = {"modules": [{"module_id": "mrac", "status": "implemented"}]}
    payload = MODULE.build_payload({"rows": []}, registry, tmp_path)
    mrac = next(row for row in payload["rows"] if row["controller"] == "mrac")
    assert mrac["status"] == "executed_blocked"
    assert mrac["mission_status"] == "passed"
    assert mrac["provenance_status"] == "passed"
    assert mrac["trajectory_status"] == "blocked"
    assert mrac["selectable"] is False
    assert "trajectory_xyz_rmse_above_max" in mrac["first_blocker"]
