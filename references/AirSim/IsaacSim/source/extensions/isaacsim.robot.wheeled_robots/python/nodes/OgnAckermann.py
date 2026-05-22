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

import numpy as np
import omni.graph.core as og
from isaacsim.core.nodes import BaseResetNode
from isaacsim.robot.wheeled_robots.ogn.OgnAckermannDatabase import OgnAckermannDatabase


class OgnAckermannInternalState(BaseResetNode):
    def __init__(self):
        self.node = None
        super().__init__(initialize=False)

    def custom_reset(self):
        self.node.get_attribute("outputs:leftWheelAngle").set(0.0)
        self.node.get_attribute("outputs:rightWheelAngle").set(0.0)
        self.node.get_attribute("outputs:wheelRotationVelocity").set(0.0)


class OgnAckermann:
    @staticmethod
    def init_instance(node, graph_instance_id):
        state = OgnAckermannDatabase.get_internal_state(node, graph_instance_id)
        state.node = node
        state.graph_id = graph_instance_id

    @staticmethod
    def internal_state():
        return OgnAckermannInternalState()

    @staticmethod
    def compute(db) -> bool:

        # Deprecation waning
        db.log_warn("This node is deprecated as of Isaac Sim 4.1.0 in favour of OgnAckermannController")

        # avoid division by zero
        if db.inputs.turningWheelRadius <= 0:
            db.log_warn("Omnigraph warning: turning wheel radius is 0")
            return False

        # if turning wheel radius is very small (< 1cm)
        elif db.inputs.turningWheelRadius < 1e-2:
            db.log_warn(f"Omnigraph warning: turning wheel radius is very small: {db.inputs.turningWheelRadius}")

        WB = db.inputs.wheelBase
        TW = db.inputs.trackWidth

        # If input steering angle is less than 0.9 degrees ~ 0.0157 rad
        if np.fabs(db.inputs.steeringAngle) < 0.0157:
            delta_l = delta_r = 0.0

        else:
            R = (-1.0 if db.inputs.invertSteeringAngle else 1.0) * WB / np.tan(db.inputs.steeringAngle)

            # Equations were simplied from the ones shown in https://www.mathworks.com/help/vdynblks/ref/kinematicsteering.html
            # compute the wheel angles by taking into account their offset from the center of the turning axle (where the bicycle model is centered), then computing the angles of each wheel relative to the turning point of the robot
            # Assuming front wheel drive
            delta_l = np.arctan(WB / (R - 0.5 * TW))
            delta_r = np.arctan(WB / (R + 0.5 * TW))

        # clamp wheel angles to max wheel rotation
        delta_l = np.clip(delta_l, -np.fabs(db.inputs.maxWheelRotation), np.fabs(db.inputs.maxWheelRotation))
        delta_r = np.clip(delta_r, -np.fabs(db.inputs.maxWheelRotation), np.fabs(db.inputs.maxWheelRotation))

        # output wheel angles
        db.outputs.leftWheelAngle = delta_l
        db.outputs.rightWheelAngle = delta_r

        w = 0.0

        if db.inputs.useAcceleration:
            if db.inputs.DT == 0.0:
                db.log_warn(f"Delta time for the simulation step is 0. Acceleration input will be ignored.")

            # compute wheel rotation velocity --> (current linear velocity + acceleration adjusted for dt) / turning (driven) wheel radius
            w = (
                db.inputs.currentLinearVelocity[1] + db.inputs.acceleration * db.inputs.DT
            ) / db.inputs.turningWheelRadius

        else:
            w = db.inputs.speed / db.inputs.turningWheelRadius

        # clamp wheel rotation velocity to max wheel velocity
        w = np.clip(w, -db.inputs.maxWheelVelocity, db.inputs.maxWheelVelocity)

        # output wheel rotation angular velocity
        db.outputs.wheelRotationVelocity = w

        # Begin next node execution (if configured)
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True

    @staticmethod
    def release_instance(node, graph_instance_id):
        try:
            state = OgnAckermannDatabase.get_internal_state(node, graph_instance_id)
        except Exception:
            state = None
            pass

        if state is not None:
            state.reset()
