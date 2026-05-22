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


class LayoutMenuExtension:
    def __init__(self, ext_id):
        self._menu_placeholder = [MenuItemDescription(name="placeholder", show_fn=lambda: False)]
        omni.kit.menu.utils.add_menu_items(self._menu_placeholder, "Layouts")

        self.__menu_layout = [
            MenuLayout.Menu(
                "Layouts",
                [
                    MenuLayout.Seperator("UI Controls"),
                    MenuLayout.Item("UI Toggle Visibility", source="Window/UI Toggle Visibility"),
                    MenuLayout.Item("Fullscreen Mode", source="Window/Fullscreen Mode"),
                    MenuLayout.Seperator("Templates"),
                    MenuLayout.Item("Default"),
                    MenuLayout.Item("Visual Scripting"),
                    MenuLayout.Item(
                        "Replicator", source="Layouts/Replicator", source_search=LayoutSourceSearch.LOCAL_ONLY
                    ),
                    MenuLayout.Item("Occupancy Map Generation"),
                    MenuLayout.Item(
                        "Action and Event Data Generation",
                        source="Layouts/Action and Event Data Generation",
                        source_search=LayoutSourceSearch.LOCAL_ONLY,
                    ),
                    MenuLayout.Seperator("Save/Load"),
                    MenuLayout.Item("Save Layout", source="Window/Layout/Save Layout..."),
                    MenuLayout.Item("Load Layout", source="Window/Layout/Load Layout..."),
                    MenuLayout.Seperator("Quick Actions"),
                    MenuLayout.Item("Quick Save", source="Layouts/Quick Save"),
                    MenuLayout.Item("Quick Load", source="Layouts/Quick Load"),
                ],
            )
        ]
        omni.kit.menu.utils.add_layout(self.__menu_layout)

    def shutdown(self):
        omni.kit.menu.utils.remove_layout(self.__menu_layout)
        omni.kit.menu.utils.remove_menu_items(self._menu_placeholder, "Layouts")
