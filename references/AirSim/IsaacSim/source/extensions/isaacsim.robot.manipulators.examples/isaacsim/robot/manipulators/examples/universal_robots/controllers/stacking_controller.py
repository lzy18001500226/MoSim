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
from typing import List, Optional

import isaacsim.robot.manipulators.controllers as manipulators_controllers
import numpy as np
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
from isaacsim.robot.manipulators.examples.universal_robots.controllers.pick_place_controller import PickPlaceController
from isaacsim.robot.manipulators.grippers import SurfaceGripper


class StackingController(manipulators_controllers.StackingController):
    """[summary]

    Args:
        name (str): [description]
        gripper (SurfaceGripper): [description]
        robot_articulation(SingleArticulation): [description]
        picking_order_cube_names (List[str]): [description]
        robot_observation_name (str): [description]
    """

    def __init__(
        self,
        name: str,
        gripper: SurfaceGripper,
        robot_articulation: SingleArticulation,
        picking_order_cube_names: List[str],
        robot_observation_name: str,
    ) -> None:
        manipulators_controllers.StackingController.__init__(
            self,
            name=name,
            pick_place_controller=PickPlaceController(
                name=name + "_pick_place_controller", gripper=gripper, robot_articulation=robot_articulation
            ),
            picking_order_cube_names=picking_order_cube_names,
            robot_observation_name=robot_observation_name,
        )
        return

    def forward(
        self,
        observations: dict,
        end_effector_orientation: Optional[np.ndarray] = None,
        end_effector_offset: Optional[np.ndarray] = None,
    ) -> ArticulationAction:
        """[summary]

        Args:
            observations (dict): [description]
            end_effector_orientation (Optional[np.ndarray], optional): [description]. Defaults to None.
            end_effector_offset (Optional[np.ndarray], optional): [description]. Defaults to None.

        Returns:
            ArticulationAction: [description]
        """
        return super().forward(
            observations, end_effector_orientation=end_effector_orientation, end_effector_offset=end_effector_offset
        )
