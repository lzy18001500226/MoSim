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
import weakref
from functools import partial
from pathlib import Path

import omni.ext
import omni.kit.commands
from isaacsim.core.utils.prims import set_prim_visibility
from isaacsim.gui.components.menu import make_menu_item_description
from omni.kit.menu.utils import MenuItemDescription, add_menu_items, remove_menu_items
from pxr import Gf, Tf


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id: str) -> None:

        menu_items = [
            make_menu_item_description(ext_id, "Contact Sensor", lambda a=weakref.proxy(self): a._add_contact_sensor()),
            make_menu_item_description(ext_id, "Imu Sensor", lambda a=weakref.proxy(self): a._add_imu_sensor()),
        ]

        icon_dir = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        sensor_icon_path = str(Path(icon_dir).joinpath("data/sensor.svg"))
        self._menu_items = [MenuItemDescription(name="Sensors", glyph=sensor_icon_path, sub_menu=menu_items)]
        add_menu_items(self._menu_items, "Create")

        # add sensor to context menu
        context_menu_dict = {
            "name": {
                "Isaac": [
                    {
                        "name": {
                            "Sensors": [
                                {
                                    "name": "Contact Sensor",
                                    "onclick_fn": lambda *_: self._add_contact_sensor(),
                                },
                                {
                                    "name": "Imu Sensor",
                                    "onclick_fn": lambda *_: self._add_imu_sensor(),
                                },
                            ],
                        },
                        "glyph": sensor_icon_path,
                    },
                ],
            },
        }

        self._viewport_create_menu = omni.kit.context_menu.add_menu(context_menu_dict, "CREATE")

    def on_shutdown(self):
        remove_menu_items(self._menu_items, "Create")
        gc.collect()

    def _get_stage_and_path(self):
        selectedPrims = omni.usd.get_context().get_selection().get_selected_prim_paths()

        if len(selectedPrims) > 0:
            curr_prim = selectedPrims[-1]
        else:
            curr_prim = None
        return curr_prim

    def _add_contact_sensor(self, *args, **kargs):
        result, prim = omni.kit.commands.execute(
            "IsaacSensorCreateContactSensor",
            path="/Contact_Sensor",
            parent=self._get_stage_and_path(),
            min_threshold=0.0,
            max_threshold=100000.0,
            color=Gf.Vec4f(1, 0, 0, 1),
            radius=-1,
            sensor_period=-1,
            translation=Gf.Vec3d(0, 0, 0),
        )

    def _add_imu_sensor(self, *args, **kargs):
        result, prim = omni.kit.commands.execute(
            "IsaacSensorCreateImuSensor",
            path="/Imu_Sensor",
            parent=self._get_stage_and_path(),
            sensor_period=-1,
            translation=Gf.Vec3d(0, 0, 0),
        )
        if result:
            # Make lidar invisible on stage as camera
            set_prim_visibility(prim=prim, visible=False)
