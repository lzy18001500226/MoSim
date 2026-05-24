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

from __future__ import annotations

from abc import ABC, abstractmethod

import isaacsim.core.experimental.utils.stage as stage_utils
import numpy as np
import warp as wp
from isaacsim.core.experimental.prims import XformPrim
from pxr import Usd, UsdGeom


class Shape(XformPrim, ABC):
    """Base class for creating/wrapping USD Geom shape prims.

    .. note::

        This class creates or wraps (one of both) USD Cube prims according to the following rules:

        * If the prim paths exist, a wrapper is placed over the USD Cube prims.
        * If the prim paths do not exist, USD Cube prims are created at each path and a wrapper is placed over them.

    Args:
        paths: Single path or list of paths to existing or non-existing (one of both) USD prims.
            Can include regular expressions for matching multiple prims.
        resolve_paths: Whether to resolve the given paths (true) or use them as is (false).
        positions: Positions in the world frame (shape ``(N, 3)``).
            If the input shape is smaller than expected, data will be broadcasted (following NumPy broadcast rules).
        translations: Translations in the local frame (shape ``(N, 3)``).
            If the input shape is smaller than expected, data will be broadcasted (following NumPy broadcast rules).
        orientations: Orientations in the world frame (shape ``(N, 4)``, quaternion ``wxyz``).
            If the input shape is smaller than expected, data will be broadcasted (following NumPy broadcast rules).
        scales: Scales to be applied to the prims (shape ``(N, 3)``).
            If the input shape is smaller than expected, data will be broadcasted (following NumPy broadcast rules).
        reset_xform_op_properties: Whether to reset the transformation operation attributes of the prims to a standard set.
            See :py:meth:`reset_xform_op_properties` for more details.

    Raises:
        ValueError: If resulting paths are mixed (existing and non-existing prims) or invalid.
    """

    def __init__(
        self,
        paths: str | list[str],
        *,
        # Prim
        resolve_paths: bool = True,
        # XformPrim
        positions: list | np.ndarray | wp.array | None = None,
        translations: list | np.ndarray | wp.array | None = None,
        orientations: list | np.ndarray | wp.array | None = None,
        scales: list | np.ndarray | wp.array | None = None,
        reset_xform_op_properties: bool = False,
    ) -> None:
        super().__init__(
            paths,
            resolve_paths=resolve_paths,
            positions=positions,
            translations=translations,
            orientations=orientations,
            scales=scales,
            reset_xform_op_properties=reset_xform_op_properties,
        )
        if not hasattr(self, "_geoms"):
            self._geoms = []

    """
    Properties.
    """

    @property
    def geoms(self) -> list[UsdGeom.Gprim]:
        """USD geometric primitives encapsulated by the wrapper.

        Returns:
            List of USD geometric primitives.

        Example:

        .. code-block:: python

            >>> prims.geoms  # doctest: +NO_CHECK
            [UsdGeom.Gprim(Usd.Prim(</World/prim_0>)),
             UsdGeom.Gprim(Usd.Prim(</World/prim_1>)),
             UsdGeom.Gprim(Usd.Prim(</World/prim_2>))]
        """
        return self._geoms

    """
    Static methods.
    """

    @staticmethod
    @abstractmethod
    def update_extents(geoms: list[UsdGeom.Gprim]) -> None:
        """Update the gprims' extents.

        Args:
            geoms: Geoms to process.
        """
        pass

    @staticmethod
    @abstractmethod
    def are_of_type(paths: str | Usd.Prim | list[str | Usd.Prim]) -> wp.array:
        """Check if the prims at the given paths are valid for creating Shape instances of this type.

        Args:
            paths: Prim paths (or prims) to check for.

        Returns:
            Boolean flags indicating if the prims are valid for creating Shape instances.
        """
        pass

    @staticmethod
    def fetch_instances(paths: str | Usd.Prim | list[str | Usd.Prim]) -> list[Shape | None]:
        """Fetch instances of Shape from prims (or prim paths) at the given paths.

        Backends: :guilabel:`usd`.

        Args:
            paths: Prim paths (or prims) to get Shape instances from.

        Returns:
            List of Shape instances or ``None`` if the prim is not a supported Shape type.

        Example:

        .. code-block:: python

            >>> import isaacsim.core.experimental.utils.stage as stage_utils
            >>> from isaacsim.core.experimental.objects import Shape
            >>>
            >>> # given a USD stage with the prims at paths /World, /World/A (Cube), /World/B (Sphere)
            >>> stage_utils.define_prim(f"/World/A", "Cube")  # doctest: +NO_CHECK
            >>> stage_utils.define_prim(f"/World/B", "Sphere")  # doctest: +NO_CHECK
            >>>
            >>> # fetch shape instances
            >>> Shape.fetch_instances(["/World", "/World/A", "/World/B"])
            [None,
             <isaacsim.core.experimental.objects.impl.shapes.cube.Cube object at 0x...>,
             <isaacsim.core.experimental.objects.impl.shapes.sphere.Sphere object at 0x...>]
        """
        # defer imports to avoid circular dependencies
        from .capsule import Capsule
        from .cone import Cone
        from .cube import Cube
        from .cylinder import Cylinder
        from .plane import Plane
        from .sphere import Sphere

        classes = [Capsule, Cone, Cube, Cylinder, Plane, Sphere]

        instances = []
        stage = stage_utils.get_current_stage(backend="usd")
        for item in paths if isinstance(paths, (list, tuple)) else [paths]:
            prim = stage.GetPrimAtPath(item) if isinstance(item, str) else item
            instance = None
            for cls in classes:
                if cls.are_of_type(prim).numpy().item():
                    instance = cls(prim.GetPath().pathString)
                    break
            instances.append(instance)
        return instances
