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

from __future__ import annotations

import numpy as np
import warp as wp

from . import ops as ops_utils


def rotation_matrix_to_quaternion(
    rotation_matrix: list | np.ndarray | wp.array,
    *,
    dtype: type | None = None,
    device: str | wp.context.Device | None = None,
) -> wp.array:
    """Convert rotation matrix to quaternion.

    Args:
        rotation_matrix: A 3x3 rotation matrix or batch of 3x3 rotation matrices with shape (..., 3, 3).
        dtype: Data type of the output array. If ``None``, the data type of the input is used.
        device: Device to place the output array on. If ``None``, the default device is used,
            unless the input is a Warp array (in which case the input device is used).

    Returns:
        Quaternion (w, x, y, z) or batch of quaternions with shape (..., 4).

    Example:

    .. code-block:: python

        >>> import isaacsim.core.experimental.utils.transform as transform_utils
        >>> import numpy as np
        >>>
        >>> # Identity matrix to quaternion
        >>> identity = np.eye(3)
        >>> quaternion = transform_utils.rotation_matrix_to_quaternion(identity)  # doctest: +NO_CHECK
        >>> quaternion.numpy()
        array([1., 0., 0., 0.])
    """
    rotation_matrix = ops_utils.place(rotation_matrix, dtype=dtype, device=device)

    # Handle single matrix case by adding batch dimension
    if rotation_matrix.ndim == 2:
        rotation_matrix = rotation_matrix.reshape((1, 3, 3))
        squeeze_output = True
    else:
        squeeze_output = False

    # Ensure we have proper 3x3 matrices
    if rotation_matrix.shape[-2:] != (3, 3):
        raise ValueError(f"Expected 3x3 rotation matrices, got shape {rotation_matrix.shape}")

    batch_shape = rotation_matrix.shape[:-2]
    batch_size = 1
    for dim in batch_shape:
        batch_size *= dim

    # Flatten batch dimensions
    rotation_matrix_flat = rotation_matrix.reshape((batch_size, 3, 3))
    output = wp.empty(shape=(batch_size, 4), dtype=rotation_matrix.dtype, device=rotation_matrix.device)

    wp.launch(
        _wk_rotation_matrix_to_quaternion,
        dim=batch_size,
        inputs=[rotation_matrix_flat, output],
        device=rotation_matrix.device,
    )

    # Reshape to original batch shape
    if squeeze_output:
        return output.reshape((4,))
    else:
        return output.reshape((*batch_shape, 4))


def euler_angles_to_rotation_matrix(
    euler_angles: list | np.ndarray | wp.array,
    *,
    degrees: bool = False,
    extrinsic: bool = True,
    dtype: type | None = None,
    device: str | wp.context.Device | None = None,
) -> wp.array:
    """Convert Euler XYZ or ZYX angles to rotation matrix.

    Args:
        euler_angles: Euler angles or batch of Euler angles with shape (..., 3).
        degrees: Whether passed angles are in degrees. Defaults to False.
        extrinsic: True if the euler angles follows the extrinsic angles
            convention (equivalent to ZYX ordering but returned in the reverse) and False if it follows
            the intrinsic angles conventions (equivalent to XYZ ordering). Defaults to True.
        dtype: Data type of the output array. If ``None``, the data type of the input is used.
        device: Device to place the output array on. If ``None``, the default device is used,
            unless the input is a Warp array (in which case the input device is used).

    Returns:
        A 3x3 rotation matrix or batch of 3x3 rotation matrices with shape (..., 3, 3).

    Example:

    .. code-block:: python

        >>> import isaacsim.core.experimental.utils.transform as transform_utils
        >>> import numpy as np
        >>>
        >>> # Zero rotation
        >>> euler = np.array([0, 0, 0])
        >>> rotation_matrix = transform_utils.euler_angles_to_rotation_matrix(euler)  # doctest: +NO_CHECK
        >>> rotation_matrix.numpy()
        array([[1., 0., 0.],
               [0., 1., 0.],
               [0., 0., 1.]], dtype=float32)
    """
    euler_angles = ops_utils.place(euler_angles, dtype=dtype, device=device)

    # Ensure floating point dtype to avoid int64 trigonometric function issues
    if euler_angles.dtype not in [wp.float32, wp.float64]:
        euler_angles = wp.array(euler_angles.numpy(), dtype=wp.float32, device=euler_angles.device)

    # Handle single angle case by adding batch dimension
    if euler_angles.ndim == 1:
        euler_angles = euler_angles.reshape((1, 3))
        squeeze_output = True
    else:
        squeeze_output = False

    # Ensure we have proper 3-element angle vectors
    if euler_angles.shape[-1] != 3:
        raise ValueError(f"Expected 3-element Euler angles, got shape {euler_angles.shape}")

    batch_shape = euler_angles.shape[:-1]
    batch_size = 1
    for dim in batch_shape:
        batch_size *= dim

    # Flatten batch dimensions
    euler_angles_flat = euler_angles.reshape((batch_size, 3))
    output = wp.empty(shape=(batch_size, 3, 3), dtype=euler_angles.dtype, device=euler_angles.device)

    wp.launch(
        _wk_euler_angles_to_rotation_matrix,
        dim=batch_size,
        inputs=[euler_angles_flat, output, degrees, extrinsic],
        device=euler_angles.device,
    )

    # Reshape to original batch shape
    if squeeze_output:
        return output.reshape((3, 3))
    else:
        return output.reshape((*batch_shape, 3, 3))


def euler_angles_to_quaternion(
    euler_angles: list | np.ndarray | wp.array,
    *,
    degrees: bool = False,
    extrinsic: bool = True,
    dtype: type | None = None,
    device: str | wp.context.Device | None = None,
) -> wp.array:
    """Convert Euler angles to quaternion.

    Args:
        euler_angles: Euler XYZ angles or batch of Euler angles with shape (..., 3).
        degrees: Whether input angles are in degrees. Defaults to False.
        extrinsic: True if the euler angles follows the extrinsic angles
            convention (equivalent to ZYX ordering but returned in the reverse) and False if it follows
            the intrinsic angles conventions (equivalent to XYZ ordering). Defaults to True.
        dtype: Data type of the output array. If ``None``, the data type of the input is used.
        device: Device to place the output array on. If ``None``, the default device is used,
            unless the input is a Warp array (in which case the input device is used).

    Returns:
        Quaternion (w, x, y, z) or batch of quaternions with shape (..., 4).

    Example:

    .. code-block:: python

        >>> import isaacsim.core.experimental.utils.transform as transform_utils
        >>> import numpy as np
        >>>
        >>> # Convert 90 degree rotation around Y axis
        >>> euler = np.array([0, np.pi/2, 0])
        >>> quaternion = transform_utils.euler_angles_to_quaternion(euler)  # doctest: +NO_CHECK
        >>> quaternion.numpy()
        array([0.70710678, 0.        , 0.70710678, 0.        ])
    """
    rotation_matrix = euler_angles_to_rotation_matrix(
        euler_angles, degrees=degrees, extrinsic=extrinsic, dtype=dtype, device=device
    )
    return rotation_matrix_to_quaternion(rotation_matrix)


def quaternion_multiplication(
    first_quaternion: list | np.ndarray | wp.array,
    second_quaternion: list | np.ndarray | wp.array,
    *,
    dtype: type | None = None,
    device: str | wp.context.Device | None = None,
) -> wp.array:
    """Multiply two quaternions using Hamilton product.

    Quaternion multiplication is used for combining rotations.
    Input quaternions are in [w, x, y, z] format.

    Args:
        first_quaternion: First quaternion or batch of quaternions with shape (..., 4) in [w, x, y, z] format.
        second_quaternion: Second quaternion or batch of quaternions with shape (..., 4) in [w, x, y, z] format.
        dtype: Data type of the output array. If ``None``, the data type of the first input is used.
        device: Device to place the output array on. If ``None``, the default device is used,
            unless the input is a Warp array (in which case the input device is used).

    Returns:
        Result of quaternion multiplication with shape (..., 4).

    Example:

    .. code-block:: python

        >>> import isaacsim.core.experimental.utils.transform as transform_utils
        >>> import numpy as np
        >>>
        >>> # Identity quaternion multiplied with itself
        >>> identity = np.array([1.0, 0.0, 0.0, 0.0])
        >>> result = transform_utils.quaternion_multiplication(identity, identity)  # doctest: +NO_CHECK
        >>> result.numpy()
        array([1., 0., 0., 0.])
    """
    first_quaternion = ops_utils.place(first_quaternion, dtype=dtype, device=device)
    second_quaternion = ops_utils.place(second_quaternion, dtype=dtype, device=first_quaternion.device)

    # Handle single quaternion case by adding batch dimension
    if first_quaternion.ndim == 1:
        first_quaternion = first_quaternion.reshape((1, 4))
        squeeze_output = True
    else:
        squeeze_output = False

    if second_quaternion.ndim == 1:
        second_quaternion = second_quaternion.reshape((1, 4))

    # Ensure we have proper 4-element quaternions
    if first_quaternion.shape[-1] != 4:
        raise ValueError(f"Expected 4-element quaternions for first input, got shape {first_quaternion.shape}")
    if second_quaternion.shape[-1] != 4:
        raise ValueError(f"Expected 4-element quaternions for second input, got shape {second_quaternion.shape}")

    # Ensure both inputs have same batch shape
    if first_quaternion.shape != second_quaternion.shape:
        raise ValueError(
            f"Input quaternions must have same shape, got {first_quaternion.shape} and {second_quaternion.shape}"
        )

    batch_shape = first_quaternion.shape[:-1]
    batch_size = 1
    for dim in batch_shape:
        batch_size *= dim

    # Flatten batch dimensions
    first_quaternion_flat = first_quaternion.reshape((batch_size, 4))
    second_quaternion_flat = second_quaternion.reshape((batch_size, 4))
    output = wp.empty(shape=(batch_size, 4), dtype=first_quaternion.dtype, device=first_quaternion.device)

    wp.launch(
        _wk_quaternion_multiplication,
        dim=batch_size,
        inputs=[first_quaternion_flat, second_quaternion_flat, output],
        device=first_quaternion.device,
    )

    # Reshape to original batch shape
    if squeeze_output:
        return output.reshape((4,))
    else:
        return output.reshape((*batch_shape, 4))


def quaternion_conjugate(
    quaternion: list | np.ndarray | wp.array,
    *,
    dtype: type | None = None,
    device: str | wp.context.Device | None = None,
) -> wp.array:
    """Compute quaternion conjugate by negating the vector part.

    Quaternion conjugate is used to compute the inverse rotation.
    For unit quaternions, conjugate equals inverse.

    Args:
        quaternion: Quaternion or batch of quaternions with shape (..., 4) in [w, x, y, z] format.
        dtype: Data type of the output array. If ``None``, the data type of the input is used.
        device: Device to place the output array on. If ``None``, the default device is used,
            unless the input is a Warp array (in which case the input device is used).

    Returns:
        Conjugate quaternion with shape (..., 4).

    Example:

    .. code-block:: python

        >>> import isaacsim.core.experimental.utils.transform as transform_utils
        >>> import numpy as np
        >>>
        >>> # Conjugate of a simple rotation quaternion
        >>> quaternion = np.array([0.7071, 0.7071, 0.0, 0.0])  # 90 deg around X
        >>> conjugate = transform_utils.quaternion_conjugate(quaternion)  # doctest: +NO_CHECK
        >>> conjugate.numpy()
        array([ 0.7071, -0.7071,  0.    ,  0.    ])
    """
    quaternion = ops_utils.place(quaternion, dtype=dtype, device=device)

    # Handle single quaternion case by adding batch dimension
    if quaternion.ndim == 1:
        quaternion = quaternion.reshape((1, 4))
        squeeze_output = True
    else:
        squeeze_output = False

    # Ensure we have proper 4-element quaternions
    if quaternion.shape[-1] != 4:
        raise ValueError(f"Expected 4-element quaternions, got shape {quaternion.shape}")

    batch_shape = quaternion.shape[:-1]
    batch_size = 1
    for dim in batch_shape:
        batch_size *= dim

    # Flatten batch dimensions
    quaternion_flat = quaternion.reshape((batch_size, 4))
    output = wp.empty(shape=(batch_size, 4), dtype=quaternion.dtype, device=quaternion.device)

    wp.launch(
        _wk_quaternion_conjugate,
        dim=batch_size,
        inputs=[quaternion_flat, output],
        device=quaternion.device,
    )

    # Reshape to original batch shape
    if squeeze_output:
        return output.reshape((4,))
    else:
        return output.reshape((*batch_shape, 4))


def quaternion_to_rotation_matrix(
    quaternion: list | np.ndarray | wp.array,
    *,
    dtype: type | None = None,
    device: str | wp.context.Device | None = None,
) -> wp.array:
    """Convert quaternion to rotation matrix.

    Converts quaternions in [w, x, y, z] format to 3x3 rotation matrices
    using the standard quaternion-to-matrix formula.

    Args:
        quaternion: Quaternion or batch of quaternions with shape (..., 4) in [w, x, y, z] format.
        dtype: Data type of the output array. If ``None``, the data type of the input is used.
        device: Device to place the output array on. If ``None``, the default device is used,
            unless the input is a Warp array (in which case the input device is used).

    Returns:
        A 3x3 rotation matrix or batch of 3x3 rotation matrices with shape (..., 3, 3).

    Example:

    .. code-block:: python

        >>> import isaacsim.core.experimental.utils.transform as transform_utils
        >>> import numpy as np
        >>>
        >>> # Identity quaternion to rotation matrix
        >>> identity = np.array([1.0, 0.0, 0.0, 0.0])
        >>> rotation_matrix = transform_utils.quaternion_to_rotation_matrix(identity)  # doctest: +NO_CHECK
        >>> rotation_matrix.numpy()
        array([[1., 0., 0.],
               [0., 1., 0.],
               [0., 0., 1.]])
    """
    quaternion = ops_utils.place(quaternion, dtype=dtype, device=device)

    # Ensure we have proper 4-element quaternions
    if quaternion.shape[-1] != 4:
        raise ValueError(f"Expected 4-element quaternions, got shape {quaternion.shape}")

    # Handle single quaternion case and determine batch size
    if quaternion.ndim == 1:
        squeeze_output = True
        batch_size = 1
    else:
        squeeze_output = False
        batch_shape = quaternion.shape[:-1]
        batch_size = int(np.prod(batch_shape))

    output = wp.empty(shape=(batch_size, 3, 3), dtype=quaternion.dtype, device=quaternion.device)

    wp.launch(
        _wk_quaternion_to_rotation_matrix,
        dim=batch_size,
        inputs=[quaternion.reshape((-1, 4)), output],
        device=quaternion.device,
    )

    # Reshape to original batch shape
    if squeeze_output:
        return output.reshape((3, 3))
    else:
        return output.reshape((*batch_shape, 3, 3))


"""
Custom Warp kernels for transform operations.
"""


@wp.kernel(enable_backward=False)
def _wk_rotation_matrix_to_quaternion(rotation_matrix: wp.array(ndim=3), output: wp.array(ndim=2)):
    """Convert rotation matrix to quaternion using Warp kernel."""
    i = wp.tid()

    # Extract matrix elements
    m00, m01, m02 = rotation_matrix[i, 0, 0], rotation_matrix[i, 0, 1], rotation_matrix[i, 0, 2]
    m10, m11, m12 = rotation_matrix[i, 1, 0], rotation_matrix[i, 1, 1], rotation_matrix[i, 1, 2]
    m20, m21, m22 = rotation_matrix[i, 2, 0], rotation_matrix[i, 2, 1], rotation_matrix[i, 2, 2]

    # Type-safe constants derived from matrix elements
    zero = m00 - m00  # Type-safe zero
    one = zero + output.dtype(1.0)  # Type-safe one using output dtype
    two = one + one  # Type-safe two
    four = two + two  # Type-safe four
    quarter = one / four  # Type-safe 0.25

    trace = m00 + m11 + m22

    if trace > zero:
        # w is largest
        s = wp.sqrt(trace + one) * two  # s = 4 * w
        w = quarter * s
        x = (m21 - m12) / s
        y = (m02 - m20) / s
        z = (m10 - m01) / s
    elif m00 > m11 and m00 > m22:
        # x is largest
        s = wp.sqrt(one + m00 - m11 - m22) * two  # s = 4 * x
        w = (m21 - m12) / s
        x = quarter * s
        y = (m01 + m10) / s
        z = (m02 + m20) / s
    elif m11 > m22:
        # y is largest
        s = wp.sqrt(one + m11 - m00 - m22) * two  # s = 4 * y
        w = (m02 - m20) / s
        x = (m01 + m10) / s
        y = quarter * s
        z = (m12 + m21) / s
    else:
        # z is largest
        s = wp.sqrt(one + m22 - m00 - m11) * two  # s = 4 * z
        w = (m10 - m01) / s
        x = (m02 + m20) / s
        y = (m12 + m21) / s
        z = quarter * s

    output[i, 0] = w
    output[i, 1] = x
    output[i, 2] = y
    output[i, 3] = z


@wp.kernel(enable_backward=False)
def _wk_euler_angles_to_rotation_matrix(
    euler_angles: wp.array(ndim=2),
    output: wp.array(ndim=3),
    degrees: bool,
    extrinsic: bool,
):
    """Convert Euler angles to rotation matrix using Warp kernel."""
    i = wp.tid()

    # Extract angles and ensure they are floating point for trigonometric functions
    # Use type-safe constants derived from array elements (same pattern as rotation_matrix_to_quaternion)
    angle1 = euler_angles[i, 0]
    angle2 = euler_angles[i, 1]
    angle3 = euler_angles[i, 2]

    # Create type-safe constants from the output array's dtype
    zero = output[i, 0, 0] - output[i, 0, 0]  # Type-safe zero
    one = zero + output.dtype(1.0)  # Type-safe one using output dtype

    # Ensure angles are floating point by adding zero (which forces type conversion)
    angle1 = angle1 + zero
    angle2 = angle2 + zero
    angle3 = angle3 + zero

    # Convert to radians if needed
    if degrees:
        # Type-safe constants using the same pattern
        pi = zero + output.dtype(3.141592653589793)  # Type-safe pi using output dtype
        one_eighty = zero + output.dtype(180.0)  # Type-safe 180
        deg_to_rad = pi / one_eighty  # Type-safe conversion factor
        angle1 = angle1 * deg_to_rad
        angle2 = angle2 * deg_to_rad
        angle3 = angle3 * deg_to_rad

    # Assign to roll, pitch, yaw based on convention
    if extrinsic:
        # ZYX extrinsic convention: [Z, Y, X] = [yaw, pitch, roll]
        roll = angle3  # X rotation (third)
        pitch = angle2  # Y rotation (second)
        yaw = angle1  # Z rotation (first)
    else:
        # XYZ intrinsic convention: [X, Y, Z] = [roll, pitch, yaw]
        roll = angle1  # X rotation (first)
        pitch = angle2  # Y rotation (second)
        yaw = angle3  # Z rotation (third)

    cr = wp.cos(roll)
    sr = wp.sin(roll)
    cy = wp.cos(yaw)
    sy = wp.sin(yaw)
    cp = wp.cos(pitch)
    sp = wp.sin(pitch)

    if extrinsic:
        # Extrinsic ZYX rotation: R = Rz(yaw) * Ry(pitch) * Rx(roll)
        # Standard formula for extrinsic ZYX Euler angles
        output[i, 0, 0] = cp * cy
        output[i, 0, 1] = cy * sp * sr - cr * sy
        output[i, 0, 2] = sr * sy + cr * cy * sp
        output[i, 1, 0] = cp * sy
        output[i, 1, 1] = cr * cy + sp * sr * sy
        output[i, 1, 2] = cr * sp * sy - cy * sr
        output[i, 2, 0] = -sp
        output[i, 2, 1] = cp * sr
        output[i, 2, 2] = cp * cr
    else:
        # Intrinsic XYZ rotation: R = Rx(roll) * Ry(pitch) * Rz(yaw)
        output[i, 0, 0] = cp * cy
        output[i, 0, 1] = -cp * sy
        output[i, 0, 2] = sp
        output[i, 1, 0] = cy * sr * sp + cr * sy
        output[i, 1, 1] = cr * cy - sr * sp * sy
        output[i, 1, 2] = -cp * sr
        output[i, 2, 0] = -cr * cy * sp + sr * sy
        output[i, 2, 1] = cy * sr + cr * sp * sy
        output[i, 2, 2] = cr * cp


@wp.kernel(enable_backward=False)
def _wk_quaternion_multiplication(a: wp.array(ndim=2), b: wp.array(ndim=2), output: wp.array(ndim=2)):
    """Multiply two quaternions using Hamilton product."""
    i = wp.tid()

    # Extract quaternion components [w, x, y, z]
    w1, x1, y1, z1 = a[i, 0], a[i, 1], a[i, 2], a[i, 3]
    w2, x2, y2, z2 = b[i, 0], b[i, 1], b[i, 2], b[i, 3]

    # Hamilton product formula
    ww = (z1 + x1) * (x2 + y2)
    yy = (w1 - y1) * (w2 + z2)
    zz = (w1 + y1) * (w2 - z2)
    xx = ww + yy + zz

    # Type-safe constants
    zero = w1 - w1  # Type-safe zero
    half = zero + output.dtype(0.5)  # Type-safe 0.5

    qq = half * (xx + (z1 - x1) * (x2 - y2))
    w = qq - ww + (z1 - y1) * (y2 - z2)
    x = qq - xx + (x1 + w1) * (x2 + w2)
    y = qq - yy + (w1 - x1) * (y2 + z2)
    z = qq - zz + (z1 + y1) * (w2 - x2)

    output[i, 0] = w
    output[i, 1] = x
    output[i, 2] = y
    output[i, 3] = z


@wp.kernel(enable_backward=False)
def _wk_quaternion_conjugate(q: wp.array(ndim=2), output: wp.array(ndim=2)):
    """Compute quaternion conjugate by negating the vector part."""
    i = wp.tid()

    # Quaternion conjugate: [w, -x, -y, -z]
    output[i, 0] = q[i, 0]  # w component unchanged
    output[i, 1] = -q[i, 1]  # negate x component
    output[i, 2] = -q[i, 2]  # negate y component
    output[i, 3] = -q[i, 3]  # negate z component


@wp.kernel(enable_backward=False)
def _wk_quaternion_to_rotation_matrix(quaternion: wp.array(ndim=2), output: wp.array(ndim=3)):
    """Convert quaternion to rotation matrix using standard formula."""
    i = wp.tid()

    # Extract quaternion components [w, x, y, z]
    w = quaternion[i, 0]
    x = quaternion[i, 1]
    y = quaternion[i, 2]
    z = quaternion[i, 3]

    # Type-safe constants
    zero = w - w  # Type-safe zero
    one = zero + output.dtype(1.0)  # Type-safe one using output dtype
    two = one + one  # Type-safe two

    # Compute squared components
    sqx = x * x
    sqy = y * y
    sqz = z * z
    sqw = w * w

    # Normalization factor
    s = one / (sqx + sqy + sqz + sqw)

    # Standard quaternion to rotation matrix formula
    output[i, 0, 0] = one - two * s * (sqy + sqz)
    output[i, 0, 1] = two * s * (x * y - z * w)
    output[i, 0, 2] = two * s * (x * z + y * w)
    output[i, 1, 0] = two * s * (x * y + z * w)
    output[i, 1, 1] = one - two * s * (sqx + sqz)
    output[i, 1, 2] = two * s * (y * z - x * w)
    output[i, 2, 0] = two * s * (x * z - y * w)
    output[i, 2, 1] = two * s * (y * z + x * w)
    output[i, 2, 2] = one - two * s * (sqx + sqy)
