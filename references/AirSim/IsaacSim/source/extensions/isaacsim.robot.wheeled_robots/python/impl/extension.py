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
import omni.kit.commands
from isaacsim.robot.wheeled_robots.bindings._isaacsim_robot_wheeled_robots import (
    acquire_wheeled_robots_interface,
    release_wheeled_robots_interface,
)


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        # we need to acquire the interface to actually load the plugin, otherwise the DifferentialController can't be found
        self.__interface = acquire_wheeled_robots_interface()

    def on_shutdown(self):
        release_wheeled_robots_interface(self.__interface)
