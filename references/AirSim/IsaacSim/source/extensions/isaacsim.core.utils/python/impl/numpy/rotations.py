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
import typing

import numpy as np
from pxr import Gf
from scipy.spatial.transform import Rotation


def gf_quat_to_tensor(orientation: typing.Union[Gf.Quatd, Gf.Quatf, Gf.Quaternion], device=None) -> np.ndarray:
    """Converts a pxr Quaternion type to a numpy array following [w, x, y, z] convention.

    Args:
        orientation (typing.Union[Gf.Quatd, Gf.Quatf, Gf.Quaternion]): [description]

    Returns:
        np.ndarray: [description]
    """
    quat = np.zeros(4)
    quat[1:] = orientation.GetImaginary()
    quat[0] = orientation.GetReal()
    return quat


def euler_angles_to_quats(
    euler_angles: np.ndarray, degrees: bool = False, extrinsic: bool = True, device=None
) -> np.ndarray:
    """Vectorized version of converting euler angles to quaternion (scalar first)

    Args:
        euler_angles np.ndarray: euler angles with shape (N, 3) or (3,) representation XYZ in extrinsic coordinates
        extrinsic (bool, optional): True if the euler angles follows the extrinsic angles
                   convention (equivalent to ZYX ordering but returned in the reverse) and False if it follows
                   the intrinsic angles conventions (equivalent to XYZ ordering).
                   Defaults to True.
        degrees (bool, optional): True if degrees, False if radians. Defaults to False.

    Returns:
        np.ndarray: quaternions representation of the angles (N, 4) or (4,) - scalar first.
    """
    if extrinsic:
        order = "xyz"
    else:
        order = "XYZ"
    rot = Rotation.from_euler(order, euler_angles, degrees=degrees)
    result = rot.as_quat()
    if len(result.shape) == 1:
        result = result[[3, 0, 1, 2]]
    else:
        result = result[:, [3, 0, 1, 2]]
    return result


def quats_to_euler_angles(
    quaternions: np.ndarray, degrees: bool = False, extrinsic: bool = True, device=None
) -> np.ndarray:
    """Vectorized version of converting quaternions (scalar first) to euler angles

    Args:
        quaternions (np.ndarray): quaternions with shape (N, 4) or (4,) - scalar first
        degrees (bool, optional): Return euler angles in degrees if True, radians if False. Defaults to False.
        extrinsic (bool, optional): True if the euler angles follows the extrinsic angles
                   convention (equivalent to ZYX ordering but returned in the reverse) and False if it follows
                   the intrinsic angles conventions (equivalent to XYZ ordering).
                   Defaults to True.

    Returns:
        np.ndarray: Euler angles in extrinsic or intrinsic coordinates XYZ order with shape (N, 3) or (3,) corresponding to the quaternion rotations
    """
    if extrinsic:
        order = "xyz"
    else:
        order = "XYZ"
    if len(quaternions.shape) == 1:
        q = quaternions[[1, 2, 3, 0]]
    else:
        q = quaternions[:, [1, 2, 3, 0]]
    rot = Rotation.from_quat(q)
    result = rot.as_euler(order, degrees)
    return result


def rot_matrices_to_quats(rotation_matrices: np.ndarray, device=None) -> np.ndarray:
    """Vectorized version of converting rotation matrices to quaternions

    Args:
        rotation_matrices (np.ndarray): N Rotation matrices with shape (N, 3, 3) or (3, 3)

    Returns:
        np.ndarray: quaternion representation of the rotation matrices (N, 4) or (4,) - scalar first
    """
    rot = Rotation.from_matrix(rotation_matrices)
    result = rot.as_quat()
    if len(result.shape) == 1:
        result = result[[3, 0, 1, 2]]
    else:
        result = result[:, [3, 0, 1, 2]]
    return result


def quats_to_rot_matrices(quaternions: np.ndarray, device=None) -> np.ndarray:
    """Vectorized version of converting quaternions to rotation matrices

    Args:
        quaternions (np.ndarray): quaternions with shape (N, 4) or (4,) and scalar first

    Returns:
        np.ndarray: N Rotation matrices with shape (N, 3, 3) or (3, 3)
    """
    if len(quaternions.shape) == 1:
        q = quaternions[[1, 2, 3, 0]]
    else:
        q = quaternions[:, [1, 2, 3, 0]]
    rot = Rotation.from_quat(q)
    result = rot.as_matrix()
    return result


def rotvecs_to_quats(rotation_vectors: np.ndarray, degrees: bool = False, device=None) -> np.ndarray:
    """Vectorized version of converting rotation vectors to quaternions

    Args:
        rotation_vectors (np.ndarray): N rotation vectors with shape (N, 3) or (3,).  The magnitude of the rotation vector describes the magnitude of the rotation.
            The normalized rotation vector represents the axis of rotation.
        degrees (bool): The magnitude of the rotation vector will be interpreted as degrees if True, and radians if False.  Defaults to False.

    Returns:
        np.ndarray: quaternion representation of the rotation matrices (N, 4) or (4,) - scalar first
    """
    rot = Rotation.from_rotvec(rotation_vectors, degrees)
    result = rot.as_quat()
    if len(result.shape) == 1:
        result = result[[3, 0, 1, 2]]
    else:
        result = result[:, [3, 0, 1, 2]]
    return result


def quats_to_rotvecs(quaternions: np.ndarray, device=None) -> np.ndarray:
    """Vectorized version of converting quaternions to rotation vectors

    Args:
        quaternions (np.ndarray): quaternions with shape (N, 4) or (4,) and scalar first

    Returns:
        np.ndarray: N rotation vectors with shape (N,3) or (3,).  The magnitude of the rotation vector describes the magnitude of the rotation.
            The normalized rotation vector represents the axis of rotation.
    """
    if len(quaternions.shape) == 1:
        q = quaternions[[1, 2, 3, 0]]
    else:
        q = quaternions[:, [1, 2, 3, 0]]
    rot = Rotation.from_quat(q)
    result = rot.as_rotvec()
    return result


def rad2deg(radian_value: np.ndarray, device=None) -> np.ndarray:
    """_summary_

    Args:
        radian_value (np.ndarray): _description_
        device (_type_, optional): _description_. Defaults to None.

    Returns:
        np.ndarray: _description_
    """
    return np.rad2deg(radian_value)


def deg2rad(degree_value: np.ndarray, device=None) -> np.ndarray:
    """_summary_

    Args:
        degree_value (np.ndarray): _description_
        device (_type_, optional): _description_. Defaults to None.

    Returns:
        np.ndarray: _description_
    """
    return np.deg2rad(degree_value)


def xyzw2wxyz(q, ret_torch=False):
    return np.roll(q, 1, -1)


def wxyz2xyzw(q, ret_torch=False):
    return np.roll(q, -1, -1)
