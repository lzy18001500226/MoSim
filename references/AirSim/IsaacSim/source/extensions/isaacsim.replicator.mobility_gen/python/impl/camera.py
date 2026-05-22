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


import os
from typing import Tuple

import omni.replicator.core as rep
from isaacsim.core.utils.prims import get_prim_at_path
from isaacsim.core.utils.stage import open_stage

from .common import Buffer, Module
from .utils.prim_utils import prim_get_world_transform


class MobilityGenCamera(Module):

    def __init__(self, prim_path: str, resolution: Tuple[int, int]):

        self._prim_path = prim_path
        self._resolution = resolution
        self._render_product = None
        self._rgb_annotator = None
        self._segmentation_annotator = None
        self._instance_id_segmentation_annotator = None
        self._normals_annotator = None
        self._depth_annotator = None
        self._prim = get_prim_at_path(self._prim_path)

        self.rgb_image = Buffer(tags=["rgb"])
        self.segmentation_image = Buffer(tags=["segmentation"])
        self.segmentation_info = Buffer()
        self.depth_image = Buffer(tags=["depth"])
        self.instance_id_segmentation_image = Buffer(tags=["segmentation"])
        self.instance_id_segmentation_info = Buffer()
        self.normals_image = Buffer(tags=["normals"])
        self.position = Buffer()
        self.orientation = Buffer()

    def enable_rendering(self):

        self._render_product = rep.create.render_product(self._prim_path, self._resolution, force_new=False)

    def disable_rendering(self):
        if self._render_product is None:
            return

        if self._rgb_annotator is not None:
            self._rgb_annotator.detach()
            self._rgb_annotator = None

        if self._segmentation_annotator is not None:
            self._segmentation_annotator.detach()
            self._segmentation_annotator = None

        if self._depth_annotator is not None:
            self._depth_annotator.detach()
            self._depth_annotator = None

        self._render_product.destroy()
        self._render_product = None

    def enable_rgb_rendering(self):
        if self._render_product is None:
            self.enable_rendering()
        if self._rgb_annotator is not None:
            return
        self._rgb_annotator = rep.AnnotatorRegistry.get_annotator("LdrColor")
        self._rgb_annotator.attach(self._render_product)

    def enable_segmentation_rendering(self):
        if self._render_product is None:
            self.enable_rendering()
        if self._segmentation_annotator is not None:
            return
        self._segmentation_annotator = rep.AnnotatorRegistry.get_annotator(
            "semantic_segmentation", init_params=dict(colorize=False)
        )
        self._segmentation_annotator.attach(self._render_product)

    def enable_instance_id_segmentation_rendering(self):
        if self._render_product is None:
            self.enable_rendering()
        if self._instance_id_segmentation_annotator is not None:
            return
        self._instance_id_segmentation_annotator = rep.AnnotatorRegistry.get_annotator(
            "instance_id_segmentation", init_params=dict(colorize=False)
        )
        self._instance_id_segmentation_annotator.attach(self._render_product)

    def enable_depth_rendering(self):
        if self._render_product is None:
            self.enable_rendering()
        if self._depth_annotator is not None:
            return
        self._depth_annotator = rep.AnnotatorRegistry.get_annotator("distance_to_camera")
        self._depth_annotator.attach(self._render_product)

    def enable_normals_rendering(self):
        if self._render_product is None:
            self.enable_rendering()
        if self._normals_annotator is not None:
            return
        self._normals_annotator = rep.AnnotatorRegistry.get_annotator("normals")
        self._normals_annotator.attach(self._render_product)

    def update_state(self):
        if self._rgb_annotator is not None:
            self.rgb_image.set_value(self._rgb_annotator.get_data()[:, :, :3])
        if self._segmentation_annotator is not None:
            data = self._segmentation_annotator.get_data()
            seg_image = data["data"]
            seg_info = data["info"]
            self.segmentation_image.set_value(seg_image)
            self.segmentation_info.set_value(seg_info)

        if self._depth_annotator is not None:
            self.depth_image.set_value(self._depth_annotator.get_data())

        if self._instance_id_segmentation_annotator is not None:
            data = self._instance_id_segmentation_annotator.get_data()
            id_seg_image = data["data"]
            id_seg_info = data["info"]
            self.instance_id_segmentation_image.set_value(id_seg_image)
            self.instance_id_segmentation_info.set_value(id_seg_info)

        if self._normals_annotator is not None:
            data = self._normals_annotator.get_data()
            self.normals_image.set_value(data)

        position, orientation = prim_get_world_transform(self._prim)
        self.position.set_value(position)
        self.orientation.set_value(orientation)

        super().update_state()
