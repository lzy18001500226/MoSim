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
from typing import List

from pxr import Usd, UsdShade


class VisualMaterial(object):
    """[summary]

    Args:
        name (str): [description]
        prim_path (str): [description]
        prim (Usd.Prim): [description]
        shaders_list (list[UsdShade.Shader]): [description]
        material (UsdShade.Material): [description]
    """

    def __init__(
        self,
        name: str,
        prim_path: str,
        prim: Usd.Prim,
        shaders_list: List[UsdShade.Shader],
        material: UsdShade.Material,
    ) -> None:
        self._shaders_list = shaders_list
        self._material = material
        self._name = name
        self._prim_path = prim_path
        self._prim = prim
        return

    @property
    def material(self) -> UsdShade.Material:
        """[summary]

        Returns:
            UsdShade.Material: [description]
        """
        return self._material

    @property
    def shaders_list(self) -> List[UsdShade.Shader]:
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._shaders_list

    @property
    def name(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return self._name

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
