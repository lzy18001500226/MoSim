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

import os
from typing import List, Optional

import carb.settings
import omni.kit.commands
import omni.usd
from omni.kit.browser.core import CategoryItem, CollectionItem, DetailItem
from omni.kit.browser.folder.core import FileSystemFolder, TreeFolderBrowserModel
from pxr import Sdf, Tf, Usd

SETTING_FOLDER = "/exts/isaacsim.examples.browser/folders"


class Example:
    def __init__(
        self,
        name: str = "",
        execute_entrypoint: callable = None,
        ui_hook: callable = None,
        category: str = "",
        thumbnail: Optional[str] = None,
    ):
        self.name = name
        self.category = category if category else "General"
        self.execute_entrypoint = execute_entrypoint
        self.ui_hook = ui_hook
        self.thumbnail = thumbnail


class ExampleCategoryItem(CategoryItem):
    def __init__(self, name: str):
        super().__init__(name)

    def add_child(self, child_name: str):
        if child_name not in [c.name for c in self.children]:
            child_category = ExampleCategoryItem(child_name)
            self.children.append(child_category)
            self.count += 1
            child_category.parent = self  # add self to the child's parent
        else:
            child_category = self.children[[c.name for c in self.children].index(child_name)]

        return child_category


class ExampleDetailItem(DetailItem):
    def __init__(self, example: Example):
        super().__init__(example.name, "", example.thumbnail)
        self.example = example
        self.ui_hook = example.ui_hook


class ExampleBrowserModel(TreeFolderBrowserModel):
    """
    Represent asset browser model
    """

    def __init__(self, *args, **kwargs):
        settings = carb.settings.get_settings()
        self._examples = {}
        super().__init__(
            *args,
            setting_folders=SETTING_FOLDER,
            show_category_subfolders=True,
            hide_file_without_thumbnails=False,
            show_summary_folder=True,
            **kwargs,
        )

    def register_example(self, **kwargs):
        example = Example(**kwargs)
        if not example.name:
            return
        if example.category not in self._examples:
            self._examples[example.category] = []

        # check if there are already an example with the same name
        if example.name in [e.name for e in self._examples[example.category]]:
            carb.log_warn(f"Example with name {example.name} already exists in category {example.category}.")
        self._examples[example.category].append(ExampleDetailItem(example))
        self.refresh_browser()
        return

    def get_category_items(self, item: CollectionItem) -> List[CategoryItem]:
        """Override to get list of category items"""
        category_items = []
        for category in self._examples:
            categories = category.split("/")

            if categories[0] not in [c.name for c in category_items]:  # if the category is not already in the list
                current_category = ExampleCategoryItem(categories[0])
                category_items.append(current_category)
            else:
                current_category = category_items[[c.name for c in category_items].index(categories[0])]

            if len(categories) > 1:
                for i in range(1, len(categories)):
                    if categories[i] not in [c.name for c in current_category.children]:
                        child_category = current_category.add_child(categories[i])
                        current_category = child_category
                    else:
                        current_category = current_category.children[
                            [c.name for c in current_category.children].index(categories[i])
                        ]

        self.sort_items(category_items)
        return category_items

    def get_detail_items(self, item: ExampleCategoryItem) -> List[ExampleDetailItem]:
        """Override to get list of detail items"""
        detail_items = []

        def lookup_category_name(item):
            key_name = item.name
            while item.parent:
                key_name = item.parent.name + "/" + key_name
                item = item.parent
            return key_name

        if item.name == self.SUMMARY_FOLDER_NAME:
            # List all files in sub folders
            for category, examples in self._examples.items:
                detail_items += examples
        else:
            lookup_name = lookup_category_name(item)
            if lookup_name in self._examples:
                detail_items += self._examples[lookup_name]

        self.sort_items(detail_items)
        return detail_items

    def execute(self, item: ExampleDetailItem) -> None:
        # Create a Reference or payload of the Props in the stage
        example = item.example
        if example.execute_entrypoint:
            example.execute_entrypoint()

    def deregister_example(self, name: str, category: str):
        if category in self._examples:
            self._examples[category] = [e for e in self._examples[category] if e.name != name]
            if len(self._examples[category]) == 0:
                del self._examples[category]
        self.refresh_browser()

    def refresh_browser(self):
        collections = self.get_item_children(None)
        if collections:
            self._item_changed(collections[0])
        else:
            self._item_changed(None)
        return
