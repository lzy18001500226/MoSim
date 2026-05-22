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


import asyncio
from re import I

import carb
import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.kit.test
from isaacsim.core.api.robots import Robot
from isaacsim.core.utils.physics import simulate_async
from isaacsim.core.utils.stage import open_stage_async
from isaacsim.storage.native import get_assets_root_path_async


class TestArticulationControllerNode(ogts.OmniGraphTestCase):
    async def setUp(self):
        """Set up  test environment, to be torn down when done"""
        await omni.usd.get_context().new_stage_async()
        self._timeline = omni.timeline.get_timeline_interface()
        # add franka robot for test
        assets_root_path = await get_assets_root_path_async()
        if assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")
            return
        (result, error) = await open_stage_async(
            assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        )

    # ----------------------------------------------------------------------
    async def tearDown(self):
        """Get rid of temporary data used by the test"""
        await omni.kit.app.get_app().next_update_async()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)
        await omni.kit.app.get_app().next_update_async()
        return

    # ----------------------------------------------------------------------
    async def test_joint_name_ogn(self):
        (test_graph, new_nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("JointNameArray", "omni.graph.nodes.ConstructArray"),
                    ("JointCommandArray", "omni.graph.nodes.ConstructArray"),
                    ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
                ],
                og.Controller.Keys.CREATE_ATTRIBUTES: [
                    ("JointCommandArray.inputs:input1", "double"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("JointNameArray.inputs:arraySize", 2),
                    ("JointNameArray.inputs:arrayType", "token[]"),
                    ("JointNameArray.inputs:input0", "panda_joint2"),
                    ("JointNameArray.inputs:input1", "panda_joint3"),
                    ("JointCommandArray.inputs:arraySize", 2),
                    ("JointCommandArray.inputs:arrayType", "double[]"),
                    ("JointCommandArray.inputs:input0", -1.0),
                    ("JointCommandArray.inputs:input1", 1.2),
                    ("ArticulationController.inputs:robotPath", "/panda"),
                ],
                og.Controller.Keys.CREATE_ATTRIBUTES: [
                    ("JointNameArray.inputs:input1", "token"),
                    ("JointCommandArray.inputs:input1", "double"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
                    ("JointNameArray.outputs:array", "ArticulationController.inputs:jointNames"),
                    ("JointCommandArray.outputs:array", "ArticulationController.inputs:positionCommand"),
                ],
            },
        )

        await og.Controller.evaluate(test_graph)

        # check where the joints are after evaluate
        robot = Robot(prim_path="/panda", name="franka")
        self._timeline.play()
        await simulate_async(2)
        robot.initialize()

        self.assertAlmostEqual(robot.get_joint_positions()[1], -1.0, delta=0.001)
        self.assertAlmostEqual(robot.get_joint_positions()[2], 1.2, delta=0.002)

    # ----------------------------------------------------------------------
    async def test_joint_index_ogn(self):
        (test_graph, new_nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("Joint1Index", "omni.graph.nodes.ConstantInt"),
                    ("Joint2Index", "omni.graph.nodes.ConstantInt"),
                    ("JointIndexArray", "omni.graph.nodes.ConstructArray"),
                    ("Joint1Position", "omni.graph.nodes.ConstantDouble"),
                    ("Joint2Position", "omni.graph.nodes.ConstantDouble"),
                    ("JointCommandArray", "omni.graph.nodes.ConstructArray"),
                    ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
                ],
                og.Controller.Keys.CREATE_ATTRIBUTES: [
                    ("JointIndexArray.inputs:input1", "int"),
                    ("JointCommandArray.inputs:input1", "double"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("Joint1Index.inputs:value", 1),
                    ("Joint2Index.inputs:value", 2),
                    ("Joint1Position.inputs:value", -1.0),
                    ("Joint2Position.inputs:value", 1.2),
                    ("JointIndexArray.inputs:arraySize", 2),
                    ("JointCommandArray.inputs:arraySize", 2),
                    ("ArticulationController.inputs:robotPath", "/panda"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
                    ("Joint1Index.inputs:value", "JointIndexArray.inputs:input0"),
                    ("Joint2Index.inputs:value", "JointIndexArray.inputs:input1"),
                    ("JointIndexArray.outputs:array", "ArticulationController.inputs:jointIndices"),
                    ("Joint1Position.inputs:value", "JointCommandArray.inputs:input0"),
                    ("Joint2Position.inputs:value", "JointCommandArray.inputs:input1"),
                    ("JointCommandArray.outputs:array", "ArticulationController.inputs:positionCommand"),
                ],
            },
        )

        await og.Controller.evaluate(test_graph)

        # check where the joints are after evaluate
        robot = Robot(prim_path="/panda", name="franka")
        self._timeline.play()
        await simulate_async(2)
        robot.initialize()

        self.assertAlmostEqual(robot.get_joint_positions()[1], -1.0, delta=0.002)
        self.assertAlmostEqual(robot.get_joint_positions()[2], 1.2, delta=0.002)

    # ----------------------------------------------------------------------
    async def test_full_array_no_index_ogn(self):
        (test_graph, new_nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("Joint1Position", "omni.graph.nodes.ConstantDouble"),
                    ("Joint2Position", "omni.graph.nodes.ConstantDouble"),
                    ("JointCommandArray", "omni.graph.nodes.ConstructArray"),
                    ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
                ],
                og.Controller.Keys.CREATE_ATTRIBUTES: [
                    ("JointCommandArray.inputs:input1", "double"),
                    ("JointCommandArray.inputs:input2", "double"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("Joint1Position.inputs:value", -1.0),
                    ("Joint2Position.inputs:value", 1.2),
                    ("JointCommandArray.inputs:arraySize", 9),
                    ("ArticulationController.inputs:robotPath", "/panda"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
                    ("Joint1Position.inputs:value", "JointCommandArray.inputs:input1"),
                    ("Joint2Position.inputs:value", "JointCommandArray.inputs:input2"),
                    ("JointCommandArray.outputs:array", "ArticulationController.inputs:positionCommand"),
                ],
            },
        )

        await og.Controller.evaluate(test_graph)

        # check where the joints are after evaluate
        robot = Robot(prim_path="/panda", name="franka")
        self._timeline.play()
        await simulate_async(2)
        robot.initialize()

        self.assertAlmostEqual(robot.get_joint_positions()[1], -1.0, delta=0.01)
        self.assertAlmostEqual(robot.get_joint_positions()[2], 1.2, delta=0.003)

    # ----------------------------------------------------------------------
    async def test_single_joint_name_ogn(self):
        (test_graph, new_nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("Joint1Name", "omni.graph.nodes.ConstantToken"),
                    ("JointNameArray", "omni.graph.nodes.ConstructArray"),
                    ("Joint1Position", "omni.graph.nodes.ConstantDouble"),
                    ("JointCommandArray", "omni.graph.nodes.ConstructArray"),
                    ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("Joint1Name.inputs:value", "panda_joint3"),
                    ("Joint1Position.inputs:value", 1.7),
                    ("JointNameArray.inputs:arraySize", 1),
                    ("JointCommandArray.inputs:arraySize", 1),
                    ("ArticulationController.inputs:robotPath", "/panda"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
                    ("Joint1Name.inputs:value", "JointNameArray.inputs:input0"),
                    ("JointNameArray.outputs:array", "ArticulationController.inputs:jointNames"),
                    ("Joint1Position.inputs:value", "JointCommandArray.inputs:input0"),
                    ("JointCommandArray.outputs:array", "ArticulationController.inputs:positionCommand"),
                ],
            },
        )

        await og.Controller.evaluate(test_graph)

        # check where the joints are after evaluate
        robot = Robot(prim_path="/panda", name="franka")
        self._timeline.play()
        await simulate_async(2)
        robot.initialize()

        self.assertAlmostEqual(robot.get_joint_positions()[2], 1.7, delta=0.002)
        self.assertGreater(abs(robot.get_joint_positions()[3] - 1.7), 0.1)

    # ----------------------------------------------------------------------
    async def test_single_joint_index_ogn(self):
        (test_graph, new_nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("Joint1Index", "omni.graph.nodes.ConstantInt"),
                    ("JointIndexArray", "omni.graph.nodes.ConstructArray"),
                    ("Joint1Position", "omni.graph.nodes.ConstantDouble"),
                    ("JointCommandArray", "omni.graph.nodes.ConstructArray"),
                    ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("Joint1Index.inputs:value", 2),
                    ("Joint1Position.inputs:value", 1.7),
                    ("JointIndexArray.inputs:arraySize", 1),
                    ("JointCommandArray.inputs:arraySize", 1),
                    ("ArticulationController.inputs:robotPath", "/panda"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
                    ("Joint1Index.inputs:value", "JointIndexArray.inputs:input0"),
                    ("JointIndexArray.outputs:array", "ArticulationController.inputs:jointIndices"),
                    ("Joint1Position.inputs:value", "JointCommandArray.inputs:input0"),
                    ("JointCommandArray.outputs:array", "ArticulationController.inputs:positionCommand"),
                ],
            },
        )

        await og.Controller.evaluate(test_graph)

        # check where the joints are after evaluate
        robot = Robot(prim_path="/panda", name="franka")
        self._timeline.play()
        await simulate_async(2)
        robot.initialize()

        self.assertAlmostEqual(robot.get_joint_positions()[2], 1.7, delta=0.002)
        self.assertGreater(abs(robot.get_joint_positions()[3] - 1.7), 0.002)

    # ----------------------------------------------------------------------
    async def test_joint_indices_different_shape(self):
        (test_graph, new_nodes, _, _) = og.Controller.edit(
            {"graph_path": "/ActionGraph", "evaluator_name": "execution"},
            {
                og.Controller.Keys.CREATE_NODES: [
                    ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                    ("Joint1Index", "omni.graph.nodes.ConstantInt"),
                    ("JointIndexArray", "omni.graph.nodes.ConstructArray"),
                    ("Joint1Position", "omni.graph.nodes.ConstantDouble"),
                    ("JointCommandArray", "omni.graph.nodes.ConstructArray"),
                    ("ArticulationController", "isaacsim.core.nodes.IsaacArticulationController"),
                ],
                og.Controller.Keys.SET_VALUES: [
                    ("Joint1Index.inputs:value", 2),
                    ("Joint1Position.inputs:value", 1.7),
                    ("JointIndexArray.inputs:arraySize", 1),
                    ("JointCommandArray.inputs:arraySize", 1),
                    ("ArticulationController.inputs:robotPath", "/panda"),
                ],
                og.Controller.Keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "ArticulationController.inputs:execIn"),
                    ("Joint1Index.inputs:value", "JointIndexArray.inputs:input0"),
                    ("JointIndexArray.outputs:array", "ArticulationController.inputs:jointIndices"),
                    ("Joint1Position.inputs:value", "JointCommandArray.inputs:input0"),
                    ("JointCommandArray.outputs:array", "ArticulationController.inputs:positionCommand"),
                ],
            },
        )

        # Initialize robot
        robot = Robot(prim_path="/panda", name="franka")
        self._timeline.play()
        await og.Controller.evaluate(test_graph)
        await simulate_async(2)
        robot.initialize()

        # Store initial joint positions
        initial_position = robot.get_joint_positions()[2]

        # Access nodes directly by their paths
        articulation_controller_node = "/ActionGraph/ArticulationController"
        joint1_position_node = "/ActionGraph/Joint1Position"

        # Change the joint position value directly
        og.Controller.attribute("inputs:value", joint1_position_node).set(0.5)

        # Update the joint indices to have a different shape but same content
        current_indices = og.Controller.attribute("inputs:jointIndices", articulation_controller_node).get()
        # Reshape to 1D if it's not already
        reshaped_indices = current_indices.reshape(-1)
        og.Controller.attribute("inputs:jointIndices", articulation_controller_node).set(reshaped_indices)

        # Evaluate the graph again with the updated values
        await og.Controller.evaluate(test_graph)
        await simulate_async(2)

        new_position = robot.get_joint_positions()[2]

        self.assertNotAlmostEqual(initial_position, new_position, delta=0.01)
        self.assertAlmostEqual(new_position, 0.5, delta=0.01)
