#!/usr/bin/env python3
"""Static contract checks for the RACER MID360/FAST-LIO frontend."""

from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_swarm_gate.sh"
FACTORY_COVERAGE_RUNNER = (
    ROOT / "Scripts" / "sunray" / "run_factory_l2_indoor_racer_swarm_coverage_gate.sh"
)
INSTANCE_LAUNCH = ROOT / "Scripts" / "sunray" / "fastlio_racer_instance.launch"
RACER_LAUNCH = ROOT / "Scripts" / "sunray" / "racer_swarm_px4ctrl_d3.launch"


class RacerFastlioFrontendContractTest(unittest.TestCase):
    def test_instance_launch_is_valid_and_remaps_absolute_fastlio_outputs(self) -> None:
        root = ET.parse(INSTANCE_LAUNCH).getroot()
        self.assertEqual(root.tag, "launch")
        remaps = {
            item.attrib["from"]: item.attrib["to"]
            for item in root.findall(".//remap")
        }
        self.assertEqual(
            remaps,
            {
                "/cloud_registered": "$(arg cloud_registered_topic)",
                "/cloud_registered_body": "$(arg cloud_registered_body_topic)",
                "/Laser_map": "$(arg laser_map_topic)",
                "/Odometry": "$(arg odom_topic)",
                "/path": "$(arg path_topic)",
            },
        )

    def test_runner_defaults_to_per_uav_fastlio_and_has_input_only_gate(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('RACER_SENSOR_SOURCE="${RACER_SENSOR_SOURCE:-fastlio}"', text)
        self.assertIn('RACER_INPUT_GATE_ONLY="${RACER_INPUT_GATE_ONLY:-false}"', text)
        self.assertIn('start_racer_fastlio_frontend "${uid}"', text)
        self.assertIn('"RACER_FASTLIO_INPUT_GATE.json"', text)
        for uid_topic in (
            '/uav${uid}/livox/lidar',
            '/uav${uid}/livox/imu',
            '/uav${uid}/mosim/fastlio/odom_raw',
            '/uav${uid}/mosim/fastlio/cloud_registered_raw',
        ):
            self.assertIn(uid_topic, text)

    def test_factory_coverage_runner_locks_racer_to_fastlio_frontend(self) -> None:
        text = FACTORY_COVERAGE_RUNNER.read_text(encoding="utf-8")
        for contract in (
            "RACER_SENSOR_SOURCE=fastlio",
            "RACER_INPUT_GATE_ONLY=false",
            'RACER_FASTLIO_SCAN_RATE_HZ="${RACER_FASTLIO_SCAN_RATE_HZ:-20.0}"',
            'RACER_FASTLIO_ALIGNMENT_Z_SOURCE="${RACER_FASTLIO_ALIGNMENT_Z_SOURCE:-truth}"',
            'RACER_FASTLIO_ALIGNMENT_REFERENCE="${RACER_FASTLIO_ALIGNMENT_REFERENCE:-config}"',
            'MIN_EXPECTED_RTF="${MIN_EXPECTED_RTF:-0.08}"',
            'WALL_TIMEOUT_S="${WALL_TIMEOUT_S:-$((TOTAL_TIMEOUT_S + 600))}"',
            'timeout --kill-after=15s "${WALL_TIMEOUT_S}s"',
        ):
            self.assertIn(contract, text)

        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('--alignment-reference "${RACER_FASTLIO_ALIGNMENT_REFERENCE}"', runner)
        self.assertIn('--alignment-origin-xyz "${alignment_origin_x} ${alignment_origin_y} 0.0"', runner)
        self.assertIn('--world-cloud-topic-template', runner)
        self.assertIn('${RACER_LOCAL_CLOUD_TOPIC_TEMPLATE}', runner)

    def test_racer_uses_cloud_input_and_keeps_depth_unused(self) -> None:
        text = RACER_LAUNCH.read_text(encoding="utf-8")
        for uid in (1, 2, 3):
            self.assertIn(
                f'<arg name="depth_topic" value="/uav{uid}/mosim/racer_d3/depth_unused"/>',
                text,
            )
            self.assertIn(
                f'<arg name="cloud_topic" value="$(arg uav{uid}_cloud_topic)"/>',
                text,
            )


if __name__ == "__main__":
    unittest.main()
