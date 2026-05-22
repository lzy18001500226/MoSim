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

import doctest
import sys

import isaacsim
import omni
import omni.kit.test

from . import _doctest


class AsyncDocTestCase(omni.kit.test.AsyncTestCase):
    """Base class for all async test cases with doctest support for checking docstrings examples

    .. note::

        Derive from it to make the tests auto discoverable.
        Test methods must start with the ``test_`` prefix

    This class add the following methods:

    * ``assertDocTest``: Check that the examples in docstrings pass for a class/module member
    * ``assertDocTests``: Check that the examples in docstrings pass for all class/module's members (names)

    Example:

    .. code-block:: python

        >>> import isaacsim.test.docstring
        >>> tester = isaacsim.test.docstring.AsyncDocTestCase()
        >>> tester.__class__.__name__
        'AsyncDocTestCase'
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._doctest_checker = _doctest.DocTest()

    def assertDocTest(
        self,
        expr: object,
        msg: str = "",
        flags: int = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.FAIL_FAST,
    ) -> None:
        """Check that the examples in docstrings pass for a class/module member

        Args:
            expr: module function or class definition, property or method to check docstrings examples for
            msg (str): custom message to display when failing
            flags (int): doctest's option flags

        Example:

        .. code-block:: python

            >>> from isaacsim.test.docstring import AsyncDocTestCase
            >>>
            >>> tester.assertDocTest(AsyncDocTestCase)
        """
        result = self._doctest_checker.checkDocTest(expr, flags)
        if not result:
            sys.tracebacklimit = 0  # don't show test file tracing, only doctest
            self.fail("Examples in docstrings failed" if not msg else msg)

    async def assertDocTests(
        self,
        expr: object,
        msg: str = "",
        flags: int = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS | doctest.FAIL_FAST,
        order: list[tuple[object, int]] = [],
        exclude: list[object] = [],
        stop_on_failure: bool = False,
        await_update: bool = True,
    ) -> None:
        """Check that the examples in docstrings pass for all class/module's members (names)

        Args:
            expr: module or class definition to check members' docstrings examples for
            msg (str): custom message to display when failing
            flags (int): doctest's option flags
            order (list[tuple[object, int]]): list of pair (name, index) to modify the examples execution order
            exclude (list[object]): list of class/module names to exclude for testing
            stop_on_failure (bool): stop testing docstrings example at fist encountered failure
            await_update (bool): await next kit application update async before running each docstrings example

        Example:

        .. code-block:: python

            >>> from isaacsim.test.docstring import AsyncDocTestCase
            >>> from omni.kit.async_engine import run_coroutine
            >>>
            >>> async def task():
            ...     await tester.assertDocTests(AsyncDocTestCase, exclude=[AsyncDocTestCase.assertDocTests])
            ...
            >>> run_coroutine(task())  # doctest: +NO_CHECK
        """
        objects = self._doctest_checker.get_members(expr, order, exclude, {"omni": omni, "isaacsim": isaacsim})
        print(f"class/module members to check: {len(objects)}")
        # test docstrings examples
        failures = 0
        for obj in objects:
            try:
                name = obj.__name__
            except:
                name = obj.fget.__name__
            print(f"  |-- checking: {name}")
            if await_update:
                await omni.kit.app.get_app().next_update_async()
            try:
                self.assertDocTest(obj, msg=msg, flags=flags)
            except AssertionError as e:
                failures += 1
                if stop_on_failure:
                    raise e
        if failures:
            self.fail(
                f"Some tests failed: failed ({failures}), successful ({len(objects) - failures}), total ({len(objects)})"
            )
