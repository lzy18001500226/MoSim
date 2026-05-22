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
from functools import partial

import carb
import omni.client
import omni.kit.commands
from isaacsim.asset.importer.urdf import _urdf
from isaacsim.ros2.urdf.RobotDescription import RobotDefinitionReader
from omni.client import Result
from pxr import Usd, UsdUtils


class URDFImportFromROS2Node(omni.kit.commands.Command):
    def __init__(
        self,
        ros2_node_name: str = "robot_state_publisher",
        import_config=_urdf.ImportConfig(),
        dest_path: str = "",
        get_articulation_root: bool = False,
    ):
        self.ros2_node_name = ros2_node_name
        self.dest_path = dest_path
        self.config = import_config
        self.robot_definition = RobotDefinitionReader()
        self.robot_definition.description_received_fn = partial(self.on_description_received)
        self.robot_model = None
        self.finished = False
        self.__subscription = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self.on_app_update,
            observer_name="isaacsim.ros2.urdf.commands.URDFImportFromROS2Node._on_app_update",
        )

    def on_app_update(self, event):
        if self.finished:
            self.__subscription = None
            if self.robot_model:
                self.import_robot(self.robot_model)
            return

    def on_description_received(self, urdf_description):

        result, robot_model = omni.kit.commands.execute(
            "URDFParseText", urdf_string=urdf_description, import_config=self.config
        )
        if result:
            self.finished = True
            self.robot_model = robot_model

    def import_robot(self, robot_model):
        if self.dest_path == "":
            all_cache_stage = UsdUtils.StageCache.Get().GetAllStages()
            if len(all_cache_stage) == 1:
                result = omni.kit.commands.execute(
                    "URDFImportRobot",
                    urdf_robot=robot_model,
                    import_config=self.config,
                    dest_path=self.dest_path,
                )
                return all_cache_stage[0].GetRootLayer().identifier
        else:
            result = omni.kit.commands.execute(
                "URDFImportRobot",
                urdf_robot=robot_model,
                import_config=self.config,
                dest_path=self.dest_path,
            )
            stage = Usd.Stage.Open(self.dest_path)
            prim_name = str(stage.GetDefaultPrim().GetName())

            # print(prim_name)
            # stage.Save()
            def add_reference_to_stage():
                current_stage = omni.usd.get_context().get_stage()
                if current_stage:
                    prim_path = omni.usd.get_stage_next_free_path(
                        current_stage, str(current_stage.GetDefaultPrim().GetPath()) + "/" + prim_name, False
                    )
                    robot_prim = current_stage.OverridePrim(prim_path)
                    if "anon:" in current_stage.GetRootLayer().identifier:
                        robot_prim.GetReferences().AddReference(self.dest_path)
                    else:
                        robot_prim.GetReferences().AddReference(
                            omni.client.make_relative_url(current_stage.GetRootLayer().identifier, self.dest_path)
                        )

            add_reference_to_stage()

    def do(self) -> Result:

        self.robot_definition.start_get_robot_description(self.ros2_node_name)
