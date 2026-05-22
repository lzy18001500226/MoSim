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
from isaacsim.core.prims import SingleXFormPrim
from isaacsim.core.utils.stage import (
    add_reference_to_stage,
    create_new_stage_async,
    get_current_stage,
    update_stage_async,
)
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.robot_setup.grasp_editor import GraspSpec, import_grasps_from_file
from isaacsim.storage.native import get_assets_root_path_async
from pxr import Sdf, UsdGeom, UsdLux, UsdPhysics


class TestGraspImporter(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = ext_manager.get_enabled_extension_id("isaacsim.robot_setup.grasp_editor")
        extension_path = ext_manager.get_extension_path(ext_id)
        self._grasp_file = extension_path + "/data/robotiq_rubix_grasp.yaml"

        await create_new_stage_async()
        await update_stage_async()
        await self._create_light()

        set_camera_view(eye=[1.6, 1.3, 1.0], target=[0, -0.3, 0], camera_prim_path="/OmniverseKit_Persp")

        asset_root_path = await get_assets_root_path_async()

        gripper_usd_path = asset_root_path + "/Isaac/Robots/Robotiq/2F-85/Robotiq_2F_85_edit.usd"
        self._gripper_path = "/gripper"
        add_reference_to_stage(gripper_usd_path, self._gripper_path)
        self._gripper_xform = SingleXFormPrim(self._gripper_path)
        self._gripper_xform.set_world_pose(np.array([0.0, 0.2, 0.0]), np.array([0.8, 0.0, 0.2, 0.0]))

        fixed_joint_path = self._gripper_path + "/FixedJoint"

        stage = get_current_stage()
        fixed_joint = UsdPhysics.FixedJoint.Define(stage, fixed_joint_path)
        fixed_joint.GetBody1Rel().SetTargets([self._gripper_path + "/Robotiq_2F_85/base_link"])

        self._cube_path = "/cube/RubikCube"
        add_reference_to_stage(asset_root_path + "/Isaac/Props/Rubiks_Cube/rubiks_cube.usd", self._cube_path)

        self._cube_xform = SingleXFormPrim(self._cube_path)
        self._cube_xform.set_world_pose(np.array([1.0, 0.0, 0.0]))

        self._grasp_spec = import_grasps_from_file(self._grasp_file)

    def assertAlmostEqual(self, a, b, msg=""):
        # overriding method because it doesn't support iterables
        a = np.array(a)
        b = np.array(b)
        self.assertFalse(np.any(abs((a[a != np.array(None)] - b[b != np.array(None)])) > 1e-3), msg)

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

    async def test_accessors(self):
        self.assertTrue(self._grasp_spec.get_grasp_names() == ["grasp_0", "grasp_1"])

        d = self._grasp_spec.get_grasp_dicts()
        self.assertTrue(d["grasp_1"]["confidence"] == 1.0)
        self.assertAlmostEqual(
            d["grasp_1"]["position"], [0.07278040418583424, 0.1386934914438153, 0.0003092657331517473]
        )
        self.assertAlmostEqual(d["grasp_1"]["orientation"]["w"], -0.16540821860820776)
        self.assertAlmostEqual(
            d["grasp_1"]["orientation"]["xyz"], [0.16535619382785066, 0.6884872031442437, -0.6865004162316599]
        )
        self.assertAlmostEqual(d["grasp_1"]["cspace_position"]["finger_joint"], 0.17335550487041473)
        self.assertAlmostEqual(d["grasp_1"]["pregrasp_cspace_position"]["finger_joint"], 1.1851336920380408e-16)

        self.assertTrue(d["grasp_0"] == self._grasp_spec.get_grasp_dict_by_name("grasp_0"))
        self.assertTrue(d["grasp_1"] == self._grasp_spec.get_grasp_dict_by_name("grasp_1"))

    # The two tests below do not numerically test the correctness of the `compute()` functions.
    # Refer to `test_grasp_editor_subframes()` for a mroe rigorous test.
    # These tests simply store golden values of positions that looked visually correct when compared
    # to pictures of the grasps saved to the `isaac_grasp` file.
    async def test_compute_gripper_pose(self):
        rb_trans, rb_quat = self._cube_xform.get_world_pose()

        print(f"rb_trans: {rb_trans}, rb_quat: {rb_quat}")
        pos, orient = self._grasp_spec.compute_gripper_pose_from_rigid_body_pose("grasp_0", rb_trans, rb_quat)
        grasp_xform_0 = SingleXFormPrim("/grasp_0")
        grasp_xform_0.set_world_pose(pos, orient)
        self._gripper_xform.set_world_pose(pos, orient)
        self.assertAlmostEqual(pos, [0.83907737, -0.03842877, 0.00609728])
        self.assertAlmostEqual(orient, [-0.56469814, 0.58969032, -0.41637607, 0.40001538])

        pos, orient = self._grasp_spec.compute_gripper_pose_from_rigid_body_pose("grasp_1", rb_trans, rb_quat)

        grasp_xform_1 = SingleXFormPrim("/grasp_1")
        grasp_xform_1.set_world_pose(pos, orient)

        print(f"pos: {pos}, orient: {orient}")
        self.assertAlmostEqual(pos, [1.07278040e00, 1.38693491e-01, -3.09265733e-04])
        self.assertAlmostEqual(orient, [-0.16540822, 0.16535619, 0.6884872, -0.68650042])

        # This line was used to visually verify that pos, orient are correct for both grasps
        # self._gripper_xform.set_world_pose(pos, orient)

    async def test_compute_rigid_body_pose(self):
        gripper_trans, gripper_quat = self._gripper_xform.get_world_pose()

        pos, orient = self._grasp_spec.compute_rigid_body_pose_from_gripper_pose("grasp_0", gripper_trans, gripper_quat)
        print(f"pos: {pos}, orient: {orient}")
        self.assertAlmostEqual(pos, [0.09281761, 0.19917378, 0.13709212])
        self.assertAlmostEqual(orient, [0.64882371, 0.66910164, -0.26698466, 0.24505096])

        pos, orient = self._grasp_spec.compute_rigid_body_pose_from_gripper_pose("grasp_1", gripper_trans, gripper_quat)
        print(f"pos: {pos}, orient: {orient}")
        self._cube_xform.set_world_pose(pos, orient)
        self.assertAlmostEqual(pos, [0.07523923, 0.19988537, 0.13737544])
        self.assertAlmostEqual(orient, [-0.00651318, -0.00608179, 0.70804808, -0.70610868])

        # This line was used to visually verify that pos, orient are correct for both grasps
        # self._cube_xform.set_world_pose(pos, orient)
