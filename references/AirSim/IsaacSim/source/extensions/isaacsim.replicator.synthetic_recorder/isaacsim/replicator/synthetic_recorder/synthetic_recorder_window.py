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

import asyncio
import json
import os
from functools import lru_cache

import carb
import omni.kit.app
import omni.ui as ui
import omni.usd
from omni.kit.menu.utils import MenuHelperWindow
from omni.kit.viewport.utility import get_active_viewport
from omni.kit.window.extensions.utils import open_file_using_os_default

from .synthetic_recorder import RecorderState, SyntheticRecorder

PARAM_TOOLTIPS = {
    "rgb": (
        "Produces an array of type np.uint8 with shape (width, height, 4), "
        "where the four channels correspond to R,G,B,A."
    ),
    "bounding_box_2d_tight": (
        "Outputs tight 2d bounding box of each entity with semantics in the camera's viewport.\n"
        "Tight bounding boxes bound only the visible pixels of entities.\n"
        "Completely occluded entities are omitted.\n"
        "Bounds only visible pixels."
    ),
    "bounding_box_2d_loose": (
        "Outputs loose 2d bounding box of each entity with semantics in the camera's field of view.\n"
        "Loose bounding boxes bound the entire entity regardless of occlusions.\n"
        "Will produce the loose 2d bounding box of any prim in the viewport, no matter if it is partially occluded or fully occluded."
    ),
    "semantic_segmentation": (
        "Outputs semantic segmentation of each entity in the camera's viewport that has semantic labels.\n"
        "If colorize is set to True (mapping from color to semantic labels), the image will be a 2d array of types np.uint8 with 4 channels.\n"
        "If colorize is set to False (mapping from semantic id to semantic labels), the image will be a 2d array of types np.uint32 with 1 channel, which is the semantic id of the entities."
    ),
    "colorize_semantic_segmentation": (
        "If True, semantic segmentation is converted to an image where semantic ids are mapped to colors and saved as a uint8 4 channel PNG image.\n"
        "If False, the output is saved as a uint32 PNG image."
    ),
    "instance_id_segmentation": (
        "Outputs instance id segmentation of each entity in the camera's viewport.\n"
        "The instance id is unique for each prim in the scene with different paths.\n"
        "If colorize is set to True (mapping from color to usd prim path of that entity), the image will be a 2d array of types np.uint8 with 4 channels.\n"
        "If colorize is set to False (mapping from instance id to usd prim path of that entity), the image will be a 2d array of types np.uint32 with 1 channel, which is the instance id of the entities."
    ),
    "colorize_instance_id_segmentation": (
        "If True, instance id segmentation is converted to an image where instance ids are mapped to colors and saved as a uint8 4 channel PNG image.\n"
        "If False, the output is saved as a uint32 PNG image."
    ),
    "instance_segmentation": (
        "Outputs instance segmentation of each entity in the camera's viewport.\n"
        "The main difference between instance id segmentation and instance segmentation is that instance segmentation annotator goes down the hierarchy to the lowest level prim which has semantic labels,\n"
        "whereas instance id segmentation always goes down to the leaf prim."
    ),
    "colorize_instance_segmentation": (
        "If True, instance segmentation is converted to an image where instances are mapped to colors and saved as a uint8 4 channel PNG image.\n"
        "If False, the output is saved as a uint32 PNG image."
    ),
    "distance_to_camera": (
        "Outputs a depth map from objects to camera positions.\n"
        "Produces a 2d array of type np.float32 with 1 channel."
    ),
    "distance_to_image_plane": (
        "Outputs a depth map from objects to the image plane of the camera.\n"
        "Produces a 2d array of type np.float32 with 1 channel."
    ),
    "bounding_box_3d": (
        "Outputs 3D bounding box of each entity with semantics in the camera's viewport, generated regardless of occlusion."
    ),
    "occlusion": (
        "Outputs the occlusion of each entity in the camera's viewport.\n"
        "Contains the instanceId, semanticId, and the occlusionRatio."
    ),
    "normals": (
        "Produces an array of type np.float32 with shape (height, width, 4).\n"
        "The first three channels correspond to (x, y, z).\n"
        "The fourth channel is unused."
    ),
    "motion_vectors": (
        "Outputs a 2D array of motion vectors representing the relative motion of a pixel in the camera's viewport between frames.\n"
        "Produces a 2d array of type np.float32 with 4 channels.\n"
        "Each value is a normalized direction in 3D space.\n"
        "The values represent motion relative to camera space."
    ),
    "camera_params": (
        "Outputs the camera model (pinhole or fisheye models), view matrix, projection matrix, fisheye nominal width/height, fisheye optical centre, fisheye maximum field of view, fisheye polynomial, near/far clipping range."
    ),
    "pointcloud": (
        "Outputs a 2D array of shape (N, 3) representing the points sampled on the surface of the prims in the viewport, where N is the number of points.\n"
        "Point positions are in the world space.\n"
        "Sample resolution is determined by the resolution of the render product.\n"
        "To get the mapping from semantic id to semantic labels, pointcloud annotator is better used with semantic segmentation annotator, and users can extract the idToLabels data from the semantic segmentation annotator."
    ),
    "pointcloud_include_unlabelled": (
        "If True, pointcloud annotator will capture any prim in the camera's perspective, no matter if it has semantics or not.\n"
        "If False, only prims with semantics will be captured."
    ),
    "skeleton_data": ("Retrieves skeleton data given skeleton prims and camera parameters"),
    "s3_bucket": (
        "The S3 Bucket name to write to. If not provided, disk backend will be used instead.\n"
        "This backend requires that AWS credentials are set up in ~/.aws/credentials."
    ),
    "s3_region": ("If provided, this is the region the S3 bucket will be set to. Default: us-east-1"),
    "s3_endpoint": ("Gateway endpoint for Amazon S3"),
}


@lru_cache()
def _ui_get_delete_glyph():
    return ui.get_custom_glyph_code("${glyphs}/menu_delete.svg")


@lru_cache()
def _ui_get_open_folder_glyph():
    return ui.get_custom_glyph_code("${glyphs}/folder_open.svg")


@lru_cache()
def _ui_get_reset_glyph():
    return ui.get_custom_glyph_code("${glyphs}/menu_refresh.svg")


class SyntheticRecorderWindow(MenuHelperWindow):
    """Synthetic Recorder UI window."""

    def __init__(self, title, ext_id):
        self._ext_id = ext_id
        # Create the window
        super().__init__(title, verbose=False)
        self.deferred_dock_in("Property")

        # Recorder
        self._recorder = None

        # UI frame collapsed states
        self._writer_frame_collapsed = False
        self._writer_params_frame_collapsed = True
        self._rp_frame_collapsed = False
        self._output_frame_collapsed = False
        self._s3_params_frame_collapsed = True
        self._config_frame_collapsed = True
        self._control_frame_collapsed = False
        self._control_params_frame_collapsed = False

        # UI buttons
        self._start_stop_button = None
        self._pause_resume_button = None

        # Create the recorder with the default values
        self._recorder = SyntheticRecorder()
        self._recorder.num_frames = 0
        self._recorder.rt_subframes = 0
        self._recorder.control_timeline = False
        self._recorder.verbose = False
        self._recorder.writer_name = "BasicWriter"
        self._recorder.out_dir = "_out_sdrec"
        self._recorder.out_working_dir = os.getcwd()
        self._recorder.use_s3 = False
        self._recorder.s3_params = {"s3_bucket": "", "s3_region": "", "s3_endpoint": ""}
        self._recorder.basic_writer_params = {
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
        self._recorder.rp_data = [["/OmniverseKit_Persp", 512, 512, ""]]

        # Overwrite parmaters with custom config files if available
        self._config_dir = os.path.abspath(
            os.path.join(
                omni.kit.app.get_app().get_extension_manager().get_extension_path(self._ext_id),
                "data",
                "",
            )
        )
        self._last_config_path = os.path.join(self._config_dir, "last_config.json")
        self._custom_params_path = ""
        self._custom_writer_name = "MyCustomWriter"
        self._config_file = "custom_config.json"

        # Load the last config file if it exists, otherwise load the default config file
        if os.path.isfile(self._last_config_path):
            self._load_config(self._last_config_path)
        else:
            self._load_config(os.path.join(self._config_dir, "default_config.json"))

        # Listen to stage closing event to stop the recorder
        self._sub_stage_event = (
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop_by_type(int(omni.usd.StageEventType.CLOSING), self._on_stage_closing_event)
        )

        # Listen to editor quit event to stop the recorder, and save the last config file
        self._sub_shutdown = (
            omni.kit.app.get_app()
            .get_shutdown_event_stream()
            .create_subscription_to_pop_by_type(
                omni.kit.app.POST_QUIT_EVENT_TYPE,
                self._on_editor_quit_event,
                name="isaacsim.replicator.synthetic_recorder::shutdown_callback",
                order=0,
            )
        )

        # Build the window UI
        self._build_window_ui()

        # Subscribe to the recorder state change event to update the buttons state accordingly
        self._recorder.subscribe_state_changed(self._on_state_changed)

    def destroy(self):
        """
        overwriting the destroy method to clean up the window
        """
        self._recorder.clear_recorder()
        self._save_config(self._last_config_path)
        self._sub_stage_event = None
        self._sub_shutdown = None
        self._start_stop_button = None
        self._pause_resume_button = None
        self._recorder = None
        super().destroy()

    def _on_stage_closing_event(self, e: carb.events.IEvent):
        """Callback function for stage closing event."""
        self._recorder.clear_recorder()

    def _on_editor_quit_event(self, e: carb.events.IEvent):
        """Callback function for editor quit event."""
        self._recorder.clear_recorder()
        self._save_config(self._last_config_path)

    def _open_dir(self, path):
        """Open the directory through the editor."""
        if not os.path.isdir(path):
            carb.log_warn(f"Could not open directory {path}.")
            return
        open_file_using_os_default(path)

    def _load_config(self, path):
        """Load the json config file and set the recorder parameters."""
        if not os.path.isfile(path):
            carb.log_warn(f"Could not find config file: '{path}'.")
            return

        if os.path.getsize(path) == 0:
            carb.log_warn(f"Config file '{path}' is empty.")
            return

        try:
            with open(path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            carb.log_warn(f"Could not parse JSON in config file: '{path}', exception: {e}")
            return
        except Exception as e:
            carb.log_warn(f"An error occurred while reading '{path}': {e}")
            return

        # Recorder params
        if self._recorder is None:
            carb.log_warn("Recorder is not initialized.")
            return
        self._recorder.writer_name = config.get("writer_name", self._recorder.writer_name)
        self._recorder.num_frames = config.get("num_frames", self._recorder.num_frames)
        self._recorder.rt_subframes = config.get("rt_subframes", self._recorder.rt_subframes)
        self._recorder.control_timeline = config.get("control_timeline", self._recorder.control_timeline)
        self._recorder.out_working_dir = config.get("out_working_dir", self._recorder.out_working_dir)
        self._recorder.out_dir = config.get("out_dir", self._recorder.out_dir)
        self._recorder.use_s3 = config.get("use_s3", self._recorder.use_s3)

        basic_writer_params = config.get("basic_writer_params")
        if isinstance(basic_writer_params, dict):
            for key, value in basic_writer_params.items():
                if key in self._recorder.basic_writer_params:
                    self._recorder.basic_writer_params[key] = value

        rp_data = config.get("rp_data")
        if isinstance(rp_data, list):
            self._recorder.rp_data = rp_data
            for rp in self._recorder.rp_data:
                if len(rp) == 3:
                    rp.append("")  # If no custom name provided, set it to an empty string

        # UI params
        self._config_file = config.get("config_file", self._config_file)
        self._custom_params_path = config.get("custom_params_path", self._custom_params_path)
        self._custom_writer_name = config.get("custom_writer_name", self._custom_writer_name)

    def _load_config_and_refresh_ui(self, directory, filename):
        """Load the config file and refresh the UI to reflect the changes."""
        self._load_config(os.path.join(directory, filename))
        asyncio.ensure_future(self._build_window_ui_async())

    def _save_config(self, path):
        """Save the current recorder parameters to a json config file."""
        dir_name = os.path.dirname(path)
        if not dir_name:
            carb.log_warn(f"Could not save config file to '{path}', missing directory path.")
            return
        os.makedirs(dir_name, exist_ok=True)
        if os.path.isfile(path):
            carb.log_info(f"Overwriting config file '{path}'.")
        try:
            with open(path, "w") as json_file:
                # Recorder
                config = {
                    "num_frames": self._recorder.num_frames,
                    "rt_subframes": self._recorder.rt_subframes,
                    "control_timeline": self._recorder.control_timeline,
                    "use_s3": self._recorder.use_s3,
                    "s3_params": self._recorder.s3_params,
                    "basic_writer_params": self._recorder.basic_writer_params,
                    "rp_data": self._recorder.rp_data,
                }
                if self._recorder.writer_name:
                    config["writer_name"] = self._recorder.writer_name
                if self._recorder.out_working_dir:
                    config["out_working_dir"] = self._recorder.out_working_dir
                if self._recorder.out_dir:
                    config["out_dir"] = self._recorder.out_dir

                # UI
                if self._custom_writer_name:
                    config["custom_writer_name"] = self._custom_writer_name
                if self._config_file:
                    config["config_file"] = self._config_file
                if self._custom_params_path:
                    config["custom_params_path"] = self._custom_params_path

                json.dump(config, json_file, indent=4)

        except Exception as e:
            carb.log_warn(f"An error occurred while saving the config file '{path}': {e}")

    def _get_custom_params(self, path):
        """Load the custom writer parameters as a dict from the given json file."""
        if not os.path.isfile(path):
            carb.log_warn(f"Could not find params file '{path}'.")
            return {}
        try:
            with open(path, "r") as f:
                params = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            carb.log_warn(f"Error reading '{path}': {e}")
            return {}
        if not isinstance(params, dict):
            carb.log_warn(f"The file '{path}' does not contain a valid dictionary.")
            return {}

        return params

    def _reset_config_dir(self):
        self._config_dir = os.path.abspath(
            os.path.join(
                omni.kit.app.get_app().get_extension_manager().get_extension_path(self._ext_id),
                "data",
                "",
            )
        )
        asyncio.ensure_future(self._build_window_ui_async())

    def _reset_out_working_dir(self):
        """Reset the working directory to the default value."""
        self._recorder.out_working_dir = os.getcwd()
        asyncio.ensure_future(self._build_window_ui_async())

    def _set_buttons_state(self):
        """Set the state of the start/stop and pause/resume buttons based on the recorder state."""
        if self._recorder.get_state() == RecorderState.STOPPED:
            self._start_stop_button.text = "Start"
            self._pause_resume_button.text = "Pause"
            self._start_stop_button.enabled = True
            self._pause_resume_button.enabled = False
        elif self._recorder.get_state() == RecorderState.RUNNING:
            self._start_stop_button.text = "Stop"
            self._pause_resume_button.text = "Pause"
            self._start_stop_button.enabled = True
            self._pause_resume_button.enabled = True
        elif self._recorder.get_state() == RecorderState.PAUSED:
            self._start_stop_button.text = "Stop"
            self._pause_resume_button.text = "Resume"
            self._start_stop_button.enabled = True
            self._pause_resume_button.enabled = True

    def _start_stop_recorder(self):
        """Start/stop the recorder, load custom writer params if the writer is a custom writer."""
        # If the writer is a custom writer, load the custom parameters from the given json config file
        if self._recorder.writer_name != "BasicWriter":
            self._recorder.custom_writer_params = self._get_custom_params(self._custom_params_path)
        asyncio.ensure_future(self._recorder.start_stop_async())

    def _pause_resume_recorder(self):
        """Pause/resume the recorder."""
        asyncio.ensure_future(self._recorder.pause_resume_async())

    def _on_state_changed(self):
        """Callback function when the recorder state changes (finished/running/paused) to update the buttons state."""
        self._set_buttons_state()

    def _build_config_ui(self):
        """Build the config part of the UI."""
        with ui.VStack(spacing=5):
            with ui.HStack():
                ui.Spacer(width=10)
                ui.Label("Config Directory", tooltip="Config files directory path")
            with ui.HStack():
                ui.Spacer(width=10)
                config_dir_model = ui.StringField(read_only=False).model
                config_dir_model.set_value(self._config_dir)

                def config_dir_changed(model):
                    self._config_dir = model.as_string

                config_dir_model.add_value_changed_fn(config_dir_changed)

                ui.Spacer(width=5)
                ui.Button(
                    f"{_ui_get_open_folder_glyph()}",
                    width=20,
                    clicked_fn=lambda: self._open_dir(self._config_dir),
                    tooltip="Open config directory",
                )

                ui.Button(
                    f"{_ui_get_reset_glyph()}",
                    width=20,
                    clicked_fn=lambda: self._reset_config_dir(),
                    tooltip="Reset config directory to default",
                )

            with ui.HStack(spacing=5):
                ui.Spacer(width=5)
                config_file_model = ui.StringField(tooltip="Config file name").model
                config_file_model.set_value(self._config_file)

                def config_file_changed(model):
                    self._config_file = model.as_string

                config_file_model.add_value_changed_fn(config_file_changed)

                ui.Button(
                    "Load",
                    clicked_fn=lambda: self._load_config_and_refresh_ui(self._config_dir, self._config_file),
                    tooltip="Load and apply selected config file",
                )
                ui.Button(
                    "Save",
                    clicked_fn=lambda: self._save_config(os.path.join(self._config_dir, self._config_file)),
                    tooltip="Save current config to selected file",
                )

    def _build_s3_ui(self):
        """Build the S3 part of the UI."""
        with ui.VStack(spacing=5):
            with ui.HStack():
                ui.Spacer(width=10)
                ui.Label("Use S3", alignment=ui.Alignment.LEFT, tooltip="Write data to S3 buckets")
                s3_model = ui.CheckBox().model
                s3_model.set_value(self._recorder.use_s3)

                def value_changed(m):
                    self._recorder.use_s3 = m.as_bool

                s3_model.add_value_changed_fn(value_changed)

            for key, val in self._recorder.s3_params.items():
                with ui.HStack():
                    ui.Spacer(width=10)
                    ui.Label(key, alignment=ui.Alignment.LEFT, tooltip=PARAM_TOOLTIPS[key])
                    model = ui.StringField().model
                    if val:
                        model.set_value(val)
                    else:
                        model.set_value("")

                    def value_changed(m, k=key):
                        self._recorder.s3_params[k] = m.as_string

                    model.add_value_changed_fn(value_changed)

    def _build_output_ui(self):
        """Build the output part of the UI."""
        with ui.VStack(spacing=5):
            with ui.HStack():
                ui.Spacer(width=10)
                ui.Label("Working Directory")
            with ui.HStack():
                ui.Spacer(width=10)
                out_working_dir_model = ui.StringField().model
                out_working_dir_model.set_value(self._recorder.out_working_dir)

                def out_working_dir_changed(model):
                    self._recorder.out_working_dir = model.as_string

                out_working_dir_model.add_value_changed_fn(out_working_dir_changed)

                ui.Spacer(width=5)
                ui.Button(
                    f"{_ui_get_open_folder_glyph()}",
                    width=20,
                    clicked_fn=lambda: self._open_dir(self._recorder.out_working_dir),
                    tooltip="Open working directory",
                )

                ui.Button(
                    f"{_ui_get_reset_glyph()}",
                    width=20,
                    clicked_fn=lambda: self._reset_out_working_dir(),
                    tooltip="Reset directory to default",
                )

            with ui.HStack(spacing=5):
                ui.Spacer(width=5)
                out_dir_model = ui.StringField().model
                out_dir_model.set_value(self._recorder.out_dir)

                def out_dir_changed(model):
                    self._recorder.out_dir = model.as_string

                out_dir_model.add_value_changed_fn(out_dir_changed)

            s3_frame = ui.CollapsableFrame("S3 Bucket", height=0, collapsed=self._s3_params_frame_collapsed)
            with s3_frame:

                def on_collapsed_changed(collapsed):
                    self._s3_params_frame_collapsed = collapsed

                s3_frame.set_collapsed_changed_fn(on_collapsed_changed)
                self._build_s3_ui()

    def _update_rp_entry(self, idx, field, value):
        """Callback function to update the render product entry."""
        self._recorder.rp_data[idx][field] = value

    def _remove_rp_entry(self, idx):
        """Callback function to remove the render product entry."""
        del self._recorder.rp_data[idx]
        asyncio.ensure_future(self._build_window_ui_async())

    def _add_new_rp_field(self):
        """Add a new UI render product entry."""
        context = omni.usd.get_context()
        stage = context.get_stage()
        selected_prims = context.get_selection().get_selected_prim_paths()
        selected_cameras = [path for path in selected_prims if stage.GetPrimAtPath(path).GetTypeName() == "Camera"]

        if selected_cameras:
            for path in selected_cameras:
                self._recorder.rp_data.append([path, 512, 512, ""])
        else:
            active_vp = get_active_viewport()
            active_cam = active_vp.get_active_camera()
            self._recorder.rp_data.append([str(active_cam), 512, 512, ""])
        asyncio.ensure_future(self._build_window_ui_async())

    def _build_rp_ui(self):
        """Build the render product part of the UI."""
        with ui.VStack(spacing=5):
            with ui.HStack(spacing=5):
                ui.Spacer(width=15)
                ui.Label("Camera Path", width=200, tooltip="Camera prim to be used as a render product")
                ui.Spacer(width=10)
                ui.Label("X", tooltip="X resolution of the render product")
                ui.Spacer(width=0)
                ui.Label("Y", tooltip="Y resolution of the render product")
                ui.Spacer(width=0)
                ui.Label("Name", tooltip="Render product name (optional)")
            for i, entry in enumerate(self._recorder.rp_data):
                with ui.HStack(spacing=5):
                    ui.Spacer(width=10)
                    path_field_model = ui.StringField(width=200).model
                    path_field_model.set_value(entry[0])
                    path_field_model.add_value_changed_fn(lambda m, idx=i: self._update_rp_entry(idx, 0, m.as_string))
                    ui.Spacer(width=10)
                    x_field = ui.IntField()
                    x_field.model.set_value(entry[1])
                    x_field.model.add_value_changed_fn(lambda m, idx=i: self._update_rp_entry(idx, 1, m.as_int))
                    ui.Spacer(width=10)
                    y_field = ui.IntField()
                    y_field.model.set_value(entry[2])
                    y_field.model.add_value_changed_fn(lambda m, idx=i: self._update_rp_entry(idx, 2, m.as_int))
                    ui.Spacer(width=10)
                    name_field = ui.StringField()
                    name_field.model.set_value(entry[3])
                    name_field.model.add_value_changed_fn(lambda m, idx=i: self._update_rp_entry(idx, 3, m.as_string))
                    ui.Button(
                        f"{_ui_get_delete_glyph()}",
                        width=30,
                        clicked_fn=lambda idx=i: self._remove_rp_entry(idx),
                        tooltip="Remove entry",
                    )
            with ui.HStack(spacing=5):
                ui.Spacer(width=5)
                ui.Button(
                    "Add New Render Product Entry", clicked_fn=self._add_new_rp_field, tooltip="Create a new entry"
                )

    def _build_params_ui(self):
        """Build the writer parameters part of the UI."""
        with ui.VStack(spacing=5):
            with ui.HStack():
                ui.Spacer(width=10)
                ui.Label("Writer")

                writer_type_collection = ui.RadioCollection()
                if self._recorder.writer_name == "BasicWriter":
                    writer_type_collection.model.set_value(0)
                else:
                    writer_type_collection.model.set_value(1)

                def writer_type_collection_changed(model):
                    if model.as_int == 0:
                        self._recorder.writer_name = "BasicWriter"
                    else:
                        self._recorder.writer_name = self._custom_writer_name
                    asyncio.ensure_future(self._build_window_ui_async())

                writer_type_collection.model.add_value_changed_fn(writer_type_collection_changed)

                ui.RadioButton(
                    text="Default", radio_collection=writer_type_collection, tooltip="Uses the default BasicWriter"
                )
                ui.RadioButton(
                    text="Custom", radio_collection=writer_type_collection, tooltip="Loads a custom writer by name"
                )

            if self._recorder.writer_name == "BasicWriter":
                self._build_basic_writer_ui()
            else:
                self._build_custom_writer_ui()

    def _build_basic_writer_ui(self):
        """Build the basic writer part of the UI."""
        for key, val in self._recorder.basic_writer_params.items():
            with ui.HStack(spacing=5):
                ui.Spacer(width=10)
                ui.Label(key, alignment=ui.Alignment.LEFT, tooltip=PARAM_TOOLTIPS[key])
                model = ui.CheckBox().model
                model.set_value(val)

                def value_changed(m, k=key):
                    self._recorder.basic_writer_params[k] = m.as_bool

                model.add_value_changed_fn(value_changed)

        with ui.HStack():

            def select_all():
                for k in self._recorder.basic_writer_params:
                    self._recorder.basic_writer_params[k] = True
                asyncio.ensure_future(self._build_window_ui_async())

            def toggle_all():
                for k in self._recorder.basic_writer_params:
                    self._recorder.basic_writer_params[k] = not self._recorder.basic_writer_params[k]
                asyncio.ensure_future(self._build_window_ui_async())

            ui.Button(text="Select All", clicked_fn=select_all, tooltip="Select all parameters")
            ui.Button(text="Toggle All", clicked_fn=toggle_all, tooltip="Toggle all parameters")

    def _build_custom_writer_ui(self):
        """Build the custom writer part of the UI."""
        with ui.HStack(spacing=5):
            ui.Spacer(width=10)
            ui.Label("Name", tooltip="The name of the custom writer from the registry")
            writer_name_model = ui.StringField().model
            writer_name_model.set_value(self._recorder.writer_name)

            def writer_name_changed(m):
                self._recorder.writer_name = m.as_string

            writer_name_model.add_value_changed_fn(writer_name_changed)

        with ui.HStack(spacing=5):
            ui.Spacer(width=10)
            ui.Label("Parameters Path", tooltip="Path to the json file storing the custom writer parameters")
            path_model = ui.StringField().model
            path_model.set_value(self._custom_params_path)

            def path_changed(m):
                self._custom_params_path = m.as_string

            path_model.add_value_changed_fn(path_changed)

    def _build_writer_ui(self):
        """Build the writer UI frame."""
        with ui.VStack(spacing=5):
            rp_frame = ui.CollapsableFrame("Render Products", height=0, collapsed=self._rp_frame_collapsed)
            with rp_frame:

                def on_collapsed_changed(collapsed):
                    self._rp_frame_collapsed = collapsed

                rp_frame.set_collapsed_changed_fn(on_collapsed_changed)
                self._build_rp_ui()

            params_frame = ui.CollapsableFrame("Parameters", height=0, collapsed=self._writer_params_frame_collapsed)
            with params_frame:

                def on_collapsed_changed(collapsed):
                    self._writer_params_frame_collapsed = collapsed

                params_frame.set_collapsed_changed_fn(on_collapsed_changed)
                self._build_params_ui()

            output_frame = ui.CollapsableFrame("Output", height=0, collapsed=self._output_frame_collapsed)
            with output_frame:

                def on_collapsed_changed(collapsed):
                    self._output_frame_collapsed = collapsed

                output_frame.set_collapsed_changed_fn(on_collapsed_changed)
                self._build_output_ui()

            config_frame = ui.CollapsableFrame("Config", height=0, collapsed=self._config_frame_collapsed)
            with config_frame:

                def on_collapsed_changed(collapsed):
                    self._config_frame_collapsed = collapsed

                config_frame.set_collapsed_changed_fn(on_collapsed_changed)
                self._build_config_ui()

    def _build_control_params_ui(self):
        """Build the control parameters part of the UI."""
        with ui.VStack(spacing=10):
            with ui.HStack(spacing=5):
                ui.Spacer(width=10)
                ui.Label("Number of frames", tooltip="If set to 0, data acquisition will run indefinitely")
                num_frames_model = ui.IntField().model
                num_frames_model.set_value(self._recorder.num_frames)

                def num_frames_changed(m):
                    self._recorder.num_frames = m.as_int

                num_frames_model.add_value_changed_fn(num_frames_changed)

                ui.Label("RTSubframes", tooltip="Render extra frames between captures to avoid rendering artifacts")
                rt_subframes_model = ui.IntField().model
                rt_subframes_model.set_value(self._recorder.rt_subframes)

                def num_rt_subframes_changed(m):
                    self._recorder.rt_subframes = m.as_int

                rt_subframes_model.add_value_changed_fn(num_rt_subframes_changed)

            with ui.HStack(spacing=5):
                ui.Spacer(width=10)
                ui.Label("Control Timeline", tooltip="Start/Stop/Pause timeline as well with the recorder")
                control_timeline_model = ui.CheckBox().model
                control_timeline_model.set_value(self._recorder.control_timeline)

                def control_timeline_value_changed(m):
                    self._recorder.control_timeline = m.as_bool

                control_timeline_model.add_value_changed_fn(control_timeline_value_changed)

                ui.Spacer(width=10)
                ui.Label("Verbose", tooltip="Print recorder status to the terminal (e.g. current frame)")
                verbose_model = ui.CheckBox().model
                verbose_model.set_value(self._recorder.verbose)

                def verbose_value_changed(m):
                    self._recorder.verbose = m.as_bool

                verbose_model.add_value_changed_fn(verbose_value_changed)

    def _build_control_ui(self):
        """Build the control UI frame."""
        with ui.VStack(spacing=5):
            control_params_frame = ui.CollapsableFrame(
                "Parameters", height=0, collapsed=self._control_params_frame_collapsed
            )
            with control_params_frame:

                def on_collapsed_changed(collapsed):
                    self._control_params_frame_collapsed = collapsed

                control_params_frame.set_collapsed_changed_fn(on_collapsed_changed)
                self._build_control_params_ui()

            with ui.HStack(spacing=5):
                ui.Spacer(width=5)
                self._start_stop_button = ui.Button(
                    "Start",
                    clicked_fn=self._start_stop_recorder,
                    enabled=True,
                    tooltip="Start/stop the recording",
                )
                self._pause_resume_button = ui.Button(
                    "Pause",
                    clicked_fn=self._pause_resume_recorder,
                    enabled=False,
                    tooltip="Pause/resume recording",
                )

    def _build_window_ui(self):
        """Build the window UI."""
        with self.frame:
            with ui.ScrollingFrame():
                with ui.VStack(spacing=5):
                    writer_frame = ui.CollapsableFrame("Writer", height=0, collapsed=self._writer_frame_collapsed)
                    with writer_frame:

                        def on_collapsed_changed(collapsed):
                            self._writer_frame_collapsed = collapsed

                        writer_frame.set_collapsed_changed_fn(on_collapsed_changed)
                        self._build_writer_ui()

                    control_frame = ui.CollapsableFrame("Control", height=0, collapsed=self._control_frame_collapsed)
                    with control_frame:

                        def on_collapsed_changed(collapsed):
                            self._control_frame_collapsed = collapsed

                        control_frame.set_collapsed_changed_fn(on_collapsed_changed)
                        self._build_control_ui()

    async def _build_window_ui_async(self):
        """Build the window UI asynchronously on the next update."""
        self._build_window_ui()
