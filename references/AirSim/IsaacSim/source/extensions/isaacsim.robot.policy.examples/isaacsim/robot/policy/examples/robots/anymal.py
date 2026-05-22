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

import io
from typing import Optional

import numpy as np
import omni
from isaacsim.core.utils.rotations import quat_to_rot_matrix
from isaacsim.robot.policy.examples.controllers import PolicyController
from isaacsim.robot.policy.examples.utils import LstmSeaNetwork
from isaacsim.storage.native import get_assets_root_path


class AnymalFlatTerrainPolicy(PolicyController):
    """The ANYmal Robot running a Flat Terrain Locomotion Policy"""

    def __init__(
        self,
        prim_path: str,
        root_path: Optional[str] = None,
        name: str = "anymal",
        usd_path: Optional[str] = None,
        position: Optional[np.ndarray] = None,
        orientation: Optional[np.ndarray] = None,
    ) -> None:
        """
        Initialize anymal robot, import policy and actuator network.

        Args:
            prim_path (str) -- prim path of the robot on the stage
            root_path (Optional[str]): The path to the articulation root of the robot
            name (str) -- name of the quadruped
            usd_path (str) -- robot usd filepath in the directory
            position (np.ndarray) -- position of the robot
            orientation (np.ndarray) -- orientation of the robot

        """
        assets_root_path = get_assets_root_path()
        if usd_path == None:
            usd_path = assets_root_path + "/Isaac/Robots/ANYbotics/anymal_c/anymal_c.usd"

        super().__init__(name, prim_path, root_path, usd_path, position, orientation)
        self.load_policy(
            assets_root_path + "/Isaac/Samples/Policies/Anymal_Policies/anymal_policy.pt",
            assets_root_path + "/Isaac/Samples/Policies/Anymal_Policies/anymal_env.yaml",
        )
        self._action_scale = 0.5
        self._previous_action = np.zeros(12)
        self._policy_counter = 0

    def _compute_observation(self, command):
        """
        Computes the the observation vector for the policy

        Argument:
        command (np.ndarray) -- the robot command (v_x, v_y, w_z)

        Returns:
        np.ndarray -- The observation vector.

        """
        lin_vel_I = self.robot.get_linear_velocity()
        ang_vel_I = self.robot.get_angular_velocity()
        pos_IB, q_IB = self.robot.get_world_pose()

        R_IB = quat_to_rot_matrix(q_IB)
        R_BI = R_IB.transpose()
        lin_vel_b = np.matmul(R_BI, lin_vel_I)
        ang_vel_b = np.matmul(R_BI, ang_vel_I)
        gravity_b = np.matmul(R_BI, np.array([0.0, 0.0, -1.0]))

        obs = np.zeros(48)
        # Base lin vel
        obs[:3] = lin_vel_b
        # Base ang vel
        obs[3:6] = ang_vel_b
        # Gravity
        obs[6:9] = gravity_b
        # Command
        obs[9:12] = command
        # Joint states
        current_joint_pos = self.robot.get_joint_positions()
        current_joint_vel = self.robot.get_joint_velocities()
        obs[12:24] = current_joint_pos - self.default_pos
        obs[24:36] = current_joint_vel

        # Previous Action
        obs[36:48] = self._previous_action

        return obs

    def forward(self, dt, command):
        """
        Compute the desired torques and apply them to the articulation

        Argument:
        dt (float) -- Timestep update in the world.
        command (np.ndarray) -- the robot command (v_x, v_y, w_z)

        """
        if self._policy_counter % self._decimation == 0:
            obs = self._compute_observation(command)
            self.action = self._compute_action(obs)
            self._previous_action = self.action.copy()

        # The learning controller uses the order of
        # FL_hip_joint FL_thigh_joint FL_calf_joint
        # FR_hip_joint FR_thigh_joint FR_calf_joint
        # RL_hip_joint RL_thigh_joint RL_calf_joint
        # RR_hip_joint RR_thigh_joint RR_calf_joint
        current_joint_pos = self.robot.get_joint_positions()
        current_joint_vel = self.robot.get_joint_velocities()

        joint_torques, _ = self._actuator_network.compute_torques(
            current_joint_pos, current_joint_vel, self._action_scale * self.action
        )
        self.robot.set_joint_efforts(joint_torques)
        self._policy_counter += 1

    def initialize(self, physics_sim_view=None) -> None:
        """
        Initialize the articulation interface, set up drive mode
        """
        super().initialize(physics_sim_view=physics_sim_view, control_mode="effort")

        # Actuator network
        assets_root_path = get_assets_root_path()
        file_content = omni.client.read_file(
            assets_root_path + "/Isaac/Samples/Policies/Anymal_Policies/sea_net_jit2.pt"
        )[2]
        file = io.BytesIO(memoryview(file_content).tobytes())
        self._actuator_network = LstmSeaNetwork()
        self._actuator_network.setup(file, self.default_pos)
        self._actuator_network.reset()
