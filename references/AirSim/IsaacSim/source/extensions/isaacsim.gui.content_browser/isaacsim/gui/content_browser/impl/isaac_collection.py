# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional

import carb.settings
import omni.client
import omni.ui as ui
from omni.kit.widget.filebrowser import FileBrowserItemFields, NucleusItem
from omni.kit.window.filepicker import AddNewItem, CollectionItem

CURRENT_PATH = Path(__file__).parent.absolute()
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons/")
SETTING_FOLDER = "/exts/isaacsim.gui.content_browser/folders"


class IsaacConnectionItem(NucleusItem):
    """
    A item for a Isaac connection
    Sub-classed from :obj:`NucleusItem`.

    Args:
        name (str): Name of the item.
        path (str): Path of the item.
    """

    def __init__(self, name: str, path: str):
        access = omni.client.AccessFlags.READ
        fields = FileBrowserItemFields(name, datetime.now(), 0, access)
        super().__init__(path, fields, is_folder=True)
        self._models = (ui.SimpleStringModel(name), datetime.now(), ui.SimpleStringModel(""))


class IsaacCollection(CollectionItem):
    def __init__(self):
        super().__init__(
            "https",
            "Isaac Sim",
            f"{ICON_PATH}/cloud.svg",
            access=omni.client.AccessFlags.READ,
            populated=False,
            order=5,
        )
        self._folders = carb.settings.get_settings().get(SETTING_FOLDER)

    def create_add_new_item(self) -> Optional[AddNewItem]:
        # Do not show "Add New Connection ..."
        return None

    def create_child_item(self, name: str, path: str, is_folder: bool = True) -> Optional[IsaacConnectionItem]:
        return IsaacConnectionItem(name, path)

    async def populate_children_async(self) -> Any:
        if self._folders:
            for folder in self._folders:
                # Extract the last part of the URL path
                parts = folder.rstrip("/").split("/")
                if parts:
                    name = parts[-1]
                    self.add_path(name, folder)
