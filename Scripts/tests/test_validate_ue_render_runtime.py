from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "UE5" / "validate_ue_render_runtime.py"


class ValidateUeRenderRuntimeTests(unittest.TestCase):
    def write_json(self, path: Path, payload: dict) -> None:
        path.write_text(json.dumps(payload), encoding="utf-8")

    def make_bundle(self, root: Path) -> tuple[Path, Path]:
        replay = root / "replay"
        replay.mkdir()
        self.write_json(
            replay / "UE_RENDER_STREAM_MANIFEST.json",
            {
                "status": "replay_contract_passed",
                "run_id": "run-ue-001",
                "scene_id": "factoryenvironmentcollect",
                "map_id": "factory_l2",
                "transport_profile": {"feedback_to_runtime": False},
            },
        )
        self.write_json(replay / "UE_RENDER_STREAM_VALIDATION.json", {"status": "passed"})
        self.write_json(
            replay / "ue_receiver_metrics.json",
            {
                "run_id": "run-ue-001",
                "received_frames": 50,
                "receive_rate_hz": 10.0,
                "sequence_gap_count": 0,
                "receiver_drop_rate": 0.0,
                "payload_bytes_per_s": 1000.0,
            },
        )
        self.write_json(
            replay / "ue_frame_metrics.json",
            {"run_id": "run-ue-001", "ue_fps": 60.0, "ue_frame_ms_mean": 16.0, "ue_frame_ms_max": 20.0, "hitch_count_50ms": 0},
        )
        log = root / "MoSimSceneLibrary.log"
        log.write_text(
            "Quadrotor MWORKS UDP receiver listening on 0.0.0.0:5005\n"
            "Quadrotor MWORKS UDP first frame: scene=factoryenvironmentcollect map=factory_l2 seq=0\n",
            encoding="utf-8",
        )
        return replay, log

    def test_accepts_runtime_metrics_and_operator_pointer_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            replay, log = self.make_bundle(Path(temporary))
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--replay-dir",
                    str(replay),
                    "--ue-log",
                    str(log),
                    "--pointer-release-operator-confirmed",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((replay / "F7B_UE_RUNTIME_RECEIVER_STATUS.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "passed")
            self.assertEqual(payload["operator_review"]["pointer_release_status"], "passed")
            self.assertEqual(payload["transport"]["feedback_to_runtime"], False)

    def test_requires_explicit_pointer_release_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            replay, log = self.make_bundle(Path(temporary))
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--replay-dir", str(replay), "--ue-log", str(log)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            payload = json.loads((replay / "F7B_UE_RUNTIME_RECEIVER_STATUS.json").read_text(encoding="utf-8"))
            self.assertIn("pointer_release_operator_review_not_confirmed", payload["issues"])


if __name__ == "__main__":
    unittest.main()
