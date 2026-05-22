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

import asyncio

import carb.settings
import omni.ext
import omni.ui as ui
from omni.kit.browser.core import OptionMenuDescription
from omni.kit.browser.folder.core import FolderOptionsMenu

DOCS_URL = "https://docs.isaacsim.omniverse.nvidia.com"
ASSETS_GUIDE_URL = DOCS_URL + "/latest/installation/install_faq.html#isaac-sim-setup-faq"


class FolderOptionsMenu(FolderOptionsMenu):
    """
    Represent options menu used in SimReady browser.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Do not use default menu items
        self._menu_descs: List[OptionMenuDescription] = [
            OptionMenuDescription(
                "Check Default Assets Root Path",
                clicked_fn=self._menu_callback,
            ),
        ]
        self._settings = carb.settings.get_settings()

        # this is a work around as some Extensions don't properly setup their default setting in time
        self._set_defaults()

        self.__await_new_scene = asyncio.ensure_future(self._assets_check_window())

    def _set_defaults(self):
        # do not display sever check pop-up on start up
        self._assets_check = False
        self._startup_run = True
        self._cancel_download_btn = None
        self._server_window = None
        self._check_success = None
        self._assets_server = None

    def destroy(self) -> None:
        super().destroy()
        self._server_window = None
        self._check_success = None

    def set_add_collection_fn(self, on_add_collection_fn: callable) -> None:
        # Do not override "Refresh Assets" since "Add Collection" is removed
        pass

    def _open_browser(self, path):
        import platform
        import subprocess
        import webbrowser

        if platform.system().lower() == "windows":
            webbrowser.open(path)
        else:
            # use native system level open, handles snap based browsers better
            subprocess.Popen(["xdg-open", path])

    def _menu_callback(self):
        if self._cancel_download_btn and self._cancel_download_btn.visible:
            self._server_window.visible = True
        else:
            if self._server_window and self._server_window.visible:
                self._server_window.visible = False
                self._server_window = None
            if self._check_success and self._check_success.visible:
                self._check_success.visible = False
                self._check_success = None
            asyncio.ensure_future(self._assets_check_window())

    async def _assets_check_success_window(self):
        self._check_success = ui.Window(
            "Isaac Sim Assets Check Successful",
            style={"alignment": ui.Alignment.CENTER},
            height=0,
            width=0,
            padding_x=10,
            padding_y=10,
            auto_resize=True,
            flags=ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_TITLE_BAR,
            visible=True,
        )

        def hide(w):
            w.visible = False

        with self._check_success.frame:
            with ui.VStack():
                ui.Spacer(height=1)
                ui.Label("Isaac Sim Assets found:", style={"font_size": 18}, alignment=ui.Alignment.CENTER)
                ui.Label("{}".format(self._assets_server), style={"font_size": 18}, alignment=ui.Alignment.CENTER)
                ui.Spacer(height=5)
                ui.Button(
                    "OK", spacing=10, alignment=ui.Alignment.CENTER, clicked_fn=lambda w=self._check_success: hide(w)
                )
                ui.Spacer()

        await omni.kit.app.get_app().next_update_async()

    async def _assets_check_window(self):
        if self._assets_check is False and self._startup_run:
            self._startup_run = False
            pass
        else:
            from isaacsim.storage.native import check_server_async

            omni.kit.app.get_app().print_and_log("Checking for Isaac Sim Assets...")
            self._check_window = ui.Window("Check Isaac Sim Assets", height=120, width=600)
            with self._check_window.frame:
                with ui.VStack(height=80):
                    ui.Spacer()
                    ui.Label("Checking for Isaac Sim assets", alignment=ui.Alignment.CENTER, style={"font_size": 18})
                    ui.Label(
                        "Please login to the Nucleus if a browser window appears",
                        alignment=ui.Alignment.CENTER,
                        style={"font_size": 18},
                    )
                    ui.Label(
                        "Restart of Isaac Sim is required if the browser window is closed without logging in.",
                        alignment=ui.Alignment.CENTER,
                        style={"font_size": 18},
                    )
                    ui.Spacer()
            await omni.kit.app.get_app().next_update_async()

            # Looks for assets root
            # Get timeout
            timeout = carb.settings.get_settings().get("/persistent/isaac/asset_root/timeout")
            if not isinstance(timeout, (int, float)):
                timeout = 10.0
            # Check /persistent/isaac/asset_root/default setting
            default_asset_root = carb.settings.get_settings().get("/persistent/isaac/asset_root/default")
            self._assets_server = await check_server_async(default_asset_root, "/Isaac", timeout)
            if self._assets_server is False:
                self._assets_server = None
            else:
                self._assets_server = default_asset_root + "/Isaac"

            self._check_window.visible = False
            self._check_window = None
            if self._assets_server is None:
                self._startup_run = False

                omni.kit.app.get_app().print_and_log("Warning: Isaac Sim Assets not found")

                frame_height = 150
                self._server_window = ui.Window(
                    "Checking Isaac Sim Assets", width=350, height=frame_height, visible=True
                )
                with self._server_window.frame:
                    with ui.VStack():
                        ui.Label("Warning: Isaac Sim Assets not found", style={"color": 0xFF00FFFF})
                        ui.Line()
                        ui.Label("See the documentation for details")
                        ui.Button("Open Documentation", clicked_fn=lambda: self._open_browser(ASSETS_GUIDE_URL))
                        ui.Spacer()
                        ui.Label("See terminal for additional information")
            else:
                omni.kit.app.get_app().print_and_log(f"Isaac Sim Assets found: {self._assets_server}")
                if not self._startup_run:
                    asyncio.ensure_future(self._assets_check_success_window())
                self._startup_run = False
