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

import gc
from pathlib import Path

import omni.ext
import omni.kit.commands
from isaacsim.core.utils.stage import add_reference_to_stage, get_next_free_path
from isaacsim.sensors.rtx import SUPPORTED_LIDAR_CONFIGS
from isaacsim.storage.native import get_assets_root_path
from omni.kit.menu.utils import MenuItemDescription, add_menu_items, remove_menu_items
from pxr import Tf


class Extension(omni.ext.IExt):

    def on_startup(self, ext_id: str) -> None:
        icon_dir = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        sensor_icon_path = str(Path(icon_dir).joinpath("data/sensor.svg"))

        rtx_lidar_vendor_dict = {}
        for config in SUPPORTED_LIDAR_CONFIGS:
            # Assume paths are of the form "/Isaac/Sensors/<Vendor>/<Sensor>/<Sensor>.usd"
            config_path = Path(config)
            vendor_name = config_path.parts[3]
            sensor_name = config_path.stem.replace("_", " ")
            if sensor_name.startswith(vendor_name):
                # Remove the vendor prefix from the sensor name
                # Note: assumes there is a single character (eg. underscore) between the vendor and sensor name
                sensor_name = sensor_name[len(vendor_name) + 1 :]

            if vendor_name not in rtx_lidar_vendor_dict:
                rtx_lidar_vendor_dict[vendor_name] = []
            rtx_lidar_vendor_dict[vendor_name].append(
                {
                    "name": sensor_name,
                    "onclick_fn": (
                        lambda *_, sensor_name=sensor_name, sensor_config=config_path.stem: self._create_lidar(
                            sensor_name, sensor_config
                        )
                    ),
                }
            )

        # Sort the vendors by name and arrange them into a list.
        rtx_lidar_vendor_list = []
        for vendor_name in sorted(rtx_lidar_vendor_dict.keys()):
            rtx_lidar_vendor_list.append({"name": {vendor_name: rtx_lidar_vendor_dict[vendor_name]}})

        # Compose the RTX Lidar menu dictionary.
        rtx_lidar_menu_dict = {"name": {"RTX Lidar": rtx_lidar_vendor_list}}

        # Wrap into a top-level Sensors dictionary (like in the camera extension).
        sensors_menu_dict = {
            "name": {
                "Sensors": [
                    rtx_lidar_menu_dict,
                    {"name": "RTX Radar", "onclick_fn": (lambda *_: self._create_radar())},
                ]
            },
            "glyph": sensor_icon_path,
        }

        # Define a helper to recursively create submenus.
        def create_submenu(menu_dict):
            # If the dict is a leaf (i.e. "name" is a string), create a MenuItemDescription.
            if "name" in menu_dict and isinstance(menu_dict["name"], str):
                return MenuItemDescription(
                    name=menu_dict["name"],
                    onclick_fn=menu_dict.get("onclick_fn"),
                    onclick_action=menu_dict.get("onclick_action"),
                )
            # Otherwise, for nested dictionaries the key is the submenu name.
            submenu_name = next(iter(menu_dict["name"]))
            items = menu_dict["name"][submenu_name]
            sub_menu_items = []
            for item in items:
                if isinstance(item.get("name"), dict):
                    sub_menu_items.append(create_submenu(item))
                else:
                    sub_menu_items.append(
                        MenuItemDescription(
                            name=item["name"],
                            onclick_fn=item.get("onclick_fn"),
                            onclick_action=item.get("onclick_action"),
                        )
                    )
            return MenuItemDescription(name=submenu_name, sub_menu=sub_menu_items, glyph=menu_dict.get("glyph"))

        # Convert the dictionary to a menu and add it.
        self._menu_items = create_submenu(sensors_menu_dict)
        add_menu_items([self._menu_items], "Create")

        # Add a menu item to the Isaac Sim in context menus.
        context_menu_dict = {
            "name": {
                "Isaac": [
                    sensors_menu_dict,
                ],
            },
            "glyph": sensor_icon_path,
        }

        self._viewport_create_menu = omni.kit.context_menu.add_menu(context_menu_dict, "CREATE")

    def on_shutdown(self):
        remove_menu_items(self._menu_items, "Create")
        self._viewport_create_menu = None
        gc.collect()

    def _get_stage_and_path(self):
        selectedPrims = omni.usd.get_context().get_selection().get_selected_prim_paths()

        if len(selectedPrims) > 0:
            curr_prim = selectedPrims[-1]
        else:
            curr_prim = None
        return curr_prim

    def _create_lidar(self, sensor_name, sensor_config):
        selected_prim = self._get_stage_and_path()
        prim_path = get_next_free_path("/" + Tf.MakeValidIdentifier(sensor_name), None)
        omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar", path=prim_path, parent=selected_prim, config=sensor_config
        )

    def _create_radar(self):
        selected_prim = self._get_stage_and_path()
        omni.kit.commands.execute("IsaacSensorCreateRtxRadar", path="/RtxRadar", parent=selected_prim)
