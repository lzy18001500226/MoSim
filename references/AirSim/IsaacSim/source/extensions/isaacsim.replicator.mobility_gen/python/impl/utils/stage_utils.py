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

import os
import tempfile  # type: ignore
from typing import Tuple  # type: ignore

import PIL.Image
from pxr import Gf, Kind, PhysxSchema, Sdf, Usd, UsdGeom, UsdLux, UsdPhysics, UsdShade


def stage_add_camera(
    stage: Usd.Stage,
    path: str,
    focal_length: float = 35,
    horizontal_aperature: float = 20.955,
    vertical_aperature: float = 20.955,
    clipping_range: Tuple[float, float] = (0.1, 100000),
) -> UsdGeom.Camera:
    """Adds a camera to a USD stage.


    Args:
        stage (Usd.Stage): The USD stage to modify.
        path (str): The path to add the USD prim.
        focal_length (float): The focal length of the camera (default 35).
        horizontal_aperature (float): The horizontal aperature of the camera
            (default 20.955).
        vertical_aperature (float): The vertical aperature of the camera
            (default 20.955).
        clipping_range (Tuple[float, float]): The clipping range of the camera.

    returns:
        UsdGeom.Camera:  The created USD camera.
    """

    camera = UsdGeom.Camera.Define(stage, path)
    camera.CreateFocalLengthAttr().Set(focal_length)
    camera.CreateHorizontalApertureAttr().Set(horizontal_aperature)
    camera.CreateVerticalApertureAttr().Set(vertical_aperature)
    camera.CreateClippingRangeAttr().Set(clipping_range)

    return camera
