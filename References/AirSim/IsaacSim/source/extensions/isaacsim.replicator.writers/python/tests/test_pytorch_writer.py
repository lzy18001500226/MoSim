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

import os
import unittest
from pathlib import Path

import carb
import numpy as np
import omni.kit
import omni.replicator.core as rep
import omni.usd
import torch
from isaacsim.core.utils.stage import create_new_stage_async
from isaacsim.replicator.writers import PytorchListener
from PIL import Image


class TestMultipleRenderProducts(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        # Create new stage
        await omni.kit.app.get_app().next_update_async()
        await create_new_stage_async()

        # Create camera and render products
        render_product1 = rep.create.render_product(rep.create.camera(position=(0, 0, 1000)), (512, 512))
        render_product2 = rep.create.render_product(rep.create.camera(position=(100, 100, 1000)), (512, 512))
        render_product3 = rep.create.render_product(rep.create.camera(position=(200, -100, 1000)), (512, 512))
        self.render_products = [render_product1, render_product2, render_product3]

        stage = omni.usd.get_context().get_stage()

        # Setup scene with randomized shapes
        torus = rep.create.torus(semantics=[("class", "torus"), ("alias", "donut")])
        sphere = rep.create.sphere(semantics=[("class", "sphere"), ("alias", "ball")])
        cube = rep.create.cube(semantics=[("class", "cube")])

        test_seed = 2134
        with rep.trigger.on_frame():
            with rep.create.group([torus, sphere, cube]):
                rep.modify.pose(
                    position=rep.distribution.uniform((-100, -100, -100), (200, 200, 200), seed=test_seed),
                    scale=rep.distribution.uniform(0.1, 2, seed=test_seed),
                )
                rep.randomizer.rotation(seed=test_seed)

        # Output directory for backend writing
        self.out_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_pytorch_writer")
        os.makedirs(self.out_dir, exist_ok=True)

        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        for rp in self.render_products:
            rp.destroy()
            rp = None
            await omni.kit.app.get_app().next_update_async()
        self.render_products = None
        await omni.kit.app.get_app().next_update_async()
        omni.usd.get_context().close_stage()

    async def _run_until_stopped(self):
        await rep.orchestrator.run_until_complete_async(num_frames=10)

    async def test_single_camera_writer_without_backend(self):
        render_products = self.render_products[1:2]
        pytorch_listener = PytorchListener()
        pytorch_writer = rep.WriterRegistry.get("PytorchWriter")
        pytorch_writer.initialize(listener=pytorch_listener, device="cpu")
        pytorch_writer.attach(render_products)

        await self._run_until_stopped()

        image = pytorch_listener.get_rgb_data()
        self.assertTrue(image.device.type == "cpu")
        self.assertTrue([*image.shape] == [1, 3, 512, 512])
        pytorch_writer.detach()
        pytorch_listener = None

    async def test_single_camera_writer_with_backend(self):
        render_products = self.render_products[0:1]
        pytorch_listener = PytorchListener()
        pytorch_writer = rep.WriterRegistry.get("PytorchWriter")

        out_dir = os.path.join(self.out_dir, "single_cam")

        pytorch_writer.initialize(output_dir=out_dir, listener=pytorch_listener, device="cpu")
        pytorch_writer.attach(render_products)

        await self._run_until_stopped()

        image = pytorch_listener.get_rgb_data()
        file_path = os.path.join(out_dir, "rgb_9_LdrColor.png")
        self.assertTrue(Path(file_path).exists())

        # convert arrays/tensors to (W, H, R) format
        file_image = np.asarray(Image.open(file_path))[:, :, :3]
        torch_to_numpy = image.numpy().transpose(0, 2, 3, 1).squeeze()

        self.assertTrue((file_image == torch_to_numpy).all())
        pytorch_writer.detach()
        pytorch_listener = None

    async def test_multiple_cameras_writer_without_backend(self):
        render_products = self.render_products
        pytorch_listener = PytorchListener()
        pytorch_writer = rep.WriterRegistry.get("PytorchWriter")
        pytorch_writer.initialize(listener=pytorch_listener, device="cpu")
        pytorch_writer.attach(render_products)

        await self._run_until_stopped()

        images = pytorch_listener.get_rgb_data()
        self.assertTrue(images.device.type == "cpu")
        self.assertTrue([*images.shape] == [3, 3, 512, 512])
        pytorch_writer.detach()
        pytorch_listener = None

    async def test_multiple_cameras_writer_with_backend(self):
        render_products = self.render_products
        pytorch_listener = PytorchListener()
        pytorch_writer = rep.WriterRegistry.get("PytorchWriter")

        out_dir = os.path.join(self.out_dir, "multi_cam")

        pytorch_writer.initialize(output_dir=out_dir, listener=pytorch_listener, device="cpu")
        pytorch_writer.attach(render_products)

        await self._run_until_stopped()

        image = pytorch_listener.get_rgb_data()
        file_paths = []
        rp_prefix = carb.settings.get_settings().get_as_string("/exts/omni.kit.hydra_texture/renderProduct/path/prefix")
        for rp in render_products:
            name = rp.path.split(rp_prefix)[-1]
            path = os.path.join(out_dir, f"rgb_9_{name}.png")
            file_paths.append(path)
            self.assertTrue(Path(path).exists())

        # convert arrays/tensors to (Batches, W, H, R) format

        file_image_one = np.expand_dims(np.asarray(Image.open(file_paths[0]))[:, :, :3], axis=0)
        file_image_two = np.expand_dims(np.asarray(Image.open(file_paths[1]))[:, :, :3], axis=0)
        file_image_three = np.expand_dims(np.asarray(Image.open(file_paths[2]))[:, :, :3], axis=0)

        concatenated_images = np.concatenate((file_image_one, file_image_two, file_image_three), axis=0)
        torch_to_numpy = image.numpy().transpose(0, 2, 3, 1)

        self.assertTrue((concatenated_images == torch_to_numpy).all())
        pytorch_writer.detach()
        pytorch_listener = None

    @unittest.skipIf(torch.cuda.is_available() == False, "GPU is not available on this machine!")
    async def test_single_camera_writer_with_gpu(self):
        render_products = self.render_products[2:3]
        pytorch_listener = PytorchListener()
        pytorch_writer = rep.WriterRegistry.get("PytorchWriter")
        pytorch_writer.initialize(listener=pytorch_listener, device="cuda")
        pytorch_writer.attach(render_products)

        await self._run_until_stopped()

        image = pytorch_listener.get_rgb_data()
        self.assertTrue(image.device.type == "cuda")
        self.assertTrue([*image.shape] == [1, 3, 512, 512])
        pytorch_writer.detach()
        pytorch_listener = None

    @unittest.skipIf(torch.cuda.is_available() == False, "GPU is not available on this machine!")
    async def test_multiple_cameras_writer_with_gpu(self):
        render_products = self.render_products
        pytorch_listener = PytorchListener()
        pytorch_writer = rep.WriterRegistry.get("PytorchWriter")
        pytorch_writer.initialize(listener=pytorch_listener, device="cuda")
        pytorch_writer.attach(render_products)

        await self._run_until_stopped()

        images = pytorch_listener.get_rgb_data()
        self.assertTrue(images.device.type == "cuda")
        self.assertTrue([*images.shape] == [3, 3, 512, 512])
        pytorch_writer.detach()
        pytorch_listener = None
