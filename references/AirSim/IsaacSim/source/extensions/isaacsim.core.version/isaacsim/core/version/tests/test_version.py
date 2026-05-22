# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import omni.kit.test
from isaacsim.core.version import get_version, parse_version


class TestIsaacVersion(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_version(self):
        parsed_version = parse_version("2000.0.0-beta.0+branch.0.hash.local")
        self.assertTrue(parsed_version.core == "2000.0.0")
        self.assertTrue(parsed_version.pretag == "beta")
        self.assertTrue(parsed_version.prebuild == "0")
        self.assertTrue(parsed_version.buildtag == "branch.0.hash.local")

        version = get_version()
        self.assertTrue(len(version) == 8)
