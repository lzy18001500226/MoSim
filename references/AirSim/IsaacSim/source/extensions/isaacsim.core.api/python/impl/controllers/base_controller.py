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
from abc import ABC, abstractmethod

from isaacsim.core.utils.types import ArticulationAction


class BaseController(ABC):
    """[summary]

    Args:
        name (str): [description]
    """

    def __init__(self, name: str) -> None:
        self._name = name

    @abstractmethod
    def forward(self, *args, **kwargs) -> ArticulationAction:
        """A controller should take inputs and returns an ArticulationAction to be then passed to the
           ArticulationController.

        Args:
            observations (dict): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            ArticulationAction: [description]
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Resets state of the controller."""
        return
