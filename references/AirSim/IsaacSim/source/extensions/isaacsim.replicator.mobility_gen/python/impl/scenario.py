# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


from typing import Optional, Tuple

import numpy as np
import PIL.Image
from PIL import Image

from .common import Buffer, Module
from .occupancy_map import OccupancyMap
from .robot import MobilityGenRobot
from .utils.registry import Registry


class MobilityGenScenario(Module):

    def __init__(self, robot: MobilityGenRobot, occupancy_map: OccupancyMap):
        self.robot = robot
        self.occupancy_map = occupancy_map
        self.buffered_occupancy_map = occupancy_map.buffered_meters(self.robot.occupancy_map_radius)

    @classmethod
    def from_robot_occupancy_map(cls, robot: MobilityGenRobot, occupancy_map: OccupancyMap):
        return cls(robot, occupancy_map)

    def reset(self):
        raise NotImplementedError

    def step(self, step_size: float) -> bool:
        raise NotImplementedError

    def get_visualization_image(self) -> Image:
        image = self.occupancy_map.ros_image()
        return image


SCENARIOS = Registry[MobilityGenScenario]()
