# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import omni.ext
import omni.kit.app

from .. import _simulation_manager
from .isaac_events import IsaacEvents
from .simulation_manager import SimulationManager

# expose pybind interface/API
_simulation_manager_interface = None


def acquire_simulation_manager_interface():
    return _simulation_manager_interface


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):
        # acquire the pybind interface
        global _simulation_manager_interface
        _simulation_manager_interface = _simulation_manager.acquire_simulation_manager_interface()
        SimulationManager._simulation_manager_interface = _simulation_manager_interface
        SimulationManager._initialize()

    def on_shutdown(self):
        # release the pybind interface
        global _simulation_manager_interface
        SimulationManager._clear()
        _simulation_manager.release_simulation_manager_interface(_simulation_manager_interface)
        _simulation_manager_interface = None
