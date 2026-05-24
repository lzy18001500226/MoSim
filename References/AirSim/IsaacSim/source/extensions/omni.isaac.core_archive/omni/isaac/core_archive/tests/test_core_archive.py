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

import omni.kit.test


class TestPipArchive(omni.kit.test.AsyncTestCase):
    # import all packages to make sure dependencies were not missed
    async def test_import_all(self):
        import cycler
        import gunicorn
        import jinja2
        import kiwisolver
        import llvmlite
        import markupsafe
        import matplotlib
        import nest_asyncio
        import numba
        import osqp
        import packaging
        import pint
        import pyparsing
        import pyperclip
        import qdldl
        import tornado

        self.assertIsNotNone(numba)
        self.assertIsNotNone(llvmlite)
        self.assertIsNotNone(nest_asyncio)
        self.assertIsNotNone(jinja2)
        self.assertIsNotNone(markupsafe)
        self.assertIsNotNone(matplotlib)
        self.assertIsNotNone(pyparsing)
        self.assertIsNotNone(cycler)
        self.assertIsNotNone(kiwisolver)
        self.assertIsNotNone(pint)
        self.assertIsNotNone(packaging)
        self.assertIsNotNone(gunicorn)
        self.assertIsNotNone(osqp)
        self.assertIsNotNone(qdldl)
        self.assertIsNotNone(tornado)
        self.assertIsNotNone(pyperclip)
