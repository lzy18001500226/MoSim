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
from typing import Any

import numpy as np


async def capture_annotator_data_async(
    annotator_name: str,
    camera_position: tuple[float, float, float] = (5, 5, 5),
    camera_look_at: tuple[float, float, float] = (0, 0, 0),
    resolution: tuple[int, int] = (1280, 720),
    camera_prim_path: str | None = None,
    render_product: Any = None,
    do_array_copy: bool = True,
) -> Any:
    """Capture annotator data from a virtual camera in the simulation.

    Args:
        annotator_name: Name of the annotator to capture data from.
            See https://docs.omniverse.nvidia.com/py/replicator/1.11.35/source/extensions/omni.replicator.core/docs/API.html#default-annotators for available annotators.
        camera_position: 3D position coordinates for the camera placement (x, y, z).
            Ignored if render_product is provided.
        camera_look_at: 3D coordinates of the target point the camera should look at.
            Ignored if render_product is provided.
        resolution: Tuple specifying the image resolution (width, height).
            Ignored if render_product is provided.
        camera_prim_path: USD path to an existing camera prim to use for capture.
            If provided, camera_position and camera_look_at are ignored.
            Ignored if render_product is provided.
        render_product: Existing render product to use for capture.
            If provided, all other parameters are ignored and this render product
            will be used directly without being destroyed afterwards.
        do_array_copy: Whether to copy the array data when retrieving from the annotator.
            Set to False for better performance if you don't need to modify the data.

    Returns:
        Annotator data. The exact type depends on the annotator:
            - For image-based annotators (rgb, depth, normals, etc.): numpy array
            - For non-array annotators (camera_params, etc.): dict
            - Mixed annotators may return dict with 'data' key containing array

    Example:

    .. code-block:: python

        >>> from isaacsim.test.utils.image_capture import capture_annotator_data_async
        >>>
        >>> # Capture RGB data with temporary camera
        >>> rgb_data = await capture_annotator_data_async(
        ...     "rgb",
        ...     camera_position=(10, 10, 10),
        ...     camera_look_at=(0, 0, 0),
        ...     resolution=(512, 512)
        ... )
        >>> rgb_data.shape
        (512, 512, 4)
        >>>
        >>> # Capture distance to camera data using existing camera
        >>> distance_data = await capture_annotator_data_async(
        ...     "distance_to_camera",
        ...     resolution=(512, 512),
        ...     camera_prim_path="/World/Camera"
        ... )
        >>> distance_data.shape
        (512, 512, 1)
        >>>
        >>> # Capture using existing render product
        >>> import omni.replicator.core as rep
        >>> existing_rp = rep.create.render_product("/World/Camera", (1920, 1080))
        >>> rgb_data = await capture_annotator_data_async(
        ...     "rgb",
        ...     render_product=existing_rp
        ... )
        >>> rgb_data.shape
        (1080, 1920, 4)
    """
    import omni.replicator.core as rep

    temp_cam = None
    temp_render_product = None

    if render_product is None:
        # Create temporary camera if needed
        camera_path = camera_prim_path
        if camera_path is None:
            # Create new camera
            temp_cam = rep.functional.create.camera(position=camera_position, look_at=camera_look_at)
            camera_path = temp_cam.GetPath()

        # Create temporary render product using either existing or temporary camera
        temp_render_product = rep.create.render_product(camera_path, resolution)
        render_product = temp_render_product

    annot = rep.AnnotatorRegistry.get_annotator(annotator_name)
    annot.attach(render_product)
    await rep.orchestrator.step_async()
    annot_data = annot.get_data(do_array_copy=do_array_copy)
    annot.detach()

    # Only destroy if we created a temporary render product
    if temp_render_product is not None:
        temp_render_product.destroy()

    # Cleanup temporary camera
    if temp_cam is not None:
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        stage.RemovePrim(camera_path)

    return annot_data


async def capture_rgb_data_async(
    camera_position: tuple[float, float, float] = (5, 5, 5),
    camera_look_at: tuple[float, float, float] = (0, 0, 0),
    resolution: tuple[int, int] = (1280, 720),
    camera_prim_path: str | None = None,
    render_product: Any = None,
) -> np.ndarray:
    """Capture an RGB image from a virtual camera in the simulation.

    Args:
        camera_position: 3D position coordinates for the camera placement (x, y, z).
            Ignored if render_product is provided.
        camera_look_at: 3D coordinates of the target point the camera should look at.
            Ignored if render_product is provided.
        resolution: Tuple specifying the image resolution (width, height).
            Ignored if render_product is provided.
        camera_prim_path: USD path to an existing camera prim to use for capture.
            If provided, camera_position and camera_look_at are ignored.
            Ignored if render_product is provided.
        render_product: Existing render product to use for capture.
            If provided, all other parameters are ignored.

    Returns:
        RGB image data as a numpy array with shape (height, width, 4) and dtype uint8.

    Example:

    .. code-block:: python

        >>> from isaacsim.test.utils.image_capture import capture_rgb_data_async
        >>>
        >>> # Using temporary camera creation
        >>> rgb_data = await capture_rgb_data_async(
        ...     camera_position=(10, 10, 10),
        ...     camera_look_at=(0, 0, 0),
        ...     resolution=(512, 512)
        ... )
        >>> rgb_data.shape
        (512, 512, 4)
        >>>
        >>> # Using existing camera prim
        >>> rgb_data = await capture_rgb_data_async(
        ...     resolution=(512, 512),
        ...     camera_prim_path="/World/Camera"
        ... )
        >>> rgb_data.shape
        (512, 512, 4)
        >>>
        >>> # Using existing render product
        >>> import omni.replicator.core as rep
        >>> existing_rp = rep.create.render_product("/World/Camera", (1920, 1080))
        >>> rgb_data = await capture_rgb_data_async(render_product=existing_rp)
        >>> rgb_data.shape
        (1080, 1920, 4)
    """
    return await capture_annotator_data_async(
        "rgb", camera_position, camera_look_at, resolution, camera_prim_path, render_product
    )


async def capture_depth_data_async(
    depth_type: str = "distance_to_camera",
    camera_position: tuple[float, float, float] = (5, 5, 5),
    camera_look_at: tuple[float, float, float] = (0, 0, 0),
    resolution: tuple[int, int] = (1280, 720),
    camera_prim_path: str | None = None,
    render_product: Any = None,
) -> np.ndarray:
    """Capture depth data from a virtual camera in the simulation.

    Args:
        depth_type: Type of depth measurement to capture. Must be either "distance_to_camera" or "distance_to_image_plane".
            - "distance_to_camera": Euclidean distance from each point to the camera origin (radial distance).
              This gives the actual 3D distance from the camera center to each point in the scene.
            - "distance_to_image_plane": Perpendicular distance from each point to the camera's image plane (Z-depth).
              This is the traditional depth buffer value used in computer graphics.
        camera_position: 3D position coordinates for the camera placement (x, y, z).
            Ignored if render_product is provided.
        camera_look_at: 3D coordinates of the target point the camera should look at.
            Ignored if render_product is provided.
        resolution: Tuple specifying the image resolution (width, height).
            Ignored if render_product is provided.
        camera_prim_path: USD path to an existing camera prim to use for capture.
            If provided, camera_position and camera_look_at are ignored.
            Ignored if render_product is provided.
        render_product: Existing render product to use for capture.
            If provided, all other parameters except depth_type are ignored.

    Returns:
        Depth data as a numpy array with shape (height, width) and dtype float32.

    Raises:
        ValueError: If depth_type is not "distance_to_camera" or "distance_to_image_plane".

    Example:

    .. code-block:: python

        >>> from isaacsim.test.utils.image_capture import capture_depth_data_async
        >>>
        >>> # Capture radial distance (distance to camera origin)
        >>> radial_depth = await capture_depth_data_async(
        ...     depth_type="distance_to_camera",
        ...     camera_position=(10, 10, 10),
        ...     camera_look_at=(0, 0, 0),
        ...     resolution=(512, 512)
        ... )
        >>> radial_depth.shape
        (512, 512, 1)
        >>>
        >>> # Capture Z-depth (distance to image plane)
        >>> z_depth = await capture_depth_data_async(
        ...     depth_type="distance_to_image_plane",
        ...     resolution=(512, 512),
        ...     camera_prim_path="/World/Camera"
        ... )
        >>> z_depth.shape
        (512, 512, 1)
        >>>
        >>> # Using existing render product
        >>> import omni.replicator.core as rep
        >>> existing_rp = rep.create.render_product("/World/Camera", (1920, 1080))
        >>> depth_data = await capture_depth_data_async(
        ...     depth_type="distance_to_camera",
        ...     render_product=existing_rp
        ... )
        >>> depth_data.shape
        (1080, 1920, 1)
    """
    valid_depth_types = ["distance_to_camera", "distance_to_image_plane"]
    if depth_type not in valid_depth_types:
        raise ValueError(
            f"Invalid depth_type '{depth_type}'. Must be one of {valid_depth_types}. "
            f"'distance_to_camera' provides radial distance from camera origin, "
            f"'distance_to_image_plane' provides perpendicular distance to camera plane (Z-depth)."
        )

    return await capture_annotator_data_async(
        depth_type, camera_position, camera_look_at, resolution, camera_prim_path, render_product
    )


async def capture_viewport_annotator_data_async(viewport_api, annotator_name="rgb") -> Any:
    """Capture annotator data from an existing viewport's render product.

    This function attaches a replicator annotator to an existing viewport's render product,
    steps the orchestrator to generate the data, and returns the captured annotator output.
    Unlike capture_annotator_data_async which creates temporary cameras, this function works
    with existing viewports in the scene.

    Args:
        viewport_api: Viewport API object that provides access to the viewport's render product.
            Must have a valid render_product_path attribute.
        annotator_name: Name of the annotator to capture data from.
            See https://docs.omniverse.nvidia.com/py/replicator/1.11.35/source/extensions/omni.replicator.core/docs/API.html#default-annotators for available annotators.
            Common options include "rgb", "depth", "normals", "semantic_segmentation", etc.

    Returns:
        Annotator data with type depending on the specific annotator used.
        For image-based annotators (rgb, depth, normals, etc.): numpy array.
        For metadata annotators (camera_params, etc.): dict.
        Mixed annotators may return dict with 'data' key containing array.

    Raises:
        ValueError: If render_product_path is None or empty.

    Example:

    .. code-block:: python

        >>> from isaacsim.test.utils.image_capture import capture_viewport_annotator_data_async
        >>> import omni.kit.viewport.utility as viewport_utils
        >>>
        >>> # Get the default viewport
        >>> viewport_api = viewport_utils.get_active_viewport()
        >>>
        >>> # Capture RGB data from the viewport
        >>> rgb_data = await capture_viewport_annotator_data_async(
        ...     viewport_api,
        ...     annotator_name="rgb"
        ... )
        >>> rgb_data.shape
        (720, 1280, 4)
        >>>
        >>> # Capture depth data from the viewport
        >>> depth_data = await capture_viewport_annotator_data_async(
        ...     viewport_api,
        ...     annotator_name="distance_to_camera"
        ... )
        >>> depth_data.shape
        (720, 1280, 1)
    """
    render_product_path = viewport_api.render_product_path
    if not render_product_path:
        raise ValueError("viewport_api.render_product_path is None or empty")

    # Use the existing capture_annotator_data_async with the viewport's render product
    return await capture_annotator_data_async(annotator_name, render_product=render_product_path)
