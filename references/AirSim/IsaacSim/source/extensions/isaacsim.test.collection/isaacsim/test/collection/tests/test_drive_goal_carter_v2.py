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

import carb
import carb.tokens
import omni.graph.core as og

# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.   .org/3/library/unittest.html
import omni.kit.test
import usdrt.Sdf
from isaacsim.core.api import World
from isaacsim.core.utils.extensions import get_extension_path_from_name
from isaacsim.core.utils.rotations import quat_to_euler_angles
from isaacsim.core.utils.stage import open_stage_async
from isaacsim.storage.native import get_assets_root_path_async
from pxr import Gf, PhysicsSchemaTools

from .robot_helpers import init_robot_sim, setup_robot_og


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestDriveGoalCarterv2(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._timeline = omni.timeline.get_timeline_interface()

        self._assets_root_path = await get_assets_root_path_async()
        if self._assets_root_path is None:
            carb.log_error("Could not find Isaac Sim assets folder")
            return

        self._extension_path = get_extension_path_from_name("isaacsim.test.collection")

        # add in carter (from nucleus)
        self.usd_path = self._assets_root_path + "/Isaac/Robots/NVIDIA/NovaCarter/nova_carter.usd"
        (result, error) = await open_stage_async(self.usd_path)
        PhysicsSchemaTools.addGroundPlane(
            omni.usd.get_context().get_stage(), "/groundPlane", "Z", 1500, Gf.Vec3f(0, 0, 0), Gf.Vec3f(0.5)
        )

        # Make sure the stage loaded
        self.assertTrue(result)
        World.clear_instance()
        # This needs to be set so that kit updates match physics updates
        self._physics_rate = 60
        carb.settings.get_settings().set_bool("/app/runLoops/main/rateLimitEnabled", True)
        carb.settings.get_settings().set_int("/app/runLoops/main/rateLimitFrequency", int(self._physics_rate))
        carb.settings.get_settings().set_int("/persistent/simulation/minFrameRate", int(self._physics_rate))
        self._physics_dt = 1 / self._physics_rate
        self._world = World(stage_units_in_meters=1.0, physics_dt=self._physics_dt, rendering_dt=self._physics_dt)
        await self._world.initialize_simulation_context_async()

        self._stage = omni.usd.get_context().get_stage()
        self._stage.SetTimeCodesPerSecond(60.0)

        await omni.kit.app.get_app().next_update_async()
        # setup omnigraph
        self.graph_path = "/ActionGraph"
        (graph, _) = setup_robot_og(
            self.graph_path, "joint_wheel_left", "joint_wheel_right", "/nova_carter/chassis_link", 0.14, 0.4132
        )

        keys = og.Controller.Keys
        og.Controller.edit(
            graph,
            {
                keys.CREATE_NODES: [
                    ("GetPrimLocalToWorldTransform", "omni.graph.nodes.GetPrimLocalToWorldTransform"),
                    ("GetRotationQuaternion", "omni.graph.nodes.GetMatrix4Quaternion"),
                    ("GetTranslation", "omni.graph.nodes.GetMatrix4Translation"),
                    ("QuinticPathPlanner", "isaacsim.robot.wheeled_robots.QuinticPathPlanner"),
                    ("CheckGoal2D", "isaacsim.robot.wheeled_robots.CheckGoal2D"),
                    ("StanleyControlPID", "isaacsim.robot.wheeled_robots.StanleyControlPID"),
                ],
                keys.CONNECT: [
                    (self.graph_path + "/OnPlaybackTick.outputs:tick", "QuinticPathPlanner.inputs:execIn"),
                    ("QuinticPathPlanner.outputs:execOut", "CheckGoal2D.inputs:execIn"),
                    ("CheckGoal2D.outputs:execOut", "StanleyControlPID.inputs:execIn"),
                    (
                        "GetPrimLocalToWorldTransform.outputs:localToWorldTransform",
                        "GetRotationQuaternion.inputs:matrix",
                    ),
                    ("GetPrimLocalToWorldTransform.outputs:localToWorldTransform", "GetTranslation.inputs:matrix"),
                    ("GetRotationQuaternion.outputs:quaternion", "QuinticPathPlanner.inputs:currentOrientation"),
                    ("GetRotationQuaternion.outputs:quaternion", "CheckGoal2D.inputs:currentOrientation"),
                    ("GetRotationQuaternion.outputs:quaternion", "StanleyControlPID.inputs:currentOrientation"),
                    ("GetTranslation.outputs:translation", "QuinticPathPlanner.inputs:currentPosition"),
                    ("GetTranslation.outputs:translation", "CheckGoal2D.inputs:currentPosition"),
                    ("GetTranslation.outputs:translation", "StanleyControlPID.inputs:currentPosition"),
                    ("QuinticPathPlanner.outputs:pathArrays", "StanleyControlPID.inputs:pathArrays"),
                    ("QuinticPathPlanner.outputs:target", "CheckGoal2D.inputs:target"),
                    ("QuinticPathPlanner.outputs:target", "StanleyControlPID.inputs:target"),
                    ("QuinticPathPlanner.outputs:targetChanged", "CheckGoal2D.inputs:targetChanged"),
                    ("QuinticPathPlanner.outputs:targetChanged", "StanleyControlPID.inputs:targetChanged"),
                    ("CheckGoal2D.outputs:reachedGoal", "StanleyControlPID.inputs:reachedGoal"),
                    (
                        "StanleyControlPID.outputs:angularVelocity",
                        self.graph_path + "/DifferentialController.inputs:angularVelocity",
                    ),
                    (
                        "StanleyControlPID.outputs:linearVelocity",
                        self.graph_path + "/DifferentialController.inputs:linearVelocity",
                    ),
                    (self.graph_path + "/computeOdom.outputs:linearVelocity", "StanleyControlPID.inputs:currentSpeed"),
                ],
                keys.SET_VALUES: [
                    ("QuinticPathPlanner.inputs:targetPosition", (-5, -5, 0)),
                    ("QuinticPathPlanner.inputs:targetOrientation", (0, 0, 0, 1)),
                    ("GetPrimLocalToWorldTransform.inputs:usePath", False),
                    (
                        self.graph_path + "/computeOdom.inputs:chassisPrim",
                        [usdrt.Sdf.Path("/nova_carter/chassis_link")],
                    ),
                    ("GetPrimLocalToWorldTransform.inputs:prim", [usdrt.Sdf.Path("/nova_carter/chassis_link")]),
                ],
            },
        )
        omni.timeline.get_timeline_interface().set_time_codes_per_second(60)

        pass

    # After running each test
    async def tearDown(self):
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        # In some cases the test will end before the asset is loaded, in this case wait for assets to load
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            await omni.kit.app.get_app().next_update_async()
        pass

    # Actual test, notice it is "async" function, so "await" can be used if needed
    async def test_quintic_planner(self):
        # Start Simulation and wait
        self._timeline.play()

        await omni.kit.app.get_app().next_update_async()

        # get output values - path arrays (velocity, x, y, and yaw arrays concatenated into one), abbreviated target array (pos.x, pos.y, rot), and target changed bool
        pathArrays = og.Controller.get(
            og.Controller.attribute(self.graph_path + "/QuinticPathPlanner.outputs:pathArrays")
        )
        target = og.Controller.attribute(self.graph_path + "/QuinticPathPlanner.outputs:target").get()
        targetChanged = og.Controller.attribute(self.graph_path + "/QuinticPathPlanner.outputs:targetChanged").get()

        self.assertGreater(len(pathArrays), 0)  # check if path arrays were generated
        self.assertGreater(len(target), 0)  # check if target was generated
        print("target changed: ", targetChanged)
        self.assertTrue(targetChanged)  # target should be changed if first frame of simulation

        # use the following line for a test of full simulation - check that number of frames from simulation start to reaching goal is approx equal to length of each path array
        self.array_idx_len = int(len(pathArrays) / 4)

        self._timeline.stop()

        print("quintic passed")
        pass

    async def test_check_goal_2d(self):
        # Start Simulation and wait
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()

        await init_robot_sim("/nova_carter")
        await omni.kit.app.get_app().next_update_async()

        # Get position and rotation data provided to node, then set target equal to pos/rot and check for reachedGoal booleans
        pos = og.Controller.attribute(self.graph_path + "/GetTranslation.outputs:translation").get()
        _, _, rot = quat_to_euler_angles(
            og.Controller.attribute(self.graph_path + "/GetRotationQuaternion.outputs:quaternion").get()
        )

        # disconnect target & targetChanged from QuinticPathPlanner to avoid overwriting artificial values
        og.Controller.disconnect(
            self.graph_path + "/QuinticPathPlanner.outputs:target", self.graph_path + "/CheckGoal2D.inputs:target"
        )
        og.Controller.disconnect(
            self.graph_path + "/QuinticPathPlanner.outputs:targetChanged",
            self.graph_path + "/CheckGoal2D.inputs:targetChanged",
        )

        # artificial target/targetChanged values
        og.Controller.attribute(self.graph_path + "/CheckGoal2D.inputs:targetChanged").set(True)
        og.Controller.attribute(self.graph_path + "/CheckGoal2D.inputs:target").set([pos[0], pos[1], rot])

        for i in range(500):
            await omni.kit.app.get_app().next_update_async()  # allow for check goal node to run and update outputs

        reached = og.Controller.get(og.Controller.attribute(self.graph_path + "/CheckGoal2D.outputs:reachedGoal"))
        self.assertTrue(
            reached[0]
        )  # reachedGoal output - corresponds to x and y position (as hypotenuse compared to threshold)
        self.assertTrue(reached[1])  # reachedGoal output - corresponds to z orientation

        self._timeline.stop()

        print("check goal passed")

        pass

    async def test_stanley_control_pid(self):
        # Start Simulation and wait
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()

        await init_robot_sim("/nova_carter")

        # allow time for carter to move from origin and start driving
        for i in range(20):
            await omni.kit.app.get_app().next_update_async()

        # check stanley outputs, if != 0, stanley seems to be providing some steering control
        # (further tests of full simulation are needed to determine if carter ends up at target position)
        angular = og.Controller.attribute(self.graph_path + "/StanleyControlPID.outputs:angularVelocity").get()
        linear = og.Controller.attribute(self.graph_path + "/StanleyControlPID.outputs:linearVelocity").get()

        self.assertNotEqual(angular, 0)
        self.assertGreater(linear, 0)

        self._timeline.stop()

        print("stanley passed")

        pass
