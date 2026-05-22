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

import typing

# python
import numpy as np
import omni.physx

# isaacsim
from isaacsim.core.utils.stage import get_current_stage

# omniverse
from pxr import Gf, UsdGeom


def ray_cast(
    position: np.array, orientation: np.array, offset: np.array, max_dist: float = 100.0
) -> typing.Tuple[typing.Union[None, str], float]:
    """Projects a raycast forward along x axis with specified offset

    If a hit is found within the maximum distance, then the object's prim path and distance to it is returned.
    Otherwise, a None and 10000 is returned.

    Args:
        position (np.array): origin's position for ray cast
        orientation (np.array): origin's orientation for ray cast
        offset (np.array): offset for ray cast
        max_dist (float, optional): maximum distance to test for collisions in stage units. Defaults to 100.0.

    Returns:
        typing.Tuple[typing.Union[None, str], float]: path to geometry that was hit and hit distance, returns None, 10000 if no hit occurred
    """
    input_tr = Gf.Matrix4f()
    input_tr.SetTranslate(Gf.Vec3f(*position.tolist()))
    input_tr.SetRotateOnly(Gf.Quatf(*orientation.tolist()))
    offset_transform = Gf.Matrix4f()
    offset_transform.SetTranslate(Gf.Vec3f(*offset.tolist()))
    raycast_tf = offset_transform * input_tr
    trans = raycast_tf.ExtractTranslation()
    direction = raycast_tf.ExtractRotation().TransformDir((1, 0, 0))
    origin = (trans[0], trans[1], trans[2])
    ray_dir = (direction[0], direction[1], direction[2])

    hit = omni.physx.get_physx_scene_query_interface().raycast_closest(origin, ray_dir, max_dist)
    if hit["hit"]:
        usdGeom = UsdGeom.Mesh.Get(get_current_stage(), hit["rigidBody"])
        distance = hit["distance"]
        return usdGeom.GetPath().pathString, distance
    return None, 10000.0
