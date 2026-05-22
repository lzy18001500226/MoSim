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

import omni.ext
import omni.usd
from omni.physx import get_physx_interface

from .. import _range_sensor
from .proximity_sensor import ProximitySensorManager, clear_sensors


class Extension(omni.ext.IExt):
    def on_startup(self):
        # step the sensor every physics step
        self._physics_step_subscription = get_physx_interface().subscribe_physics_step_events(self._on_update)
        self._proximity_sensor_manager = ProximitySensorManager()  # Store instance to sensor manager singleton
        self._lidar = _range_sensor.acquire_lidar_sensor_interface()
        self._generic = _range_sensor.acquire_generic_sensor_interface()
        self._lightbeam = _range_sensor.acquire_lightbeam_sensor_interface()

    def on_shutdown(self):
        # Handle ProximitySensorManager
        self._physics_step_subscription = None  # clear subscription
        clear_sensors()  # clear sensors on shutdown
        self._proximity_sensor_manager = None

        # Release sensor interfaces
        _range_sensor.release_lidar_sensor_interface(self._lidar)
        _range_sensor.release_generic_sensor_interface(self._generic)
        _range_sensor.release_lightbeam_sensor_interface(self._lightbeam)

    def _on_update(self, dt):
        self._proximity_sensor_manager.update()
        pass
