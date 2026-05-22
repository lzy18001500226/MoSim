# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import carb
import omni.graph.core as og
import omni.kit.app
import omni.kit.test
from isaacsim.core.utils.physics import simulate_async
from isaacsim.core.utils.stage import add_reference_to_stage, create_new_stage_async
from isaacsim.storage.native import get_assets_root_path_async
from pxr import Sdf


class TestTransformListener(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await create_new_stage_async()
        self._timeline = omni.timeline.get_timeline_interface()

    # After running each test
    async def tearDown(self):
        self._timeline = None

    # ----------------------------------------------------------------------
    async def test_transform_listener(self):
        # add robot
        assets_root_path = await get_assets_root_path_async()
        if assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")
            return
        asset_path = assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        robot = add_reference_to_stage(usd_path=asset_path, prim_path="/World/panda")
        robot.GetVariantSet("Gripper").SetVariantSelection("Default")
        robot.GetVariantSet("Mesh").SetVariantSelection("Performance")

        # define graph to publish /tf
        (test_graph, new_nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("PublishTransformTree", "isaacsim.ros2.bridge.ROS2PublishTransformTree"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("PublishTransformTree.inputs:topicName", "tf"),
                    ("PublishTransformTree.inputs:targetPrims", [Sdf.Path("/World/panda")]),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "PublishTransformTree.inputs:execIn"),
                ],
            },
        )
        subscriber_node = new_nodes[-1]

        # load plugin
        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        print(ext_path)
        carb.get_framework().load_plugins(
            loaded_file_wildcards=["isaacsim.ros2.tf_viewer.plugin"],
            search_paths=[os.path.abspath(os.path.join(ext_path, "bin"))],
        )

        # load the transform listener
        from .. import _transform_listener as module

        interface = module.acquire_transform_listener_interface()
        interface.initialize(os.environ.get("ROS_DISTRO", "").lower())

        # run the simulation
        self._timeline.play()
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
            interface.spin()

        frames, transforms, relations = interface.get_transforms("panda_link0")
        # print(frames, transforms, relations)

        interface.finalize()
        module.release_transform_listener_interface(interface)

        # check frames
        gt_frames = [
            "panda_link0",
            "panda_link1",
            "panda_link2",
            "panda_link3",
            "panda_link4",
            "panda_link5",
            "panda_link6",
            "panda_link7",
            "panda_hand",
            "panda_leftfinger",
            "panda_rightfinger",
        ]
        for frame in gt_frames:
            self.assertIn(frame, frames)

        # check transforms
        self.assertTupleEqual(transforms.get("panda_link0", tuple()), ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0)))

        # check relations
        gt_relations = [
            ("panda_link1", "panda_link0"),
            ("panda_link2", "panda_link1"),
            ("panda_link3", "panda_link2"),
            ("panda_link4", "panda_link3"),
            ("panda_link5", "panda_link4"),
            ("panda_link6", "panda_link5"),
            ("panda_link7", "panda_link6"),
            ("panda_hand", "panda_link7"),
            ("panda_leftfinger", "panda_hand"),
            ("panda_rightfinger", "panda_hand"),
        ]
        for relation in gt_relations:
            self.assertIn(relation, relations)
