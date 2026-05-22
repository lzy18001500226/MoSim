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

from typing import Optional

import numpy as np
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.prims import get_prim_at_path
from isaacsim.core.utils.transformations import get_world_pose_from_relative
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.robot.policy.examples.controllers import PolicyController
from isaacsim.storage.native import get_assets_root_path


class FrankaOpenDrawerPolicy(PolicyController):
    """The Franka Open Drawer Policy. In this policy, the robot will open the top drawer of the cabinet and hold it open"""

    def __init__(
        self,
        prim_path: str,
        cabinet: SingleArticulation,
        root_path: Optional[str] = None,
        name: str = "franka",
        usd_path: Optional[str] = None,
        position: Optional[np.ndarray] = None,
        orientation: Optional[np.ndarray] = None,
    ) -> None:
        """
        Initialize franka robot and import flat terrain policy.

        Args:
            prim_path (str) -- prim path of the robot on the stage
            root_path (Optional[str]): The path to the articulation root of the robot
            name (str) -- name of the quadruped
            usd_path (str) -- robot usd filepath in the directory
            position (np.ndarray) -- position of the robot
            orientation (np.ndarray) -- orientation of the robot

        """
        assets_root_path = get_assets_root_path()

        policy_path = assets_root_path + "/Isaac/Samples/Policies/Franka_Policies/Open_Drawer_Policy/"
        if usd_path == None:
            usd_path = assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"

        super().__init__(name, prim_path, root_path, usd_path, position, orientation)

        self.load_policy(
            policy_path + "policy.pt",
            policy_path + "env.yaml",
        )

        self._action_scale = 1.0
        self._previous_action = np.zeros(9)
        self._policy_counter = 0

        self.cabinet = cabinet

        self.franka_hand_prim = get_prim_at_path(self.robot.prim_path + "/panda_hand")
        self.drawer_handle_top_prim = get_prim_at_path(self.cabinet.prim_path + "/drawer_handle_top")

    def _compute_observation(self):
        """
        Compute the observation vector for the policy.

        Returns:
        np.ndarray -- The observation vector.

        """
        # relative transform from the drawer handle to the drawer handle link
        """
        From env.yaml
        - prim_path: /World/envs/env_.*/Cabinet/drawer_handle_top
            name: drawer_handle_top
            offset:
                pos: !!python/tuple
                - 0.305
                - 0.0
                - 0.01
        """
        drawer_world_pos, _ = get_world_pose_from_relative(
            self.drawer_handle_top_prim, np.array([0.305, 0, 0.01]), np.array([1, 0, 0, 0])
        )

        # relative transform from the tool cneter to the hands
        """
        From env.yaml
        - prim_path: /World/envs/env_.*/Robot/panda_hand
            name: ee_tcp
            offset:
                pos: !!python/tuple
                - 0.0
                - 0.0
                - 0.1034
        """
        robot_world_pos, _ = get_world_pose_from_relative(
            self.franka_hand_prim, np.array([0, 0, 0.1034]), np.array([1, 0, 0, 0])
        )

        obs = np.zeros(31)
        # Base lin pos
        obs[:9] = self.robot.get_joint_positions() - self.default_pos

        # Base ang vel
        obs[9:18] = self.robot.get_joint_velocities() - self.default_vel

        # Joint states
        obs[18:19] = self.cabinet.get_joint_positions()[self.drawer_link_idx]
        obs[19:20] = self.cabinet.get_joint_velocities()[self.drawer_link_idx]

        # relative distance between drawer and robot
        obs[20:23] = drawer_world_pos - robot_world_pos

        # Previous Action
        obs[23:31] = self._previous_action[0:8]

        return obs

    def forward(self, dt):
        """
        Compute the desired articulation action and apply them to the robot articulation.

        Argument:
        dt (float) -- Timestep update in the world.

        """
        if self._policy_counter % self._decimation == 0:
            obs = self._compute_observation()
            self.action = self._compute_action(obs)
            self._previous_action = self.action.copy()

        # articulation space
        # copy last item for two fingers in order to increase action size from 8 to 9
        # finger positions are absolute positions, not relative to the default position
        self.action[0:8] = self.action[0:8] + self.default_pos[0:8]
        action_input = np.append(self.action, self.action[-1])
        action = ArticulationAction(joint_positions=(action_input * self._action_scale))
        # here action is size 9
        self.robot.apply_action(action)

        self._policy_counter += 1

    def initialize(self, physics_sim_view=None) -> None:
        """
        Initialize the articulation interface, set up drive mode
        """
        super().initialize(physics_sim_view=physics_sim_view, control_mode="force", set_articulation_props=True)

        self.cabinet.initialize(physics_sim_view=physics_sim_view)

        self.drawer_link_idx = self.cabinet.get_dof_index("drawer_top_joint")

        self.robot.set_solver_position_iteration_count(32)
        self.robot.set_solver_velocity_iteration_count(4)
        self.robot.set_stabilization_threshold(0)
        self.robot.set_sleep_threshold(0)
