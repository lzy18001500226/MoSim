# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from typing import List, Tuple

import carb
import numpy as np
from isaacsim.core.utils.numpy.rotations import quats_to_rot_matrices, rot_matrices_to_quats

from .data_writer import DataWriter


class GraspSpec:
    def __init__(self, imported_data: dict):
        self._imported_data = imported_data

    def get_grasp_names(self) -> List[str]:
        """Get a list of valid grasp names stored in the imported `isaac_grasp` file.

        Returns:
            List[str]:
                List of valid grasp names.
        """
        return list(self._imported_data["grasps"].keys())

    def get_grasp_dict_by_name(self, name: str) -> dict:
        """Get a dictionary of all data associated with a specific grasp name.

        Args:
            name (str): Valid grasp name.

        Returns:
            dict:
                Dictionary containing the data associated with this grasp.  This includes

            confidence (float):
                A confidence value between 0.0 and 1.0 indicating the quality of this grasp.

            position (np.array):
                Translation of the gripper frame relative to the rigid body frame.

            orientation (dict):
                Dictionary with `w` and `xyz` components that define the orientation
                of the gripper frame relative to the rigid body frame.

            cspace_position (dict):
                A dictionary mapping each DOF that is considered to be part of
                the gripper to the position it was in when grasping this object.

            pregrasp_cspace_position (dict):
                A dictionary mapping each DOF that is considered to be
                part of the gripper to its open position.  I.e. a grasp of this object can be
                acheived by moving from the `pregrasp_cspace_position` to `cspace_position` while
                the gripper is at the relative pose specified by `position` and `orientation`.
        """
        if name not in self._imported_data["grasps"]:
            carb.log_error(f"Invalid grasp name {name} was given.  Nothing will be returned.")
            return
        return self._imported_data["grasps"][name]

    def get_grasp_dicts(self) -> dict:
        """Get a dictionary of dictionaries that specify each grasp in the imported file.  The
        `get_grasp_dict_by_name()` function describes the content of each inner dictionary, and the
        `get_grasp_names()` function provides the keys to this dictionary.

        Returns:
            dict:
                A dictionary of dictionaries that define each grasp in the imported file.
        """
        return self._imported_data["grasps"]

    def compute_gripper_pose_from_rigid_body_pose(
        self, grasp_name: str, rb_trans: np.array, rb_quat: np.array
    ) -> Tuple[np.array, np.array]:
        """Given a position of the rigid body in the world or robot frame, compute the position of
        the gripper in that same frame to replicate the grasp associated `grasp_name`.

        Args:
            grasp_name (str): Name of an imported grasp.
            rb_trans (np.array): Translation of the rigid body in the desired frame of reference.
            rb_quat (np.array): Quaternion orientation of the rigid body in the desired frame of reference.

        Returns:
            Tuple[np.array, np.array]:
                Translation and orientation of the gripper in the desired frame of reference.
        """
        if grasp_name not in self._imported_data["grasps"]:
            carb.log_warn(
                f"Invalid grasp name {grasp_name} provided.  Use `get_grasp_names()` to "
                + "get a list of valid grasp names."
            )
            return None, None
        grasp = self.get_grasp_dict_by_name(grasp_name)

        art_quat_rel_rb = np.array([grasp["orientation"]["w"], *grasp["orientation"]["xyz"]])
        art_rot_rel_rb, rb_rot = quats_to_rot_matrices(np.vstack([art_quat_rel_rb, rb_quat]))
        art_trans_rel_rb = np.array(grasp["position"])

        art_trans = rb_rot @ art_trans_rel_rb + rb_trans
        art_rot = rb_rot @ art_rot_rel_rb

        return art_trans, rot_matrices_to_quats(art_rot)

    def compute_rigid_body_pose_from_gripper_pose(
        self, grasp_name: str, gripper_trans: np.array, gripper_quat: np.array
    ) -> Tuple[np.array, np.array]:
        """Given a position of the gripper in the world or robot frame, compute the position of
        the rigid body in that same frame to replicate the grasp associated `grasp_name`.

        Args:
            grasp_name (str): Name of an imported grasp.
            gripper_trans (np.array): Translation of the gripper in the desired frame of reference.
            gripper_quat (np.array): Quaternion orientation of the gripper in the desired frame of reference.

        Returns:
            Tuple[np.array, np.array]:
                Translation and orientation of the rigid body in the desired frame of reference.
        """
        if grasp_name not in self._imported_data["grasps"]:
            carb.log_warn(
                f"Invalid grasp name {grasp_name} provided.  Use `get_grasp_names()` to "
                + "get a list of valid grasp names."
            )
            return None, None
        grasp = self.get_grasp_dict_by_name(grasp_name)

        art_quat_rel_rb = np.array([grasp["orientation"]["w"], *grasp["orientation"]["xyz"]])
        art_rot_rel_rb, art_rot = quats_to_rot_matrices(np.vstack([art_quat_rel_rb, gripper_quat]))
        art_trans_rel_rb = np.array(grasp["position"])

        rb_rot = art_rot @ art_rot_rel_rb.T
        rb_quat = rot_matrices_to_quats(rb_rot)
        rb_trans_rel_art = gripper_trans - rb_rot @ art_trans_rel_rb

        return rb_trans_rel_art, rb_quat


def import_grasps_from_file(file_path: str) -> GraspSpec:
    """Parse an `isaac_grasp` YAML file for use in Isaac Sim.  The resulting `GraspSpec` class will
    allow you to look up the data for each grasp by its name.

    Args:
        file_path (str): A path to an `isaac_grasp` YAML file with format version 1.0.

    Returns:
        GraspSpec:
            A data class that stores the information needed to replicate a grasp in Isaac
            Sim.  This class also includes convenience functions to compute the desired pose of the
            gripper frame as a function of the of object position, or to compute the desired object
            position as a function of gripper pose.
    """
    data_writer = DataWriter("", "")

    error_msg = data_writer.import_grasps_from_file(file_path)
    if error_msg != "":
        carb.log_error(error_msg)

    return GraspSpec(data_writer.data)
