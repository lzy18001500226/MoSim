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
import os
from unittest.mock import patch

import carb.settings
import numpy as np
import omni.kit
import omni.usd
from isaacsim.test.utils.image_comparison import compare_arrays_within_tolerances
from PIL import Image


class TestDataAugmentation(omni.kit.test.AsyncTestCase):

    RGB_MEAN_DIFF_TOLERANCE = 100
    DEPTH_MEAN_DIFF_TOLERANCE = 5
    NUM_FRAMES = 2
    SEED = 12

    async def setUp(self):
        await omni.kit.app.get_app().next_update_async()
        omni.usd.get_context().new_stage()
        await omni.kit.app.get_app().next_update_async()
        self.original_dlss_exec_mode = carb.settings.get_settings().get("rtx/post/dlss/execMode")

    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        omni.usd.get_context().new_stage()
        await omni.kit.app.get_app().next_update_async()
        carb.settings.get_settings().set("rtx/post/dlss/execMode", self.original_dlss_exec_mode)

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

    async def run_annotator_augmentation_async(self, out_subdir: str, num_frames: int, use_warp: bool, seed: int):
        import asyncio
        import os
        import time

        import carb.settings
        import numpy as np
        import omni
        import omni.replicator.core as rep
        import warp as wp
        from isaacsim.core.utils.stage import open_stage
        from isaacsim.storage.native import get_assets_root_path
        from PIL import Image

        rep.set_global_seed(seed)

        ENV_URL = "/Isaac/Environments/Grid/default_environment.usd"

        # Enable scripts
        carb.settings.get_settings().set_bool("/app/omni.graph.scriptnode/opt_in", True)

        # Set DLSS to Quality mode (2) for best SDG results , options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)
        carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

        # Illustrative augmentation switching red and blue channels in rgb data using numpy (CPU) and warp (GPU)
        def rgb_to_bgr_np(data_in):
            data_in[:, :, [0, 2]] = data_in[:, :, [2, 0]]
            return data_in

        @wp.kernel
        def rgb_to_bgr_wp(data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8)):
            i, j = wp.tid()
            data_out[i, j, 0] = data_in[i, j, 2]
            data_out[i, j, 1] = data_in[i, j, 1]
            data_out[i, j, 2] = data_in[i, j, 0]
            data_out[i, j, 3] = data_in[i, j, 3]

        # Gaussian noise augmentation on depth data in numpy (CPU) and warp (GPU)
        def gaussian_noise_depth_np(data_in, sigma: float, seed: int):
            np.random.seed(seed)
            result = data_in.astype(np.float32) + np.random.randn(*data_in.shape) * sigma
            return np.clip(result, 0, None).astype(data_in.dtype)

        rep.AnnotatorRegistry.register_augmentation(
            "gn_depth_np", rep.annotators.Augmentation.from_function(gaussian_noise_depth_np, sigma=0.1, seed=seed)
        )

        @wp.kernel
        def gaussian_noise_depth_wp(
            data_in: wp.array2d(dtype=wp.float32), data_out: wp.array2d(dtype=wp.float32), sigma: float, seed: int
        ):
            i, j = wp.tid()
            # Unique ID for random seed per pixel
            scalar_pixel_id = i * data_in.shape[1] + j
            state = wp.rand_init(seed, scalar_pixel_id)
            data_out[i, j] = data_in[i, j] + sigma * wp.randn(state)

        rep.AnnotatorRegistry.register_augmentation(
            "gn_depth_wp", rep.annotators.Augmentation.from_function(gaussian_noise_depth_wp, sigma=0.1, seed=seed)
        )

        # Helper functions for writing images from annotator data
        def write_rgb(data, path):
            rgb_img = Image.fromarray(data).convert("RGBA")
            rgb_img.save(path + ".png")

        def write_depth(data, path):
            # Convert to numpy (if warp), normalize, handle any nan values, and convert to from float32 to 8-bit int array
            if isinstance(data, wp.array):
                data = data.numpy()
            # Replace any -inf and inf values with nan, then calculate the mean value and replace nan with the mean
            data[np.isinf(data)] = np.nan
            data = np.nan_to_num(data, nan=np.nanmean(data), copy=False)
            normalized_array = (data - np.min(data)) / (np.max(data) - np.min(data))
            integer_array = (normalized_array * 255).astype(np.uint8)
            depth_img = Image.fromarray(integer_array).convert("L")
            depth_img.save(path + ".png")

        # Setup the environment
        assets_root_path = get_assets_root_path()
        open_stage(assets_root_path + ENV_URL)

        # Disable capture on play and async rendering
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
        carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
        carb.settings.get_settings().set("/app/asyncRendering", False)

        # Create a red cube and a render product from a camera looking at the cube from the top
        red_mat = rep.create.material_omnipbr(diffuse=(1, 0, 0))
        red_cube = rep.create.cube(position=(0, 0, 0.71), material=red_mat)
        cam = rep.create.camera(position=(0, 0, 5), look_at=(0, 0, 0))
        rp = rep.create.render_product(cam, (512, 512))

        # Get the local augmentations, either from function or from the registry
        rgb_to_bgr_augm = None
        gn_depth_augm = None
        if use_warp:
            rgb_to_bgr_augm = rep.annotators.Augmentation.from_function(rgb_to_bgr_wp)
            gn_depth_augm = rep.AnnotatorRegistry.get_augmentation("gn_depth_wp")
        else:
            rgb_to_bgr_augm = rep.annotators.Augmentation.from_function(rgb_to_bgr_np)
            gn_depth_augm = rep.AnnotatorRegistry.get_augmentation("gn_depth_np")

        # Output directories
        out_dir = os.path.join(os.getcwd(), out_subdir)
        print(f"Writing data to: {out_dir}")
        os.makedirs(out_dir, exist_ok=True)

        # Register the annotator together with its augmentation
        rep.annotators.register(
            name="rgb_to_bgr_augm",
            annotator=rep.annotators.augment(
                source_annotator=rep.AnnotatorRegistry.get_annotator("rgb"),
                augmentation=rgb_to_bgr_augm,
            ),
        )

        rgb_to_bgr_annot = rep.AnnotatorRegistry.get_annotator("rgb_to_bgr_augm")
        depth_annot_1 = rep.AnnotatorRegistry.get_annotator("distance_to_camera")
        depth_annot_1.augment(gn_depth_augm)
        depth_annot_2 = rep.AnnotatorRegistry.get_annotator("distance_to_camera")
        depth_annot_2.augment(gn_depth_augm, sigma=0.5)

        rgb_to_bgr_annot.attach(rp)
        depth_annot_1.attach(rp)
        depth_annot_2.attach(rp)

        # Generate a replicator graph to rotate the cube every capture frame
        with rep.trigger.on_frame():
            with red_cube:
                rep.randomizer.rotation()

        # Evaluate the graph
        rep.orchestrator.preview()

        # The orchestrator.step() function will trigger the randomization graph and feed annotators with new data
        async def run_example_async(num_frames):
            # Wait a few frames for the new stage to fully load
            for _ in range(10):
                await omni.kit.app.get_app().next_update_async()
            # Measure the duration of capturing the data
            start_time = time.time()
            for i in range(num_frames):
                await rep.orchestrator.step_async(rt_subframes=32)
                rgb_data = rgb_to_bgr_annot.get_data()
                depth_data_1 = depth_annot_1.get_data()
                depth_data_2 = depth_annot_2.get_data()
                write_rgb(rgb_data, os.path.join(out_dir, f"annot_rgb_{i}"))
                write_depth(depth_data_1, os.path.join(out_dir, f"annot_depth_1_{i}"))
                write_depth(depth_data_2, os.path.join(out_dir, f"annot_depth_2_{i}"))
            return start_time

        # Run the example
        start_time = await run_example_async(num_frames)
        await rep.orchestrator.wait_until_complete_async()
        print(
            f"The duration for capturing {num_frames} frames using '{'warp' if use_warp else 'numpy'}' was: {time.time() - start_time:.4f} seconds, with an average of {(time.time() - start_time) / num_frames:.4f} seconds per frame."
        )

    async def run_writer_augmentation_async(self, out_subdir: str, num_frames: int, use_warp: bool, seed: int):
        import asyncio
        import os
        import time

        import carb.settings
        import numpy as np
        import omni
        import omni.replicator.core as rep
        import warp as wp
        from isaacsim.core.utils.stage import open_stage
        from isaacsim.storage.native import get_assets_root_path

        rep.set_global_seed(seed)
        ENV_URL = "/Isaac/Environments/Grid/default_environment.usd"

        # Enable scripts
        carb.settings.get_settings().set_bool("/app/omni.graph.scriptnode/opt_in", True)

        # Set DLSS to Quality mode (2) for best SDG results , options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)
        carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

        # Gaussian noise augmentation on rgba data in numpy (CPU) and warp (GPU)
        def gaussian_noise_rgb_np(data_in, sigma: float, seed: int):
            np.random.seed(seed)
            data_in = data_in.astype(np.float32)
            data_in[:, :, 0] = data_in[:, :, 0] + np.random.randn(*data_in.shape[:-1]) * sigma
            data_in[:, :, 1] = data_in[:, :, 1] + np.random.randn(*data_in.shape[:-1]) * sigma
            data_in[:, :, 2] = data_in[:, :, 2] + np.random.randn(*data_in.shape[:-1]) * sigma
            data_in = np.clip(data_in, 0, 255).astype(np.uint8)
            return data_in

        @wp.kernel
        def gaussian_noise_rgb_wp(
            data_in: wp.array3d(dtype=wp.uint8), data_out: wp.array3d(dtype=wp.uint8), sigma: float, seed: int
        ):
            # Get thread coordinates and image dimensions to calculate unique pixel ID for random generation
            i, j = wp.tid()
            dim_i = data_in.shape[0]
            dim_j = data_in.shape[1]
            pixel_id = i * dim_i + j

            # Use pixel_id as offset to create unique seeds for each pixel and channel (ensure independent noise patterns across R,G,B channels)
            state_r = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 0))
            state_g = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 1))
            state_b = wp.rand_init(seed, pixel_id + (dim_i * dim_j * 2))

            # Apply noise to each channel independently using unique seeds
            data_out[i, j, 0] = wp.uint8(wp.int32(data_in[i, j, 0]) + wp.int32(sigma * wp.randn(state_r)))
            data_out[i, j, 1] = wp.uint8(wp.int32(data_in[i, j, 1]) + wp.int32(sigma * wp.randn(state_g)))
            data_out[i, j, 2] = wp.uint8(wp.int32(data_in[i, j, 2]) + wp.int32(sigma * wp.randn(state_b)))
            data_out[i, j, 3] = data_in[i, j, 3]

        # Gaussian noise augmentation on depth data in numpy (CPU) and warp (GPU)
        def gaussian_noise_depth_np(data_in, sigma: float, seed: int):
            np.random.seed(seed)
            result = data_in.astype(np.float32) + np.random.randn(*data_in.shape) * sigma
            return np.clip(result, 0, None).astype(data_in.dtype)

        rep.AnnotatorRegistry.register_augmentation(
            "gn_depth_np", rep.annotators.Augmentation.from_function(gaussian_noise_depth_np, sigma=0.1, seed=seed)
        )

        @wp.kernel
        def gaussian_noise_depth_wp(
            data_in: wp.array2d(dtype=wp.float32), data_out: wp.array2d(dtype=wp.float32), sigma: float, seed: int
        ):
            i, j = wp.tid()
            # Unique ID for random seed per pixel
            scalar_pixel_id = i * data_in.shape[1] + j
            state = wp.rand_init(seed, scalar_pixel_id)
            data_out[i, j] = data_in[i, j] + sigma * wp.randn(state)

        rep.AnnotatorRegistry.register_augmentation(
            "gn_depth_wp", rep.annotators.Augmentation.from_function(gaussian_noise_depth_wp, sigma=0.1, seed=seed)
        )

        # Setup the environment
        assets_root_path = get_assets_root_path()
        open_stage(assets_root_path + ENV_URL)

        # Disable capture on play and async rendering
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
        carb.settings.get_settings().set("/omni/replicator/asyncRendering", False)
        carb.settings.get_settings().set("/app/asyncRendering", False)

        # Create a red cube and a render product from a camera looking at the cube from the top
        red_mat = rep.create.material_omnipbr(diffuse=(1, 0, 0))
        red_cube = rep.create.cube(position=(0, 0, 0.71), material=red_mat)
        cam = rep.create.camera(position=(0, 0, 5), look_at=(0, 0, 0))
        rp = rep.create.render_product(cam, (512, 512))

        # Access default annotators from replicator
        rgb_to_hsv_augm = rep.annotators.Augmentation.from_function(rep.augmentations_default.aug_rgb_to_hsv)
        hsv_to_rgb_augm = rep.annotators.Augmentation.from_function(rep.augmentations_default.aug_hsv_to_rgb)

        # Access the custom annotators as functions or from the registry
        gn_rgb_augm = None
        gn_depth_augm = None
        if use_warp:
            gn_rgb_augm = rep.annotators.Augmentation.from_function(gaussian_noise_rgb_wp, sigma=6.0, seed=seed)
            gn_depth_augm = rep.AnnotatorRegistry.get_augmentation("gn_depth_wp")
        else:
            gn_rgb_augm = rep.annotators.Augmentation.from_function(gaussian_noise_rgb_np, sigma=6.0, seed=seed)
            gn_depth_augm = rep.AnnotatorRegistry.get_augmentation("gn_depth_np")

        # Create a writer and apply the augmentations to its corresponding annotators
        out_dir = os.path.join(os.getcwd(), out_subdir)
        print(f"Writing data to: {out_dir}")
        writer = rep.WriterRegistry.get("BasicWriter")
        writer.initialize(output_dir=out_dir, rgb=True, distance_to_camera=True)

        augmented_rgb_annot = rep.annotators.get("rgb").augment_compose(
            [rgb_to_hsv_augm, gn_rgb_augm, hsv_to_rgb_augm], name="rgb"
        )
        writer.add_annotator(augmented_rgb_annot)
        writer.augment_annotator("distance_to_camera", gn_depth_augm)

        # Attach render product to writer
        writer.attach([rp])

        # Generate a replicator graph randomizing the cube's rotation every frame
        with rep.trigger.on_frame():
            with red_cube:
                rep.randomizer.rotation()

        # Evaluate the graph
        rep.orchestrator.preview()

        # The `step()` function will trigger the randomization graph and the writers
        async def run_example_async(num_frames):
            # Wait a few frames for the new stage to fully load
            for _ in range(10):
                await omni.kit.app.get_app().next_update_async()
            # Measure the duration of capturing the data
            start_time = time.time()
            for _ in range(num_frames):
                await rep.orchestrator.step_async(rt_subframes=32)
            return start_time

        start_time = await run_example_async(num_frames)
        await rep.orchestrator.wait_until_complete_async()
        print(
            f"The duration for capturing {num_frames} frames using '{'warp' if use_warp else 'numpy'}' was: {time.time() - start_time:.4f} seconds, with an average of {(time.time() - start_time) / num_frames:.4f} seconds per frame."
        )

    async def test_data_augmentation_no_warp_async(self):
        out_subdir = "_out_augm_annot_warp_False"
        await self.run_annotator_augmentation_async(
            out_subdir=out_subdir, num_frames=self.NUM_FRAMES, use_warp=False, seed=self.SEED
        )

        golden_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "golden", out_subdir)
        test_dir = os.path.join(os.getcwd(), out_subdir)
        print(f"Golden directory: {golden_dir}")
        print(f"Test directory: {test_dir}")

        # Compare the rgb data (larger tolerance due to denoising differences)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "annot_rgb", self.RGB_MEAN_DIFF_TOLERANCE)
        # Compare the depth data (smaller tolerance since it is not influenced by denoising)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "annot_depth_1", self.DEPTH_MEAN_DIFF_TOLERANCE)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "annot_depth_2", self.DEPTH_MEAN_DIFF_TOLERANCE)

    async def test_data_augmentation_with_warp_async(self):
        out_subdir = "_out_augm_annot_warp_True"
        await self.run_annotator_augmentation_async(
            out_subdir=out_subdir, num_frames=self.NUM_FRAMES, use_warp=True, seed=self.SEED
        )

        golden_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "golden", out_subdir)
        test_dir = os.path.join(os.getcwd(), out_subdir)
        print(f"Golden directory: {golden_dir}")
        print(f"Test directory: {test_dir}")

        # Compare the rgb data (larger tolerance due to denoising differences)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "annot_rgb", self.RGB_MEAN_DIFF_TOLERANCE)
        # Compare the depth data (smaller tolerance since it is not influenced by denoising)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "annot_depth_1", self.DEPTH_MEAN_DIFF_TOLERANCE)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "annot_depth_2", self.DEPTH_MEAN_DIFF_TOLERANCE)

    async def test_data_augmentation_writer_no_warp_async(self):
        out_subdir = "_out_augm_writer_warp_False"
        await self.run_writer_augmentation_async(
            out_subdir=out_subdir, num_frames=self.NUM_FRAMES, use_warp=False, seed=self.SEED
        )

        golden_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "golden", out_subdir)
        test_dir = os.path.join(os.getcwd(), out_subdir)
        print(f"Golden directory: {golden_dir}")
        print(f"Test directory: {test_dir}")

        # Compare the rgb data (larger tolerance due to denoising differences)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "rgb", self.RGB_MEAN_DIFF_TOLERANCE)
        # Compare the depth data (smaller tolerance since it is not influenced by denoising)
        self.compare_npy_files(
            golden_dir, test_dir, "distance_to_image_plane", mean_diff_tolerance=self.DEPTH_MEAN_DIFF_TOLERANCE
        )

    async def test_data_augmentation_writer_with_warp_async(self):
        out_subdir = "_out_augm_writer_warp_True"
        await self.run_writer_augmentation_async(
            out_subdir=out_subdir, num_frames=self.NUM_FRAMES, use_warp=True, seed=self.SEED
        )

        golden_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "golden", out_subdir)
        test_dir = os.path.join(os.getcwd(), out_subdir)
        print(f"Golden directory: {golden_dir}")
        print(f"Test directory: {test_dir}")

        # Compare the rgb data (larger tolerance due to denoising differences)
        self.compare_images_with_mean_diff(golden_dir, test_dir, "rgb", self.RGB_MEAN_DIFF_TOLERANCE)
        # Compare the depth data (smaller tolerance since it is not influenced by denoising)
        self.compare_npy_files(
            golden_dir, test_dir, "distance_to_image_plane", mean_diff_tolerance=self.DEPTH_MEAN_DIFF_TOLERANCE
        )
