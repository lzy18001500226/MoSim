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

import asyncio
import os

import carb
import cv2
import isaacsim.core.utils.numpy.rotations as rot_utils
import numpy as np
import omni
import omni.kit.test
import omni.replicator.core as rep
from isaacsim.core.api import World
from isaacsim.core.api.objects import VisualCone, VisualCuboid
from isaacsim.core.utils.stage import create_new_stage_async, update_stage_async
from isaacsim.sensors.camera import SingleViewDepthSensor
from isaacsim.sensors.camera.tests.utils import compare_images, save_image
from isaacsim.storage.native import get_assets_root_path_async

SAVE_IMAGE_AS_TEST = False
SAVE_IMAGE_AS_GOLDEN = False
IMG_COMPARISON_TOLERANCE = 0.94

SUPPORTED_ANNOTATORS = [
    "DepthSensorDistance",
    "DepthSensorPointCloudPosition",
    "DepthSensorPointCloudColor",
    "DepthSensorImager",
]


class TestSingleViewDepthSensor(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):

        await create_new_stage_async()
        self.my_world = World(stage_units_in_meters=1.0)
        await self.my_world.initialize_simulation_context_async()
        self.my_world.scene.add_default_ground_plane()

        # Add two cubes and a cone
        self.cube_1 = self.my_world.scene.add(
            VisualCuboid(
                prim_path="/cube_1",
                name="cube_1",
                position=np.array([0.25, 0.25, 0.25]),
                scale=np.array([0.5, 0.5, 0.5]),
                size=1.0,
                color=np.array([255, 0, 0]),
            )
        )
        self.cube_2 = self.my_world.scene.add(
            VisualCuboid(
                prim_path="/cube_2",
                name="cube_2",
                position=np.array([-1.0, -1.0, 0.25]),
                scale=np.array([1.0, 1.0, 1.0]),
                size=1.0,
                color=np.array([0, 0, 255]),
            )
        )
        self.cone = self.my_world.scene.add(
            VisualCone(
                prim_path="/cone",
                name="cone",
                position=np.array([-0.1, -0.3, 0.2]),
                scale=np.array([1.0, 1.0, 1.0]),
                color=np.array([0, 255, 0]),
            )
        )

        self.camera = SingleViewDepthSensor(
            prim_path="/World/camera",
            name="depth_camera",
            position=np.array([3.0, 0.0, 0.6]),
            orientation=rot_utils.euler_angles_to_quats(np.array([0, 0, 180]), degrees=True),
            frequency=20,
            resolution=(1920, 1080),
        )

        await self.my_world.reset_async()
        # Warmup
        for _ in range(20):
            await update_stage_async()

        self.golden_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "golden")
        self.test_dir = carb.tokens.get_tokens_interface().resolve("${temp}/test_camera_view_sensor")

        return

    # After running each test
    async def tearDown(self):
        # self.camera = None
        self.my_world.clear_instance()
        await omni.kit.app.get_app().next_update_async()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(0.25)
        await omni.kit.app.get_app().next_update_async()
        return

    async def test_getter_setter_methods(self):
        """Test the getter and setter methods of the SingleViewDepthSensor."""
        # Before initialization, getters should return None
        self.assertIsNone(self.camera.get_baseline_mm())
        self.assertIsNone(self.camera.get_confidence_threshold())
        self.assertIsNone(self.camera.get_enabled())
        self.assertIsNone(self.camera.get_focal_length_pixel())
        self.assertIsNone(self.camera.get_max_disparity_pixel())
        self.assertIsNone(self.camera.get_max_distance())
        self.assertIsNone(self.camera.get_min_distance())
        self.assertIsNone(self.camera.get_noise_downscale_factor_pixel())
        self.assertIsNone(self.camera.get_noise_mean())
        self.assertIsNone(self.camera.get_noise_sigma())
        self.assertIsNone(self.camera.get_rgb_depth_output_mode())
        self.assertIsNone(self.camera.get_sensor_size_pixel())
        self.assertIsNone(self.camera.get_show_distance())

        # Initialize the camera
        self.camera.initialize()
        await update_stage_async()

        # After initialization, getters should return default values
        self.assertAlmostEqual(self.camera.get_baseline_mm(), 55.0)
        self.assertAlmostEqual(self.camera.get_confidence_threshold(), 0.95)
        self.assertTrue(self.camera.get_enabled())
        self.assertAlmostEqual(self.camera.get_focal_length_pixel(), 897.0)
        self.assertAlmostEqual(self.camera.get_max_disparity_pixel(), 110.0)
        self.assertAlmostEqual(self.camera.get_max_distance(), 10000000.0)
        self.assertAlmostEqual(self.camera.get_min_distance(), 0.5)
        self.assertAlmostEqual(self.camera.get_noise_downscale_factor_pixel(), 1.0)
        self.assertAlmostEqual(self.camera.get_noise_mean(), 0.25)
        self.assertAlmostEqual(self.camera.get_noise_sigma(), 0.25)
        self.assertEqual(self.camera.get_outlier_removal_enabled(), 3)
        self.assertEqual(self.camera.get_rgb_depth_output_mode(), 0)
        self.assertEqual(self.camera.get_sensor_size_pixel(), 1280)
        self.assertFalse(self.camera.get_show_distance())

        # Test setters with new values
        self.camera.set_baseline_mm(60.0)
        self.assertAlmostEqual(self.camera.get_baseline_mm(), 60.0)

        self.camera.set_confidence_threshold(0.8)
        self.assertAlmostEqual(self.camera.get_confidence_threshold(), 0.8)

        self.camera.set_enabled(False)
        self.assertFalse(self.camera.get_enabled())

        self.camera.set_focal_length_pixel(900.0)
        self.assertAlmostEqual(self.camera.get_focal_length_pixel(), 900.0)

        self.camera.set_max_disparity_pixel(120.0)
        self.assertAlmostEqual(self.camera.get_max_disparity_pixel(), 120.0)

        self.camera.set_max_distance(9000000.0)
        self.assertAlmostEqual(self.camera.get_max_distance(), 9000000.0)

        self.camera.set_min_distance(1.0)
        self.assertAlmostEqual(self.camera.get_min_distance(), 1.0)

        self.camera.set_noise_downscale_factor_pixel(2.0)
        self.assertAlmostEqual(self.camera.get_noise_downscale_factor_pixel(), 2.0)

        self.camera.set_noise_mean(0.5)
        self.assertAlmostEqual(self.camera.get_noise_mean(), 0.5)

        self.camera.set_noise_sigma(0.5)
        self.assertAlmostEqual(self.camera.get_noise_sigma(), 0.5)

        self.camera.set_outlier_removal_enabled(1)
        self.assertEqual(self.camera.get_outlier_removal_enabled(), 1)

        self.camera.set_rgb_depth_output_mode(1)
        self.assertEqual(self.camera.get_rgb_depth_output_mode(), 1)

        self.camera.set_sensor_size_pixel(1920)
        self.assertEqual(self.camera.get_sensor_size_pixel(), 1920)

        self.camera.set_show_distance(True)
        self.assertTrue(self.camera.get_show_distance())

    async def test_annotator_methods(self):
        """Test the annotator-related methods of the SingleViewDepthSensor."""
        # Initialize the camera
        self.camera.initialize()
        await update_stage_async()

        # Test attaching annotators
        for annotator in SUPPORTED_ANNOTATORS:
            self.camera.attach_annotator(annotator)
            # Check if the annotator was added to the camera's custom annotators
            self.assertIn(annotator, self.camera._custom_annotators)
            # Detach the annotator
            self.camera.detach_annotator(annotator)
            # Check if the annotator was removed
            self.assertNotIn(annotator, self.camera._custom_annotators)

        # Test attaching multiple annotators
        for annotator in SUPPORTED_ANNOTATORS:
            self.camera.attach_annotator(annotator)

        # Check if all annotators are in the camera's custom annotators
        for annotator in SUPPORTED_ANNOTATORS:
            self.assertIn(annotator, self.camera._custom_annotators)

        # Detach each annotator individually
        for annotator in SUPPORTED_ANNOTATORS:
            self.camera.detach_annotator(annotator)
            self.assertNotIn(annotator, self.camera._custom_annotators)

        # Test with invalid annotator name
        with self.assertRaises(rep.annotators.AnnotatorRegistryError):
            self.camera.attach_annotator("InvalidAnnotator")

    async def test_depth_sensor_distance_annotator(self):
        """Test the DepthSensorDistance annotator."""

        # Initialize the black grid scene for the background
        assets_root_path = await get_assets_root_path_async()
        path_to = omni.kit.commands.execute(
            "CreateReferenceCommand",
            usd_context=omni.usd.get_context(),
            path_to="/World/black_grid",
            asset_path=assets_root_path + "/Isaac/Environments/Grid/gridroom_black.usd",
            instanceable=False,
        )

        # Initialize the camera
        self.camera.initialize(attach_rgb_annotator=False)

        self.camera.set_focal_length(1.814756)
        self.camera.set_focus_distance(400.0)
        self.camera.set_baseline_mm(55)
        self.camera.set_focal_length_pixel(891.0)
        self.camera.set_sensor_size_pixel(1280.0)
        self.camera.set_max_disparity_pixel(110.0)
        self.camera.set_confidence_threshold(0.99)
        self.camera.set_noise_mean(0.5)
        self.camera.set_noise_sigma(1.0)
        self.camera.set_noise_downscale_factor_pixel(1.0)
        self.camera.set_min_distance(0.5)
        self.camera.set_max_distance(9999.9)

        self.camera.attach_annotator("DepthSensorDistance")
        await update_stage_async()

        await omni.syntheticdata.sensors.next_render_simulation_async(self.camera.get_render_product_path(), 10)
        image = self.camera.get_current_frame()["DepthSensorDistance"].astype(np.uint8)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        save_image(
            image,
            f"depth_sensor_distance_annotator.png",
            self.golden_dir,
            self.test_dir,
            save_as_golden=SAVE_IMAGE_AS_GOLDEN,
            save_as_test=SAVE_IMAGE_AS_TEST,
        )
        # load golden image
        golden_img_path = os.path.join(self.golden_dir, "depth_sensor_distance_annotator.png")
        golden_img = cv2.imread(golden_img_path, cv2.IMREAD_UNCHANGED)
        # check
        score = compare_images(golden_img, image)
        self.assertTrue(
            score[0] > IMG_COMPARISON_TOLERANCE,
            f"comparison score ({score[0]}, ({score[1]}, {score[2]})) < {IMG_COMPARISON_TOLERANCE}",
        )
