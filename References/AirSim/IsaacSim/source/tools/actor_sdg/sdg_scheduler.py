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


"""
Standalone script to run an actor sdg job

Example:
    ./python.sh tools/actor_sdg/sdg_scheduler.py -c tools/actor_sdg/default_config.yaml

Optional params:
    --sensor_placment_file sensor_placements.json
    --crash_report_path /home/xxx
    --no_random_commands
    --debug_print
    --save_usd
"""

import argparse
import asyncio
import os
import sys

import numpy as np
from isaacsim import SimulationApp

BASE_EXP_PATH = os.path.join(os.environ["EXP_PATH"], "isaacsim.exp.action_and_event_data_generation.base.kit")
APP_CONFIG = {"renderer": "RayTracedLighting", "headless": True, "width": 1920, "height": 1080}


class ActorSDG:
    def __init__(
        self, sim_app, config_file_path, camera_file_path, crash_report_path, no_random_commands, debug_print, save_usd
    ):
        self._sim_app = sim_app
        # Inputs
        self.config_file_path = config_file_path
        self.camera_file_path = camera_file_path
        self.crash_report_path = crash_report_path
        self.no_random_commands = no_random_commands
        self.debug_print = debug_print
        self.save_usd = save_usd

        self.output_path = None
        self.camera_placements_json = None
        self._sim_manager = None
        self._setup_sim_sub = None
        self._setup_sim_succeed = False
        self._dg_sub = None
        self._settings = None

    async def run(self):
        # Enable all required extensions
        self._enable_extensions()
        await self._sim_app.app.next_update_async()
        # Set up global settings
        self._set_simulation_settings()
        await self._sim_app.app.next_update_async()

        # Init SimulatonManager
        from isaacsim.replicator.agent.core.simulation import SimulationManager

        self._sim_manager = SimulationManager()

        try:
            can_load_config = self._sim_manager.load_config_file(self.config_file_path)
            if not can_load_config:
                return False

            writer_selection = self._sim_manager.get_config_file_property_group("replicator", "writer_selection")
            params = writer_selection.content_prop.get_value()
            self.output_path = params["output_dir"]
            # Set up sim
            await self._setup_sim()

            # [Optional] Camera placement
            if self.camera_file_path:
                self._do_camera_placement()

            # [Optional] Generate random commands
            if not self.no_random_commands:
                await self._gen_random_commands()

            # Wait for data generation callback
            await self._sim_manager.run_data_generation_async(will_wait_until_complete=True)
            return True
        except Exception as e:
            import carb

            carb.log_error(f"Failed to load config file {e}")
            return False

    def _enable_extensions(self):
        import omni.kit.app

        ext_manager = omni.kit.app.get_app().get_extension_manager()

        ext_manager.set_extension_enabled_immediate("omni.kit.viewport.window", True)
        ext_manager.set_extension_enabled_immediate("omni.kit.manipulator.prim", True)
        ext_manager.set_extension_enabled_immediate("omni.kit.property.usd", True)
        ext_manager.set_extension_enabled_immediate("omni.kit.scripting", True)
        ext_manager.set_extension_enabled_immediate("omni.anim.timeline", True)
        ext_manager.set_extension_enabled_immediate("omni.anim.graph.core", True)
        ext_manager.set_extension_enabled_immediate("omni.anim.retarget.core", True)
        ext_manager.set_extension_enabled_immediate("omni.anim.navigation.core", True)
        ext_manager.set_extension_enabled_immediate("omni.anim.people", True)
        ext_manager.set_extension_enabled_immediate("isaacsim.replicator.agent.core", True)
        ext_manager.set_extension_enabled_immediate("omni.kit.mesh.raycast", True)
        ext_manager.set_extension_enabled_immediate("omni.physx.graph", True)  # For Conveyor Belt

    def _set_simulation_settings(self):
        import carb
        import omni.replicator.core as rep

        rep.settings.carb_settings("/omni/replicator/backend/writeThreads", 16)
        self._settings = carb.settings.get_settings()
        self._settings.set("/app/scripting/ignoreWarningDialog", True)
        self._settings.set("/persistent/exts/omni.anim.navigation.core/navMesh/viewNavMesh", False)
        self._settings.set("/exts/omni.anim.people/navigation_settings/navmesh_enabled", True)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/aim_cameras_at_characters", True)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/min_camera_distance", 6.5)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/max_camera_distance", 14.5)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/max_camera_look_down_angle", 60)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/min_camera_look_down_angle", 0)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/min_camera_height", 2)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/max_camera_height", 3)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/character_focus_height", 0.7)
        self._settings.set("/persistent/exts/isaacsim.replicator.agent/frame_write_interval", 1)
        self._settings.set("/app/omni.graph.scriptnode/enable_opt_in", False)  # To bypass action graph scriptnode check
        self._settings.set("/rtx/raytracing/fractionalCutoutOpacity", True)  # Needed for the DH characters

        # Logging and debug print
        self._settings.set("/log/level", "info")
        self._settings.set("/log/channels/omni.replicator.core", "info")
        self._settings.set("/log/channels/isaacsim.replicator.character.core", "info")
        self._settings.set("/log/channels/omni.usd", "error")
        self._settings.set("/log/channels/omni.hydra", "error")
        self._settings.set("/log/channels/omni.kit.menu.*", "error")
        self._settings.set("/log/channels/omni.kit.property.*", "error")
        self._settings.set("/log/channels/omni.anim.graph.*", "error")
        self._settings.set("/exts/isaacsim.replicator.agent/debug_print", self.debug_print)

        # Crash reporter
        self._settings.set("/crashreporter/enabled", True)
        if self.crash_report_path:
            self._settings.set("/crashreporter/dumpDir", self.crash_report_path)
            path = self._settings.get("/crashreporter/dumpDir")
            print(f"Using carsh reporter path: {path}")

    async def _setup_sim(self):
        def done_callback(e):
            self._setup_sim_succeed = True
            self._setup_sim_sub = None

        # Set up simulation and start data generation
        self._setup_sim_sub = self._sim_manager.register_set_up_simulation_done_callback(done_callback)
        self._sim_manager.set_up_simulation_from_config_file()

        while self._setup_sim_sub and not self._sim_app.is_exiting():
            await self._sim_app.app.next_update_async()

    async def _gen_random_commands(self):
        if self._sim_manager.get_config_file_valid_value("character", "command_file"):
            task = asyncio.create_task(self._sim_manager.generate_random_commands())
            await task
            commands = task.result()
            self._sim_manager.save_commands(commands)
        if self._sim_manager.get_config_file_valid_value("robot", "command_file"):
            task = asyncio.create_task(self._sim_manager.generate_random_robot_commands())
            await task
            commands = task.result()
            self._sim_manager.save_robot_commands(commands)

    # ===== Camera placement related =====

    def _do_camera_placement(self):
        self._read_camera_json()
        if not self.camera_placements_json:
            return
        print(f"camera_placements_json = {self.camera_placements_json}")
        prop = self._sim_manager.get_config_file_property("sensor", "camera_num")
        prop.set_value(len(self.camera_placements_json))
        # Load camera
        self._sim_manager.load_camera_from_config_file()
        self._place_cameras()

    def _read_camera_json(self):
        import json

        import carb
        import omni.client

        # Read json file
        result, version, context = omni.client.read_file(self.camera_file_path)
        if result != omni.client.Result.OK:
            carb.log_error(f"Cannot load camera file path: {self.camera_file_path}. Skip camera placement.")
            return
        json_str = memoryview(context).tobytes().decode("utf-8")
        self.camera_placements_json = json.loads(json_str)

    def _place_cameras(self):
        import carb

        # Perform placement
        from isaacsim.replicator.agent.core.stage_util import CameraUtil

        camera_prims = CameraUtil.get_cameras_in_stage()
        count = 0
        for camera_dict in self.camera_placements_json:
            if count >= len(camera_prims):
                carb.log_warn("No enough cameras in the scene to set placement. Will skip the rest placement data.")
                break
            self._place_one_camera(camera_dict, camera_prims[count])
            count += 1

        print(f"Place total {count} cameras.")

    def _place_one_camera(self, camera_dict, camera_prim):
        from isaacsim.core.utils.rotations import euler_to_rot_matrix
        from isaacsim.replicator.agent.core.stage_util import CameraUtil
        from pxr import Gf

        # Extract focal length
        # - In OV, the default pixel size is 20.955/1920=0.0109140625mm
        ov_focal_length = camera_dict["focal_length"] * 0.0109140625
        # Extract transformation
        ov_pos = Gf.Vec3d(camera_dict["x"], camera_dict["y"], camera_dict["height"])
        yaw = camera_dict["yaw"]
        pitch = camera_dict["pitch"]
        np_mat_yaw = euler_to_rot_matrix(np.array([0, yaw, 0]), degrees=True, extrinsic=False)
        np_mat_pitch = euler_to_rot_matrix(np.array([-pitch, 0, 0]), degrees=True, extrinsic=False)
        np_mat_default = euler_to_rot_matrix(
            np.array([90, -90, 0]), degrees=True, extrinsic=False
        )  # To make sure when yaw=0, the camera in IsaacSim points to X positive
        rot_matrix = (
            Gf.Matrix3d(np_mat_pitch.T.tolist())
            * Gf.Matrix3d(np_mat_yaw.T.tolist())
            * Gf.Matrix3d(np_mat_default.T.tolist())
        )
        # ov_rot_euler = rot_matrix.ExtractRotation().Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
        ov_rot = rot_matrix.ExtractRotation().GetQuat()
        CameraUtil.set_camera(camera_prim, ov_pos, ov_rot, ov_focal_length)


def get_args():
    parser = argparse.ArgumentParser("Actor SDG")
    parser.add_argument("-c", "--config_file", required=True, help="Path to a IRA config file")
    # Optional config
    parser.add_argument(
        "--sensor_placment_file", required=False, help="Path to camera placement json file. Default is none."
    )
    parser.add_argument(
        "--crash_report_path",
        required=False,
        default=None,
        help="Path to store the crash report. Default is the current working directory.",
    )
    parser.add_argument(
        "--no_random_commands",
        required=False,
        default=False,
        action="store_true",
        help="Do not generate random commands.",
    )
    parser.add_argument(
        "--debug_print", required=False, default=False, action="store_true", help="Enable IRA debug print."
    )
    parser.add_argument(
        "--save_usd",
        action="store_true",
        default=False,
        help="Save the simulated scene when data generation finishes.",
    )
    args, _ = parser.parse_known_args()
    return args


# ===== Save USD =====
async def _save_usd(save_as_path):
    print("Saving USD...")
    try:
        import omni.usd

        await omni.usd.get_context().save_as_stage_async(save_as_path)
        print("Save scene to: " + str(save_as_path))
        await omni.usd.get_context().close_stage_async()
    except Exception as e:
        print("Caught exception. Unable to save USD. " + str(e), file=sys.stderr)


def main():
    # Read command line arguments
    args = get_args()
    config_file_path = args.config_file
    camera_file_path = args.sensor_placment_file
    crash_report_path = args.crash_report_path
    no_random_commands = args.no_random_commands
    debug_print = args.debug_print
    save_usd = args.save_usd

    print("Config file path: {}".format(config_file_path))
    print("Sensor placement file path: {}".format(camera_file_path))
    print("Crash Report Path: {}".format(crash_report_path))
    print("Don't random commands: {}".format(no_random_commands))
    print("Debug Print: {}".format(debug_print))
    print("Save USD: {}".format(save_usd))

    # Check files exist
    if not os.path.isfile(config_file_path):
        print("Invalid config file path. Exit.", file=sys.stderr)
        return
    if camera_file_path and not os.path.isfile(camera_file_path):
        print("Invalid camera placement path. Exit.", file=sys.stderr)
        return

    # Start SimApp
    sim_app = SimulationApp(launch_config=APP_CONFIG, experience=BASE_EXP_PATH)

    # Start SDG
    sdg = ActorSDG(
        sim_app,
        os.path.abspath(config_file_path),
        camera_file_path,
        crash_report_path,
        no_random_commands,
        debug_print,
        save_usd,
    )

    from omni.kit.async_engine import run_coroutine

    task = run_coroutine(sdg.run())
    try:
        while not task.done():
            sim_app.update()

        if not task.result():
            print("Failed to run SDG")

        # [Optional] Save USD to
        if save_usd:
            import omni.client

            save_as_path = omni.client.combine_urls("{}/".format(sdg.output_path), "scene.usd")
            save_usd_task = asyncio.ensure_future(_save_usd(save_as_path))
            while not save_usd_task.done():
                sim_app.update()

    # Close app
    finally:
        sim_app.close()


if __name__ == "__main__":
    main()
