import importlib.util
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720"
MODEL_DIR = ROOT / "Models/MoSimQuadrotorModel/Guidance/Planning"


def load_auditor():
    path = ROOT / "Scripts/planning/audit_three_uav_mworks_result.py"
    spec = importlib.util.spec_from_file_location("three_uav_mworks_auditor", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ThreeUavOpenBlocksMworksTest(unittest.TestCase):
    def test_planning_bundle_is_collision_safe(self):
        metrics = json.loads(
            (RESULT_DIR / "metrics/three_uav_planning_metrics.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metrics["status"], "accepted")
        self.assertGreaterEqual(metrics["schedule"]["minimum_pair_distance_m"], 1.0)
        self.assertEqual(len(metrics["vehicles"]), 3)
        for index in range(1, 4):
            self.assertTrue((RESULT_DIR / f"raw/uav{index}_reference.csv").is_file())
            self.assertGreaterEqual(metrics["vehicles"][index - 1]["min_obstacle_distance_m"], 0.35)

    def test_generated_model_reuses_three_whole_aircraft_vehicles(self):
        model = (MODEL_DIR / "ThreeUavOpenBlocksReconfigurableFormationLinearMPC.mo").read_text(encoding="utf-8")
        vehicle = (MODEL_DIR / "OpenBlocksLinearMPCVehicle.mo").read_text(encoding="utf-8")
        self.assertEqual(model.count("OpenBlocksLinearMPCVehicle vehicle"), 3)
        self.assertEqual(vehicle.count("MoSimQuadrotorModel.Vehicle.Electricals.Actuator actuator"), 4)
        self.assertIn("terrain_render_stride = 10", model)
        vehicle_reference_connections = [
            line for line in model.splitlines()
            if line.strip().startswith("connect(reference") and "vehicle" in line
        ]
        self.assertEqual(len(vehicle_reference_connections), 9)

    def test_package_exposes_chinese_tree_alias(self):
        package = (MODEL_DIR / "package.mo").read_text(encoding="utf-8")
        order = (MODEL_DIR / "package.order").read_text(encoding="utf-8")
        self.assertIn("model OpenBlocksThreeUavFormation", package)
        self.assertIn("OpenBlocksThreeUavFormation", order.splitlines())

    def test_real_mworks_result_passes_collision_gate(self):
        auditor = load_auditor()
        metrics = auditor.audit(
            RESULT_DIR / "raw/mworks_full_conservative_304p84s.csv",
            RESULT_DIR / "metrics/three_uav_planning_metrics.json",
        )
        self.assertTrue(metrics["accepted"])
        self.assertEqual(metrics["status"], "accepted_with_reduced_clearance_margin")
        self.assertGreaterEqual(metrics["minimum_actual_pair_distance_m"], 1.0)
        self.assertGreaterEqual(metrics["minimum_clearance_lower_bound_m"], 0.0)
        self.assertFalse(metrics["gates"]["planning_margin_preserved"])
        manifest = json.loads(
            (RESULT_DIR / "logs/THREE_UAV_OPEN_BLOCKS_MWORKS_RUN_MANIFEST.json").read_text(encoding="utf-8")
        )
        native_record = next(
            artifact for artifact in manifest["artifacts"]
            if artifact["role"] == "native_result_local_only"
        )
        self.assertEqual(native_record["publication"], "local_only_over_100_mb")
        native = ROOT / native_record["path"]
        if native.is_file():
            self.assertEqual(native.stat().st_size, native_record["size_bytes"])
            self.assertEqual(hashlib.sha256(native.read_bytes()).hexdigest().upper(), native_record["sha256"])


if __name__ == "__main__":
    unittest.main()
