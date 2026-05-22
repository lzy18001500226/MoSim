# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
"""Extension to export USD to URDF."""

# Standard Library
import os
import pathlib
import re
from dataclasses import dataclass
from typing import Optional

# Third Party
import numpy as np

# NVIDIA
import omni
import omni.ui as ui
from isaacsim.core.utils.stage import open_stage
from isaacsim.gui.components.element_wrappers import Button, CheckBox, CollapsableFrame, DropDown, StringField
from isaacsim.gui.components.ui_utils import get_style
from omni.physx import get_physx_property_query_interface
from omni.physx.bindings._physx import PhysxPropertyQueryMode, PhysxPropertyQueryResult
from omni.usd import StageEventType
from pxr import Gf, PhysicsSchemaTools, Sdf, Usd, UsdPhysics, UsdUtils

if os.name == "nt":
    file_dir = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
    exporter_urdf_dir = file_dir.joinpath(pathlib.Path("../../../../pip_prebundle")).resolve()
    os.add_dll_directory(exporter_urdf_dir.__str__())

import nvidia.srl.tools.logger as logger
import nvidia.srl.usd.prim_helper as prim_helper
from nvidia.srl.from_usd.to_urdf import UsdToUrdf
from nvidia.srl.math.transform import Rotation

from .style import get_option_style


class UrdfExporter:
    def __init__(self):
        self.log_level = logger.level_from_name("ERROR")
        # Initialize parameters as direct attributes
        self._mesh_dir = "meshes"
        self._mesh_path_prefix = "file://"
        self._root = None
        self._visualize_collision_meshes = False

    def cleanup(self):
        self._mesh_dir = None
        self._mesh_path_prefix = ""
        self._root = None
        self._visualize_collision_meshes = False

    def _on_value_changed(self, param_name: str, new_value):
        """Generic handler for value changes in UI elements.

        Args:
            param_name: The name of the instance attribute to update (without leading underscore)
            new_value: The new value to store
        """
        setattr(self, f"_{param_name}", new_value)

    def build_exporter_options(self):
        with ui.VStack(style=get_option_style(), spacing=5, height=0):
            mesh_field = StringField(
                "Mesh Folder Name",
                default_value="meshes",
                tooltip="Folder name for mesh files. Defaults to 'meshes'.",
                use_folder_picker=False,
                on_value_changed_fn=lambda v: self._on_value_changed("mesh_dir", v),
            )

            mesh_path_prefix_options = ["file://", "package://", "./"]
            self._mesh_path_prefix = "file://"
            self._package_name = ""

            def on_mesh_path_prefix_changed(new_value):
                self._on_value_changed("mesh_path_prefix", new_value)
                self._mesh_path_prefix = new_value
                self._package_name_frame.visible = new_value == "package://"
                # ui.refresh()

            # Replaced ComboBoxField with DropDown
            def populate_mesh_prefix_options():
                return mesh_path_prefix_options

            dropdown = DropDown(
                label="Mesh Path Prefix",
                tooltip="Prefix to add to URDF mesh filename values.",
                populate_fn=populate_mesh_prefix_options,
                on_selection_fn=on_mesh_path_prefix_changed,
                keep_old_selections=False,
                add_flourish=True,
            )

            self._package_name_frame = ui.Frame()
            with self._package_name_frame:
                with ui.HStack():
                    ui.Spacer(width=20)
                    package_name_field = StringField(
                        "Package Name",
                        default_value="",
                        tooltip="Name of the ROS package for 'package://' mesh paths.",
                        on_value_changed_fn=lambda v: setattr(self, "_package_name", v),
                    )
            # Initialize items and trigger default selection callback
            dropdown.repopulate()

            root_path_field = StringField(
                "Root Prim Path",
                default_value="",
                tooltip="Root prim path of the robot to be exported. Defaults to the default prim.",
                on_value_changed_fn=lambda v: self._on_value_changed("root", v),
            )
            ## TODO: should open a stage picker?

            stage_visualize_collisions_check_box = CheckBox(
                "Visualize Collisions",
                default_value=False,
                tooltip="Visualization collider meshes even if their visibility is disabled.",
                on_click_fn=lambda v: self._on_value_changed("visualize_collision_meshes", v),
            )

    def _on_export_button_clicked_fn(self, export_dir: str, export_filename: str):
        sanitized_export_dir = os.path.normpath(export_dir)
        self._mesh_dir = os.path.join(sanitized_export_dir, os.path.basename(self._mesh_dir))

        # check if all the necessary fields have been filled out
        if not self._root:
            stage = omni.usd.get_context().get_stage()
            self._root = stage.GetDefaultPrim().GetPath().pathString
            print("Root prim not specified. Using the Default Prim on Stage. ", self._root)

        export_path = os.path.join(export_dir, f"{export_filename}.urdf")

        usd_to_urdf_kwargs = {
            "node_names_to_remove": None,
            "edge_names_to_remove": None,
            "root": self._root,
            "parent_link_is_body_1": None,
            "log_level": self.log_level,
        }

        stage = omni.usd.get_context().get_stage()

        # Create a new USD layer to store inertia data
        inertia_temp_layer = Sdf.Layer.CreateAnonymous("inertia_temp.usda")

        # Set the new layer as the edit target
        root_layer = stage.GetRootLayer()
        root_layer.subLayerPaths.append(inertia_temp_layer.identifier)
        stage.SetEditTarget(Usd.EditTarget(inertia_temp_layer))

        # Set the inertia values for the prims in the new layer
        inertia_prims = prim_helper.get_prims(stage, has_apis=[UsdPhysics.MassAPI, UsdPhysics.RigidBodyAPI])

        for prim in inertia_prims:
            inertia_data = InertiaData.init_from_prim(prim)
            mass_api = UsdPhysics.MassAPI(prim)

            # Set the mass
            mass_api.GetMassAttr().Set(inertia_data.mass)

            # Set the center of mass
            x = float(inertia_data.ref_point[0])
            y = float(inertia_data.ref_point[1])
            z = float(inertia_data.ref_point[2])
            mass_api.GetCenterOfMassAttr().Set(Gf.Vec3f(x, y, z))

            # Set the inertia diagonal
            x = float(inertia_data.inertia_diag[0])
            y = float(inertia_data.inertia_diag[1])
            z = float(inertia_data.inertia_diag[2])
            mass_api.GetDiagonalInertiaAttr().Set(Gf.Vec3f(x, y, z))

            # Set the principal axes
            quat = inertia_data.prin_axes.as_quat()
            w = float(quat[3])
            x = float(quat[0])
            y = float(quat[1])
            z = float(quat[2])
            mass_api.GetPrincipalAxesAttr().Set(Gf.Quatf(w, (x, y, z)))

        # Create the UsdToUrdf object with the inertia data in the stage
        usd_to_urdf = UsdToUrdf(stage, **usd_to_urdf_kwargs)

        mesh_prefix = self._mesh_path_prefix

        if self._mesh_path_prefix == "package://":
            if self._package_name == "":
                self._package_name = os.path.splitext(os.path.basename(export_path))[0]
            # Sanitize package name: lowercase, alphanumeric and underscores, no consecutive underscores, at least 2 chars

            sanitized_name = re.sub(r"[^a-z0-9_]", "_", self._package_name.lower())
            sanitized_name = re.sub(r"_+", "_", sanitized_name)
            sanitized_name = sanitized_name.strip("_")
            if len(sanitized_name) < 2:
                sanitized_name = sanitized_name + "_pkg"
            mesh_prefix = self._mesh_path_prefix + sanitized_name + "/"

        # Check if the mesh directory is a subdirectory of the export directory
        use_uri_file_prefix = mesh_prefix == "file://"
        if use_uri_file_prefix and self._mesh_dir and not self._mesh_dir.endswith("/"):
            self._mesh_dir = self._mesh_dir + "/"
        output_path = usd_to_urdf.save_to_file(
            urdf_output_path=export_path,
            visualize_collision_meshes=self._visualize_collision_meshes,
            mesh_dir=self._mesh_dir,
            mesh_path_prefix=mesh_prefix,
            use_uri_file_prefix=use_uri_file_prefix,
        )

        # Override the URI file prefix to be relative path if the mesh path prefix is "./"
        if mesh_prefix == "./":
            with open(export_path, "r") as f:
                urdf_content = f.read()
            urdf_content = urdf_content.replace(self._mesh_dir, "./")
            with open(export_path, "w") as f:
                f.write(urdf_content)

        # Revert the stage back to its original state by removing the new layer if it was added
        root_layer.subLayerPaths.remove(inertia_temp_layer.identifier)
        stage.SetEditTarget(stage.GetRootLayer())

        return True


@dataclass
class InertiaData:
    """Helper class to store inertia data."""

    mass: Optional[float] = None
    ref_point: Optional[np.ndarray] = None
    inertia_diag: Optional[np.ndarray] = None
    prin_axes: Optional[Rotation] = None

    @classmethod
    def get_physx_queried_inertia_data(cls, prim) -> "InertiaData":
        inertia_data = cls()

        def rigid_body_fn(rigid_info, prim_path: str):
            nonlocal inertia_data

            if rigid_info.result == PhysxPropertyQueryResult.VALID:
                inertia_data.mass = rigid_info.mass
                inertia_data.ref_point = np.array(rigid_info.center_of_mass)
                inertia_data.inertia_diag = np.array(rigid_info.inertia)

                prin_axes_quat = np.array(
                    [
                        rigid_info.principal_axes[3],
                        rigid_info.principal_axes[0],
                        rigid_info.principal_axes[1],
                        rigid_info.principal_axes[2],
                    ]
                )
                try:
                    inertia_data.prin_axes = Rotation.from_quat(prin_axes_quat)
                except ValueError:
                    inertia_data.prin_axes = None
            else:
                raise RuntimeError(f"PhysX query rigid info is not valid for the given prim: '{prim_path}'")

        stage = prim.GetStage()
        stage_cache = UsdUtils.StageCache().Get()
        stage_id = stage_cache.GetId(stage).ToLongInt()
        prim_path = str(prim.GetPath())
        prim_id = PhysicsSchemaTools.sdfPathToInt(prim_path)

        get_physx_property_query_interface().query_prim(
            stage_id=stage_id,
            prim_id=prim_id,
            query_mode=PhysxPropertyQueryMode.QUERY_RIGID_BODY_WITH_COLLIDERS,
            rigid_body_fn=lambda rigid_info: rigid_body_fn(rigid_info, prim_path=prim_path),
        )

        return inertia_data

    @classmethod
    def init_from_prim(cls, prim):
        inertia_data = cls.get_physx_queried_inertia_data(prim)

        mass_api = UsdPhysics.MassAPI(prim)

        mass_attr = mass_api.GetMassAttr()
        if mass_attr.IsValid() and mass_attr.HasValue() and mass_attr.HasAuthoredValue():
            inertia_data.mass = mass_attr.Get()

        ref_point_attr = mass_api.GetCenterOfMassAttr()
        if ref_point_attr.IsValid() and ref_point_attr.HasValue() and ref_point_attr.HasAuthoredValue():
            inertia_data.ref_point = np.array(ref_point_attr.Get())

        inertia_diag_attr = mass_api.GetDiagonalInertiaAttr()
        if inertia_diag_attr.IsValid() and inertia_diag_attr.HasValue() and inertia_diag_attr.HasAuthoredValue():
            inertia_data.inertia_diag = np.array(inertia_diag_attr.Get())

        prin_axes_attr = mass_api.GetPrincipalAxesAttr()
        if prin_axes_attr.IsValid() and prin_axes_attr.HasValue() and prin_axes_attr.HasAuthoredValue():
            prin_axes_gf_quat = mass_api.GetPrincipalAxesAttr().Get()
            prin_axes_quat = np.array(list(prin_axes_gf_quat.GetImaginary()) + [prin_axes_gf_quat.GetReal()])
            try:
                inertia_data.prin_axes = Rotation.from_quat(prin_axes_quat)
            except ValueError:
                pass

        return inertia_data


def create_new_stage_with_inertia_data(stage):
    link_prims = prim_helper.get_prims(stage, has_apis=[UsdPhysics.MassAPI, UsdPhysics.RigidBodyAPI])

    for prim in link_prims:
        inertia_data = InertiaData.init_from_prim(prim)
        mass_api = UsdPhysics.MassAPI(prim)

        # Set the mass
        mass_api.GetMassAttr().Set(inertia_data.mass)

        # Set the center of mass
        x = float(inertia_data.ref_point[0])
        y = float(inertia_data.ref_point[1])
        z = float(inertia_data.ref_point[2])
        mass_api.GetCenterOfMassAttr().Set(Gf.Vec3f(x, y, z))

        # Set the inertia diagonal
        x = float(inertia_data.inertia_diag[0])
        y = float(inertia_data.inertia_diag[1])
        z = float(inertia_data.inertia_diag[2])
        mass_api.GetDiagonalInertiaAttr().Set(Gf.Vec3f(x, y, z))

        # Set the principal axes
        quat = inertia_data.prin_axes.as_quat()
        w = float(quat[3])
        x = float(quat[0])
        y = float(quat[1])
        z = float(quat[2])
        mass_api.GetPrincipalAxesAttr().Set(Gf.Quatf(w, (x, y, z)))

    return stage
