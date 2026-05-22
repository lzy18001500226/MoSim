# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import asyncio

import carb
import omni.kit.commands
import omni.kit.utils
from isaacsim.core.utils._isaac_utils import transforms
from isaacsim.core.utils.stage import get_current_stage, get_current_stage_id
from pxr import Sdf


class IsaacSimSpawnPrim(omni.kit.commands.Command):
    """Command to spawn a new prim in the stage and set its transform. This uses dynamic_control to properly handle physics objects and articulation

    Typical usage example:

    .. code-block:: python

        omni.kit.commands.execute(
            "IsaacSimSpawnPrim",
            usd_path="/path/to/file.usd",
            prim_path="/World/Prim,
            translation=(0, 0, 0),
            rotation=(0, 0, 0, 1),
        )
    """

    def __init__(
        self, usd_path: str, prim_path: str, translation: carb.Float3 = (0, 0, 0), rotation: carb.Float4 = (0, 0, 0, 1)
    ):
        # condensed way to copy all input arguments into self with an underscore prefix
        for name, value in vars().items():
            if name != "self":
                setattr(self, f"_{name}", value)
        pass
        self._stage = get_current_stage()
        self._stage_id = get_current_stage_id()
        self._context = omni.usd.get_context()
        pass

    def do(self) -> bool:
        self._prim = self._stage.DefinePrim(self._prim_path, "Xform")
        self._prim.GetReferences().AddReference(self._usd_path)
        if self._translation is not None and self._rotation is not None:
            transforms.set_transform(
                self._stage_id,
                str(self._prim.GetPath()),
                tuple(self._translation),
                tuple(self._rotation),
            )

        return True
        pass

    def undo(self):
        pass


class IsaacSimTeleportPrim(omni.kit.commands.Command):
    """Command to set a transform of a prim. This uses dynamic_control to properly handle physics objects and articulation

    Typical usage example:

    .. code-block:: python

        omni.kit.commands.execute(
            "IsaacSimTeleportPrim",
            prim_path="/World/Prim,
            translation=(0, 0, 0),
            rotation=(0, 0, 0, 1),
        )
    """

    def __init__(self, prim_path: str, translation: carb.Float3 = (0, 0, 0), rotation: carb.Float4 = (0, 0, 0, 1)):
        for name, value in vars().items():
            if name != "self":
                setattr(self, f"_{name}", value)
        self._stage = get_current_stage()
        self._stage_id = get_current_stage_id()
        self._context = omni.usd.get_context()
        pass

    def do(self) -> bool:
        if self._translation is not None and self._rotation is not None:
            transforms.set_transform(self._stage_id, str(self._prim_path), self._translation, self._rotation)
        return True
        pass

    def undo(self):
        pass


class IsaacSimScalePrim(omni.kit.commands.Command):
    """Command to set a scale of a prim

    Typical usage example:

    .. code-block:: python

        omni.kit.commands.execute(
            "IsaacSimScalePrim",
            prim_path="/World/Prim,
            scale=(1.5, 1.5, 1.5),
        )
    """

    def __init__(self, prim_path: str, scale: carb.Float3 = (0, 0, 0)):
        for name, value in vars().items():
            if name != "self":
                setattr(self, f"_{name}", value)
        self._stage = get_current_stage()
        self._stage_id = get_current_stage_id()
        self._context = omni.usd.get_context()
        pass

    def do(self) -> bool:
        if self._scale is not None:
            transforms.set_scale(self._stage_id, str(self._prim_path), self._scale)
        return True
        pass

    def undo(self):
        pass


class IsaacSimDestroyPrim(omni.kit.commands.Command):
    """Command to set a delete a prim. This variant has less overhead than other commands as it doesn't store an undo operation

    Typical usage example:

    .. code-block:: python

        omni.kit.commands.execute(
            "IsaacSimDestroyPrim",
            prim_path="/World/Prim,
        )
    """

    def __init__(self, prim_path: str):
        for name, value in vars().items():
            if name != "self":
                setattr(self, f"_{name}", value)
        pass

    def do(self) -> bool:
        delete_cmd = omni.usd.commands.DeletePrimsCommand([self._prim_path])
        delete_cmd.do()
        pass

    def undo(self):
        pass


omni.kit.commands.register_all_commands_in_module(__name__)
