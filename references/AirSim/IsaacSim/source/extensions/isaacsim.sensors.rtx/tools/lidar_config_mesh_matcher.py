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

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

import argparse
import json
import re
from pathlib import Path

import carb
import omni.kit.commands
import omni.usd
from isaacsim.core.utils.stage import add_reference_to_stage, create_new_stage, save_stage
from isaacsim.storage.native import get_assets_root_path
from pxr import Gf, Usd

parser = argparse.ArgumentParser(description="This tool will create a RTX sensor at the desired location of the USD")
parser.add_argument(
    "-j",
    "--json",
    help="json config, if this is a directory, then it will apply to all json files in that directory (not to subdirectories)",
)
parser.add_argument("-u", "--usd_path", help="usd path to match")
parser.add_argument("-o", "--om_path", default=True, help="True for omniverse asset, False for local asset")
parser.add_argument(
    "-t",
    "--translation",
    default=[0, 0, 0],
    type=float,
    nargs="*",
    help="Relative translation between the mesh and sensor, default [0,0,0]",
)
parser.add_argument(
    "-q",
    "--orientation",
    default=[1, 0, 0, 0],
    type=float,
    nargs="*",
    help="Relative transform between mesh and sensor, in quat WXYZ, default [1,0,0,0]",
)
args, unknown = parser.parse_known_args()


def main():
    input_path = Path(args.json)
    config_paths = []

    if not input_path.exists():
        carb.log_error(f"{str(input_path)} does not exist")
        return

    elif input_path.is_file():
        config_paths.append(input_path)
    elif input_path.is_dir():
        config_paths = list(input_path.glob("*.json"))
    else:
        carb.log_error(f"{str(input_path)} is not dir or file")
        return

    if not args.om_path:
        usd_path = args.usd_path
    else:
        usd_path = get_assets_root_path() + args.usd_path

    translation = Gf.Vec3d(args.translation[0], args.translation[1], args.translation[2])
    orientation = Gf.Quatd(args.orientation[0], args.orientation[1], args.orientation[2], args.orientation[3])

    for config_path in config_paths:
        create_new_stage()
        _stage = omni.usd.get_context().get_stage()
        name = config_path.stem
        print(f"creating mesh from {str(usd_path)} prim path {str(name)}")
        prim = add_reference_to_stage(usd_path=usd_path, prim_path="/" + name)
        _stage.SetDefaultPrim(prim)

        result, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path="/sensor",
            parent="/" + name,
            config=str(config_path),
            translation=translation,
            orientation=orientation,
        )
        if not result:
            carb.log_error(f"failed to sensor for {str(config_path)}")
            continue

        data = json.load(open(str(config_path)))
        ui_name = data["name"]
        # this regex generates a usd file from the sensor name, and replaces all symbols and spaces with underscores so it's a legal filename
        ui_name = re.sub(r'[@#!$%^&<>:"/\\|?*\0 ]', "_", ui_name)
        dir = str(config_path.parent)
        save_stage(dir + "/" + str(ui_name) + ".usd")


if __name__ == "__main__":
    main()
    simulation_app.close()
