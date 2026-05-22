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

import asyncio
import os
import unittest
from pathlib import Path

import carb
import matplotlib.pyplot as plt
import numpy as np
import omni.kit.test
import omni.replicator.core as rep
from isaacsim.core.api.materials import OmniPBR
from isaacsim.core.api.objects import VisualCuboid
from isaacsim.core.utils.stage import create_new_stage_async, get_current_stage, update_stage_async
from isaacsim.sensors.rtx import (
    SUPPORTED_LIDAR_CONFIGS,
    LidarRtx,
    apply_nonvisual_material,
    decode_material_id,
    get_gmo_data,
    get_material_id,
)
from isaacsim.storage.native import get_assets_root_path
from pxr import Gf, UsdGeom

DEBUG_DRAW_PRINT = False

# Maximum difference in fireTimeNs for Example_Rotary configuration
MAX_TIMESTAMP_DIFF = 3500


def create_sarcophagus(enable_nonvisual_material: bool = True):
    # Autogenerate sarcophagus
    dims = [(10, 5, 7), (15, 9, 11), (20, 13, 15), (25, 17, 19)]
    i = 0
    cube_info = {}
    for l, h1, h2 in dims:
        h = h1 + h2
        x_sign = -1 if 0 < i < 3 else 1
        y_sign = -1 if i > 1 else 1
        signs = np.array([x_sign, y_sign, 1])

        # Place cube normal to x-axis
        cube = VisualCuboid(
            prim_path=f"/World/cube_{i*4}",
            name=f"cube_{i*4}",
            position=np.multiply(signs, np.array([l + 0.5, l / 2, h1 - h / 2])),
            scale=np.array([1, l, h]),
        )
        if enable_nonvisual_material:
            material = OmniPBR(
                prim_path=f"/World/cube_{i*4}/material",
                name=f"cube_{i*4}_material",
                color=np.array([1, 0, 0]),
            )
            apply_nonvisual_material(material.prim, "aluminum", "paint", "emissive")
            cube.apply_visual_material(material)
            cube_info[f"/World/cube_{i*4}"] = {"material_id": get_material_id(material.prim)}

        # place cube normal to y-axis
        cube = VisualCuboid(
            prim_path=f"/World/cube_{i*4+1}",
            name=f"cube_{i*4+1}",
            position=np.multiply(signs, np.array([l / 2, l + 0.5, h1 - h / 2])),
            scale=np.array([l, 1, h]),
        )
        if enable_nonvisual_material:
            material = OmniPBR(
                prim_path=f"/World/cube_{i*4+1}/material",
                name=f"cube_{i*4+1}_material",
                color=np.array([0, 1, 0]),
            )
            apply_nonvisual_material(material.prim, "steel", "clearcoat", "emissive")
            cube.apply_visual_material(material)
            cube_info[f"/World/cube_{i*4+1}"] = {"material_id": get_material_id(material.prim)}

        # place cube normal to z-axis, top
        cube = VisualCuboid(
            prim_path=f"/World/cube_{i*4+2}",
            name=f"cube_{i*4+2}",
            position=np.multiply(signs, np.array([l / 2, l / 2, h1 + 0.5])),
            scale=np.array([l, l, 1]),
        )
        if enable_nonvisual_material:
            material = OmniPBR(
                prim_path=f"/World/cube_{i*4+2}/material",
                name=f"cube_{i*4+2}_material",
                color=np.array([0, 0, 1]),
            )
            apply_nonvisual_material(material.prim, "concrete", "clearcoat", "emissive")
            cube.apply_visual_material(material)
            cube_info[f"/World/cube_{i*4+2}"] = {"material_id": get_material_id(material.prim)}

        # place cube normal to z-axis, bottom
        cube = VisualCuboid(
            prim_path=f"/World/cube_{i*4+3}",
            name=f"cube_{i*4+3}",
            position=np.multiply(signs, np.array([l / 2, l / 2, -h2 - 0.5])),
            scale=np.array([l, l, 1]),
        )
        if enable_nonvisual_material:
            material = OmniPBR(
                prim_path=f"/World/cube_{i*4+3}/material",
                name=f"cube_{i*4+3}_material",
                color=np.array([1, 1, 0]),
            )
            apply_nonvisual_material(material.prim, "concrete", "paint", "emissive")
            cube.apply_visual_material(material)
            cube_info[f"/World/cube_{i*4+3}"] = {"material_id": get_material_id(material.prim)}

        i += 1
    return cube_info


class TestIsaacCreateRTXLidarScanBuffer(omni.kit.test.AsyncTestCase):
    """Test the Isaac Create RTX Lidar Scan Buffer annotator"""

    async def setUp(self):
        """Setup test environment with a cube and lidar"""
        await create_new_stage_async()
        await update_stage_async()

        # Ordering octants in binary order, such that octant 0 is +++, octant 1 is ++-, etc. for XYZ.
        self._octant_dimensions = [
            (10, 10, 5),
            (10, 10, 7),
            (25, 25, 17),
            (25, 25, 19),
            (15, 15, 9),
            (15, 15, 11),
            (20, 20, 13),
            (20, 20, 15),
        ]
        self.cube_info = create_sarcophagus()

        self._timeline = omni.timeline.get_timeline_interface()
        self._annotator_data = None
        self.hydra_texture = None

    async def tearDown(self):
        self._timeline.stop()
        if self._annotator:
            self._annotator.detach()
        self.hydra_texture.destroy()
        self.hydra_texture = None
        await omni.kit.app.get_app().next_update_async()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)
        await update_stage_async()

    async def _test_intensity(self):
        pass

    async def _test_object_id(self):
        stable_id_map = LidarRtx.decode_stable_id_mapping(self._annotator_stable_id_map_data.tobytes())
        self.assertGreater(len(stable_id_map), 0, "Expected non-empty stable id map.")

        object_ids = LidarRtx.get_object_ids(self.objectId)
        self.assertEqual(
            len(object_ids), len(self.cube_prim_paths), "Expected same number of object ids as number of valid returns."
        )

        unexpected_object_ids = set(object_ids) - stable_id_map.keys()
        self.assertFalse(
            len(unexpected_object_ids) > 0,
            f"Expected no unexpected object ids. Unexpected object ids: {unexpected_object_ids}",
        )

        for i, object_id in enumerate(object_ids):
            az = self.azimuth[i]
            el = self.elevation[i]
            r = self.distance[i]
            if (az % 45) < 0.5:
                # Skip returns that are within 0.5deg of an octant edge or corner
                continue
            stable_id = stable_id_map[object_id]
            self.assertEqual(
                stable_id,
                self.cube_prim_paths[i],
                f"Return {i} with azimuth {az}, elevation {el}, range {r}, and object id {object_id} has stable id {stable_id}, but intersected {self.cube_prim_paths[i]}.",
            )

    async def _test_velocity(self):
        pass

    async def _test_normal(self):
        pass

    async def _test_timestamp(self):
        timestamp_diffs = np.diff(self.timestamp)
        self.assertTrue(np.all(timestamp_diffs >= 0), "Timestamps are not monotonically increasing.")
        self.assertTrue(
            np.all(timestamp_diffs <= MAX_TIMESTAMP_DIFF),
            "Max difference in timestamps is expected to be 3500ns, the maximum difference in fireTimeNs in the Example_Rotary configuration.",
        )
        pass

    async def _test_emitter_id(self):
        pass

    async def _test_beam_id(self):
        pass

    async def _test_material_id(self):

        self.assertEqual(
            len(self.materialId),
            len(self.cube_prim_paths),
            "Expected same number of material ids as number of valid returns.",
        )

        for material_id, prim_path in zip(self.materialId, self.cube_prim_paths):
            self.assertEqual(
                self.cube_info[prim_path]["material_id"],
                material_id,
                f"Expected material id {self.cube_info[prim_path]['material_id']} for return generated by {prim_path}, got {material_id}.",
            )

        pass

    async def test_annotator_outputs(self):  # Create sensor prim
        kwargs = {
            "path": "lidar",
            "parent": None,
            "translation": Gf.Vec3d(0.0, 0.0, 0.0),
            "orientation": Gf.Quatd(1.0, 0.0, 0.0, 0.0),
            "config": "Example_Rotary",
            "variant": None,
            "omni:sensor:Core:outputFrameOfReference": "WORLD",
            "omni:sensor:Core:auxOutputType": "FULL",
        }

        _, self.sensor = omni.kit.commands.execute(f"IsaacSensorCreateRtxLidar", **kwargs)
        sensor_type = self.sensor.GetTypeName()
        self.assertEqual(
            sensor_type, "OmniLidar", f"Expected OmniLidar prim, got {sensor_type}. Was sensor prim created?"
        )

        # Create render product and attach to sensor
        self.hydra_texture = rep.create.render_product(
            self.sensor.GetPath(),
            [32, 32],
            name="RtxSensorRenderProduct",
            render_vars=["GenericModelOutput", "RtxSensorMetadata"],
        )
        # Attach annotator to render product
        self._annotator = rep.AnnotatorRegistry.get_annotator("IsaacCreateRTXLidarScanBuffer")
        self._annotator.initialize(
            outputIntensity=True,
            outputDistance=True,
            outputObjectId=True,
            outputVelocity=True,
            outputAzimuth=True,
            outputElevation=True,
            outputNormal=True,
            outputTimestamp=True,
            outputEmitterId=True,
            outputBeamId=True,
            outputMaterialId=True,
        )
        self._annotator.attach([self.hydra_texture.path])

        # Attach StableIdMap annotator to OmniLidar prim to pick up object IDs
        self._annotator_stable_id_map = rep.AnnotatorRegistry.get_annotator("StableIdMap")
        self._annotator_stable_id_map.attach([self.hydra_texture.path])

        # Render frames until we get valid data, or until we've rendered the maximum number of frames
        self._timeline.play()
        for _ in range(10):
            # Wait for a single frame
            await omni.kit.app.get_app().next_update_async()
            self._annotator_data = self._annotator.get_data()
            self._annotator_stable_id_map_data = self._annotator_stable_id_map.get_data()
            if self._annotator_data and "data" in self._annotator_data and self._annotator_data["data"].size > 0:
                break
        self._timeline.stop()

        # Test that all expected keys are present in the annotator data, then copy those values to the test class attributes
        for expected_key in [
            "azimuth",
            "beamId",
            "data",
            "distance",
            "elevation",
            "emitterId",
            "index",
            "intensity",
            "materialId",
            "normal",
            "objectId",
            "timestamp",
            "velocity",
        ]:
            self.assertIn(expected_key, self._annotator_data)
            setattr(self, expected_key, self._annotator_data[expected_key])

        self.assertIn("info", self._annotator_data)
        for expected_key in [
            "numChannels",
            "numEchos",
            "numReturnsPerScan",
            "renderProductPath",
            "ticksPerScan",
            "transform",
            "azimuth",
            "beamId",
            "distance",
            "elevation",
            "emitterId",
            "index",
            "intensity",
            "materialId",
            "normal",
            "objectId",
            "timestamp",
            "velocity",
        ]:
            self.assertIn(expected_key, self._annotator_data["info"])
            setattr(self, expected_key, self._annotator_data["info"][expected_key])

        # Test point cloud data shape
        self.assertGreater(self.data.shape[0], 0, "Expected non-empty data.")
        self.assertEqual(self.data.shape[1], 3)

        # Get octant dimensions and indices
        r_vals = np.linalg.norm(self.data, axis=1)
        unit_vecs = np.divide(self.data, np.repeat(r_vals[:, None], 3, axis=1))
        octant = (unit_vecs[:, 0] < 0) * 4 + (unit_vecs[:, 1] < 0) * 2 + (unit_vecs[:, 2] < 0)
        dims = np.array([self._octant_dimensions[o] for o in octant])

        # Let alpha be the angle between the normal to the plane and the return vector
        # Let the distance from the origin of the return vector along the normal vector to the plane be l =  dims(idx)
        # Let expected range R be the distance along the return vector to the point of intersection with the plane
        # Then, cos(alpha) = l / R
        # Next, observe cos(alpha) = n-hat dot r-hat, where n-hat is the unit normal vector to the plane
        # and r-hat is the unit return vector
        # Therefore, R = l / (n-hat dot r-hat)
        # n-hat dot r-hat is simply the index of the unit return vector corresponding to the plane
        # This simplifies the computation of expected range to elementwise-division of the dimensions by the unit return vectors
        # The minimum of these values is the expected range to the first plane the return vector will intersect
        # The minimum index of the plane is the index of the plane that is struck first in the octant
        plane_idx = np.argmin(np.divide(dims, np.abs(unit_vecs)), axis=1)

        # Determine the cube which was struck by the return vector.
        # The first check is which octant the return vector is in. Note the sequence is based on the sequence of
        # octants as defined in the test setup.
        cube_idx = np.zeros(octant.shape, dtype=int)
        cube_idx[octant == 0] = 0
        cube_idx[octant == 1] = 0
        cube_idx[octant == 2] = 3
        cube_idx[octant == 3] = 3
        cube_idx[octant == 4] = 1
        cube_idx[octant == 5] = 1
        cube_idx[octant == 6] = 2
        cube_idx[octant == 7] = 2
        # Next, multiply the cube index by 4 to get which iteration of the test setup we're in, then add the plane index
        # to select if the return vector struck the x-normal face, y-normal face, or one of the z-normal faces.
        cube_idx = cube_idx * 4 + plane_idx
        # For odd octants (z < 0), the z-normal face is the bottom face, so add 1 to the cube index.
        cube_idx[np.bitwise_and(octant % 2 == 1, plane_idx == 2)] += 1
        # Finally, convert the cube index to the prim path of the cube.
        self.cube_prim_paths = [f"/World/cube_{int(i)}" for i in cube_idx]

        await self._test_intensity()
        await self._test_object_id()
        await self._test_velocity()
        await self._test_normal()
        await self._test_timestamp()
        await self._test_emitter_id()
        await self._test_beam_id()
        await self._test_material_id()


class TestRTXSensorAnnotator(omni.kit.test.AsyncTestCase):
    """Test class for RTX sensor annotators"""

    # This class is not meant to be run as a test, but rather to be used as a base class for other tests
    _assets_root_path = get_assets_root_path()
    _accumulate_returns = False

    async def setUp(self):
        """Setup test environment with a cube and lidar"""
        await create_new_stage_async()
        await update_stage_async()

        # Ordering octants in binary order, such that octant 0 is +++, octant 1 is ++-, etc. for XYZ.
        self._octant_dimensions = [
            (10, 10, 5),
            (10, 10, 7),
            (25, 25, 17),
            (25, 25, 19),
            (15, 15, 9),
            (15, 15, 11),
            (20, 20, 13),
            (20, 20, 15),
        ]
        create_sarcophagus(enable_nonvisual_material=False)

        self._timeline = omni.timeline.get_timeline_interface()
        self.hydra_texture = None
        self._isaac_create_rtx_lidar_scan_buffer_annotator = None
        self._isaac_compute_rtx_lidar_flat_scan_annotator = None
        self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_annotator = None
        self._isaac_create_rtx_lidar_scan_buffer_data = None
        self._isaac_compute_rtx_lidar_flat_scan_data = None
        self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data = None

    async def tearDown(self):
        self._timeline.stop()
        if self._isaac_create_rtx_lidar_scan_buffer_annotator:
            self._isaac_create_rtx_lidar_scan_buffer_annotator.detach()
        if self._isaac_compute_rtx_lidar_flat_scan_annotator:
            self._isaac_compute_rtx_lidar_flat_scan_annotator.detach()
        if self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_annotator:
            self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_annotator.detach()
        self.hydra_texture.destroy()
        self.hydra_texture = None
        await omni.kit.app.get_app().next_update_async()
        while omni.usd.get_context().get_stage_loading_status()[2] > 0:
            print("tearDown, assets still loading, waiting to finish...")
            await asyncio.sleep(1.0)
        await update_stage_async()

    async def _test_returns(
        self, az_vals: np.array, el_vals: np.array, r_vals: np.array, cartesian: bool = False
    ) -> None:
        """Tests sensor returns stored in GMO buffer against expected range, for a given set of azimuth and elevation values.

        Args:
            az_vals (np.array): azimuth values (degrees)
            el_vals (np.array): elevation values (degrees)
            r_vals (np.array): range values (meters)
            cartesian (bool): If True, assumes inpus are in Cartesian coordinates - az = x, el = y, r = z, all in meters. Default False.
        """
        # NOTE: if an element of unit_vecs is 0, indicating the return vector is parallel to the plane, the result of np.divide will be inf
        # Suppress the error
        np.seterr(divide="ignore")

        if not cartesian:
            # Get cartesian unit vectors from spherical coordinates
            azr = np.deg2rad(az_vals)
            elr = np.deg2rad(el_vals)
            x = np.multiply(np.cos(azr), np.cos(elr))
            y = np.multiply(np.sin(azr), np.cos(elr))
            z = np.sin(elr)
            unit_vecs = np.concatenate((x[..., None], y[..., None], z[..., None]), axis=1)
        else:
            unit_vecs = np.concatenate((az_vals[..., None], el_vals[..., None], r_vals[..., None]), axis=1)
            r_vals = np.linalg.norm(unit_vecs, axis=1)
            # Normalize unit vectors
            unit_vecs = np.divide(unit_vecs, np.repeat(r_vals[:, None], 3, axis=1))
            # Get spherical coordinates from cartesian unit vectors
            az_vals = np.arctan2(unit_vecs[:, 1], unit_vecs[:, 0])
            # el_vals = np.arcsin(unit_vecs[:, 2])
        # Get octant dimensions and indices
        octant = (unit_vecs[:, 0] < 0) * 4 + (unit_vecs[:, 1] < 0) * 2 + (unit_vecs[:, 2] < 0)
        dims = np.array([self._octant_dimensions[o] for o in octant])

        # Let alpha be the angle between the normal to the plane and the return vector
        # Let the distance from the origin of the return vector along the normal vector to the plane be l =  dims(idx)
        # Let expected range R be the distance along the return vector to the point of intersection with the plane
        # Then, cos(alpha) = l / R
        # Next, observe cos(alpha) = n-hat dot r-hat, where n-hat is the unit normal vector to the plane
        # and r-hat is the unit return vector
        # Therefore, R = l / (n-hat dot r-hat)
        # n-hat dot r-hat is simply the index of the unit return vector corresponding to the plane
        # This simplifies the computation of expected range to elementwise-division of the dimensions by the unit return vectors
        # The minimum of these values is the expected range to the first plane the return vector will intersect
        expected_range = np.min(np.divide(dims, np.abs(unit_vecs)), axis=1)

        if DEBUG_DRAW_PRINT:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection="3d")
            x_plot = np.multiply(unit_vecs[:, 0], r_vals)
            y_plot = np.multiply(unit_vecs[:, 1], r_vals)
            z_plot = np.multiply(unit_vecs[:, 2], r_vals)
            x_expected = np.multiply(unit_vecs[:, 0], expected_range)
            y_expected = np.multiply(unit_vecs[:, 1], expected_range)
            z_expected = np.multiply(unit_vecs[:, 2], expected_range)
            ax.scatter(x_plot, y_plot, z_plot, c="b")
            ax.scatter(x_expected, y_expected, z_expected, c="r")
            plt.savefig(f"test_returns_{self.fig_name}.png")
            plt.close()

        # Compute percent differences
        percent_diffs = np.divide(np.abs(expected_range - r_vals), expected_range)

        # Exclude returns that are within 0.5deg of an octant edge or corner
        near_edge = np.full(az_vals.shape, False)
        for excl_az in np.arange(-180, 181, 45):
            near_edge = np.logical_or(near_edge, np.abs(az_vals - excl_az) < 0.5)
        not_near_edge = np.logical_not(near_edge)

        # Compute the number of returns that exceed the threshold of 2%
        num_exceeding_threshold = np.sum(np.logical_and(percent_diffs > 2e-2, np.array(not_near_edge)))
        num_returns = np.size(az_vals)
        carb.log_warn(f"num_returns: {num_returns}")
        pct_exceeding_threshold = num_exceeding_threshold / num_returns * 100
        valid_threshold = 1.0 if num_returns >= 100 else 10.0
        self.assertLessEqual(
            pct_exceeding_threshold,
            valid_threshold,
            f"Expected fewer than 1% of returns to differ from expected range by more than 2%. {num_exceeding_threshold} of {num_returns} returns exceeded threshold.",
        )

    async def _test_isaac_compute_rtx_lidar_flat_scan_annotator_result(self):
        """Tests the annotator result."""

        # Test that all expected keys are present in the annotator data, then copy those values to the test class attributes
        for expected_key in [
            "azimuthRange",
            "depthRange",
            "horizontalFov",
            "horizontalResolution",
            "intensitiesData",
            "linearDepthData",
            "numCols",
            "numRows",
            "rotationRate",
        ]:
            self.assertIn(expected_key, self._isaac_compute_rtx_lidar_flat_scan_data)
            setattr(self, expected_key, self._isaac_compute_rtx_lidar_flat_scan_data[expected_key])

        # Confirm default values for 3D lidar
        if not self._is_2d_lidar:
            self.assertTrue(np.allclose(np.zeros([1, 2]), self.azimuthRange), f"azimuthRange: {self.azimuthRange}")
            self.assertTrue(np.allclose(np.zeros([1, 2]), self.depthRange), f"depthRange: {self.depthRange}")
            self.assertEqual(0.0, self.horizontalFov)
            self.assertEqual(0.0, self.horizontalResolution)
            self.assertEqual(0, self.intensitiesData.size)
            self.assertEqual(0, self.linearDepthData.size)
            self.assertEqual(0, self.numCols)
            self.assertEqual(1, self.numRows)
            self.assertEqual(0.0, self.rotationRate)
            return

        # Construct azimuth and elevation vectors, then test returns
        num_elements = self.numCols
        self.assertGreater(num_elements, 0, "Expecting more than zero elements in output.")
        azimuth_vals = np.linspace(self.azimuthRange[0], self.azimuthRange[1], num_elements)
        elevation_vals = np.zeros_like(azimuth_vals)
        # Remove any returns with range below threshold
        valid_returns = self.linearDepthData > 1e-3
        await self._test_returns(
            az_vals=azimuth_vals[valid_returns],
            el_vals=elevation_vals[valid_returns],
            r_vals=self.linearDepthData[valid_returns],
        )

    async def _test_isaac_extract_rtx_sensor_point_cloud_no_accumulator_annotator_result(self):
        """Tests the annotator result."""

        # Test that all expected keys are present in the annotator data, then copy those values to the test class attributes
        self.assertIn("data", self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data)
        self.data = self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data["data"]

        self.assertIn("info", self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data)
        for expected_key in [
            "transform",
        ]:
            self.assertIn(expected_key, self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data["info"])
            setattr(
                self, expected_key, self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data["info"][expected_key]
            )

        # Test data (cartesian)
        self.assertGreater(self.data.shape[0], 0, "Expected non-empty data.")
        self.assertEqual(self.data.shape[1], 3)
        await self._test_returns(self.data[:, 0], self.data[:, 1], self.data[:, 2], cartesian=True)

        return

    async def _test_isaac_create_rtx_lidar_scan_buffer_annotator_result(self):
        """Tests the annotator result."""

        # Test that all expected keys are present in the annotator data, then copy those values to the test class attributes
        for expected_key in [
            "azimuth",
            "beamId",
            "data",
            "distance",
            "elevation",
            "emitterId",
            "index",
            "intensity",
            "materialId",
            "normal",
            "objectId",
            "timestamp",
            "velocity",
        ]:
            self.assertIn(expected_key, self._isaac_create_rtx_lidar_scan_buffer_data)
            setattr(self, expected_key, self._isaac_create_rtx_lidar_scan_buffer_data[expected_key])

        self.assertIn("info", self._isaac_create_rtx_lidar_scan_buffer_data)
        for expected_key in [
            "numChannels",
            "numEchos",
            "numReturnsPerScan",
            "renderProductPath",
            "ticksPerScan",
            "transform",
            "azimuth",
            "beamId",
            "distance",
            "elevation",
            "emitterId",
            "index",
            "intensity",
            "materialId",
            "normal",
            "objectId",
            "timestamp",
            "velocity",
        ]:
            self.assertIn(expected_key, self._isaac_create_rtx_lidar_scan_buffer_data["info"])
            setattr(self, expected_key, self._isaac_create_rtx_lidar_scan_buffer_data["info"][expected_key])

        # Test data (cartesian)
        self.assertGreater(self.data.shape[0], 0, "Expected non-empty data.")
        self.assertEqual(self.data.shape[1], 3)
        await self._test_returns(self.data[:, 0], self.data[:, 1], self.data[:, 2], cartesian=True)

        return

    async def test_generic_model_output(self):
        from isaacsim.sensors.rtx import get_gmo_data

        # Create sensor prim
        kwargs = {
            "path": "lidar",
            "parent": None,
            "translation": Gf.Vec3d(0.0, 0.0, 0.0),
            "orientation": Gf.Quatd(1.0, 0.0, 0.0, 0.0),
            "config": "Example_Rotary",
            "omni:sensor:Core:outputFrameOfReference": "WORLD",
            "omni:sensor:Core:auxOutputType": "FULL",
        }
        _, self.sensor = omni.kit.commands.execute(f"IsaacSensorCreateRtxLidar", **kwargs)
        sensor_type = self.sensor.GetTypeName()
        self.assertEqual(
            sensor_type, "OmniLidar", f"Expected OmniLidar prim, got {sensor_type}. Was sensor prim created?"
        )
        self.assertEqual(
            self.sensor.GetAttribute("omni:sensor:Core:auxOutputType").Get(),
            "FULL",
            f"Expected auxOutputType to be FULL, got {self.sensor.GetAttribute('omni:sensor:Core:auxOutputType').Get()}",
        )

        # Create render product and attach to sensor
        self.hydra_texture = rep.create.render_product(
            self.sensor.GetPath(),
            [32, 32],
            name="RtxSensorRenderProduct",
            render_vars=["GenericModelOutput", "RtxSensorMetadata"],
        )
        # Attach annotator to render product
        self._annotator = rep.AnnotatorRegistry.get_annotator("GenericModelOutput")
        self._annotator.attach([self.hydra_texture.path])

        self._timeline.play()

        num_incorrect_magic_number_frames = 0
        num_zero_elements_frames = 0
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
            data = self._annotator.get_data()
            gmo = get_gmo_data(data)
            if gmo.magicNumber != 0x4E474D4F:
                num_incorrect_magic_number_frames += 1
                continue
            if gmo.numElements == 0:
                num_zero_elements_frames += 1
                continue
            else:
                # Try accessing all the fields of the GMO buffer
                self.assertIsNotNone(gmo.majorVersion)
                self.assertIsNotNone(gmo.minorVersion)
                self.assertIsNotNone(gmo.patchVersion)
                self.assertIsNotNone(gmo.sizeInBytes)
                self.assertIsNotNone(gmo.numElements)
                self.assertIsNotNone(gmo.frameId)
                self.assertIsNotNone(gmo.timestampNs)
                self.assertIsNotNone(gmo.frameOfReference)
                self.assertIsNotNone(gmo.motionCompensationState)
                self.assertIsNotNone(gmo.elementsCoordsType)
                self.assertIsNotNone(gmo.outputType)
                self.assertIsNotNone(gmo.frameStart)
                self.assertIsNotNone(gmo.frameEnd)
                self.assertIsNotNone(gmo.auxType)
                self.assertIsNotNone(gmo.timeOffSetNs)
                self.assertIsNotNone(gmo.x)
                self.assertIsNotNone(gmo.y)
                self.assertIsNotNone(gmo.z)
                self.assertIsNotNone(gmo.scalar)
                self.assertIsNotNone(gmo.flags)
                self.assertIsNotNone(gmo.scanComplete)
                self.assertIsNotNone(gmo.azimuthOffset)
                self.assertIsNotNone(gmo.emitterId)
                self.assertIsNotNone(gmo.channelId)
                self.assertIsNotNone(gmo.echoId)
                self.assertIsNotNone(gmo.matId)
                self.assertIsNotNone(gmo.objId)
                self.assertIsNotNone(gmo.tickId)
                self.assertIsNotNone(gmo.tickStates)
                self.assertIsNotNone(gmo.hitNormals)
                self.assertIsNotNone(gmo.velocities)

        NUM_MAX_FRAMES_WITH_INCORRECT_MAGIC_NUMBER = 5
        NUM_MAX_FRAMES_WITH_ZERO_ELEMENTS = 2
        self.assertLess(
            num_incorrect_magic_number_frames,
            NUM_MAX_FRAMES_WITH_INCORRECT_MAGIC_NUMBER,
            f"Expected fewer than {NUM_MAX_FRAMES_WITH_INCORRECT_MAGIC_NUMBER} frames with incorrect magic number.",
        )
        self.assertLess(
            num_zero_elements_frames,
            NUM_MAX_FRAMES_WITH_ZERO_ELEMENTS,
            f"Expected fewer than {NUM_MAX_FRAMES_WITH_ZERO_ELEMENTS} frame(s) with zero elements.",
        )


ETM_SKIP_LIST = []


def _create_flat_scan_annotator_test(config: str = None, variant: str = None):
    """Create OmniLidar prim with specified config and variants, then attach an annotator and run for several frames.

    Args:
        sensor_type (Literal[&quot;lidar&quot;, &quot;radar&quot;], optional): _description_. Defaults to "lidar".
        prim_type (Literal[&quot;sensor&quot;, &quot;camera&quot;], optional): _description_. Defaults to "sensor".
        config (str, optional): _description_. Defaults to None.
    """

    async def test_function(self):

        if os.getenv("ETM_ACTIVE") and f"{config}_{variant}" in ETM_SKIP_LIST:
            raise unittest.SkipTest("Skipping test in ETM.")

        self.fig_name = f"lidar_sensor_{config}_{variant}"

        # Create sensor prim
        kwargs = {
            "path": "/lidar",
            "parent": None,
            "translation": Gf.Vec3d(0.0, 0.0, 0.0),
            "orientation": Gf.Quatd(1.0, 0.0, 0.0, 0.0),
            "config": config,
            "variant": variant,
            "omni:sensor:Core:outputFrameOfReference": "WORLD",
        }
        _, self.sensor = omni.kit.commands.execute(f"IsaacSensorCreateRtxLidar", **kwargs)
        sensor_type = self.sensor.GetTypeName()
        self.assertEqual(
            sensor_type, "OmniLidar", f"Expected OmniLidar prim, got {sensor_type}. Was sensor prim created?"
        )

        # Create render product and attach to sensor
        self.hydra_texture = rep.create.render_product(
            self.sensor.GetPath(),
            [32, 32],
            name="RtxSensorRenderProduct",
            render_vars=["GenericModelOutput", "RtxSensorMetadata"],
        )
        # Attach annotators to render product
        self._isaac_create_rtx_lidar_scan_buffer_annotator = rep.AnnotatorRegistry.get_annotator(
            "IsaacCreateRTXLidarScanBufferForFlatScan"
        )
        self._isaac_compute_rtx_lidar_flat_scan_annotator = rep.AnnotatorRegistry.get_annotator(
            "IsaacComputeRTXLidarFlatScan"
        )

        self._isaac_create_rtx_lidar_scan_buffer_annotator.attach([self.hydra_texture.path])
        self._isaac_compute_rtx_lidar_flat_scan_annotator.attach([self.hydra_texture.path])

        # Test attributes of the sensor prim
        elevationDeg = self.sensor.GetAttribute("omni:sensor:Core:emitterState:s001:elevationDeg").Get()
        self._is_2d_lidar = all([abs(i) < 1e-3 for i in list(elevationDeg)])

        # Render to get annotator results
        await omni.kit.app.get_app().next_update_async()
        self._timeline.play()
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
            self._isaac_create_rtx_lidar_scan_buffer_data = (
                self._isaac_create_rtx_lidar_scan_buffer_annotator.get_data()
            )

            self._isaac_compute_rtx_lidar_flat_scan_data = self._isaac_compute_rtx_lidar_flat_scan_annotator.get_data()
            # print(f"self._isaac_create_rtx_lidar_scan_buffer_data: {self._isaac_create_rtx_lidar_scan_buffer_data}")
            # print(f"self._isaac_compute_rtx_lidar_flat_scan_data: {self._isaac_compute_rtx_lidar_flat_scan_data}")
            if (
                self._isaac_create_rtx_lidar_scan_buffer_data
                and "data" in self._isaac_create_rtx_lidar_scan_buffer_data
                and self._isaac_create_rtx_lidar_scan_buffer_data["data"].size > 0
            ):
                if not self._is_2d_lidar or (
                    self._isaac_compute_rtx_lidar_flat_scan_data
                    and "numCols" in self._isaac_compute_rtx_lidar_flat_scan_data
                    and self._isaac_compute_rtx_lidar_flat_scan_data["numCols"] > 0
                ):
                    break

        self._timeline.stop()

        await self._test_isaac_create_rtx_lidar_scan_buffer_annotator_result()
        await self._test_isaac_compute_rtx_lidar_flat_scan_annotator_result()

    return test_function


def _create_isaac_extract_rtx_sensor_point_cloud_test(config: str = None, variant: str = None):
    """Create OmniLidar prim with specified config and variants, then attach an IsaacExtractRTXSensorPointCloud annotator and run for several frames.

    Args:
        sensor_type (Literal[&quot;lidar&quot;, &quot;radar&quot;], optional): _description_. Defaults to "lidar".
        prim_type (Literal[&quot;sensor&quot;, &quot;camera&quot;], optional): _description_. Defaults to "sensor".
        config (str, optional): _description_. Defaults to None.
    """

    async def test_function(self):

        if os.getenv("ETM_ACTIVE") and f"{config}_{variant}" in ETM_SKIP_LIST:
            raise unittest.SkipTest("Skipping test in ETM.")

        self.fig_name = f"lidar_sensor_{config}_{variant}"

        # Create sensor prim
        kwargs = {
            "path": "lidar",
            "parent": None,
            "translation": Gf.Vec3d(0.0, 0.0, 0.0),
            "orientation": Gf.Quatd(1.0, 0.0, 0.0, 0.0),
            "config": config,
            "variant": variant,
            "omni:sensor:Core:outputFrameOfReference": "WORLD",
        }
        _, self.sensor = omni.kit.commands.execute(f"IsaacSensorCreateRtxLidar", **kwargs)
        sensor_type = self.sensor.GetTypeName()
        self.assertEqual(
            sensor_type, "OmniLidar", f"Expected OmniLidar prim, got {sensor_type}. Was sensor prim created?"
        )

        # Create render product and attach to sensor
        self.hydra_texture = rep.create.render_product(
            self.sensor.GetPath(),
            [32, 32],
            name="RtxSensorRenderProduct",
            render_vars=["GenericModelOutput", "RtxSensorMetadata"],
        )
        # Attach annotator to render product
        self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_annotator = rep.AnnotatorRegistry.get_annotator(
            "IsaacExtractRTXSensorPointCloudNoAccumulator"
        )
        self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_annotator.attach([self.hydra_texture.path])

        # Render to get annotator results
        await omni.kit.app.get_app().next_update_async()
        self._timeline.play()
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
            self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data = (
                self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_annotator.get_data()
            )
            if (
                self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data
                and "data" in self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data
                and self._isaac_extract_rtx_sensor_point_cloud_no_accumulator_data["data"].size > 0
            ):
                break

        self._timeline.stop()

        await self._test_isaac_extract_rtx_sensor_point_cloud_no_accumulator_annotator_result()

    return test_function


# Iterate over all supported lidar configs and variants, creating a test for each as sensor prims
data_source = "gpu"
for config_path in SUPPORTED_LIDAR_CONFIGS:
    config_name = Path(config_path).stem
    for variant in SUPPORTED_LIDAR_CONFIGS[config_path] or [None]:
        flat_scan_test_func = _create_flat_scan_annotator_test(config=config_name, variant=variant)
        flat_scan_test_name = f"lidar_sensor_flatscan_{config_name}_{variant}_{data_source}"
        flat_scan_test_func.__name__ = f"test_{flat_scan_test_name}"
        flat_scan_test_func.__doc__ = f"Test IsaacComputeRTXLidarFlatScan and IsaacCreateRTXLidarScanBuffer annotator results using OmniLidar prim, with config {config_name} and variant {variant} and data on {data_source.upper()}."
        setattr(TestRTXSensorAnnotator, flat_scan_test_func.__name__, flat_scan_test_func)

        pcna_test_func = _create_isaac_extract_rtx_sensor_point_cloud_test(config=config_name, variant=variant)
        pcna_test_name = f"lidar_sensor_pointcloud_{config_name}_{variant}_{data_source}"
        pcna_test_func.__name__ = f"test_{pcna_test_name}"
        pcna_test_func.__doc__ = f"Test IsaacExtractRTXSensorPointCloudNoAccumulator annotator results using OmniLidar prim, with config {config_name} and variant {variant} and data on {data_source.upper()}."
        setattr(TestRTXSensorAnnotator, pcna_test_func.__name__, pcna_test_func)
