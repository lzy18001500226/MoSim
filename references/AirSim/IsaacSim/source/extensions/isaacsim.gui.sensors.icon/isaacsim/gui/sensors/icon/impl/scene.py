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
__all__ = ["IconScene"]

import carb.input
import carb.settings
import omni.timeline
import omni.ui as ui
from omni.ui import scene as sc

from .manipulator import IconManipulator, PreventOthers
from .model import IconModel

VISIBLE_SETTING = "/persistent/exts/isaacsim.gui.sensors.icon/visible_on_startup"


class IconScene:  # pragma: no cover
    """The window with the manupulator"""

    def __init__(self, title: str = None, icon_scale: float = 1.0, **kwargs):
        self._sensor_icon = SensorIcon.get_instance()
        self._manipulater = IconManipulator(
            model=self._sensor_icon.get_model(),
            aspect_ratio_policy=sc.AspectRatioPolicy.PRESERVE_ASPECT_HORIZONTAL,
            icon_scale=icon_scale,
        )
        prevent_others = PreventOthers()

        # we don't want the prim icon show outside the viewport area
        # so we need do check on end drag,
        # don't check it on change(dragging) to get a better performance
        right_drag_gesture = sc.DragGesture(
            name="SensorIcon_look_drag",
            on_ended_fn=lambda sender: self._end_drag(sender),
            mouse_button=1,  # hook right button
            manager=prevent_others,
        )

        left_drag_gesture = sc.DragGesture(
            name="SensorIcon_navigation_drag",  # naigation bar use left button to drag
            on_ended_fn=lambda sender: self._end_drag(sender),
            mouse_button=0,  # hook left button
            manager=prevent_others,
        )

        # TODO: This would cause crash when click the prim icon,
        # note it until find a better solution
        # self._screen = sc.Screen(gestures=[
        #     right_drag_gesture,
        #     left_drag_gesture
        # ])
        self.visible = True

    def _end_drag(self, sender):
        self._manipulater.rebuild_icons(need_check=True)

    @property
    def visible(self):
        return self._manipulater.visible

    @visible.setter
    def visible(self, value: bool):
        value = bool(value)
        # self._model.beam_visible = value
        self._manipulater.visible = value

    def destroy(self):
        self.clear()
        self._manipulater = None

    def clear(self):
        if not self._manipulater:
            return
        self._manipulater.clear()

    def __del__(self):
        self.destroy()


class SensorIcon:
    _instance = None

    def __init__(self, test=False):
        self.model = IconModel()
        self._settings = carb.settings.get_settings()
        self._visible_sub = self._settings.subscribe_to_node_change_events(VISIBLE_SETTING, self._on_visible_changed)
        self.toggle_all_fn = []
        self._timeline = omni.timeline.get_timeline_interface()

        if self._settings.get(VISIBLE_SETTING) is False:
            self.model.hide_all()

        self.timeline_event_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event, name="SensorIconTimelineEventHandler"
        )

    def _on_timeline_event(self, event):
        if event.type == int(omni.timeline.TimelineEventType.STOP):
            if self.model:
                self.model.refresh_all_icon_visuals()

    def _on_visible_changed(self, *args):
        if not self.model:
            return

        visible = self._settings.get(VISIBLE_SETTING)
        if visible:
            self.model.show_all()
        else:
            self.model.hide_all()
        for fn in self.toggle_all_fn:
            fn(visible)

    def register_toggle_all_fn(self, fn):
        self.toggle_all_fn.append(fn)

    def unregister_toggle_all_fn(self, fn):
        self.toggle_all_fn.remove(fn)

    @staticmethod
    def get_instance():
        if not SensorIcon._instance:
            SensorIcon._instance = SensorIcon()
        return SensorIcon._instance

    def destroy(self):
        if self.timeline_event_sub:
            self.timeline_event_sub = None

        self.clear()
        self.model = None
        SensorIcon._instance = None

    def get_model(self):
        return self.model

    def add_sensor_icon(self, prim_path, icon_url=None):
        if not self.model:
            return
        self.model.add_sensor_icon(prim_path, icon_url)

    def remove_sensor_icon(self, prim_path):
        if not self.model:
            return
        self.model.remove_sensor_icon(prim_path)

    def set_icon_click_fn(self, prim_path, call_back):
        if not self.model:
            return
        self.model.set_icon_click_fn(prim_path, call_back)

    def show_sensor_icon(self, prim_path):
        if not self.model:
            return
        self.model.show_sensor_icon(prim_path)

    def hide_sensor_icon(self, prim_path):
        if not self.model:
            return
        self.model.hide_sensor_icon(prim_path)

    def clear(self):
        if not self.model:
            return
        self.model.clear()
