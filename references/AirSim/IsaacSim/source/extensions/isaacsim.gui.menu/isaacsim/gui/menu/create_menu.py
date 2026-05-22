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
import asyncio
import weakref
from functools import partial
from pathlib import Path

import carb
import omni.kit.menu.utils
import usd.schema.isaac.robot_schema
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.gui.components.menu import make_menu_item_description
from isaacsim.storage.native.nucleus import get_assets_root_path
from omni.kit.menu.utils import MenuItemDescription, MenuLayout, add_menu_items, remove_menu_items


# -----------------------------------------------------------------------------
# Global create_asset function
# -----------------------------------------------------------------------------
def create_asset(usd_path, stage_path, camera_position=None, camera_target=None):
    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        carb.log_error("Could not find Isaac Sim assets folder")
        return

    path_to = omni.kit.commands.execute(
        "CreateReferenceCommand",
        usd_context=omni.usd.get_context(),
        path_to=stage_path,
        asset_path=assets_root_path + usd_path,
        instanceable=False,
    )

    carb.log_info(f"Added reference to {stage_path} at {path_to}")

    if camera_position is not None and camera_target is not None:
        set_camera_view(camera_position, camera_target)


# -----------------------------------------------------------------------------
# Global create_apriltag function
# -----------------------------------------------------------------------------
def create_apriltag(usd_path, shader_name, stage_path, tag_path):
    from pxr import Sdf

    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        carb.log_error("Could not find Isaac Sim assets folder")
        return

    stage = omni.usd.get_context().get_stage()
    stage_path = omni.usd.get_stage_next_free_path(stage, stage_path, False)

    async def create_tag():
        omni.kit.commands.execute(
            "CreateMdlMaterialPrim",
            mtl_url=assets_root_path + usd_path,
            mtl_name=shader_name,
            mtl_path=stage_path,
            select_new_prim=True,
        )
        mtl = stage.GetPrimAtPath(stage_path + "/Shader")
        attr = mtl.CreateAttribute("inputs:tag_mosaic", Sdf.ValueTypeNames.Asset)
        attr.Set(Sdf.AssetPath(assets_root_path + tag_path))

    asyncio.ensure_future(create_tag())


# -----------------------------------------------------------------------------
# Class CreateMenuExtension
# -----------------------------------------------------------------------------
class CreateMenuExtension:
    def __init__(self, ext_id):
        self._ext_id = ext_id
        self._menu_categories = []

        self.__menu_layout = [
            MenuLayout.Menu(
                "Create",
                [
                    MenuLayout.Item("Mesh"),
                    MenuLayout.Item("Shape"),
                    MenuLayout.Item("Lights", source="Create/Light"),
                    MenuLayout.Item("Audio"),
                    MenuLayout.Item("Camera"),
                    MenuLayout.Item("Scope"),
                    MenuLayout.Item("Xform", source="Create/Xform"),
                    MenuLayout.Item("Materials", source="Create/Material"),
                    MenuLayout.Item("Graphs", source="Create/Visual Scripting"),
                    MenuLayout.Item("Arbitrary Output Variables (AOV)", source="Create/AOV"),
                    MenuLayout.Item("Physics", source="Create/Physics"),
                    MenuLayout.Seperator("Assets"),
                    MenuLayout.SubMenu(
                        "Robots",
                        [
                            MenuLayout.Item("Asset Browser"),
                            MenuLayout.Seperator("Actuators"),
                            MenuLayout.Item("Surface Gripper"),
                            MenuLayout.Seperator("Examples"),
                        ],
                    ),
                    MenuLayout.SubMenu(
                        "Environments",
                        [
                            MenuLayout.Item(name="Asset Browser"),
                            MenuLayout.Seperator("Examples"),
                        ],
                    ),
                    MenuLayout.SubMenu(
                        "Sensors",
                        [
                            MenuLayout.Item(name="Asset Browser"),
                            MenuLayout.Seperator("Generic Sensors"),
                        ],
                    ),
                    # MenuLayout.Item("ROS 2 Assets", source="Create/ROS 2 Assets"),
                    MenuLayout.SubMenu(
                        "ROS 2 Assets",
                        [
                            MenuLayout.Item("Asset Browser", source="Create/ROS 2 Assets/Asset Browser"),
                            MenuLayout.Seperator("Examples"),
                            MenuLayout.Item("Room", source="Create/ROS 2 Assets/Room"),
                            MenuLayout.Item("Room 2", source="Create/ROS 2 Assets/Room 2"),
                        ],
                    ),
                ],
            )
        ]

        omni.kit.menu.utils.add_layout(self.__menu_layout)

        # turn dictionary into menu items
        def create_submenu(menu_dict):
            # Handle non-nested menu items
            if "name" in menu_dict and isinstance(menu_dict["name"], str):
                return [
                    MenuItemDescription(
                        name=menu_dict["name"],
                        onclick_fn=menu_dict.get("onclick_fn"),
                        onclick_action=menu_dict.get("onclick_action"),
                        glyph=menu_dict.get("glyph"),
                    )
                ]

            # Handle nested submenus recursively
            submenu_name = next(iter(menu_dict["name"]))
            items = menu_dict["name"][submenu_name]
            sub_menu_items = []
            for item in items:
                if isinstance(item.get("name"), dict):
                    # Recursively handle nested submenu
                    sub_menu_items.append(create_submenu(item))
                else:
                    # Handle leaf menu item
                    sub_menu_items.append(
                        MenuItemDescription(
                            name=item["name"],
                            onclick_fn=item.get("onclick_fn"),
                            onclick_action=item.get("onclick_action"),
                        )
                    )

            return [MenuItemDescription(name=submenu_name, sub_menu=sub_menu_items, glyph=menu_dict.get("glyph"))]

        icon_dir = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        robot_icon_path = str(Path(icon_dir).joinpath("data/robot.svg"))

        robot_menu_dict = {
            "name": {
                "Robots": [
                    {
                        "name": "Ant",
                        "onclick_fn": lambda *_: create_asset(
                            "/Isaac/Robots/IsaacSim/Ant/ant_instanceable.usd", "/Ant"
                        ),
                    },
                    {
                        "name": "Boston Dynamics Spot (Quadruped)",
                        "onclick_fn": lambda *_: create_asset("/Isaac/Robots/BostonDynamics/spot/spot.usd", "/spot"),
                    },
                    {
                        "name": "Franka Emika Panda Arm",
                        "onclick_fn": lambda *_: create_asset(
                            "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd", "/Franka"
                        ),
                    },
                    {
                        "name": "Humanoid",
                        "onclick_fn": lambda *_: create_asset(
                            "/Isaac/Robots/IsaacSim/Humanoid/humanoid_instanceable.usd", "/Humanoid"
                        ),
                    },
                    {
                        "name": "Nova Carter with Sensors",
                        "onclick_fn": lambda *_: create_asset(
                            "/Isaac/Robots/NVIDIA/NovaCarter/nova_carter.usd", "/Nova_Carter"
                        ),
                    },
                    {
                        "name": "Quadcopter",
                        "onclick_fn": lambda *_: create_asset(
                            "/Isaac/Robots/IsaacSim/Quadcopter/quadcopter.usd", "/Quadcopter"
                        ),
                    },
                    {
                        "name": "Asset Browser",
                        "onclick_action": ("isaacsim.asset.browser", "open_isaac_sim_asset_browser"),
                    },
                ]
            },
            "glyph": robot_icon_path,
        }

        self._menu_categories.append(add_menu_items(create_submenu(robot_menu_dict), "Create"))

        ## Environments
        environment_menu_dict = {
            "name": {
                "Environments": [
                    {
                        "name": "Black Grid",
                        "onclick_fn": lambda *_: create_asset(
                            "/Isaac/Environments/Grid/gridroom_black.usd", "/BlackGrid"
                        ),
                    },
                    {
                        "name": "Flat Grid",
                        "onclick_fn": lambda *_: create_asset(
                            "/Isaac/Environments/Grid/default_environment.usd", "/FlatGrid"
                        ),
                    },
                    {
                        "name": "Simple Room",
                        "onclick_fn": lambda *_: create_asset(
                            "/Isaac/Environments/Simple_Room/simple_room.usd",
                            "/SimpleRoom",
                            [3.15, 3.15, 2.0],
                            [0, 0, 0],
                        ),
                    },
                    {
                        "name": "Asset Browser",
                        "onclick_action": ("isaacsim.asset.browser", "open_isaac_sim_asset_browser"),
                    },
                ]
            },
            "glyph": str(Path(icon_dir).joinpath("data/environment.svg")),
        }

        self._menu_categories.append(add_menu_items(create_submenu(environment_menu_dict), "Create"))

        ## Sensor
        sensor_sub_menu = [
            MenuItemDescription(
                name="Asset Browser", onclick_action=("isaacsim.asset.browser", "open_isaac_sim_asset_browser")
            ),
        ]
        sensor_icon_path = str(Path(icon_dir).joinpath("data/sensor.svg"))
        sensor_menu = [MenuItemDescription(name="Sensors", glyph=sensor_icon_path, sub_menu=sensor_sub_menu)]
        self._menu_categories.append(add_menu_items(sensor_menu, "Create"))

        ## April Tags
        apriltag_menu_dict = {
            "name": "April Tags",
            "onclick_action": (ext_id, "isaac_create_apriltag"),
            "glyph": str(Path(icon_dir).joinpath("data/apriltag.svg")),
        }
        self._menu_categories.append(add_menu_items(create_submenu(apriltag_menu_dict), "Create"))

        ## add apriltag selection
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.register_action(
            ext_id,
            "isaac_create_apriltag",
            lambda: create_apriltag(
                "/Isaac/Materials/AprilTag/AprilTag.mdl",
                "AprilTag",
                "/Looks/AprilTag",
                "/Isaac/Materials/AprilTag/Textures/tag36h11.png",
            ),
            display_name="Create AprilTag",
            description="Create a AprilTag",
            tag="Create AprilTag",
        )

        # Matching the Create in Context Menus (Viewport and Stage)
        def remove_asset_browser(menu_dict):
            new_dict = {}
            for key, value in menu_dict.items():
                if isinstance(value, dict):
                    new_dict[key] = remove_asset_browser(value)
                elif isinstance(value, list):
                    new_dict[key] = [x for x in value if x.get("name") != "Asset Browser"]
                elif value != "Asset Browser":
                    new_dict[key] = value
            return new_dict

        # Remove the Asset Browser from robot, environment
        robot_context_menu_dict = remove_asset_browser(robot_menu_dict)
        environment_context_menu_dict = remove_asset_browser(environment_menu_dict)

        isaac_create_menu_dict = {
            "name": {
                "Isaac": [
                    robot_context_menu_dict,
                    environment_context_menu_dict,
                    apriltag_menu_dict,
                ]
            },
            "glyph": str(Path(icon_dir).joinpath("data/robot.svg")),
        }

        self._viewport_create_menu = omni.kit.context_menu.add_menu(
            isaac_create_menu_dict,
            "CREATE",
        )

    def shutdown(self):
        omni.kit.menu.utils.remove_layout(self.__menu_layout)
        for menu_item in self._menu_categories:
            remove_menu_items(menu_item, "Create")

        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_action(
            self._ext_id,
            "isaac_create_apriltag",
        )
        # remove_context_menus
        self._viewport_create_menu = None
