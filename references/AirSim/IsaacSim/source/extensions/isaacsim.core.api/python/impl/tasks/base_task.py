# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from typing import Optional

import numpy as np
from isaacsim.core.api.scenes.scene import Scene
from isaacsim.core.api.simulation_context import SimulationContext


class BaseTask(object):
    """This class provides a way to set up a task in a scene and modularize adding objects to stage,
    getting observations needed for the behavioral layer, calculating metrics needed about the task,
    calling certain things pre-stepping, creating multiple tasks at the same time and much more.

    Checkout the required tutorials at https://docs.isaacsim.omniverse.nvidia.com/latest/index.html

    Args:
        name (str): needs to be unique if added to the World.
        offset (Optional[np.ndarray], optional): offset applied to all assets of the task.
    """

    def __init__(self, name: str, offset: Optional[np.ndarray] = None) -> None:
        self._scene = None
        self._name = name
        self._offset = offset
        self._task_objects = dict()
        if self._offset is None:
            self._offset = np.array([0.0, 0.0, 0.0])

        if SimulationContext.instance() is not None:
            self._device = SimulationContext.instance().device
        return

    @property
    def device(self):
        return self._device

    @property
    def scene(self) -> Scene:
        """Scene of the world

        Returns:
            Scene: [description]
        """
        return self._scene

    @property
    def name(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return self._name

    def set_up_scene(self, scene: Scene) -> None:
        """Adding assets to the stage as well as adding the encapsulated objects such as SingleXFormPrim..etc
           to the task_objects happens here.

        Args:
            scene (Scene): [description]
        """
        self._scene = scene
        return

    def _move_task_objects_to_their_frame(self):

        # if self._task_path:
        # TODO: assumption all task objects are under the same parent
        # Specifying a task path has many limitations atm
        # SingleXFormPrim(prim_path=self._task_path, position=self._offset)
        # for object_name, task_object in self._task_objects.items():
        #     new_prim_path = self._task_path + "/" + task_object.prim_path.split("/")[-1]
        #     task_object.change_prim_path(new_prim_path)
        #     current_position, current_orientation = task_object.get_world_pose()
        for object_name, task_object in self._task_objects.items():
            current_position, current_orientation = task_object.get_world_pose()
            task_object.set_world_pose(position=current_position + self._offset)
            task_object.set_default_state(position=current_position + self._offset)
        return

    def get_task_objects(self) -> dict:
        """[summary]

        Returns:
            dict: [description]
        """
        return self._task_objects

    def get_observations(self) -> dict:
        """Returns current observations from the objects needed for the behavioral layer.

        Raises:
            NotImplementedError: [description]

        Returns:
            dict: [description]
        """
        raise NotImplementedError

    def calculate_metrics(self) -> dict:
        """[summary]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def is_done(self) -> bool:
        """Returns True of the task is done.

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def pre_step(self, time_step_index: int, simulation_time: float) -> None:
        """called before stepping the physics simulation.

        Args:
            time_step_index (int): [description]
            simulation_time (float): [description]
        """
        return

    def post_reset(self) -> None:
        """Calls while doing a .reset() on the world."""
        return

    def get_description(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return ""

    def cleanup(self) -> None:
        """Called before calling a reset() on the world to removed temporary objects that were added during
        simulation for instance.
        """
        return

    def set_params(self, *args, **kwargs) -> None:
        """Changes the modifiable parameters of the task

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def get_params(self) -> dict:
        """Gets the parameters of the task.
           This is defined differently for each task in order to access the task's objects and values.
           Note that this is different from get_observations.
           Things like the robot name, block name..etc can be defined here for faster retrieval.
           should have the form of params_representation["param_name"] = {"value": param_value, "modifiable": bool}

        Raises:
            NotImplementedError: [description]

        Returns:
            dict: defined parameters of the task.
        """
        raise NotImplementedError
