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
import os
import weakref
import webbrowser

import carb


class UIBuilder:
    """Manage extension UI"""

    def __init__(self, menu_name, menu_item_name, host, port, get_url_callback):
        self._menu_items = []

        self._host = host
        self._port = port
        self._menu_name = menu_name
        self._menu_item_name = menu_item_name
        self._get_url_callback = get_url_callback

        # get application folder
        self._app_folder = carb.settings.get_settings().get_as_string("/app/folder")
        if not self._app_folder:
            self._app_folder = carb.tokens.get_tokens_interface().resolve("${app}")
        self._app_folder = os.path.normpath(os.path.join(self._app_folder, os.pardir))

    def startup(self):
        """Create menu item"""
        try:
            from omni.kit.menu.utils import MenuItemDescription, add_menu_items

            self._menu_items = [
                MenuItemDescription(
                    name=self._menu_item_name,
                    onclick_fn=lambda p=weakref.proxy(self): p._launch(),
                )
            ]
            add_menu_items(self._menu_items, self._menu_name)
        except ImportError:
            pass

    def shutdown(self):
        """Clean up menu item"""
        try:
            from omni.kit.menu.utils import remove_menu_items

            remove_menu_items(self._menu_items, "Window")
        except ImportError:
            pass
        self._menu_items = []

    def _launch(self, *args, **kwargs):
        """Open Jupyter in the default browser"""
        url = f"http://127.0.0.1:{self._port}"
        carb.log_info(f"Open Jupyter in the default browser: {url}")
        webbrowser.open_new_tab(url)
        # get app.display_url
        display_url = self._get_url_callback()
        carb.log_info(display_url)
        # show notification in Kit window
        try:
            import omni.kit.notification_manager as notification_manager
        except ImportError:
            pass
        else:
            if display_url:
                notification = "Jupyter is running at:\n\n" + display_url
                status = notification_manager.NotificationStatus.INFO
            else:
                notification = "Unable to identify Jupyter app URL"
                status = notification_manager.NotificationStatus.WARNING
            notification_manager.post_notification(
                notification,
                hide_after_timeout=len(display_url),
                duration=3,
                status=status,
                button_infos=[notification_manager.NotificationButtonInfo("OK", on_complete=None)],
            )
