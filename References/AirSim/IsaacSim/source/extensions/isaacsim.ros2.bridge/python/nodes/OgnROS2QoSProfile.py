# SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import json
import traceback

import carb
import omni
from isaacsim.core.nodes import BaseResetNode
from isaacsim.ros2.bridge.ogn.OgnROS2QoSProfileDatabase import OgnROS2QoSProfileDatabase


class OgnROS2QoSProfileInternalState(BaseResetNode):
    def __init__(self):
        self.node = None

        # Semaphore to prevent createProfile attribute to be set to custom when it is the one modifying the policy inputs
        self.usingPresetProfileSemaphore = 0

        self.numInputs = 8  # Number of inputs in the node minus 1

        self.firstFrame = True
        super().__init__(initialize=False)

    def custom_reset(self):
        self.firstFrame = True
        pass

    def on_qos_policy_change(self, attr):
        if not self.usingPresetProfileSemaphore:
            self.node.get_attribute("inputs:createProfile").set("Custom")
            return

        self.usingPresetProfileSemaphore = self.usingPresetProfileSemaphore - 1

    def on_attribute_changed(self, attr):

        if attr.get() == "Custom":
            self.changedToCustom = True
            return

        self.usingPresetProfileSemaphore = self.numInputs

        def set_time_default():
            self.node.get_attribute("inputs:deadline").set(0.0)
            self.node.get_attribute("inputs:lifespan").set(0.0)
            self.node.get_attribute("inputs:leaseDuration").set(0.0)

        def set_default():
            self.node.get_attribute("inputs:history").set("keepLast")
            self.node.get_attribute("inputs:depth").set(10)
            self.node.get_attribute("inputs:reliability").set("reliable")
            self.node.get_attribute("inputs:durability").set("volatile")
            self.node.get_attribute("inputs:liveliness").set("systemDefault")
            set_time_default()

        if attr.get() == "Default for publishers/subscribers":
            set_default()

        elif attr.get() == "Services":
            set_default()

        elif attr.get() == "System Default":
            self.node.get_attribute("inputs:history").set("systemDefault")
            self.node.get_attribute("inputs:depth").set(0)
            self.node.get_attribute("inputs:reliability").set("systemDefault")
            self.node.get_attribute("inputs:durability").set("systemDefault")
            self.node.get_attribute("inputs:liveliness").set("systemDefault")
            set_time_default()

        elif attr.get() == "Sensor Data":
            self.node.get_attribute("inputs:history").set("keepLast")
            self.node.get_attribute("inputs:depth").set(5)
            self.node.get_attribute("inputs:reliability").set("bestEffort")
            self.node.get_attribute("inputs:durability").set("volatile")
            self.node.get_attribute("inputs:liveliness").set("systemDefault")
            set_time_default()


class OgnROS2QoSProfile:
    @staticmethod
    def internal_state():
        return OgnROS2QoSProfileInternalState()

    @staticmethod
    def compute(db) -> bool:

        state = db.per_instance_state
        if state.firstFrame:
            qos_profile = {
                "history": db.inputs.history,
                "depth": db.inputs.depth,
                "reliability": db.inputs.reliability,
                "durability": db.inputs.durability,
                "deadline": db.inputs.deadline,
                "lifespan": db.inputs.lifespan,
                "liveliness": db.inputs.liveliness,
                "leaseDuration": db.inputs.leaseDuration,
            }

            db.outputs.qosProfile = json.dumps(qos_profile)

            state.firstFrame = False

    @staticmethod
    def init_instance(node, graph_instance_id):
        state = OgnROS2QoSProfileDatabase.get_internal_state(node, graph_instance_id)
        state.node = node

        attributeNames = [
            "inputs:history",
            "inputs:depth",
            "inputs:reliability",
            "inputs:durability",
            "inputs:deadline",
            "inputs:lifespan",
            "inputs:liveliness",
            "inputs:leaseDuration",
        ]

        attr = node.get_attribute("inputs:createProfile")
        attr.register_value_changed_callback(state.on_attribute_changed)

        for attrInput in attributeNames:
            attr_policy = node.get_attribute(attrInput)
            attr_policy.register_value_changed_callback(state.on_qos_policy_change)

        state.on_attribute_changed(attr)

    @staticmethod
    def release_instance(node, graph_instance_id):
        try:
            state = OgnROS2QoSProfileInternalState.per_instance_internal_state(node)
        except Exception:
            state = None
            pass

        if state is not None:
            state.reset()
