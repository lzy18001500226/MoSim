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

import importlib
import os

import carb
from omni.isaac.merge_mesh import new_extension_name as _new_ext
from omni.isaac.merge_mesh import old_extension_name as _old_ext

# Get the file name
_file_name = os.path.splitext(os.path.basename(__file__))[0]

_new_package = __package__.replace(_old_ext, _new_ext)
carb.log_warn(
    f"{__package__}.{_file_name} has been deprecated in favor of {_new_package}.{_file_name}. Please update your code accordingly "
)

_module = importlib.import_module(f"{_new_package}.{_file_name}")

globals().update({k: v for k, v in _module.__dict__.items() if not k.startswith("_")})

del _new_package
del _file_name
del _module
del _old_ext
del _new_ext
del os
del importlib
del carb
