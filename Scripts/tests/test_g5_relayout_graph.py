from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUALITY_DIR = ROOT / "Scripts" / "quality"
if str(QUALITY_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_DIR))

from apply_g5_smart_layout import apply_layout_to_text, normalized_visual_metadata
from build_g5_relayout_graph import build_graph, graph_summary, validate_graph


PID_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Controllers" / "GraphicalMIL" / "PidFamily"


class G5RelayoutGraphTests(unittest.TestCase):
    def test_pid_graphs_are_deterministic_and_well_formed(self) -> None:
        names = [
            "MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo",
            "MoSim_PID_GAIN_SCHEDULED_PID_GRAPHICAL_MIL.mo",
            "MoSim_PID_FUZZY_PID_GRAPHICAL_MIL.mo",
            "MoSim_PID_NEURAL_PID_GRAPHICAL_MIL.mo",
        ]
        for name in names:
            with self.subTest(name=name):
                model_path = PID_ROOT / name
                first = build_graph(model_path)
                second = build_graph(model_path)
                self.assertEqual(first, second)
                self.assertEqual(validate_graph(first), [])
                self.assertGreater(len(first["nodes"]), 10)
                self.assertGreater(len(first["edges"]), 10)

    def test_summary_binds_exact_source_hash(self) -> None:
        model_path = PID_ROOT / "MoSim_PID_CASCADE_PID_GRAPHICAL_MIL.mo"
        summary = graph_summary(model_path, build_graph(model_path))
        self.assertEqual(summary["schema"], "mosim.g5_relayout_graph_summary.v1")
        self.assertEqual(summary["source_model"], model_path.relative_to(ROOT).as_posix())
        self.assertEqual(len(summary["source_sha256"]), 64)
        self.assertTrue(json.dumps(summary, ensure_ascii=False))

    def test_layout_rewrite_changes_only_visual_metadata(self) -> None:
        source = """within Demo;
model Controller
  Lib.Block a
    annotation(Placement(transformation(origin = {0, 0}, extent = {{-5, -5}, {5, 5}})));
  Lib.Block b
    annotation(Placement(transformation(origin = {20, 0}, extent = {{-5, -5}, {5, 5}})));
equation
  connect(a.y, b.u)
    annotation(Line(origin = {0, 0}, points = {{0, 0}, {0, 0}}));
end Controller;
"""
        layout = {
            "children": [
                {"id": "a", "x": -40.0, "y": 10.0, "width": 20.0, "height": 10.0},
                {"id": "b", "x": 20.0, "y": 10.0, "width": 20.0, "height": 10.0},
            ],
            "edges": [
                {
                    "id": "edge_001_a_to_b",
                    "_color": [0, 0, 127],
                    "sections": [
                        {
                            "startPoint": {"x": -20.0, "y": 15.0},
                            "bendPoints": [{"x": 0.0, "y": 15.0}],
                            "endPoint": {"x": 20.0, "y": 15.0},
                        }
                    ],
                }
            ],
        }
        updated, counts = apply_layout_to_text(source, layout)
        self.assertEqual(counts, {"component_count": 2, "connect_count": 1})
        self.assertEqual(normalized_visual_metadata(source), normalized_visual_metadata(updated))
        self.assertIn("extent = {{-40,10}, {-20,20}}", updated)
        self.assertIn("Line(points = {{-20,15},{0,15},{20,15}}, color = {0,0,127})", updated)


if __name__ == "__main__":
    unittest.main()
