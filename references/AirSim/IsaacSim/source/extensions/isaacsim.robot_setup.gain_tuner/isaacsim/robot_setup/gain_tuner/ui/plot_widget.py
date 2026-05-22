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
from typing import Callable, List, Optional, Tuple, Union

import numpy as np
import omni.ui as ui
from isaacsim.gui.components.element_wrappers import Frame, XYPlot

LABEL_HEIGHT = 14


class CustomXYPlot(XYPlot):
    def __init__(
        self,
        x_data: Union[List[List], List] = [],
        y_data: Union[List[List], List] = [],
        header_count: int = 0,
        show_legend: bool = False,
        legends: List[str] = None,
        data_colors: List[List[int]] = None,
    ):
        self._data_colors = data_colors
        self._header_count = header_count
        super().__init__(
            "",
            x_data=x_data,
            y_data=y_data,
            show_legend=show_legend,
            legends=legends,
        )

    def set_data_colors(self, data_colors: List[int]):
        self._data_colors = data_colors
        self._container_frame.rebuild()

    def _build_widget(self):
        self._plot_frames = []
        self._plots = []

        self._color_widgets = []
        self._show_plot_cbs = []

        LINE_HEIGHT = 23

        label = self._label
        tooltip = self._tooltip
        x_label = self._x_label
        y_label = self._y_label
        plot_num_lines = self._plot_num_lines

        plot_height = plot_num_lines * LINE_HEIGHT

        x_fracs, y_data, x_min, x_max = self._get_interpolated_data(self._x_min, self._x_max)
        self._x_min = x_min
        self._x_max = x_max
        self._interpolated_y_data = y_data
        self._x_fracs = x_fracs

        self._data_colors = self._get_data_colors(len(y_data))
        group_num = int(len(self._x_data) / (self._header_count))

        def on_show_legend(model):
            if model.get_value_as_bool():
                self._show_legend = True
                self._legend_frame.visible = True
                self._legend_frame.rebuild()
            else:
                self._show_legend = False
                self._legend_frame.visible = False

        def build_legend_frame():
            def toggle_plot_visibility(show, i):
                for j in range(group_num * i, group_num * (i + 1)):
                    self._is_plot_visible[j] = show
                    if j < len(self._plot_frames):
                        self._plot_frames[j].visible = show

            legends = ["Command Joint", "Observed Joint", "User Data Driven"]
            self._show_plot_cbs = []
            with ui.HStack(spacing=3):
                ui.Spacer(width=10)
                for i in range(self._header_count):
                    with ui.VStack():
                        with ui.HStack():
                            model = ui.SimpleBoolModel()
                            model.set_value(self._is_plot_visible[i])
                            show_plot_cb = ui.CheckBox(model=model, width=10)
                            self._show_plot_cbs.append(show_plot_cb)
                            model.add_value_changed_fn(
                                lambda model, idx=i: toggle_plot_visibility(model.get_value_as_bool(), idx)
                            )
                            ui.Spacer(width=3)
                            ui.Label(legends[i], alignment=ui.Alignment.LEFT, height=LABEL_HEIGHT)
                            ui.Spacer()
                        ui.Spacer(height=2)
                        with ui.HStack(spacing=0):
                            for i in range(group_num * i, group_num * (i + 1)):
                                ui.Line(
                                    width=ui.Fraction(self._header_count / len(self._x_data)),
                                    style={"color": self._data_colors[i], "border_width": 4},
                                )
                    ui.Spacer(width=10)

        def set_x_axis_values(low, high):
            assert high >= low

            if high == low:
                high = low + 0.0001

                # Handle float overflow
                if high == low:
                    return

            num_fields = len(self._x_axis_float_fields)
            spacing = (high - low) / num_fields
            num_decimals = int(max(0, np.log10(5 / (high - low)) + 2))

            self._x_max_float_drag.step = (high - low) / 20
            self._x_min_float_drag.step = (high - low) / 20
            for i, float_field in enumerate(self._x_axis_float_fields):
                float_field.text = str(np.round(low + spacing / 2 + spacing * i, decimals=num_decimals))

        def set_y_axis_values(low, high):
            assert high >= low

            if high == low:
                high = low + 0.0001

                # Handle float overflow
                if high == low:
                    return

            num_fields = len(self._y_axis_float_fields)
            spacing = (high - low) / num_fields
            num_decimals = int(max(0, np.log10(5 / (high - low)) + 2))
            self._y_min_float_drag.step = (high - low) / 20
            self._y_max_float_drag.step = (high - low) / 20
            for i, float_field in enumerate(self._y_axis_float_fields):
                float_field.text = str(np.round(high - spacing / 2 - spacing * i, decimals=num_decimals))

        def build_x_axis_frame():
            self._x_axis_float_fields = []

            def update_x_min(model):
                self._x_min = model.as_float
                if self._x_min >= self._x_max:
                    self._x_max = self._x_min + 1.0
                    self._x_max_float_drag.model.set_value(self._x_max)
                self._x_fracs, self._interpolated_y_data, _, _ = self._get_interpolated_data(
                    x_min=self._x_min, x_max=self._x_max
                )

                for i, plot_frame in enumerate(self._plot_frames):
                    plot_frame.set_build_fn(
                        build_fn=lambda x_fracs=self._x_fracs[i], y_data=self._interpolated_y_data[
                            i
                        ], color_idx=i: build_plot(x_fracs, y_data, color_idx)
                    )

                set_x_axis_values(self._x_min, self._x_max)

            def update_x_max(model):
                self._x_max = model.as_float
                if self._x_max <= self._x_min:
                    self._x_min = self._x_max - 1.0
                    self._x_min_float_drag.model.set_value(self._x_min)
                self._x_fracs, self._interpolated_y_data, _, _ = self._get_interpolated_data(
                    x_min=self._x_min, x_max=self._x_max
                )

                for i, plot_frame in enumerate(self._plot_frames):
                    plot_frame.set_build_fn(
                        build_fn=lambda x_fracs=self._x_fracs[i], y_data=self._interpolated_y_data[
                            i
                        ], color_idx=i: build_plot(x_fracs, y_data, color_idx)
                    )

                set_x_axis_values(self._x_min, self._x_max)

            with ui.HStack():
                self._x_min_float_drag = ui.FloatDrag(name="Field", alignment=ui.Alignment.LEFT_TOP, tooltip="X Min")
                x_min_model = self._x_min_float_drag.model
                x_min_model.set_value(
                    self._x_min
                )  # There is blank space between the plotted line and the sides of the plot's colored rectangle
                for i in range(plot_num_lines):
                    float_field = ui.Label("", alignment=ui.Alignment.CENTER)
                    self._x_axis_float_fields.append(float_field)

                self._x_max_float_drag = ui.FloatDrag(name="Field", alignment=ui.Alignment.LEFT_BOTTOM, tooltip="X Max")
                x_max_model = self._x_max_float_drag.model
                x_max_model.set_value(self._x_max)

                x_min_model.add_value_changed_fn(update_x_min)
                x_max_model.add_value_changed_fn(update_x_max)

            set_x_axis_values(x_min, x_max)

        def build_y_axis_frame():
            # Add fields for controlling min and max y values on plot
            def update_y_min(model):
                self._y_min = model.as_float

                if self._y_min >= self._y_max:
                    self._y_max = self._y_min + 1.0
                    self._y_max_float_drag.model.set_value(self._y_max)

                for plot in self._plots:
                    plot.scale_min = model.as_float

                set_y_axis_values(self._y_min, self._y_max)

            def update_y_max(model):
                self._y_max = model.as_float
                if self._y_max <= self._y_min:
                    self._y_min = self._y_max - 1.0
                    self._y_min_float_drag.model.set_value(self._y_min)

                for plot in self._plots:
                    plot.scale_max = model.as_float

                set_y_axis_values(self._y_min, self._y_max)

            y_max = self.get_y_max()
            y_min = self.get_y_min()

            if y_min is None:
                y_min = 0.0
            self._y_min = y_min

            if y_max is None:
                y_max = y_min + 1.0
            self._y_max = y_max

            with ui.HStack(spacing=2):
                # Make it wide enough to contain the text on one line with a minimum size of 60 pixels
                label_frame_width = 20

                # Make axis markers
                self._y_axis_float_fields = []
                with ui.Frame(height=plot_height):

                    with ui.VStack(spacing=0):
                        self._y_max_float_drag = ui.FloatDrag(
                            name="Field",
                            # width=label_frame_width,
                            height=LABEL_HEIGHT,
                            alignment=ui.Alignment.CENTER,
                            tooltip="Y Max",
                        )
                        y_max_model = self._y_max_float_drag.model

                        y_max_model.set_value(y_max)
                        # ui.Spacer(height=3)  # There is blank space between the plotted line and the edges of the plot's colored rectangle
                        for i in range(plot_num_lines):
                            float_field = ui.Label("", alignment=ui.Alignment.CENTER)
                            self._y_axis_float_fields.append(float_field)
                        # ui.Spacer(height=3)
                        self._y_min_float_drag = ui.FloatDrag(
                            name="Field",
                            # width=label_frame_width,
                            height=LABEL_HEIGHT,
                            alignment=ui.Alignment.CENTER,
                            tooltip="Y Min",
                        )
                        y_min_model = self._y_min_float_drag.model
                        y_min_model.set_value(y_min)

                        y_min_model.add_value_changed_fn(update_y_min)
                        y_max_model.add_value_changed_fn(update_y_max)

            set_y_axis_values(y_min, y_max)

        def build_plot(x_fracs, y_data, color_idx):
            """Build the frame for a plot

            Args:
                x_fracs (np.array (2,)): Fraction of available space that the plot should cover
                y_data (np.array): data with which to fill the plot
            """

            color = self._data_colors[color_idx]
            visible = self._is_plot_visible[color_idx]
            with ui.HStack():
                # ui.Frame is the only omni.ui object that seems to consistently obey the given spacing rules
                # So each plot is on a Frame between two other invisible frames to get the placement right
                w = self._base_plot.computed_width
                if w == 0:
                    return

                # Plots have 6 pixel margins on them, so the fraction of the figure occupied needs to be modified
                x_low = max(0.0, x_fracs[0] - 6 / w)
                x_high = min(1.0, x_fracs[1] + 6 / w)
                y_min = self.get_y_min()
                y_max = self.get_y_max()
                if y_min is None:
                    y_min = 0.0
                if y_max is None:
                    y_max = 1.0

                f = ui.Frame(width=ui.Fraction(x_low))
                with ui.Frame(width=ui.Fraction(x_high - x_low)):
                    plot = ui.Plot(
                        ui.Type.LINE,
                        y_min,
                        y_max,
                        *y_data,
                        height=plot_height,
                        style={"color": color, "background_color": 0x0},
                    )
                    self._plots.append(plot)
                ui.Frame(width=ui.Fraction(1 - x_high))

        with ui.ZStack():
            with ui.VStack(spacing=3):
                ui.Spacer(height=10)
                with ui.HStack(height=30):
                    ui.Spacer(width=10)
                    self._legend_frame = ui.Frame(build_fn=build_legend_frame)
                    self._legend_frame.rebuild()
                    self._legend_frame.visible = self._show_legend
                    ui.Spacer(width=10)
                with ui.HStack():
                    ui.Spacer(width=10)
                    with ui.HStack(spacing=0):
                        # Make the y axis label
                        y_axis_frame = ui.Frame(build_fn=build_y_axis_frame, width=ui.Fraction(0.1))

                        # VStack the plot on top of the X axis label
                        with ui.VStack(spacing=0):

                            # ZStacking everything that goes on the actual data plot
                            with ui.ZStack():
                                ui.Rectangle(height=plot_height)
                                self._base_plot = ui.Plot(ui.Type.LINE, 0.0, 1.0, 0.0, style={"background_color": 0x0})
                                for i in range(len(y_data)):
                                    plot_frame = Frame(
                                        build_fn=lambda x_fracs=x_fracs[i], y_data=y_data[i], color_idx=i: build_plot(
                                            x_fracs, y_data, color_idx
                                        )
                                    )
                                    plot_frame.visible = (
                                        self._is_plot_visible[i] if i < len(self._is_plot_visible) else False
                                    )
                                    self._plot_frames.append(plot_frame)

                                # Create an invisible frame on top that will give a helpful tooltip
                                self._tooltip_frame = ui.Plot(
                                    mouse_moved_fn=self._mouse_moved_on_plot,
                                    style={"color": 0xFFFFFFFF, "background_color": 0x0},
                                )
                                self._tooltip_frame.set_mouse_pressed_fn(self._mouse_moved_on_plot)
                                self._tooltip_frame.set_mouse_released_fn(self._on_mouse_released)
                                self._tooltip_frame.set_computed_content_size_changed_fn(
                                    lambda *args: [plot.rebuild() for plot in self._plot_frames]
                                )
                                # Make the tooltip invisible
                                self._on_mouse_released()

                            # Create the x axis label
                            x_axis_frame = Frame(build_fn=build_x_axis_frame).frame
                            x_axis_frame.rebuild()

                    ui.Spacer(width=10)
                ui.Spacer(height=10)
            ui.Rectangle(
                height=ui.Fraction(1),
                width=ui.Fraction(1),
                style={"background_color": 0x0, "border_width": 1, "border_color": 0xFF000000, "border_radius": 1},
            )

        self._has_built = True
