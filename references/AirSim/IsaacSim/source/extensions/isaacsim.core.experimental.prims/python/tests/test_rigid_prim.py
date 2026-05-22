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

from typing import Literal

import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
import omni.kit.test
import warp as wp
from isaacsim.core.experimental.prims import RigidPrim
from isaacsim.core.experimental.utils.backend import use_backend

from .common import check_allclose, check_array, cprint, draw_indices, draw_sample, parametrize


async def populate_stage(max_num_prims: int, operation: Literal["wrap", "create"], **kwargs) -> None:
    assert operation == "wrap", "Other operations except 'wrap' are not supported"
    # create new stage
    await stage_utils.create_new_stage_async()
    # define prims
    stage_utils.define_prim(f"/World", "Xform")
    stage_utils.define_prim(f"/World/PhysicsScene", "PhysicsScene")
    for i in range(max_num_prims):
        stage_utils.define_prim(f"/World/A_{i}", "Xform")
        stage_utils.define_prim(f"/World/A_{i}/B", "Cube")


class TestRigidPrim(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        """Method called to prepare the test fixture"""
        super().setUp()

    async def tearDown(self):
        """Method called immediately after the test method has been called"""
        super().tearDown()

    # --------------------------------------------------------------------

    def check_backend(self, backend, prim):
        if backend == "tensor":
            self.assertTrue(prim.is_physics_tensor_entity_valid(), f"Tensor API should be enabled ({backend})")
        elif backend in ["usd", "usdrt", "fabric"]:
            self.assertFalse(prim.is_physics_tensor_entity_valid(), f"Tensor API should be disabled ({backend})")
        else:
            raise ValueError(f"Invalid backend: {backend}")

    # --------------------------------------------------------------------

    @parametrize(
        backends=["tensor", "usd"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_len(self, prim, num_prims, device, backend):
        self.assertEqual(len(prim), num_prims, f"Invalid RigidPrim ({num_prims} prims) len")

    @parametrize(
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_world_poses(self, prim, num_prims, device, backend):
        # check backend and define USD usage
        self.check_backend(backend, prim)
        if backend in ["usdrt", "fabric"]:
            await omni.kit.app.get_app().next_update_async()
        elif backend == "usd":
            prim.reset_xform_op_properties()
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for (v0, expected_v0), (v1, expected_v1) in zip(
                draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                draw_sample(shape=(expected_count, 4), dtype=wp.float32, normalized=True),
            ):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_world_poses(v0, v1, indices=indices)
                    output = prim.get_world_poses(indices=indices)
                check_array(output[0], shape=(expected_count, 3), dtype=wp.float32, device=device)
                check_array(output[1], shape=(expected_count, 4), dtype=wp.float32, device=device)
                check_allclose((expected_v0, expected_v1), output, given=(v0, v1))

    @parametrize(
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_local_poses(self, prim, num_prims, device, backend):
        # check backend and define USD usage
        self.check_backend(backend, prim)
        if backend in ["usdrt", "fabric"]:
            await omni.kit.app.get_app().next_update_async()
        elif backend == "usd":
            prim.reset_xform_op_properties()
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for (v0, expected_v0), (v1, expected_v1) in zip(
                draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                draw_sample(shape=(expected_count, 4), dtype=wp.float32, normalized=True),
            ):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_local_poses(v0, v1, indices=indices)
                    output = prim.get_local_poses(indices=indices)
                check_array(output[0], shape=(expected_count, 3), dtype=wp.float32, device=device)
                check_array(output[1], shape=(expected_count, 4), dtype=wp.float32, device=device)
                check_allclose((expected_v0, expected_v1), output, given=(v0, v1))

    @parametrize(
        backends=["tensor", "usd"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_velocities(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for (v0, expected_v0), (v1, expected_v1) in zip(
                draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                draw_sample(shape=(expected_count, 3), dtype=wp.float32),
            ):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_velocities(v0, v1, indices=indices)
                    output = prim.get_velocities(indices=indices)
                check_array(output, shape=(expected_count, 3), dtype=wp.float32, device=device)
                check_allclose((expected_v0, expected_v1), output, given=(v0, v1))

    @parametrize(
        backends=["tensor", "usd"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_masses(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for v0, expected_v0 in draw_sample(shape=(expected_count, 1), dtype=wp.float32):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_masses(v0, indices=indices)
                    output = prim.get_masses(indices=indices)
                    inverse_output = prim.get_masses(indices=indices, inverse=True)
                check_array((output, inverse_output), shape=(expected_count, 1), dtype=wp.float32, device=device)
                check_allclose(expected_v0, output, given=(v0,))
                expected_inverse = 1.0 / (output.numpy() + 1e-8)
                check_allclose(expected_inverse, inverse_output, given=(v0,))

    @parametrize(
        backends=["tensor", "usd"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_enabled_rigid_bodies(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for v0, expected_v0 in draw_sample(shape=(expected_count, 1), dtype=wp.bool):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_enabled_rigid_bodies(v0, indices=indices)
                    output = prim.get_enabled_rigid_bodies(indices=indices)
                check_array(output, shape=(expected_count, 1), dtype=wp.bool, device=device)
                check_allclose(expected_v0, output, given=(v0,))

    @parametrize(
        backends=["tensor", "usd"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_enabled_gravities(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for v0, expected_v0 in draw_sample(shape=(expected_count, 1), dtype=wp.bool):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_enabled_gravities(v0, indices=indices)
                    output = prim.get_enabled_gravities(indices=indices)
                check_array(output, shape=(expected_count, 1), dtype=wp.bool, device=device)
                check_allclose(expected_v0, output, given=(v0,))

    @parametrize(
        backends=["tensor"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_coms(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for (v0, expected_v0), (v1, expected_v1) in zip(
                draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                draw_sample(shape=(expected_count, 4), dtype=wp.float32, normalized=True),
            ):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_coms(v0, v1, indices=indices)
                    output = prim.get_coms(indices=indices)
                check_array(output[0], shape=(expected_count, 3), dtype=wp.float32, device=device)
                check_array(output[1], shape=(expected_count, 4), dtype=wp.float32, device=device)
                check_allclose((expected_v0, expected_v1), output, given=(v0, v1))

    @parametrize(
        backends=["tensor"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_inertias(self, prim, num_prims, device, backend):
        def _transform(x):  # transform to a diagonal inertia matrix
            x[:, [1, 2, 3, 5, 6, 7]] = 0.0
            return x

        # check backend
        self.check_backend(backend, prim)
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for v0, expected_v0 in draw_sample(shape=(expected_count, 9), dtype=wp.float32, transform=_transform):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_inertias(v0, indices=indices)
                    output = prim.get_inertias(indices=indices)
                    inverse_output = prim.get_inertias(indices=indices, inverse=True)
                check_array((output, inverse_output), shape=(expected_count, 9), dtype=wp.float32, device=device)
                check_allclose(expected_v0, output, given=(v0,))
                expected_inverse = np.linalg.inv(output.numpy().reshape((-1, 3, 3))).reshape((expected_count, 9))
                check_allclose(expected_inverse, inverse_output, given=(v0,))

    @parametrize(
        backends=["usd"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_densities(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for v0, expected_v0 in draw_sample(shape=(expected_count, 1), dtype=wp.float32):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_densities(v0, indices=indices)
                    output = prim.get_densities(indices=indices)
                check_array(output, shape=(expected_count, 1), dtype=wp.float32, device=device)
                check_allclose(expected_v0, output, given=(v0,))

    @parametrize(
        backends=["usd"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_sleep_thresholds(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for v0, expected_v0 in draw_sample(shape=(expected_count, 1), dtype=wp.float32):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_sleep_thresholds(v0, indices=indices)
                    output = prim.get_sleep_thresholds(indices=indices)
                check_array(output, shape=(expected_count, 1), dtype=wp.float32, device=device)
                check_allclose(expected_v0, output, given=(v0,))

    @parametrize(
        backends=["tensor", "usd"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_default_state(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)
        if backend == "usd":
            prim.reset_xform_op_properties()
        # test cases
        for indices, expected_count in draw_indices(count=num_prims, step=2):
            cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
            for (v0, expected_v0), (v1, expected_v1), (v2, expected_v2), (v3, expected_v3) in zip(
                draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                draw_sample(shape=(expected_count, 4), dtype=wp.float32, normalized=True),
                draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                draw_sample(shape=(expected_count, 3), dtype=wp.float32),
            ):
                with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                    prim.set_default_state(v0, v1, v2, v3, indices=indices)
                    output = prim.get_default_state(indices=indices)
                    prim.reset_to_default_state()
                check_array(output[0], shape=(expected_count, 3), dtype=wp.float32, device=device)
                check_array(output[1], shape=(expected_count, 4), dtype=wp.float32, device=device)
                check_array(output[2:], shape=(expected_count, 3), dtype=wp.float32, device=device)
                check_allclose((expected_v0, expected_v1, expected_v2, expected_v3), output, given=(v0, v1, v2, v3))

    @parametrize(
        backends=["tensor"],
        operations=["wrap"],
        prim_class=RigidPrim,
        prim_class_kwargs={"masses": [1.0]},
        populate_stage_func=populate_stage,
    )
    async def test_apply_forces(self, prim, num_prims, device, backend):
        # check backend
        self.check_backend(backend, prim)

        # test cases (forces)
        for local_frame in [True, False]:
            # - all
            for indices, expected_count in draw_indices(count=num_prims, step=2):
                cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
                for v0, _ in draw_sample(shape=(expected_count, 3), dtype=wp.float32):
                    with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                        prim.apply_forces(v0, indices=indices, local_frame=local_frame)

        # test cases (forces and torques at positions)
        for local_frame in [True, False]:
            # - all
            for indices, expected_count in draw_indices(count=num_prims, step=2):
                cprint(f"  |    |-- indices: {type(indices).__name__}, expected_count: {expected_count}")
                for (v0, _), (v1, _), (positions, _) in zip(
                    draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                    draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                    draw_sample(shape=(expected_count, 3), dtype=wp.float32),
                ):
                    with use_backend(backend, raise_on_unsupported=True, raise_on_fallback=True):
                        prim.apply_forces_and_torques_at_pos(
                            v0, v1, positions=positions, indices=indices, local_frame=local_frame
                        )
