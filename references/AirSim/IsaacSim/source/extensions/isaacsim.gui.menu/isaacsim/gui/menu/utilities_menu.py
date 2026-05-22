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
import omni.kit.menu.utils
from omni.kit.menu.utils import LayoutSourceSearch, MenuItemDescription, MenuLayout


class UtilitiesMenuExtension:
    def __init__(self, ext_id):
        self._menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]
        omni.kit.menu.utils.add_menu_items(self._menu_placeholder, "Utilities")

        self.__menu_layout = [
            MenuLayout.Menu(
                "Utilities",
                [
                    MenuLayout.Seperator("Profilers & Debuggers"),
                    MenuLayout.Item("OmniGraph Tool Kit", source="Window/Visual Scripting/Toolkit"),
                    MenuLayout.Item("Physics Debugger", source="Window/Physics/Debug"),
                    MenuLayout.Item("Profiler", source="Window/Profiler"),
                    MenuLayout.Item("Statistics"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item("Generate Extension Templates"),
                    MenuLayout.Item("Registered Actions", source="Window/Actions"),
                ],
            )
        ]
        omni.kit.menu.utils.add_layout(self.__menu_layout)

    def shutdown(self):
        omni.kit.menu.utils.remove_layout(self.__menu_layout)
        omni.kit.menu.utils.remove_menu_items(self._menu_placeholder, "Utilities")
