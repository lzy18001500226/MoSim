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

import traceback
from typing import Dict

import carb
import cv2 as cv
import numpy as np
import omni
import omni.replicator.core as rep
import omni.syntheticdata
from isaacsim.core.nodes import BaseWriterNode
from isaacsim.ros2.bridge import collect_namespace, compute_relative_pose, read_camera_info
from pxr import Usd


class OgnROS2CameraInfoHelperInternalState(BaseWriterNode):
    def __init__(self):
        self.viewport = None
        self.viewport_name = ""
        self.rv = ""
        self.rvRight = ""
        self.resetSimulationTimeOnStop = False
        self.publishStepSize = 1

        super().__init__(initialize=False)

    def post_attach(self, writer, render_product):
        try:
            if self.rv != "":
                omni.syntheticdata.SyntheticData.Get().set_node_attributes(
                    self.rv + "IsaacSimulationGate", {"inputs:step": self.publishStepSize}, render_product
                )
            if self.rvRight != "":
                omni.syntheticdata.SyntheticData.Get().set_node_attributes(
                    self.rvRight + "IsaacSimulationGate", {"inputs:step": self.publishStepSize}, render_product
                )

            omni.syntheticdata.SyntheticData.Get().set_node_attributes(
                "IsaacReadSimulationTime", {"inputs:resetOnStop": self.resetSimulationTimeOnStop}, render_product
            )
        except:
            pass


class OgnROS2CameraInfoHelper:
    @staticmethod
    def internal_state():
        return OgnROS2CameraInfoHelperInternalState()

    @staticmethod
    def add_camera_info_writer(db, frameId, topicName, camera_info, render_product_path: str, time_type: str = ""):
        writer = rep.writers.get(f"ROS2{time_type}PublishCameraInfo")
        writer.initialize(
            frameId=frameId,
            nodeNamespace=collect_namespace(db.inputs.nodeNamespace, render_product_path),
            queueSize=db.inputs.queueSize,
            topicName=topicName,
            context=db.inputs.context,
            qosProfile=db.inputs.qosProfile,
            width=camera_info.width,
            height=camera_info.height,
            projectionType=camera_info.distortion_model,
            k=camera_info.k,
            r=camera_info.r,
            p=camera_info.p,
            physicalDistortionModel=camera_info.distortion_model,
            physicalDistortionCoefficients=camera_info.d,
        )
        db.per_instance_state.attach_writer(writer, render_product_path)
        return

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.enabled is False:
            if db.per_instance_state.initialized is False:
                return True
            else:
                db.per_instance_state.custom_reset()
                return True

        if db.per_instance_state.initialized is False:
            db.per_instance_state.initialized = True
            # Get stage reference
            stage = omni.usd.get_context().get_stage()

            with Usd.EditContext(stage, stage.GetSessionLayer()):

                is_stereo = False
                if not db.inputs.renderProductPath:
                    carb.log_warn(f"Render product {db.inputs.renderProductPath} not valid")
                    db.per_instance_state.initialized = False
                    return False
                if db.inputs.renderProductPathRight:
                    is_stereo = True

                db.per_instance_state.resetSimulationTimeOnStop = db.inputs.resetSimulationTimeOnStop
                db.per_instance_state.publishStepSize = db.inputs.frameSkipCount + 1

                time_type_input = ""
                if db.inputs.useSystemTime:
                    time_type_input = "SystemTime"
                    if db.inputs.resetSimulationTimeOnStop:
                        carb.log_warn("System timestamp is being used. Ignoring resetSimulationTimeOnStop input")

                camera_info_left, camera_left = read_camera_info(render_product_path=db.inputs.renderProductPath)

                if is_stereo:
                    camera_info_right, camera_right = read_camera_info(
                        render_product_path=db.inputs.renderProductPathRight
                    )

                    width_left = camera_info_left.width
                    height_left = camera_info_left.height
                    width_right = camera_info_right.width
                    height_right = camera_info_right.height
                    if width_left != width_right or height_left != height_right:
                        carb.log_warn(
                            f"Mismatched stereo camera resolutions: left = [{width_left}, {height_left}], right = [{width_right}, {height_right}]"
                        )
                        return False

                    distortion_model_left = camera_info_left.distortion_model
                    distortion_model_right = camera_info_right.distortion_model
                    if distortion_model_left != distortion_model_right:
                        carb.log_warn(
                            f"Mismatched stereo camera distortion models: left = {distortion_model_left}, right = {distortion_model_right}."
                        )
                        return False

                    translation, orientation = compute_relative_pose(
                        left_camera_prim=camera_left, right_camera_prim=camera_right
                    )

                    # Compute stereo rectification parameters
                    if distortion_model_left == "equidistant":
                        (
                            R1,
                            R2,
                            P1,
                            P2,
                            _,
                        ) = cv.fisheye.stereoRectify(
                            K1=np.reshape(camera_info_left.k, [3, 3]),
                            D1=np.array(camera_info_left.d),
                            K2=np.reshape(camera_info_right.k, [3, 3]),
                            D2=np.array(camera_info_right.d),
                            imageSize=(width_left, height_left),
                            R=orientation,
                            tvec=translation,
                            flags=cv.CALIB_ZERO_DISPARITY,
                        )
                    else:
                        R1, R2, P1, P2, _, _, _ = cv.stereoRectify(
                            cameraMatrix1=np.reshape(camera_info_left.k, [3, 3]),
                            distCoeffs1=np.array(camera_info_left.d),
                            cameraMatrix2=np.reshape(camera_info_right.k, [3, 3]),
                            distCoeffs2=np.array(camera_info_right.d),
                            imageSize=(width_left, height_left),
                            R=orientation,
                            T=translation,
                            flags=cv.CALIB_ZERO_DISPARITY,
                        )

                    camera_info_left.r = R1.ravel().tolist()
                    camera_info_right.r = R2.ravel().tolist()
                    camera_info_left.p = P1.ravel().tolist()
                    camera_info_right.p = P2.ravel().tolist()

                    # Create right-side writer
                    db.per_instance_state.rvRight = "PostProcessDispatchRight"
                    OgnROS2CameraInfoHelper.add_camera_info_writer(
                        db,
                        topicName=db.inputs.topicNameRight,
                        frameId=db.inputs.frameIdRight,
                        camera_info=camera_info_right,
                        render_product_path=db.inputs.renderProductPathRight,
                        time_type=time_type_input,
                    )

                # Create left-side writer
                db.per_instance_state.rv = "PostProcessDispatch"
                OgnROS2CameraInfoHelper.add_camera_info_writer(
                    db,
                    topicName=db.inputs.topicName,
                    frameId=db.inputs.frameId,
                    camera_info=camera_info_left,
                    render_product_path=db.inputs.renderProductPath,
                    time_type=time_type_input,
                )

        else:
            return True

    @staticmethod
    def release_instance(node, graph_instance_id):
        try:
            state = OgnROS2CameraInfoHelperInternalState.per_instance_internal_state(node)
        except Exception:
            state = None
            pass

        if state is not None:
            state.reset()
