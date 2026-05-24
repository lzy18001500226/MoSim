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

import omni.usd
from pxr import Sdf, UsdGeom, UsdLux


def Singleton(class_):
    """A singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def get_stage_default_prim_path(stage):
    """
    Helper function used for getting default prim path for any given stage.
    """
    if stage.HasDefaultPrim():
        return stage.GetDefaultPrim().GetPath()
    else:
        from pxr import Sdf

        return Sdf.Path.absoluteRootPath


def copy_prim_hierarchy(src_prim, dst_stage, dst_path, filter_fn=None):
    """
    Recursively copy only the hierarchy of src_prim to dst_stage at the specified dst_path.
    """
    # new_prim =dst_stage.DefinePrim(dst_path, src_prim.GetTypeName())
    dst_prim = dst_stage.DefinePrim(dst_path.pathString, src_prim.GetTypeName())

    # TODO: somehow differentiate the prims that you can copy and the ones you can't
    if filter_fn and not filter_fn(src_prim):
        prim = dst_stage.GetPrimAtPath(dst_path)
        # prim.SetActive(False)

    # Recursively copy child prims
    for child in src_prim.GetChildren():
        child_dst_path = dst_path.AppendChild(child.GetName())
        copy_prim_hierarchy(child, dst_stage, child_dst_path, filter_fn)


def copy_prim(src_prim, dst_stage, dst_path):
    """
    Recursively copy src_prim along with its attributes, relationships, and children
    to dst_stage at the specified dst_path.
    """
    # Ensure dst_path is an Sdf.Path object
    if isinstance(dst_path, str):
        dst_path = Sdf.Path(dst_path)
    # Define a prim of the same type at the destination stage
    dst_prim = dst_stage.DefinePrim(dst_path, src_prim.GetTypeName())

    # Copy all attributes
    for attr in src_prim.GetAttributes():
        dst_attr = dst_prim.CreateAttribute(attr.GetName(), attr.GetTypeName())
        value = attr.Get()
        if value is not None:
            dst_attr.Set(value)

    # Copy all relationships
    for rel in src_prim.GetRelationships():
        dst_rel = dst_prim.CreateRelationship(rel.GetName())
        targets = rel.GetTargets()
        dst_rel.SetTargets(targets)

    # Recursively copy child prims
    for child in src_prim.GetChildren():
        child_dst_path = dst_path.AppendChild(child.GetName())
        copy_prim(child, dst_stage, child_dst_path)


def find_unique_filename(filename):
    """
    Find a unique filename by adding incrementing numbers to the end of the filename.
    """
    base_name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filename):
        filename = f"{base_name}({counter}){ext}"
        counter += 1
    return filename


def apply_standard_stage_settings(stage):
    # Z-up, meters, default lighting
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    # environment lighting
    light_prim = UsdLux.DistantLight.Define(stage, Sdf.Path("/Environment/DistantLight"))
    light_prim.CreateIntensityAttr(3000)


def can_create_dir(path: str) -> bool:
    """
    Return True if we can write into `path` if it existed:
      - If `path` exists and is a directory: test write permission on it.
      - Otherwise: walk upward to find the nearest existing parent and test write there.
    """
    # Normalize
    path = os.path.abspath(path)

    # If it already exists and is a dir, test it directly:
    if os.path.isdir(path):
        return os.access(path, os.W_OK)

    # Otherwise, find nearest existing parent
    parent = path
    while parent and not os.path.exists(parent):
        parent = os.path.dirname(parent)
    # If we walked off the root (shouldn’t really happen), bail out
    if not parent:
        return False

    # Must be a directory to create a subdir
    if not os.path.isdir(parent):
        parent = os.path.dirname(parent)
        if not parent or not os.path.isdir(parent):
            return False

    return os.access(parent, os.W_OK)


def stage_is_dirty(stage):
    # Iterate through every layer in the stack (root + all sublayers + session)
    for layer in stage.GetLayerStack():
        if layer.IsDirty():
            return True
    return False
