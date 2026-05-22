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
import weakref
from functools import partial
from typing import Optional

import omni.kit.app
import omni.ui as ui
import omni.usd
from omni.kit.widget.stage import StageWidget

from ..style import get_asset_picker_style


def filter_prims(stage, prim_list, type_list):
    if len(type_list) != 0:
        filtered_selection = []
        for item in prim_list:
            prim = stage.GetPrimAtPath(item.path)
            if prim:
                for _type in type_list:
                    if prim.IsA(_type):
                        filtered_selection.append(item)
                        break
        if filtered_selection != prim_list:
            return filtered_selection
    return prim_list


class SelectionWatch:
    def __init__(self, stage, on_selection_changed_fn, filter_type_list=[], targets_limit=0):
        self._stage = stage
        self._last_selected_prim_paths = None
        self._filter_type_list = filter_type_list
        self._on_selection_changed_fn = on_selection_changed_fn
        self._targets_limit = targets_limit
        self._tree_view = None

    def reset(self, stage):
        self.clear_selection()
        self._stage = weakref.ref(stage)

    def set_tree_view(self, tree_view):
        self._tree_view = tree_view
        self._tree_view.set_selection_changed_fn(self._on_widget_selection_changed)
        self._last_selected_prim_paths = None

    def clear_selection(self):
        if not self._tree_view:
            return

        self._tree_view.model.update_dirty()
        self._tree_view.selection = []
        if self._on_selection_changed_fn:
            self._on_selection_changed_fn([])

    def _on_widget_selection_changed(self, selection):
        stage = self._stage()
        if not stage:
            return

        prim_paths = [str(item.path) for item in selection if item]

        # Deselect instance proxy items if they were selected
        selection = [item for item in selection if item and not item.instance_proxy]

        # Although the stage view has filter, you can still select the ancestor of filtered prims, which might not match the type.
        selection = filter_prims(stage, selection, self._filter_type_list)

        # Deselect if over the limit
        if self._targets_limit > 0 and len(selection) > self._targets_limit:
            selection = selection[: self._targets_limit]

        if self._tree_view.selection != selection:
            self._tree_view.selection = selection
            prim_paths = [str(item.path) for item in selection]

        if prim_paths == self._last_selected_prim_paths:
            return

        self._last_selected_prim_paths = prim_paths
        if self._on_selection_changed_fn:
            self._on_selection_changed_fn(self._last_selected_prim_paths)

    def enable_filtering_checking(self, enable: bool):
        """
        It is used to prevent selecting the prims that are filtered out but
        still displayed when such prims have filtered children. When `enable`
        is True, SelectionWatch should consider filtering when changing Kit's
        selection.
        """

    def set_filtering(self, filter_string: Optional[str]):
        pass


class RobotAssetPicker:
    def __init__(
        self,
        title,
        stage,
        filter_type_list=[],
        on_targets_selected=None,
        modal_window=False,
        targets_limit=1,
        target_name="",
    ):
        self._weak_stage = weakref.ref(stage)
        self._selected_paths = []
        self._on_targets_selected = on_targets_selected
        self._filter_type_list = filter_type_list
        self._use_modal = modal_window
        self._targets_limit = targets_limit
        self._target_name = target_name
        self._selection_watch = SelectionWatch(
            stage=self._weak_stage,
            on_selection_changed_fn=self._on_selection_changed,
            filter_type_list=self._filter_type_list,
            targets_limit=self._targets_limit,
        )
        self._stage_widget = None
        self._window = ui.Window(
            f"{title}",
            width=600,
            height=800,
            visible=False,
            flags=ui.WINDOW_FLAGS_MODAL if self._use_modal else ui.WINDOW_FLAGS_NONE,
            visibility_changed_fn=self.on_window_visibility_changed,
        )
        self._window.frame.set_build_fn(self._build_frame)

    def _build_frame(self):
        with ui.VStack():
            with ui.Frame():
                self._stage_widget = StageWidget(None, columns_enabled=["Type"])
                self._stage_widget.set_selection_watch(self._selection_watch)

            with ui.VStack(height=0, style=get_asset_picker_style(), spacing=2):
                ui.Spacer(height=2)
                self._label = ui.Label(f"Selected {self._target_name}:\nNone")
                self._button = ui.Button(
                    "Select",
                    height=10,
                    clicked_fn=partial(RobotAssetPicker._on_select, weak_self=weakref.ref(self)),
                    enabled=False,
                    identifier="select_button",
                )
                ui.Spacer(height=4)
            self.on_window_visibility_changed(True)

    def on_window_visibility_changed(self, visible):
        # the _stage_widget not build yet, will call again in build frame
        if not self._stage_widget:
            return
        if not visible:
            if self._stage_widget:
                self._stage_widget.open_stage(None)
        else:
            # Only attach the stage when picker is open. Otherwise the Tf notice listener in StageWidget kills perf
            stage = omni.usd.get_context().get_stage()
            self._selection_watch.reset(stage)
            self._weak_stage = weakref.ref(stage)
            self._stage_widget.open_stage(self._weak_stage())
            if self._filter_type_list:
                self._stage_widget._filter_by_type(self._filter_type_list, False)
                self._stage_widget._filter_button.enable_filters(self._filter_type_list)

    def destroy(self):
        if self._window:
            self._window.destroy()
        self._window = None
        self._weak_stage = None

    @staticmethod
    def _on_select(weak_self: callable):
        # pylint: disable=protected-access
        weak_self = weak_self()
        if not weak_self:
            return

        if weak_self._on_targets_selected:
            weak_self._on_targets_selected(weak_self._selected_paths)
        weak_self._window.visible = False

    def set_on_selected(self, on_select):
        self._on_targets_selected = on_select

    def clean(self):
        self._window.set_visibility_changed_fn(None)
        self._window = None
        self._selection_watch = None
        self._stage_widget.open_stage(None)
        self._stage_widget.destroy()
        self._stage_widget = None
        self._filter_type_list = None
        self._on_targets_selected = None

    @property
    def visible(self):
        return self._window.visible

    @visible.setter
    def visible(self, visible):
        self._window.visible = visible

    def _on_selection_changed(self, paths):
        self._selected_paths = paths
        if self._button:
            self._button.enabled = len(self._selected_paths) > 0
        if self._label:
            text = "\n".join(self._selected_paths)
            label_text = f"Selected {self._target_name}"
            if self._targets_limit > 0:
                label_text += f" ({len(self._selected_paths)}/{self._targets_limit})"
            label_text += f":\n{text if text else 'None'}"
            self._label.text = label_text
