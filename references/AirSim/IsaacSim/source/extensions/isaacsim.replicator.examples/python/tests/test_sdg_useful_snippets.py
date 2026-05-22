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

import carb.settings
import omni.kit
import omni.usd
from isaacsim.test.utils.file_validation import validate_folder_contents


class TestSDGUsefulSnippets(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.kit.app.get_app().next_update_async()
        omni.usd.get_context().new_stage()
        await omni.kit.app.get_app().next_update_async()
        self.original_dlss_exec_mode = carb.settings.get_settings().get("rtx/post/dlss/execMode")

    async def tearDown(self):
        omni.usd.get_context().close_stage()
        await omni.kit.app.get_app().next_update_async()
        # In some cases the test will end before the asset is loaded, in this case wait for assets to load
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            await omni.kit.app.get_app().next_update_async()
        carb.settings.get_settings().set("rtx/post/dlss/execMode", self.original_dlss_exec_mode)

    async def test_sdg_snippet_multi_camera(self):
        import os

        import omni.kit
        import omni.replicator.core as rep
        import omni.usd
        from omni.replicator.core import AnnotatorRegistry, Writer
        from PIL import Image
        from pxr import Sdf, UsdGeom

        NUM_FRAMES = 5

        # Save rgb image to file
        def save_rgb(rgb_data, file_name):
            rgb_img = Image.fromarray(rgb_data).convert("RGBA")
            rgb_img.save(file_name + ".png")

        # Randomize cube color every frame using a replicator randomizer
        def cube_color_randomizer():
            cube_prims = rep.get.prims(path_pattern="Cube")
            with cube_prims:
                rep.randomizer.color(colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1)))
            return cube_prims.node

        # Access data through a custom replicator writer
        class MyWriter(Writer):
            def __init__(self, rgb: bool = True):
                self._frame_id = 0
                self.annotators = []
                if rgb:
                    self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))
                # Create writer output directory
                self.file_path = os.path.join(os.getcwd(), "_out_mc_writer", "")
                print(f"Writing writer data to {self.file_path}")
                dir = os.path.dirname(self.file_path)
                os.makedirs(dir, exist_ok=True)

            def write(self, data):
                for annotator in data.keys():
                    annotator_split = annotator.split("-")
                    if len(annotator_split) > 1:
                        render_product_name = annotator_split[-1]
                    if annotator.startswith("rgb"):
                        save_rgb(data[annotator], f"{self.file_path}/{render_product_name}_frame_{self._frame_id}")
                self._frame_id += 1

        rep.WriterRegistry.register(MyWriter)

        # Create a new stage with a dome light
        omni.usd.get_context().new_stage()
        stage = omni.usd.get_context().get_stage()
        dome_light = stage.DefinePrim("/World/DomeLight", "DomeLight")
        dome_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(900.0)

        # Create cube
        cube_prim = stage.DefinePrim("/World/Cube", "Cube")
        UsdGeom.Xformable(cube_prim).AddTranslateOp().Set((0.0, 5.0, 1.0))

        # Register cube color randomizer to trigger on every frame
        rep.randomizer.register(cube_color_randomizer)
        with rep.trigger.on_frame():
            rep.randomizer.cube_color_randomizer()

        # Create cameras
        camera_prim1 = stage.DefinePrim("/World/Camera1", "Camera")
        UsdGeom.Xformable(camera_prim1).AddTranslateOp().Set((0.0, 10.0, 20.0))
        UsdGeom.Xformable(camera_prim1).AddRotateXYZOp().Set((-15.0, 0.0, 0.0))

        camera_prim2 = stage.DefinePrim("/World/Camera2", "Camera")
        UsdGeom.Xformable(camera_prim2).AddTranslateOp().Set((-10.0, 15.0, 15.0))
        UsdGeom.Xformable(camera_prim2).AddRotateXYZOp().Set((-45.0, 0.0, 45.0))

        # Create render products
        rp1 = rep.create.render_product(str(camera_prim1.GetPrimPath()), resolution=(320, 320))
        rp2 = rep.create.render_product(str(camera_prim2.GetPrimPath()), resolution=(640, 640))
        rp3 = rep.create.render_product("/OmniverseKit_Persp", (1024, 1024))

        # Access the data through a custom writer
        writer = rep.WriterRegistry.get("MyWriter")
        writer.initialize(rgb=True)
        writer.attach([rp1, rp2, rp3])

        # Access the data through annotators
        rgb_annotators = []
        for rp in [rp1, rp2, rp3]:
            rgb = rep.AnnotatorRegistry.get_annotator("rgb")
            rgb.attach(rp)
            rgb_annotators.append(rgb)

        # Create annotator output directory
        file_path = os.path.join(os.getcwd(), "_out_mc_annot", "")
        print(f"Writing annotator data to {file_path}")
        dir = os.path.dirname(file_path)
        os.makedirs(dir, exist_ok=True)

        # Data will be captured manually using step
        rep.orchestrator.set_capture_on_play(False)

        async def run_example_async():
            for i in range(NUM_FRAMES):
                # The step function provides new data to the annotators, triggers the randomizers and the writer
                await rep.orchestrator.step_async(rt_subframes=4)
                for j, rgb_annot in enumerate(rgb_annotators):
                    save_rgb(rgb_annot.get_data(), f"{dir}/rp{j}_step_{i}")

        await run_example_async()

        # Validate the output directory contents
        folder_contents_success_annot = validate_folder_contents(path=file_path, expected_counts={"png": 15})
        folder_contents_success_writer = validate_folder_contents(path=writer.file_path, expected_counts={"png": 15})
        self.assertTrue(folder_contents_success_annot, f"Output directory contents validation failed for {file_path}")
        self.assertTrue(
            folder_contents_success_writer, f"Output directory contents validation failed for {writer.file_path}"
        )

    async def test_sdg_snippet_simulation_get_data(self):
        import json
        import os

        import carb.settings
        import numpy as np
        import omni
        import omni.replicator.core as rep
        from isaacsim.core.api import World
        from isaacsim.core.api.objects import DynamicCuboid
        from isaacsim.core.utils.semantics import add_labels
        from PIL import Image

        # Util function to save rgb annotator data
        def write_rgb_data(rgb_data, file_path):
            rgb_img = Image.fromarray(rgb_data).convert("RGBA")
            rgb_img.save(file_path + ".png")

        # Util function to save semantic segmentation annotator data
        def write_sem_data(sem_data, file_path):
            id_to_labels = sem_data["info"]["idToLabels"]
            with open(file_path + ".json", "w") as f:
                json.dump(id_to_labels, f)
            sem_image_data = sem_data["data"]
            sem_img = Image.fromarray(sem_image_data).convert("RGBA")
            sem_img.save(file_path + ".png")

        # Create a new stage with the default ground plane
        omni.usd.get_context().new_stage()

        # Setup the simulation world
        world = World()
        world.scene.add_default_ground_plane()

        # Setting capture on play to False will prevent the replicator from capturing data each frame
        carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)

        # Set DLSS to Quality mode (2) for best SDG results , options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto)))))))))
        carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

        # Create a camera and render product to collect the data from
        cam = rep.create.camera(position=(5, 5, 5), look_at=(0, 0, 0))
        rp = rep.create.render_product(cam, (512, 512))

        # Set the output directory for the data
        out_dir = os.path.join(os.getcwd(), "_out_sim_event")
        os.makedirs(out_dir, exist_ok=True)
        print(f"Outputting data to {out_dir}..")

        # Example of using a writer to save the data
        writer = rep.WriterRegistry.get("BasicWriter")
        writer.initialize(
            output_dir=f"{out_dir}/writer", rgb=True, semantic_segmentation=True, colorize_semantic_segmentation=True
        )
        writer.attach(rp)

        # Run a preview to ensure the replicator graph is initialized
        rep.orchestrator.preview()

        # Example of accessing the data directly from annotators
        rgb_annot = rep.AnnotatorRegistry.get_annotator("rgb")
        rgb_annot.attach(rp)
        sem_annot = rep.AnnotatorRegistry.get_annotator("semantic_segmentation", init_params={"colorize": True})
        sem_annot.attach(rp)

        async def run_example_async():
            await world.initialize_simulation_context_async()
            await world.reset_async()

            # Spawn and drop a few cubes, capture data when they stop moving
            for i in range(5):
                cuboid = world.scene.add(
                    DynamicCuboid(prim_path=f"/World/Cuboid_{i}", name=f"Cuboid_{i}", position=(0, 0, 10 + i))
                )
                add_labels(cuboid.prim, labels=["Cuboid"], instance_name="class")

                for s in range(500):
                    await omni.kit.app.get_app().next_update_async()
                    vel = np.linalg.norm(cuboid.get_linear_velocity())
                    if vel < 0.1:
                        print(f"Cube_{i} stopped moving after {s} simulation steps, writing data..")
                        # Trigger the writer and update the annotators with new data
                        await rep.orchestrator.step_async(rt_subframes=4, delta_time=0.0, pause_timeline=False)
                        write_rgb_data(rgb_annot.get_data(), f"{out_dir}/Cube_{i}_step_{s}_rgb")
                        write_sem_data(sem_annot.get_data(), f"{out_dir}/Cube_{i}_step_{s}_sem")
                        break

            await rep.orchestrator.wait_until_complete_async()

        await run_example_async()

        # Validate the output directory contents
        annot_out_dir = out_dir
        folder_contents_success_annot = validate_folder_contents(
            path=annot_out_dir, expected_counts={"png": 10, "json": 5}
        )
        writer_out_dir = f"{out_dir}/writer"
        folder_contents_success_writer = validate_folder_contents(
            path=writer_out_dir, expected_counts={"png": 10, "json": 5}
        )
        self.assertTrue(
            folder_contents_success_annot, f"Output directory contents validation failed for {annot_out_dir}"
        )
        self.assertTrue(
            folder_contents_success_writer, f"Output directory contents validation failed for {writer_out_dir}"
        )

    async def test_sdg_snippet_custom_event_and_write(self):
        import os

        import omni.replicator.core as rep
        import omni.usd

        omni.usd.get_context().new_stage()
        distance_light = rep.create.light(rotation=(315, 0, 0), intensity=4000, light_type="distant")

        large_cube = rep.create.cube(scale=1.25, position=(1, 1, 0))
        small_cube = rep.create.cube(scale=0.75, position=(-1, -1, 0))
        large_cube_prim = large_cube.get_output_prims()["prims"][0]
        small_cube_prim = small_cube.get_output_prims()["prims"][0]

        rp = rep.create.render_product("/OmniverseKit_Persp", (512, 512))
        writer = rep.WriterRegistry.get("BasicWriter")
        out_dir = os.path.join(os.getcwd(), "_out_custom_event")
        print(f"Writing data to {out_dir}")
        writer.initialize(output_dir=out_dir, rgb=True)
        writer.attach(rp)

        with rep.trigger.on_custom_event(event_name="randomize_large_cube"):
            with large_cube:
                rep.randomizer.rotation()

        with rep.trigger.on_custom_event(event_name="randomize_small_cube"):
            with small_cube:
                rep.randomizer.rotation()

        async def run_example_async():
            print(f"Randomizing small cube")
            rep.utils.send_og_event(event_name="randomize_small_cube")
            print("Capturing frame")
            await rep.orchestrator.step_async(rt_subframes=8)

            print("Moving small cube")
            small_cube_prim.GetAttribute("xformOp:translate").Set((-2, -2, 0))
            print("Capturing frame")
            await rep.orchestrator.step_async(rt_subframes=8)

            print(f"Randomizing large cube")
            rep.utils.send_og_event(event_name="randomize_large_cube")
            print("Capturing frame")
            await rep.orchestrator.step_async(rt_subframes=8)

            print("Moving large cube")
            large_cube_prim.GetAttribute("xformOp:translate").Set((2, 2, 0))
            print("Capturing frame")
            await rep.orchestrator.step_async(rt_subframes=8)

            # Wait until all the data is saved to disk
            await rep.orchestrator.wait_until_complete_async()

        await run_example_async()

        # Validate the output directory contents
        folder_contents_success = validate_folder_contents(path=out_dir, expected_counts={"png": 4})
        self.assertTrue(folder_contents_success, f"Output directory contents validation failed for {out_dir}")

    async def test_sdg_snippet_motion_blur_short(self):
        import asyncio
        import os

        import carb.settings
        import omni.kit.app
        import omni.replicator.core as rep
        import omni.timeline
        import omni.usd
        from isaacsim.storage.native import get_assets_root_path
        from pxr import PhysxSchema, Sdf, UsdGeom, UsdPhysics

        # Paths to the animated and physics-ready assets
        PHYSICS_ASSET_URL = "/Isaac/Props/YCB/Axis_Aligned_Physics/003_cracker_box.usd"
        ANIM_ASSET_URL = "/Isaac/Props/YCB/Axis_Aligned/003_cracker_box.usd"

        # -z velocities and start locations of the animated (left side) and physics (right side) assets (stage units/s)
        ASSET_VELOCITIES = [0, 5, 10]
        ASSET_X_MIRRORED_LOCATIONS = [(0.5, 0, 0.3), (0.3, 0, 0.3), (0.1, 0, 0.3)]

        # Used to calculate how many frames to animate the assets to maintain the same velocity as the physics assets
        ANIMATION_DURATION = 10

        # Create a new stage with animated and physics-enabled assets with synchronized motion
        def setup_stage():
            # Create new stage
            omni.usd.get_context().new_stage()
            stage = omni.usd.get_context().get_stage()
            timeline = omni.timeline.get_timeline_interface()
            timeline.set_end_time(ANIMATION_DURATION)

            # Create lights
            dome_light = stage.DefinePrim("/World/DomeLight", "DomeLight")
            dome_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(100.0)
            distant_light = stage.DefinePrim("/World/DistantLight", "DistantLight")
            if not distant_light.GetAttribute("xformOp:rotateXYZ"):
                UsdGeom.Xformable(distant_light).AddRotateXYZOp()
            distant_light.GetAttribute("xformOp:rotateXYZ").Set((-75, 0, 0))
            distant_light.CreateAttribute("inputs:intensity", Sdf.ValueTypeNames.Float).Set(2500)

            # Setup the physics assets with gravity disabled and the requested velocity
            assets_root_path = get_assets_root_path()
            physics_asset_url = assets_root_path + PHYSICS_ASSET_URL
            for loc, vel in zip(ASSET_X_MIRRORED_LOCATIONS, ASSET_VELOCITIES):
                prim = stage.DefinePrim(f"/World/physics_asset_{int(abs(vel))}", "Xform")
                prim.GetReferences().AddReference(physics_asset_url)
                if not prim.GetAttribute("xformOp:translate"):
                    UsdGeom.Xformable(prim).AddTranslateOp()
                prim.GetAttribute("xformOp:translate").Set(loc)
                prim.GetAttribute("physxRigidBody:disableGravity").Set(True)
                prim.GetAttribute("physxRigidBody:angularDamping").Set(0.0)
                prim.GetAttribute("physxRigidBody:linearDamping").Set(0.0)
                prim.GetAttribute("physics:velocity").Set((0, 0, -vel))

            # Setup animated assets maintaining the same velocity as the physics assets
            anim_asset_url = assets_root_path + ANIM_ASSET_URL
            for loc, vel in zip(ASSET_X_MIRRORED_LOCATIONS, ASSET_VELOCITIES):
                start_loc = (-loc[0], loc[1], loc[2])
                prim = stage.DefinePrim(f"/World/anim_asset_{int(abs(vel))}", "Xform")
                prim.GetReferences().AddReference(anim_asset_url)
                if not prim.GetAttribute("xformOp:translate"):
                    UsdGeom.Xformable(prim).AddTranslateOp()
                anim_distance = vel * ANIMATION_DURATION
                end_loc = (start_loc[0], start_loc[1], start_loc[2] - anim_distance)
                end_keyframe = timeline.get_time_codes_per_seconds() * ANIMATION_DURATION
                # Timesampled keyframe (animated) translation
                prim.GetAttribute("xformOp:translate").Set(start_loc, time=0)
                prim.GetAttribute("xformOp:translate").Set(end_loc, time=end_keyframe)

        # Capture motion blur frames with the given delta time step and render mode
        async def run_motion_blur_example_async(
            num_frames=3, custom_delta_time=None, use_path_tracing=True, pt_subsamples=8, pt_spp=64
        ):
            # Create a new stage with the assets
            setup_stage()
            stage = omni.usd.get_context().get_stage()

            # Set DLSS to Quality mode (2) for best SDG results , options: 0 (Performance), 1 (Balanced), 2 (Quality), 3 (Auto))))))))))))))))
            carb.settings.get_settings().set("rtx/post/dlss/execMode", 2)

            # Set replicator settings (capture only on request and enable motion blur)
            carb.settings.get_settings().set("/omni/replicator/captureOnPlay", False)
            carb.settings.get_settings().set("/omni/replicator/captureMotionBlur", True)

            # Set motion blur settings based on the render mode
            if use_path_tracing:
                print(f"[MotionBlur] Setting PathTracing render mode motion blur settings")
                carb.settings.get_settings().set("/rtx/rendermode", "PathTracing")
                # (int): Total number of samples for each rendered pixel, per frame.
                carb.settings.get_settings().set("/rtx/pathtracing/spp", pt_spp)
                # (int): Maximum number of samples to accumulate per pixel. When this count is reached the rendering stops until a scene or setting change is detected, restarting the rendering process. Set to 0 to remove this limit.
                carb.settings.get_settings().set("/rtx/pathtracing/totalSpp", pt_spp)
                carb.settings.get_settings().set("/rtx/pathtracing/optixDenoiser/enabled", 0)
                # Number of sub samples to render if in PathTracing render mode and motion blur is enabled.
                carb.settings.get_settings().set("/omni/replicator/pathTracedMotionBlurSubSamples", pt_subsamples)
            else:
                print(f"[MotionBlur] Setting RayTracedLighting render mode motion blur settings")
                carb.settings.get_settings().set("/rtx/rendermode", "RayTracedLighting")
                # 0: Disabled, 1: TAA, 2: FXAA, 3: DLSS, 4:RTXAA
                carb.settings.get_settings().set("/rtx/post/aa/op", 2)
                # (float): The fraction of the largest screen dimension to use as the maximum motion blur diameter.
                carb.settings.get_settings().set("/rtx/post/motionblur/maxBlurDiameterFraction", 0.02)
                # (float): Exposure time fraction in frames (1.0 = one frame duration) to sample.
                carb.settings.get_settings().set("/rtx/post/motionblur/exposureFraction", 1.0)
                # (int): Number of samples to use in the filter. A higher number improves quality at the cost of performance.
                carb.settings.get_settings().set("/rtx/post/motionblur/numSamples", 8)

            # Setup camera and writer
            camera = rep.create.camera(position=(0, 1.5, 0), look_at=(0, 0, 0), name="MotionBlurCam")
            render_product = rep.create.render_product(camera, (1280, 720))
            basic_writer = rep.WriterRegistry.get("BasicWriter")
            delta_time_str = "None" if custom_delta_time is None else f"{custom_delta_time:.4f}"
            render_mode_str = f"pt_subsamples_{pt_subsamples}_spp_{pt_spp}" if use_path_tracing else "rt"
            output_directory = os.path.join(os.getcwd(), f"_out_motion_blur_dt_{delta_time_str}_{render_mode_str}")
            print(f"[MotionBlur] Output directory: {output_directory}")
            basic_writer.initialize(output_dir=output_directory, rgb=True)
            basic_writer.attach(render_product)

            # Run a few updates to make sure all materials are fully loaded for capture
            for _ in range(50):
                await omni.kit.app.get_app().next_update_async()

            # Use the physics scene to modify the physics FPS (if needed) to guarantee motion samples at any custom delta time
            physx_scene = None
            for prim in stage.Traverse():
                if prim.IsA(UsdPhysics.Scene):
                    physx_scene = PhysxSchema.PhysxSceneAPI.Apply(prim)
                    break
            if physx_scene is None:
                print(f"[MotionBlur] Creating a new PhysicsScene")
                physics_scene = UsdPhysics.Scene.Define(stage, "/PhysicsScene")
                physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/PhysicsScene"))

            # Check the target physics depending on the custom delta time and the render mode
            target_physics_fps = stage.GetTimeCodesPerSecond() if custom_delta_time is None else 1 / custom_delta_time
            if use_path_tracing:
                target_physics_fps *= pt_subsamples

            # Check if the physics FPS needs to be increased to match the custom delta time
            orig_physics_fps = physx_scene.GetTimeStepsPerSecondAttr().Get()
            if target_physics_fps > orig_physics_fps:
                print(f"[MotionBlur] Changing physics FPS from {orig_physics_fps} to {target_physics_fps}")
                physx_scene.GetTimeStepsPerSecondAttr().Set(target_physics_fps)

            # Start the timeline for physics updates in the step function
            timeline = omni.timeline.get_timeline_interface()
            timeline.play()

            # Capture frames
            for i in range(num_frames):
                print(f"[MotionBlur] \tCapturing frame {i}")
                await rep.orchestrator.step_async(delta_time=custom_delta_time)

            # Restore the original physics FPS
            if target_physics_fps > orig_physics_fps:
                print(f"[MotionBlur] Restoring physics FPS from {target_physics_fps} to {orig_physics_fps}")
                physx_scene.GetTimeStepsPerSecondAttr().Set(orig_physics_fps)

            # Switch back to the raytracing render mode
            if use_path_tracing:
                print(f"[MotionBlur] Restoring render mode to RayTracedLighting")
                carb.settings.get_settings().set("/rtx/rendermode", "RayTracedLighting")

            # Wait until all the data is saved to disk
            await rep.orchestrator.wait_until_complete_async()

            # Validate the output directory contents
            folder_contents_success = validate_folder_contents(path=output_directory, expected_counts={"png": 3})
            self.assertTrue(
                folder_contents_success, f"Output directory contents validation failed for {output_directory}"
            )

        async def run_motion_blur_examples_async():
            motion_blur_step_duration = [None, 1 / 240]  # [None, 1 / 30, 1 / 60, 1 / 240]
            for custom_delta_time in motion_blur_step_duration:
                # RayTracing examples
                await run_motion_blur_example_async(custom_delta_time=custom_delta_time, use_path_tracing=False)
                # PathTracing examples
                spps = [32]  # [32, 128]
                motion_blur_sub_samples = [4]  # [4, 16]
                for motion_blur_sub_sample in motion_blur_sub_samples:
                    for spp in spps:
                        await run_motion_blur_example_async(
                            custom_delta_time=custom_delta_time,
                            use_path_tracing=True,
                            pt_subsamples=motion_blur_sub_sample,
                            pt_spp=spp,
                        )

        await run_motion_blur_examples_async()
