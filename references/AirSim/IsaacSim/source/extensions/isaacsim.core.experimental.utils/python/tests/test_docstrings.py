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

import isaacsim.core.experimental.utils.impl.backend as backend_utils
import isaacsim.core.experimental.utils.impl.foundation as foundation_utils
import isaacsim.core.experimental.utils.impl.ops as ops_utils
import isaacsim.core.experimental.utils.impl.prim as prim_utils
import isaacsim.core.experimental.utils.impl.stage as stage_utils
import isaacsim.core.experimental.utils.impl.transform as transform_utils
import isaacsim.test.docstring


class TestExtensionDocstrings(isaacsim.test.docstring.AsyncDocTestCase):
    async def setUp(self):
        """Method called to prepare the test fixture"""
        super().setUp()
        # create new stage
        await stage_utils.create_new_stage_async()

    async def tearDown(self):
        """Method called immediately after the test method has been called"""
        super().tearDown()

    async def test_backend_docstrings(self):
        await self.assertDocTests(backend_utils)

    async def test_foundation_docstrings(self):
        await self.assertDocTests(foundation_utils)

    async def test_ops_docstrings(self):
        await self.assertDocTests(ops_utils)

    async def test_prim_docstrings(self):
        await self.assertDocTests(prim_utils)

    async def test_stage_docstrings(self):
        await self.assertDocTests(stage_utils)

    async def test_transform_docstrings(self):
        await self.assertDocTests(transform_utils)
