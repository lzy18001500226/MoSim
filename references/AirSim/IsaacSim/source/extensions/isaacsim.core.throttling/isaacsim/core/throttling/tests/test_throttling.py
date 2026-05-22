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
import carb.settings
import omni.ext
import omni.kit.test


class TestIsaacThrottling(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.set_start_time(0)
        self._timeline.set_end_time(1)
        self._settings = carb.settings.get_settings()

        # Reset async rendering state to clean test environment
        self._settings.set("/app/asyncRendering", False)
        self._settings.set("/app/asyncRenderingLowLatency", False)
        pass

    async def tearDown(self):
        # Reset state after each test
        self._settings.set("/app/asyncRendering", False)
        self._settings.set("/app/asyncRenderingLowLatency", False)
        pass

    # async rendering always off
    async def test_on_stop_play_toggles_off(self):
        self._settings = carb.settings.get_settings()
        self._settings.set("/rtx/ecoMode/enabled", True)
        self._settings.set("/app/asyncRendering", False)
        self._settings.set("/app/asyncRenderingLowLatency", False)

        self._settings.set("/exts/isaacsim.core.throttling/enable_async", False)
        self._settings.set("/exts/isaacsim.core.throttling/enable_manualmode", False)

        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._settings.get("/rtx/ecoMode/enabled"), False)
        self.assertEqual(self._settings.get("/exts/omni.kit.hydra_texture/gizmos/enabled"), False)
        self.assertFalse(self._settings.get("/app/asyncRendering"))
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._settings.get("/rtx/ecoMode/enabled"), True)
        self.assertEqual(self._settings.get("/exts/omni.kit.hydra_texture/gizmos/enabled"), True)
        self.assertFalse(self._settings.get("/app/asyncRendering"))
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._settings.get("/rtx/ecoMode/enabled"), False)
        self.assertEqual(self._settings.get("/exts/omni.kit.hydra_texture/gizmos/enabled"), False)
        self.assertFalse(self._settings.get("/app/asyncRendering"))
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._settings.get("/rtx/ecoMode/enabled"), True)
        self.assertEqual(self._settings.get("/exts/omni.kit.hydra_texture/gizmos/enabled"), True)
        self.assertFalse(self._settings.get("/app/asyncRendering"))
        pass

    async def test_on_stop_play_callback(self):
        self._settings = carb.settings.get_settings()
        self._settings.set("/rtx/ecoMode/enabled", True)
        self._settings.set("/app/asyncRendering", False)
        self._settings.set("/app/asyncRenderingLowLatency", False)

        self._settings.set("/exts/isaacsim.core.throttling/enable_async", True)
        self._settings.set("/exts/isaacsim.core.throttling/enable_manualmode", True)

        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._settings.get("/rtx/ecoMode/enabled"), False)
        self.assertEqual(self._settings.get("/exts/omni.kit.hydra_texture/gizmos/enabled"), False)
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._settings.get("/rtx/ecoMode/enabled"), True)
        self.assertEqual(self._settings.get("/exts/omni.kit.hydra_texture/gizmos/enabled"), True)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._settings.get("/rtx/ecoMode/enabled"), False)
        self.assertEqual(self._settings.get("/exts/omni.kit.hydra_texture/gizmos/enabled"), False)
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()
        self.assertEqual(self._settings.get("/rtx/ecoMode/enabled"), True)
        self.assertEqual(self._settings.get("/exts/omni.kit.hydra_texture/gizmos/enabled"), True)
        pass

    async def test_async_rendering_10_frame_delay(self):
        """Test that async rendering is re-enabled after 10 frames when timeline stops."""
        self._settings = carb.settings.get_settings()

        # Enable async toggle
        self._settings.set("/exts/isaacsim.core.throttling/enable_async", True)

        # Start with timeline playing (async should be disabled)
        self._timeline.play()
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(self._settings.get("/app/asyncRendering"))

        # Stop timeline - start the 10-frame delay
        self._timeline.stop()
        await omni.kit.app.get_app().next_update_async()

        # For frames 1-9, async rendering should be disabled
        for frame in range(1, 10):
            await omni.kit.app.get_app().next_update_async()
            self.assertFalse(
                self._settings.get("/app/asyncRendering"), f"Async rendering should be False at frame {frame}"
            )

        # On frame 10, async rendering should be enabled
        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._settings.get("/app/asyncRendering"), "Async rendering should be True after 10 frames")

        await omni.kit.app.get_app().next_update_async()
        self.assertTrue(self._settings.get("/app/asyncRendering"))
        pass
