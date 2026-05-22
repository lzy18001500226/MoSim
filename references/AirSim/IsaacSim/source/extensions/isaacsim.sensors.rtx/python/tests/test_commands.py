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
"""Unit tests for RTX sensor commands.

Tests the functionality of creating different types of RTX sensors through commands.
"""

from pathlib import Path

import omni.kit.commands
import omni.kit.test
import omni.usd
from isaacsim.core.utils.prims import get_prim_at_path
from isaacsim.core.utils.stage import traverse_stage
from isaacsim.sensors.rtx import SUPPORTED_LIDAR_CONFIGS, SUPPORTED_LIDAR_VARIANT_SET_NAME
from pxr import Gf, Sdf, UsdGeom


class TestRtxSensorCommands(omni.kit.test.AsyncTestCase):
    """Test cases for RTX sensor creation commands."""

    async def setUp(self):
        """Create a new stage for each test."""
        await omni.usd.get_context().new_stage_async()
        self.stage = omni.usd.get_context().get_stage()

    async def tearDown(self):
        """Clean up the stage after each test."""
        await omni.usd.get_context().close_stage_async()

    async def test_create_rtx_lidar_configs(self):
        """Test creating RTX Lidar sensors with different configurations."""
        translation = Gf.Vec3d(0.0, 0.0, 0.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)

        for config_path in SUPPORTED_LIDAR_CONFIGS:
            config = Path(config_path).stem
            vendor_name = Path(config_path).parts[3]
            # Try all possible supported config names:
            # 1. exact match to config path stem
            # 2. exact match to config path stem, with spaces instead of underscores
            # 3. exact match to config path stem, with vendor name stripped
            # 4. exact match to config path stem, with spaces instead of underscores, and vendor name stripped
            allowed_configs = [
                config,
                config.replace("_", " "),
            ]
            if config.startswith(vendor_name):
                allowed_configs.append(config[len(vendor_name) + 1 :])
                allowed_configs.append(config[len(vendor_name) + 1 :].replace("_", " "))
            # Create new stage for each config to avoid conflicts
            await omni.usd.get_context().new_stage_async()
            self.stage = omni.usd.get_context().get_stage()
            for i, allowed_config in enumerate(allowed_configs):

                for variant in SUPPORTED_LIDAR_CONFIGS[config_path] or [None]:
                    path = f"/RtxLidar_{config}_{i}_{variant}"
                    _, prim = omni.kit.commands.execute(
                        "IsaacSensorCreateRtxLidar",
                        path=path,
                        config=allowed_config,
                        variant=variant,
                        translation=translation,
                        orientation=orientation,
                    )

                    self.assertIsNotNone(
                        prim, f"Failed to create prim for config {allowed_config} and variant {variant}"
                    )
                    self.assertEqual(prim.GetTypeName(), "OmniLidar")

                    if variant is not None:
                        prim = get_prim_at_path(path)
                        variant_set = prim.GetVariantSet(SUPPORTED_LIDAR_VARIANT_SET_NAME)
                        self.assertGreater(
                            len(variant_set.GetVariantNames()),
                            0,
                            f"Variant set '{SUPPORTED_LIDAR_VARIANT_SET_NAME}' on prim {path} does not contain any variants.",
                        )
                        current_variant = variant_set.GetVariantSelection()
                        self.assertEqual(
                            current_variant,
                            variant,
                            f"Incorrect variant selection {current_variant} for config {allowed_config} and variant {variant}",
                        )

    async def test_create_rtx_lidar_invalid_config(self):
        """Test creating an RTX Lidar sensor with an invalid configuration."""
        translation = Gf.Vec3d(0.0, 0.0, 0.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)
        path = "/RtxLidar_InvalidConfig"
        invalid_config = "invalid_config"

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path=path,
            config=invalid_config,
            translation=translation,
            orientation=orientation,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        self.assertTrue(prim.IsA("OmniLidar"))

    async def test_create_rtx_radar_no_config(self):
        """Test creating an RTX Radar sensor without a configuration."""
        translation = Gf.Vec3d(0.0, 1.0, 2.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxRadar",
            path="/RtxRadar",
            translation=translation,
            orientation=orientation,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        self.assertTrue(prim.IsA("OmniRadar"))

    async def test_create_rtx_radar_with_config(self):
        """Test creating an RTX Radar sensor with a configuration."""
        translation = Gf.Vec3d(0.0, 1.0, 2.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)
        config = "test_radar_config"

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxRadar",
            path="/RtxRadar",
            config=config,
            translation=translation,
            orientation=orientation,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        self.assertTrue(prim.IsA("OmniRadar"))

    async def test_create_rtx_ids_default_config(self):
        """Test creating an RTX IDS sensor with default configuration."""
        translation = Gf.Vec3d(0.0, 0.0, 1.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxIDS",
            path="/RtxIDS",
            translation=translation,
            orientation=orientation,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        self.assertEqual(prim.GetPath(), Sdf.Path("/RtxIDS"))
        self.assertEqual(prim.GetTypeName(), "Camera")

        # Verify sensor type and default config
        sensor_type_attr = prim.GetAttribute("cameraSensorType")
        self.assertTrue(sensor_type_attr.IsValid())
        self.assertEqual(sensor_type_attr.Get(), "ids")

        config_attr = prim.GetAttribute("sensorModelConfig")
        self.assertTrue(config_attr.IsValid())
        self.assertEqual(config_attr.Get(), "idsoccupancy")

        plugin_attr = prim.GetAttribute("sensorModelPluginName")
        self.assertTrue(plugin_attr.IsValid())
        self.assertEqual(plugin_attr.Get(), "omni.sensors.nv.ids.ids.plugin")

    async def test_create_rtx_ids_with_config(self):
        """Test creating an RTX IDS sensor with a specific configuration."""
        translation = Gf.Vec3d(0.0, 0.0, 1.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)
        config = "test_ids_config"

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxIDS",
            path="/RtxIDS",
            config=config,
            translation=translation,
            orientation=orientation,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        self.assertEqual(prim.GetTypeName(), "Camera")

        sensor_type_attr = prim.GetAttribute("cameraSensorType")
        self.assertTrue(sensor_type_attr.IsValid())
        self.assertEqual(sensor_type_attr.Get(), "ids")

        config_attr = prim.GetAttribute("sensorModelConfig")
        self.assertTrue(config_attr.IsValid())
        self.assertEqual(config_attr.Get(), config)

        plugin_attr = prim.GetAttribute("sensorModelPluginName")
        self.assertTrue(plugin_attr.IsValid())
        self.assertEqual(plugin_attr.Get(), "omni.sensors.nv.ids.ids.plugin")

    async def test_create_rtx_ultrasonic_default(self):
        """Test creating an RTX Ultrasonic sensor with default configuration."""
        translation = Gf.Vec3d(-1.0, 0.0, 0.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxUltrasonic",
            path="/RtxUltrasonic",
            translation=translation,
            orientation=orientation,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        self.assertEqual(prim.GetPath(), Sdf.Path("/RtxUltrasonic"))
        self.assertEqual(prim.GetTypeName(), "Camera")

        # Verify sensor type
        sensor_type_attr = prim.GetAttribute("cameraSensorType")
        self.assertTrue(sensor_type_attr.IsValid())
        self.assertEqual(sensor_type_attr.Get(), "ultrasonic")

        plugin_attr = prim.GetAttribute("sensorModelPluginName")
        self.assertTrue(plugin_attr.IsValid())
        self.assertEqual(plugin_attr.Get(), "omni.sensors.nv.ultrasonic.wpm_ultrasonic.plugin")

    async def test_create_rtx_ultrasonic_with_config(self):
        """Test creating an RTX Ultrasonic sensor with a specific configuration."""
        translation = Gf.Vec3d(-1.0, 0.0, 0.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)
        config = "test_ultrasonic_config"

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxUltrasonic",
            path="/RtxUltrasonic",
            config=config,
            translation=translation,
            orientation=orientation,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        self.assertEqual(prim.GetTypeName(), "Camera")

        config_attr = prim.GetAttribute("sensorModelConfig")
        self.assertTrue(config_attr.IsValid())
        self.assertEqual(config_attr.Get(), config)

        plugin_attr = prim.GetAttribute("sensorModelPluginName")
        self.assertTrue(plugin_attr.IsValid())
        self.assertEqual(plugin_attr.Get(), "omni.sensors.nv.ultrasonic.wpm_ultrasonic.plugin")

    async def test_sensor_with_parent(self):
        """Test creating a sensor with a parent prim."""
        # Create a parent Xform
        parent_path = "/World"
        parent = UsdGeom.Xform.Define(self.stage, parent_path)

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path="/RtxLidar",
            parent=parent_path,
            config="OS1",
        )

        self.assertIsNotNone(prim)

        # Find OmniLidar prim by traversing the stage
        found_lidar = False
        for prim in traverse_stage():
            if prim.IsA("OmniLidar"):
                found_lidar = True
                self.assertTrue(prim.GetPath().HasPrefix(parent_path))
                break

        self.assertTrue(found_lidar, "Failed to find OmniLidar prim with parent")

    async def test_rtx_radar_force_camera_prim_with_config(self):
        """Test RTX Radar with force_camera_prim=True and config specified."""
        translation = Gf.Vec3d(0.0, 1.0, 2.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)
        config = "test_radar_config"

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxRadar",
            path="/RtxRadar",
            config=config,
            translation=translation,
            orientation=orientation,
            force_camera_prim=True,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        # Verify it's a Camera prim with radar sensor type
        self.assertTrue(prim.IsA(UsdGeom.Camera))
        sensor_type_attr = prim.GetAttribute("cameraSensorType")
        self.assertTrue(sensor_type_attr.IsValid())
        self.assertEqual(sensor_type_attr.Get(), "radar")
        # Verify config is set
        config_attr = prim.GetAttribute("sensorModelConfig")
        self.assertTrue(config_attr.IsValid())
        self.assertEqual(config_attr.Get(), config)

        plugin_attr = prim.GetAttribute("sensorModelPluginName")
        self.assertTrue(plugin_attr.IsValid())
        self.assertEqual(plugin_attr.Get(), "omni.sensors.nv.radar.wpm_dmatapprox.plugin")

    async def test_rtx_lidar_force_camera_prim_with_config(self):
        """Test RTX Lidar with force_camera_prim=True and config specified."""
        translation = Gf.Vec3d(0.0, 0.0, 0.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)
        config = Path(list(SUPPORTED_LIDAR_CONFIGS.keys())[0]).stem  # Use the first available config

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path="/RtxLidar",
            config=config,
            translation=translation,
            orientation=orientation,
            force_camera_prim=True,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        # Verify it's a Camera prim with lidar sensor type
        self.assertTrue(prim.IsA(UsdGeom.Camera))

        sensor_type_attr = prim.GetAttribute("cameraSensorType")
        self.assertTrue(sensor_type_attr.IsValid())
        self.assertEqual(sensor_type_attr.Get(), "lidar")
        # Verify config is set
        config_attr = prim.GetAttribute("sensorModelConfig")
        self.assertTrue(config_attr.IsValid())
        self.assertEqual(config_attr.Get(), config)

        plugin_attr = prim.GetAttribute("sensorModelPluginName")
        self.assertTrue(plugin_attr.IsValid())
        self.assertEqual(plugin_attr.Get(), "omni.sensors.nv.lidar.lidar_core.plugin")

    async def test_rtx_lidar_default_creation(self):
        """Test RTX Lidar default creation (no config, no force_camera_prim)."""
        translation = Gf.Vec3d(0.0, 0.0, 0.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path="/RtxLidar",
            translation=translation,
            orientation=orientation,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        # Verify it's an OmniLidar prim
        self.assertTrue(prim.IsA("OmniLidar"))

    async def test_rtx_lidar_force_camera_no_config(self):
        """Test RTX Lidar with force_camera_prim=True but no config specified."""
        translation = Gf.Vec3d(0.0, 0.0, 0.0)
        orientation = Gf.Quatd(1.0, 0.0, 0.0, 0.0)

        _, prim = omni.kit.commands.execute(
            "IsaacSensorCreateRtxLidar",
            path="/RtxLidar",
            translation=translation,
            orientation=orientation,
            force_camera_prim=True,
        )

        self.assertIsNotNone(prim)
        self.assertTrue(prim.IsValid())
        # Verify it's a Camera prim with lidar sensor type
        self.assertTrue(prim.IsA(UsdGeom.Camera))
        sensor_type_attr = prim.GetAttribute("cameraSensorType")
        self.assertTrue(sensor_type_attr.IsValid())
        self.assertEqual(sensor_type_attr.Get(), "lidar")
        # Verify sensorModelConfig attribute doesn't exist
        config_attr = prim.GetAttribute("sensorModelConfig")
        self.assertFalse(config_attr.IsValid())

        plugin_attr = prim.GetAttribute("sensorModelPluginName")
        self.assertTrue(plugin_attr.IsValid())
        self.assertEqual(plugin_attr.Get(), "omni.sensors.nv.lidar.lidar_core.plugin")
