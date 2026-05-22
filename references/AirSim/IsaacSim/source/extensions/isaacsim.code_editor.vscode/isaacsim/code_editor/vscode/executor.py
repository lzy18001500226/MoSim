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
import __future__

import contextlib
import dis
import io
import traceback

try:
    from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT
except ImportError:
    PyCF_ALLOW_TOP_LEVEL_AWAIT = 0


class Executor:
    """Execute Python statements or expressions from strings

    Args:
        globals (str): global namespace
        locals (str): local namespace
    """

    def __init__(self, globals: dict = {}, locals: dict = {}) -> None:
        self._globals = globals
        self._locals = locals
        self._compiler_flags = self._get_compiler_flags()
        self._coroutine_flag = self._get_coroutine_flag()

    def _get_compiler_flags(self) -> int:
        """Get current Python version compiler flags"""
        flags = 0
        for value in globals().values():
            try:
                if isinstance(value, __future__._Feature):
                    flags |= value.compiler_flag
            except BaseException:
                pass
        return flags | PyCF_ALLOW_TOP_LEVEL_AWAIT

    def _get_coroutine_flag(self) -> int:
        """Get current Python version coroutine flag"""
        for k, v in dis.COMPILER_FLAG_NAMES.items():
            if v == "COROUTINE":
                return k
        return -1

    async def execute(self, source: str) -> tuple[str, Exception, str]:
        """Execute source in the Python scope

        Args:
            source (str): statement or expression

        Returns:
            tuple[str, Exception, str]: standard output, exception thrown (or None if not thrown), exception trace
        """
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                do_exec_step = True
                # try 'eval' first
                try:
                    code = compile(source, "<string>", "eval", flags=self._compiler_flags, dont_inherit=True)
                except SyntaxError:
                    pass
                else:
                    result = eval(code, self._globals, self._locals)
                    do_exec_step = False
                # if 'eval' fails, try 'exec'
                if do_exec_step:
                    code = compile(source, "<string>", "exec", flags=self._compiler_flags, dont_inherit=True)
                    result = eval(code, self._globals, self._locals)
                # await the result if it is a coroutine
                if self._coroutine_flag != -1 and bool(code.co_flags & self._coroutine_flag):
                    result = await result
        except Exception as e:
            return output.getvalue(), e, traceback.format_exc()
        return output.getvalue(), None, ""
