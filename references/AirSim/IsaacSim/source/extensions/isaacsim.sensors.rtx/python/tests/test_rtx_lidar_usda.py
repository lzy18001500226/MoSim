# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import glob
import os

import carb
import omni.kit.test
import omni.usd
from isaacsim.core.utils.stage import add_reference_to_stage, create_new_stage_async, update_stage_async


def _create_test_for_usda(usda_path):
    """Create a test function for a specific USDA file"""
    file_name = os.path.basename(usda_path).split(".")[0]

    async def test_function(self):

        # Add reference to stage
        reference_prim_path = f"/World/{file_name}"
        add_reference_to_stage(usd_path=usda_path, prim_path=reference_prim_path)

        # Wait for reference to load
        await update_stage_async()

        # Verify reference was added correctly
        self.assertTrue(
            self.stage.GetPrimAtPath(reference_prim_path).IsValid(),
        )

    # Set proper function name and docstring
    test_function.__name__ = f"test_reference_{file_name}"
    test_function.__doc__ = f"Test adding {file_name} USDA as a reference"

    return test_function


class TestRtxLidarUsda(omni.kit.test.AsyncTestCase):
    """Test adding RTX lidar USDAs as references to a stage"""

    async def setUp(self):
        await create_new_stage_async()
        self.stage = omni.usd.get_context().get_stage()


# Find all USDA files and dynamically add test methods to the TestRtxLidarUsda class
extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
lidar_configs_dir = os.path.join(extension_path, "data", "lidar_configs")
usda_files = glob.glob(pathname="**/*.usda", root_dir=lidar_configs_dir, recursive=True)

# Make sure we found some files and report a useful message if not
if len(usda_files) == 0:
    carb.log_warn(f"No USDA files found in {lidar_configs_dir}")
else:
    # Add a test method for each USDA file
    for usda_file in usda_files:
        test_func = _create_test_for_usda(os.path.join(lidar_configs_dir, usda_file))
        setattr(TestRtxLidarUsda, test_func.__name__, test_func)
