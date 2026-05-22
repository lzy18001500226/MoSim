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


from typing import Tuple

import numpy as np
import PIL.Image
from isaacsim.replicator.mobility_gen.impl.common import Buffer, Module
from isaacsim.replicator.mobility_gen.impl.inputs import Gamepad, Keyboard
from isaacsim.replicator.mobility_gen.impl.occupancy_map import OccupancyMap
from isaacsim.replicator.mobility_gen.impl.path_planner import compress_path, generate_paths
from isaacsim.replicator.mobility_gen.impl.pose_samplers import GridPoseSampler, UniformPoseSampler
from isaacsim.replicator.mobility_gen.impl.robot import MobilityGenRobot

# isaacsim.replicator.mobility_gen.examples
from isaacsim.replicator.mobility_gen.impl.scenario import SCENARIOS, MobilityGenScenario
from isaacsim.replicator.mobility_gen.impl.utils.path_utils import PathHelper
from isaacsim.replicator.mobility_gen.impl.utils.registry import Registry
from PIL import Image, ImageDraw


@SCENARIOS.register()
class KeyboardTeleoperationScenario(MobilityGenScenario):

    def __init__(self, robot: MobilityGenRobot, occupancy_map: OccupancyMap):
        super().__init__(robot, occupancy_map)
        self.keyboard = Keyboard()
        self.pose_sampler = UniformPoseSampler()

    def reset(self):
        pose = self.pose_sampler.sample(self.buffered_occupancy_map)
        self.robot.set_pose_2d(pose)
        self.update_state()

    def step(self, step_size):

        self.update_state()

        buttons = self.keyboard.buttons.get_value()

        w_val = float(buttons[0])
        a_val = float(buttons[1])
        s_val = float(buttons[2])
        d_val = float(buttons[3])

        linear_velocity = (w_val - s_val) * self.robot.keyboard_linear_velocity_gain
        angular_velocity = (a_val - d_val) * self.robot.keyboard_angular_velocity_gain

        self.robot.action.set_value(np.array([linear_velocity, angular_velocity]))

        self.robot.write_action(step_size)

        self.update_state()

        return True


@SCENARIOS.register()
class GamepadTeleoperationScenario(MobilityGenScenario):

    def __init__(self, robot: MobilityGenRobot, occupancy_map: OccupancyMap):
        super().__init__(robot, occupancy_map)
        self.gamepad = Gamepad()
        self.pose_sampler = UniformPoseSampler()

    def reset(self):
        pose = self.pose_sampler.sample(self.buffered_occupancy_map)
        self.robot.set_pose_2d(pose)
        self.update_state()

    def step(self, step_size: float):

        self.gamepad.update_state()

        axes = self.gamepad.axes.get_value()
        linear_velocity = axes[0] * self.robot.gamepad_linear_velocity_gain
        angular_velocity = axes[3] * self.robot.gamepad_angular_velocity_gain

        self.robot.action.set_value(np.array([linear_velocity, angular_velocity]))
        self.robot.write_action(step_size)

        self.update_state()

        return True


@SCENARIOS.register()
class RandomAccelerationScenario(MobilityGenScenario):

    def __init__(self, robot: MobilityGenRobot, occupancy_map: OccupancyMap):
        super().__init__(robot, occupancy_map)
        self.pose_sampler = GridPoseSampler(robot.random_action_grid_pose_sampler_grid_size)
        self.is_alive = True
        self.collision_occupancy_map = occupancy_map.buffered(robot.occupancy_map_collision_radius)

    def reset(self):
        self.robot.action.set_value(np.zeros(2))
        pose = self.pose_sampler.sample(self.buffered_occupancy_map)
        self.robot.set_pose_2d(pose)
        self.is_alive = True
        self.update_state()

    def step(self, step_size: float):

        self.update_state()

        current_action = self.robot.action.get_value()

        linear_velocity = (
            current_action[0] + step_size * np.random.randn(1) * self.robot.random_action_linear_acceleration_std
        )
        angular_velocity = (
            current_action[1] + step_size * np.random.randn(1) * self.robot.random_action_angular_acceleration_std
        )

        linear_velocity = np.clip(linear_velocity, *self.robot.random_action_linear_velocity_range)[0]
        angular_velocity = np.clip(angular_velocity, *self.robot.random_action_angular_velocity_range)[0]

        self.robot.action.set_value(np.array([linear_velocity, angular_velocity]))
        self.robot.write_action(step_size)

        self.update_state()

        # Check out of bounds or collision
        pose = self.robot.get_pose_2d()
        if not self.collision_occupancy_map.check_world_point_in_bounds(pose):
            self.is_alive = False
        elif not self.collision_occupancy_map.check_world_point_in_freespace(pose):
            self.is_alive = False

        return self.is_alive


@SCENARIOS.register()
class RandomPathFollowingScenario(MobilityGenScenario):
    def __init__(self, robot: MobilityGenRobot, occupancy_map: OccupancyMap):
        super().__init__(robot, occupancy_map)
        self.pose_sampler = UniformPoseSampler()
        self.is_alive = True
        self.target_path = Buffer()
        self.collision_occupancy_map = occupancy_map.buffered(robot.occupancy_map_collision_radius)

    def _vector_angle(self, w: np.ndarray, v: np.ndarray):
        delta_angle = np.arctan2(w[1] * v[0] - w[0] * v[1], w[0] * v[0] + w[1] * v[1])
        return delta_angle

    def set_random_target_path(self):
        current_pose = self.robot.get_pose_2d()

        start_px = self.occupancy_map.world_to_pixel_numpy(np.array([[current_pose.x, current_pose.y]]))
        freespace = self.buffered_occupancy_map.freespace_mask()

        start = (start_px[0, 1], start_px[0, 0])

        output = generate_paths(start, freespace)
        end = output.sample_random_end_point()
        path = output.unroll_path(end)
        path, _ = compress_path(path)  # remove redundant points
        path = path[:, ::-1]  # y,x -> x,y coordinates
        path = self.occupancy_map.pixel_to_world_numpy(path)
        self.target_path.set_value(path)
        self.target_path_helper = PathHelper(path)

    def reset(self):
        self.robot.action.set_value(np.zeros(2))
        pose = self.pose_sampler.sample(self.buffered_occupancy_map)
        self.robot.set_pose_2d(pose)
        self.set_random_target_path()
        self.is_alive = True
        self.update_state()

    def step(self, step_size: float):

        self.update_state()
        target_path = self.target_path.get_value()
        current_pose = self.robot.get_pose_2d()

        if not self.collision_occupancy_map.check_world_point_in_bounds(current_pose):
            self.is_alive = False
            return self.is_alive
        elif not self.collision_occupancy_map.check_world_point_in_freespace(current_pose):
            self.is_alive = False
            return self.is_alive

        pt_robot = np.array([current_pose.x, current_pose.y])
        pt_path, pt_path_length, _, _ = self.target_path_helper.find_nearest(pt_robot)
        pt_target = self.target_path_helper.get_point_by_distance(
            distance=pt_path_length + self.robot.path_following_target_point_offset_meters
        )

        path_end = target_path[-1]
        dist_to_target = np.sqrt(np.sum((pt_robot - path_end) ** 2))

        if dist_to_target < self.robot.path_following_stop_distance_threshold:
            self.is_alive = False
        else:
            vec_robot_unit = np.array([np.cos(current_pose.theta), np.sin(current_pose.theta)])
            vec_target = pt_target - pt_robot
            vec_target_unit = vec_target / np.sqrt(np.sum(vec_target**2))
            d_theta = self._vector_angle(vec_robot_unit, vec_target_unit)

            if abs(d_theta) > self.robot.path_following_forward_angle_threshold:
                linear_velocity = 0.0
            else:
                linear_velocity = self.robot.path_following_speed

            angular_gain: float = self.robot.path_following_angular_gain
            angular_velocity = -angular_gain * d_theta
            self.robot.action.set_value(np.array([linear_velocity, angular_velocity]))

        self.robot.write_action(step_size=step_size)

        return self.is_alive

    def get_visualization_image(self):
        image = self.occupancy_map.ros_image().copy().convert("RGBA")
        draw = ImageDraw.Draw(image)
        path = self.target_path.get_value()
        if path is not None:
            line_coordinates = []
            path_pixels = self.occupancy_map.world_to_pixel_numpy(path)
            for i in range(len(path_pixels)):
                line_coordinates.append(int(path_pixels[i, 0]))
                line_coordinates.append(int(path_pixels[i, 1]))
            width_pixels = self.robot.occupancy_map_radius / self.occupancy_map.resolution
            draw.line(line_coordinates, fill="green", width=int(width_pixels / 2), joint="curve")

        return image
