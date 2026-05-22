# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import sys

from isaacsim import SimulationApp

# The most basic usage for creating a simulation app
simulation_app = SimulationApp()

ADDITIONAL_EXTENSIONS_PEOPLE = [
    "omni.isaac.core",
    "omni.anim.people",
    "omni.anim.navigation.bundle",
    "omni.anim.timeline",
    "omni.anim.graph.bundle",
    "omni.anim.graph.core",
    "omni.anim.graph.ui",
    "omni.anim.retarget.bundle",
    "omni.anim.retarget.core",
    "omni.anim.retarget.ui",
    "omni.kit.scripting",
]

import carb
import omni
from isaacsim.core.utils.extensions import enable_extension
from isaacsim.storage.native import get_assets_root_path

for e in ADDITIONAL_EXTENSIONS_PEOPLE:
    enable_extension(e)
    simulation_app.update()

enable_extension("isaacsim.ros2.bridge")
simulation_app.update()

# Locate Isaac Sim assets folder to load sample
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit()
usd_path = assets_root_path + "/Isaac/Samples/NvBlox/nvblox_sample_scene.usd"

omni.usd.get_context().open_stage(usd_path)

# Wait two frames so that stage starts loading
simulation_app.update()
simulation_app.update()

print("Loading stage...")
from isaacsim.core.utils.stage import is_stage_loading

while is_stage_loading():
    simulation_app.update()
print("Loading Complete")

omni.timeline.get_timeline_interface().play()

frame = 0

while simulation_app.is_running() and frame < 10:
    simulation_app.update()
    frame = frame + 1

simulation_app.close()  # Cleanup application
