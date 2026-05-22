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

import carb
from omni.isaac.core.physics_context.physics_context import PhysicsContext
from omni.isaac.core.simulation_context.simulation_context import SimulationContext
from omni.isaac.core.world.world import World

old_extension_name = "omni.isaac.core"
new_extension_name = "isaacsim.core.api"

# Provide deprecation warning to user
carb.log_warn(
    f"{old_extension_name} has been deprecated in favor of {new_extension_name}. Please update your code accordingly."
)
