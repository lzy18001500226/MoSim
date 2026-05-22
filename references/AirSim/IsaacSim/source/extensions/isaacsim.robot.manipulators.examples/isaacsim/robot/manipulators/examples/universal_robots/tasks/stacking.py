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

import numpy as np
from isaacsim.core.api.tasks import Stacking as BaseStacking
from isaacsim.core.utils.prims import is_prim_path_valid
from isaacsim.core.utils.stage import get_stage_units
from isaacsim.core.utils.string import find_unique_string_name
from isaacsim.robot.manipulators.examples.universal_robots import UR10


class Stacking(BaseStacking):
    """[summary]

    Args:
        name (str, optional): [description]. Defaults to "ur10_stacking".
        target_position (Optional[np.ndarray], optional): [description]. Defaults to None.
        cube_size (Optional[np.ndarray], optional): [description]. Defaults to None.
        offset (Optional[np.ndarray], optional): [description]. Defaults to None.
    """

    def __init__(
        self,
        name: str = "ur10_stacking",
        target_position: Optional[np.ndarray] = None,
        cube_size: Optional[np.ndarray] = None,
        offset: Optional[np.ndarray] = None,
    ) -> None:
        if target_position is None:
            target_position = np.array([0.7, 0.7, 0]) / get_stage_units()
        BaseStacking.__init__(
            self,
            name=name,
            cube_initial_positions=np.array([[0.3, 0.3, 0.3], [0.3, -0.3, 0.3]]) / get_stage_units(),
            cube_initial_orientations=None,
            stack_target_position=target_position,
            cube_size=cube_size,
            offset=offset,
        )
        return

    def set_robot(self) -> UR10:
        """[summary]

        Returns:
            UR10: [description]
        """
        ur10_prim_path = find_unique_string_name(
            initial_name="/World/ur10", is_unique_fn=lambda x: not is_prim_path_valid(x)
        )
        ur10_robot_name = find_unique_string_name(
            initial_name="my_ur10", is_unique_fn=lambda x: not self.scene.object_exists(x)
        )
        self._ur10_robot = UR10(prim_path=ur10_prim_path, name=ur10_robot_name, attach_gripper=True)
        self._ur10_robot.set_joints_default_state(
            positions=np.array([-np.pi / 2, -np.pi / 2, -np.pi / 2, -np.pi / 2, np.pi / 2, 0])
        )
        return self._ur10_robot

    def pre_step(self, time_step_index: int, simulation_time: float) -> None:
        """[summary]

        Args:
            time_step_index (int): [description]
            simulation_time (float): [description]
        """
        BaseStacking.pre_step(self, time_step_index=time_step_index, simulation_time=simulation_time)
        self._ur10_robot.gripper.update()
        return
