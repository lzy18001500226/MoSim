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

import isaacsim.asset.gen.omap.bindings._omap as omap_bindings
import isaacsim.test.docstring
from isaacsim.core.utils.stage import create_new_stage_async


class TestExtensionDocstrings(isaacsim.test.docstring.AsyncDocTestCase):
    async def setUp(self):
        """Method called to prepare the test fixture"""
        super().setUp()
        # create new stage
        await create_new_stage_async()

    async def tearDown(self):
        """Method called immediately after the test method has been called"""
        super().tearDown()

    async def test_omap_docstrings(self):
        await self.assertDocTests(omap_bindings)

    async def test_omap_generator_docstrings(self):
        await self.assertDocTests(omap_bindings.Generator)
