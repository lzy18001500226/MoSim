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
from collections import OrderedDict

import carb
import yaml

from .grasp_tester import GraspTestResults


# Data Class for Import/Export
class DataWriter:
    def __init__(self, gripper_frame_name, rb_frame_name):
        self.data = OrderedDict()
        self.data["format"] = "isaac_grasp"
        self.data["format_version"] = 1.0

        self.data["object_frame"] = rb_frame_name
        self.data["gripper_frame"] = gripper_frame_name

        self.data["grasps"] = OrderedDict()

    def get_next_grasp_name(self):
        return "grasp_" + str(len(self.data["grasps"]))

    def _add_grasp(self, results: GraspTestResults, confidence):
        x = results.grasp_test_settings

        grasp_dict = OrderedDict()
        name = self.get_next_grasp_name()
        grasp_dict["confidence"] = confidence
        grasp_dict["position"] = results.articulation_rel_trans
        grasp_dict["orientation"] = {
            "w": results.articulation_rel_quat[0],
            "xyz": list(results.articulation_rel_quat[1:]),
        }
        cspace_grasp_state_dict = OrderedDict()
        cspace_open_state_dict = OrderedDict()
        for dof_name, open_position, closed_position in zip(
            x.active_joints, x.active_joint_open_positions, results.stable_positions
        ):
            cspace_grasp_state_dict[dof_name] = closed_position
            cspace_open_state_dict[dof_name] = open_position
        grasp_dict["cspace_position"] = cspace_grasp_state_dict
        grasp_dict["pregrasp_cspace_position"] = cspace_open_state_dict

        self.data["grasps"][name] = grasp_dict
        return name

    def recursive_cast_to_float(self, d):
        from collections.abc import Iterable

        for k, v in d.items():
            if isinstance(v, str):
                try:
                    f = float(v)
                    d[k] = f
                except:
                    pass
            elif isinstance(v, dict):
                self.recursive_cast_to_float(v)
            elif isinstance(v, Iterable):
                l = []
                for item in v:
                    f = item
                    if isinstance(item, str):
                        try:
                            f = float(item)
                        except:
                            pass
                    l.append(f)
                d[k] = l

    def safe_load_yaml(self, path):
        with open(path, "r") as stream:
            try:
                parsed_file = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                carb.log_error("Attempted to load invalid yaml file " + str(exc))
                return {}

        self.recursive_cast_to_float(parsed_file)
        return parsed_file

    def import_grasps_from_file(self, file_path):
        x = self.safe_load_yaml(file_path)
        if len(x) == 0:
            return "The specified file could not be imported because it is not a valid YAML file."
        if x.get("format", None) != "isaac_grasp":
            return "The specified file could not be imported because it is not in the 'isaac_grasp' YAML format."
        elif "grasps" not in x:
            return "The specified file could not be imported because it does not contain any grasps."
        elif "format_version" not in x or abs(x["format_version"] - 1.0) > 1e-10:
            print("Format Version", x.get("format_version", None))
            carb.log_warn(
                "Attempting to parse grasp file that does not match the expected formatting version of 1.0. "
                + "This may result in errors."
            )

        self.data["grasps"] = x["grasps"]

        return ""

    def write_grasp_to_file(self, results: GraspTestResults, confidence: float, file_path: str):
        grasp_name = self._add_grasp(results, confidence)
        if len(self.data["grasps"]) == 1:
            self._write_first_grasp_to_file(grasp_name, file_path)
            return
        with open(file_path, "a") as f:
            self._write_grasp(grasp_name, f)

    def _write_grasp(self, k, f):
        def write_array(f, pre_string, array, end_string):
            f.write(f"{pre_string}[")
            for v in array[:-1]:
                f.write(f"{v}, ")
            f.write(f"{array[-1]}]{end_string}")

        def s(num_spaces):
            return "   " * num_spaces

        x = self.data

        v = x["grasps"][k]
        f.write(f'{s(1)}"{k}":\n')

        f.write(f'{s(2)}confidence: {v["confidence"]}\n')

        write_array(f, f"{s(2)}position: ", v["position"], "\n")
        write_array(f, f'{s(2)}orientation: {{w: {v["orientation"]["w"]}, xyz: ', v["orientation"]["xyz"], "}\n")

        f.write(f"{s(2)}cspace_position:\n")
        for key, val in v["cspace_position"].items():
            f.write(f"{s(3)}{key}: {val}\n")

        f.write(f"{s(2)}pregrasp_cspace_position:\n")
        for key, val in v["pregrasp_cspace_position"].items():
            f.write(f"{s(3)}{key}: {val}\n")
        f.write("\n")

    def _write_first_grasp_to_file(self, grasp_name, file_path: str):
        x = self.data

        with open(file_path, "w") as f:
            f.write(f'format: {x["format"]}\n')
            f.write(f'format_version: {x["format_version"]}\n\n')
            f.write(f'object_frame: {x["object_frame"]}\n')
            f.write(f'gripper_frame: {x["gripper_frame"]}\n\n')
            f.write(f"grasps:\n")
            self._write_grasp(grasp_name, f)
