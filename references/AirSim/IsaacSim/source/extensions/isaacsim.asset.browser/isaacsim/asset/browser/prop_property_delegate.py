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

import asyncio
import os
from typing import List

import omni.kit.app
import omni.ui as ui
import omni.usd
import requests
from isaacsim.core.utils.stage import get_next_free_path, open_stage
from omni.kit.browser.folder.core import BrowserPropertyDelegate, FileDetailItem
from omni.kit.notification_manager import post_notification
from pxr import Usd


class PropAssetPropertyDelegate(BrowserPropertyDelegate):
    """
    A delegate to show properties of assets of type Prop.
    """

    def accepted(self, items: List[FileDetailItem]) -> bool:
        """BrowserPropertyDelegate method override"""
        return len(items) == 1

    def build_widgets(self, items: List[FileDetailItem]) -> None:
        item = items[0]

        def get_file_size(url):
            file_size_raw = 0
            try:
                # local files
                file_size_raw = os.path.getsize(url)
            except FileNotFoundError:
                try:
                    # remote files
                    response = requests.head(url)
                    if response.status_code == 200:
                        file_size_raw = int(response.headers.get("content-length", 0))
                except requests.exceptions.RequestException as e:
                    print(e)
            except Exception as e:
                print(e)

            return int(int(file_size_raw) / 1000)

        url = item.url
        self.file_size = get_file_size(url)
        usd_filetypes = [".usd", ".usda", ".usdc", ".usdz"]

        self._container = ui.VStack(height=0, spacing=5)
        with self._container:
            with ui.VStack(margin=5):
                self._build_thumbnail(item)

                with ui.VStack():
                    # File information
                    ui.Spacer(height=12)
                    self._name_label = ui.Label("File name: " + item.name, height=0)
                    ui.Label("File size: " + str(self.file_size) + " KB", height=0)
                    folder_path = "/".join(item.url.split("/")[7:])
                    folder_label = ui.Label("File Path: " + folder_path, height=0)
                    folder_label.elided_text = True
                    folder_label.tooltip = folder_path
                    ui.Spacer(height=24)

                if item.name.endswith(tuple(usd_filetypes)):
                    # buttons
                    with ui.HStack():
                        ref_load_btn = ui.Button("Load as Reference", height=36)
                        ref_load_btn.set_clicked_fn(lambda: self.load_as_reference(item))
                        ui.Spacer(width=12)
                        open_asset_btn = ui.Button("Open File", height=36)
                        open_asset_btn.set_clicked_fn(lambda: self.open_asset(item))

                    self._build_variant_options(item)

                else:
                    # buttons
                    with ui.HStack():
                        download_btn = ui.Button("Download File", height=36)
                        download_btn.set_clicked_fn(lambda: self.download_file(item))

    def _build_thumbnail(self, item: FileDetailItem):
        if item.thumbnail is None:
            return
        """Builds thumbnail frame and resizes"""
        self._thumbnail_frame = ui.Frame(height=0)
        self._thumbnail_frame.set_computed_content_size_changed_fn(self._on_thumbnail_frame_size_changed)

        with self._thumbnail_frame:
            with ui.HStack():
                ui.Spacer(width=4)
                with ui.ZStack():
                    ui.Rectangle()
                    self._thumbnail_img = ui.Image(
                        item.thumbnail,
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                        alignment=ui.Alignment.CENTER_TOP,
                    )

    def _on_thumbnail_frame_size_changed(self):
        # Dynamic change thumbnail size to be half of frame width
        async def __change_thumbnail_size_async():
            await omni.kit.app.get_app().next_update_async()
            image_size = self._thumbnail_frame.computed_width / 4
            self._thumbnail_img.height = ui.Pixel(image_size)

        asyncio.ensure_future(__change_thumbnail_size_async())

    def _build_variant_options(self, item: FileDetailItem):
        url = item.url
        self.has_variants = False
        if self.file_size > 50:
            self.has_variants = False
            # display nothing additional than the load buttons
        else:
            self.has_variants = True
            self.variant_overwrite = {}
            self.variant_dict = {}
            variant_set_names = []
            stage = Usd.Stage.Open(item.url, load=Usd.Stage.LoadNone)
            if stage.HasDefaultPrim():
                vset = stage.GetDefaultPrim().GetVariantSets()
                variant_set_names = vset.GetNames()
            else:
                pass
            for name in variant_set_names:
                variant_set = vset.GetVariantSet(name)
                variants = variant_set.GetVariantNames()
                self.variant_dict[name] = variants

            self.variant_overwrite = {name: self.variant_dict[name][0] for name in variant_set_names}

            with ui.VStack():
                if variant_set_names:
                    ui.Spacer(height=12)
                    ui.Label("Variant Options", style={"font_size": 18})
                    ui.Spacer()
                    ui.Spacer(height=12)
                    collection_dict = {}
                    for name in variant_set_names:
                        collection = ui.RadioCollection()
                        collection_dict[name] = collection
                        with ui.VStack(margin=5):
                            ui.Label(name)
                            ui.Spacer(height=6)
                            variant_set = vset.GetVariantSet(name)
                            variants = variant_set.GetVariantNames()
                            with ui.HStack(spacing=2, height=23):
                                for j in range(len(variants)):
                                    # with ui.HStack(spacing=2, height=23):
                                    ui.Spacer(width=5)
                                    ui.RadioButton(radio_collection=collection, width=23)
                                    ui.Label(variants[j], width=0)
                            ui.Spacer(height=8)

                    for name, collection in collection_dict.items():
                        collection_model = collection.model
                        collection_model.add_value_changed_fn(lambda m, name=name: _variants_added(m, name))

        def _variants_added(m, name):
            checked = m.get_value_as_int()
            self.variant_overwrite[name] = self.variant_dict[name][checked]

    def load_as_reference(self, item: FileDetailItem):
        url = item.url
        robot_filename = item.name
        stage = omni.usd.get_context().get_stage()
        if stage.HasDefaultPrim():
            default_prim = stage.GetDefaultPrim()
            base_prim_path = default_prim.GetPath().pathString
        else:
            base_prim_path = "/"
        robot_name, _ = os.path.splitext(robot_filename)
        asset_stage_path = get_next_free_path(robot_name, base_prim_path)
        ref_prim = stage.DefinePrim(asset_stage_path, "Xform")
        ref_prim.GetReferences().AddReference(url)

        # Get the referenced prim and its variant set
        if self.has_variants:
            for name, variant in self.variant_overwrite.items():
                variant_set = ref_prim.GetVariantSets().GetVariantSet(name)
                variant_set.SetVariantSelection(variant)

    def open_asset(self, item: FileDetailItem):
        open_stage(item.url)
        # update the variant set if there is any
        if self.has_variants:
            asset_prim = omni.usd.get_context().get_stage().GetDefaultPrim()
            for name, variant in self.variant_overwrite.items():
                variant_set = asset_prim.GetVariantSets().GetVariantSet(name)
                variant_set.SetVariantSelection(variant)

    def download_file(self, item: FileDetailItem):
        url = item.url
        filename = item.name

        # download file to users Download folder
        download_folder = os.path.expanduser("~") + "/Downloads/"
        download_path = download_folder + filename

        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(download_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            post_notification(f"Downloaded {filename} to {download_path}")
        except requests.exceptions.RequestException as e:
            post_notification(f"Failed to download {filename}: {e}")
