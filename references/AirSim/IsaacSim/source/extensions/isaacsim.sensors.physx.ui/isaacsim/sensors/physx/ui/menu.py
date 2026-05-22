# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import weakref
from pathlib import Path

import carb
import omni.kit.commands
from isaacsim.core.utils.prims import create_prim
from isaacsim.core.utils.stage import get_next_free_path
from isaacsim.gui.components.menu import make_menu_item_description
from isaacsim.storage.native import get_assets_root_path
from omni.kit.menu.utils import MenuItemDescription, add_menu_items, remove_menu_items
from pxr import Gf


class RangeSensorMenu:
    def __init__(self, ext_id: str):
        menu_items = [
            MenuItemDescription(
                name="PhysX Lidar",
                sub_menu=[
                    make_menu_item_description(ext_id, "Rotating", lambda a=weakref.proxy(self): a._add_lidar()),
                    make_menu_item_description(
                        ext_id, "Generic", lambda a=weakref.proxy(self): a._add_generic(), "PhysX Generic"
                    ),
                ],
            ),
            MenuItemDescription(
                name="LightBeam Sensor",
                sub_menu=[
                    make_menu_item_description(
                        ext_id, "Generic", lambda a=weakref.proxy(self): a._add_lightbeam_sensor(), "LightBeam Generic"
                    ),
                    make_menu_item_description(
                        ext_id,
                        "Tashan TS-F-A",
                        lambda *_: create_prim(
                            prim_path=get_next_free_path("/TS_F_A", None),
                            prim_type="Xform",
                            usd_path=get_assets_root_path() + "/Isaac/Sensors/Tashan/TS-F-A/TS-F-A.usd",
                        ),
                    ),
                ],
            ),
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
                                    "name": {
                                        "PhysX Lidar": [
                                            {
                                                "name": "Rotating",
                                                "onclick_fn": lambda *_: self._add_lidar(),
                                            },
                                            {
                                                "name": "Generic",
                                                "onclick_fn": lambda *_: self._add_generic(),
                                            },
                                        ],
                                    },
                                },
                                {
                                    "name": {
                                        "LightBeam Sensor": [
                                            {
                                                "name": "Generic",
                                                "onclick_fn": lambda *_: self._add_lightbeam_sensor(),
                                            },
                                            {
                                                "name": "Tashan TS-F-A",
                                                "onclick_fn": lambda *_: create_prim(
                                                    prim_path=get_next_free_path("/TS_F_A", None),
                                                    prim_type="Xform",
                                                    usd_path=get_assets_root_path()
                                                    + "/Isaac/Sensors/Tashan/TS-F-A/TS-F-A.usd",
                                                ),
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                        "glyph": sensor_icon_path,
                    },
                ],
            },
        }

        self._viewport_create_menu = omni.kit.context_menu.add_menu(context_menu_dict, "CREATE")

    def _get_stage_and_path(self):
        self._stage = omni.usd.get_context().get_stage()
        selectedPrims = omni.usd.get_context().get_selection().get_selected_prim_paths()

        if len(selectedPrims) > 0:
            curr_prim = selectedPrims[-1]
        else:
            curr_prim = None
        return curr_prim

    def _add_lidar(self, *args, **kwargs):
        result, prim = omni.kit.commands.execute(
            "RangeSensorCreateLidar",
            path="/Lidar",
            parent=self._get_stage_and_path(),
            min_range=0.4,
            max_range=100.0,
            draw_points=False,
            draw_lines=False,
            horizontal_fov=360.0,
            vertical_fov=30.0,
            horizontal_resolution=0.4,
            vertical_resolution=4.0,
            rotation_rate=20.0,
            high_lod=False,
            yaw_offset=0.0,
            enable_semantics=False,
        )

    def _add_generic(self, *args, **kwargs):
        result, prim = omni.kit.commands.execute(
            "RangeSensorCreateGeneric",
            path="/GenericSensor",
            parent=self._get_stage_and_path(),
            min_range=0.4,
            max_range=100.0,
            draw_points=False,
            draw_lines=False,
            sampling_rate=60,
        )

    def _add_lightbeam_sensor(self, *args, **kargs):
        result, prim = omni.kit.commands.execute(
            "IsaacSensorCreateLightBeamSensor",
            path="/LightBeam_Sensor",
            parent=self._get_stage_and_path(),
            translation=Gf.Vec3d(0, 0, 0),
            orientation=Gf.Quatd(1.0, 0.0, 0.0, 0.0),
            forward_axis=Gf.Vec3d(1, 0, 0),
        )

    def shutdown(self):
        remove_menu_items(self._menu_items, "Create")
        self.menus = None
