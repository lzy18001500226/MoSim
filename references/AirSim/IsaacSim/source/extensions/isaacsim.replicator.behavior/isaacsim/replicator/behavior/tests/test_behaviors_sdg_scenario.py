# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import io
import json
import os
from unittest.mock import patch

import numpy as np
import omni.kit.app
import omni.kit.test
import omni.usd
from isaacsim.test.utils.image_comparison import compare_arrays_within_tolerances
from PIL import Image


class TestBehaviorsSDGScenario(omni.kit.test.AsyncTestCase):
    """
    SDG pipeline test using behavior scripts and comparing to the golden data
    """

    RGB_MEAN_DIFF_TOLERANCE = 150
    DEPTH_MEAN_DIFF_TOLERANCE = 1
    DEPTH_RTOL = 1.0e-4
    DEPTH_ATOL = 1.0e-3
    RANDOM_SEED = 10
    OUTPUT_DIR = "_out_behaviors_sdg"

    async def setUp(self):
        await omni.kit.app.get_app().next_update_async()
        omni.usd.get_context().new_stage()
        await omni.kit.app.get_app().next_update_async()

    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        omni.usd.get_context().close_stage()
        await omni.kit.app.get_app().next_update_async()

    # Compare PNG files with the specified prefix using mean pixel difference
    def compare_images_with_mean_diff(self, golden_dir, test_dir, prefix, tolerance):
        print(f"Comparing {prefix} images with mean difference tolerance: {tolerance}")
        # Get the list of .png files matching the prefix
        golden_files = sorted([f for f in os.listdir(golden_dir) if f.startswith(prefix) and f.endswith(".png")])
        test_files = sorted([f for f in os.listdir(test_dir) if f.startswith(prefix) and f.endswith(".png")])

        # Ensure the file lists match
        self.assertListEqual(
            golden_files,
            test_files,
            f"File names mismatch for {prefix}*.png: {golden_files} in golden_dir vs {test_files} in test_dir.",
        )

        # Iterate over the matching .png files and compare them using image comparison utilities
        for file_name in golden_files:
            golden_file_path = os.path.join(golden_dir, file_name)
            test_file_path = os.path.join(test_dir, file_name)

            # Open images and convert to arrays
            golden_image = Image.open(golden_file_path)
            test_image = Image.open(test_file_path)
            golden_array = np.array(golden_image)
            test_array = np.array(test_image)

            # Use comprehensive comparison utilities
            stdout_capture = io.StringIO()
            with patch("sys.stdout", stdout_capture):
                result = compare_arrays_within_tolerances(
                    golden_array,
                    test_array,
                    allclose_rtol=None,  # Disable allclose for this test
                    allclose_atol=None,
                    mean_tolerance=tolerance,
                    print_all_stats=True,
                )

            # Only print detailed stats on failure to keep logs clean
            if not result["passed"]:
                captured_output = stdout_capture.getvalue()
                print(f"\t'{file_name}': FAILED comparison")
                print(captured_output)
            else:
                print(f"\t'{file_name}': PASSED (mean_diff={result['metrics']['mean_abs']:.3f})")

            self.assertTrue(
                result["passed"],
                f"Mean difference comparison failed for {file_name}. "
                f"Expected mean_diff <= {tolerance}, got {result['metrics']['mean_abs']:.3f}.\n"
                f"Detailed statistics:\n{stdout_capture.getvalue()}",
            )

    # Compare .json files with the specified prefix
    def compare_json_files(self, golden_dir, test_dir, prefix):
        print(f"Comparing {prefix} json files")
        # Get the list of .json files matching the prefix
        golden_files = sorted([f for f in os.listdir(golden_dir) if f.startswith(prefix) and f.endswith(".json")])
        test_files = sorted([f for f in os.listdir(test_dir) if f.startswith(prefix) and f.endswith(".json")])

        # Ensure the file lists match
        self.assertListEqual(
            golden_files,
            test_files,
            f"File names mismatch for {prefix}*.json: {golden_files} in golden_dir vs {test_files} in test_dir.",
        )

        # Compare the content of each file
        for file_name in golden_files:
            golden_file_path = os.path.join(golden_dir, file_name)
            test_file_path = os.path.join(test_dir, file_name)

            # Load JSON content
            with open(golden_file_path, "r") as golden_file:
                golden_data = json.load(golden_file)

            with open(test_file_path, "r") as test_file:
                test_data = json.load(test_file)

            # Compare the structure and content
            self.assertEqual(
                golden_data, test_data, f"Content mismatch in file {file_name}: {golden_file_path} vs {test_file_path}."
            )

    # Compare .npy files with the specified prefix
    def compare_npy_files(self, golden_dir, test_dir, prefix, mean_diff_tolerance=None, rtol=1.0e-5, atol=1.0e-8):
        comparison_method = "mean_diff" if mean_diff_tolerance is not None else "allclose"
        tolerance_str = (
            f"mean_diff_tolerance: {mean_diff_tolerance}"
            if mean_diff_tolerance is not None
            else f"rtol: {rtol}, atol: {atol}"
        )
        print(f"Comparing {prefix} npy files using {comparison_method} with {tolerance_str}")

        # Get the list of .npy files matching the prefix
        golden_files = sorted([f for f in os.listdir(golden_dir) if f.startswith(prefix) and f.endswith(".npy")])
        test_files = sorted([f for f in os.listdir(test_dir) if f.startswith(prefix) and f.endswith(".npy")])

        # Ensure the file lists match
        self.assertListEqual(
            golden_files,
            test_files,
            f"File names mismatch for {prefix}*.npy: {golden_files} in golden_dir vs {test_files} in test_dir.",
        )

        # Compare the content of each file using comprehensive comparison utilities
        for file_name in golden_files:
            golden_file_path = os.path.join(golden_dir, file_name)
            test_file_path = os.path.join(test_dir, file_name)

            # Load numpy data
            golden_data = np.load(golden_file_path)
            test_data = np.load(test_file_path)

            # Use comprehensive comparison utilities
            stdout_capture = io.StringIO()
            with patch("sys.stdout", stdout_capture):
                if mean_diff_tolerance is not None:
                    # Use mean difference comparison
                    result = compare_arrays_within_tolerances(
                        golden_data,
                        test_data,
                        allclose_rtol=None,  # Disable allclose for mean diff comparison
                        allclose_atol=None,
                        mean_tolerance=mean_diff_tolerance,
                        print_all_stats=True,
                    )
                else:
                    # Use allclose comparison
                    result = compare_arrays_within_tolerances(
                        golden_data,
                        test_data,
                        allclose_rtol=rtol,
                        allclose_atol=atol,
                        print_all_stats=True,
                    )

            # Only print detailed stats on failure to keep logs clean
            if not result["passed"]:
                captured_output = stdout_capture.getvalue()
                print(f"\t'{file_name}': FAILED comparison")
                print(captured_output)
            else:
                if mean_diff_tolerance is not None:
                    print(f"\t'{file_name}': PASSED (mean_diff={result['metrics']['mean_abs']:.6f})")
                else:
                    print(f"\t'{file_name}': PASSED (allclose with rtol={rtol}, atol={atol})")

            # Assert with detailed error message
            if mean_diff_tolerance is not None:
                self.assertTrue(
                    result["passed"],
                    f"Mean difference comparison failed for {file_name}. "
                    f"Expected mean_diff <= {mean_diff_tolerance}, got {result['metrics']['mean_abs']:.6f}.\n"
                    f"Detailed statistics:\n{stdout_capture.getvalue()}",
                )
            else:
                self.assertTrue(
                    result["passed"],
                    f"Allclose comparison failed for {file_name} with rtol={rtol}, atol={atol}.\n"
                    f"Detailed statistics:\n{stdout_capture.getvalue()}",
                )

    async def setup_and_run_behaviors_sdg(self):
        import asyncio
        import inspect
        import os
        import random

        import omni.kit.app
        import omni.replicator.core as rep
        import omni.timeline
        import omni.usd
        from isaacsim.core.utils.semantics import add_labels, remove_labels
        from isaacsim.replicator.behavior.behaviors import (
            LightRandomizer,
            LocationRandomizer,
            LookAtBehavior,
            RotationRandomizer,
            TextureRandomizer,
            VolumeStackRandomizer,
        )
        from isaacsim.replicator.behavior.global_variables import EXPOSED_ATTR_NS
        from isaacsim.replicator.behavior.utils.behavior_utils import (
            add_behavior_script_with_parameters_async,
            publish_event_and_wait_for_completion_async,
        )
        from isaacsim.storage.native import get_assets_root_path_async
        from pxr import Gf, UsdGeom

        async def setup_and_run_stacking_simulation_async(prim):
            STACK_ASSETS_CSV = (
                "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxC_01.usd,"
                "/Isaac/Environments/Simple_Warehouse/Props/SM_CardBoxD_01.usd,"
                "/Isaac/Props/KLT_Bin/small_KLT_visual.usd,"
            )

            # Add the behavior script with custom parameters
            script_path = inspect.getfile(VolumeStackRandomizer)
            parameters = {
                f"{EXPOSED_ATTR_NS}:{VolumeStackRandomizer.BEHAVIOR_NS}:assets:csv": STACK_ASSETS_CSV,
                f"{EXPOSED_ATTR_NS}:{VolumeStackRandomizer.BEHAVIOR_NS}:assets:numRange": Gf.Vec2i(2, 15),
            }
            await add_behavior_script_with_parameters_async(prim, script_path, parameters)

            # Helper function to handle publishing and waiting for events
            async def handle_event(action, expected_state, max_wait):
                return await publish_event_and_wait_for_completion_async(
                    publish_payload={"prim_path": prim.GetPath(), "action": action},
                    expected_payload={"prim_path": prim.GetPath(), "state_name": expected_state},
                    publish_event_name=VolumeStackRandomizer.EVENT_NAME_IN,
                    subscribe_event_name=VolumeStackRandomizer.EVENT_NAME_OUT,
                    max_wait_updates=max_wait,
                )

            # Define and execute the stacking simulation steps
            actions = [("reset", "RESET", 10), ("setup", "SETUP", 500), ("run", "FINISHED", 1500)]
            for action, state, wait in actions:
                print(f"Executing '{action}' and waiting for state '{state}'...")
                if not await handle_event(action, state, wait):
                    print(f"Failed to complete '{action}' with state '{state}'.")
                    return

            print("Stacking simulation finished.")

        async def setup_texture_randomizer_async(prim):
            TEXTURE_ASSETS_CSV = (
                "/Isaac/Materials/Textures/Patterns/nv_bamboo_desktop.jpg,"
                "/Isaac/Materials/Textures/Patterns/nv_wood_boards_brown.jpg,"
                "/Isaac/Materials/Textures/Patterns/nv_wooden_wall.jpg,"
            )

            script_path = inspect.getfile(TextureRandomizer)
            parameters = {
                f"{EXPOSED_ATTR_NS}:{TextureRandomizer.BEHAVIOR_NS}:interval": 5,
                f"{EXPOSED_ATTR_NS}:{TextureRandomizer.BEHAVIOR_NS}:textures:csv": TEXTURE_ASSETS_CSV,
            }
            await add_behavior_script_with_parameters_async(prim, script_path, parameters)

        async def setup_light_behaviors_async(prim):
            # Light randomization
            light_script_path = inspect.getfile(LightRandomizer)
            light_parameters = {
                f"{EXPOSED_ATTR_NS}:{LightRandomizer.BEHAVIOR_NS}:interval": 4,
                f"{EXPOSED_ATTR_NS}:{LightRandomizer.BEHAVIOR_NS}:range:intensity": Gf.Vec2f(20000, 120000),
            }
            await add_behavior_script_with_parameters_async(prim, light_script_path, light_parameters)

            # Location randomization
            location_script_path = inspect.getfile(LocationRandomizer)
            location_parameters = {
                f"{EXPOSED_ATTR_NS}:{LocationRandomizer.BEHAVIOR_NS}:interval": 2,
                f"{EXPOSED_ATTR_NS}:{LocationRandomizer.BEHAVIOR_NS}:range:minPosition": Gf.Vec3d(-1.25, -1.25, 0.0),
                f"{EXPOSED_ATTR_NS}:{LocationRandomizer.BEHAVIOR_NS}:range:maxPosition": Gf.Vec3d(1.25, 1.25, 0.0),
            }
            await add_behavior_script_with_parameters_async(prim, location_script_path, location_parameters)

        async def setup_target_asset_behaviors_async(prim):
            # Rotation randomization with default parameters
            rotation_script_path = inspect.getfile(RotationRandomizer)
            await add_behavior_script_with_parameters_async(prim, rotation_script_path, {})

            # Location randomization
            location_script_path = inspect.getfile(LocationRandomizer)
            location_parameters = {
                f"{EXPOSED_ATTR_NS}:{LocationRandomizer.BEHAVIOR_NS}:interval": 3,
                f"{EXPOSED_ATTR_NS}:{LocationRandomizer.BEHAVIOR_NS}:range:minPosition": Gf.Vec3d(-0.2, -0.2, -0.2),
                f"{EXPOSED_ATTR_NS}:{LocationRandomizer.BEHAVIOR_NS}:range:maxPosition": Gf.Vec3d(0.2, 0.2, 0.2),
            }
            await add_behavior_script_with_parameters_async(prim, location_script_path, location_parameters)

        async def setup_camera_behaviors_async(prim, target_prim_path):
            # Look at behavior following the target asset
            script_path = inspect.getfile(LookAtBehavior)
            parameters = {
                f"{EXPOSED_ATTR_NS}:{LookAtBehavior.BEHAVIOR_NS}:targetPrimPath": target_prim_path,
            }
            await add_behavior_script_with_parameters_async(prim, script_path, parameters)

        async def setup_writer_and_capture_data_async(camera_path, num_captures):
            # Create the writer and the render product
            rp = rep.create.render_product(camera_path, (512, 512))
            writer = rep.writers.get("BasicWriter")
            output_directory = os.path.join(os.getcwd(), self.OUTPUT_DIR)
            print(f"output_directory: {output_directory}")
            writer.initialize(output_dir=output_directory, rgb=True, distance_to_image_plane=True, colorize_depth=True)
            writer.attach(rp)

            # Disable capture on play, data is captured manually using the step function
            rep.orchestrator.set_capture_on_play(False)

            # Start the timeline for the behavior scripts to run
            timeline = omni.timeline.get_timeline_interface()
            timeline.play()
            await omni.kit.app.get_app().next_update_async()

            # Capture frames
            for i in range(num_captures):
                # Advance the app (including the timeline)
                await omni.kit.app.get_app().next_update_async()

                # Capture and write frame
                print(f"Capturing frame {i} at time {timeline.get_current_time():.4f}")
                await rep.orchestrator.step_async(rt_subframes=32, delta_time=0.0, pause_timeline=False)

            # Stop the timeline (and the behavior scripts triggering)
            timeline.stop()
            await omni.kit.app.get_app().next_update_async()

            # Free the renderer resources
            writer.detach()
            rp.destroy()

            # Make sure all the frames are written from the backend queue
            await rep.orchestrator.wait_until_complete_async()

        async def run_example_async():
            STAGE_URL = "/Isaac/Samples/Replicator/Stage/warehouse_pallets_behavior_scripts.usd"
            PALLETS_ROOT_PATH = "/Root/Pallets"
            LIGHTS_ROOT_PATH = "/Root/Lights"
            CAMERA_PATH = "/Root/Camera_01"
            TARGET_ASSET_URL = "/Isaac/Props/YCB/Axis_Aligned/035_power_drill.usd"
            TARGET_ASSET_PATH = "/Root/Target"
            TARGET_ASSET_LABEL = "power_drill"
            TARGET_ASSET_LOCATION = (-1.5, 5.5, 1.5)

            # Open stage
            assets_root_path = await get_assets_root_path_async()
            print(f"Opening stage from {assets_root_path + STAGE_URL}")
            await omni.usd.get_context().open_stage_async(assets_root_path + STAGE_URL)
            stage = omni.usd.get_context().get_stage()

            random.seed(self.RANDOM_SEED)
            rep.set_global_seed(self.RANDOM_SEED)

            # Check if all required prims exist in the stage
            pallets_root_prim = stage.GetPrimAtPath(PALLETS_ROOT_PATH)
            lights_root_prim = stage.GetPrimAtPath(LIGHTS_ROOT_PATH)
            camera_prim = stage.GetPrimAtPath(CAMERA_PATH)
            if not all([pallets_root_prim.IsValid(), lights_root_prim.IsValid(), camera_prim.IsValid()]):
                print(f"Not all required prims exist in the stage.")
                return

            # Spawn the target asset at the requested location, label it with the target asset label
            target_prim = stage.DefinePrim(TARGET_ASSET_PATH, "Xform")
            target_prim.GetReferences().AddReference(assets_root_path + TARGET_ASSET_URL)
            if not target_prim.HasAttribute("xformOp:translate"):
                UsdGeom.Xformable(target_prim).AddTranslateOp()
            target_prim.GetAttribute("xformOp:translate").Set(TARGET_ASSET_LOCATION)
            remove_labels(target_prim, include_descendants=True)
            add_labels(target_prim, labels=[TARGET_ASSET_LABEL], instance_name="class")

            # Setup and run the stacking simulation before capturing the data
            await setup_and_run_stacking_simulation_async(pallets_root_prim)

            # Setup texture randomizer
            await setup_texture_randomizer_async(pallets_root_prim)

            # Setup the light behaviors
            await setup_light_behaviors_async(lights_root_prim)

            # Setup the target asset behaviors
            await setup_target_asset_behaviors_async(target_prim)

            # Setup the camera behaviors
            await setup_camera_behaviors_async(camera_prim, str(target_prim.GetPath()))

            # Setup the writer and capture the data, behavior scripts are triggered by running the timeline
            await setup_writer_and_capture_data_async(camera_path=camera_prim.GetPath(), num_captures=6)

        await run_example_async()

    async def test_behavior_sdg_pipeline_warehouse(self):
        print(f"Starting the behaviors SDG pipeline")
        await self.setup_and_run_behaviors_sdg()

        # Get the platform subfolder (linux or windows)
        platform_subfolder = "linux" if os.name == "posix" else "windows"
        golden_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data", "golden", self.OUTPUT_DIR, platform_subfolder
        )
        test_dir = os.path.join(os.getcwd(), self.OUTPUT_DIR)
        print(f"Golden directory: {golden_dir}")
        print(f"Test directory: {test_dir}")

        # Compare the rgb data (larger tolerance due to denoising differences)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "rgb", self.RGB_MEAN_DIFF_TOLERANCE)

        # Compare the depth data (smaller tolerance since it is not influenced by denoising)
        self.compare_images_with_mean_diff(
            golden_dir, test_dir, "distance_to_image_plane", self.DEPTH_MEAN_DIFF_TOLERANCE
        )
