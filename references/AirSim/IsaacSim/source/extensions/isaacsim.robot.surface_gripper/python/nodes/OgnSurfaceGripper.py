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

import isaacsim.robot.surface_gripper._surface_gripper as surface_gripper


class OgnSurfaceGripper:

    @staticmethod
    def compute(db) -> bool:
        gripper_interface = surface_gripper.acquire_surface_gripper_interface()
        if db.inputs.enabled and len(db.inputs.SurfaceGripper) > 0:
            input_prim = db.inputs.SurfaceGripper[0].pathString
            status = gripper_interface.get_gripper_status(input_prim)
            if status == surface_gripper.GripperStatus.Open:
                gripper_interface.close_gripper(input_prim)
            else:
                gripper_interface.open_gripper(input_prim)
