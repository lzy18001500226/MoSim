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

import carb.events
import omni.usd


class BaseResetNode:
    """
    Base class for nodes that automatically reset when stop is pressed.
    """

    def __init__(self, initialize=False):
        self.initialized = initialize

        timeline = omni.timeline.get_timeline_interface()

        self.timeline_event_sub = timeline.get_timeline_event_stream().create_subscription_to_pop_by_type(
            int(omni.timeline.TimelineEventType.STOP), self.on_stop_play, name="IsaacSimOGNCoreNodesStageEventHandler"
        )

    def on_stop_play(self, event: carb.events.IEvent):
        self.custom_reset()
        self.initialized = False

    # Defined by subclass
    def custom_reset(self):
        pass

    def reset(self):
        self.timeline_event_sub = None
        self.initialized = None
