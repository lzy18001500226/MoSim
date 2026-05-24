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

import math

import isaacsim.core.experimental.utils.transform as transform_utils
import numpy as np
import omni.kit.test
import warp as wp


class TestTransform(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        """Method called to prepare the test fixture"""
        super().setUp()
        # ---------------
        # Do custom setUp
        # ---------------
        self.tolerance = 1e-6

    async def tearDown(self):
        """Method called immediately after the test method has been called"""
        # ------------------
        # Do custom tearDown
        # ------------------
        super().tearDown()

    # --------------------------------------------------------------------

    async def test_rotation_matrix_to_quaternion(self):
        """Test rotation_matrix_to_quaternion with single and batch inputs"""
        # Test identity matrix with different input types
        identity_inputs = [
            np.eye(3),  # numpy
            wp.array(np.eye(3)),  # warp
        ]

        for identity in identity_inputs:
            result = transform_utils.rotation_matrix_to_quaternion(identity)

            # Check that result is a warp array
            self.assertIsInstance(result, wp.array)
            self.assertEqual(result.shape, (4,))

            # Identity should produce quaternion [1, 0, 0, 0] (w, x, y, z)
            result_np = result.numpy()
            expected = np.array([1.0, 0.0, 0.0, 0.0])
            self.assertTrue(np.allclose(result_np, expected, atol=self.tolerance))

        # Test batch of identity matrices
        batch = np.array([np.eye(3), np.eye(3)], dtype=np.float32)
        result_batch = transform_utils.rotation_matrix_to_quaternion(batch)

        # Check that result is a warp array with correct shape
        self.assertIsInstance(result_batch, wp.array)
        self.assertEqual(result_batch.shape, (2, 4))

        # Check that all quaternions are unit quaternions
        result_batch_np = result_batch.numpy()
        norms = np.linalg.norm(result_batch_np, axis=1)
        expected_norms = np.ones(2)
        self.assertTrue(np.allclose(norms, expected_norms, atol=self.tolerance))

    async def test_euler_angles_to_rotation_matrix(self):
        """Test euler_angles_to_rotation_matrix with single and batch inputs"""
        # Test zero rotation with different input types
        euler_inputs = [
            [0.0, 0.0, 0.0],  # list
            np.array([0.0, 0.0, 0.0]),  # numpy
            wp.array([0.0, 0.0, 0.0]),  # warp
        ]

        for euler in euler_inputs:
            result = transform_utils.euler_angles_to_rotation_matrix(euler)

            # Check that result is a warp array
            self.assertIsInstance(result, wp.array)
            self.assertEqual(result.shape, (3, 3))

            # Should produce identity matrix
            result_np = result.numpy()
            expected = np.eye(3)
            self.assertTrue(np.allclose(result_np, expected, atol=self.tolerance))

        # Test batch of zero rotations
        euler_batch = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], dtype=np.float32)
        result_batch = transform_utils.euler_angles_to_rotation_matrix(euler_batch)

        # Check that result is a warp array with correct shape
        self.assertIsInstance(result_batch, wp.array)
        self.assertEqual(result_batch.shape, (2, 3, 3))

        # Check that all matrices are orthogonal (det = 1)
        result_batch_np = result_batch.numpy()
        for i in range(2):
            det = np.linalg.det(result_batch_np[i])
            self.assertAlmostEqual(det, 1.0, places=5)

    async def test_euler_angles_to_quaternion(self):
        """Test euler_angles_to_quaternion with single and batch inputs"""
        # Test zero rotation with different input types
        euler_inputs = [
            [0.0, 0.0, 0.0],  # list
            np.array([0.0, 0.0, 0.0]),  # numpy
            wp.array([0.0, 0.0, 0.0]),  # warp
        ]

        for euler in euler_inputs:
            result = transform_utils.euler_angles_to_quaternion(euler)

            # Check that result is a warp array
            self.assertIsInstance(result, wp.array)
            self.assertEqual(result.shape, (4,))

            # Should produce identity quaternion [1, 0, 0, 0]
            result_np = result.numpy()
            expected = np.array([1.0, 0.0, 0.0, 0.0])
            self.assertTrue(np.allclose(result_np, expected, atol=self.tolerance))

        # Test batch of zero rotations
        euler_batch = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], dtype=np.float32)
        result_batch = transform_utils.euler_angles_to_quaternion(euler_batch)

        # Check that result is a warp array with correct shape
        self.assertIsInstance(result_batch, wp.array)
        self.assertEqual(result_batch.shape, (2, 4))

        # Check that all quaternions are unit quaternions
        result_batch_np = result_batch.numpy()
        norms = np.linalg.norm(result_batch_np, axis=1)
        expected_norms = np.ones(2)
        self.assertTrue(np.allclose(norms, expected_norms, atol=self.tolerance))

    async def test_degrees_vs_radians(self):
        """Test that degrees and radians produce consistent results"""
        # Test conversion consistency for zero rotation
        euler_deg = [0.0, 0.0, 0.0]
        euler_rad = [0.0, 0.0, 0.0]

        # Test rotation matrix
        result_deg = transform_utils.euler_angles_to_rotation_matrix(euler_deg, degrees=True)
        result_rad = transform_utils.euler_angles_to_rotation_matrix(euler_rad, degrees=False)

        self.assertTrue(np.allclose(result_deg.numpy(), result_rad.numpy(), atol=self.tolerance))

        # Test quaternion
        result_deg = transform_utils.euler_angles_to_quaternion(euler_deg, degrees=True)
        result_rad = transform_utils.euler_angles_to_quaternion(euler_rad, degrees=False)

        self.assertTrue(np.allclose(result_deg.numpy(), result_rad.numpy(), atol=self.tolerance))

    async def test_basic_mathematical_properties(self):
        """Test basic mathematical properties of the results"""
        # Test identity rotation
        euler = [0.0, 0.0, 0.0]

        # Test rotation matrix properties
        rotation_matrix = transform_utils.euler_angles_to_rotation_matrix(euler)
        R = rotation_matrix.numpy()

        # Check that it's close to identity
        identity = np.eye(3)
        self.assertTrue(np.allclose(R, identity, atol=self.tolerance))

        # Check determinant is 1
        det = np.linalg.det(R)
        self.assertAlmostEqual(det, 1.0, places=5)

        # Test quaternion properties
        quaternion = transform_utils.euler_angles_to_quaternion(euler)
        q = quaternion.numpy()

        # Check that it's a unit quaternion
        norm = np.linalg.norm(q)
        self.assertAlmostEqual(norm, 1.0, places=5)

    async def test_quaternion_multiplication(self):
        """Test quaternion_multiplication with single and batch inputs"""
        # Test identity quaternion multiplication with different input types
        quaternion_inputs = [
            [1.0, 0.0, 0.0, 0.0],  # list
            np.array([1.0, 0.0, 0.0, 0.0]),  # numpy
            wp.array([1.0, 0.0, 0.0, 0.0]),  # warp
        ]

        for quaternion in quaternion_inputs:
            result = transform_utils.quaternion_multiplication(quaternion, quaternion)

            # Check that result is a warp array
            self.assertIsInstance(result, wp.array)
            self.assertEqual(result.shape, (4,))

            # Identity * Identity should be identity
            result_numpy = result.numpy()
            expected = np.array([1.0, 0.0, 0.0, 0.0])
            self.assertTrue(np.allclose(result_numpy, expected, atol=self.tolerance))

        # Test batch of identity quaternions
        identity_batch = np.array([[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        result_batch = transform_utils.quaternion_multiplication(identity_batch, identity_batch)

        # Check that result is a warp array with correct shape
        self.assertIsInstance(result_batch, wp.array)
        self.assertEqual(result_batch.shape, (2, 4))

        # Check that all results are unit quaternions
        result_batch_numpy = result_batch.numpy()
        norms = np.linalg.norm(result_batch_numpy, axis=1)
        expected_norms = np.ones(2)
        self.assertTrue(np.allclose(norms, expected_norms, atol=self.tolerance))

    async def test_quaternion_conjugate(self):
        """Test quaternion_conjugate with single and batch inputs"""
        # Test with a rotation around X axis using different input types
        quaternion_inputs = [
            [0.7071, 0.7071, 0.0, 0.0],  # list
            np.array([0.7071, 0.7071, 0.0, 0.0]),  # numpy
            wp.array([0.7071, 0.7071, 0.0, 0.0]),  # warp
        ]

        for quaternion in quaternion_inputs:
            result = transform_utils.quaternion_conjugate(quaternion)

            # Check that result is a warp array
            self.assertIsInstance(result, wp.array)
            self.assertEqual(result.shape, (4,))

            # Conjugate should negate vector components
            result_numpy = result.numpy()
            expected = np.array([0.7071, -0.7071, 0.0, 0.0])
            self.assertTrue(np.allclose(result_numpy, expected, atol=self.tolerance))

        # Test batch of rotations
        quaternion_batch = np.array(
            [[0.7071, 0.7071, 0.0, 0.0], [0.7071, 0.0, 0.7071, 0.0]],  # 90 degrees around X  # 90 degrees around Y
            dtype=np.float32,
        )
        result_batch = transform_utils.quaternion_conjugate(quaternion_batch)

        # Check that result is a warp array with correct shape
        self.assertIsInstance(result_batch, wp.array)
        self.assertEqual(result_batch.shape, (2, 4))

        # Check that all results are unit quaternions
        result_batch_numpy = result_batch.numpy()
        norms = np.linalg.norm(result_batch_numpy, axis=1)
        expected_norms = np.ones(2)
        self.assertTrue(np.allclose(norms, expected_norms, atol=self.tolerance))

    async def test_quaternion_to_rotation_matrix(self):
        """Test quaternion_to_rotation_matrix with single and batch inputs, including round-trip validation"""
        # Test identity quaternion with different input types
        quaternion_inputs = [
            [1.0, 0.0, 0.0, 0.0],  # list
            np.array([1.0, 0.0, 0.0, 0.0]),  # numpy
            wp.array([1.0, 0.0, 0.0, 0.0]),  # warp
        ]

        for quaternion in quaternion_inputs:
            result = transform_utils.quaternion_to_rotation_matrix(quaternion)

            # Check that result is a warp array
            self.assertIsInstance(result, wp.array)
            self.assertEqual(result.shape, (3, 3))

            # Identity quaternion should produce identity matrix
            result_numpy = result.numpy()
            expected = np.eye(3)
            self.assertTrue(np.allclose(result_numpy, expected, atol=self.tolerance))

        # Test batch of identity quaternions
        identity_batch = np.array([[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        result_batch = transform_utils.quaternion_to_rotation_matrix(identity_batch)

        # Check that result is a warp array with correct shape
        self.assertIsInstance(result_batch, wp.array)
        self.assertEqual(result_batch.shape, (2, 3, 3))

        # Check that all matrices are orthogonal (det = 1)
        result_batch_numpy = result_batch.numpy()
        for i in range(2):
            det = np.linalg.det(result_batch_numpy[i])
            self.assertAlmostEqual(det, 1.0, places=5)

        # Test round-trip conversion: quaternion -> matrix -> quaternion
        quaternion = [0.7071, 0.7071, 0.0, 0.0]  # 90 degrees around X

        # Convert to rotation matrix
        rotation_matrix = transform_utils.quaternion_to_rotation_matrix(quaternion)

        # Convert back to quaternion
        quaternion_back = transform_utils.rotation_matrix_to_quaternion(rotation_matrix)

        # Results should be approximately equal (allowing for sign differences)
        original_np = np.array(quaternion)
        back_np = quaternion_back.numpy()

        # Check that either the quaternions are equal or one is the negative of the other
        # (both represent the same rotation)
        self.assertTrue(
            np.allclose(original_np, back_np, atol=self.tolerance)
            or np.allclose(original_np, -back_np, atol=self.tolerance)
        )

        # Test round-trip conversion with batch of quaternions
        quaternion_batch = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],  # Identity
                [0.7071, 0.7071, 0.0, 0.0],  # 90 degrees around X
                [0.7071, 0.0, 0.7071, 0.0],  # 90 degrees around Y
                [0.7071, 0.0, 0.0, 0.7071],  # 90 degrees around Z
            ],
            dtype=np.float32,
        )

        # Convert to rotation matrices
        rotation_matrices = transform_utils.quaternion_to_rotation_matrix(quaternion_batch)

        # Convert back to quaternions
        quaternions_back = transform_utils.rotation_matrix_to_quaternion(rotation_matrices)

        # Check that all roundtrip conversions are valid
        original_np = quaternion_batch
        back_np = quaternions_back.numpy()

        for i in range(4):
            # Check that either the quaternions are equal or one is the negative of the other
            self.assertTrue(
                np.allclose(original_np[i], back_np[i], atol=self.tolerance)
                or np.allclose(original_np[i], -back_np[i], atol=self.tolerance)
            )

        # Test mathematical properties of quaternion_to_rotation_matrix results
        quaternion = [0.7071, 0.7071, 0.0, 0.0]  # 90 degrees around X
        result = transform_utils.quaternion_to_rotation_matrix(quaternion)
        R = result.numpy()

        # Check that it's a valid rotation matrix
        # 1. Determinant should be 1
        det = np.linalg.det(R)
        self.assertAlmostEqual(det, 1.0, places=5)

        # 2. Should be orthogonal (R * R^T = I)
        R_transpose = R.T
        identity = np.eye(3)
        self.assertTrue(np.allclose(np.dot(R, R_transpose), identity, atol=self.tolerance))

        # 3. Check specific values for 90-degree X rotation
        expected = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]])
        self.assertTrue(np.allclose(R, expected, atol=self.tolerance))

    async def test_quaternion_multiplication_associativity(self):
        """Test that quaternion multiplication is associative"""
        # Test (first_quaternion * second_quaternion) * third_quaternion = first_quaternion * (second_quaternion * third_quaternion)
        first_quaternion = np.array([0.7071, 0.7071, 0.0, 0.0])  # 90 deg around X
        second_quaternion = np.array([0.7071, 0.0, 0.7071, 0.0])  # 90 deg around Y
        third_quaternion = np.array([0.7071, 0.0, 0.0, 0.7071])  # 90 deg around Z

        # Compute (first_quaternion * second_quaternion) * third_quaternion
        quaternion_first_second = transform_utils.quaternion_multiplication(first_quaternion, second_quaternion)
        quaternion_result_left = transform_utils.quaternion_multiplication(quaternion_first_second, third_quaternion)

        # Compute first_quaternion * (second_quaternion * third_quaternion)
        quaternion_second_third = transform_utils.quaternion_multiplication(second_quaternion, third_quaternion)
        quaternion_result_right = transform_utils.quaternion_multiplication(first_quaternion, quaternion_second_third)

        # Results should be equal
        self.assertTrue(
            np.allclose(quaternion_result_left.numpy(), quaternion_result_right.numpy(), atol=self.tolerance)
        )
