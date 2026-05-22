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
import carb
import omni.kit.commands
from omni.kit.widget.stage import ContextMenu
from omni.kit.widget.stage.stage_delegate import StageDelegate

from ..builders.robot_templates import RobotRegistry


class RobotContextMenu(ContextMenu):
    def on_mouse_event(self, event):
        import omni.kit.menu.core

        # check its expected event
        if event.type != int(omni.kit.menu.core.MenuEventType.ACTIVATE):
            return

        try:
            import omni.kit.context_menu
        except ModuleNotFoundError:
            return
        # get context menu core functionality & check its enabled
        context_menu = omni.kit.context_menu.get_instance()
        if context_menu is None:
            carb.log_error("context_menu is disabled!")
            return

        # get stage
        stage = event.payload.get("stage", None)
        if stage is None:
            carb.log_error("stage not avaliable")
            return None

        # get parameters passed by event
        prim_path = event.payload["prim_path"]

        # setup objects, this is passed to all functions
        objects = {}
        objects["use_hovered"] = True if prim_path else False
        objects["stage_win"] = self._stage_win
        objects["node_open"] = event.payload["node_open"]
        objects["stage"] = stage
        objects["function_list"] = self.function_list
        objects["stage_model"] = self._stage_model

        prim_list = []
        hovered_prim = event.payload["prim_path"]
        paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        if len(paths) > 0:
            for path in paths:
                prim = stage.GetPrimAtPath(path)
                if prim:
                    prim_list.append(prim)
                    if prim == hovered_prim:
                        hovered_prim = None

        elif prim_path is not None:
            prim = stage.GetPrimAtPath(prim_path)
            if prim:
                prim_list.append(prim)

        if prim_list:
            objects["prim_list"] = prim_list
        if hovered_prim:
            objects["hovered_prim"] = stage.GetPrimAtPath(hovered_prim)

        # setup menu
        menu_dict = [
            {
                "name": "Mark as Reference to Align Parent Link",
                "glyph": "menu_rename.svg",
                "show_fn": [self._can_align_parent_link_origin, self._is_prim_selected, self.is_one_prim_selected],
                "onclick_fn": self._align_parent_link_origin,
            },
            {
                "name": "Delete",
                "glyph": "menu_delete.svg",
                "show_fn": [self._is_prim_selected, self._can_delete],
                "onclick_fn": self._delete_prims,
            },
        ]

        # show menu
        try:
            context_menu.show_context_menu("robot_stage_window", objects, menu_dict)
        except Exception as e:
            print(f"Error showing context menu: {str(e)}")

    def _can_align_parent_link_origin(self, objects):
        if not "prim_list" in objects:
            return False
        prim_list = objects["prim_list"][0]  # only process one prim at a time
        # break down path of the prim and it needs to have at least 3 parts (robot/link/link_name)
        path_parts = prim_list.GetPath().pathString.split("/")
        if len(path_parts) < 4:
            return False
        else:
            return True

    def _align_parent_link_origin(self, objects):
        registered_robot = RobotRegistry().get()
        if registered_robot is None:
            return False
        ref_prim_path = objects["prim_list"][0].GetPath().pathString
        # if registered_robot already has reference mesh property, get it, otherwise,= add_property
        if not hasattr(registered_robot, "reference_mesh"):
            registered_robot.add_property(registered_robot.__class__, "reference_mesh", {})

        parent_link_path = "/".join(ref_prim_path.split("/")[:3])  # the first three parts of the path

        reference_mesh_table = registered_robot.reference_mesh
        reference_mesh_table[parent_link_path] = ref_prim_path
        registered_robot.reference_mesh = reference_mesh_table

        return True

    def _is_prim_selected(self, objects: dict):
        """
        Checks if any prims are selected

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if one or more prim is selected otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        return True

    def is_one_prim_selected(self, objects: dict):
        """
        Checks if one prim is selected.

        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if one prim is selected otherwise False.
        """
        if not "prim_list" in objects:
            return False
        return len(objects["prim_list"]) == 1

    def _can_delete(self, objects: dict):
        """
        Checks if prims can be deleted
        Args:
            objects (dict): context_menu data
        Returns:
            (bool): True if prim can be deleted otherwise False.
        """
        if not any(item in objects for item in ["prim", "prim_list"]):
            return False
        prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

        for prim in prim_list:
            if not prim.IsValid():
                return False
            no_delete = prim.GetMetadata("no_delete")
            if no_delete is not None and no_delete is True:
                return False
        return True

    def _delete_prims(self, objects: dict, destructive=True):
        """
        Delete prims

        Args:
            remove the prim from the robot_temp_stage, and mark the prim to delete during reorg
        """
        # remove the prim from the robot_temp_stage
        prims = objects.get("prim_list", [])
        stage = objects["stage"]
        if prims:
            for prim in prims:
                prim_path = prim.GetPath()
                stage.RemovePrim(prim_path)

        # marking it to be deleted during reorg
        registered_robot = RobotRegistry().get()
        if registered_robot is None:
            return False
        to_delete_prim_path = objects["prim_list"][0].GetPath().pathString
        # if registered_robot already has reference mesh property, get it, otherwise,= add_property
        if not hasattr(registered_robot, "delete_prim_paths"):
            registered_robot.add_property(registered_robot.__class__, "delete_prim_paths", [])

        delete_prim_paths = registered_robot.delete_prim_paths
        delete_prim_paths.append(to_delete_prim_path)
        registered_robot.delete_prim_paths = delete_prim_paths

        return True


class RobotStageDelegate(StageDelegate):

    def __init__(self):
        super().__init__(context_menu=RobotContextMenu())
