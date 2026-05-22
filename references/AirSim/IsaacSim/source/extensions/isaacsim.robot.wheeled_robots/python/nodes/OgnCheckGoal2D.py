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
from isaacsim.core.utils.rotations import quat_to_euler_angles
from isaacsim.robot.wheeled_robots.controllers.stanley_control import normalize_angle
from isaacsim.robot.wheeled_robots.ogn.OgnCheckGoal2DDatabase import OgnCheckGoal2DDatabase


class OgnCheckGoal2DInternalState(BaseResetNode):
    # modeled after OgnDifferentialController state layout
    def __init__(self):
        # store target pos to prevent repeated & unnecessary db.inputs.target access
        self.node = None
        self.target = [0, 0, 0]  # [x, y, z_rot]
        super().__init__(initialize=False)

    def custom_reset(self):
        # reset target to origin (not an ideal reset solution but technically works)
        self.node.get_attribute("inputs:target").set([0.0, 0.0, 0.0])


class OgnCheckGoal2D:
    @staticmethod
    def init_instance(node, graph_instance_id):
        state = OgnCheckGoal2DDatabase.get_internal_state(node, graph_instance_id)
        state.node = node
        state.graph_id = graph_instance_id

    @staticmethod
    def release_instance(node, graph_instance_id):
        try:
            state = OgnCheckGoal2DDatabase.get_internal_state(node, graph_instance_id)
        except Exception:
            state = None
            pass

        if state is not None:
            state.reset()

    @staticmethod
    def internal_state():
        return OgnCheckGoal2DInternalState()

    @staticmethod
    def compute(db) -> bool:
        state = db.per_instance_state

        # if planner outputs targetChanged = True, new target data will be accessed and stored
        if db.inputs.targetChanged:
            state.target = db.inputs.target

        # get current pos/rot data
        pos = db.inputs.currentPosition
        x = pos[0]
        y = pos[1]
        _, _, rot = quatd4_to_euler(db.inputs.currentOrientation)

        # compare & output if diff between current pos/rot and target pos/rot is above threshold limits
        t = db.inputs.thresholds
        db.outputs.reachedGoal = [np.hypot(x - state.target[0], y - state.target[1]) <= t[0], rot <= t[1]]

        # begin next node (steering control)
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True


def quatd4_to_euler(orientation):
    # implementation for quat_to_euler_angles that normalizes outputs
    x, y, z, w = tuple(orientation)
    roll, pitch, yaw = quat_to_euler_angles(np.array([w, x, y, z]))

    return normalize_angle(roll), normalize_angle(pitch), normalize_angle(yaw)
