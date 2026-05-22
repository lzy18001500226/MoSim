# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import random

import carb
import omni.kit.window.property
from isaacsim.replicator.behavior.global_variables import EXPOSED_ATTR_NS
from isaacsim.replicator.behavior.utils.behavior_utils import (
    check_if_exposed_variables_should_be_removed,
    create_exposed_variables,
    get_exposed_variable,
    remove_exposed_variables,
)
from isaacsim.replicator.behavior.utils.scene_utils import (
    get_rotation_op_and_value,
    set_rotation_op_and_value,
    set_rotation_with_ops,
)
from omni.kit.scripting import BehaviorScript
from pxr import Gf, Sdf, Usd, UsdGeom


class RotationRandomizer(BehaviorScript):
    """
    Behavior script that randomizes the rotation of prims within specified euler angle bounds.
    Rotations are handled using various xformOps, including 'xformOp:rotateXYZ', 'xformOp:orient', etc.
    depending on the existing xformOps of the prim. If no rotation xformOp exists 'xformOp:orient' is used.
    The behavior can be applied to multiple prims at once.
    """

    BEHAVIOR_NS = "rotationRandomizer"
    VARIABLES_TO_EXPOSE = [
        {
            "attr_name": "range:minRotation",
            "attr_type": Sdf.ValueTypeNames.Vector3d,
            "default_value": Gf.Vec3d(0.0, 0.0, 0.0),
            "doc": "The minimum rotation (in degrees) for the randomization.",
        },
        {
            "attr_name": "range:maxRotation",
            "attr_type": Sdf.ValueTypeNames.Vector3d,
            "default_value": Gf.Vec3d(360.0, 360.0, 360.0),
            "doc": "The maximum rotation (in degrees) for the randomization.",
        },
        {
            "attr_name": "includeChildren",
            "attr_type": Sdf.ValueTypeNames.Bool,
            "default_value": True,
            "doc": "Include valid prim children to the behavior.",
        },
        {
            "attr_name": "interval",
            "attr_type": Sdf.ValueTypeNames.UInt,
            "default_value": 0,
            "doc": "Interval for updating the behavior. Value 0 means every frame.",
        },
    ]

    def on_init(self):
        """Called when the script is assigned to a prim."""
        self._min_rotation = Gf.Vec3d(0.0, 0.0, 0.0)
        self._max_rotation = Gf.Vec3d(360.0, 360.0, 360.0)
        self._update_counter = 0
        self._interval = 0
        self._valid_prims = []
        self._initial_rotations = {}

        # Expose the variables as USD attributes
        create_exposed_variables(self.prim, EXPOSED_ATTR_NS, self.BEHAVIOR_NS, self.VARIABLES_TO_EXPOSE)

        # Refresh the property windows to show the exposed variables
        omni.kit.window.property.get_window().request_rebuild()

    def on_destroy(self):
        """Called when the script is unassigned from a prim."""
        self._reset()
        # Exposed variables should be removed if the script is no longer assigned to the prim
        if check_if_exposed_variables_should_be_removed(self.prim, __file__):
            remove_exposed_variables(self.prim, EXPOSED_ATTR_NS, self.BEHAVIOR_NS, self.VARIABLES_TO_EXPOSE)
            omni.kit.window.property.get_window().request_rebuild()

    def on_play(self):
        """Called when `play` is pressed."""
        self._setup()
        # Make sure the initial behavior is applied if the interval is larger than 0
        if self._interval > 0:
            self._apply_behavior()

    def on_stop(self):
        """Called when `stop` is pressed."""
        self._reset()

    def on_update(self, current_time: float, delta_time: float):
        """Called on per frame update events that occur when `playing`."""
        if delta_time <= 0:
            return
        if self._interval <= 0:
            self._apply_behavior()
        else:
            self._update_counter += 1
            if self._update_counter >= self._interval:
                self._apply_behavior()
                self._update_counter = 0

    def _setup(self):
        # Fetch the exposed attributes
        self._min_rotation = self._get_exposed_variable("range:minRotation")
        self._max_rotation = self._get_exposed_variable("range:maxRotation")
        include_children = self._get_exposed_variable("includeChildren")
        self._interval = self._get_exposed_variable("interval")

        # Get the prims to apply the behavior to
        if include_children:
            self._valid_prims = [prim for prim in Usd.PrimRange(self.prim) if prim.IsA(UsdGeom.Xformable)]
        elif self.prim.IsA(UsdGeom.Xformable):
            self._valid_prims = [self.prim]
        else:
            self._valid_prims = []
            carb.log_warn(f"[{self.prim_path}] No valid prims found.")

        # Save the initial rotation op and value of the prims (create xformOp:orient if none present)
        for prim in self._valid_prims:
            rotation_data = get_rotation_op_and_value(prim)
            self._initial_rotations[prim] = rotation_data

    def _reset(self):
        # Set prims back to their initial rotations
        for prim, rotation_data in self._initial_rotations.items():
            rotation_op, rotation_val = rotation_data
            set_rotation_op_and_value(prim, rotation_op, rotation_val)
        # Clear cached values
        self._valid_prims.clear()
        self._initial_rotations.clear()
        self._interval = 0
        self._update_counter = 0

    def _apply_behavior(self):
        # Randomize the rotation for each valid prim
        for prim in self._valid_prims:
            self._randomize_rotation(prim)

    def _randomize_rotation(self, prim):
        # Create a Gf.Rotation from random Euler angles within the bounds
        rotation = (
            Gf.Rotation(Gf.Vec3d.XAxis(), random.uniform(self._min_rotation[0], self._max_rotation[0]))
            * Gf.Rotation(Gf.Vec3d.YAxis(), random.uniform(self._min_rotation[1], self._max_rotation[1]))
            * Gf.Rotation(Gf.Vec3d.ZAxis(), random.uniform(self._min_rotation[2], self._max_rotation[2]))
        )
        # Set the rotation using and existing xformOp (orient, rotate, transform) or create a new default xformOp:orient
        set_rotation_with_ops(prim, rotation)

    def _get_exposed_variable(self, attr_name):
        full_attr_name = f"{EXPOSED_ATTR_NS}:{self.BEHAVIOR_NS}:{attr_name}"
        return get_exposed_variable(self.prim, full_attr_name)
