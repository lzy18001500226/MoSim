from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts/quality/check_ue_truth_replay_contract.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_ue_truth_replay_contract", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_default_truth_replay_contract_passes_for_two_scenes(tmp_path: Path) -> None:
    checker = load_checker()
    tmp_path.mkdir(parents=True, exist_ok=True)
    output_json = tmp_path / "ue_truth_replay_contract_check.json"
    output_md = tmp_path / "ue_truth_replay_contract_check.md"
    report = checker.validate(
        ROOT / "Results/unreal_scene_mapping",
        list(checker.DEFAULT_SCENES),
        ROOT / "Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation",
    )
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checker.write_markdown(output_md, report)

    assert report["ok"], report
    assert report["schema"] == "mosim.ue_truth_replay_contract_check.v1"
    assert report["status"] == "ue_truth_replay_static_ready_runtime_blocked_or_degraded"
    assert report["runtime_ready"] is False
    assert "unreal_editor_listener_unavailable" in report["runtime_blockers"]
    scenes = {scene["scene_id"]: scene for scene in report["scenes"]}
    assert set(scenes) == {"factoryenvironmentcollect", "derelictcorridormegascans"}
    assert scenes["factoryenvironmentcollect"]["status"] == "ue_truth_replay_static_contract_ready"
    assert scenes["factoryenvironmentcollect"]["counts"]["path_cells"] == 34
    assert scenes["derelictcorridormegascans"]["status"] == "ue_truth_replay_static_contract_ready"
    assert scenes["derelictcorridormegascans"]["counts"]["path_cells"] == 45
    assert report["accepted_run"]["accepted_candidate"]["controller_id"] == "linear_mpc_online_fault_allocation_sysblock"
    assert output_json.exists()
    assert "Static readiness does not prove planner_ready" in output_md.read_text(encoding="utf-8")


def test_rejects_scene_planner_global_truth_leak(tmp_path: Path) -> None:
    checker = load_checker()
    source_root = ROOT / "Results/unreal_scene_mapping"
    mapping_root = tmp_path / "unreal_scene_mapping"
    scene_root = mapping_root / "factoryenvironmentcollect"
    scene_root.mkdir(parents=True)

    for name in [
        "planner_summary.json",
        "occupancy_grid.json",
        "runtime_review_bundle.json",
    ]:
        shutil.copy2(source_root / "factoryenvironmentcollect" / name, scene_root / name)
    (scene_root / "mworks_smoke/collision").mkdir(parents=True)
    shutil.copy2(
        source_root / "factoryenvironmentcollect/mworks_smoke/collision/mworks_scene_truth_collision.json",
        scene_root / "mworks_smoke/collision/mworks_scene_truth_collision.json",
    )
    shutil.copy2(source_root / "UE_SCENE_RUNTIME_READINESS.json", mapping_root / "UE_SCENE_RUNTIME_READINESS.json")

    planner_path = scene_root / "planner_summary.json"
    planner = json.loads(planner_path.read_text(encoding="utf-8"))
    planner["global_truth_available_to_planner"] = True
    planner_path.write_text(json.dumps(planner, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = checker.validate(
        mapping_root,
        ["factoryenvironmentcollect"],
        ROOT / "Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation",
    )
    assert not report["ok"]
    assert any("planner_global_truth_must_be_false" in issue for issue in report["issues"])


def main() -> int:
    temp = ROOT / "Results/tmp/test_ue_truth_replay_contract"
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)
    try:
        test_current_default_truth_replay_contract_passes_for_two_scenes(temp / "pass")
        test_rejects_scene_planner_global_truth_leak(temp / "reject")
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    print("[OK] UE truth replay contract tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
