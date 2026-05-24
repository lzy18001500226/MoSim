# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add support for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test
import Semantics
from isaacsim.core.utils.prims import get_prim_at_path

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
from isaacsim.core.utils.semantics import (
    add_labels,
    add_update_semantics,
    check_incorrect_labels,
    check_incorrect_semantics,
    check_missing_labels,
    check_missing_semantics,
    count_labels_in_scene,
    count_semantics_in_scene,
    get_labels,
    remove_all_semantics,
    remove_labels,
    upgrade_prim_semantics_to_labels,
)


# Having a test class derived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class TestSemantics(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        pass

    async def tearDown(self):
        await omni.kit.app.get_app().next_update_async()
        pass

    def create_test_environment(self):
        # creates a test environment with 4 cubes meshes
        # assign semantics "cube" for 2, "sphere" for 1, and leave the last one missing
        result, path_0 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        result, path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        result, path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")
        result, path_3 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube")

        add_update_semantics(get_prim_at_path(path_0), "cube")
        add_update_semantics(get_prim_at_path(path_1), "cube")
        add_update_semantics(get_prim_at_path(path_2), "sphere")

        return [path_0, path_1, path_2, path_3]

    def create_test_environment_new_labels(self):
        # creates a test environment with 4 cubes meshes using the new LabelsAPI
        # assign labels "cube" for 2, "sphere" for 1, and leave the last one missing
        # Also add a nested prim with labels
        result, path_0 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube", prim_path="/World/Cube_0")
        result, path_1 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube", prim_path="/World/Cube_1")
        result, path_2 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube", prim_path="/World/Cube_2")
        result, path_3 = omni.kit.commands.execute("CreateMeshPrimCommand", prim_type="Cube", prim_path="/World/Cube_3")
        result, path_4 = omni.kit.commands.execute(
            "CreateMeshPrimCommand", prim_type="Cube", prim_path="/World/Cube_0/Nested_Cube"
        )

        add_labels(prim=get_prim_at_path(path_0), labels=["cube"], instance_name="class")
        add_labels(prim=get_prim_at_path(path_1), labels=["cube"], instance_name="class")
        add_labels(prim=get_prim_at_path(path_2), labels=["sphere"], instance_name="class")
        add_labels(prim=get_prim_at_path(path_4), labels=["nested"], instance_name="shape")  # Nested prim

        return [path_0, path_1, path_2, path_3, path_4]

    async def test_add_update_semantics(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.DefinePrim("/test", "Xform")
        # make sure we can apply semantics to a new prim
        add_update_semantics(prim, "test_data")
        semantic_api = Semantics.SemanticsAPI.Get(prim, "Semantics")
        self.assertIsNotNone(semantic_api)

        type_attr = semantic_api.GetSemanticTypeAttr()
        data_attr = semantic_api.GetSemanticDataAttr()
        self.assertEqual(type_attr.Get(), "class")
        self.assertEqual(data_attr.Get(), "test_data")

        # make sure we can update existing semantics
        add_update_semantics(prim, "new_test_data")
        self.assertEqual(type_attr.Get(), "class")
        self.assertEqual(data_attr.Get(), "new_test_data")

        # add a second semantic label, first should remain valid
        add_update_semantics(prim, "another_data", "another_class", "1")
        # first should remain valid
        semantic_api = Semantics.SemanticsAPI.Get(prim, "Semantics")
        type_attr = semantic_api.GetSemanticTypeAttr()
        data_attr = semantic_api.GetSemanticDataAttr()
        self.assertIsNotNone(semantic_api)
        self.assertEqual(type_attr.Get(), "class")
        self.assertEqual(data_attr.Get(), "new_test_data")
        # second should exist
        semantic_api_1 = Semantics.SemanticsAPI.Get(prim, "Semantics1")
        self.assertIsNotNone(semantic_api_1)
        type_attr_1 = semantic_api_1.GetSemanticTypeAttr()
        data_attr_1 = semantic_api_1.GetSemanticDataAttr()
        self.assertEqual(type_attr_1.Get(), "another_class")
        self.assertEqual(data_attr_1.Get(), "another_data")

        # we should be able to update this new semantic label
        add_update_semantics(prim, "test_data", "another_class", "1")

        self.assertEqual(type_attr_1.Get(), "another_class")
        self.assertEqual(data_attr_1.Get(), "test_data")

        # should not error with None input
        add_update_semantics(prim, None, None)

        pass

    async def test_remove_semantics(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.DefinePrim("/test", "Xform")
        nested_prim = stage.DefinePrim("/test/test", "Xform")
        # make sure we can apply semantics to a new prim
        add_update_semantics(prim, "test_data_a")
        add_update_semantics(prim, "test_data_b", suffix="_a")
        semantic_api = Semantics.SemanticsAPI.Get(prim, "Semantics")
        self.assertIsNotNone(semantic_api)
        # Check the first semantic
        type_attr = semantic_api.GetSemanticTypeAttr()
        data_attr = semantic_api.GetSemanticDataAttr()
        self.assertEqual(type_attr.Get(), "class")
        self.assertEqual(data_attr.Get(), "test_data_a")
        # Add semantics to nested
        add_update_semantics(nested_prim, "test_data_nested")
        remove_all_semantics(prim)
        # there should be no semantic properties left
        for prop in prim.GetProperties():
            is_semantic = Semantics.SemanticsAPI.IsSemanticsAPIPath(prop.GetPath())
            self.assertFalse(is_semantic)
        # nested should not be touched and have one semantic property
        is_semantic = Semantics.SemanticsAPI.IsSemanticsAPIPath("/test/test.semantic:Semantics:params:semanticData")
        self.assertTrue(is_semantic)

        add_update_semantics(prim, "test_data_a")
        add_update_semantics(prim, "test_data_b", suffix="_a")
        remove_all_semantics(prim, recursive=True)
        # neither prim should have semantics now
        for prop in prim.GetProperties():
            is_semantic = Semantics.SemanticsAPI.IsSemanticsAPIPath(prop.GetPath())
            self.assertFalse(is_semantic)
        for nested_prim in prim.GetProperties():
            is_semantic = Semantics.SemanticsAPI.IsSemanticsAPIPath(prop.GetPath())
            self.assertFalse(is_semantic)

    async def test_check_missing_semantics(self):
        cube_paths = self.create_test_environment()
        prim_paths = check_missing_semantics()

        # there should be one cube missing the label, cube_4
        self.assertEqual(len(prim_paths), 1)
        self.assertTrue(prim_paths[0] == cube_paths[3])

    async def test_check_incorrect_semantics(self):
        cube_paths = self.create_test_environment()
        mismatch_prims = check_incorrect_semantics()

        # there should be one cube with an incorrect label, cube_3
        self.assertEqual(len(mismatch_prims), 1)
        self.assertTrue(mismatch_prims[0][0] == cube_paths[2])
        self.assertTrue(mismatch_prims[0][1] == "sphere")

    async def test_count_semantics_in_scene(self):
        cube_paths = self.create_test_environment()
        semantics_dict = count_semantics_in_scene()

        # there should be 3 counts, 1 missing, 2 cube, and 1 sphere
        self.assertEqual(len(semantics_dict), 3)
        self.assertEqual(semantics_dict["missing"], 1)
        self.assertEqual(semantics_dict["cube"], 2)
        self.assertEqual(semantics_dict["sphere"], 1)

        # only search at cube_0, there should be 2 counts, 0 missing, 1 cube
        semantics_dict = count_semantics_in_scene(cube_paths[0])
        self.assertEqual(len(semantics_dict), 2)
        self.assertEqual(semantics_dict["missing"], 0)
        self.assertEqual(semantics_dict["cube"], 1)

    async def test_upgrade_prim_semantics_to_labels(self):
        stage = omni.usd.get_context().get_stage()
        prim = stage.DefinePrim("/test_upgrade", "Xform")

        # 1) Create old semantics
        add_update_semantics(prim, semantic_label="old_data", type_label="old_type")
        self.assertTrue(
            bool(Semantics.SemanticsAPI.Get(prim, "Semantics")), "Old SemanticsAPI should be valid after creation"
        )

        # 2) Upgrade semantics
        # The upgrade function now always removes the old semantics.
        upgraded_count = upgrade_prim_semantics_to_labels(prim)
        self.assertGreater(upgraded_count, 0, "At least one instance should be upgraded")

        # 3) Verify old semantics are removed
        # Old semantics should be removed (API object should be invalid)
        self.assertFalse(
            bool(Semantics.SemanticsAPI.Get(prim, "Semantics")),
            msg="Old SemanticsAPI should be invalid after upgrade",
        )

        # 4) Verify new labels exist (Optional: and are correct)
        # This part can be expanded to check the actual labels if needed.
        # For now, we confirm the old API is gone and new one might exist via get_labels.
        new_labels = get_labels(prim)
        self.assertTrue(
            "old_type" in new_labels and new_labels["old_type"] == ["old_data"],
            "New labels should be present and correct after upgrade.",
        )

    async def test_new_labels_api(self):
        stage = omni.usd.get_context().get_stage()
        # Create a test prim and a nested prim
        prim = stage.DefinePrim("/new_labels_test", "Xform")
        nested_prim = stage.DefinePrim("/new_labels_test/nested", "Xform")

        # 1) Add labels using the new API
        add_labels(prim=prim, labels=["label_a", "label_b"], instance_name="class")
        add_labels(prim=prim, labels=["shape_a"], instance_name="shape")
        add_labels(prim=nested_prim, labels=["nested_label"], instance_name="class")

        labels_dict = get_labels(prim)
        self.assertIn("class", labels_dict)
        self.assertEqual(sorted(labels_dict["class"]), sorted(["label_a", "label_b"]))  # Sort for consistent comparison
        self.assertIn("shape", labels_dict)
        self.assertEqual(labels_dict["shape"], ["shape_a"])
        nested_labels_dict = get_labels(nested_prim)
        self.assertIn("class", nested_labels_dict)
        self.assertEqual(nested_labels_dict["class"], ["nested_label"])

        # 2) Re-invoke add_labels with overwrite=False (should append)
        add_labels(prim=prim, labels=["label_c"], instance_name="class", overwrite=False)
        labels_dict = get_labels(prim)
        self.assertEqual(sorted(labels_dict["class"]), sorted(["label_a", "label_b", "label_c"]))

        # 3) Overwrite existing labels for a specific instance
        add_labels(prim=prim, labels=["replaced_label"], instance_name="class", overwrite=True)
        labels_dict = get_labels(prim)
        self.assertEqual(labels_dict["class"], ["replaced_label"])
        self.assertIn("shape", labels_dict)  # Other instance should remain untouched
        self.assertEqual(labels_dict["shape"], ["shape_a"])

        # 4) Test remove_labels: Remove specific instance
        remove_labels(prim, instance_name="shape")
        labels_dict = get_labels(prim)
        self.assertIn("class", labels_dict)
        self.assertNotIn("shape", labels_dict)

        # 5) Test remove_labels: Remove all instances on prim
        add_labels(prim=prim, labels=["shape_b"], instance_name="shape")  # Re-add shape instance
        remove_labels(prim)  # Remove all
        labels_dict = get_labels(prim)
        self.assertEqual(len(labels_dict), 0)  # Should be empty

        # 6) Test remove_labels: Recursive removal
        add_labels(prim=prim, labels=["label_root"], instance_name="class")
        add_labels(prim=nested_prim, labels=["label_nested"], instance_name="class")
        remove_labels(prim, include_descendants=True)
        labels_dict = get_labels(prim)
        nested_labels_dict = get_labels(nested_prim)
        self.assertEqual(len(labels_dict), 0)
        self.assertEqual(len(nested_labels_dict), 0)  # Nested should also be removed

        # 7) Test remove_labels: Recursive removal of specific instance
        add_labels(prim=prim, labels=["label_root"], instance_name="class")
        add_labels(prim=prim, labels=["shape_root"], instance_name="shape")
        add_labels(prim=nested_prim, labels=["label_nested"], instance_name="class")
        add_labels(prim=nested_prim, labels=["shape_nested"], instance_name="shape")
        remove_labels(prim, instance_name="class", include_descendants=True)  # Remove only 'class' recursively
        labels_dict = get_labels(prim)
        nested_labels_dict = get_labels(nested_prim)
        self.assertNotIn("class", labels_dict)
        self.assertIn("shape", labels_dict)  # shape should remain
        self.assertNotIn("class", nested_labels_dict)
        self.assertIn("shape", nested_labels_dict)  # shape should remain

        pass

    async def test_check_missing_labels(self):
        """Test the check_missing_labels function using the new LabelsAPI."""
        cube_paths = self.create_test_environment_new_labels()
        # Check from root
        missing_paths = check_missing_labels()

        # Cubes 0, 1, 2, and nested cube 4 have labels. Cube 3 does not.
        # The check includes all Mesh types, including the nested one.
        # Expected missing: Cube_3
        self.assertEqual(len(missing_paths), 1)
        self.assertIn(cube_paths[3], missing_paths)  # Cube_3 should be missing

        # Check from specific path /World/Cube_0
        missing_paths_subtree = check_missing_labels(prim_path="/World/Cube_0")
        # Cube_0 has labels, Nested_Cube has labels. None missing in this subtree.
        self.assertEqual(len(missing_paths_subtree), 0)

    async def test_check_incorrect_labels(self):
        """Test the check_incorrect_labels function using the new LabelsAPI."""
        cube_paths = self.create_test_environment_new_labels()
        # Check from root
        mismatch_prims = check_incorrect_labels()

        # Cube_0 path: /World/Cube_0, label: cube -> OK
        # Cube_1 path: /World/Cube_1, label: cube -> OK
        # Cube_2 path: /World/Cube_2, label: sphere -> MISMATCH
        # Cube_3 path: /World/Cube_3, label: (none) -> OK (no label to mismatch)
        # Nested_Cube path: /World/Cube_0/Nested_Cube, label: nested -> OK
        # Expected mismatch: [Cube_2 path, "sphere"]
        self.assertEqual(len(mismatch_prims), 1)
        self.assertEqual(mismatch_prims[0][0], cube_paths[2])  # Path of Cube_2
        self.assertEqual(mismatch_prims[0][1], "sphere")  # Incorrect label

        # Check from specific path /World/Cube_0
        mismatch_prims_subtree = check_incorrect_labels(prim_path="/World/Cube_0")
        # Cube_0: OK, Nested_Cube: OK. None mismatching in this subtree.
        self.assertEqual(len(mismatch_prims_subtree), 0)

    async def test_count_labels_in_scene_new(self):
        """Test the count_labels_in_scene function using the new LabelsAPI."""
        cube_paths = self.create_test_environment_new_labels()
        # Count from root
        labels_dict = count_labels_in_scene()

        # Expected counts:
        # missing_labels: 1 (Cube_3)
        # cube: 2 (Cube_0, Cube_1)
        # sphere: 1 (Cube_2)
        # nested: 1 (Nested_Cube)
        # Total prims checked: 5 (Cube_0, Cube_1, Cube_2, Cube_3, Nested_Cube)
        print("Labels Dict (Root):", labels_dict)  # Debug print
        self.assertEqual(labels_dict.get("missing_labels", 0), 1)
        self.assertEqual(labels_dict.get("cube", 0), 2)
        self.assertEqual(labels_dict.get("sphere", 0), 1)
        self.assertEqual(labels_dict.get("nested", 0), 1)
        # Check total keys excluding 'missing_labels' match the unique labels + 'missing_labels'
        self.assertEqual(len(labels_dict), 4)  # cube, sphere, nested, missing_labels

        # Count from specific path /World/Cube_0
        labels_dict_subtree = count_labels_in_scene(prim_path="/World/Cube_0")
        # Prims checked: Cube_0, Nested_Cube
        # Expected counts:
        # missing_labels: 0
        # cube: 1 (Cube_0)
        # nested: 1 (Nested_Cube)
        print("Labels Dict (Subtree):", labels_dict_subtree)  # Debug print
        self.assertEqual(labels_dict_subtree.get("missing_labels", 0), 0)
        self.assertEqual(labels_dict_subtree.get("cube", 0), 1)
        self.assertEqual(labels_dict_subtree.get("nested", 0), 1)
        # Expect 3 keys: cube, nested, and missing_labels (even if 0)
        self.assertEqual(len(labels_dict_subtree), 3)
