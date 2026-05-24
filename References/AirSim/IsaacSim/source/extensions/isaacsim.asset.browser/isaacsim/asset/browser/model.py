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

import carb.settings
import omni.kit.commands
import omni.usd
from isaacsim.core.utils.stage import open_stage
from omni.kit.browser.core import DetailItem
from omni.kit.browser.folder.core import FileSystemFolder, TreeFolderBrowserModel
from pxr import Sdf, Tf, Usd

SETTING_FOLDER = "/exts/isaacsim.asset.browser/folders"


class AssetBrowserModel(TreeFolderBrowserModel):
    """
    Represent asset browser model
    """

    def __init__(self, *args, **kwargs):
        settings = carb.settings.get_settings()
        self.__default_folders = settings.get(SETTING_FOLDER)
        ext_manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = ext_manager.get_enabled_extension_id("isaacsim.asset.browser")
        extension_path = ext_manager.get_extension_path(ext_id)
        cache_path = os.path.abspath(os.path.join(f"{extension_path}", "cache/isaacsim.asset.browser.cache.json"))

        super().__init__(
            *args,
            setting_folders=SETTING_FOLDER,
            show_category_subfolders=True,
            hide_file_without_thumbnails=settings.get("/exts/isaacsim.asset.browser/data/hide_file_without_thumbnails"),
            local_cache_file=cache_path,
            show_summary_folder=True,
            filter_file_suffixes=settings.get("/exts/isaacsim.asset.browser/data/filter_file_suffixes"),
            timeout=settings.get("/exts/isaacsim.asset.browser/data/timeout"),
            **kwargs,
        )

    def create_folder_object(self, name: str, url: str, **kwargs) -> FileSystemFolder:
        """
        Create a folder object when a root folder appended. Default using FileSystemFolder.
        User could overridden to create own folder object for special usage.
        Args and keyword args please reference to FileSystemFolder.
        """
        if self.__default_folders and any(url.startswith(folder) for folder in self.__default_folders):
            # OM-75191: For folders in default settings, hide file without thumbnail
            # Otherwise show all files - OM-113211
            kwargs["ignore_file_without_thumbnail"] = False
        return FileSystemFolder(name, url, **kwargs)

    def execute(self, item: DetailItem) -> None:
        """
        action when double clicked on an item: open the original file
        """

        usd_filetypes = [".usd", ".usda", ".usdc", ".usdz"]
        if item.name.endswith(tuple(usd_filetypes)):
            stage = omni.usd.get_context().get_stage()
            if not stage:
                return
            open_stage(item.url)
        else:
            pass

        # # Create a Reference or payload of the Props in the stage
        # stage = omni.usd.get_context().get_stage()
        # if not stage:
        #     return

        # new_prim_path = self._make_prim_path(stage, item.url)
        # as_instanceable = carb.settings.get_settings().get("/persistent/app/stage/instanceableOnCreatingReference")

        # # Determine if we should create a payload or reference
        # create_as_payload = carb.settings.get_settings().get("/persistent/app/stage/dragDropImport") == "payload"

        # print("creating something", create_as_payload)

        # # Add asset to stage
        # cmd_name = "CreatePayloadCommand" if create_as_payload else "CreateReferenceCommand"
        # omni.kit.commands.execute(
        #     cmd_name,
        #     usd_context=omni.usd.get_context(),
        #     path_to=new_prim_path,
        #     asset_path=item.url,
        #     instanceable=as_instanceable,
        # )

    def _make_prim_path(self, stage: Usd.Stage, url: str, prim_path: Sdf.Path = None, prim_name: str = None):
        """Make a new/unique prim path for the given url"""
        if prim_path is None or prim_path.isEmpty:
            if stage.HasDefaultPrim():
                prim_path = stage.GetDefaultPrim().GetPath()
            else:
                prim_path = Sdf.Path.absoluteRootPath

        if prim_name is None:
            prim_name = Tf.MakeValidIdentifier(os.path.basename(os.path.splitext(url)[0]))

        return Sdf.Path(omni.usd.get_stage_next_free_path(stage, prim_path.AppendChild(prim_name).pathString, False))
