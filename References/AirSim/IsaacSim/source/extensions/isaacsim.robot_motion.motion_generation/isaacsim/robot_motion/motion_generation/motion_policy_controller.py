# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import isaacsim.core.api.objects
import numpy as np
from isaacsim.core.api.controllers.base_controller import BaseController
from isaacsim.core.utils.rotations import euler_angles_to_quat
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.robot_motion.motion_generation.articulation_motion_policy import ArticulationMotionPolicy
from isaacsim.robot_motion.motion_generation.motion_policy_interface import MotionPolicy


class MotionPolicyController(BaseController):
    """A Controller that steps using an arbitrary MotionPolicy

    Args:
        name (str): name of this controller
        articulation_motion_policy (ArticulationMotionPolicy): a wrapper around a MotionPolicy for computing ArticulationActions that can be directly applied to the robot
    """

    def __init__(self, name: str, articulation_motion_policy: ArticulationMotionPolicy) -> None:
        BaseController.__init__(self, name)

        self._articulation_motion_policy = articulation_motion_policy
        self._motion_policy = self._articulation_motion_policy.get_motion_policy()
        return

    def forward(
        self, target_end_effector_position: np.ndarray, target_end_effector_orientation: Optional[np.ndarray] = None
    ) -> ArticulationAction:
        """Compute an ArticulationAction representing the desired robot state for the next simulation frame

        Args:
            target_translation (nd.array): Translation vector (3x1) for robot end effector.
                Target translation should be specified in the same units as the USD stage, relative to the stage origin.
            target_orientation (Optional[np.ndarray], optional): Quaternion of desired rotation for robot end effector relative to USD stage global frame.
                Target orientation defaults to None, which means that the robot may reach the target with any orientation.

        Returns:
            ArticulationAction: A wrapper object containing the desired next state for the robot
        """

        self._motion_policy.set_end_effector_target(target_end_effector_position, target_end_effector_orientation)

        self._motion_policy.update_world()

        action = self._articulation_motion_policy.get_next_articulation_action()

        return action

    def add_obstacle(self, obstacle: isaacsim.core.api.objects, static: bool = False) -> None:
        """Add an object from isaacsim.core.api.objects as an obstacle to the motion_policy

        Args:
            obstacle (isaacsim.core.api.objects): Dynamic, Visual, or Fixed object from isaacsim.core.api.objects
            static (bool): If True, the obstacle may be assumed by the MotionPolicy to remain stationary over time
        """
        self._motion_policy.add_obstacle(obstacle, static=static)
        return

    def remove_obstacle(self, obstacle: isaacsim.core.api.objects) -> None:
        """Remove and added obstacle from the motion_policy

        Args:
            obstacle (isaacsim.core.api.objects): Object from isaacsim.core.api.objects that has been added to the motion_policy
        """
        self._motion_policy.remove_obstacle(obstacle)
        return

    def reset(self) -> None:
        """ """
        self._motion_policy.reset()
        return

    def get_articulation_motion_policy(self) -> ArticulationMotionPolicy:
        """Get ArticulationMotionPolicy that was passed to this class on initialization

        Returns:
            ArticulationMotionPolicy: a wrapper around a MotionPolicy for computing ArticulationActions that can be directly applied to the robot
        """
        return self._articulation_motion_policy

    def get_motion_policy(self) -> MotionPolicy:
        """Get MotionPolicy object that is being used to generate robot motions

        Returns:
            MotionPolicy: An instance of a MotionPolicy that is being used to compute robot motions
        """
        return self._motion_policy
