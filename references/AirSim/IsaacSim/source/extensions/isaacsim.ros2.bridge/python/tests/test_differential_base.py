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

import time
from copy import deepcopy

import carb
import omni.graph.core as og
import omni.kit.commands
import omni.kit.test
import omni.kit.usd
import usdrt.Sdf
from isaacsim.core.api import SimulationContext
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.core.utils.physics import simulate_async
from pxr import Gf

from .common import (
    ROS2TestCase,
    add_carter,
    add_carter_ros,
    add_nova_carter_ros,
    get_qos_profile,
    set_rotate,
    set_translate,
)


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestRos2DifferentialBase(ROS2TestCase):
    # Before running each test
    async def setUp(self):
        await super().setUp()
        SimulationContext.clear_instance()
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        self.simulation_context = SimulationContext()
        SimulationManager.enable_fabric(enable=False)

        # Initialize class members
        self._trans = None
        self._odom_data = None

        # Create ROS2 node for this test
        import rclpy

        self.node = self.create_node("isaac_sim_test_diff_drive")

    # After running each test
    async def tearDown(self):
        for _ in range(10):
            self.spin()
            time.sleep(0.1)
        self.node = None

        # Reset class members
        self._trans = None
        self._odom_data = None

        await super().tearDown()

    def spin(self):
        """Spin the ROS2 node once with a timeout."""
        import rclpy

        rclpy.spin_once(self.node, timeout_sec=0.1)

    def tf_callback(self, data):
        self._trans = data.transforms[-1]

    def odom_callback(self, data):
        self._odom_data = data.pose.pose

    def move_cmd_msg(self, x, y, z, ax, ay, az):
        from geometry_msgs.msg import Twist

        msg = Twist()
        msg.linear.x = x
        msg.linear.y = y
        msg.linear.z = z
        msg.angular.x = ax
        msg.angular.y = ay
        msg.angular.z = az
        return msg

    async def test_carter_differential_base(self):

        from geometry_msgs.msg import Twist
        from nav_msgs.msg import Odometry
        from tf2_msgs.msg import TFMessage

        await add_carter_ros(self._assets_root_path)
        stage = omni.usd.get_context().get_stage()

        # add an odom prim to carter
        odom_prim = stage.DefinePrim("/Carter/chassis_link/odom", "Xform")

        graph_path = "/Carter/ActionGraph"

        # add an tf publisher for world->odom
        try:
            og.Controller.edit(
                graph_path,
                {
                    og.Controller.Keys.CREATE_NODES: [("PublishTF", "isaacsim.ros2.bridge.ROS2PublishTransformTree")],
                    og.Controller.Keys.SET_VALUES: [
                        ("PublishTF.inputs:topicName", "tf_test"),
                        ("PublishTF.inputs:targetPrims", [usdrt.Sdf.Path("/Carter/chassis_link/odom")]),
                    ],
                    og.Controller.Keys.CONNECT: [
                        (graph_path + "/on_playback_tick.outputs:tick", "PublishTF.inputs:execIn"),
                        (
                            graph_path + "/isaac_read_simulation_time.outputs:simulationTime",
                            "PublishTF.inputs:timeStamp",
                        ),
                    ],
                },
            )
        except Exception as e:
            print(e)

        # move carter off origin
        carter_prim = stage.GetPrimAtPath("/Carter")
        new_translate = Gf.Vec3d(1.00, -3.00, 0.25)
        new_rotate = Gf.Rotation(Gf.Vec3d(0, 0, 1), 45)
        set_translate(carter_prim, new_translate)
        set_rotate(carter_prim, new_rotate)
        await omni.kit.app.get_app().next_update_async()

        tf_sub = self.create_subscription(self.node, TFMessage, "tf_test", self.tf_callback, get_qos_profile())
        odom_sub = self.create_subscription(self.node, Odometry, "odom", self.odom_callback, get_qos_profile())
        cmd_vel_pub = self.create_publisher(self.node, Twist, "cmd_vel", 1)

        await omni.kit.app.get_app().next_update_async()
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(2, 60, self.spin)

        # wait 1 second for all data to be recieved by subscribers
        for _ in range(10):
            self.spin()
            time.sleep(0.1)

        # check 0: is carter initial tf position and odometry position
        # [tx, ty, tz, rx, ry, rz, rw]
        expected_trans = [1.0, -3.0, -0.01, 0, 0, 0.38268, 0.9238]
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0, 0, -0.23, 0, 0, 0, 1]
        self.check_pose(expected_trans, expected_odom, tolerance=1)

        # straight forward
        move_cmd = self.move_cmd_msg(0.1, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        await simulate_async(3, 60, self.spin)

        # stop
        move_cmd = self.move_cmd_msg(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        await simulate_async(1, 60, self.spin)

        # check 1: location using default param
        print(self._trans.transform, self._odom_data)
        # [tx, ty, tz, rx, ry, rz, rw]
        expected_trans = [1.22, -2.78, -0.01, 0, 0, 0.38268, 0.9238]
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0.3, 0, -0.23, 0, 0, 0, 1]
        self.check_pose(expected_trans, expected_odom, tolerance=1)

        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        self.spin()
        self._trans = None

        # change wheel rotation and wheel base
        og.Controller.set(og.Controller.attribute(graph_path + "/differential_controller.inputs:wheelRadius"), 0.1)
        og.Controller.set(og.Controller.attribute(graph_path + "/differential_controller.inputs:wheelDistance"), 0.5)

        self._timeline.play()

        await simulate_async(1, 60, self.spin)

        for _ in range(10):
            self.spin()
            time.sleep(0.1)

        # check 3: is carter initial tf position and odometry position
        # [tx, ty, tz, rx, ry, rz, rw]
        expected_trans = [1.0, -3.0, 0, 0, 0, 0.38268, 0.9238]
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0, 0, -0.23, 0, 0, 0, 1]
        self.check_pose(expected_trans, expected_odom, tolerance=1)

        # straight forward
        move_cmd = self.move_cmd_msg(0.1, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        await simulate_async(3, 60, self.spin)

        # stop
        move_cmd = self.move_cmd_msg(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        await simulate_async(1, 60, self.spin)

        # check 4: location after change radius
        for _ in range(10):
            self.spin()
            time.sleep(0.1)

        # [tx, ty, tz, rx, ry, rz, rw]
        expected_trans = [1.51, -2.49, 0, 0, 0, 0.3846, 0.9230]
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0.7, 0, -0.23, 0, 0, 0, 1]
        self.check_pose(expected_trans, expected_odom, tolerance=1)

        self._timeline.stop()
        self.spin()
        pass

    # add carter and ROS topic from scratch
    async def test_differential_base_scratch(self):

        from geometry_msgs.msg import Twist
        from nav_msgs.msg import Odometry

        await add_carter(self._assets_root_path)

        odom_sub = self.create_subscription(self.node, Odometry, "odom", self.odom_callback, 10)
        cmd_vel_pub = self.create_publisher(self.node, Twist, "cmd_vel", 1)

        graph_path = "/ActionGraph"
        (graph_id, created_nodes) = self.add_differential_drive(graph_path, "/Carter")
        og.Controller.attribute(graph_path + "/diffController.inputs:wheelRadius").set(0.1)

        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(3, 60, self.spin)

        # check 0: is carter initially stationary
        # No transform expected in this test, only check odometry
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0, 0, 0, 0, 0, 0, 1]
        self.check_pose(None, expected_odom, tolerance=1)

        # rotate
        move_cmd = self.move_cmd_msg(0.0, 0.0, 0.0, 0.0, 0.0, 0.2)
        cmd_vel_pub.publish(move_cmd)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(2, 60, self.spin)

        # stop
        move_cmd = self.move_cmd_msg(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(1, 60, self.spin)

        # check 1: location using default param
        odom_data = deepcopy(self._odom_data)
        self.assertAlmostEqual(odom_data.position.x, 0, 1)
        self.assertAlmostEqual(odom_data.position.y, 0, 1)
        self.assertAlmostEqual(odom_data.orientation.x, 0, 1)
        self.assertAlmostEqual(odom_data.orientation.y, 0, 1)
        self.assertAlmostEqual(odom_data.orientation.z, 0.40, 1)
        self.assertAlmostEqual(odom_data.orientation.w, 0.916, 1)

        # change wheel rotation and wheel base
        omni.kit.commands.execute("DeletePrims", paths=[graph_path])

        (graph_id, created_nodes) = self.add_differential_drive(graph_path, "/Carter")
        og.Controller.attribute(graph_path + "/diffController.inputs:wheelRadius").set(0.1)
        og.Controller.attribute(graph_path + "/diffController.inputs:wheelDistance").set(0.8)

        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(1, 60, self.spin)

        # rotate back
        move_cmd = self.move_cmd_msg(0.0, 0.0, 0.0, 0.0, 0.0, -0.2)
        cmd_vel_pub.publish(move_cmd)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(2, 60, self.spin)

        # stop
        move_cmd = self.move_cmd_msg(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(1, 60, self.spin)

        # check 3: location after change radius
        odom_data = deepcopy(self._odom_data)
        self.assertAlmostEqual(odom_data.position.x, 0, 1)
        self.assertAlmostEqual(odom_data.position.y, 0, 1)
        self.assertAlmostEqual(odom_data.orientation.x, 0, 1)
        self.assertAlmostEqual(odom_data.orientation.y, 0, 1)
        self.assertAlmostEqual(odom_data.orientation.z, -0.61, 1)
        self.assertAlmostEqual(odom_data.orientation.w, 0.79, 1)

        self._timeline.stop()
        self.spin()
        pass

    async def test_nova_carter_differential_base(self):
        from geometry_msgs.msg import Twist
        from nav_msgs.msg import Odometry
        from tf2_msgs.msg import TFMessage

        await add_nova_carter_ros(self._assets_root_path)
        stage = omni.usd.get_context().get_stage()

        graph_path = "/nova_carter_ros2_sensors/transform_tree_odometry"
        drive_graph_path = "/nova_carter_ros2_sensors/differential_drive"
        # add an tf publisher for world->base_link
        try:
            og.Controller.edit(
                graph_path,
                {
                    og.Controller.Keys.CREATE_NODES: [("PublishTF", "isaacsim.ros2.bridge.ROS2PublishTransformTree")],
                    og.Controller.Keys.SET_VALUES: [
                        ("PublishTF.inputs:topicName", "tf_test"),
                        (
                            "PublishTF.inputs:targetPrims",
                            [usdrt.Sdf.Path("/nova_carter_ros2_sensors/chassis_link/base_link")],
                        ),
                    ],
                    og.Controller.Keys.CONNECT: [
                        (graph_path + "/on_playback_tick.outputs:tick", "PublishTF.inputs:execIn"),
                        (
                            graph_path + "/isaac_read_simulation_time.outputs:simulationTime",
                            "PublishTF.inputs:timeStamp",
                        ),
                    ],
                },
            )
        except Exception as e:
            print(e)
        await omni.kit.app.get_app().next_update_async()
        # move carter off origin
        carter_prim = stage.GetPrimAtPath("/nova_carter_ros2_sensors")
        new_translate = Gf.Vec3d(1.00, -3.00, 0.0)
        new_rotate = Gf.Rotation(Gf.Vec3d(0, 0, 1), 45)
        set_translate(carter_prim, new_translate)
        set_rotate(carter_prim, new_rotate)
        await omni.kit.app.get_app().next_update_async()

        tf_sub = self.create_subscription(self.node, TFMessage, "tf_test", self.tf_callback, get_qos_profile())
        odom_sub = self.create_subscription(self.node, Odometry, "chassis/odom", self.odom_callback, get_qos_profile())
        cmd_vel_pub = self.create_publisher(self.node, Twist, "cmd_vel", 1)

        await omni.kit.app.get_app().next_update_async()
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(2, 60, self.spin)

        # wait 1 second for all data to be recieved by subscribers
        for _ in range(10):
            self.spin()
            time.sleep(0.1)

        # check 0: is carter initial tf position and odometry position
        # [tx, ty, tz, rx, ry, rz, rw]
        expected_trans = [1.0, -3.0, 0, 0, 0, 0.38268, 0.9238]
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0, 0, 0, 0, 0, 0, 1]
        self.check_pose(expected_trans, expected_odom, tolerance=1)

        # straight forward
        move_cmd = self.move_cmd_msg(0.1, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(3, 60, self.spin)

        # stop
        move_cmd = self.move_cmd_msg(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)

        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(1, 60, self.spin)

        # check 1: location using default param
        carb.log_info(str(self._trans.transform))
        carb.log_info(str(self._odom_data))
        # [tx, ty, tz, rx, ry, rz, rw]
        expected_trans = [1.22, -2.78, 0, 0, 0, 0.38268, 0.9238]
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0.3, 0, 0, 0, 0, 0, 1]
        self.check_pose(expected_trans, expected_odom, tolerance=1)

        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        self.spin()
        self._trans = None

        # change wheel rotation and wheel base
        og.Controller.set(
            og.Controller.attribute(drive_graph_path + "/differential_controller_01.inputs:wheelRadius"), 0.1
        )
        og.Controller.set(
            og.Controller.attribute(drive_graph_path + "/differential_controller_01.inputs:wheelDistance"), 0.5
        )

        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()

        await simulate_async(1, 60, self.spin)

        # check 3: is carter initial tf position and odometry position
        # [tx, ty, tz, rx, ry, rz, rw]
        expected_trans = [1.0, -3.0, 0, 0, 0, 0.38268, 0.9238]
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0, 0, 0, 0, 0, 0, 1]
        self.check_pose(expected_trans, expected_odom, tolerance=1)

        # straight forward
        move_cmd = self.move_cmd_msg(0.1, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(3, 60, self.spin)

        # stop
        move_cmd = self.move_cmd_msg(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        cmd_vel_pub.publish(move_cmd)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        await simulate_async(1, 60, self.spin)

        # check 4: location after change radius
        carb.log_info(str(self._trans.transform))
        carb.log_info(str(self._odom_data))
        # [tx, ty, tz, rx, ry, rz, rw] - Use delta tolerance for translation as specified in original
        expected_trans = [1.30, -2.69, 0, 0, 0, 0.3815, 0.9244]
        # [px, py, pz, ox, oy, oz, ow]
        expected_odom = [0.43, 0, 0, 0, 0, 0, 1]
        self.check_pose(expected_trans, expected_odom, tolerance=1)

        self._timeline.stop()
        self.spin()
        pass

    def check_pose(self, expected_trans, expected_odom, tolerance=1):
        """Verify robot pose against expected transform and odometry values.

        This method compares the current robot pose (from self._trans and self._odom_data)
        against expected transform and odometry values.

        Args:
            expected_trans: List/array of expected transform values [tx, ty, tz, rx, ry, rz, rw]
                or None to skip transform checks. Order: translation x,y,z, rotation x,y,z,w.
            expected_odom: List/array of expected odometry values [px, py, pz, ox, oy, oz, ow]
                or None to skip odometry checks. Order: position x,y,z, orientation x,y,z,w.
            tolerance: Tolerance for floating point comparisons (places parameter).
            delta: Delta tolerance for floating point comparisons (delta parameter).
                When provided, uses delta instead of places for translation values.
        """
        # Check transform values if expected_trans is provided
        if expected_trans is not None:
            self.assertIsNotNone(self._trans)
            if len(expected_trans) >= 3:
                self.assertAlmostEqual(self._trans.transform.translation.x, expected_trans[0], tolerance)
                self.assertAlmostEqual(self._trans.transform.translation.y, expected_trans[1], tolerance)
                self.assertAlmostEqual(self._trans.transform.translation.z, expected_trans[2], tolerance)
            if len(expected_trans) >= 7:
                self.assertAlmostEqual(self._trans.transform.rotation.x, expected_trans[3], tolerance)
                self.assertAlmostEqual(self._trans.transform.rotation.y, expected_trans[4], tolerance)
                self.assertAlmostEqual(self._trans.transform.rotation.z, expected_trans[5], tolerance)
                self.assertAlmostEqual(self._trans.transform.rotation.w, expected_trans[6], tolerance)

        # Check odometry values if expected_odom is provided
        if expected_odom is not None:
            self.assertIsNotNone(self._odom_data)
            odom_data = deepcopy(self._odom_data)
            if len(expected_odom) >= 3:
                self.assertAlmostEqual(odom_data.position.x, expected_odom[0], tolerance)
                self.assertAlmostEqual(odom_data.position.y, expected_odom[1], tolerance)
                self.assertAlmostEqual(odom_data.position.z, expected_odom[2], tolerance)
            if len(expected_odom) >= 7:
                self.assertAlmostEqual(odom_data.orientation.x, expected_odom[3], tolerance)
                self.assertAlmostEqual(odom_data.orientation.y, expected_odom[4], tolerance)
                self.assertAlmostEqual(odom_data.orientation.z, expected_odom[5], tolerance)
                self.assertAlmostEqual(odom_data.orientation.w, expected_odom[6], tolerance)

    def add_differential_drive(self, graph_path, robot_path):

        try:
            keys = og.Controller.Keys
            (graph, nodes, _, _) = og.Controller.edit(
                {"graph_path": graph_path, "evaluator_name": "execution"},
                {
                    keys.CREATE_NODES: [
                        ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                        ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
                        # Added nodes used for Odometry publisher
                        ("computeOdom", "isaacsim.core.nodes.IsaacComputeOdometry"),
                        ("publishOdom", "isaacsim.ros2.bridge.ROS2PublishOdometry"),
                        ("publishRawTF", "isaacsim.ros2.bridge.ROS2PublishRawTransformTree"),
                        # Added nodes used for Twist subscriber, differential drive
                        ("subscribeTwist", "isaacsim.ros2.bridge.ROS2SubscribeTwist"),
                        ("breakLinVel", "omni.graph.nodes.BreakVector3"),
                        ("breakAngVel", "omni.graph.nodes.BreakVector3"),
                        ("diffController", "isaacsim.robot.wheeled_robots.DifferentialController"),
                        ("artController", "isaacsim.core.nodes.IsaacArticulationController"),
                    ],
                    keys.CONNECT: [
                        ("OnPlaybackTick.outputs:tick", "computeOdom.inputs:execIn"),
                        ("OnPlaybackTick.outputs:tick", "publishOdom.inputs:execIn"),
                        ("OnPlaybackTick.outputs:tick", "publishRawTF.inputs:execIn"),
                        ("ReadSimTime.outputs:simulationTime", "publishOdom.inputs:timeStamp"),
                        ("ReadSimTime.outputs:simulationTime", "publishRawTF.inputs:timeStamp"),
                        ("computeOdom.outputs:angularVelocity", "publishOdom.inputs:angularVelocity"),
                        ("computeOdom.outputs:linearVelocity", "publishOdom.inputs:linearVelocity"),
                        ("computeOdom.outputs:orientation", "publishOdom.inputs:orientation"),
                        ("computeOdom.outputs:position", "publishOdom.inputs:position"),
                        ("computeOdom.outputs:orientation", "publishRawTF.inputs:rotation"),
                        ("computeOdom.outputs:position", "publishRawTF.inputs:translation"),
                        ("OnPlaybackTick.outputs:tick", "subscribeTwist.inputs:execIn"),
                        ("OnPlaybackTick.outputs:tick", "artController.inputs:execIn"),
                        ("subscribeTwist.outputs:execOut", "diffController.inputs:execIn"),
                        ("subscribeTwist.outputs:linearVelocity", "breakLinVel.inputs:tuple"),
                        ("breakLinVel.outputs:x", "diffController.inputs:linearVelocity"),
                        ("subscribeTwist.outputs:angularVelocity", "breakAngVel.inputs:tuple"),
                        ("breakAngVel.outputs:z", "diffController.inputs:angularVelocity"),
                        ("diffController.outputs:velocityCommand", "artController.inputs:velocityCommand"),
                    ],
                    og.Controller.Keys.SET_VALUES: [
                        ("diffController.inputs:wheelRadius", 0.24),
                        ("diffController.inputs:wheelDistance", 0.5),
                        ("artController.inputs:jointNames", ["left_wheel", "right_wheel"]),
                        ("computeOdom.inputs:chassisPrim", [usdrt.Sdf.Path(robot_path)]),
                        ("artController.inputs:targetPrim", [usdrt.Sdf.Path(robot_path)]),
                    ],
                },
            )
        except Exception as e:
            print(e)

        return graph, nodes
