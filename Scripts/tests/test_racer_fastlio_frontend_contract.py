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
COMMONFRAME_GATE = ROOT / "Scripts" / "sunray" / "run_factory_l2_racer_fastlio_commonframe_gate.sh"
INSTANCE_LAUNCH = ROOT / "Scripts" / "sunray" / "fastlio_racer_instance.launch"
RACER_LAUNCH = ROOT / "Scripts" / "sunray" / "racer_swarm_px4ctrl_d3.launch"
OFFSET_BRIDGE = ROOT / "Scripts" / "ros" / "ros1_coordinate_offset_bridge.py"


class RacerFastlioFrontendContractTest(unittest.TestCase):
    def test_commonframe_pair_opt_requires_explicit_factory_opt_in(self) -> None:
        source = COMMONFRAME_GATE.read_text(encoding="utf-8")
        self.assertIn(
            'RACER_D3_DISABLE_PAIR_OPT="${RACER_D3_DISABLE_PAIR_OPT:-true}"',
            source,
        )
        self.assertIn(
            'RACER_D3_ALLOW_PAIR_OPT_FACTORY="${RACER_D3_ALLOW_PAIR_OPT_FACTORY:-false}"',
            source,
        )

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
        self.assertIn('RACER_FASTLIO_MIN_SIM_RATE_HZ="${RACER_FASTLIO_MIN_SIM_RATE_HZ:-15.0}"', text)
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
            'MIN_WALL_TIMEOUT_S=$((MAVROS_READY_TIMEOUT_S + TOTAL_TIMEOUT_S + 120))',
            'timeout --kill-after=15s "${WALL_TIMEOUT_S}s"',
        ):
            self.assertIn(contract, text)

        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('--alignment-reference "${RACER_FASTLIO_ALIGNMENT_REFERENCE}"', runner)
        self.assertIn('--alignment-origin-xyz "${alignment_origin_x} ${alignment_origin_y} 0.0"', runner)
        self.assertIn('--world-cloud-topic-template', runner)
        self.assertIn('${RACER_LOCAL_CLOUD_TOPIC_TEMPLATE}', runner)

    def test_commonframe_gate_freezes_the_accepted_racer_profile(self) -> None:
        text = COMMONFRAME_GATE.read_text(encoding="utf-8")
        for contract in (
            "RACER_SENSOR_SOURCE=fastlio",
            "RACER_D3_SWARM_SAFE_DIST=3.5",
            "RACER_D3_OBSTACLES_INFLATION=0.35",
            "EGO_CMD_SAFETY_SMOOTHING_MAX_SPEED_MPS=1.5",
            "EGO_CMD_SAFETY_MOTION_TIME_BASIS=ros_sim_time",
            "EGO_CMD_SAFETY_MAX_VELOCITY_MPS=2.0",
            "EGO_CMD_SAFETY_MAX_ACCELERATION_MPS2=1.2",
            "EGO_CMD_SAFETY_MAX_JERK_MPS3=6.0",
            "RACER_FASTLIO_ALIGNMENT_Z_SOURCE=truth",
        ):
            self.assertIn(contract, text)

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

    def test_reference_odom_uses_each_spawn_delta_for_common_local_origin(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn('offset_x="$(python3 - "${START1_X}" "${start_x}"', text)
        self.assertIn('offset_y="$(python3 - "${START1_Y}" "${start_y}"', text)
        self.assertIn('_output_topic:="${racer_odom_output}"', text)
        self.assertIn('_offset_x:="${offset_x}"', text)
        self.assertIn('_offset_y:="${offset_y}"', text)
        self.assertIn('_latch_input_origin:="$(if [[ "${RACER_SENSOR_SOURCE}" == "fastlio" ]]', text)
        self.assertIn('_origin_latch_samples:="$(if [[ "${RACER_SENSOR_SOURCE}" == "fastlio" ]]', text)
        self.assertIn('_target_origin_x:="${target_origin_x}"', text)
        self.assertIn('_target_origin_y:="${target_origin_y}"', text)

        bridge = OFFSET_BRIDGE.read_text(encoding="utf-8")
        self.assertIn('self.latch_input_origin = bool(rospy.get_param("~latch_input_origin", False))', bridge)
        self.assertIn('self.latched_input_origin', bridge)
        self.assertIn('"target_origin_xyz": self.target_origin', bridge)

    def test_dynamic_alignment_summary_is_written_during_runtime(self) -> None:
        adapter = (ROOT / "Scripts" / "sunray" / "fastlio_odom_alignment_adapter.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("dynamic_summary_last_write_wall", adapter)
        self.assertIn('"alignment_origin_xyz": list(self.args.alignment_origin_xyz)', adapter)
        self.assertIn('"reference_odom_topic": self.args.local_topic', adapter)
        self.assertIn('"child_frame": self.args.child_frame', adapter)
        self.assertIn('"comparison_mode": "first_sample_relative_motion"', adapter)
        self.assertIn('"initial_reference_xyz"', adapter)

        frontend = (ROOT / "Scripts" / "sunray" / "fuel_cloud_pose_frontend_diagnostic.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('"cloud_hz_sim"', frontend)
        self.assertIn('"cloud_nonmonotonic_stamps"', frontend)
        self.assertIn('"sync_callback_reorders"', frontend)
        self.assertIn('"sync_nonmonotonic_stamps"', frontend)
        self.assertIn("callback_reorder_only; source monotonicity is reported separately", frontend)

        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('_motion_time_basis:="${EGO_CMD_SAFETY_MOTION_TIME_BASIS}"', runner)
        self.assertIn('"motion_time_basis": "${EGO_CMD_SAFETY_MOTION_TIME_BASIS}"', runner)
        self.assertIn("def read_live_json(path: Path, attempts: int = 20", runner)
        self.assertIn("data = read_live_json(path)", runner)
        self.assertIn("dynamic = read_live_json(dynamic_path)", runner)
        self.assertIn("cloud = read_live_json(cloud_path)", runner)
        self.assertNotIn('failures.append(f"uav{uid}:sync_stamp_nonmonotonic")', runner)
        self.assertIn('failures.append(f"uav{uid}:cloud_pose_max_stamp_delta={max_pair_delta}")', runner)


if __name__ == "__main__":
    unittest.main()
