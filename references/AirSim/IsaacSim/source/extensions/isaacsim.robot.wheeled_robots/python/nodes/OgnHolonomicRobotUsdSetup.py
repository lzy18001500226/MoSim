# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


from re import I

import numpy as np
import omni.graph.core as og
from isaacsim.robot.wheeled_robots.ogn.OgnHolonomicRobotUsdSetupDatabase import OgnHolonomicRobotUsdSetupDatabase
from isaacsim.robot.wheeled_robots.robots.holonomic_robot_usd_setup import HolonomicRobotUsdSetup


class OgnHolonomicRobotUsdSetupInternalState:
    def __init__(self):
        self.robot_prim_path = ""
        self.com_prim_path = ""
        self.wheel_radius = 0.0
        self.wheel_positions = np.array([])
        self.wheel_orientations = np.array([])
        self.mecanum_angles = 0.0
        self.wheel_dof_names = []
        self.robot_params = None
        self.initialized = False

    def initialize(self) -> None:
        if self.robot_prim_path:
            self.robot_params = HolonomicRobotUsdSetup(
                robot_prim_path=self.robot_prim_path, com_prim_path=self.com_prim_path
            )
            self.initialized = True


class OgnHolonomicRobotUsdSetup:
    """
    nodes for bundling robot parameters for any robot to be used by differential and articulation controller
    """

    @staticmethod
    def init_instance(node, graph_instance_id):
        state = OgnHolonomicRobotUsdSetupDatabase.get_internal_state(node, graph_instance_id)
        state.node = node

    @staticmethod
    def internal_state():
        return OgnHolonomicRobotUsdSetupInternalState()

    @staticmethod
    def compute(db) -> bool:
        try:
            # check about the using path vs bundle thing
            state = db.per_instance_state

            if db.inputs.usePath:
                robot_prim_path = db.inputs.robotPrimPath
                com_prim_path = db.inputs.comPrimPath
            else:
                if len(db.inputs.robotPrim) == 0 or len(db.inputs.comPrim) == 0:
                    return False
                else:
                    robot_prim_path = db.inputs.robotPrim[0].GetString()
                    com_prim_path = db.inputs.comPrim[0].GetString()

            if (robot_prim_path != state.robot_prim_path) or (com_prim_path != state.com_prim_path):
                state.robot_prim_path = robot_prim_path
                state.com_prim_path = com_prim_path

            if not state.initialized:
                state.initialize()

            if state.initialized:
                stop = False
                error_log = ""
                # TODO: Add a check to see if the wheel radius is valid
                if len(state.robot_params.wheel_radius) == 0:
                    error_log += "Wheel radius list is empty\n"
                    stop = True
                if len(state.robot_params.wheel_positions) == 0:
                    error_log += "Wheel positions list is empty\n"
                    stop = True
                if len(state.robot_params.wheel_orientations) == 0:
                    error_log += "Wheel orientations list is empty\n"
                    stop = True
                if len(state.robot_params.mecanum_angles) == 0:
                    error_log += "Mecanum angles list is empty\n"
                    stop = True
                if len(state.robot_params.wheel_dof_names) == 0:
                    error_log += "Wheel dof names list is empty\n"
                    stop = True
                if stop:
                    db.log_error(error_log)
                    return False

                db.outputs.wheelRadius = state.robot_params.wheel_radius
                db.outputs.wheelPositions = state.robot_params.wheel_positions
                db.outputs.wheelOrientations = state.robot_params.wheel_orientations
                db.outputs.mecanumAngles = state.robot_params.mecanum_angles
                db.outputs.wheelAxis = state.robot_params.wheel_axis
                db.outputs.upAxis = state.robot_params.up_axis
                db.outputs.wheelDofNames = state.robot_params.wheel_dof_names

        except Exception as error:
            db.log_error(str(error))
            return False

        return True
