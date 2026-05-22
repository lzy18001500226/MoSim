# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List

import numpy as np
from isaacsim.core.api.articulations import ArticulationSubset
from isaacsim.core.utils.numpy.rotations import quats_to_rot_matrices, rot_matrices_to_quats
from isaacsim.core.utils.xforms import get_world_pose

# Size of rolling window over joint positions to detect steady state position convergence.
WINDOW_SIZE = 10

# The STD of the rolling window must be below this threshold for a grasp to be considered stabilized.
STABILITY_TEST_THRESHOLD = 1e-4


class GraspTestSettings:
    def __init__(
        self,
        articulation_path: str,
        articulation_pose_frame: str,
        active_joints: List[str],
        active_joint_open_positions: List[float],
        active_joint_closed_positions: List[float],
        active_joint_close_speeds: List[float],
        inactive_joint_fixed_positions: List[float],
        rigid_body_path: str,
        rigid_body_pose_frame: str,
        external_force_magnitude: float,
        external_torque_magnitude: float,
    ):
        self.articulation_path = articulation_path
        self.articulation_pose_frame = articulation_pose_frame
        self.active_joints = active_joints
        self.active_joint_open_positions = np.array(active_joint_open_positions)
        self.active_joint_closed_positions = np.array(active_joint_closed_positions)
        self.active_joint_close_velocities = np.array(active_joint_close_speeds) * np.sign(
            active_joint_closed_positions - self.active_joint_open_positions
        )
        self.inactive_joint_fixed_positions = np.array(inactive_joint_fixed_positions)
        self.rigid_body_path = rigid_body_path
        self.rigid_body_pose_frame = rigid_body_pose_frame
        self.external_force_magnitude = external_force_magnitude
        self.external_torque_magnitude = external_torque_magnitude


class GraspTestResults:
    def __init__(
        self,
        grasp_test_settings: GraspTestSettings,
        articulation_rel_trans: np.array,
        articulation_rel_quat: np.array,
        stable_positions: np.array,
        suggested_confidence: float,
        success: bool,
    ):
        self.grasp_test_settings = grasp_test_settings
        self.articulation_rel_quat = articulation_rel_quat
        self.articulation_rel_trans = articulation_rel_trans
        self.stable_positions = stable_positions
        self.suggested_confidence = suggested_confidence
        self.success = success


class GraspTester:
    def __init__(self):
        self._test_grasp_generator = None
        self._test_timestep = 0

    def initialize_test_grasp_script(self, articulation, rigid_body, grasp_test_settings):
        self._test_grasp_generator = self._test_grasp_script(articulation, rigid_body, grasp_test_settings)
        self._test_timestep = 0

    def close_gripper_trajectory(self, t, open_positions, close_positions, close_velocities):
        # Return position command to close the gripper as a function of t.  The trajectory moves
        # from open_positions to close_positions at a constant velocity of close_velocities.
        max_close_distance = np.abs(open_positions - close_positions)
        desired_close_distance = np.abs(t * close_velocities)
        signed_close_distance_clipped = np.clip(desired_close_distance, a_min=None, a_max=max_close_distance) * np.sign(
            close_velocities
        )

        return open_positions + signed_close_distance_clipped

    def update_grasp_test(self, step: float):
        try:
            result = next(self._test_grasp_generator)
            self._test_timestep += step
            return result
        except StopIteration as e:
            # StopIteration occurs when the script returns, and e.value is the return value
            return e.value

    def compute_relative_pose(self, rigid_body_frame: str, articulation_frame: str):
        # Compute the pose of the articulation frame relative to the rigid body frame
        rb_trans, rb_quat = get_world_pose(rigid_body_frame)
        gripper_trans, gripper_quat = get_world_pose(articulation_frame)

        gripper_rot_mat, rb_rot_mat = quats_to_rot_matrices(np.vstack([gripper_quat, rb_quat]))

        rel_trans = rb_rot_mat.T @ (gripper_trans - rb_trans)
        rel_rot = rb_rot_mat.T @ gripper_rot_mat

        return rel_trans, rot_matrices_to_quats(rel_rot)

    def _apply_external_force(self, rigid_body, force_magnitude, active_subset, closed_positions, apply_torque=False):
        s = "torque" if apply_torque else "force"
        succ = True
        for idx in range(3):
            for sign in [1, -1]:
                force = np.zeros((1, 3))
                torque = np.zeros((1, 3))

                if apply_torque:
                    torque[0, idx] = force_magnitude * sign
                else:
                    force[0, idx] = force_magnitude * sign

                force_duration = self._test_timestep + 0.33

                position_window = np.tile(active_subset.get_joint_positions()[np.newaxis, :], (WINDOW_SIZE, 1))

                while (
                    self._test_timestep < force_duration
                    or np.linalg.norm(position_window.std(axis=0)) > STABILITY_TEST_THRESHOLD
                ):
                    f = str(torque[0, :]) + " N*m" if apply_torque else str(force[0, :]) + " N"

                    rigid_body.apply_forces_and_torques_at_pos(force, torque)
                    yield (f"Applying {s} of {f} about Rigid Body reference frame.")

                    position_window[:-1] = position_window[1:]
                    position_window[-1] = active_subset.get_joint_positions()

                if np.linalg.norm(closed_positions - active_subset.get_joint_positions()) < STABILITY_TEST_THRESHOLD:
                    yield (
                        "The initial grasp succeeded, but it was not able to withstand "
                        + f"rigid body {s} of  {f} applied for 1/3 second about the reference frame.  "
                        + "Exporting the grasp will export the state of the initial successdul grasp."
                    )
                    succ = False
                    break

            if not succ:
                break

        rigid_body.apply_forces_and_torques_at_pos(np.zeros((1, 3)), np.zeros((1, 3)))
        rigid_body.set_velocities(np.zeros((1, 6)))
        yield ()

        rigid_body.set_velocities(np.zeros((1, 6)))

        yield ()
        return succ

    def _test_grasp_script(self, articulation, rigid_body, test_settings):
        x = test_settings

        active_subset = ArticulationSubset(articulation, x.active_joints)
        active_subset.set_joint_positions(x.active_joint_open_positions)

        close_command = lambda t: self.close_gripper_trajectory(
            t, x.active_joint_open_positions, x.active_joint_closed_positions, x.active_joint_close_velocities
        )

        # Compute time expected for the gripper to close based on the specified per-joint velocities.
        safe_div_mask = x.active_joint_close_velocities != 0.0
        close_durations = x.active_joint_closed_positions - x.active_joint_open_positions
        close_durations[safe_div_mask] /= x.active_joint_close_velocities[safe_div_mask]
        close_durations[x.active_joint_close_velocities == 0.0] = 0.0
        close_duration = np.max(close_durations)

        # A window of the last WINDOW_SIZE joint states.  Closing the gripper should not stop until
        # the STD of position_window is near-zero.
        position_window = np.tile(active_subset.get_joint_positions()[np.newaxis, :], (WINDOW_SIZE, 1))

        status_msg = "Closing Gripper..."

        while (
            self._test_timestep < close_duration
            or np.linalg.norm(position_window.std(axis=0)) > STABILITY_TEST_THRESHOLD
        ):
            active_subset.apply_action(close_command(self._test_timestep), x.active_joint_close_velocities)
            yield (status_msg)

            position_window[:-1] = position_window[1:]
            position_window[-1] = active_subset.get_joint_positions()

        stable_positions = active_subset.get_joint_positions()

        rel_trans, rel_quat = self.compute_relative_pose(x.rigid_body_pose_frame, x.articulation_pose_frame)

        # Gripper fully closing implies that the object fell out.
        if np.linalg.norm(x.active_joint_closed_positions - stable_positions) < STABILITY_TEST_THRESHOLD:
            status_msg = (
                "Because the gripper reached the fully closed position, this test is "
                + "considered a failure.  It is assumed that the user parameter for close "
                + "position is sufficiently smaller than the rigid body dimensions at the "
                + "grasp point that a meaningful force will be applied when attempting to "
                + "reach the closed position.  This also implies that when the gripper "
                + "reaches the closed position, the rigid body must have escaped the grasp."
            )
            yield (status_msg)

            return GraspTestResults(x, rel_trans, rel_quat, stable_positions, 0.0, False)

        yield (status_msg)

        # Command a huge velocity in order to get up to max effort.  It has been verified that this increases
        # the force/torque threshold of losing a grasp, but it has not been verified that the user max effort
        # parameter is always reached.
        if x.external_force_magnitude > 0 or x.external_torque_magnitude > 0:
            active_subset.apply_action(
                close_command(self._test_timestep), np.sign(x.active_joint_close_velocities) * 1e15
            )

        if x.external_force_magnitude > 0:
            succ = yield from self._apply_external_force(
                rigid_body, x.external_force_magnitude, active_subset, x.active_joint_closed_positions
            )
            if not succ:
                return GraspTestResults(x, rel_trans, rel_quat, stable_positions, 0.5, False)

        if x.external_torque_magnitude > 0:
            succ = yield from self._apply_external_force(
                rigid_body,
                x.external_torque_magnitude,
                active_subset,
                x.active_joint_closed_positions,
                apply_torque=True,
            )

            if not succ:
                return GraspTestResults(x, rel_trans, rel_quat, stable_positions, 0.5, False)

        yield ("Passed Grasp Testing")

        return GraspTestResults(x, rel_trans, rel_quat, stable_positions, 1.0, True)
