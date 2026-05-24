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

import carb
import numpy as np
from omni.replicator.core import AnnotatorRegistry, BackendDispatch, Writer
from PIL import Image, ImageDraw

__version__ = "0.1.0"


class DataVisualizationWriter(Writer):
    """Data Visualization Writer

    This writer can be used to visualize various annotator data.

    Supported annotators:
    - bounding_box_2d_tight
    - bounding_box_2d_loose
    - bounding_box_3d

    Supported backgrounds:
    - rgb
    - normals

    Args:
        output_dir (str):
            Output directory for the data visualization files forwarded to the backend writer.
        bounding_box_2d_tight (bool, optional):
            If True, 2D tight bounding boxes will be drawn on the selected background (transparent by default).
            Defaults to False.
        bounding_box_2d_tight_params (dict, optional):
            Parameters for the 2D tight bounding box annotator. Defaults to None.
        bounding_box_2d_loose (bool, optional):
            If True, 2D loose bounding boxes will be drawn on the selected background (transparent by default).
            Defaults to False.
        bounding_box_2d_loose_params (dict, optional):
            Parameters for the 2D loose bounding box annotator. Defaults to None.
        bounding_box_3d (bool, optional):
            If True, 3D bounding boxes will be drawn on the selected background (transparent by default). Defaults to False.
        bounding_box_3d_params (dict, optional):
            Parameters for the 3D bounding box annotator. Defaults to None.
        frame_padding (int, optional):
            Number of digits used for the frame number in the file name. Defaults to 4.

    """

    BB_2D_TIGHT = "bounding_box_2d_tight_fast"
    BB_2D_LOOSE = "bounding_box_2d_loose_fast"
    BB_3D = "bounding_box_3d_fast"
    SUPPORTED_BACKGROUNDS = ["rgb", "normals"]

    def __init__(
        self,
        output_dir: str,
        bounding_box_2d_tight: bool = False,
        bounding_box_2d_tight_params: dict = None,
        bounding_box_2d_loose: bool = False,
        bounding_box_2d_loose_params: dict = None,
        bounding_box_3d: bool = False,
        bounding_box_3d_params: dict = None,
        frame_padding: int = 4,
    ):
        self.version = __version__
        self.data_structure = "renderProduct"
        self._output_dir = output_dir
        self.backend = BackendDispatch({"paths": {"out_dir": output_dir}})

        self._frame_id = 0
        self._frame_padding = frame_padding

        self.annotators = []
        self._annotator_params = {}
        valid_backgrounds = set()

        # Add the enabled annotators to the writer, store its parameters, and verify if a valid background type is given
        if bounding_box_2d_tight:
            self.annotators.append(AnnotatorRegistry.get_annotator(self.BB_2D_TIGHT))
            if bounding_box_2d_tight_params is not None:
                self._annotator_params[self.BB_2D_TIGHT] = bounding_box_2d_tight_params
                if (background := bounding_box_2d_tight_params.get("background")) and self._is_valid_background(
                    background
                ):
                    valid_backgrounds.add(background)
            else:
                self._annotator_params[self.BB_2D_TIGHT] = {}

        if bounding_box_2d_loose:
            self.annotators.append(AnnotatorRegistry.get_annotator(self.BB_2D_LOOSE))
            if bounding_box_2d_loose_params is not None:
                self._annotator_params[self.BB_2D_LOOSE] = bounding_box_2d_loose_params
                if (background := bounding_box_2d_loose_params.get("background")) and self._is_valid_background(
                    background
                ):
                    valid_backgrounds.add(background)
            else:
                self._annotator_params[self.BB_2D_LOOSE] = {}

        if bounding_box_3d:
            self.annotators.append(AnnotatorRegistry.get_annotator(self.BB_3D))
            # The 'camera params' annotator contains the camera data needed for the 3D bounding box screen projection
            self.annotators.append(AnnotatorRegistry.get_annotator("camera_params"))
            if bounding_box_3d_params is not None:
                self._annotator_params[self.BB_3D] = bounding_box_3d_params
                if (background := bounding_box_3d_params.get("background")) and self._is_valid_background(background):
                    valid_backgrounds.add(background)
            else:
                self._annotator_params[self.BB_3D] = {}

        # Add the valid background annotators to the writer
        for background in valid_backgrounds:
            self.annotators.append(AnnotatorRegistry.get_annotator(background))

    def write(self, data: dict):
        # Iterate over the render products
        for rp_name, annotators_data in data["renderProducts"].items():

            # Iterate over the selected annotators and their parameters
            for annot_name, annot_params in self._annotator_params.items():

                # Get the background image for the selected annotator
                background_type = annot_params.get("background", None)
                background_res = tuple(annotators_data["resolution"])
                background_img = self._get_background_image(annotators_data, background_type, background_res)

                # Draw the overlay type on the background image
                if annot_data := annotators_data.get(annot_name, None):
                    draw = ImageDraw.Draw(background_img)
                    if annot_name == self.BB_2D_TIGHT or annot_name == self.BB_2D_LOOSE:
                        self._draw_2d_bounding_boxes(draw, annot_data, annot_params)

                    if annot_name == self.BB_3D:
                        camera_params = annotators_data.get("camera_params", None)
                        self._draw_3d_bounding_boxes(draw, annot_data, camera_params, annot_params)

                    file_path = f"{rp_name}/{annot_name}_{self._frame_id:0{self._frame_padding}}.png"
                    self.backend.write_image(file_path, np.asarray(background_img))

        self._frame_id += 1

    def _get_background_image(self, annotators_data: dict, background_type: str, resolution: tuple) -> Image:
        # Check if the background type is available in the annotators data and if needed convert it to image format
        if background_annot_data := annotators_data.get(background_type):
            background_data = background_annot_data["data"]

            if background_type == "rgb":
                return Image.fromarray(background_data)

            if background_type == "normals":
                colored_data = ((background_data * 0.5 + 0.5) * 255).astype(np.uint8)
                return Image.fromarray(colored_data)

        # If no background is chosen use a transparent image as default
        return Image.new("RGBA", resolution, (0, 0, 0, 0))

    def _draw_2d_bounding_boxes(self, draw: ImageDraw, annot_data: dict, write_params: dict):
        # Get the 2d bboxes from the annotator
        bboxes_data = annot_data["data"]

        # Get the recangle draw parameters
        fill_color = None if "fill" not in write_params else write_params["fill"]
        rectangle_color = "green" if "outline" not in write_params else write_params["outline"]
        rectangle_width = 1 if "width" not in write_params else write_params["width"]

        # Iterate the bounding boxes and draw the rectangles
        for bbox in bboxes_data:
            # ('semanticId', '<u4'), ('x_min', '<i4'), ('y_min', '<i4'), ('x_max', '<i4'), ('y_max', '<i4'), ('occlusionRatio', '<f4')
            x_min, y_min, x_max, y_max = bbox[1], bbox[2], bbox[3], bbox[4]
            draw.rectangle(
                [x_min, y_min, x_max, y_max], fill=fill_color, outline=rectangle_color, width=rectangle_width
            )

    def _draw_3d_bounding_boxes(self, draw: ImageDraw, annot_data: dict, camera_params: dict, write_params: dict):
        # Get the 3d bboxes from the annotator
        bboxes_data = annot_data["data"]

        # Transpose is needed for the row-column-major conversion
        cam_view_transform = camera_params["cameraViewTransform"].reshape((4, 4))
        cam_view_transform = cam_view_transform.T
        cam_projection_transform = camera_params["cameraProjection"].reshape((4, 4))
        cam_projection_transform = cam_projection_transform.T

        # The resolution is used to map the Normalized Device Coordinates (NDC) to screen space
        screen_width, screen_height = camera_params["renderProductResolution"]

        # Get the line draw parameters
        line_color = "green" if "fill" not in write_params else write_params["fill"]
        line_width = 1 if "width" not in write_params else write_params["width"]

        # Iterate the bounding boxes and draw the edges
        for bbox in bboxes_data:
            # ('semanticId', '<u4'), ('x_min', '<f4'), ('y_min', '<f4'), ('z_min', '<f4'), ('x_max', '<f4'), ('y_max', '<f4'), ('z_max', '<f4'), ('transform', '<f4', (4, 4)), ('occlusionRatio', '<f4')
            # Bounding box points in local coordinate system
            x_min, y_min, z_min, x_max, y_max, z_max = (bbox[1], bbox[2], bbox[3], bbox[4], bbox[5], bbox[6])

            # Transformation matrix from local to world coordinate system
            local_to_world_transform = bbox[7]
            local_to_world_transform = local_to_world_transform.T

            # Calculate all 8 vertices of the bounding box in local space
            vertices_local = [
                np.array([x_min, y_min, z_min, 1]),
                np.array([x_min, y_min, z_max, 1]),
                np.array([x_min, y_max, z_min, 1]),
                np.array([x_min, y_max, z_max, 1]),
                np.array([x_max, y_min, z_min, 1]),
                np.array([x_max, y_min, z_max, 1]),
                np.array([x_max, y_max, z_min, 1]),
                np.array([x_max, y_max, z_max, 1]),
            ]

            # Transform vertices to world, camera, and screen space
            vertices_screen = []
            for vertex in vertices_local:
                # Transform to world space
                world_homogeneous = np.dot(local_to_world_transform, vertex)
                # Transform to camera space
                camera_homogeneous = np.dot(cam_view_transform, world_homogeneous)
                # Projection transformation
                clip_space = np.dot(cam_projection_transform, camera_homogeneous)
                # Normalize Device Coordinates (NDC)
                ndc = clip_space[:3] / clip_space[3]
                # Map NDC to screen space
                screen_point = ((ndc[0] + 1) * screen_width / 2, (1 - ndc[1]) * screen_height / 2)
                vertices_screen.append(screen_point)

            # Draw the bounding box edges
            draw.line([vertices_screen[0], vertices_screen[1]], fill=line_color, width=line_width)
            draw.line([vertices_screen[0], vertices_screen[2]], fill=line_color, width=line_width)
            draw.line([vertices_screen[0], vertices_screen[4]], fill=line_color, width=line_width)
            draw.line([vertices_screen[1], vertices_screen[3]], fill=line_color, width=line_width)
            draw.line([vertices_screen[1], vertices_screen[5]], fill=line_color, width=line_width)
            draw.line([vertices_screen[2], vertices_screen[3]], fill=line_color, width=line_width)
            draw.line([vertices_screen[2], vertices_screen[6]], fill=line_color, width=line_width)
            draw.line([vertices_screen[3], vertices_screen[7]], fill=line_color, width=line_width)
            draw.line([vertices_screen[4], vertices_screen[5]], fill=line_color, width=line_width)
            draw.line([vertices_screen[4], vertices_screen[6]], fill=line_color, width=line_width)
            draw.line([vertices_screen[5], vertices_screen[7]], fill=line_color, width=line_width)
            draw.line([vertices_screen[6], vertices_screen[7]], fill=line_color, width=line_width)

    def _is_valid_background(self, background: str) -> bool:
        if background in self.SUPPORTED_BACKGROUNDS:
            return True
        else:
            carb.log_warn(
                f"Background '{background}' is not supported, please choose from the supported types: {self.SUPPORTED_BACKGROUNDS}, default transparent image will be used instead.."
            )
            return False

    def detach(self):
        self._frame_id = 0
        return super().detach()
