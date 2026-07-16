import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "sunray" / "build_racer_d0_source_audit.py"
SPEC = importlib.util.spec_from_file_location("build_racer_d0_source_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RacerD0SourceAuditTests(unittest.TestCase):
    def test_auto_detects_racer_and_fame_sources(self):
        racer = ROOT / "References" / "Lab" / "exploration_coverage" / "RACER"
        fame = (
            ROOT
            / "References"
            / "Lab"
            / "exploration_coverage"
            / "fast_multi_robot_exploration"
        )
        self.assertEqual(MODULE.detect_variant(racer, "auto"), "racer")
        self.assertEqual(MODULE.detect_variant(fame, "auto"), "fame")

    def test_fame_summary_and_findings_are_not_labeled_racer(self):
        fame = (
            ROOT
            / "References"
            / "Lab"
            / "exploration_coverage"
            / "fast_multi_robot_exploration"
        )
        interface = MODULE.collect_interface(fame, "fame")
        findings = MODULE.derive_findings(
            fame, interface, MODULE.collect_dependency_hints(fame), "fame"
        )
        self.assertTrue(all(item["id"].startswith("FAME_D0_") for item in findings))
        self.assertTrue(interface["code_topics"]["fame_exploration_fsm"]["present"])
        self.assertTrue(any("selectable planner variants" in item["claim"] for item in findings))


if __name__ == "__main__":
    unittest.main()
