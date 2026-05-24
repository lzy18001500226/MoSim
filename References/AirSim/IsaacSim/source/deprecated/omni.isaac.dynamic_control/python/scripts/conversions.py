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

from omni.isaac.dynamic_control import _dynamic_control
from pxr import Gf


def _vec3d_quatd_to_dctransform(translation: Gf.Vec3d, quat: Gf.Quatd) -> _dynamic_control.Transform:
    pose_t = (translation[0], translation[1], translation[2])
    pose_r = (quat.GetImaginary()[0], quat.GetImaginary()[1], quat.GetImaginary()[2], quat.GetReal())
    return _dynamic_control.Transform(pose_t, pose_r)


def create_transform(translation, rotation) -> _dynamic_control.Transform:
    if isinstance(rotation, Gf.Rotation):
        return _vec3d_quatd_to_dctransform(translation, rotation.GetQuat())
    if isinstance(rotation, Gf.Quatd):
        return _vec3d_quatd_to_dctransform(translation, rotation)


def create_transform_from_mat(mat: Gf.Matrix4d) -> _dynamic_control.Transform:
    trans = mat.ExtractTranslation()
    q = mat.ExtractRotation().GetQuaternion()
    (q_x, q_y, q_z) = q.GetImaginary()
    quat = [q_x, q_y, q_z, q.GetReal()]
    tr = _dynamic_control.Transform()
    tr.p = trans
    tr.r = quat
    return tr
