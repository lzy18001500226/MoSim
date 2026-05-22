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
from typing import Optional

import carb
import isaacsim.core.utils.stage as stage_utils
import omni.kit.app
from pxr import Usd, UsdPhysics, UsdShade


class PhysicsMaterial(object):
    """[summary]

    Args:
        prim_path (str): [description]
        name (str, optional): [description]. Defaults to "physics_material".
        static_friction (Optional[float], optional): [description]. Defaults to None.
        dynamic_friction (Optional[float], optional): [description]. Defaults to None.
        restitution (Optional[float], optional): [description]. Defaults to None.
    """

    def __init__(
        self,
        prim_path: str,
        name: str = "physics_material",
        static_friction: Optional[float] = None,
        dynamic_friction: Optional[float] = None,
        restitution: Optional[float] = None,
    ) -> None:
        self._name = name
        self._prim_path = prim_path

        stage = stage_utils.get_current_stage()
        if stage.GetPrimAtPath(prim_path).IsValid():
            carb.log_info("Physics Material Prim already defined at path: {}".format(prim_path))
            self._material = UsdShade.Material(stage.GetPrimAtPath(prim_path))
        else:
            self._material = UsdShade.Material.Define(stage, prim_path)
        self._prim = stage.GetPrimAtPath(prim_path)
        if self._prim.HasAPI(UsdPhysics.MaterialAPI):
            self._material_api = UsdPhysics.MaterialAPI(self._prim)
        else:
            self._material_api = UsdPhysics.MaterialAPI.Apply(self._prim)
        if static_friction is not None:
            self._material_api.CreateStaticFrictionAttr().Set(static_friction)
        if dynamic_friction is not None:
            self._material_api.CreateDynamicFrictionAttr().Set(dynamic_friction)
        if restitution is not None:
            self._material_api.CreateRestitutionAttr().Set(restitution)
        return

    @property
    def prim_path(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return self._prim_path

    @property
    def prim(self) -> Usd.Prim:
        """[summary]

        Returns:
            Usd.Prim: [description]
        """
        return self._prim

    @property
    def name(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return self._name

    @property
    def material(self) -> UsdShade.Material:
        """[summary]

        Returns:
            UsdShade.Material: [description]
        """
        return self._material

    def set_dynamic_friction(self, friction: float) -> None:
        """[summary]

        Args:
            friction (float): [description]
        """
        if self._material_api.GetDynamicFrictionAttr().Get() is None:
            self._material_api.CreateDynamicFrictionAttr().Set(friction)
        else:
            self._material_api.GetDynamicFrictionAttr().Set(friction)
        return

    def get_dynamic_friction(self) -> float:
        """[summary]

        Returns:
            float: [description]
        """
        if self._material_api.GetDynamicFrictionAttr().Get() is None:
            carb.log_warn("A dynamic friction attribute is not set yet")
            return None
        else:
            return self._material_api.GetDynamicFrictionAttr().Get()

    def set_static_friction(self, friction: float) -> None:
        """[summary]

        Args:
            friction (float): [description]
        """
        if self._material_api.GetStaticFrictionAttr().Get() is None:
            self._material_api.CreateStaticFrictionAttr().Set(friction)
        else:
            self._material_api.GetStaticFrictionAttr().Set(friction)
        return

    def get_static_friction(self) -> float:
        """[summary]

        Returns:
            float: [description]
        """
        if self._material_api.GetStaticFrictionAttr().Get() is None:
            carb.log_warn("A static friction attribute is not set yet")
            return None
        else:
            return self._material_api.GetStaticFrictionAttr().Get()

    def set_restitution(self, restitution: float) -> None:
        """[summary]

        Args:
            restitution (float): [description]
        """
        if self._material_api.GetRestitutionAttr().Get() is None:
            self._material_api.CreateRestitutionAttr().Set(restitution)
        else:
            self._material_api.GetRestitutionAttr().Set(restitution)
        return

    def get_restitution(self) -> float:
        """[summary]

        Returns:
            float: [description]
        """
        if self._material_api.GetRestitutionAttr().Get() is None:
            carb.log_warn("A restitution attribute is not set yet")
            return None
        else:
            return self._material_api.GetRestitutionAttr().Get()
