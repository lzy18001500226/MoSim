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

import omni.kit.commands
from usd.schema.isaac import robot_schema


class CreateSurfaceGripper(omni.kit.commands.Command):
    """Creates Action graph containing a Surface Gripper node, and all prims to facilitate its creation

    Typical usage example:

    .. code-block:: python

        result, prim  = omni.kit.commands.execute(
                "CreateSurfaceGripper",
                prim_path="/SurfaceGripper",
            )
    """

    def __init__(self, prim_path: str = ""):
        # condensed way to copy all input arguments into self with an underscore prefix
        for name, value in vars().items():
            if name != "self":
                setattr(self, f"_{name}", value)
        self._prim = None
        self._stage = omni.usd.get_context().get_stage()
        self._prim_path = None
        stage = omni.usd.get_context().get_stage()
        if prim_path == "":
            selection = omni.usd.get_context().get_selection()
            paths = selection.get_selected_prim_paths()
            if paths:
                prim_path = paths[0]
            else:
                default_prim = stage.GetDefaultPrim()
                if default_prim is None:
                    # If no default prim, create at root level
                    prim_path = "/"
                else:
                    prim_path = str(default_prim.GetPath())
        self._prim_path = omni.usd.get_stage_next_free_path(stage, prim_path + "/SurfaceGripper", False)
        pass

    def do(self):
        self._prim = robot_schema.CreateSurfaceGripper(self._stage, self._prim_path)
        return self._prim

    def undo(self):
        if self._prim:
            return self._stage.RemovePrim(self._prim_path)
        pass


omni.kit.commands.register_all_commands_in_module(__name__)
