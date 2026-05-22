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


import os
import pathlib

import omni.ext

# Work around a (not understood) issue on Windows where the lula python extension module (pyd file)
# is loaded properly but the DLLs on which it depends are not, despite being in the same directory.
if os.name == "nt":
    file_dir = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
    lula_dir = file_dir.joinpath(pathlib.Path("../../../pip_prebundle")).resolve()
    os.add_dll_directory(lula_dir.__str__())


from lula import LogLevel, set_default_logger_prefix, set_log_level


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):
        set_log_level(LogLevel.WARNING)
        set_default_logger_prefix("[Lula] ")

    def on_shutdown(self):
        pass
