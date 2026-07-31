from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "Scripts" / "UE5" / "generate_factory_ue_render_replay.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_factory_ue_render_replay", GENERATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_single_uav_runtime_layout_uses_truth_and_command_reference(tmp_path: Path) -> None:
    generator = load_generator()
    (tmp_path / "truth.csv").write_text(
        "t,phase,x,y,z,vx,vy,vz,roll,pitch,yaw\n"
        "0.0,takeoff,1,2,3,0,0,0,0,0,0\n"
        "1.0,hover,2,3,4,1,1,1,0,0,0\n",
        encoding="utf-8",
    )
    (tmp_path / "reference.csv").write_text(
        "t,phase,x,y,z,cmd_x,cmd_y,cmd_z\n"
        "0.0,takeoff,1,2,3,10,20,30\n"
        "1.0,hover,2,3,4,11,21,31\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "ue_replay"

    args = generator.parse_args(
        [
            "--run-dir",
            str(tmp_path),
            "--output-dir",
            str(output_dir),
            "--vehicles",
            "uav1",
            "--state-source",
            "truth",
            "--source-profile",
            "sunray_ros1_gazebo_truth_csv_display_only",
            "--include-reference-plan",
            "--reference-plan-source",
            "reference",
            "--rate-hz",
            "2",
        ]
    )
    summary = generator.build_replay(args)

    assert summary["status"] == "passed"
    frames = [json.loads(line) for line in (output_dir / "ue_render_frame.jsonl").read_text(encoding="utf-8").splitlines()]
    assert frames[0]["position_m"] == [1.0, 2.0, 3.0]
    assert frames[0]["reference_position_m"] == [10.0, 20.0, 30.0]
    assert frames[0]["state_source_profile"] == "sunray_ros1_gazebo_truth_csv_display_only"
    assert frames[0]["local_plan"]["source"].endswith("reference.csv")

    manifest = json.loads((output_dir / "UE_RENDER_STREAM_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["source_topics_or_files"]["uav1"]["state"].endswith("truth.csv")
    assert manifest["source_topics_or_files"]["uav1"]["reference_plan"].endswith("reference.csv")
