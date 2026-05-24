# SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

"""Test to verify that viewport rendering callbacks are triggered on the first frame."""

import sys
import time

from isaacsim import SimulationApp

# Create simulation app
kit = SimulationApp({"headless": False})


import omni

# Track if callback was called
callback_called = False


def data_acquisition_callback(event):
    """Callback function triggered on rendering events."""
    global callback_called
    print(f"Received render event: {event.type}")
    callback_called = True


# Subscribe to NEW_FRAME rendering events
data_callback = (
    omni.usd.get_context()
    .get_rendering_event_stream()
    .create_subscription_to_pop_by_type(
        int(omni.usd.StageRenderingEventType.NEW_FRAME),
        data_acquisition_callback,
        name="test_viewport_ready.acquisition_callback",
        order=0,
    )
)

try:
    # Simulate one frame to trigger rendering callback
    kit.update()

    # Check if callback was called on first frame
    if not callback_called:
        print("ERROR: Rendering callback was not called on the first frame")

        # Wait for viewport to be ready before exiting to prevent app hang
        max_wait_frames = 100
        for i in range(max_wait_frames):
            print(f"Waiting for viewport to be ready before exiting... frame {i}")
            kit.update()
            time.sleep(0.02)
            if callback_called:
                break

        sys.exit(1)

    print("SUCCESS: Rendering callback was called on the first frame")

finally:
    # Cleanup
    kit.close()
