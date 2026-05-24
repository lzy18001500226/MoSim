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

import asyncio

import numpy as np

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
import omni.kit.test
from isaacsim.core.api.objects import GroundPlane
from isaacsim.core.prims import SingleXFormPrim, XFormPrim
from isaacsim.core.utils.stage import (
    add_reference_to_stage,
    create_new_stage_async,
    get_current_stage,
    update_stage_async,
)
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.robot_setup.grasp_editor import import_grasps_from_file
from isaacsim.robot_setup.grasp_editor.util import move_rb_subframe_to_position
from isaacsim.storage.native import get_assets_root_path_async
from pxr import Sdf, UsdLux, UsdPhysics


class TestGraspSubframes(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = ext_manager.get_enabled_extension_id("isaacsim.robot_setup.grasp_editor")
        extension_path = ext_manager.get_extension_path(ext_id)
        self._grasp_file = extension_path + "/data/robotiq_soup_grasp.yaml"

        await create_new_stage_async()
        await update_stage_async()
        await self._create_light()

        set_camera_view(eye=[-0.6, -0.45, 0.3], target=[0, 0.3, 0], camera_prim_path="/OmniverseKit_Persp")

        asset_root_path = await get_assets_root_path_async()

        gripper_usd_path = asset_root_path + "/Isaac/Robots/Robotiq/2F-140/Robotiq_2F_140_config.usd"
        self._gripper_path = "/Robotiq_2F_140"
        add_reference_to_stage(gripper_usd_path, self._gripper_path)
        self._gripper_xform = SingleXFormPrim(self._gripper_path)
        self._gripper_xform.set_world_pose(np.array([-0.24, 0.02, 0.11]))
        self._gripper_subframe = "/Robotiq_2F_140/robotiq_base_link"

        fixed_joint_path = self._gripper_path + "/FixedJoint"

        stage = get_current_stage()
        fixed_joint = UsdPhysics.FixedJoint.Define(stage, fixed_joint_path)
        fixed_joint.GetBody1Rel().SetTargets([self._gripper_subframe])

        self._rb_path = "/soup_can"
        add_reference_to_stage(asset_root_path + "/Isaac/Props/YCB/Axis_Aligned/005_tomato_soup_can.usd", self._rb_path)

        self._rb_xform = XFormPrim(self._rb_path)
        self._rb_xform.set_world_poses(
            np.array([-0.06, 0.0, 0.14])[np.newaxis, :], np.array([0.707, -0.707, 0.0, 0.0])[np.newaxis, :]
        )

        self._rb_subframe = SingleXFormPrim(
            "/soup_can/subframe", translation=np.array([0.2, 0.1, -0.05]), orientation=np.array([0.5, 0.2, 0.6, -1])
        )

        await self._create_light()

        GroundPlane("/ground")

        self._ground_truth_rb_translations = [
            np.array([0.14, -0.05, 0.04]),
            np.array([-0.02809064, 0.09239036, -0.06723371]),
            np.array([-0.37823358, -0.09652396, -0.05137331]),
        ]

        self._ground_truth_rb_quats = [
            np.array([-0.45706322, 0.25004356, 0.20701967, 0.82807867]),
            np.array([0.76656104, -0.42007253, 0.06654073, -0.48113986]),
            np.array([-0.32704174, 0.84878149, -0.11111393, 0.40033409]),
        ]

        self._ground_truth_gripper_translation = np.array([-0.24, 0.02, 0.11])
        self._ground_truth_gripper_orientation = np.array([0.0, 7.07106781e-01, 0.0, 7.07106781e-01])

        self._grasp_spec = import_grasps_from_file(self._grasp_file)
        await update_stage_async()

    def assertAlmostEqual(self, a, b, msg="", tol=1e-6):
        # overriding method because it doesn't support iterables
        a = np.array(a)
        b = np.array(b)
        self.assertFalse(np.any(abs((a[a != np.array(None)] - b[b != np.array(None)])) > tol), msg)

    async def _create_light(self):
        sphereLight = UsdLux.SphereLight.Define(get_current_stage(), Sdf.Path("/World/SphereLight"))
        sphereLight.CreateRadiusAttr(2)
        sphereLight.CreateIntensityAttr(100000)
        SingleXFormPrim(str(sphereLight.GetPath().pathString)).set_world_pose([6.5, 0, 12])

    async def tearDown(self):
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)
        await update_stage_async()

    # Each ground truth pose for the representative subframes was captured when creating the imported
    # grasp file.  The information in the file should be enough to exactly recover the ground truth pose
    def compareRigidBodyPoseToGroundTruth(self, grasp_index, translation, orientation):
        self.assertAlmostEqual(self._ground_truth_rb_translations[grasp_index], translation)
        self.assertAlmostEqual(self._ground_truth_rb_quats[grasp_index], orientation, tol=1e-3)

    def compareGripperPoseToGroundTruth(self, translation, orientation):
        self.assertAlmostEqual(self._ground_truth_gripper_translation, translation)
        self.assertAlmostEqual(self._ground_truth_gripper_orientation, orientation, tol=1e-3)

    # Carry out test described in
    async def test_derived_poses(self):
        """Ground truths were recorded from the Properties Panel while using the Grasp Editor UI
        to author the grasps in `robotiq_soup_grasp.yaml`.  These ground truths represent the
        state of the gripper and soup for each authored grasp (The gripper was left in one place).

        This test starts validates that give the ground truth location of the soup can subframe, the
        GraspSpec class is able to derive the ground truth position of the gripper subframe.  Likewise,
        given the ground truth position of the gripper subframe, the GraspSpec class can derive the
        ground truth position of the soup can subframe.
        """
        for i, (rb_trans, rb_quat) in enumerate(zip(self._ground_truth_rb_translations, self._ground_truth_rb_quats)):
            t, q = self._grasp_spec.compute_gripper_pose_from_rigid_body_pose(
                self._grasp_spec.get_grasp_names()[i], rb_trans, rb_quat
            )
            self.compareGripperPoseToGroundTruth(t, q)

        for i in range(len(self._ground_truth_rb_translations)):
            t, q = self._grasp_spec.compute_rigid_body_pose_from_gripper_pose(
                self._grasp_spec.get_grasp_names()[i],
                self._ground_truth_gripper_translation,
                self._ground_truth_gripper_orientation,
            )
            self.compareRigidBodyPoseToGroundTruth(i, t, q)

    async def test_move_rb_subframe_to_position(self):
        # The move_rb_base_to_position
        desired_trans = np.array([0.123, -2.4, 0.6])
        desired_orient = np.array([0.965, 0.0, 0.0, -0.259])  # -30 degree about Z

        move_rb_subframe_to_position(self._rb_xform, self._rb_subframe.prim_path, desired_trans, desired_orient)

        t, q = self._rb_subframe.get_world_pose()

        self.assertAlmostEqual(t, desired_trans)
        # Error is expected to accumulate from rotation conversions
        self.assertAlmostEqual(q, desired_orient, tol=1e-3)
