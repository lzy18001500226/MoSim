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
from typing import Callable

import omni.ui as ui


class Splitter:
    def __init__(self, build_left_fn: Callable[[], None], build_right_fn: Callable[[], None]):
        self._frame = ui.Frame()
        self._frame.set_build_fn(self.on_build)
        self.__build_left_fn = build_left_fn
        self.__build_right_fn = build_right_fn

    def destroy(self):
        self.__build_right_fn = None
        self.__build_left_fn = None
        self._frame = None

    def on_build(self):
        with ui.HStack():
            with ui.ZStack(width=0):
                # Left pannel
                with ui.Frame():
                    self.__build_left_fn()

                # Draggable splitter
                placer = ui.Placer(drag_axis=ui.Axis.X, offset_x=300.0, draggable=True)

                def left_moved(x):
                    placer.offset_x = max(230.0, x.value)

                placer.set_offset_x_changed_fn(left_moved)
                with placer:
                    with ui.ZStack(width=10):
                        ui.Rectangle(name="splitter")
                        ui.Rectangle(name="splitter_highlight", width=4)

            # Right pannel
            with ui.Frame():
                self.__build_right_fn()
