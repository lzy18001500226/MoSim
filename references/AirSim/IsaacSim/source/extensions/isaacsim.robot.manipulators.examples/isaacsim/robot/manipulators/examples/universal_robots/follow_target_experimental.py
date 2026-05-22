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

import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
from isaacsim.core.experimental.materials import PreviewSurfaceMaterial
from isaacsim.core.experimental.objects import Cube
from isaacsim.core.experimental.prims import GeomPrim
from isaacsim.robot.manipulators.examples.universal_robots.ur10_experimental import UR10Experimental
from isaacsim.storage.native import get_assets_root_path


class UR10FollowTarget:
    """Standalone UR10 follow target task.

    This class provides a complete follow target implementation for UR10 robot
    without inheriting from any base classes. It manages the robot, target cube, and
    provides the necessary interface for the simulation.

    Args:
        name (str, optional): Task name. Defaults to "ur10_follow_target".
        target_position (Optional[np.ndarray], optional): Target position [x, y, z]. Defaults to None.
    """

    def __init__(self) -> None:
        """Initialize the UR follow target task."""

        # Initialize robot and target references
        self.robot = None
        self.target_cube = None

    def setup_scene(
        self,
        target_position: Optional[np.ndarray] = None,
    ) -> None:
        """Set up the scene with robot, target cube, and environment.

        Args:
            target_position: Initial target position. If None, uses default.
        """

        # Set default target position if none provided
        if target_position is None:
            self.target_position = np.array([0.5, 0.0, 0.3])
        else:
            self.target_position = np.array(target_position)

        # Create a new USD stage with default sunlight lighting
        stage_utils.create_new_stage(template="sunlight")

        # Add ground plane environment for physics simulation
        ground_plane = stage_utils.add_reference_to_stage(
            usd_path=get_assets_root_path() + "/Isaac/Environments/Grid/default_environment.usd",
            path="/World/ground",
        )

        # Create the UR10 robot controller without gripper for this demo
        self.robot = UR10Experimental(robot_path="/World/ur10_robot", create_robot=True, attach_gripper=False)

        # Create red visual material for the target cube
        visual_material = PreviewSurfaceMaterial("/Visual_materials/red")
        visual_material.set_input_values("diffuseColor", [1.0, 0.0, 0.0])

        # Create target cube that the robot will follow
        cube_shape = Cube(
            paths="/World/TargetCube",
            positions=self.target_position,
            orientations=np.array([1, 0, 0, 0]),
            sizes=[1.0],
            scales=np.array([0.05, 0.05, 0.05]),  # 5cm cube
            reset_xform_op_properties=True,
        )

        # Apply visual material and make it a rigid body for physics
        cube_shape.apply_visual_materials(visual_material)
        self.target_cube = GeomPrim(paths=cube_shape.paths)

    def get_target_position(self) -> np.ndarray:
        """Get the current target cube position.

        Returns:
            Current target position [x, y, z].
        """
        if self.target_cube is not None:
            position, _ = self.target_cube.get_world_poses()
            return position.numpy().flatten()
        return self.target_position

    def get_robot_end_effector_position(self) -> np.ndarray:
        """Get the current robot end effector position.

        Returns:
            Current end effector position [x, y, z].
        """
        if self.robot is not None:
            position, _ = self.robot.end_effector_link.get_world_poses()
            return position.numpy().flatten()
        return np.zeros(3)

    def target_reached(self, threshold: float = 0.05) -> bool:
        """Check if the end effector has reached the target.

        Args:
            threshold: Distance threshold to consider target reached.

        Returns:
            True if target is reached, False otherwise.
        """
        target_pos = self.get_target_position()
        ee_pos = self.get_robot_end_effector_position()
        distance = np.linalg.norm(target_pos - ee_pos)
        return distance < threshold

    def move_to_target(self, ik_method: str = "damped-least-squares") -> None:
        """Move the robot end effector towards the target position.

        Args:
            ik_method: The inverse kinematics method to use.
        """
        if self.robot is not None and self.target_cube is not None:
            target_pos = self.get_target_position()
            # Use the enhanced UR10Controller's set_end_effector_pose method
            self.robot.set_end_effector_pose(
                position=target_pos, orientation=np.array([[0.0, 1.0, 0.0, 0.0]]), ik_method=ik_method
            )

    def reset_robot(self) -> None:
        """Reset the robot to its default pose."""
        if self.robot is not None:
            self.robot.reset_to_default_pose()
