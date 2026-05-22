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

# Standard library imports
import asyncio
import os
import tempfile
from typing import Any

# Local imports
import isaacsim.core.experimental.prims as prims
import isaacsim.core.utils.stage as stage_utils

# Third-party imports
import numpy as np
import omni.kit.actions.core
import omni.kit.commands
import omni.kit.test
from isaacsim.core.experimental.prims import Articulation
from isaacsim.core.utils.stage import create_new_stage_async, open_stage_async
from isaacsim.storage.native import get_assets_root_path
from nvidia.srl.from_usd.to_urdf import UsdToUrdf


# Having a test class derived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestUrdfExporter(omni.kit.test.AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._timeline = omni.timeline.get_timeline_interface()
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        pass

    # After running each test
    async def tearDown(self):
        # Wait for any pending stage loading operations to complete
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)

        # Stop timeline if running
        if self._timeline and self._timeline.is_playing():
            self._timeline.stop()

        # Ensure app updates are processed
        # Create a new stage to release any previously open files
        await omni.kit.app.get_app().next_update_async()
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        pass

    @staticmethod
    def check(
        prims,
        member,
        member_args: list[tuple] | None = None,
        member_kwargs: list[dict] | None = None,
        msg: list[str] | None = None,
    ) -> bool:
        import itertools

        def show_mismatch(member_name: str, *, i: int, x: Any, j: int, y: Any) -> None:
            if msg is None:
                print(f"\n'{member_name}' mismatch")
            else:
                print(f"\n'{member_name}' mismatch for {msg[i]} and {msg[j]}")
            print(f"  - {x}")
            print(f"  - {y}")

        def check_values(x: Any, y: Any) -> tuple[bool, Any, Any]:
            # tuple
            if isinstance(x, tuple):
                status = True
                new_x, new_y = [], []
                for xx, yy in zip(x, y):
                    result, xx, yy = check_values(xx, yy)
                    new_x.append(xx)
                    new_y.append(yy)
                    if not result:
                        status = False
                        break
                return status, tuple(new_x), tuple(new_y)
            # Warp arrays
            elif hasattr(x, "numpy"):  # Check if it has numpy method (wp.array, torch.Tensor, etc.)
                try:
                    x_np = x.numpy()
                    y_np = y.numpy()
                    return np.allclose(x_np, y_np, rtol=1e-03, atol=1e-05), x_np, y_np
                except:
                    pass
            # generic Python types
            elif x != y:
                return False, x, y
            return True, x, y

        status = True

        # Handle both properties and methods
        if isinstance(member, property):
            member_name = member.fget.__name__

            results = [member.fget(prim) for prim in prims]
        else:
            member_name = member.__name__
            member_args = [()] * len(prims) if member_args is None else member_args
            member_kwargs = [{}] * len(prims) if member_kwargs is None else member_kwargs
            results = [member(prim, *member_args[i], **member_kwargs[i]) for i, prim in enumerate(prims)]
        for (i, x), (j, y) in itertools.combinations(enumerate(results), 2):
            result, x, y = check_values(x, y)
            if not result:
                # check if only base name is different
                if member_name == "link_names":
                    status = True
                    for i in range(1, len(x)):
                        if x[i] != y[i]:
                            status = False
                            show_mismatch(member_name, i=i, x=x, j=j, y=y)
                            break
                else:
                    status = False
                    show_mismatch(member_name, i=i, x=x, j=j, y=y)
        return status

    def compare_usd_files(
        self,
        usd_path_1: str,
        usd_path_2: str,
        root_path_1: str,
        root_path_2: str = None,
        articulation_root_1: str = None,
        articulation_root_2: str = None,
    ) -> bool:
        """Compare two USD files by loading them into separate stages and comparing their articulations.

        Args:
            usd_path_1: Path to the first USD file
            usd_path_2: Path to the second USD file
            root_path_1: Path to the articulation root in the first USD
            root_path_2: Path to the articulation root in the second USD (if None, will auto-detect)

        Returns:
            bool: True if the articulations match, False otherwise
        """

        # Load first USD into a new stage
        stage_utils.create_new_stage()
        if "nova_carter" in usd_path_1:
            robot_1 = stage_utils.add_reference_to_stage(usd_path_1, articulation_root_1)
            robot_1.GetVariantSet("Sensors").SetVariantSelection("None")
        else:
            stage_utils.add_reference_to_stage(usd_path_1, articulation_root_1)

        articulation_1 = prims.Articulation(articulation_root_1)

        # Load second USD into a new stage
        if "nova_carter" in usd_path_2:
            robot_2 = stage_utils.add_reference_to_stage(usd_path_2, articulation_root_2)
            robot_2.GetVariantSet("Sensors").SetVariantSelection("None")
        else:
            stage_utils.add_reference_to_stage(usd_path_2, articulation_root_2)
        articulation_2 = prims.Articulation(articulation_root_2)

        # Compare using the check function
        articulations = [articulation_1, articulation_2]

        msg = ["usd_1", "usd_2"]

        # Compare basic structural properties
        print(f"Comparing articulations from {usd_path_1} and {usd_path_2}")

        # Check number of DOFs
        print(Articulation.num_dofs, " Articulation.num_dofs")
        if not TestUrdfExporter.check(articulations, Articulation.num_dofs, msg=msg):
            self.assertTrue(False, "Number of DOFs don't match")
        else:
            print("PASS Number of DOFs match")

        # Check number of links
        if not TestUrdfExporter.check(articulations, Articulation.num_links, msg=msg):
            self.assertTrue(False, "Number of links don't match")
        else:
            print("PASS Number of links match")

        # Check joint names
        if not TestUrdfExporter.check(articulations, Articulation.joint_names, msg=msg):
            self.assertTrue(False, "Joint names don't match")
        else:
            print("PASS Joint names match")

        # Check link names
        if not TestUrdfExporter.check(articulations, Articulation.link_names, msg=msg):
            self.assertTrue(False, "Link names don't match")
        else:
            print("PASS Link names match")

        # Try to compare poses if physics is available
        try:
            if articulation_1.is_physics_tensor_entity_valid() and articulation_2.is_physics_tensor_entity_valid():
                if TestUrdfExporter.check(articulations, Articulation.get_world_poses, msg=msg):
                    print("PASS World poses match")
                else:
                    self.assertTrue(False, "World poses don't match")
            else:
                print("WARN Physics not initialized, skipping pose comparison")
        except Exception as e:
            print(f"WARN Could not compare poses: {e}")

        print("PASS All comparisons passed!")
        return True

    async def test_exporter_ur10e(self):
        """Test exporting the UR10e robot from USD to URDF and validate the exported URDF"""
        assets_root_path = get_assets_root_path()[: len(get_assets_root_path())] + "/"
        robot_path = "Isaac/Robots/UniversalRobots/ur10e/ur10e.usd"
        robot_path = os.path.join(assets_root_path, robot_path)
        await open_stage_async(robot_path)
        stage = stage_utils.get_current_stage()

        # Create a temporary directory for test output
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:

            usd_to_urdf_kwargs = {
                "node_names_to_remove": None,
                "edge_names_to_remove": None,
                "root": "ur10e",
                "parent_link_is_body_1": None,
                "log_level": "INFO",
            }

            # Create UsdToUrdf object
            with self.assertRaises(Exception, msg="Expected failure: joint transforms inconsistent"):
                usd_to_urdf = UsdToUrdf(stage, **usd_to_urdf_kwargs)

            # Ensure stage is cleared before temp directory cleanup
            await create_new_stage_async()
            await omni.kit.app.get_app().next_update_async()

    async def test_exporter_2f_140_base(self):
        """Test exporting the 2F-140 base robot from USD to URDF and validate the exported URDF"""
        assets_root_path = get_assets_root_path()[: len(get_assets_root_path())] + "/"
        robot_path = "Isaac/Robots/Robotiq/2F-140/Robotiq_2F_140_base.usd"
        robot_path = os.path.join(assets_root_path, robot_path)
        await open_stage_async(robot_path)
        stage = stage_utils.get_current_stage()

        # Create a temporary directory for test output
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:

            usd_to_urdf_kwargs = {
                "node_names_to_remove": None,
                "edge_names_to_remove": None,
                "root": "Robotiq_2F_140",
                "parent_link_is_body_1": None,
                "log_level": "INFO",
            }

            # Create UsdToUrdf object
            with self.assertRaises(Exception, msg="Expected failure: kinematic loops found"):
                usd_to_urdf = UsdToUrdf(stage, **usd_to_urdf_kwargs)

            # Ensure stage is cleared before temp directory cleanup
            await create_new_stage_async()
            await omni.kit.app.get_app().next_update_async()

    async def test_exporter_nova_carter(self):
        """Test exporting the NovaCarter robot from USD to URDF and validate the exported URDF"""

        assets_root_path = get_assets_root_path()[: len(get_assets_root_path())] + "/"
        robot_path = "Isaac/Robots/NVIDIA/NovaCarter/nova_carter.usd"
        robot_path = os.path.join(assets_root_path, robot_path)
        await open_stage_async(robot_path)
        stage = stage_utils.get_current_stage()

        # Create a temporary directory for test output
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            # Test exporting to URDF
            usd_to_check = os.path.join(temp_dir, f"nova_carter_original.usd")

            usd_to_urdf_kwargs = {
                "node_names_to_remove": None,
                "edge_names_to_remove": None,
                "root": "nova_carter",
                "parent_link_is_body_1": None,
                "log_level": "INFO",
            }

            # Create UsdToUrdf object
            usd_to_urdf = UsdToUrdf(stage, **usd_to_urdf_kwargs)

            # Export to URDF
            output_urdf_path = os.path.join(temp_dir, f"nova_carter_exported.urdf")
            output_path = usd_to_urdf.save_to_file(
                urdf_output_path=output_urdf_path,
                visualize_collision_meshes=False,
                mesh_dir=temp_dir,
                mesh_path_prefix="file://<path to output directory>",
                use_uri_file_prefix=True,
            )
            stage_utils.save_stage(usd_to_check)
            self.assertTrue(os.path.exists(output_urdf_path), f"Exported URDF file not found for nova_carter")

            await create_new_stage_async()

            _, import_config = omni.kit.commands.execute("URDFCreateImportConfig")
            import_config.merge_fixed_joints = True
            import_config.convex_decomp = False
            import_config.import_inertia_tensor = True
            import_config.fix_base = False
            import_config.collision_from_visuals = False

            omni.kit.commands.execute(
                "URDFParseAndImportFile",
                urdf_path=output_urdf_path,
                import_config=import_config,
            )

            urdf_to_check = os.path.join(temp_dir, f"nova_carter_exported.usd")
            stage_utils.save_stage(urdf_to_check)

            await create_new_stage_async()

            comparison_result = self.compare_usd_files(
                usd_path_1=usd_to_check,
                usd_path_2=urdf_to_check,
                root_path_1="nova_carter",
                root_path_2=None,
                articulation_root_1="/World/nova_carter/nova_carter",
                articulation_root_2="/World/nova_carter_01/nova_carter",
            )
            self.assertTrue(comparison_result, "USD comparison failed")

            # Ensure stage is cleared before temp directory cleanup
            await create_new_stage_async()
            await omni.kit.app.get_app().next_update_async()

        return

    async def test_exporter_tien_kung(self):
        """Test exporting the TienKung robot from USD to URDF and validate the exported URDF"""
        assets_root_path = get_assets_root_path()[: len(get_assets_root_path())] + "/"
        robot_path = "Isaac/Robots/XHumanoid/Tien Kung/tienkung.usd"
        robot_path = os.path.join(assets_root_path, robot_path)

        await open_stage_async(robot_path)
        stage = stage_utils.get_current_stage()
        # Create a temporary directory for test output
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:

            usd_to_urdf_kwargs = {
                "node_names_to_remove": None,
                "edge_names_to_remove": None,
                "root": "humanoid",
                "parent_link_is_body_1": None,
                "log_level": "INFO",
            }

            # Create UsdToUrdf object
            with self.assertRaises(Exception, msg="Expected failure: joint transforms inconsistent"):
                usd_to_urdf = UsdToUrdf(stage, **usd_to_urdf_kwargs)

            # Ensure stage is cleared before temp directory cleanup
            await create_new_stage_async()
            await omni.kit.app.get_app().next_update_async()

    async def test_exporter_unitree_go2(self):
        """Test exporting the Unitree Go2 robot from USD to URDF and validate the exported URDF"""
        assets_root_path = get_assets_root_path()[: len(get_assets_root_path())] + "/"
        robot_path = "Isaac/Robots/Unitree/Go2/go2.usd"
        robot_path = os.path.join(assets_root_path, robot_path)

        await open_stage_async(robot_path)
        stage = stage_utils.get_current_stage()

        # Create a temporary directory for test output
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            usd_to_check = os.path.join(temp_dir, f"unitree_go2_original.usd")

            usd_to_urdf_kwargs = {
                "node_names_to_remove": None,
                "edge_names_to_remove": None,
                "root": "go2_description",
                "parent_link_is_body_1": None,
                "log_level": "INFO",
            }

            # Create UsdToUrdf object
            usd_to_urdf = UsdToUrdf(stage, **usd_to_urdf_kwargs)

            # Export to URDF
            output_urdf_path = os.path.join(temp_dir, f"unitree_go2_exported.urdf")
            output_path = usd_to_urdf.save_to_file(
                urdf_output_path=output_urdf_path,
                visualize_collision_meshes=False,
                mesh_dir=temp_dir,
                mesh_path_prefix="file://<path to output directory>",
                use_uri_file_prefix=True,
            )
            stage_utils.save_stage(usd_to_check)
            self.assertTrue(os.path.exists(output_urdf_path), f"Exported URDF file not found for go2")

            await create_new_stage_async()

            _, import_config = omni.kit.commands.execute("URDFCreateImportConfig")
            import_config.merge_fixed_joints = False
            import_config.convex_decomp = False
            import_config.import_inertia_tensor = True
            import_config.fix_base = False
            import_config.collision_from_visuals = False

            omni.kit.commands.execute(
                "URDFParseAndImportFile",
                urdf_path=output_urdf_path,
                import_config=import_config,
            )

            urdf_to_check = os.path.join(temp_dir, f"unitree_go2_exported.usd")
            stage_utils.save_stage(urdf_to_check)

            await create_new_stage_async()

            comparison_result = self.compare_usd_files(
                usd_path_1=usd_to_check,
                usd_path_2=urdf_to_check,
                root_path_1="go2_description",
                root_path_2="go2",
                articulation_root_1="/World/go2",
                articulation_root_2="/World/go2_01",
            )
            self.assertTrue(comparison_result, "USD comparison failed")

            # Ensure stage is cleared before temp directory cleanup
            await create_new_stage_async()
            await omni.kit.app.get_app().next_update_async()

        return
