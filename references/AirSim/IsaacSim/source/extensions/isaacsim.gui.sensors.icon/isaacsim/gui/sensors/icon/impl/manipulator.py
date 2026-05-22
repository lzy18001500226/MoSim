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
__all__ = ["IconManipulator", "PreventOthers"]

import asyncio
import functools

import carb.settings
import omni.kit.app
import omni.kit.viewport.utility as vpUtil
import omni.ui as ui
from omni.ui import color as cl
from omni.ui import scene as sc
from pxr import Gf, Sdf

SHOW_TITLE_PATH = "exts/omni.kit.prim.icon/showTitle"


class PreventOthers(sc.GestureManager):
    """
    Prevent other gestures from hiding the icon click gesture.
    """

    def __init__(self):
        super().__init__()

    def can_be_prevented(self, gesture):
        return False

    def should_prevent(self, gesture, preventer):
        if preventer.state == sc.GestureState.BEGAN or preventer.state == sc.GestureState.CHANGED:
            return True
        return super().should_prevent(gesture, preventer)


class IconManipulator(sc.Manipulator):
    def __init__(self, icon_scale: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self._icons = {}
        self._icons_images = {}
        self._icon_panel = None
        self._icon_scale = icon_scale

    def on_build(self):
        if not self.model:
            return
        self._icon_panel = sc.Transform(transform=sc.Matrix44.get_translation_matrix(0, 0, 0))
        self.rebuild_icons()

    def rebuild_icons(self, need_check=False):
        for prim_path in list(self._icons.keys()):
            if self._icons[prim_path]:
                self._icons[prim_path].clear()
            self._icons.pop(prim_path, None)
            self._icons_images.pop(prim_path, None)

        if not self._icon_panel:
            return

        self._icon_panel.clear()
        with self._icon_panel:
            for prim_path in self.model.get_prim_paths():
                self.build_icon_by_path(prim_path, need_check)

    def check_viewport_pos(self, position):
        """Check if the world position is within the viewport screen space."""
        viewport_api = vpUtil.get_active_viewport()
        if not viewport_api:
            return False
        if not isinstance(position, Gf.Vec3d):
            try:
                position = Gf.Vec3d(position)
            except Exception:
                return False  # Cannot convert

        world_to_ndc = viewport_api.world_to_ndc
        ndc_pos = world_to_ndc.Transform(position)

        # map_ndc_to_texture returns None for viewport if position is outside
        pos, viewport = viewport_api.map_ndc_to_texture([ndc_pos[0], ndc_pos[1]])
        return viewport is not None

    def build_icon_by_path(self, prim_path, need_check):
        """Build the UI elements for a single icon at the given path."""
        icon_pos = self.model.get_position(prim_path)
        if not icon_pos:
            return
        if need_check:
            if not self.check_viewport_pos(icon_pos):
                return

        icon_trans = sc.Transform(
            look_at=sc.Transform.LookAt.CAMERA,
            transform=sc.Matrix44.get_translation_matrix(*icon_pos),
        )
        icon_url = self.model.get_icon_url(prim_path)
        prevent_others = PreventOthers()

        self._icons[prim_path] = icon_trans
        with icon_trans:
            with sc.Transform():
                # Click gesture prevents other gestures from hiding it
                icons_image = sc.Image(
                    icon_url,
                    0.09 * self._icon_scale,
                    0.09 * self._icon_scale,
                    gesture=sc.ClickGesture(functools.partial(self._icon_clicked, prim_path), manager=prevent_others),
                )
                self._icons_images[prim_path] = icons_image

            # Optionally show prim name as label
            show_title = carb.settings.get_settings().get(SHOW_TITLE_PATH)
            if show_title:
                with sc.Transform(scale_to=sc.Space.NDC, transform=sc.Matrix44.get_translation_matrix(-0.03, -0.04, 0)):
                    name = prim_path.name
                    if len(name) > 12:
                        name = name[0:4] + "..." + name[-4:]
                    sc.Label(name)

        # Ensure the UI element respects the model's visibility state
        item = self.model.get_item(prim_path) if self.model else None
        if item is not None:
            icon_trans.visible = item.visible

    def update_icon_position(self, prim_path):
        """Update the transform of an existing icon UI element."""
        icon_pos = self.model.get_position(prim_path)
        if not icon_pos:
            return
        if prim_path in self._icons:
            self._icons[prim_path].transform = sc.Matrix44.get_translation_matrix(*icon_pos)

    def on_model_updated(self, item):
        """Callback when the model signals an item has changed."""
        if not item:
            # Model cleared or major change, rebuild everything
            self.invalidate()
            return

        prim_path = item.prim_path
        if prim_path in self._icons:
            # Item exists in UI, update or remove it
            if item.removed:
                if self._icons[prim_path]:
                    self._icons[prim_path].clear()
                self._icons.pop(prim_path, None)
                self._icons_images.pop(prim_path, None)
            else:
                # Update visibility and position
                if self._icons[prim_path]:
                    self._icons[prim_path].visible = item.visible
                self.update_icon_position(prim_path)
        elif not item.removed:
            # Item is new and not marked for removal, build it
            if not self._icon_panel:
                self.on_build()
            if self._icon_panel:
                with self._icon_panel:
                    self.build_icon_by_path(prim_path, False)

    def _icon_clicked(self, prim_path: Sdf.Path, shape: sc.AbstractShape):
        """Handle click gestures on the icon image."""

        async def delay_click():
            await omni.kit.app.get_app().next_update_async()
            # Re-fetch the handler inside async func to ensure it's still valid
            # and check it before calling
            actual_click_handler = self.model.get_on_click(prim_path)
            if actual_click_handler:
                actual_click_handler(prim_path)
            else:
                pass  # No handler registered, do nothing silently

        asyncio.ensure_future(delay_click())
