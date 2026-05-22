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


import os

import omni.kit.app
import omni.kit.commands
import omni.kit.test
import omni.replicator.core as rep
import omni.timeline
import omni.usd
from isaacsim.replicator.synthetic_recorder.synthetic_recorder import RecorderState, SyntheticRecorder

BASIC_WRITER_ANNOTATORS = (
    "rgb",
    "bounding_box_2d_tight",
    "bounding_box_2d_loose",
    "semantic_segmentation",
    "instance_id_segmentation",
    "instance_segmentation",
    "distance_to_camera",
    "distance_to_image_plane",
    "bounding_box_3d",
    "occlusion",
    "normals",
    "motion_vectors",
    "camera_params",
    "pointcloud",
    "skeleton_data",
)

BASIC_WRITER_ANNOTATORS_ARGS = (
    "colorize_semantic_segmentation",
    "colorize_instance_id_segmentation",
    "colorize_instance_segmentation",
    "pointcloud_include_unlabelled",
)


class TestRecorderBasic(omni.kit.test.AsyncTestCase):
    """
    Test the basic functionality of the recorder.
    """

    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def setup_stage_empty_async(self):
        await omni.usd.get_context().new_stage_async()

    async def setup_stage_with_no_semantics(self):
        await omni.usd.get_context().new_stage_async()
        rep.create.cube()
        rep.create.sphere(position=(1, 1, 0))

    async def setup_stage_with_semantics(self):
        await omni.usd.get_context().new_stage_async()
        rep.create.cube(semantics=[("class", "cube")])
        rep.create.sphere(position=(1, 1, 0), semantics=[("class", "sphere")])

    async def run_recorder_loop_basic_writer_all_annotators_async(self, out_dir=None):
        # Create a new instance of the SyntheticRecorder
        recorder = SyntheticRecorder()
        recorder.num_frames = 3
        recorder.rt_subframes = 0
        recorder.control_timeline = False
        recorder.verbose = True

        # Use the basic writer with all annotators enabled
        recorder.writer_name = "BasicWriter"
        recorder.basic_writer_params = {annot: True for annot in BASIC_WRITER_ANNOTATORS}
        recorder.basic_writer_params.update({annot_args: True for annot_args in BASIC_WRITER_ANNOTATORS_ARGS})

        # Render products, will created and destroyed every new capture
        rep_cam_node = rep.create.camera(position=(0, 0, 5), look_at=(0, 0, 0), name="my_rep_camera")
        cam_path = rep_cam_node.get_output_prims()["prims"][0].GetChildren()[0].GetPath()
        recorder.rp_data = [
            ["/OmniverseKit_Persp", 256, 256, "my_rp_name"],
            ["/OmniverseKit_Persp", 256, 256, ""],
            [cam_path, 256, 256, "my_cam_rp_name"],
            [cam_path, 256, 256, ""],
        ]

        # Location to save the recording folder
        recorder.out_working_dir = os.getcwd()

        # Run the recorder a few times
        for i in range(3):
            recorder.out_dir = f"_out_sdrec_test_{i}" if out_dir is None else f"{out_dir}_{i}"
            print(f"Starting recorder {i}; writing data to {os.path.join(recorder.out_working_dir, recorder.out_dir)}")
            await recorder.start_stop_async()
            await omni.kit.app.get_app().next_update_async()
            self.assertTrue(
                recorder.get_state() == RecorderState.STOPPED, "Recorder did not stop after start_stop_async()"
            )

    async def test_recorder_empty_stage(self):
        await self.setup_stage_empty_async()
        await self.run_recorder_loop_basic_writer_all_annotators_async(out_dir="_out_sdrec_test_empty")

    async def test_recorder_no_semantics(self):
        await self.setup_stage_with_no_semantics()
        await self.run_recorder_loop_basic_writer_all_annotators_async(out_dir="_out_sdrec_test_no_semantics")

    async def test_recorder_with_semantics(self):
        await self.setup_stage_with_semantics()
        await self.run_recorder_loop_basic_writer_all_annotators_async(out_dir="_out_sdrec_test_with_semantics")
