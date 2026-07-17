#!/usr/bin/env python3
"""Three-UAV takeoff/formation/land gate driven by official MWORKS-generated C."""

from __future__ import annotations

import ctypes
import json
import math
import os
from pathlib import Path
import time

import rospy
from quadrotor_msgs.msg import PositionCommand, TakeoffLand

from p8_formation_runtime_math import (
    common_to_odom_xy,
    next_takeoff_uid,
    odom_to_common_xy,
    point_at_distance,
    rate_limit_vector,
    should_retry_takeoff,
)
from px4ctrl_swarm_basic_mission_node import SwarmBasicMission, parse_args


MODES = {
    1: "leader_follower", 2: "virtual_structure", 3: "consensus",
    4: "containment", 5: "formation_tracking", 6: "formation_reconfiguration",
    7: "fault_tolerant_formation", 8: "formation_cbf",
    9: "distributed_mpc_formation",
}


class GeneratedFormationMission(SwarmBasicMission):
    def __init__(self, args):
        args.takeoff_timeout_s = float(os.environ.get("P8_TAKEOFF_TIMEOUT_S", "180"))
        args.land_timeout_s = float(os.environ.get("P8_LAND_TIMEOUT_S", "240"))
        args.landed_z_max = float(os.environ.get("P8_LANDED_Z_MAX", "0.30"))
        args.steady_hover_tail_s = float(os.environ.get("P8_STEADY_HOVER_TAIL_S", "5.0"))
        args.require_disarmed = True
        super().__init__(args)
        self.mode_id = int(os.environ.get("P8_FORMATION_MODE_ID", "1"))
        if self.mode_id not in MODES:
            raise ValueError(f"unsupported P8_FORMATION_MODE_ID={self.mode_id}")
        default_lib = Path(args.result_dir).parents[1] / "control_platform/p8_formation_generated_runtime_20260717/libmosim_p8_formation_generated.so"
        self.library_path = Path(os.environ.get("P8_FORMATION_GENERATED_LIB", str(default_lib))).resolve()
        self.library = ctypes.CDLL(str(self.library_path))
        self.library.mosim_p8_generated_init.argtypes = []
        self.library.mosim_p8_generated_step.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
        self.library.mosim_p8_generated_step.restype = ctypes.c_int
        self.library.mosim_p8_generated_init()
        self.generated_reset = True
        self.generated_rows = []
        self.tracking_rows = {uid: [] for uid in self.uavs}
        self.takeoff_request_count = 0
        self.takeoff_requests_by_uav = {uid: 0 for uid in self.uavs}
        self.land_request_count = 0
        self.land_requests_by_uav = {uid: 0 for uid in self.uavs}
        self.last_takeoff_request_s = float("-inf")
        self.takeoff_retry_interval_s = float(os.environ.get("P8_TAKEOFF_RETRY_INTERVAL_S", "1.0"))
        self.takeoff_maximum_requests = int(os.environ.get("P8_TAKEOFF_MAXIMUM_REQUESTS", "120"))
        self.generated_velocity_feedforward_scale = float(
            os.environ.get("P8_GENERATED_VELOCITY_FEEDFORWARD_SCALE", "0.0")
        )
        self.generated_position_rate_limit_mps = float(
            os.environ.get("P8_GENERATED_POSITION_RATE_LIMIT_MPS", "0.35")
        )
        self.applied_common_targets = {}
        self.cbf_injection_distance_m = float(os.environ.get("P8_CBF_INJECTION_DISTANCE_M", "0.85"))
        self.cbf_injection_timeout_s = float(os.environ.get("P8_CBF_INJECTION_TIMEOUT_S", "5.0"))
        self.cbf_injection_steps = 0
        self.cbf_event_observed = False
        self.land_retry_timer = rospy.Timer(rospy.Duration(1.0), self.retry_land_for_armed_uavs)

    def all_ready(self):
        return super().all_ready() and all(
            uav.takeoff_land_pub.get_num_connections() > 0
            and uav.cmd_pub.get_num_connections() > 0
            for uav in self.uavs.values()
        )

    def publish_takeoff_land(self, cmd, repeats):
        msg = TakeoffLand()
        msg.takeoff_land_cmd = cmd
        if cmd == TakeoffLand.LAND:
            for _ in range(repeats):
                for uid, uav in self.uavs.items():
                    if uav.state and uav.state.armed:
                        uav.takeoff_land_pub.publish(msg)
                        self.land_request_count += 1
                        self.land_requests_by_uav[uid] += 1
                rospy.sleep(0.1)
            return
        if cmd != TakeoffLand.TAKEOFF:
            return super().publish_takeoff_land(cmd, repeats)
        for _ in range(repeats):
            uid = next_takeoff_uid({
                candidate_uid: bool(uav.state and uav.state.armed)
                for candidate_uid, uav in self.uavs.items()
            })
            if uid is None:
                break
            self.uavs[uid].takeoff_land_pub.publish(msg)
            self.takeoff_request_count += 1
            self.takeoff_requests_by_uav[uid] += 1
            self.last_takeoff_request_s = time.monotonic()
            rospy.sleep(0.1)

    def retry_land_for_armed_uavs(self, _event):
        if self.phase != "land":
            return
        msg = TakeoffLand()
        msg.takeoff_land_cmd = TakeoffLand.LAND
        for uid, uav in self.uavs.items():
            if uav.state and uav.state.armed:
                uav.takeoff_land_pub.publish(msg)
                self.land_request_count += 1
                self.land_requests_by_uav[uid] += 1

    @staticmethod
    def common_xy_for(uav):
        if not uav.odom or uav.home_odom_xy is None:
            return uav.start_xy
        return odom_to_common_xy(
            uav.start_xy,
            uav.home_odom_xy,
            (float(uav.odom["x"]), float(uav.odom["y"])),
        )

    def generated_input(self):
        values = [float(self.mode_id), 0.02]
        leader_start = self.uavs[1].start_xy
        values += [leader_start[0], leader_start[1], self.takeoff_target_z(self.uavs[1]), 0.0, 0.0, 0.0, self.args.yaw]
        for uid in range(1, 4):
            uav = self.uavs[uid]
            odom = uav.odom or {"x": 0.0, "y": 0.0, "z": self.args.takeoff_height}
            common_xy = self.common_xy_for(uav)
            values += [common_xy[0], common_xy[1], odom["z"]]
        for uid in range(1, 4):
            odom = self.uavs[uid].odom or {"vx": 0.0, "vy": 0.0, "vz": 0.0}
            values += [odom["vx"], odom["vy"], odom["vz"]]
        values += [1.0, 0.0 if self.mode_id == 7 else 1.0, 1.0, 1.0, 1.0, 1.0 if self.generated_reset else 0.0]
        return values

    def publish_hover_cmds(self):
        if self.phase == "takeoff":
            now_s = time.monotonic()
            if should_retry_takeoff(
                now_s,
                self.last_takeoff_request_s,
                self.takeoff_request_count,
                self.takeoff_maximum_requests,
                self.takeoff_retry_interval_s,
                all(uav.state and uav.state.armed for uav in self.uavs.values()),
            ):
                self.publish_takeoff_land(TakeoffLand.TAKEOFF, 1)
            return
        if self.phase != "hover":
            return super().publish_hover_cmds()
        inputs = (ctypes.c_double * 33)(*self.generated_input())
        outputs = (ctypes.c_double * 24)()
        if self.library.mosim_p8_generated_step(inputs, outputs) != 0:
            raise RuntimeError("official generated formation step failed")
        self.generated_reset = False
        row = {"t": self.now(), "mode_id": self.mode_id, "mode": MODES[self.mode_id], "minimum_pair_distance_input_m": outputs[18], "formation_rmse_input_m": outputs[19], "active_agents": outputs[20], "failed_mask": outputs[21], "safety_corrections": outputs[22], "status_code": outputs[23]}
        self.generated_rows.append(row)
        if int(row["safety_corrections"]) > 0:
            self.cbf_event_observed = True
        hover_elapsed_s = row["t"] - self.generated_rows[0]["t"]
        for uid, uav in self.uavs.items():
            base = 3 * (uid - 1)
            velocity_base = 9 + base
            raw_common_target = (outputs[base], outputs[base + 1], outputs[base + 2])
            if (
                self.mode_id == 8
                and uid == 2
                and not self.cbf_event_observed
                and hover_elapsed_s < self.cbf_injection_timeout_s
            ):
                anchor_xy = self.common_xy_for(self.uavs[1])
                compressed_xy = point_at_distance(
                    anchor_xy,
                    self.uavs[2].start_xy,
                    self.cbf_injection_distance_m,
                )
                raw_common_target = (compressed_xy[0], compressed_xy[1], raw_common_target[2])
                self.cbf_injection_steps += 1
            previous_target = self.applied_common_targets.get(uid)
            if previous_target is None:
                actual_xy = self.common_xy_for(uav)
                previous_target = (actual_xy[0], actual_xy[1], float(uav.odom["z"]))
            common_target = rate_limit_vector(
                previous_target,
                raw_common_target,
                self.generated_position_rate_limit_mps * 0.02,
            )
            self.applied_common_targets[uid] = common_target
            home_odom_xy = uav.home_odom_xy or uav.start_xy
            local_target_xy = common_to_odom_xy(uav.start_xy, home_odom_xy, common_target[:2])
            msg = PositionCommand(); msg.header.stamp = rospy.Time.now(); msg.header.frame_id = self.args.path_frame
            msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
            msg.position.x = local_target_xy[0]
            msg.position.y = local_target_xy[1]
            msg.position.z = common_target[2]
            msg.velocity.x = self.generated_velocity_feedforward_scale * outputs[velocity_base]
            msg.velocity.y = self.generated_velocity_feedforward_scale * outputs[velocity_base + 1]
            msg.velocity.z = self.generated_velocity_feedforward_scale * outputs[velocity_base + 2]
            msg.yaw = self.args.yaw; uav.cmd_pub.publish(msg)
            if uav.odom:
                actual_xy = self.common_xy_for(uav)
                actual = (actual_xy[0], actual_xy[1], uav.odom["z"])
                self.tracking_rows[uid].append({"t": row["t"], "xy_error_m": math.hypot(actual[0] - common_target[0], actual[1] - common_target[1]), "z_error_m": abs(actual[2] - common_target[2]), "raw_formation_xy_error_m": math.hypot(actual[0] - raw_common_target[0], actual[1] - raw_common_target[1]), "raw_formation_z_error_m": abs(actual[2] - raw_common_target[2])})

    def hover_metrics(self, uav):
        rows = self.tracking_rows[uav.uid]
        if rows and self.args.steady_hover_tail_s > 0:
            t0 = rows[-1]["t"] - self.args.steady_hover_tail_s
            rows = [row for row in rows if row["t"] >= t0]
        xy = [row["xy_error_m"] for row in rows]; z = [row["z_error_m"] for row in rows]
        return {"sample_count": len(rows), "xy_rmse_m": self.rmse(xy), "xy_max_m": max(xy) if xy else None, "z_abs_rmse_m": self.rmse(z), "z_abs_max_m": max(z) if z else None}

    def acceptance_blockers(self):
        blockers = super().acceptance_blockers()
        if not self.generated_rows:
            blockers.append("generated_formation_rows_missing")
        if self.mode_id == 7 and not any(int(row["failed_mask"]) == 2 and int(row["active_agents"]) == 2 for row in self.generated_rows):
            blockers.append("fault_tolerant_event_not_observed")
        if self.mode_id == 8 and not any(int(row["safety_corrections"]) > 0 for row in self.generated_rows):
            blockers.append("formation_cbf_event_not_observed")
        return blockers

    def write_outputs(self, status, blockers):
        super().write_outputs(status, blockers)
        self.write_csv(self.result_dir / "p8_generated_formation_diagnostics.csv", self.generated_rows)
        for uid, rows in self.tracking_rows.items():
            self.write_csv(self.result_dir / f"uav{uid}_p8_generated_tracking.csv", rows)
        path = self.result_dir / "PX4CTRL_SWARM_BASIC_METRICS.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update({"schema": "mosim.control_platform.p8_generated_formation_gazebo.v1", "formation_mode_id": self.mode_id, "formation_mode": MODES[self.mode_id], "official_generated_library": str(self.library_path), "generated_step_count": len(self.generated_rows), "generated_velocity_feedforward_scale": self.generated_velocity_feedforward_scale, "generated_position_rate_limit_mps": self.generated_position_rate_limit_mps, "velocity_interface_contract": "Generated positions are authoritative references. Core velocity outputs are bounded correction commands, not trajectory derivatives, so px4ctrl feedforward is disabled by default to avoid duplicating its position feedback.", "position_interface_contract": "Raw generated formation references are Euclidean-rate-limited before px4ctrl; tracking metrics use the applied command while raw formation errors remain in each tracking CSV.", "cbf_runtime_injection": {"target_pair_distance_m": self.cbf_injection_distance_m, "timeout_s": self.cbf_injection_timeout_s, "injection_steps": self.cbf_injection_steps, "generated_c_event_observed": self.cbf_event_observed}, "takeoff_request_count": self.takeoff_request_count, "takeoff_requests_by_uav": self.takeoff_requests_by_uav, "takeoff_strategy": "sequential_first_unarmed", "land_request_count": self.land_request_count, "land_requests_by_uav": self.land_requests_by_uav, "land_strategy": "bounded_retry_while_armed", "frame_contract": "common_xy = start_xy + odom_xy - home_odom_xy; controller_xy = home_odom_xy + common_xy - start_xy", "claim_boundary": "One P8 mode drives three real Sunray/PX4/MAVROS/px4ctrl vehicles in Gazebo through official MWORKS-generated C; Gazebo truth is evaluation-only."})
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main():
    rospy.init_node("mosim_p8_formation_generated_mission")
    raise SystemExit(GeneratedFormationMission(parse_args()).run())


if __name__ == "__main__":
    main()
