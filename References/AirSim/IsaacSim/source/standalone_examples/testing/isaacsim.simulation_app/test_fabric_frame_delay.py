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
import os

from isaacsim import SimulationApp

simulation_app = SimulationApp(
    {"headless": True}, experience=f'{os.environ["EXP_PATH"]}/isaacsim.exp.base.zero_delay.kit'
)

import sys

import carb
import isaacsim.core.utils.prims as prim_utils
import isaacsim.core.utils.stage as stage_utils
import numpy as np
import torch
from isaacsim.core.api import SimulationContext
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.prims import Articulation, RigidPrim
from isaacsim.core.utils.prims import get_prim_attribute_value
from isaacsim.storage.native import get_assets_root_path

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit()

asset_path = assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"


def main():
    for device, backend in [["cuda:0", "torch"], ["cpu", "numpy"]]:
        SimulationContext.clear_instance()
        stage_utils.create_new_stage()
        sim = SimulationContext(stage_units_in_meters=1.0, physics_dt=0.01, device=device, backend=backend)
        prim_utils.create_prim("/World/Origin1", "Xform", translation=[0.0, 0.0, 0.0])
        cube = DynamicCuboid(
            prim_path="/World/Origin1/cube",
            name="cube",
            position=np.array([-3.0, 0.0, 0.1]),
            scale=np.array([1.0, 2.0, 0.2]),
            size=1.0,
            color=np.array([255, 0, 0]),
        )
        stage_utils.add_reference_to_stage(usd_path=asset_path, prim_path="/World/Franka")
        articulated_system = Articulation("/World/Franka")
        rigid_link = RigidPrim("/World/Franka/panda_link1")
        sim.reset()
        cube.initialize()
        rigid_link.initialize()
        articulated_system.initialize()
        articulated_system.set_world_poses(
            positions=torch.tensor([[-10, -10, 0]], device=device) if backend == "torch" else [[-10, -10, 0]]
        )
        position = cube.get_world_pose()[0]
        position[0] += 3
        cube.set_world_pose(position=position)
        cube_fabric_world_matrix = get_prim_attribute_value(
            "/World/Origin1/cube", "omni:fabric:worldMatrix", fabric=True
        )
        cube_fabric_world_position = np.array(cube_fabric_world_matrix.ExtractTranslation())
        if not (
            np.isclose(
                cube_fabric_world_position,
                np.array([-3.0, 0.0, 0.1]),
                atol=0.01,
            ).all()
        ):
            print(f"[FAIL] PhysX is not synced with Fabric CPU")
            sys.exit(1)
        sim.render()
        panda_link1_fabric_world_matrix = get_prim_attribute_value(
            "/World/Franka/panda_link1", "omni:fabric:worldMatrix", fabric=True
        )
        panda_link1_fabric_world_position = np.array(panda_link1_fabric_world_matrix.ExtractTranslation())
        if not (
            np.isclose(
                panda_link1_fabric_world_position,
                np.array([-10.0, -10.0, 0.33]),
                atol=0.01,
            ).all()
        ):
            print(f"[FAIL] Kinematic Tree is not updated in fabric")
            sys.exit(1)
        cube_fabric_world_matrix = get_prim_attribute_value(
            "/World/Origin1/cube", "omni:fabric:worldMatrix", fabric=True
        )
        cube_fabric_world_position = np.array(cube_fabric_world_matrix.ExtractTranslation())
        if not (
            np.isclose(
                cube_fabric_world_position,
                np.array([0.0, 0.0, 0.1]),
                atol=0.01,
            ).all()
        ):
            print(f"[FAIL] PhysX is not synced with Fabric CPU")
            sys.exit(1)

    print(f"[PASS] Fabric frame delay test passed")
    simulation_app.close()


if __name__ == "__main__":
    main()
