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


import carb

old_extension_name = "omni.isaac.manipulators"
new_extension_name = "isaacsim.robot.manipulators"

# Provide deprecation warning to user

carb.log_warn(
    f"{old_extension_name} has been deprecated in favor of {new_extension_name}. Please update your code accordingly."
)

from .single_manipulator import *
