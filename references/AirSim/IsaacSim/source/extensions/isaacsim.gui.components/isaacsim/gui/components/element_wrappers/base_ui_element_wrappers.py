# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import omni.ui as ui
from isaacsim.gui.components.ui_utils import get_style


class UIWidgetWrapper:
    """
    Base class for creating wrappers around any subclass of omni.ui.Widget in order to provide an easy interface
    for creating and managing specific types of widgets such as state buttons or file pickers.
    """

    def __init__(self, container_frame: ui.Frame):
        self._container_frame = container_frame

    @property
    def container_frame(self) -> ui.Frame:
        return self._container_frame

    @property
    def enabled(self) -> bool:
        return self.container_frame.enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.container_frame.enabled = value

    @property
    def visible(self) -> bool:
        return self.container_frame.visible

    @visible.setter
    def visible(self, value: bool):
        self.container_frame.visible = value

    def cleanup(self):
        """
        Perform any necessary cleanup
        """
        pass
