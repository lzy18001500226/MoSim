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


import carb
import omni.ext
import omni.kit.app
import omni.timeline

ASYNC_TOGGLE_SETTING = "/exts/isaacsim.core.throttling/enable_async"
MANUAL_TOGGLE_SETTING = "/exts/isaacsim.core.throttling/enable_manualmode"


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):
        # Initialize loop runner
        self._loop_runner = None
        try:
            import omni.kit.loop._loop as omni_loop

            self._loop_runner = omni_loop.acquire_loop_interface()
        except Exception:
            pass

        # frame counting for async toggle
        self._frame_count = 0
        self._waiting_for_async_reenable = False
        self._frame_update_subscription = None
        self._frame_delay = 10  # default 10 frame delay

        # Enable the developer throttling settings when extension starts
        carb.settings.get_settings().set("/app/show_developer_preference_section", True)

        timeline = omni.timeline.get_timeline_interface()
        self.timeline_event_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
            self.on_stop_play, name="IsaacSimThrottlingEventHandler"
        )

        _settings = carb.settings.get_settings()

        if _settings.get(ASYNC_TOGGLE_SETTING):
            # Enable async rendering at startup
            _settings.set("/app/asyncRendering", True)
            _settings.set("/app/asyncRenderingLowLatency", True)

        if _settings.get(MANUAL_TOGGLE_SETTING):
            self._set_loop_manual_mode(False)

    def _set_loop_manual_mode(self, manual_mode: bool):
        if self._loop_runner is not None:
            try:
                self._loop_runner.set_manual_mode(manual_mode)
            except Exception:
                pass

    def _on_frame_update(self, event: carb.events.IEvent):
        """Frame update callback for async toggle frame delay."""
        if not self._waiting_for_async_reenable:
            return
        self._frame_count += 1

        if self._frame_count >= self._frame_delay:
            # Check timeline did not play within the frame delay
            timeline = omni.timeline.get_timeline_interface()
            if not timeline.is_playing():
                # toggle async rendering
                _settings = carb.settings.get_settings()
                if _settings.get(ASYNC_TOGGLE_SETTING):
                    _settings.set("/app/asyncRendering", True)
                    _settings.set("/app/asyncRenderingLowLatency", True)

            self._waiting_for_async_reenable = False
            self._frame_count = 0

            # Unsubscribe to save on frame update callback overhead
            if self._frame_update_subscription is not None:
                self._frame_update_subscription = None

    def _start_frame_counting(self):
        """Start counting frames for async rendering delay."""
        if self._waiting_for_async_reenable:
            return

        self._frame_count = 0
        self._waiting_for_async_reenable = True

        # Create subscription on-demand to save on overhead
        self._frame_update_subscription = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_frame_update,
            observer_name="IsaacSimThrottling._on_frame_update",
        )

    def on_stop_play(self, event: carb.events.IEvent):
        # Disable eco mode if playing sim, enable if stopped
        # Disable legacy gizmos during runtime
        # Disable manual mode on stop, enable on play
        # Disable async rendering during runtime (with frame delay)
        _settings = carb.settings.get_settings()
        if event.type == int(omni.timeline.TimelineEventType.PLAY):
            _settings.set("/rtx/ecoMode/enabled", False)
            _settings.set("/exts/omni.kit.hydra_texture/gizmos/enabled", False)

            if _settings.get(ASYNC_TOGGLE_SETTING):
                _settings.set("/app/asyncRendering", False)
                _settings.set("/app/asyncRenderingLowLatency", False)

            if _settings.get(MANUAL_TOGGLE_SETTING):
                self._set_loop_manual_mode(True)

        elif event.type == int(omni.timeline.TimelineEventType.STOP) or event.type == int(
            omni.timeline.TimelineEventType.PAUSE
        ):
            _settings.set("/rtx/ecoMode/enabled", True)
            _settings.set("/exts/omni.kit.hydra_texture/gizmos/enabled", True)

            if _settings.get(ASYNC_TOGGLE_SETTING):
                # Start frame delay counting to give replicator time to finish
                self._start_frame_counting()

            if _settings.get(MANUAL_TOGGLE_SETTING):
                self._set_loop_manual_mode(False)

    def on_shutdown(self):
        self.timeline_event_sub = None

        if self._frame_update_subscription is not None:
            self._frame_update_subscription = None

        self._waiting_for_async_reenable = False
        self._frame_count = 0
