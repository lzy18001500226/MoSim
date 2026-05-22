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

import json
import os

import carb
import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.usd


def compare_json_dicts_recursive(data1, data2, path=""):
    if isinstance(data1, (list, tuple)) and isinstance(data2, (list, tuple)):
        if len(data1) != len(data2):
            return f"Length mismatch at {path}: {len(data1)} != {len(data2)}"
        if any(isinstance(x, float) for x in data1 + data2):
            try:
                np.testing.assert_allclose(data1, data2, rtol=1e-5, atol=1e-5)
            except AssertionError:
                return f"Value mismatch at {path}: {data1} != {data2}"
        else:
            for i, (v1, v2) in enumerate(zip(data1, data2)):
                error = compare_json_dicts_recursive(v1, v2, f"{path}[{i}]")
                if error:
                    return error
    elif isinstance(data1, dict) and isinstance(data2, dict):
        keys1, keys2 = set(data1.keys()), set(data2.keys())
        if keys1 != keys2:
            extra1 = keys1 - keys2
            extra2 = keys2 - keys1
            msg = []
            if extra1:
                msg.append(f"Extra keys in first dict at {path}: {extra1}")
            if extra2:
                msg.append(f"Extra keys in second dict at {path}: {extra2}")
            return "\n".join(msg)
        for key in keys1:
            # If quaternion, compare it with its negated quaternion as well since it represents the same rotation
            if (
                "quat" in key
                and isinstance(data1[key], list)
                and isinstance(data2[key], list)
                and len(data1[key]) == 4
                and len(data2[key]) == 4
            ):
                q1 = np.array(data1[key])
                q2 = np.array(data2[key])
                try:
                    np.testing.assert_allclose(q1, q2, rtol=1e-5, atol=1e-5)
                except AssertionError:
                    try:
                        np.testing.assert_allclose(q1, -q2, rtol=1e-5, atol=1e-5)
                    except AssertionError:
                        return f"Quaternion mismatch at {path}.{key}: {data1[key]} != {data2[key]} (and not negative of each other)"
            else:
                error = compare_json_dicts_recursive(data1[key], data2[key], f"{path}.{key}" if path else key)
                if error:
                    return error
    elif isinstance(data1, float) and isinstance(data2, float):
        try:
            np.testing.assert_allclose(data1, data2, rtol=1e-5, atol=1e-5)
        except AssertionError:
            return f"Float mismatch at {path}: {data1} != {data2}"
    elif data1 != data2:
        return f"Value mismatch at {path}: {data1} != {data2}"
    return None


class TestPoseWriter(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_pose_writer(self):
        # Setup stage
        await omni.usd.get_context().new_stage_async()
        rep.create.light(light_type="dome", intensity=500)
        rep.create.cube(scale=(1, 1, 1), semantics=[("class", "cube")], position=(0, 0, 0), rotation=(0, 0, 0))
        rep.create.cube(
            scale=(1, 1, 1), semantics=[("class", "cube_rotated")], position=(-1, -1, 0), rotation=(0, 0, 45)
        )
        rep.create.cube(
            scale=(1.5, 0.5, 1), semantics=[("class", "cube_scaled")], position=(1, 1, 0), rotation=(75, 65, 0)
        )

        # Create render products
        cam1 = rep.create.camera(position=(0, 0, 10), look_at=(0, 0, 0), name="cam1")
        cam2 = rep.create.camera(position=(-4, -4, 8), look_at=(0, 0, 0), name="cam2")
        rp1 = rep.create.render_product(cam1, (512, 512), name="rp1")
        rp2 = rep.create.render_product(cam2, (512, 512), name="rp2")
        render_products = [rp1, rp2]

        # Setup writer
        # out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_pose_writer")
        out_dir = os.path.join(os.getcwd(), "test_pose_writer")
        writer = rep.writers.get("PoseWriter")
        writer.initialize(output_dir=out_dir, use_subfolders=True, write_debug_images=True)
        writer.attach(render_products)

        # Capture data
        await rep.orchestrator.step_async()
        await rep.orchestrator.wait_until_complete_async()

        # Golden json file paths
        golden_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "golden", "out_pose_writer")
        golden_rp1_json = os.path.join(golden_dir, "rp1", "000000.json")
        golden_rp2_json = os.path.join(golden_dir, "rp2", "000000.json")
        self.assertTrue(os.path.exists(golden_rp1_json), f"Golden file {golden_rp1_json} does not exist")
        self.assertTrue(os.path.exists(golden_rp2_json), f"Golden file {golden_rp2_json} does not exist")

        # Output json file paths
        rp1_json = os.path.join(out_dir, "rp1", "000000.json")
        rp2_json = os.path.join(out_dir, "rp2", "000000.json")
        self.assertTrue(os.path.exists(rp1_json), f"Output file {rp1_json} does not exist")
        self.assertTrue(os.path.exists(rp2_json), f"Output file {rp2_json} does not exist")

        # Compare the json golden output with the output for the two render products
        with open(golden_rp1_json, "r") as f:
            golden_rp1_data = json.load(f)
        with open(rp1_json, "r") as f:
            rp1_data = json.load(f)
        error = compare_json_dicts_recursive(rp1_data, golden_rp1_data)
        self.assertIsNone(error, f"'/rp1' comparison failed:\n{error}")

        with open(golden_rp2_json, "r") as f:
            golden_rp2_data = json.load(f)
        with open(rp2_json, "r") as f:
            rp2_data = json.load(f)
        error = compare_json_dicts_recursive(rp2_data, golden_rp2_data)
        self.assertIsNone(error, f"'/rp2' comparison failed:\n{error}")

        # Clean up
        writer.detach()
        for rp in render_products:
            rp.destroy()
            rp = None
        render_products = None
        await omni.usd.get_context().close_stage_async()
