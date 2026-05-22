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

import isaacsim.core.utils.numpy.rotations as rot_utils
import numpy as np
import omni.kit.app
import omni.kit.test
from isaacsim.core.api import World
from isaacsim.core.api.objects import FixedCuboid
from isaacsim.core.utils.semantics import add_labels
from isaacsim.core.utils.stage import create_new_stage_async
from isaacsim.sensors.camera import Camera

GOLDEN_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "golden", "camera_pointcloud")
SAVE_GOLDEN_DATA = False
SAVE_DEBUG_IMGS = False


def debug_draw_clear_points():
    from isaacsim.util.debug_draw import _debug_draw

    draw_iface = _debug_draw.acquire_debug_draw_interface()
    draw_iface.clear_points()


def debug_draw_pointcloud(pointcloud_data, color, size, clear_existing=False):
    if not (isinstance(pointcloud_data, np.ndarray) and pointcloud_data.ndim == 2 and pointcloud_data.shape[1] == 3):
        print("Warning: pointcloud_data must be a NumPy array with shape (N, 3).")
        return

    from isaacsim.util.debug_draw import _debug_draw

    draw_iface = _debug_draw.acquire_debug_draw_interface()

    points_cloud = []
    colors_cloud = []
    sizes_cloud = []
    for i in range(pointcloud_data.shape[0]):
        points_cloud.append(pointcloud_data[i].tolist())
        colors_cloud.append(color)
        sizes_cloud.append(size)

    if clear_existing:
        debug_draw_clear_points()
    draw_iface.draw_points(points_cloud, colors_cloud, sizes_cloud)


async def debug_capture_rgb_image_async(camera_position, camera_look_at, resolution, out_dir, file_name):
    import omni.replicator.core as rep
    from PIL import Image

    debug_cam = rep.create.camera(position=camera_position, look_at=camera_look_at)
    render_product = rep.create.render_product(debug_cam, resolution)
    rgb_annot = rep.annotators.get("rgb")
    rgb_annot.attach(render_product)
    await rep.orchestrator.step_async()
    rgb_data = rgb_annot.get_data()
    rgb_img = Image.fromarray(rgb_data).convert("RGBA")
    rgb_img.save(os.path.join(out_dir, file_name))
    print(f"Saved image to {os.path.join(out_dir, file_name)} with shape {rgb_data.shape}")
    rgb_annot.detach()
    render_product.destroy()


class TestCameraSensorPointcloud(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await create_new_stage_async()
        self.my_world = World(stage_units_in_meters=1.0)
        await self.my_world.initialize_simulation_context_async()
        await omni.kit.app.get_app().next_update_async()

        self.my_world.scene.add_default_ground_plane()
        self.cube_1 = self.my_world.scene.add(
            FixedCuboid(
                prim_path="/World/cube_1",
                name="cube_1",
                position=np.array([0.1, 0.15, 0.25]),
                scale=np.array([1.2, 0.8, 0.1]),
                orientation=rot_utils.euler_angles_to_quats(np.array([15, -10, 0]), degrees=True),
            )
        )
        self.cube_2 = self.my_world.scene.add(
            FixedCuboid(
                prim_path="/World/cube_2",
                name="cube_2",
                position=np.array([1, -1, 0]),
                scale=np.array([0.5, 0.6, 0.7]),
            )
        )
        self.cube_3 = self.my_world.scene.add(
            FixedCuboid(
                prim_path="/World/cube_3",
                name="cube_3",
                position=np.array([-1, -1, -0.25]),
            )
        )
        self.camera = self.my_world.scene.add(
            Camera(
                prim_path="/World/camera",
                name="camera",
                frequency=60,
                position=np.array([0.0, 0.0, 10]),
                resolution=(256, 256),
                orientation=rot_utils.euler_angles_to_quats(np.array([0, 90, 30]), degrees=True),
            )
        )
        # add_labels(self.cube_1.prim, labels=["cube_small"], instance_name="class")
        # add_labels(self.cube_2.prim, labels=["cube_medium"], instance_name="class")
        # add_labels(self.cube_3.prim, labels=["cube_large"], instance_name="class")
        await self.my_world.reset_async()

    async def tearDown(self):
        self.my_world.stop()
        await omni.kit.app.get_app().next_update_async()
        self.camera = None
        self.my_world.clear_instance()
        await omni.kit.app.get_app().next_update_async()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        return

    async def compare_pointcloud_data_resolution(
        self, resolution=(64, 64), save_golden_data=False, save_debug_imgs=False
    ):
        # self.camera.initialize()
        self.camera.set_resolution(resolution)
        resolution = self.camera.get_resolution()
        expected_shape = (resolution[0] * resolution[1], 3)

        # Get pointcloud data from depth
        self.camera.add_distance_to_image_plane_to_frame()
        await omni.syntheticdata.sensors.next_render_simulation_async(self.camera.get_render_product_path(), 5)

        # Get the pointcloud data from depth annotator and make sure the shape is correct
        pointcloud_data_world_frame_from_depth = self.camera.get_pointcloud()
        pointcloud_data_camera_frame_from_depth = self.camera.get_pointcloud(world_frame=False)
        self.assertEqual(
            pointcloud_data_world_frame_from_depth.shape,
            expected_shape,
            f"World frame pointcloud data from depth annotator shape {pointcloud_data_world_frame_from_depth.shape} does not match expected shape {expected_shape}",
        )
        self.assertEqual(
            pointcloud_data_camera_frame_from_depth.shape,
            expected_shape,
            f"Camera frame pointcloud data from depth annotator shape {pointcloud_data_camera_frame_from_depth.shape} does not match expected shape {expected_shape}",
        )

        # Get pointcloud data from pointcloud annotator and make sure the shape is correct
        self.camera.add_pointcloud_to_frame()
        await omni.syntheticdata.sensors.next_render_simulation_async(self.camera.get_render_product_path(), 5)

        pointcloud_data_world_frame = self.camera.get_pointcloud()
        pointcloud_data_camera_frame = self.camera.get_pointcloud(world_frame=False)
        self.assertEqual(
            pointcloud_data_world_frame.shape,
            expected_shape,
            f"World frame pointcloud data from pointcloud annotator shape {pointcloud_data_world_frame.shape} does not match expected shape {expected_shape}",
        )
        self.assertEqual(
            pointcloud_data_camera_frame.shape,
            expected_shape,
            f"Camera frame pointcloud data from pointcloud annotator shape {pointcloud_data_camera_frame.shape} does not match expected shape {expected_shape}",
        )

        # Save the golden data (world and camera frame) from the pointcloud annotator
        if save_golden_data:
            os.makedirs(GOLDEN_DIR, exist_ok=True)
            print(f"Saving golden data to {GOLDEN_DIR}")
            np.save(
                os.path.join(GOLDEN_DIR, f"pointcloud_data_world_frame_res_{resolution[0]}_{resolution[1]}.npy"),
                pointcloud_data_world_frame,
            )
            np.save(
                os.path.join(GOLDEN_DIR, f"pointcloud_data_camera_frame_res_{resolution[0]}_{resolution[1]}.npy"),
                pointcloud_data_camera_frame,
            )

        # Load the world frame golden pointcloud data
        golden_pointcloud_data_world_frame = np.load(
            os.path.join(GOLDEN_DIR, f"pointcloud_data_world_frame_res_{resolution[0]}_{resolution[1]}.npy")
        )
        # NOTE: pointcloud annotator data order is not guaranteed, compare the sorted arrays
        self.assertTrue(
            np.allclose(
                np.sort(pointcloud_data_world_frame, axis=0),
                np.sort(golden_pointcloud_data_world_frame, axis=0),
                atol=1e-5,
            ),
            f"World frame (sorted) pointcloud data from pointcloud annotator does not match the (sorted) golden data",
        )
        # NOTE: depth-based pointcloud data has different ordering from the golden data, compare the sorted arrays
        self.assertTrue(
            np.allclose(
                np.sort(pointcloud_data_world_frame_from_depth, axis=0),
                np.sort(golden_pointcloud_data_world_frame, axis=0),
                atol=1e-5,
            ),
            f"World frame (sorted) pointcloud data from depth does not match the (sorted) golden data",
        )

        # Load the camera frame golden pointcloud data
        golden_pointcloud_data_camera_frame = np.load(
            os.path.join(GOLDEN_DIR, f"pointcloud_data_camera_frame_res_{resolution[0]}_{resolution[1]}.npy")
        )
        # NOTE: pointcloud annotator data order is not guaranteed, compare the sorted arrays
        self.assertTrue(
            np.allclose(
                np.sort(pointcloud_data_camera_frame, axis=0),
                np.sort(golden_pointcloud_data_camera_frame, axis=0),
                atol=1e-5,
            ),
            f"World frame (sorted) pointcloud data from pointcloud annotator does not match the (sorted) golden data",
        )
        # NOTE: depth-based pointcloud data has different ordering from the golden data, compare the sorted arrays
        self.assertTrue(
            np.allclose(
                np.sort(pointcloud_data_camera_frame_from_depth, axis=0),
                np.sort(golden_pointcloud_data_camera_frame, axis=0),
                atol=1e-5,
            ),
            f"Camera frame (sorted)pointcloud data from depth does not match the (sorted) golden data",
        )

        # Draw the pointcloud data for visual inspection and save the rgb image
        if save_debug_imgs:
            out_dir = os.path.join(os.getcwd(), f"_sensor_camera_pointcloud_debug")
            os.makedirs(out_dir, exist_ok=True)
            print(f"Saving debug images to {out_dir}")
            green_color = (0, 1, 0, 0.75)
            green_size = 4
            red_color = (1, 0, 0, 0.5)
            red_size = 8

            # Draw world frame pointcloud data and save the rgb image (red from depth, green from pointcloud annotator)
            debug_draw_clear_points()
            debug_draw_pointcloud(pointcloud_data_world_frame, color=green_color, size=green_size)
            debug_draw_pointcloud(pointcloud_data_world_frame_from_depth, color=red_color, size=red_size)
            await debug_capture_rgb_image_async(
                camera_position=(5, 5, 5),
                camera_look_at=(0, 0, 0),
                resolution=(1280, 720),
                out_dir=out_dir,
                file_name=f"pointcloud_data_world_frame_res_{resolution[0]}_{resolution[1]}_rgb.png",
            )

            # Draw camera frame pointcloud data and save the rgb image (red from depth, green from pointcloud annotator)
            debug_draw_clear_points()
            debug_draw_pointcloud(pointcloud_data_camera_frame, color=green_color, size=green_size)
            debug_draw_pointcloud(pointcloud_data_camera_frame_from_depth, color=red_color, size=red_size)
            await debug_capture_rgb_image_async(
                camera_position=(5, 5, 15),
                camera_look_at=(0, 0, 10),
                resolution=(1280, 720),
                out_dir=out_dir,
                file_name=f"pointcloud_data_camera_frame_res_{resolution[0]}_{resolution[1]}_rgb.png",
            )

    async def test_pointcloud_data_resolution_4_4(self):
        await self.compare_pointcloud_data_resolution(
            resolution=(4, 4), save_golden_data=SAVE_GOLDEN_DATA, save_debug_imgs=SAVE_DEBUG_IMGS
        )

    async def test_pointcloud_data_resolution_64_64(self):
        await self.compare_pointcloud_data_resolution(
            resolution=(64, 64), save_golden_data=SAVE_GOLDEN_DATA, save_debug_imgs=SAVE_DEBUG_IMGS
        )

    async def test_pointcloud_data_resolution_67_137(self):
        await self.compare_pointcloud_data_resolution(
            resolution=(67, 137), save_golden_data=SAVE_GOLDEN_DATA, save_debug_imgs=SAVE_DEBUG_IMGS
        )

    async def test_pointcloud_data_resolution_211_99(self):
        await self.compare_pointcloud_data_resolution(
            resolution=(211, 99), save_golden_data=SAVE_GOLDEN_DATA, save_debug_imgs=SAVE_DEBUG_IMGS
        )
