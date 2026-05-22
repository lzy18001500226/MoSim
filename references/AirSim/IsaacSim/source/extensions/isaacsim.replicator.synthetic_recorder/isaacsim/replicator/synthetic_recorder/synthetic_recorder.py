# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
from enum import Enum

import carb.events
import carb.settings
import omni.kit.app
import omni.replicator.core as rep
import omni.timeline
import omni.usd
import Semantics
from pxr import UsdGeom, UsdSemantics, UsdSkel

# If both width and height are larger than this value, warn the user
MAX_RESOLUTION_WARN = 8000

# Large number to use as a default value when the recorder should run indefinitely
MAX_NUM_FRAMES = 100000000

# Annotators that require semantically labeled prims
SEMANTICS_ANNOTATORS = (
    "bounding_box_2d_tight",
    "bounding_box_2d_loose",
    "semantic_segmentation",
    "instance_id_segmentation",
    "instance_segmentation",
    "bounding_box_3d",
    "occlusion",
)


# Possible states of the recorder
class RecorderState(Enum):
    STOPPED = 0
    RUNNING = 1
    PAUSED = 2


class SyntheticRecorder:
    """Synthetic Data Recorder class handling the recording process."""

    def __init__(self):
        # Public -- modified by the UI
        self.num_frames = 0
        self.rt_subframes = 0
        self.control_timeline = False
        self.verbose = False
        self.writer_name = "BasicWriter"
        self.rp_data = []
        self.custom_writer_params = {}
        self.basic_writer_params = {
            "rgb": True,
            "bounding_box_2d_tight": False,
            "bounding_box_2d_loose": False,
            "semantic_segmentation": False,
            "colorize_semantic_segmentation": False,
            "instance_id_segmentation": False,
            "colorize_instance_id_segmentation": False,
            "instance_segmentation": False,
            "colorize_instance_segmentation": False,
            "distance_to_camera": False,
            "distance_to_image_plane": False,
            "bounding_box_3d": False,
            "occlusion": False,
            "normals": False,
            "motion_vectors": False,
            "camera_params": False,
            "pointcloud": False,
            "pointcloud_include_unlabelled": False,
            "skeleton_data": False,
        }
        self.out_dir = "_out_sdrec"
        self.out_working_dir = os.getcwd()
        self.use_s3 = False
        self.s3_params = {"s3_bucket": "", "s3_region": "", "s3_endpoint": ""}

        # Internal
        self._state = RecorderState.STOPPED
        self._state_subscribers = []
        self._writer = None
        self._current_frame = 0
        self._render_products = []
        self._original_capture_on_play = None

    def get_state(self):
        """Get the current state of the recorder."""
        return self._state

    def subscribe_state_changed(self, callback):
        """Subscribe to the recorder state changes."""
        self._state_subscribers.append(callback)

    def _notify_state_subscribers(self):
        """Notify the subscribers about the state change."""
        for callback in self._state_subscribers:
            callback()

    def _set_state(self, state):
        """Set the state of the recorder and notify any subscribers about the change."""
        self._state = state
        self._notify_state_subscribers()

    def init_recorder(self):
        """Initialize the recorder (create a new one) and attach the writer to the render products (newly created)."""
        if self._writer is None:
            try:
                self._writer = rep.WriterRegistry.get(self.writer_name)
            except Exception as e:
                print(f"[SDR][Warn] Could not create writer {self.writer_name}: {e}")
                return False

        # Store the original capture on play setting and disable it if necessary
        self._original_capture_on_play = carb.settings.get_settings().get("/omni/replicator/captureOnPlay")
        if self._original_capture_on_play:
            rep.orchestrator.set_capture_on_play(False)
            print("[SDR][Warn] Disabling replicator capture on play flag during recording.")

        writer_params = {}
        if self.writer_name == "BasicWriter":
            if self.use_s3:
                if not self.s3_params.get("s3_bucket", None):
                    print("[SDR][Warn] Could not initialize writer, s3_bucket parameter is missing.")
                    return False
                for key, value in self.s3_params.items():
                    if value == "":
                        self.s3_params[key] = None
                writer_params = {**self.basic_writer_params, **self.s3_params}
            else:
                writer_params = {**self.basic_writer_params}

            # If the stage is not semantically labeled, disable any semantics related annotators
            stage_is_labeled = self._check_if_stage_is_semantically_labeled()
            if not stage_is_labeled:
                print(
                    "[SDR][Warn] Stage is not semantically labeled, semantics related annotators will not work, removing them."
                )
                self._disable_semantics_annotators(writer_params)

            # If the stage does not have any skeleton prims, disable the skeleton_data annotator
            if writer_params.get("skeleton_data", False) and not self._check_if_stage_has_skeleton_prims():
                print(f"[SDR][Warn] Stage does not have any skeleton prims, disabling skeleton annotator.")
                writer_params["skeleton_data"] = False
        else:
            # If a custom writer is used instead of the BasicWriter, load the given custom parameters
            writer_params = {**self.custom_writer_params}

        if self.use_s3:
            output_dir = self.out_dir
        else:
            output_dir = os.path.join(self.out_working_dir, self.out_dir)
        try:
            self._writer.initialize(output_dir=output_dir, **writer_params)
        except Exception as e:
            print(f"[SDR][Warn] Could not initialize writer {self.writer_name}: {e}")
            return False

        for rp_entry in self.rp_data:
            if not self._check_if_valid_rp_entry(rp_entry):
                print(f"[SDR][Warn] Invalid render product entry {rp_entry}.")
                continue
            camera_path = rp_entry[0]
            resolution = (rp_entry[1], rp_entry[2])
            custom_name = rp_entry[3] if rp_entry[3] else None
            rp = rep.create.render_product(camera_path, resolution, name=custom_name, force_new=True)
            self._render_products.append(rp)

        if not self._render_products:
            print(f"[SDR][Warn] No valid render products found to initialize the writer.")
            return False

        try:
            self._writer.attach(self._render_products)
        except Exception as e:
            print(f"[SDR][Warn] Could not attach render products to writer: {e}")
            return False

        if self.verbose:
            print(f"[SDR][Recorder] Initialized.")

        return True

    def clear_recorder(self):
        """Clear the recorder state, detach the writer, and destroy the render products."""
        if self._state != RecorderState.STOPPED:
            self._set_state(RecorderState.STOPPED)
        self._current_frame = 0
        if self._writer:
            self._writer.detach()
            self._writer = None
        for rp in self._render_products:
            rp.destroy()
        self._render_products.clear()

        # Reset the capture on play flag to its original value
        if self._original_capture_on_play is not None:
            rep.orchestrator.set_capture_on_play(self._original_capture_on_play)
            if self._original_capture_on_play:
                print(f"[SDR][Warn] Re-enabled replicator capture on play flag after recording.")
            self._original_capture_on_play = None

    async def start_stop_async(self):
        """Start or stop the recording loop."""
        timeline = omni.timeline.get_timeline_interface()
        if self._state == RecorderState.STOPPED and self.init_recorder():
            # Start recording if the state is STOPPED and init_recorder() was successful
            if self.verbose:
                print(
                    f"[SDR][Recorder] Start;\tFrame: {self._current_frame};\tTime: {timeline.get_current_time():.4f}."
                )
            self._set_state(RecorderState.RUNNING)
            if self.control_timeline and not timeline.is_playing():
                if self.verbose:
                    print(f"[SDR][ControlTimeline] Start Recording; Timeline is not playing. Starting it.")
                timeline.play()
                timeline.commit()
            # Start the recording loop with the specified number of frames (or run indefinitely == MAX_NUM_FRAMES)
            num_frames = self.num_frames if self.num_frames > 0 else MAX_NUM_FRAMES
            await self._run_recording_loop_async(num_frames)
        else:
            # Stop the recording if the state is RUNNING or PAUSED
            if self.verbose:
                print(f"[SDR] Stop;\tFrame: {self._current_frame};\tTime: {timeline.get_current_time():.4f}.")
            if self.rt_subframes > 0:
                rep.orchestrator.stop()
            self._set_state(RecorderState.STOPPED)
            await self._finish_recording_async()

    async def pause_resume_async(self):
        """Pause or resume the recording loop."""
        timeline = omni.timeline.get_timeline_interface()
        if self._state == RecorderState.RUNNING:
            if self.verbose:
                print(
                    f"[SDR][Recorder] Pause;\tFrame: {self._current_frame};\tTime: {timeline.get_current_time():.4f}."
                )
            if self.rt_subframes > 0:
                rep.orchestrator.pause()
            self._set_state(RecorderState.PAUSED)
            if self.control_timeline and timeline.is_playing():
                if self.verbose:
                    print(f"[SDR][ControlTimeline] Pausing Recording; Timeline is playing. Pausing it.")
                timeline.pause()
                timeline.commit()
        elif self._state == RecorderState.PAUSED:
            if self.verbose:
                print(
                    f"[SDR][Recorder] Resume;\tFrame: {self._current_frame};\tTime: {timeline.get_current_time():.4f}."
                )
            self._set_state(RecorderState.RUNNING)
            if self.control_timeline and not timeline.is_playing():
                if self.verbose:
                    print(f"[SDR][ControlTimeline] Resuming Recording; Timeline is not playing. Starting it.")
                timeline.play()
                timeline.commit()
            # Resume the recording loop (internal frame counter will continue from the last frame)
            num_frames = self.num_frames if self.num_frames > 0 else MAX_NUM_FRAMES
            await self._run_recording_loop_async(num_frames)
        else:
            print(f"[SDR][Warn] Recorder is in an unexpected state ({self._state.name}), try again.")

    def _check_if_valid_camera(self, path):
        """Check if the camera path is valid for the render product."""
        context = omni.usd.get_context()
        stage = context.get_stage()
        prim = stage.GetPrimAtPath(path)

        if not prim.IsValid():
            print(f"[SDR][Warn] {path} is not a valid prim path.")
            return False

        if UsdGeom.Camera(prim):
            return True
        else:
            print(f"[SDR][Warn] {prim.GetPath()} is not a valid 'Camera' type.")
            return False

    def _check_if_valid_resolution(self, width, height):
        """Check if the resolution is valid for the render product."""
        if width > 0 and height > 0:
            if width > MAX_RESOLUTION_WARN and height > MAX_RESOLUTION_WARN:
                print(f"[SDR][Warn] Using a large resolution {width}x{height} might lead to out of memory issues.")
            return True
        else:
            print(f"[SDR][Warn] Invalid resolution: {width}x{height}. Width and height must be larger than 0.")
        return False

    def _check_if_valid_rp_entry(self, entry):
        """Check if the render product entry is valid."""
        return (
            len(entry) == 4  # (camera path, width, height, custom name="")
            and self._check_if_valid_camera(entry[0])
            and self._check_if_valid_resolution(entry[1], entry[2])
        )

    def _check_if_stage_is_semantically_labeled(self):
        """Check if the stage has any semantically labeled prims."""
        stage = omni.usd.get_context().get_stage()
        for prim in stage.Traverse():
            # Check the new semantics API
            if prim.HasAPI(UsdSemantics.LabelsAPI):
                return True
            # Check the old semantics API
            if prim.HasAPI(Semantics.SemanticsAPI):
                return True
        return False

    def _check_if_stage_has_skeleton_prims(self):
        """Check if the stage has any skeleton prims."""
        stage = omni.usd.get_context().get_stage()
        for prim in stage.Traverse():
            if prim.IsA(UsdSkel.Skeleton):
                return True
        return False

    def _disable_semantics_annotators(self, writer_params):
        """Disable semantics related annotators if the stage does not have semantically labeled prims."""
        # Store the annotators that were disabled due to the stage not having semantically labeled prims
        disabled_annotators = []
        # Iterate over the semantics related annotators and disable them if they are enabled
        for annotator in SEMANTICS_ANNOTATORS:
            # Check if the annotator is in the writer parameters and if it is enabled
            if annotator in writer_params and writer_params[annotator]:
                writer_params[annotator] = False
                disabled_annotators.append(annotator)
        if disabled_annotators:
            print(f"[SDR][Warn] Disabled the following semantics related annotators: {disabled_annotators}.")

    async def _run_recording_loop_async(self, num_frames):
        """Run the recording loop for the specified number of frames."""
        timeline = omni.timeline.get_timeline_interface()
        while self._current_frame < num_frames:
            # Stop the recording loop if the state has been changed from RUNNING to PAUSED or STOPPED
            if self._state != RecorderState.RUNNING:
                break
            # Make sure the timeline is playing if Control Timeline is enabled
            if self.control_timeline and not timeline.is_playing():
                if self.verbose:
                    print(f"[SDR][ControlTimeline] Recording; Timeline is not playing. Starting it.")
                timeline.play()
                timeline.commit()
            if self.verbose:
                print(f"[SDR][Capture] Frame: {self._current_frame};\tTime: {timeline.get_current_time():.4f};")
            await rep.orchestrator.step_async(rt_subframes=self.rt_subframes, delta_time=None, pause_timeline=False)
            self._current_frame += 1

        # The recording loop has finished change the state to STOPPED
        if self._state == RecorderState.RUNNING:
            self._set_state(RecorderState.STOPPED)
            await self._finish_recording_async()

    async def _finish_recording_async(self):
        """Finish the recording and wait until the data is complete."""
        timeline = omni.timeline.get_timeline_interface()
        # If the timeline should be controlled by the recorder and it is running, stop it
        if self.control_timeline and timeline.is_playing():
            if self.verbose:
                print(f"[SDR][ControlTimeline] Finishing Recording; Timeline is playing. Stopping it.")
            timeline.stop()
            timeline.commit()
        await rep.orchestrator.wait_until_complete_async()
        if self.verbose:
            print(f"[SDR][Recorder] Finished;\tData written to: {os.path.join(self.out_working_dir, self.out_dir)}.")
        self.clear_recorder()
