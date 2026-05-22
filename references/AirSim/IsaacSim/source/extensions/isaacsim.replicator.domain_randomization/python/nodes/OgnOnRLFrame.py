# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import numpy as np
import omni.graph.core as og
from isaacsim.replicator.domain_randomization.scripts import context


class OgnOnRLFrameInternalState:
    def __init__(self):
        self.frame_count = None


class OgnOnRLFrame:
    @staticmethod
    def internal_state():
        return OgnOnRLFrameInternalState()

    @staticmethod
    def compute(db) -> bool:
        if not context._context or not context._context.trigger:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return True

        context._context.trigger = False
        state = db.per_instance_state
        reset_inds = context.get_reset_inds()

        if state.frame_count is None:
            state.frame_count = np.zeros(db.inputs.num_envs)

        if reset_inds is not None and len(reset_inds) > 0:
            state.frame_count[reset_inds] = 0
            db.outputs.resetInds = reset_inds
        else:
            db.outputs.resetInds = []

        db.outputs.frameNum = state.frame_count

        state.frame_count += 1

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True
